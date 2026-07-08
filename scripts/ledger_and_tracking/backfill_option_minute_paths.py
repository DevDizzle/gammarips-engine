"""One-shot backfill of option_minute_paths from enriched_option_outcomes.

For every labeled (contract, entry_day) in the outcomes substrate, fetches
the per-minute option bars over the 3-trading-day excursion window
[entry_day .. exit_day_3d] from Polygon minute aggregates (one range call
per contract-day) and loads them into
`profit_scout.option_minute_paths` via EXPLICIT-SCHEMA load jobs (no
streaming, no autodetect). Executed 2026-07-07 (~3.1k contract-days).

Idempotent per scan_date batch: each batch DELETEs its scan_dates' rows
before loading, so a re-run cannot duplicate. Safe to re-run for a date
range with --from/--to.

Usage:
    PROJECT_ID=profitscout-fida8 POLYGON_API_KEY=... \
      python scripts/ledger_and_tracking/backfill_option_minute_paths.py [--from YYYY-MM-DD] [--to YYYY-MM-DD]
"""

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
TABLE_ID = f"{PROJECT_ID}.profit_scout.option_minute_paths"
OUTCOMES = f"`{PROJECT_ID}.profit_scout.enriched_option_outcomes`"
ET = ZoneInfo("America/New_York")
API_KEY = (os.environ.get("POLYGON_API_KEY") or "").strip()
WORKERS = int(os.environ.get("BACKFILL_WORKERS", "16"))

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


def fetch_minute_bars(contract: str, start: str, end: str) -> list[dict]:
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{contract}"
        f"/range/1/minute/{start}/{end}"
    )
    params = {"adjusted": "true", "sort": "asc", "limit": 50000}
    for attempt in range(3):
        try:
            resp = requests.get(
                url, params=params,
                headers={"Authorization": f"Bearer {API_KEY}"}, timeout=15,
            )
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return (resp.json() or {}).get("results") or []
        except Exception as e:  # noqa: BLE001
            print(f"  warn: {contract} fetch attempt {attempt+1}: {e}", file=sys.stderr)
            time.sleep(1)
    return []


def bars_to_rows(task: dict, bars: list[dict], ingested_at: str) -> list[dict]:
    """Keep bars from the first 3 distinct ET session dates on/after entry_day."""
    rows = []
    session_dates: list[str] = []
    for b in bars:
        try:
            dt = datetime.fromtimestamp(int(b["t"]) / 1e3, tz=UTC)
        except (KeyError, TypeError, ValueError, OSError):
            continue
        bar_date = dt.astimezone(ET).date().isoformat()
        if bar_date < task["entry_day"]:
            continue
        if bar_date not in session_dates:
            if len(session_dates) >= 3:
                continue
            session_dates.append(bar_date)
        rows.append(
            {
                "scan_date": task["scan_date"],
                "entry_day": task["entry_day"],
                "contract": task["contract"],
                "ticker": task["ticker"],
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
                "source": "polygon minute aggs (backfill 2026-07-07)",
                "ingested_at": ingested_at,
            }
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="dfrom", default=None)
    ap.add_argument("--to", dest="dto", default=None)
    args = ap.parse_args()

    if not API_KEY:
        sys.exit("POLYGON_API_KEY not set")

    client = bigquery.Client(project=PROJECT_ID)
    where = ["recommended_contract IS NOT NULL", "entry_day IS NOT NULL"]
    if args.dfrom:
        where.append(f"scan_date >= '{args.dfrom}'")
    if args.dto:
        where.append(f"scan_date <= '{args.dto}'")
    q = f"""
    SELECT DISTINCT CAST(scan_date AS STRING) AS scan_date,
           CAST(entry_day AS STRING) AS entry_day,
           recommended_contract AS contract, ticker,
           CAST(COALESCE(exit_day_3d,
                DATE_ADD(entry_day, INTERVAL 6 DAY)) AS STRING) AS window_end
    FROM {OUTCOMES}
    WHERE {' AND '.join(where)}
    ORDER BY scan_date, contract
    """
    tasks = [dict(r) for r in client.query(q).result()]
    print(f"{len(tasks)} contract-days to backfill")

    ingested_at = datetime.now(UTC).isoformat()
    all_rows: list[dict] = []
    n_empty = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {
            ex.submit(
                fetch_minute_bars, t["contract"], t["entry_day"], t["window_end"]
            ): t
            for t in tasks
        }
        done = 0
        for fut in as_completed(futs):
            t = futs[fut]
            try:
                bars = fut.result()
            except Exception as e:  # noqa: BLE001
                print(f"  warn: {t['contract']} future: {e}", file=sys.stderr)
                bars = []
            rows = bars_to_rows(t, bars, ingested_at)
            if not rows:
                n_empty += 1
            all_rows.extend(rows)
            done += 1
            if done % 250 == 0:
                print(f"  fetched {done}/{len(tasks)} ({len(all_rows)} bars so far)")

    print(f"fetch complete: {len(all_rows)} bars, {n_empty} empty contract-days")

    # Idempotency: clear the scan_dates we are about to load.
    scan_dates = sorted({t["scan_date"] for t in tasks})
    client.query(
        f"DELETE FROM `{TABLE_ID}` WHERE scan_date IN UNNEST(@sds)",
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ArrayQueryParameter("sds", "DATE", scan_dates)]
        ),
    ).result()

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    CHUNK = 100_000
    for i in range(0, len(all_rows), CHUNK):
        chunk = all_rows[i : i + CHUNK]
        job = client.load_table_from_json(chunk, TABLE_ID, job_config=job_config)
        job.result()
        print(f"  loaded rows {i}..{i + len(chunk)}")

    print("DONE")


if __name__ == "__main__":
    main()
