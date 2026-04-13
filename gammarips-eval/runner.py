"""EvalRunner — the core batch loop.

Pulls new rows from profit_scout.llm_traces_v1 since a watermark, joins
ground-truth data (signal_performance, signals_labeled_v1), dispatches to
the configured evaluator chain for each trace's service, and writes the
scored results back to profit_scout.llm_eval_results_v1.

Idempotent: eval_id is deterministic on (trace_id, evaluator, eval_version)
so re-runs produce duplicate rows only if the same trace + evaluator combo
has not yet been written. BQ streaming inserts do not enforce uniqueness;
a daily MERGE dedup job is out of scope for v1.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml
from google.cloud import bigquery, firestore

from evaluators import run_evaluator, list_evaluators

logger = logging.getLogger(__name__)

WATERMARK_DOC = "gammarips_evals/watermark"


def _load_config() -> dict:
    path = Path(__file__).parent / "config.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def _deterministic_eval_id(trace_id: str, evaluator: str, version: str) -> str:
    h = hashlib.sha256(f"{trace_id}|{evaluator}|{version}".encode()).hexdigest()
    return h[:32]


@dataclass
class Trace:
    trace_id: str
    service: str
    call_site: str
    run_id: str
    scan_date: date
    ticker: Optional[str]
    model_provider: str
    model_id: str
    prompt: Optional[str]
    response_text: Optional[str]
    response_parsed: Optional[Any]
    status: str

    @classmethod
    def from_row(cls, row) -> "Trace":
        parsed = None
        if row.get("response_parsed"):
            try:
                parsed = json.loads(row["response_parsed"]) if isinstance(row["response_parsed"], str) else row["response_parsed"]
            except Exception:
                parsed = None
        return cls(
            trace_id=row["trace_id"],
            service=row["service"],
            call_site=row["call_site"],
            run_id=row["run_id"],
            scan_date=row["scan_date"],
            ticker=row.get("ticker"),
            model_provider=row["model_provider"],
            model_id=row["model_id"],
            prompt=row.get("prompt"),
            response_text=row.get("response_text"),
            response_parsed=parsed,
            status=row["status"],
        )


class EvalRunner:
    def __init__(self, project_id: str, dataset: str):
        self.project_id = project_id
        self.dataset = dataset
        self.config = _load_config()
        self.eval_version = self.config.get("eval_version", "v1.0.0")
        self.traces_table = f"{project_id}.{dataset}.llm_traces_v1"
        self.results_table = f"{project_id}.{dataset}.llm_eval_results_v1"
        self.bq = bigquery.Client(project=project_id)
        try:
            self.fs = firestore.Client(project=project_id)
        except Exception as e:  # noqa: BLE001
            logger.warning("Firestore client init failed: %s", e)
            self.fs = None

        # Registry introspection — helpful for /healthz style debugging.
        logger.info("Registered evaluators: %s", list_evaluators())

    # ----- watermark -----

    def _read_watermark(self) -> Optional[datetime]:
        if self.fs is None:
            return None
        try:
            doc = self.fs.document(WATERMARK_DOC).get()
            if doc.exists:
                ts = doc.to_dict().get("last_created_at")
                if ts:
                    return ts
        except Exception as e:
            logger.warning("watermark read failed: %s", e)
        return None

    def _write_watermark(self, ts: datetime) -> None:
        if self.fs is None:
            return
        try:
            self.fs.document(WATERMARK_DOC).set({"last_created_at": ts})
        except Exception as e:
            logger.warning("watermark write failed: %s", e)

    # ----- trace pull -----

    def _fetch_traces(
        self,
        since: Optional[str],
        limit: int,
        service_filter: Optional[str],
    ) -> list[Trace]:
        if since:
            where = f"created_at > TIMESTAMP('{since}')"
        else:
            wm = self._read_watermark()
            if wm is not None:
                where = f"created_at > TIMESTAMP('{wm.isoformat()}')"
            else:
                # First-run bootstrap: scan today + yesterday only.
                where = "scan_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)"

        if service_filter:
            where += f" AND service = '{service_filter}'"

        # Only score successful calls; errors / parse_errors are still in BQ
        # for ops debugging but not evaluated.
        where += " AND status = 'ok'"

        query = f"""
            SELECT *
            FROM `{self.traces_table}`
            WHERE {where}
            ORDER BY created_at ASC
            LIMIT {int(limit)}
        """
        logger.info("Fetching traces: %s", query.strip())
        rows = list(self.bq.query(query).result())
        return [Trace.from_row(dict(r)) for r in rows]

    # ----- ground truth -----

    def _fetch_signal_performance(self, scan_date: date) -> dict[str, dict]:
        """Map ticker -> {peak_return_pct, win_tier, ...} for a scan_date."""
        query = f"""
            SELECT ticker, peak_return AS peak_return_pct, win_tier, peak_price_3d, entry_price
            FROM `{self.project_id}.{self.dataset}.signal_performance`
            WHERE scan_date = '{scan_date.isoformat()}'
        """
        try:
            rows = self.bq.query(query).result()
            return {r["ticker"]: dict(r) for r in rows}
        except Exception as e:
            logger.warning("signal_performance fetch failed for %s: %s", scan_date, e)
            return {}

    # ----- evaluation -----

    def run_batch(
        self,
        since: Optional[str] = None,
        limit: int = 500,
        dry_run: bool = False,
        service_filter: Optional[str] = None,
    ) -> dict:
        traces = self._fetch_traces(since, limit, service_filter)
        logger.info("Pulled %d traces", len(traces))
        if not traces:
            return {"traces_scanned": 0, "results_written": 0}

        # Pre-fetch ground truth for each distinct (scan_date) the traces touch.
        scan_dates = {t.scan_date for t in traces}
        gt_by_date: dict[date, dict[str, dict]] = {
            sd: self._fetch_signal_performance(sd) for sd in scan_dates
        }

        service_evals = self.config.get("service_evaluators", {})
        thresholds = self.config.get("thresholds", {})

        # --- Judge-call budget guard ---
        # Conservative per-call estimate for Gemini 3 Flash with typical
        # prompt + short structured response (~3k in + ~300 out tokens).
        # Anything cheaper is fine; this is an upper bound used to convert
        # the configured dollar cap into a call cap.
        _per_judge_cost = 0.003
        _max_spend = float(
            os.environ.get(
                "EVAL_MAX_SPEND_USD",
                str(self.config.get("max_spend_usd_per_run", 2.0)),
            )
        )
        _max_judge_calls = max(1, int(_max_spend / _per_judge_cost))
        budget = {"used": 0, "max": _max_judge_calls, "exhausted": False}
        logger.info(
            "judge budget: max_spend=$%.2f, per_call≈$%.4f, max_calls=%d",
            _max_spend, _per_judge_cost, _max_judge_calls,
        )

        rows_to_write: list[dict] = []
        max_trace_ts: Optional[datetime] = None

        for trace in traces:
            evaluators_for_service = service_evals.get(trace.service, [])
            if not evaluators_for_service:
                continue

            gt_ctx = {
                "signal_performance": gt_by_date.get(trace.scan_date, {}),
                "budget": budget,
            }

            for evaluator_name in evaluators_for_service:
                try:
                    result = run_evaluator(
                        evaluator_name,
                        trace=trace,
                        gt_context=gt_ctx,
                        config=self.config,
                    )
                except Exception as e:
                    logger.warning(
                        "evaluator %s failed on trace %s: %s",
                        evaluator_name, trace.trace_id, e,
                    )
                    continue

                if result is None:
                    continue

                threshold = thresholds.get(evaluator_name, 0.5)
                passed = None
                if result.score is not None:
                    passed = result.score >= threshold

                rows_to_write.append({
                    "eval_id": _deterministic_eval_id(
                        trace.trace_id, evaluator_name, self.eval_version
                    ),
                    "trace_id": trace.trace_id,
                    "service": trace.service,
                    "scan_date": trace.scan_date.isoformat(),
                    "evaluator": evaluator_name,
                    "eval_version": self.eval_version,
                    "judge_model": result.judge_model,
                    "score": result.score,
                    "passed": passed,
                    "details": json.dumps(result.details) if result.details else None,
                    "ground_truth_source": result.ground_truth_source,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })

        if dry_run:
            return {
                "traces_scanned": len(traces),
                "results_prepared": len(rows_to_write),
                "results_written": 0,
                "dry_run": True,
                "judge_calls_used": budget["used"],
                "budget_exhausted": budget["exhausted"],
            }

        if rows_to_write:
            errors = self.bq.insert_rows_json(self.results_table, rows_to_write)
            if errors:
                logger.warning("BQ insert errors: %s", errors)
                return {
                    "traces_scanned": len(traces),
                    "results_written": 0,
                    "errors": errors[:5],
                }

        # Only advance watermark past scan_dates that had ground truth
        # available. Traces from dates without GT stay behind the watermark
        # so they get re-scanned once signal_performance catches up.
        dates_with_gt = {sd for sd, gt in gt_by_date.items() if gt}
        if dates_with_gt:
            loose_wm = max(dates_with_gt)
            self._write_watermark(datetime.combine(loose_wm, datetime.min.time(), tzinfo=timezone.utc))
        else:
            loose_wm = None

        return {
            "traces_scanned": len(traces),
            "results_written": len(rows_to_write),
            "watermark_advanced_to": loose_wm.isoformat() if loose_wm else None,
            "judge_calls_used": budget["used"],
            "judge_calls_max": budget["max"],
            "budget_exhausted": budget["exhausted"],
        }
