"""Cache Polygon minute bars for every signal in `signals_labeled_v1`.

For each signal, fetch bars from `entry_day` (first trading day after scan_date)
through `min(entry_day + 15 trading days, expiration_day)`, so any reasonable
hold-window sweep can run against the same cached data without re-hitting
Polygon. Pickled to disk as a dict keyed by (ticker, scan_date_iso).

Skips signals whose entry_day is in the future (no bars to fetch yet).

Usage:
    POLYGON_API_KEY=$(gcloud secrets versions access latest --secret=POLYGON_API_KEY \
        --project=profitscout-fida8) \
    python scripts/research/build_bar_cache_v1.py
"""

import os
import pickle
import sys
import time
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import pytz
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "forward-paper-trader"))
import main as trader  # noqa: E402

PROJECT_ID = "profitscout-fida8"
SOURCE_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
CACHE_PATH = Path("/tmp/signal_bars_v1.pkl")
SIM_VERSION = "V3_MECHANICS_2026_04_07"
MAX_HOLD_TRADING_DAYS = 15  # cap fetch window

est = pytz.timezone("America/New_York")


def fetch_population(client: bigquery.Client) -> pd.DataFrame:
    sql = f"""
    SELECT
        ticker,
        scan_date,
        recommended_strike,
        recommended_expiration,
        direction
    FROM `{SOURCE_TABLE}`
    WHERE simulator_version = '{SIM_VERSION}'
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND exit_reason != 'FUTURE_TIMEOUT'
    ORDER BY scan_date, ticker
    """
    return client.query(sql).to_dataframe()


def main():
    if not os.environ.get("POLYGON_API_KEY"):
        print("ERROR: POLYGON_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    trader.POLYGON_API_KEY = os.environ["POLYGON_API_KEY"].strip()

    client = bigquery.Client(project=PROJECT_ID)
    df = fetch_population(client)
    print(f"Fetching bars for {len(df)} signals…")

    cache: dict = {}
    if CACHE_PATH.exists():
        with CACHE_PATH.open("rb") as f:
            cache = pickle.load(f)
        print(f"Resume: {len(cache)} signals already cached")

    today_et = datetime.now(est).date()
    written = 0

    for i, row in df.iterrows():
        scan_d = row["scan_date"]
        if isinstance(scan_d, datetime):
            scan_d = scan_d.date()
        key = (row["ticker"], scan_d.isoformat())
        if key in cache:
            continue

        entry_day = trader.get_next_trading_day(scan_d)
        if entry_day is None or entry_day >= today_et:
            cache[key] = []
            continue

        exp_d = row["recommended_expiration"]
        if isinstance(exp_d, (pd.Timestamp, datetime)):
            exp_d = exp_d.date()

        # Wider window for the sweep: up to 15 trading days OR contract expiration,
        # whichever is sooner.
        window_end = trader.get_nth_next_trading_day(entry_day, MAX_HOLD_TRADING_DAYS)
        if window_end is None:
            window_end = entry_day
        if exp_d and window_end > exp_d:
            window_end = exp_d
        # Also clip window_end so we don't fetch into the future.
        if window_end >= today_et:
            window_end = trader.get_next_trading_day(today_et)
            window_end = window_end if window_end else today_et

        opt_ticker = trader.build_polygon_ticker(
            row["ticker"], exp_d, row["direction"], float(row["recommended_strike"])
        )
        bars = trader.fetch_minute_bars(opt_ticker, entry_day, window_end)
        time.sleep(0.18)

        cache[key] = bars
        written += 1

        if written % 100 == 0:
            print(f"  {written} new signals fetched (total cache: {len(cache)})")
            with CACHE_PATH.open("wb") as f:
                pickle.dump(cache, f)

    with CACHE_PATH.open("wb") as f:
        pickle.dump(cache, f)
    print(f"Done. Cache size: {len(cache)} signals → {CACHE_PATH}")
    print(f"Cache file size: {CACHE_PATH.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
