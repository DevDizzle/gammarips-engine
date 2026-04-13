"""One-time backfill of benchmarking columns on forward_paper_ledger_v3_hold2.

Populates these columns for every executed row (exit_reason NOT IN
('SKIPPED','INVALID_LIQUIDITY')) that doesn't already have them:

    underlying_entry_price
    underlying_exit_price
    underlying_return
    spy_entry_price
    spy_exit_price
    spy_return_over_window
    hv_20d_entry
    vix_5d_delta_entry
    (iv_rank_entry / iv_percentile_entry left null until vendor is wired)

Cache reuse: stock and SPY bars from /tmp/stock_bars_v1.pkl and
/tmp/spy_bars_v1.pkl (built by scripts/research/relabel_underlying_v1.py) are
used first. Rows not covered by the cache (recent trades) trigger fresh
Polygon fetches.

Idempotent: re-running skips rows that already have underlying_return.

Usage:
    POLYGON_API_KEY=$(gcloud secrets versions access latest \\
        --secret=POLYGON_API_KEY --project=profitscout-fida8) \\
    FMP_API_KEY=$(gcloud secrets versions access latest \\
        --secret=FMP_API_KEY --project=profitscout-fida8) \\
    python scripts/ledger_and_tracking/backfill_benchmarks_v1.py
"""

import os
import pickle
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

import pandas as pd
import pytz
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "forward-paper-trader"))
import main as trader  # noqa: E402
import benchmark_context as bctx  # noqa: E402

PROJECT_ID = "profitscout-fida8"
LEDGER_TABLE = f"{PROJECT_ID}.profit_scout.forward_paper_ledger_v3_hold2"

STOCK_CACHE_PATH = Path("/tmp/stock_bars_v1.pkl")
SPY_CACHE_PATH = Path("/tmp/spy_bars_v1.pkl")

est = pytz.timezone("America/New_York")


def load_stock_cache() -> dict:
    if not STOCK_CACHE_PATH.exists():
        print(f"  (no stock cache at {STOCK_CACHE_PATH}; will fetch fresh for every row)")
        return {}
    with STOCK_CACHE_PATH.open("rb") as f:
        cache = pickle.load(f)
    print(f"  loaded stock cache: {len(cache)} entries")
    return cache


def load_spy_cache_df():
    """Return a flat list of SPY bars covering the broadest cached window."""
    if not SPY_CACHE_PATH.exists():
        return None
    try:
        with SPY_CACHE_PATH.open("rb") as f:
            obj = pickle.load(f)
        df = obj.get("df") if isinstance(obj, dict) else None
        if df is None or df.empty:
            return None
        # Convert DataFrame back to a Polygon-bar-shaped list for the locator fns
        bars = []
        for ts, row in df.iterrows():
            bars.append({"t": int(ts.timestamp() * 1000), "c": float(row["close"])})
        print(f"  loaded SPY cache: {len(bars)} bars, {df.index.min()} → {df.index.max()}")
        return bars
    except Exception as e:
        print(f"  SPY cache load failed ({e}); will fetch fresh")
        return None


def fetch_ledger_rows(client: bigquery.Client) -> pd.DataFrame:
    sql = f"""
    SELECT ticker, scan_date, direction, entry_timestamp, exit_timestamp,
           exit_reason, realized_return_pct
    FROM `{LEDGER_TABLE}`
    WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
      AND underlying_return IS NULL
    ORDER BY scan_date, ticker
    """
    return client.query(sql).to_dataframe()


def ts_utc_to_ms(ts) -> int:
    """BQ timestamp (string or datetime) → ms-epoch integer."""
    if isinstance(ts, str):
        ts = pd.Timestamp(ts)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return int(ts.timestamp() * 1000)


def get_stock_bars(ticker: str, scan_d: date, entry_day: date, end_day: date,
                   stock_cache: dict) -> list:
    """Try the cache first; fall back to a fresh fetch."""
    key = (ticker, scan_d.isoformat())
    if key in stock_cache:
        return stock_cache[key]
    # Fresh fetch for recent trades not in the labeled cohort.
    bars = trader.fetch_minute_bars(ticker, entry_day, end_day)
    time.sleep(0.15)
    return bars


