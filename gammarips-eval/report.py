"""Weekly eval report builder.

Aggregates profit_scout.llm_eval_results_v1 for a given ISO week into a
markdown digest and writes it to Firestore at eval_reports/{iso_week}.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from google.cloud import bigquery, firestore

logger = logging.getLogger(__name__)


def _iso_week_bounds(iso_week: str) -> tuple[str, str]:
    """'2026-W15' -> ('2026-04-06', '2026-04-12')."""
    year_str, week_str = iso_week.split("-W")
    start = datetime.strptime(f"{year_str}-W{week_str}-1", "%G-W%V-%u").date()
    from datetime import timedelta
    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def build_weekly_report(
    *,
    project_id: str,
    dataset: str,
    iso_week: str,
    dry_run: bool = False,
) -> dict:
    start_iso, end_iso = _iso_week_bounds(iso_week)
    bq = bigquery.Client(project=project_id)
    results_table = f"{project_id}.{dataset}.llm_eval_results_v1"
    traces_table = f"{project_id}.{dataset}.llm_traces_v1"

    # Aggregate 1: pass rate per (service, evaluator).
    # Dedupe on eval_id — see docs/EVAL-SYSTEM.md "Deduplication".
    agg_q = f"""
        WITH deduped AS (
          SELECT *
          FROM `{results_table}`
          WHERE scan_date BETWEEN '{start_iso}' AND '{end_iso}'
          QUALIFY ROW_NUMBER() OVER (
            PARTITION BY eval_id ORDER BY created_at DESC
          ) = 1
        )
        SELECT service, evaluator,
               COUNT(*) AS n,
               AVG(score) AS mean_score,
               SUM(CAST(passed AS INT64)) AS n_passed,
               SUM(CASE WHEN passed IS TRUE THEN 1 ELSE 0 END) / COUNT(*) AS pass_rate
        FROM deduped
        GROUP BY service, evaluator
        ORDER BY service, evaluator
    """
    agg_rows = list(bq.query(agg_q).result())

    # Aggregate 2: per-service cost and call volume
    cost_q = f"""
        SELECT service, model_id,
               COUNT(*) AS n_calls,
               SUM(cost_usd) AS total_cost_usd,
               SUM(input_tokens) AS total_in_tokens,
               SUM(output_tokens) AS total_out_tokens
        FROM `{traces_table}`
        WHERE scan_date BETWEEN '{start_iso}' AND '{end_iso}'
          AND status = 'ok'
        GROUP BY service, model_id
        ORDER BY total_cost_usd DESC
    """
    cost_rows = list(bq.query(cost_q).result())

    # Aggregate 3: worst 5 traces by score (dedupe on eval_id first).
    worst_q = f"""
        WITH deduped AS (
          SELECT *
          FROM `{results_table}`
          WHERE scan_date BETWEEN '{start_iso}' AND '{end_iso}'
            AND score IS NOT NULL
          QUALIFY ROW_NUMBER() OVER (
            PARTITION BY eval_id ORDER BY created_at DESC
          ) = 1
        )
        SELECT r.trace_id, r.service, r.evaluator, r.score,
               t.ticker, t.model_id, t.call_site
        FROM deduped r
        LEFT JOIN `{traces_table}` t USING (trace_id)
        ORDER BY r.score ASC
        LIMIT 5
    """
    worst_rows = list(bq.query(worst_q).result())

    # ----- Markdown -----
    lines: list[str] = []
    lines.append(f"# GammaRips Eval Report — {iso_week}")
    lines.append("")
    lines.append(f"**Window:** {start_iso} to {end_iso}")
    lines.append("")

    lines.append("## Pass rates by service × evaluator")
    lines.append("")
    lines.append("| Service | Evaluator | N | Mean score | Pass rate |")
    lines.append("|---|---|---:|---:|---:|")
    for r in agg_rows:
        ms = r["mean_score"]
        pr = r["pass_rate"]
        ms_str = f"{ms:.3f}" if ms is not None else "—"
        pr_str = f"{pr:.1%}" if pr is not None else "—"
        lines.append(
            f"| {r['service']} | {r['evaluator']} | {r['n']} | {ms_str} | {pr_str} |"
        )
    lines.append("")

    lines.append("## Cost & volume by service × model")
    lines.append("")
    lines.append("| Service | Model | Calls | Input tok | Output tok | Total USD |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for r in cost_rows:
        lines.append(
            f"| {r['service']} | {r['model_id']} | {r['n_calls']} | "
            f"{r['total_in_tokens'] or 0} | {r['total_out_tokens'] or 0} | "
            f"${(r['total_cost_usd'] or 0):.4f} |"
        )
    lines.append("")

    lines.append("## Worst 5 traces")
    lines.append("")
    lines.append("| Trace | Service | Call site | Ticker | Evaluator | Score |")
    lines.append("|---|---|---|---|---|---:|")
    for r in worst_rows:
        lines.append(
            f"| `{r['trace_id'][:12]}` | {r['service']} | {r['call_site']} | "
            f"{r.get('ticker') or '—'} | {r['evaluator']} | {r['score']:.3f} |"
        )
    lines.append("")

    markdown = "\n".join(lines)

    doc_data = {
        "iso_week": iso_week,
        "start": start_iso,
        "end": end_iso,
        "markdown": markdown,
        "aggregates": {
            "pass_rates": [dict(r) for r in agg_rows],
            "cost_by_model": [dict(r) for r in cost_rows],
            "worst_traces": [dict(r) for r in worst_rows],
        },
        "generated_at": datetime.now(timezone.utc),
    }

    if dry_run:
        return {
            "iso_week": iso_week,
            "dry_run": True,
            "markdown_preview": markdown[:1500],
        }

    fs = firestore.Client(project=project_id)
    fs.collection("eval_reports").document(iso_week).set(doc_data)

    return {
        "iso_week": iso_week,
        "doc_path": f"eval_reports/{iso_week}",
        "n_eval_rows": sum(r["n"] for r in agg_rows),
    }
