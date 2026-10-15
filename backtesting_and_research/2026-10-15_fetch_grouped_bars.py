#!/usr/bin/env python3
"""Fetch Polygon grouped-daily ADJUSTED bars, one call per NYSE session, into parquet.

READ-ONLY. Writes parquet only into backtesting_and_research/cache/stockmove/bars/
(gitignored). Resumable: a date whose parquet exists with a full ticker count is skipped.
`_fetch_grouped_adj` is copied from scripts/ledger_and_tracking/load_underlying_daily_bars.py
(that script is a one-shot loader and is not run here).

Leakage rule 4 of the 2026-10-15 stock-move pre-registration: count tickers per date. A
short date is an outage. The run stops loud and never fills forward.

Usage:  env -u PROJECT_ID .venv/bin/python backtesting_and_research/2026-10-15_fetch_grouped_bars.py \
            --start 2025-02-03 --end 2026-10-14
The Polygon key comes from POLYGON_API_KEY or Secret Manager. It is never printed.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import date, datetime

import pandas as pd
import pandas_market_calendars as mcal
import requests

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "backtesting_and_research", "cache", "stockmove", "bars")
PROJECT = "profitscout-fida8"
MIN_TICKERS = 7000
SESS = requests.Session()


def _polygon_key() -> str:
    key = os.environ.get("POLYGON_API_KEY", "").strip()
    if key:
        return key
    out = subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret=POLYGON_API_KEY", f"--project={PROJECT}"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def _fetch_grouped_adj(d: date, key: str) -> list[dict]:
    """Polygon grouped-daily ADJUSTED for one date. [] on failure (caller logs)."""
    url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{d.isoformat()}"
    params = {"adjusted": "true", "apiKey": key}
    for attempt in range(3):
        try:
            resp = SESS.get(url, params=params, timeout=60)
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json().get("results", []) or []
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                print(f"  {d}: fetch failed after retries: {type(e).__name__}")
                return []
            time.sleep(2 ** attempt)
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2025-02-03")
    ap.add_argument("--end", required=True, help="last CLOSED NYSE session, YYYY-MM-DD")
    args = ap.parse_args()
    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    sched = mcal.get_calendar("NYSE").schedule(start_date=start, end_date=end)
    days = [d.date() for d in sched.index]
    os.makedirs(OUT, exist_ok=True)
    key = _polygon_key()
    print(f"sessions {days[0]} .. {days[-1]} ({len(days)})", flush=True)
    fetched = skipped = 0
    for i, d in enumerate(days):
        path = os.path.join(OUT, f"{d.isoformat()}.parquet")
        if os.path.exists(path):
            n = len(pd.read_parquet(path, columns=["ticker"]))
            if n >= MIN_TICKERS:
                skipped += 1
                continue
        bars = _fetch_grouped_adj(d, key)
        rows = [{"date": d, "ticker": str(b.get("T", "")).upper(), "open": b.get("o"),
                 "high": b.get("h"), "low": b.get("l"), "close": b.get("c"),
                 "volume": b.get("v"), "vwap": b.get("vw"), "n_trades": b.get("n")}
                for b in bars if b.get("T")]
        if len(rows) < MIN_TICKERS:
            print(f"OUTAGE {d}: {len(rows)} tickers (< {MIN_TICKERS}). Stop.", flush=True)
            return 3
        pd.DataFrame(rows).to_parquet(path, index=False)
        fetched += 1
        if fetched % 25 == 0:
            print(f"  {i + 1}/{len(days)} {d}: {len(rows)} tickers", flush=True)
        time.sleep(0.15)
    print(f"done: fetched {fetched}, skipped {skipped}, sessions {len(days)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