def compute_row_fields(
    row: pd.Series,
    stock_cache: dict,
    spy_bars: list | None,
    vix_by_entry_day: dict,
    hv_by_ticker_day: dict,
) -> dict:
    """Return a dict of the new column values for this ledger row."""
    ticker = row["ticker"]
    scan_d = row["scan_date"]
    if isinstance(scan_d, datetime):
        scan_d = scan_d.date()

    entry_ts = row["entry_timestamp"]
    exit_ts = row["exit_timestamp"]
    if entry_ts is None or exit_ts is None:
        return {}

    entry_ts_ms = ts_utc_to_ms(entry_ts)
    exit_ts_ms = ts_utc_to_ms(exit_ts)
    entry_day = pd.Timestamp(entry_ts).date() if not isinstance(entry_ts, datetime) else entry_ts.date()
    exit_day = pd.Timestamp(exit_ts).date() if not isinstance(exit_ts, datetime) else exit_ts.date()

    out: dict = {}

    # Stock-side
    try:
        stock_bars = get_stock_bars(ticker, scan_d, entry_day, exit_day + timedelta(days=1), stock_cache)
        entry_px = bctx.find_price_at_or_after(stock_bars, entry_ts_ms)
        exit_px = bctx.find_price_at_or_before(stock_bars, exit_ts_ms)
        out["underlying_entry_price"] = entry_px
        out["underlying_exit_price"] = exit_px
        if entry_px and exit_px and entry_px > 0:
            raw = (exit_px - entry_px) / entry_px
            sign = 1.0 if str(row["direction"]).upper() == "BULLISH" else -1.0
            out["underlying_return"] = float(sign * raw)
    except Exception as e:
        print(f"  [{ticker} {scan_d}] stock-side fetch failed: {e}")

    # SPY-side
    if spy_bars:
        try:
            spy_entry = bctx.find_price_at_or_after(spy_bars, entry_ts_ms)
            spy_exit = bctx.find_price_at_or_before(spy_bars, exit_ts_ms)
            out["spy_entry_price"] = spy_entry
            out["spy_exit_price"] = spy_exit
            if spy_entry and spy_exit and spy_entry > 0:
                out["spy_return_over_window"] = float((spy_exit - spy_entry) / spy_entry)
        except Exception as e:
            print(f"  [{ticker} {scan_d}] SPY fetch failed: {e}")

    # HV_20d (cached per (ticker, entry_day))
    hv_key = (ticker, entry_day.isoformat())
    if hv_key in hv_by_ticker_day:
        out["hv_20d_entry"] = hv_by_ticker_day[hv_key]
    else:
        try:
            hv = bctx.fetch_hv_20d(ticker, entry_day)
            hv_by_ticker_day[hv_key] = hv
            out["hv_20d_entry"] = hv
        except Exception as e:
            print(f"  [{ticker} {scan_d}] HV fetch failed: {e}")

    # VIX 5d delta (cached per entry_day via get_regime_context)
    if entry_day in vix_by_entry_day:
        out["vix_5d_delta_entry"] = vix_by_entry_day[entry_day]
    else:
        try:
            _, _, vix_delta = trader.get_regime_context(entry_day)
            vix_by_entry_day[entry_day] = vix_delta
            out["vix_5d_delta_entry"] = vix_delta
        except Exception as e:
            print(f"  [{ticker} {scan_d}] VIX delta fetch failed: {e}")

    return out


def build_update_sql(ticker: str, scan_date: date, fields: dict) -> str | None:
    if not fields:
        return None
    set_parts = []
    for k, v in fields.items():
        if v is None:
            set_parts.append(f"{k} = NULL")
        else:
            set_parts.append(f"{k} = {float(v)}")
    set_clause = ", ".join(set_parts)
    scan_str = scan_date.isoformat() if isinstance(scan_date, date) else str(scan_date)
    return (
        f"UPDATE `{LEDGER_TABLE}` "
        f"SET {set_clause} "
        f"WHERE ticker = '{ticker}' AND scan_date = '{scan_str}'"
    )


def main():
    if not os.environ.get("POLYGON_API_KEY"):
        print("ERROR: POLYGON_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    trader.POLYGON_API_KEY = os.environ["POLYGON_API_KEY"].strip()
    bctx.POLYGON_API_KEY = os.environ["POLYGON_API_KEY"].strip()
    trader.FMP_API_KEY = os.environ.get("FMP_API_KEY", "").strip()

    print("Loading ledger rows to backfill…")
    client = bigquery.Client(project=PROJECT_ID)
    df = fetch_ledger_rows(client)
    print(f"  {len(df)} rows need backfill")
    if df.empty:
        print("Nothing to do.")
        return

    print("\nLoading caches…")
    stock_cache = load_stock_cache()
    spy_bars = load_spy_cache_df()

    vix_by_entry_day: dict[date, float | None] = {}
    hv_by_ticker_day: dict[tuple[str, str], float | None] = {}

    print("\nComputing per-row fields…")
    updates: list[tuple[str, date, dict]] = []
    for i, row in df.iterrows():
        fields = compute_row_fields(row, stock_cache, spy_bars, vix_by_entry_day, hv_by_ticker_day)
        if fields:
            scan_d = row["scan_date"].date() if isinstance(row["scan_date"], datetime) else row["scan_date"]
            updates.append((row["ticker"], scan_d, fields))
            print(f"  {row['ticker']:8s} {scan_d} → { {k: (round(v,4) if isinstance(v,float) else v) for k,v in fields.items()} }")
        else:
            print(f"  {row['ticker']:8s} {row['scan_date']} → SKIPPED (no fields computed)")

    print(f"\n{len(updates)} UPDATE statements to run")
    print("Dry run: first 2 SQL statements for sanity check:")
    for ticker, scan_d, fields in updates[:2]:
        print("  " + (build_update_sql(ticker, scan_d, fields) or ""))

    confirm = os.environ.get("BACKFILL_CONFIRM", "")
    if confirm != "YES":
        print("\nSet BACKFILL_CONFIRM=YES in the environment to execute.")
        print("Aborting without writing.")
        return

    print("\nExecuting UPDATEs…")
    n_ok = 0
    n_fail = 0
    for ticker, scan_d, fields in updates:
        sql = build_update_sql(ticker, scan_d, fields)
        if not sql:
            continue
        try:
            client.query(sql).result()
            n_ok += 1
        except Exception as e:
            print(f"  [{ticker} {scan_d}] UPDATE failed: {e}")
            n_fail += 1
    print(f"Done. {n_ok} rows updated, {n_fail} failed.")


if __name__ == "__main__":
    main()
