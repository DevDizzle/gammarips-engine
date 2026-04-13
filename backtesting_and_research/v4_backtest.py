"""
V4 backtest: BULLISH-only, liquidity floor, deterministic flags, no Gemini.

Pulls every raw signal from overnight_signals over the available window, applies
the candidate V4 gates, fetches D+1 (entry day) and D+3 (2d hold timeout) option
bars from Polygon, applies realistic friction, and produces head-to-head tables
against the current V3 gate on the same universe.

Execution model matches forward-paper-trader:
  scan_date = D
  entry     = D+1 open   (next trading day)
  exit_1d   = D+1 close  (hold_days=1)
  exit_2d   = D+3 close  (hold_days=2, matches V3.1)
  peak      = max high over D+1..D+3

Friction: buy at open*(1+spread/2), sell at close*(1-spread/2).
Spread_pct is taken from scan-day row; assumed symmetric on exit (conservative).
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
MAX_WORKERS = 32
POLYGON_BASE = "https://api.polygon.io/v2/aggs/ticker"


def get_polygon_key() -> str:
    key = os.getenv("POLYGON_API_KEY")
    if key:
        return key
    return subprocess.check_output(
        ["gcloud", "secrets", "versions", "access", "latest",
         "--secret=POLYGON_API_KEY", f"--project={PROJECT}"],
        text=True,
    ).strip()


def next_trading_day(d: date) -> date:
    n = d + timedelta(days=1)
    while n.weekday() >= 5:
        n += timedelta(days=1)
    return n


def nth_trading_day(d: date, n: int) -> date:
    cur = d
    for _ in range(n):
        cur = next_trading_day(cur)
    return cur


def load_signals() -> pd.DataFrame:
    bq = bigquery.Client(project=PROJECT)
    # Pull the whole history we have. We filter BULLISH + liquidity in SQL.
    sql = f"""
    SELECT
      scan_date,
      ticker,
      direction,
      overnight_score,
      recommended_contract,
      recommended_mid_price  AS entry_mid_scan,
      recommended_dte        AS dte,
      recommended_spread_pct AS spread_pct,
      recommended_volume     AS vol,
      recommended_oi         AS oi,
      recommended_expiration AS expiration,
      call_vol_oi_ratio,
      put_vol_oi_ratio
    FROM `{PROJECT}.profit_scout.overnight_signals`
    WHERE direction = 'BULLISH'
      AND recommended_contract IS NOT NULL
      AND recommended_mid_price > 0
      AND recommended_dte > 2
      AND ((recommended_volume >= 100 AND recommended_oi >= 50)
           OR recommended_oi >= 250)
      AND recommended_spread_pct <= 0.40
    """
    df = bq.query(sql).result().to_dataframe()
    df["scan_date"] = pd.to_datetime(df["scan_date"]).dt.date
    df["entry_day"]   = df["scan_date"].apply(next_trading_day)
    df["exit_1d_day"] = df["entry_day"]  # close of entry day
    df["exit_2d_day"] = df["entry_day"].apply(lambda d: nth_trading_day(d, 2))
    return df


def fetch_bar_range(session, key, contract, start: date, end: date):
    """Returns a dict keyed by ISO date → {open,high,low,close,vol}."""
    url = f"{POLYGON_BASE}/{contract}/range/1/day/{start.isoformat()}/{end.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 10, "apiKey": key}
    for attempt in range(3):
        try:
            r = session.get(url, params=params, timeout=15)
            if r.status_code == 429:
                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            out = {}
            for b in r.json().get("results") or []:
                d = pd.Timestamp(b["t"], unit="ms", tz="UTC").tz_convert("US/Eastern").date()
                out[d.isoformat()] = {
                    "o": float(b["o"]), "h": float(b["h"]),
                    "l": float(b["l"]), "c": float(b["c"]),
                    "v": int(b.get("v", 0) or 0),
                }
            return out
        except Exception:
            if attempt == 2:
                return None
            time.sleep(0.5)
    return None


def fetch_all(df: pd.DataFrame, key: str) -> pd.DataFrame:
    session = requests.Session()
    rows = df.to_dict("records")
    out: list[dict] = []
    t0 = time.time()

    def work(row):
        bars = fetch_bar_range(
            session, key, row["recommended_contract"],
            row["entry_day"], row["exit_2d_day"],
        )
        return row, bars

    done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(work, r) for r in rows]
        for fut in as_completed(futs):
            row, bars = fut.result()
            done += 1
            if done % 1000 == 0:
                print(f"  {done}/{len(rows)} ({time.time()-t0:.0f}s)", file=sys.stderr)
            if not bars:
                continue
            entry_iso = row["entry_day"].isoformat()
            exit1_iso = row["exit_1d_day"].isoformat()
            exit2_iso = row["exit_2d_day"].isoformat()
            entry_bar = bars.get(entry_iso)
            if not entry_bar:
                continue
            row["entry_open"]  = entry_bar["o"]
            row["entry_close"] = entry_bar["c"]
            row["entry_high"]  = entry_bar["h"]
            exit1 = bars.get(exit1_iso) or entry_bar
            row["exit_1d_close"] = exit1["c"]
            row["exit_1d_high"]  = exit1["h"]
            exit2 = bars.get(exit2_iso)
            if exit2:
                row["exit_2d_close"] = exit2["c"]
                # peak high across any day in window
                row["peak_high"] = max(b["h"] for b in bars.values())
            else:
                row["exit_2d_close"] = None
                row["peak_high"] = max((b["h"] for b in bars.values()), default=None)
            out.append(row)
    return pd.DataFrame(out)


def apply_friction(df: pd.DataFrame) -> pd.DataFrame:
    s = df["spread_pct"].fillna(0).clip(lower=0, upper=0.8)
    buy_eff = df["entry_open"] * (1 + s / 2)

    def ret(exit_col):
        exit_eff = df[exit_col] * (1 - s / 2)
        return (exit_eff - buy_eff) / buy_eff

    df["ret_1d_fric"]   = ret("exit_1d_close")
    df["ret_2d_fric"]   = ret("exit_2d_close")
    df["ret_peak_fric"] = ret("peak_high")
    df["win_1d"]   = (df["ret_1d_fric"]   > 0).astype(int)
    df["win_2d"]   = (df["ret_2d_fric"]   > 0).astype(int)
    df["hit_25_peak"] = (df["ret_peak_fric"] >= 0.25).astype(int)
    df["hit_50_peak"] = (df["ret_peak_fric"] >= 0.50).astype(int)
    df["bull_flow_v4"] = (df["call_vol_oi_ratio"].fillna(0) > 1.5).astype(int)
    return df


def summarize(df: pd.DataFrame) -> None:
    print(f"\n=== Dataset: {len(df)} BULLISH rows, post-liquidity-gate ===")
    print(f"With valid D+1 entry bar: {df['entry_open'].notna().sum()}")
    print(f"With valid D+3 exit bar (2d hold complete): {df['exit_2d_close'].notna().sum()}")

    # ---- 1-day hold table ----
    df1 = df[df["exit_1d_close"].notna()].copy()
    print(f"\n{'='*90}")
    print(f"ONE-DAY HOLD  (n={len(df1)})")
    print(f"{'='*90}")
    gates_1d = [
        ("V3 baseline: overnight_score >= 6          ", df1["overnight_score"] >= 6),
        ("V4 no gate:  BULLISH + liquidity only      ", pd.Series(True, index=df1.index)),
        ("V4 bull_flow: + call_vol_oi_ratio > 1.5    ", df1["bull_flow_v4"] == 1),
        ("V4 NOT bull_flow (the rest)                ", df1["bull_flow_v4"] == 0),
    ]
    _print_table(df1, gates_1d, "1d")

    # ---- 2-day hold table ----
    df2 = df[df["exit_2d_close"].notna()].copy()
    print(f"\n{'='*90}")
    print(f"TWO-DAY HOLD  (n={len(df2)})  — matches V3.1 HOLD_DAYS=2")
    print(f"{'='*90}")
    gates_2d = [
        ("V3 baseline: overnight_score >= 6          ", df2["overnight_score"] >= 6),
        ("V4 no gate:  BULLISH + liquidity only      ", pd.Series(True, index=df2.index)),
        ("V4 bull_flow: + call_vol_oi_ratio > 1.5    ", df2["bull_flow_v4"] == 1),
        ("V4 NOT bull_flow (the rest)                ", df2["bull_flow_v4"] == 0),
    ]
    _print_table(df2, gates_2d, "2d")

    # ---- Score-bucket monotonicity check on the full universe (2d) ----
    print(f"\n{'='*90}")
    print("Score-bucket check (BULLISH, 2d hold): does overnight_score matter at all?")
    print(f"{'='*90}")
    print(f"{'score':>6} | {'n':>5} | {'mean_2d':>10} | {'med':>8} | "
          f"{'win%':>6} | {'hit25%':>7} | {'mean_peak':>10}")
    for sc in sorted(df2["overnight_score"].dropna().unique()):
        sub = df2[df2["overnight_score"] == sc]
        if len(sub) < 10:
            continue
        print(f"{int(sc):>6d} | {len(sub):>5d} | "
              f"{sub['ret_2d_fric'].mean():>+9.4f}  | "
              f"{sub['ret_2d_fric'].median():>+7.4f} | "
              f"{100*sub['win_2d'].mean():>5.1f}% | "
              f"{100*sub['hit_25_peak'].mean():>6.1f}% | "
              f"{sub['ret_peak_fric'].mean():>+9.4f}")

    # ---- Volume counter: how many trades per day would each V4 gate generate? ----
    print(f"\n{'='*90}")
    print("Trades-per-scan-date volume (2d complete subset):")
    print(f"{'='*90}")
    per_day_v3  = df2[df2["overnight_score"] >= 6].groupby("scan_date").size()
    per_day_v4  = df2.groupby("scan_date").size()
    per_day_bf  = df2[df2["bull_flow_v4"] == 1].groupby("scan_date").size()
    summary = pd.DataFrame({
        "V3_score>=6": per_day_v3,
        "V4_bullish+liquidity": per_day_v4,
        "V4_bull_flow": per_day_bf,
    }).fillna(0).astype(int)
    print(summary)
    print(f"\nMean trades/day:")
    print(f"  V3 (score>=6):        {summary['V3_score>=6'].mean():.1f}")
    print(f"  V4 (bullish+liq):     {summary['V4_bullish+liquidity'].mean():.1f}")
    print(f"  V4 (+bull_flow):      {summary['V4_bull_flow'].mean():.1f}")


def _print_table(df, gates, suffix):
    col = f"ret_{suffix}_fric"
    win_col = f"win_{suffix}"
    print(f"{'Gate':<44} | {'n':>5} | {'mean':>9} | {'med':>8} | "
          f"{'win%':>6} | {'hit25%':>7} | {'hit50%':>7} | {'mean_peak':>10}")
    print("-" * 120)
    for label, mask in gates:
        sub = df[mask]
        if len(sub) == 0:
            print(f"{label:<44} | {'(empty)':>5}")
            continue
        print(f"{label:<44} | "
              f"{len(sub):>5d} | "
              f"{sub[col].mean():>+8.4f} | "
              f"{sub[col].median():>+7.4f} | "
              f"{100*sub[win_col].mean():>5.1f}% | "
              f"{100*sub['hit_25_peak'].mean():>6.1f}% | "
              f"{100*sub['hit_50_peak'].mean():>6.1f}% | "
              f"{sub['ret_peak_fric'].mean():>+9.4f}")


def main():
    key = get_polygon_key()
    print("Loading BULLISH signals post-liquidity from BQ...", file=sys.stderr)
    df = load_signals()
    print(f"  {len(df)} rows to fetch", file=sys.stderr)

    print("Fetching day+1..day+3 option bars from Polygon...", file=sys.stderr)
    enriched = fetch_all(df, key)
    print(f"  {len(enriched)} rows with at least D+1 bar", file=sys.stderr)

    enriched = apply_friction(enriched)
    out_path = "/tmp/v4_backtest.parquet"
    enriched.to_parquet(out_path)
    print(f"  saved → {out_path}", file=sys.stderr)

    summarize(enriched)


if __name__ == "__main__":
    main()
