"""
V4 bracket simulation using REAL V3 bracket params: +40% TP / -25% SL / 2d timeout.

Cross-check against the actual forward_paper_ledger_v3_hold2 realized P&L.

Execution model (matches forward-paper-trader):
  scan_date = D
  entry     = D+1 open, pay ask  (entry_eff = open * (1 + spread/2))
  TP limit  = entry_eff * 1.40   (triggered if intraday high >= TP on any hold day)
  SL stop   = entry_eff * 0.75   (triggered if intraday low  <= SL on any hold day)
  timeout   = D+3 close, sell bid (exit_eff = close * (1 - spread/2))

With daily OHLC only, we can't see intraday ordering. We report two bounds:
  OPTIMISTIC: TP checked before SL within a day
  PESSIMISTIC: SL checked before TP within a day
If both converge, the answer is robust. A 3rd "neutral" model splits 50/50 when
both trigger same day.
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

TP_PCT = 0.40    # +40%  (real V3 TARGET value)
SL_PCT = 0.25    # -25%  (real V3 STOP value, expressed as magnitude)
HOLD_DAYS = 2    # D+1 entry through D+3 exit (matches V3.1)


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
    sql = f"""
    SELECT
      scan_date,
      ticker,
      direction,
      overnight_score,
      recommended_contract,
      recommended_dte        AS dte,
      recommended_spread_pct AS spread_pct,
      recommended_volume     AS vol,
      recommended_oi         AS oi,
      call_vol_oi_ratio,
      put_vol_oi_ratio
    FROM `{PROJECT}.profit_scout.overnight_signals`
    WHERE direction = 'BULLISH'
      AND recommended_contract IS NOT NULL
      AND recommended_mid_price > 0
      AND recommended_dte > 3
      AND ((recommended_volume >= 100 AND recommended_oi >= 50)
           OR recommended_oi >= 250)
      AND recommended_spread_pct <= 0.40
    """
    df = bq.query(sql).result().to_dataframe()
    df["scan_date"] = pd.to_datetime(df["scan_date"]).dt.date
    df["d1"] = df["scan_date"].apply(next_trading_day)          # entry day
    df["d2"] = df["d1"].apply(next_trading_day)
    df["d3"] = df["d2"].apply(next_trading_day)                 # timeout day
    return df


def fetch_bars(session, key, contract, start: date, end: date):
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
        bars = fetch_bars(session, key, row["recommended_contract"], row["d1"], row["d3"])
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
            d1 = bars.get(row["d1"].isoformat())
            if not d1:
                continue
            d2 = bars.get(row["d2"].isoformat())
            d3 = bars.get(row["d3"].isoformat())
            row.update({
                "d1_o": d1["o"], "d1_h": d1["h"], "d1_l": d1["l"], "d1_c": d1["c"],
                "d2_o": d2["o"] if d2 else None,
                "d2_h": d2["h"] if d2 else None,
                "d2_l": d2["l"] if d2 else None,
                "d2_c": d2["c"] if d2 else None,
                "d3_o": d3["o"] if d3 else None,
                "d3_h": d3["h"] if d3 else None,
                "d3_l": d3["l"] if d3 else None,
                "d3_c": d3["c"] if d3 else None,
            })
            out.append(row)
    return pd.DataFrame(out)


def simulate_bracket(row, tp_first: bool) -> tuple[str, float]:
    """Walk the bracket day by day. tp_first=True is optimistic.

    Returns (exit_reason, net_return_pct).
    """
    s = max(0.0, min(0.8, float(row.get("spread_pct") or 0)))
    entry_eff = row["d1_o"] * (1 + s / 2)
    tp_price = entry_eff * (1 + TP_PCT)
    sl_price = entry_eff * (1 - SL_PCT)

    days = [
        (row.get("d1_h"), row.get("d1_l"), row.get("d1_c")),
        (row.get("d2_h"), row.get("d2_l"), row.get("d2_c")),
        (row.get("d3_h"), row.get("d3_l"), row.get("d3_c")),
    ]

    last_close = None
    for high, low, close in days:
        if high is None or low is None:
            continue
        last_close = close
        hit_tp = high >= tp_price
        hit_sl = low  <= sl_price
        if hit_tp and hit_sl:
            return ("TARGET", TP_PCT) if tp_first else ("STOP", -SL_PCT)
        if hit_tp:
            return ("TARGET", TP_PCT)
        if hit_sl:
            return ("STOP", -SL_PCT)
    # timeout — sell at last available close, pay bid
    if last_close is None:
        return ("NO_DATA", float("nan"))
    exit_eff = last_close * (1 - s / 2)
    return ("TIMEOUT", (exit_eff - entry_eff) / entry_eff)


def run_sim(df: pd.DataFrame, tp_first: bool) -> pd.DataFrame:
    reasons, rets = [], []
    for _, row in df.iterrows():
        reason, ret = simulate_bracket(row, tp_first)
        reasons.append(reason)
        rets.append(ret)
    out = df.copy()
    out["exit_reason"] = reasons
    out["ret"] = rets
    return out


def report(df: pd.DataFrame, label: str) -> None:
    df = df[df["exit_reason"] != "NO_DATA"]
    n = len(df)
    mean = df["ret"].mean()
    med  = df["ret"].median()
    win  = 100 * (df["ret"] > 0).mean()
    dist = df["exit_reason"].value_counts().to_dict()
    by_reason = df.groupby("exit_reason")["ret"].agg(["count", "mean"])
    print(f"\n--- {label} ---")
    print(f"  n={n}  mean={mean:+.4f}  median={med:+.4f}  win%={win:.1f}")
    print(f"  exit distribution: {dist}")
    for reason, stats in by_reason.iterrows():
        print(f"    {reason:>8s}: n={int(stats['count']):>4d}  "
              f"mean_ret={stats['mean']:+.4f}")


def cross_check_ledger():
    bq = bigquery.Client(project=PROJECT)
    sql = """
    SELECT direction, exit_reason,
           COUNT(*) AS n,
           ROUND(AVG(realized_return_pct), 4) AS mean_ret
    FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
    WHERE scan_date BETWEEN "2026-02-21" AND "2026-04-10"
      AND is_skipped = FALSE
      AND realized_return_pct IS NOT NULL
    GROUP BY direction, exit_reason
    ORDER BY direction, exit_reason
    """
    df = bq.query(sql).result().to_dataframe()
    print("\n=== REAL V3 ledger (2026-02-21 .. 2026-04-10) ===")
    print(df.to_string(index=False))
    total_n = int(df["n"].sum())
    weighted_mean = (df["mean_ret"] * df["n"]).sum() / max(total_n, 1)
    print(f"\nTotal n={total_n}, weighted mean realized_return = {weighted_mean:+.4f}")


def main():
    key = get_polygon_key()
    print("Loading bullish-liquidity universe from BQ...", file=sys.stderr)
    df = load_signals()
    print(f"  {len(df)} rows", file=sys.stderr)

    print("Fetching D+1..D+3 daily option bars...", file=sys.stderr)
    enriched = fetch_all(df, key)
    enriched = enriched[enriched["d1_o"].notna()]
    print(f"  {len(enriched)} rows with entry bar", file=sys.stderr)
    enriched.to_parquet("/tmp/v4_bracket_sim.parquet")

    complete = enriched[enriched["d3_c"].notna() | enriched["d2_c"].notna()]
    print(f"  {len(complete)} rows with ≥ 2 day bars (hold window closable)",
          file=sys.stderr)

    print(f"\n{'='*90}")
    print(f"V4 BRACKET SIMULATION  (TP=+{int(TP_PCT*100)}%, SL=-{int(SL_PCT*100)}%, "
          f"timeout=D+{HOLD_DAYS+1} close, BULLISH + liquidity only)")
    print(f"{'='*90}")
    print(f"Universe: {len(complete)} bullish+liquid signals over {complete['scan_date'].nunique()} scan dates")

    opt = run_sim(complete, tp_first=True)
    pes = run_sim(complete, tp_first=False)
    report(opt, "V4 no-gate  OPTIMISTIC (TP-first intraday)")
    report(pes, "V4 no-gate  PESSIMISTIC (SL-first intraday)")

    # V3-equivalent slice (score >= 6) on same universe
    opt_v3 = run_sim(complete[complete["overnight_score"] >= 6], tp_first=True)
    pes_v3 = run_sim(complete[complete["overnight_score"] >= 6], tp_first=False)
    report(opt_v3, "V3-slice score>=6  OPTIMISTIC")
    report(pes_v3, "V3-slice score>=6  PESSIMISTIC")

    # Volume stats
    n_days = complete["scan_date"].nunique()
    print(f"\nVolume: V4 no-gate = {len(complete)/n_days:.0f} trades/day, "
          f"V3-slice = {(complete['overnight_score']>=6).sum()/n_days:.0f} trades/day")

    cross_check_ledger()


if __name__ == "__main__":
    main()
