"""Daily option_minute_paths top-up (MCP Priority-4 / RM-002 / must-fix #6g).

Each evening (after the labeler), POST /persist_minute_paths reconciles the
minute-bar excursion paths for the last 3 scan_dates' enriched pools into
`profit_scout.option_minute_paths`: one Polygon minute-aggs range call per
(contract, scan_date), covering [entry_day .. min(exit_day_3d, today)]. By a
window's third session it is complete and drops out of the reconcile set.

The pool comes from overnight_signals_enriched (available the same evening,
independent of labeler lag). Writes are idempotent per scan_date:
DELETE-then-LOAD via EXPLICIT-SCHEMA load jobs — never streaming (the DELETE
would hit streaming buffers), never autodetect (2026-07-02 outage rule).

LEAKAGE WALL: these are realized post-entry bars (the excursion tape) — same
class as the opp_* opportunity surface. Research/label substrate ONLY: never
a feature, never joined into enriched_features_v1, never read by the
selection path or the live trader. This module is called ONLY from its own
endpoint; run_forward_paper_trading / run_label_enriched_pool never import
it. History back to 2026-04-13 was loaded by
scripts/ledger_and_tracking/backfill_option_minute_paths.py (2026-07-07).
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import requests
from google.cloud import bigquery

logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
TABLE_ID = f"{PROJECT_ID}.profit_scout.option_minute_paths"

FETCH_TIMEOUT_S = int(os.environ.get("MINUTE_PATHS_FETCH_TIMEOUT_S", "15"))
MAX_WORKERS = int(os.environ.get("MINUTE_PATHS_MAX_WORKERS", "16"))

_ET = ZoneInfo("America/New_York")

SCHEMA = [
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("entry_day", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("contract", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ticker", "STRING"),
    bigquery.SchemaField("ts", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("bar_date", "DATE"),
    bigquery.SchemaField("day_index", "INTEGER"),
    bigquery.SchemaField("open", "FLOAT"),
    bigquery.SchemaField("high", "FLOAT"),
    bigquery.SchemaField("low", "FLOAT"),
    bigquery.SchemaField("close", "FLOAT"),
    bigquery.SchemaField("volume", "INTEGER"),
    bigquery.SchemaField("vwap", "FLOAT"),
    bigquery.SchemaField("transactions", "INTEGER"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP"),
]


def _fetch_minute_bars(contract: str, start: str, end: str, api_key: str) -> list[dict]:
    """One range fetch, bearer-header key (never in the URL), 429-aware,
    fail-soft to []."""
    url = f"https://api.polygon.io/v2/aggs/ticker/{contract}/range/1/minute/{start}/{end}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000}
    for attempt in range(3):
        try:
            resp = requests.get(
                url, params=params,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=FETCH_TIMEOUT_S,
            )
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return (resp.json() or {}).get("results") or []
        except Exception as e:  # noqa: BLE001
            logger.warning(f"minute-paths fetch {contract} attempt {attempt+1}: {e}")
            time.sleep(1)
    return []


def _bars_to_rows(
    scan_date: date, entry_day: date, contract: str, ticker: str,
    bars: list[dict], ingested_at: str,
) -> list[dict]:
    """Keep bars from the first 3 distinct ET session dates on/after entry_day
    (the excursion window), tagging each with day_index 1..3."""
    rows: list[dict] = []
    session_dates: list[str] = []
    entry_s = entry_day.isoformat()
    for b in bars:
        try:
            dt = datetime.fromtimestamp(int(b["t"]) / 1e3, tz=UTC)
        except (KeyError, TypeError, ValueError, OSError):
            continue
        bar_date = dt.astimezone(_ET).date().isoformat()
        if bar_date < entry_s:
            continue
        if bar_date not in session_dates:
            if len(session_dates) >= 3:
                continue
            session_dates.append(bar_date)
        rows.append(
            {
                "scan_date": scan_date.isoformat(),
                "entry_day": entry_s,
                "contract": contract,
                "ticker": ticker,
                "ts": dt.isoformat(),
                "bar_date": bar_date,
                "day_index": session_dates.index(bar_date) + 1,
                "open": b.get("o"),
                "high": b.get("h"),
                "low": b.get("l"),
                "close": b.get("c"),
                "volume": int(b["v"]) if b.get("v") is not None else None,
                "vwap": b.get("vw"),
                "transactions": b.get("n"),
                "source": "polygon minute aggs (daily persist)",
                "ingested_at": ingested_at,
            }
        )
    return rows


def _fetch_pool(client: bigquery.Client, scan_date: date) -> list[tuple[str, str]]:
    q = f"""
    SELECT DISTINCT ticker, recommended_contract
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = @sd AND recommended_contract IS NOT NULL
    """
    job = client.query(
        q,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("sd", "DATE", scan_date)]
        ),
    )
    return [(str(r.ticker), str(r.recommended_contract)) for r in job.result()]


def persist_minute_paths(windows: list[dict]) -> dict:
    """Reconcile minute paths for the given windows. Each window dict:
    {"scan_date": date, "entry_day": date, "window_end": date} (window_end
    already clamped to today by the caller). Returns a summary dict; never
    raises past the top-level try."""
    api_key = (os.environ.get("POLYGON_API_KEY") or "").strip()
    if not api_key:
        return {"status": "error", "reason": "POLYGON_API_KEY not set"}

    client = bigquery.Client(project=PROJECT_ID)
    ingested_at = datetime.now(UTC).isoformat()
    summary: dict = {"status": "success", "windows": []}

    for w in windows:
        scan_date: date = w["scan_date"]
        entry_day: date = w["entry_day"]
        window_end: date = w["window_end"]
        try:
            pool = _fetch_pool(client, scan_date)
            if not pool:
                summary["windows"].append(
                    {"scan_date": scan_date.isoformat(), "skipped": "empty pool"}
                )
                continue

            rows: list[dict] = []
            with ThreadPoolExecutor(max_workers=max(1, min(MAX_WORKERS, len(pool)))) as ex:
                futs = {
                    ex.submit(
                        _fetch_minute_bars, c,
                        entry_day.isoformat(), window_end.isoformat(), api_key,
                    ): (t, c)
                    for (t, c) in pool
                }
                for fut in as_completed(futs):
                    t, c = futs[fut]
                    try:
                        bars = fut.result()
                    except Exception as e:  # noqa: BLE001
                        logger.warning(f"minute-paths future {c}: {e}")
                        bars = []
                    rows.extend(_bars_to_rows(scan_date, entry_day, c, t, bars, ingested_at))

            # Idempotent reconcile: replace this scan_date's rows wholesale.
            client.query(
                f"DELETE FROM `{TABLE_ID}` WHERE scan_date = @sd",
                job_config=bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("sd", "DATE", scan_date)
                    ]
                ),
            ).result()
            if rows:
                job_config = bigquery.LoadJobConfig(
                    schema=SCHEMA,
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                )
                client.load_table_from_json(rows, TABLE_ID, job_config=job_config).result()

            summary["windows"].append(
                {
                    "scan_date": scan_date.isoformat(),
                    "entry_day": entry_day.isoformat(),
                    "window_end": window_end.isoformat(),
                    "contracts": len(pool),
                    "bars": len(rows),
                }
            )
            logger.info(
                f"minute-paths: {scan_date} reconciled — {len(pool)} contracts, "
                f"{len(rows)} bars through {window_end}"
            )
        except Exception as e:  # noqa: BLE001
            logger.error(f"minute-paths window {scan_date} failed: {e}")
            summary["status"] = "partial"
            summary["windows"].append(
                {"scan_date": scan_date.isoformat(), "error": str(e)[:200]}
            )

    return summary
