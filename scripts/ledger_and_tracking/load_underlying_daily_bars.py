"""Load ADJUSTED underlying daily bars into the BQ cache (substrate must-fix #5c).

    ################################################################################
    #  NOT YET EXECUTED.  This makes BigQuery WRITES (delete-then-load per date)      #
    #  and calls Polygon.  It is gammarips-review + OWNER gated.  Do NOT run it        #
    #  until both sign off AND create_underlying_daily_bars.py has been run.           #
    ################################################################################

WHAT (docs/DECISIONS/2026-07-01-momentum-persist-and-opportunity-surface.md):
Populate profitscout-fida8.profit_scout.underlying_daily_bars from Polygon
grouped-daily ADJUSTED — ONE call per NYSE trading day returns every US stock's
adjusted OHLCV, so a full window is a handful of calls, not per-ticker fan-out.
This is the SAME endpoint the live enrichment momentum tilt uses
(_fetch_grouped_daily_closes), so the cache is byte-consistent with the tilt.

This REPLACES the dependence on the gitignored, stale local parquet cache
(backtesting_and_research/cache/poly_daily_underlying/) — momentum is now
reproducible from BQ infra.

SCOPE: by default only rows for tickers that appear in the research substrate
(enriched_option_outcomes ∪ overnight_signals_enriched) are kept, to bound size.
--all-tickers keeps the full grouped-daily universe (larger, more reusable).

IDEMPOTENT: per date, DELETE WHERE date=d then load-append (load job, not
streaming). Safe to re-run a window.

SCHEDULED USE (deferred wiring): run daily after the close to append the latest
CLOSED session:  python .../load_underlying_daily_bars.py --confirm --latest-only
A Cloud Scheduler → small endpoint (or the research VM cron) is the eventual home;
NOT wired here (kept a gated manual script until review + owner OK).

AUTH: reads POLYGON_API_KEY from os.environ at runtime; never logged / written to
disk / hardcoded. Inject at run time, e.g.:
    export POLYGON_API_KEY=$(gcloud secrets versions access latest \
        --secret=POLYGON_API_KEY --project=profitscout-fida8)

USAGE (from repo root):
    # PREVIEW — reads/fetches nothing-destructive, writes NOTHING:
    python scripts/ledger_and_tracking/load_underlying_daily_bars.py --dry-run \
        --start 2024-12-01 --end 2026-07-01
    # EXECUTE (only after review + owner sign-off + create_* run):
    python scripts/ledger_and_tracking/load_underlying_daily_bars.py --confirm \
        --start 2024-12-01 --end 2026-07-01

One-shot / scheduled loader (per .claude/rules/scripts-ledger.md): do NOT run
without explicit user approval.
"""

import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, date, timezone

import requests
import pandas_market_calendars as mcal
from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "underlying_daily_bars"
TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
SOURCE_TAG = "polygon_grouped_daily_adj"

_NYSE = mcal.get_calendar("NYSE")
POLY_KEY = os.environ.get("POLYGON_API_KEY", "").strip()
SESS = requests.Session()


def _trading_days(start: date, end: date) -> list[date]:
    sched = _NYSE.schedule(start_date=start, end_date=end)
    return [d.date() for d in sched.index]


def _substrate_tickers(client) -> set[str]:
    """Union of tickers in enriched_option_outcomes + overnight_signals_enriched."""
    sql = f"""
    SELECT DISTINCT ticker FROM `{PROJECT_ID}.{DATASET_ID}.enriched_option_outcomes`
      WHERE ticker IS NOT NULL
    UNION DISTINCT
    SELECT DISTINCT ticker FROM `{PROJECT_ID}.{DATASET_ID}.overnight_signals_enriched`
      WHERE ticker IS NOT NULL
    """
    return {str(r["ticker"]).strip().upper() for r in client.query(sql).result() if r["ticker"]}


