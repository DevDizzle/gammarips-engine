"""
Fetch 1-MINUTE option bars for every (contract, entry_day) in
enriched_option_outcomes — RESEARCH cache only. Unblocks the entry-timing
backtest (does our fixed 10:00 ET entry systematically bleed vs an earlier fill?).

Writes a NEW local per-(contract,day) parquet cache. Does NOT touch BigQuery
production tables (read-only SELECT DISTINCT), does NOT modify the live pipeline,
does NOT touch frozen scripts/research/.

Fetch: GET /v2/aggs/ticker/{OPT}/range/1/minute/{day}/{day}
       adjusted=true, sort=asc, limit=50000.

Auth: POLYGON_API_KEY from os.environ at runtime; never logged/written/hardcoded.
  export POLYGON_API_KEY=$(gcloud secrets versions access latest \
      --secret=POLYGON_API_KEY --project=profitscout-fida8)

Resumable: a (contract,day) whose parquet already exists is skipped. Empty
results are cached as a 0-row parquet so dead contract-days aren't re-fetched.
Mirrors fetch_underlying_daily_bars.py request/retry shape.
"""
import os
import time
import datetime
import requests
import pandas as pd
from google.cloud import bigquery

CACHE_DIR = "/home/user/gammarips-engine/backtesting_and_research/cache/poly_minute_option"
BQ_PROJECT = "profitscout-fida8"
BQ_TABLE = "profitscout-fida8.profit_scout.enriched_option_outcomes"

POLY_KEY = os.environ.get("POLYGON_API_KEY", "").strip()
SESS = requests.Session()


def sanitize(contract: str) -> str:
    return contract.replace(":", "_")


def build_pairs():
    bq = bigquery.Client(project=BQ_PROJECT)
    rows = bq.query(
        f"""SELECT DISTINCT recommended_contract AS c, entry_day AS d
            FROM `{BQ_TABLE}`
            WHERE recommended_contract IS NOT NULL AND entry_day IS NOT NULL"""
    ).result()
    pairs = sorted({(r["c"], r["d"].isoformat()) for r in rows})
    print(f"distinct (contract, entry_day) pairs: {len(pairs)}")
    return pairs


def fetch_minute(contract: str, day: str):
    """1-min bars for one option on one session. Returns (results, status)."""
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{contract}/range/1/minute/"
        f"{day}/{day}"
    )
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLY_KEY}
    for attempt in range(4):
        try:
            resp = SESS.get(url, params=params, timeout=30)
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json().get("results", []) or [], resp.status_code
        except Exception as e:
            if attempt == 3:
                return [], getattr(getattr(e, "response", None), "status_code", -1)
            time.sleep(2 ** attempt)
    return [], -1


def bars_to_df(contract, day, bars):
    rows = []
    for b in bars:
        rows.append({
            "ts_utc": datetime.datetime.fromtimestamp(b["t"] / 1000, datetime.timezone.utc),
            "open": b.get("o"), "high": b.get("h"), "low": b.get("l"),
            "close": b.get("c"), "volume": b.get("v"), "vwap": b.get("vw"),
        })
    df = pd.DataFrame(rows, columns=["ts_utc", "open", "high", "low", "close", "volume", "vwap"])
    df["contract"] = contract
    df["entry_day"] = day
    if not df.empty:
        df = df.sort_values("ts_utc").reset_index(drop=True)
    return df


def main():
    if not POLY_KEY:
        raise SystemExit("POLYGON_API_KEY not in env -- inject it at run time.")
    os.makedirs(CACHE_DIR, exist_ok=True)
    pairs = build_pairs()

    n_attempt = n_success = n_fail = n_skip = n_empty = 0
    failed = []
    for i, (contract, day) in enumerate(pairs):
        out_path = os.path.join(CACHE_DIR, f"{sanitize(contract)}__{day}.parquet")
        if os.path.exists(out_path):
            n_skip += 1
            continue
        n_attempt += 1
        bars, status = fetch_minute(contract, day)
        if status not in (200,) and not bars:
            n_fail += 1
            failed.append((contract, day, status))
            time.sleep(0.05)
            continue
        df = bars_to_df(contract, day, bars)
        df.to_parquet(out_path, index=False)  # may be 0-row (cached as 'dead')
        if df.empty:
            n_empty += 1
        else:
            n_success += 1
        time.sleep(0.05)
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{len(pairs)} | ok={n_success} empty={n_empty} "
                  f"fail={n_fail} skip={n_skip}", flush=True)

    print("\n==== DONE ====")
    print(f"pairs={len(pairs)} attempted={n_attempt} ok={n_success} "
          f"empty={n_empty} failed={n_fail} skipped(cached)={n_skip}")
    print(f"cache dir: {CACHE_DIR}")
    if failed:
        print(f"FAILED ({len(failed)}): " +
              ", ".join(f"{c}@{d}({s})" for c, d, s in failed[:40]) +
              (" ..." if len(failed) > 40 else ""))


if __name__ == "__main__":
    main()
