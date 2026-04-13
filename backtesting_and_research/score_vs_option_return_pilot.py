"""
Pilot: does overnight_score correlate with next-day OPTION premium return?

For each signal row in the last 14 days, fetch the next-trading-day daily bar
for its recommended_contract from Polygon, compute forward return on the
option (not the stock), and bucket by score.

Output: score-bucket table + distribution stats + correlation.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import pandas as pd
import requests
from google.cloud import bigquery

PROJECT = "profitscout-fida8"
LOOKBACK_DAYS = 14
MAX_WORKERS = 24
POLYGON_BASE = "https://api.polygon.io/v2/aggs/ticker"


def get_polygon_key() -> str:
    key = os.getenv("POLYGON_API_KEY")
    if key:
        return key
    out = subprocess.check_output(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret=POLYGON_API_KEY", f"--project={PROJECT}"],
        text=True,
    ).strip()
    return out


def next_trading_day(d: date) -> date:
    n = d + timedelta(days=1)
    while n.weekday() >= 5:
        n += timedelta(days=1)
    return n


def load_signals() -> pd.DataFrame:
    bq = bigquery.Client(project=PROJECT)
    sql = f"""
    SELECT
      scan_date,
      ticker,
      direction,
      overnight_score,
      recommended_contract,
      recommended_mid_price AS entry_mid,
      recommended_dte       AS dte,
      recommended_spread_pct AS spread_pct,
      recommended_expiration AS expiration
    FROM `{PROJECT}.profit_scout.overnight_signals`
    WHERE scan_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {LOOKBACK_DAYS} DAY)
      AND recommended_contract IS NOT NULL
      AND recommended_mid_price > 0
      AND recommended_dte > 1
    """
    df = bq.query(sql).result().to_dataframe()
    df["scan_date"] = pd.to_datetime(df["scan_date"]).dt.date
    df["next_day"]  = df["scan_date"].apply(next_trading_day)
    return df


def fetch_daily_bar(session: requests.Session, key: str, contract: str, day: date) -> dict | None:
    url = f"{POLYGON_BASE}/{contract}/range/1/day/{day.isoformat()}/{day.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 5, "apiKey": key}
    for attempt in range(3):
        try:
            r = session.get(url, params=params, timeout=15)
            if r.status_code == 429:
                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            results = r.json().get("results") or []
            if not results:
                return None
            b = results[0]
            return {
                "next_open":  float(b["o"]),
                "next_high":  float(b["h"]),
                "next_low":   float(b["l"]),
                "next_close": float(b["c"]),
                "next_vol":   int(b.get("v", 0) or 0),
            }
        except Exception as e:
            if attempt == 2:
                print(f"  fetch failed {contract} {day}: {e}", file=sys.stderr)
            time.sleep(0.5)
    return None


def fetch_all(df: pd.DataFrame, key: str) -> pd.DataFrame:
    session = requests.Session()
    rows = df.to_dict("records")
    out: list[dict] = []
    t0 = time.time()

    def work(row):
        bar = fetch_daily_bar(session, key, row["recommended_contract"], row["next_day"])
        return row, bar

    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(work, r) for r in rows]
        for fut in as_completed(futs):
            row, bar = fut.result()
            done += 1
            if done % 500 == 0:
                elapsed = time.time() - t0
                print(f"  {done}/{len(rows)} ({elapsed:.0f}s)", file=sys.stderr)
            if bar is None:
                continue
            merged = {**row, **bar}
            out.append(merged)
    return pd.DataFrame(out)


def summarize(df: pd.DataFrame) -> None:
    entry = df["entry_mid"]
    df["ret_close"] = (df["next_close"] - entry) / entry
    df["ret_high"]  = (df["next_high"]  - entry) / entry
    df["ret_open"]  = (df["next_open"]  - entry) / entry
    df["win_close"] = (df["ret_close"] > 0).astype(int)
    df["win_25pct"] = (df["ret_high"] >= 0.25).astype(int)

    n_total = len(df)
    print(f"\n=== Pilot results: {n_total} contract-days with next-day data ===\n")

    print("Score bucket | N    | mean ret_close | median | % win | % hit +25% | mean ret_high")
    print("-" * 92)
    for score in sorted(df["overnight_score"].dropna().unique()):
        sub = df[df["overnight_score"] == score]
        if len(sub) < 5:
            continue
        print(
            f"    {int(score):>2d}       | {len(sub):>4d} | "
            f"{sub['ret_close'].mean():>+.4f}        | "
            f"{sub['ret_close'].median():>+.4f} | "
            f"{100*sub['win_close'].mean():>5.1f}% | "
            f"{100*sub['win_25pct'].mean():>6.1f}%   | "
            f"{sub['ret_high'].mean():>+.4f}"
        )

    print("\n--- Gate-style buckets ---")
    for label, mask in [
        ("score <= 3  (culled)", df["overnight_score"] <= 3),
        ("score 4-5   (culled)", df["overnight_score"].between(4, 5)),
        ("score >= 6  (passed)", df["overnight_score"] >= 6),
        ("score >= 7         ", df["overnight_score"] >= 7),
    ]:
        sub = df[mask]
        if len(sub) == 0:
            continue
        print(
            f"{label}: n={len(sub):4d}  "
            f"mean_close={sub['ret_close'].mean():+.4f}  "
            f"median={sub['ret_close'].median():+.4f}  "
            f"win%={100*sub['win_close'].mean():5.1f}  "
            f"hit25%={100*sub['win_25pct'].mean():5.1f}  "
            f"mean_high={sub['ret_high'].mean():+.4f}"
        )

    corr_c = df[["overnight_score", "ret_close"]].corr().iloc[0, 1]
    corr_h = df[["overnight_score", "ret_high"]].corr().iloc[0, 1]
    print(f"\nPearson corr(score, ret_close) = {corr_c:+.4f}")
    print(f"Pearson corr(score, ret_high)  = {corr_h:+.4f}")

    by_dir = df.groupby("direction")["ret_close"].agg(["count", "mean", "median"])
    print(f"\nBy direction:\n{by_dir}")


def main():
    key = get_polygon_key()
    print("Loading signals from BigQuery...", file=sys.stderr)
    signals = load_signals()
    print(f"  {len(signals)} rows to fetch", file=sys.stderr)

    print("Fetching next-day option bars from Polygon...", file=sys.stderr)
    enriched = fetch_all(signals, key)
    print(f"  {len(enriched)} rows with data "
          f"({100*len(enriched)/len(signals):.1f}% hit rate)", file=sys.stderr)

    out_path = "/tmp/score_vs_option_return_pilot.parquet"
    enriched.to_parquet(out_path)
    print(f"  saved → {out_path}", file=sys.stderr)

    summarize(enriched)


if __name__ == "__main__":
    main()
