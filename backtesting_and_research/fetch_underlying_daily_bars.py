"""
Fetch split/dividend-ADJUSTED underlying EQUITY daily bars (RESEARCH cache only).

Unblocks a momentum backtest. Writes a NEW local per-ticker parquet cache; does
NOT touch BigQuery production tables (BQ is read-only for the ticker universe),
does NOT modify the live pipeline, does NOT modify any frozen scripts/research/.

Ticker universe = union (deduped, uppercased) of:
  1. distinct `ticker` in backtesting_and_research/analysis_option_pnl.parquet
  2. distinct `ticker` in BigQuery profitscout-fida8.profit_scout.enriched_option_outcomes
     (read-only SELECT DISTINCT, so the cache is reusable for future tests).

Fetch: GET /v2/aggs/ticker/{T}/range/1/day/2024-12-01/2026-06-19?adjusted=true
       sort=asc, limit=50000. next_url pagination handled defensively.

Auth: reads POLYGON_API_KEY from os.environ at runtime; never logged, never
written to disk, never hardcoded. Inject at run time, e.g.:
  export POLYGON_API_KEY=$(gcloud secrets versions access latest \
      --secret=POLYGON_API_KEY --project=profitscout-fida8)

Resumable: a ticker whose {TICKER}.parquet already exists is skipped.

Request/retry shape references backtesting_and_research/fetch_hold_window_bars.py.
"""
import os
import time
import datetime
import requests
import pandas as pd
from google.cloud import bigquery

CACHE_DIR = "/home/user/gammarips-engine/backtesting_and_research/cache/poly_daily_underlying"
PARQUET_UNIVERSE = "/home/user/gammarips-engine/backtesting_and_research/analysis_option_pnl.parquet"
BQ_PROJECT = "profitscout-fida8"
BQ_TABLE = "profitscout-fida8.profit_scout.enriched_option_outcomes"

START_DATE = "2024-12-01"
END_DATE = "2026-06-19"
INSUFFICIENT_BARS = 300  # < this many bars => flag (recent IPO / delisting / thin)

POLY_KEY = os.environ.get("POLYGON_API_KEY", "").strip()
SESS = requests.Session()


def build_universe():
    """Union of parquet tickers + BQ tickers, deduped + uppercased."""
    pq = pd.read_parquet(PARQUET_UNIVERSE, columns=["ticker"])
    pq_tickers = {str(t).strip().upper() for t in pq["ticker"].dropna().unique()}
    print(f"parquet tickers: {len(pq_tickers)}")

    bq = bigquery.Client(project=BQ_PROJECT)
    rows = bq.query(
        f"SELECT DISTINCT ticker FROM `{BQ_TABLE}` WHERE ticker IS NOT NULL"
    ).result()
    bq_tickers = {str(r["ticker"]).strip().upper() for r in rows if r["ticker"]}
    print(f"BQ tickers: {len(bq_tickers)}")

    universe = sorted(t for t in (pq_tickers | bq_tickers) if t)
    print(f"union (deduped, uppercased): {len(universe)} tickers")
    return universe


def fetch_daily(ticker):
    """Adjusted daily bars over [START_DATE, END_DATE]. Returns (results, status).
    Handles next_url pagination defensively (unlikely to trigger at this size).
    Retries 429/5xx with exponential backoff (3 tries)."""
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/"
        f"{START_DATE}/{END_DATE}"
    )
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLY_KEY}
    all_results = []
    last_status = -1
    pages = 0
    while url is not None and pages < 50:
        pages += 1
        ok = False
        for attempt in range(3):
            try:
                resp = SESS.get(url, params=params, timeout=30)
                last_status = resp.status_code
                if resp.status_code == 429 or resp.status_code >= 500:
                    time.sleep(2 ** attempt)  # 1s, 2s, 4s
                    continue
                resp.raise_for_status()
                payload = resp.json()
                all_results.extend(payload.get("results", []) or [])
                # next_url already carries query params except apiKey
                nxt = payload.get("next_url")
                if nxt:
                    url = nxt
                    params = {"apiKey": POLY_KEY}
                else:
                    url = None
                ok = True
                break
            except Exception as e:
                last_status = getattr(getattr(e, "response", None), "status_code", -1)
                if attempt == 2:
                    return all_results, last_status
                time.sleep(2 ** attempt)
        if not ok:
            return all_results, last_status
    return all_results, last_status


def bars_to_df(ticker, bars):
    rows = []
    for b in bars:
        d = datetime.datetime.fromtimestamp(b["t"] / 1000, datetime.timezone.utc).date()
        rows.append(
            {
                "date": d,
                "open": b.get("o"),
                "high": b.get("h"),
                "low": b.get("l"),
                "close": b.get("c"),
                "volume": b.get("v"),
                "ticker": ticker,
            }
        )
    df = pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume", "ticker"])
    if not df.empty:
        df = df.sort_values("date").reset_index(drop=True)
    return df


def main():
    if not POLY_KEY:
        raise SystemExit("POLYGON_API_KEY not in env -- inject it at run time.")

    os.makedirs(CACHE_DIR, exist_ok=True)
    universe = build_universe()

    n_attempt = n_success = n_fail = n_skip = 0
    total_rows = 0
    failed = []
    insufficient = []  # (ticker, nbars)
    cover_min = None
    cover_max = None

    for i, ticker in enumerate(universe):
        out_path = os.path.join(CACHE_DIR, f"{ticker}.parquet")
        if os.path.exists(out_path):
            n_skip += 1
            # account for already-cached coverage/rows so the final report is complete
            try:
                ex = pd.read_parquet(out_path, columns=["date"])
                total_rows += len(ex)
                if len(ex) < INSUFFICIENT_BARS:
                    insufficient.append((ticker, len(ex)))
                if not ex.empty:
                    dmin, dmax = ex["date"].min(), ex["date"].max()
                    cover_min = dmin if cover_min is None else min(cover_min, dmin)
                    cover_max = dmax if cover_max is None else max(cover_max, dmax)
            except Exception:
                pass
            continue

        n_attempt += 1
        bars, status = fetch_daily(ticker)
        if status != 200 and not bars:
            n_fail += 1
            failed.append((ticker, status))
            time.sleep(0.1)
            continue

        df = bars_to_df(ticker, bars)
        df.to_parquet(out_path, index=False)
        n_success += 1
        total_rows += len(df)
        if len(df) < INSUFFICIENT_BARS:
            insufficient.append((ticker, len(df)))
        if not df.empty:
            dmin, dmax = df["date"].min(), df["date"].max()
            cover_min = dmin if cover_min is None else min(cover_min, dmin)
            cover_max = dmax if cover_max is None else max(cover_max, dmax)

        time.sleep(0.1)  # polite pacing
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(universe)} | success={n_success} fail={n_fail} skip={n_skip}")

    print("\n==== DONE ====")
    print(f"universe={len(universe)} attempted={n_attempt} success={n_success} "
          f"failed={n_fail} skipped(cached)={n_skip}")
    print(f"total rows written/cached: {total_rows}")
    print(f"coverage: {cover_min} .. {cover_max}")
    print(f"cache dir: {CACHE_DIR}")
    if failed:
        print(f"FAILED ({len(failed)}): " + ", ".join(f"{t}({s})" for t, s in failed))
    if insufficient:
        insufficient.sort(key=lambda x: x[1])
        print(f"INSUFFICIENT (<{INSUFFICIENT_BARS} bars) ({len(insufficient)}): "
              + ", ".join(f"{t}={n}" for t, n in insufficient))


if __name__ == "__main__":
    main()