def _fetch_grouped_adj(d: date) -> list[dict]:
    """Polygon grouped-daily ADJUSTED for one date. [] on failure (caller logs)."""
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{d.isoformat()}"
    params = {"adjusted": "true", "apiKey": POLY_KEY}
    for attempt in range(3):
        try:
            resp = SESS.get(url, params=params, timeout=30)
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json().get("results", []) or []
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                print(f"  {d}: fetch failed after retries: {e}")
                return []
            time.sleep(2 ** attempt)
    return []


def _rows_for_date(d: date, keep: set[str] | None) -> list[dict]:
    loaded_at = datetime.now(timezone.utc).isoformat()
    out = []
    for bar in _fetch_grouped_adj(d):
        t = bar.get("T")
        if not t:
            continue
        t = str(t).upper()
        if keep is not None and t not in keep:
            continue
        out.append({
            "date": d.isoformat(),
            "ticker": t,
            "open": bar.get("o"),
            "high": bar.get("h"),
            "low": bar.get("l"),
            "close": bar.get("c"),
            "volume": bar.get("v"),
            "adjusted": True,
            "source": SOURCE_TAG,
            "loaded_at": loaded_at,
        })
    return out


def _delete_then_load(client, d: date, rows: list[dict]) -> int:
    """Idempotent per-date replace via a load job (not streaming)."""
    client.query(
        f'DELETE FROM `{TABLE}` WHERE date = "{d.isoformat()}"'
    ).result()
    if not rows:
        return 0
    jsonl = "\n".join(json.dumps(r) for r in rows)
    job = client.load_table_from_file(
        io.BytesIO(jsonl.encode("utf-8")),
        TABLE,
        job_config=bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        ),
    )
    job.result()
    return job.output_rows or 0


def main():
    ap = argparse.ArgumentParser(description="Load underlying daily bars cache (must-fix #5c)")
    ap.add_argument("--start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date(2024, 12, 1))
    ap.add_argument("--end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date.today())
    ap.add_argument("--all-tickers", action="store_true",
                    help="keep the full grouped-daily universe (default: substrate tickers only)")
    ap.add_argument("--latest-only", action="store_true",
                    help="load only the most recent CLOSED NYSE session (scheduled-daily mode)")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true", help="fetch + count only; write NOTHING")
    grp.add_argument("--confirm", action="store_true", help="EXECUTE the writes (review + owner OK)")
    args = ap.parse_args()

    if not POLY_KEY:
        print("FATAL: POLYGON_API_KEY not in env — inject it at run time (see header).")
        sys.exit(2)

    client = bigquery.Client(project=PROJECT_ID)

    if args.latest_only:
        days = _trading_days(args.end.replace(day=1) if args.end.day < 5 else args.start, args.end)
        days = days[-1:] if days else []
    else:
        days = _trading_days(args.start, args.end)

    keep = None if args.all_tickers else _substrate_tickers(client)
    scope = "ALL grouped-daily tickers" if keep is None else f"{len(keep)} substrate tickers"
    mode = "DRY-RUN (no writes)" if args.dry_run else "EXECUTE (writing)"
    print(f"=== underlying_daily_bars load ===")
    print(f"    mode  : {mode}")
    print(f"    window: {days[0] if days else '-'} .. {days[-1] if days else '-'} ({len(days)} sessions)")
    print(f"    scope : {scope}\n")

    total = 0
    for i, d in enumerate(days):
        rows = _rows_for_date(d, keep)
        if args.dry_run:
            print(f"  [dry-run] {d}: would upsert {len(rows)} rows")
        else:
            n = _delete_then_load(client, d, rows)
            total += n
            print(f"  {d}: upserted {n} rows")
        time.sleep(0.15)  # polite pacing
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(days)} sessions")

    print("\n=== SUMMARY ===")
    print(f"  sessions processed: {len(days)}")
    if args.dry_run:
        print("  DRY RUN — nothing written. Re-run with --confirm after review + owner OK.")
    else:
        print(f"  rows upserted     : {total}")


if __name__ == "__main__":
    main()
