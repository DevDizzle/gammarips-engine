"""Read-only snapshot of the forward paper ledger.

Prints cohort stats, the option-vs-stock-vs-SPY comparison, and stratifications
by VIX bucket, HV bucket, and direction. **Does NOT rank filters, search for
winners, or suggest changes.** The output is the same shape every run so you
can eyeball it weekly without inviting a filter search.

Run with:
    python scripts/ledger_and_tracking/current_ledger_stats.py
"""

import sys

import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
LEDGER_TABLE = f"{PROJECT_ID}.profit_scout.forward_paper_ledger"


def fmt_pct(x) -> str:
    if pd.isna(x):
        return "   n/a"
    return f"{x * 100:+6.2f}%"


def stat_block(s: pd.Series) -> dict:
    s = s.dropna()
    if len(s) == 0:
        return {"n": 0, "mean": None, "median": None, "win": None}
    return {
        "n": int(len(s)),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "win": float((s > 0).mean()),
    }


def print_pnl_table(df: pd.DataFrame) -> None:
    print("\n--- Option vs Stock vs SPY (cohort-wide) ---")
    print(f"{'Instrument':<32} {'N':>4}  {'mean':>8}  {'median':>8}  {'win%':>6}")
    cols = [
        ("Option return (bracketed)", "realized_return_pct"),
        ("Underlying return 1x (signed)", "underlying_return"),
        ("SPY return over window", "spy_return_over_window"),
    ]
    for label, col in cols:
        if col not in df.columns:
            continue
        b = stat_block(df[col])
        win_str = f"{b['win']*100:5.1f}%" if b["win"] is not None else "  n/a"
        print(f"{label:<32} {b['n']:>4}  {fmt_pct(b['mean'])}  {fmt_pct(b['median'])}  {win_str:>6}")

    if "underlying_return" in df.columns and "spy_return_over_window" in df.columns:
        alpha = df["underlying_return"] - df["spy_return_over_window"]
        b = stat_block(alpha)
        win_str = f"{b['win']*100:5.1f}%" if b["win"] is not None else "  n/a"
        print(f"{'Alpha: underlying - SPY':<32} {b['n']:>4}  {fmt_pct(b['mean'])}  {fmt_pct(b['median'])}  {win_str:>6}")


def print_vix_buckets(df: pd.DataFrame) -> None:
    if "VIX_at_entry" not in df.columns:
        return
    print("\n--- Stratified by VIX at entry ---")
    print(f"{'VIX bucket':<12} {'N':>4}  {'opt mean':>10}  {'stock mean':>10}  {'spy mean':>10}")
    bins = [(0, 20, "<20"), (20, 25, "20-25"), (25, 30, "25-30"), (30, 100, "30+")]
    for lo, hi, label in bins:
        sub = df[(df["VIX_at_entry"] >= lo) & (df["VIX_at_entry"] < hi)]
        if len(sub) == 0:
            print(f"{label:<12} {'0':>4}  {'  n/a':>10}  {'  n/a':>10}  {'  n/a':>10}")
            continue
        opt = sub["realized_return_pct"].dropna()
        stk = sub["underlying_return"].dropna() if "underlying_return" in sub.columns else pd.Series(dtype=float)
        spy = sub["spy_return_over_window"].dropna() if "spy_return_over_window" in sub.columns else pd.Series(dtype=float)
        opt_m = f"{opt.mean()*100:+6.2f}%" if len(opt) else "  n/a"
        stk_m = f"{stk.mean()*100:+6.2f}%" if len(stk) else "  n/a"
        spy_m = f"{spy.mean()*100:+6.2f}%" if len(spy) else "  n/a"
        print(f"{label:<12} {len(sub):>4}  {opt_m:>10}  {stk_m:>10}  {spy_m:>10}")


def print_hv_buckets(df: pd.DataFrame) -> None:
    if "hv_20d_entry" not in df.columns:
        return
    print("\n--- Stratified by HV_20d at entry ---")
    print(f"{'HV bucket':<12} {'N':>4}  {'opt mean':>10}  {'stock mean':>10}")
    bins = [(0, 0.3, "<30%"), (0.3, 0.5, "30-50%"), (0.5, 0.8, "50-80%"), (0.8, 5, "80%+")]
    for lo, hi, label in bins:
        sub = df[(df["hv_20d_entry"] >= lo) & (df["hv_20d_entry"] < hi)]
        if len(sub) == 0:
            continue
        opt = sub["realized_return_pct"].dropna()
        stk = sub["underlying_return"].dropna() if "underlying_return" in sub.columns else pd.Series(dtype=float)
        opt_m = f"{opt.mean()*100:+6.2f}%" if len(opt) else "  n/a"
        stk_m = f"{stk.mean()*100:+6.2f}%" if len(stk) else "  n/a"
        print(f"{label:<12} {len(sub):>4}  {opt_m:>10}  {stk_m:>10}")


def print_direction(df: pd.DataFrame) -> None:
    print("\n--- Stratified by direction ---")
    print(f"{'Direction':<12} {'N':>4}  {'opt mean':>10}  {'stock mean':>10}  {'opt win%':>10}")
    for d in ["BULLISH", "BEARISH"]:
        sub = df[df["direction"] == d]
        if len(sub) == 0:
            continue
        opt = sub["realized_return_pct"].dropna()
        stk = sub["underlying_return"].dropna() if "underlying_return" in sub.columns else pd.Series(dtype=float)
        opt_m = f"{opt.mean()*100:+6.2f}%" if len(opt) else "  n/a"
        stk_m = f"{stk.mean()*100:+6.2f}%" if len(stk) else "  n/a"
        win = f"{(opt > 0).mean()*100:5.1f}%" if len(opt) else "  n/a"
        print(f"{d:<12} {len(sub):>4}  {opt_m:>10}  {stk_m:>10}  {win:>10}")


def print_coverage(df: pd.DataFrame) -> None:
    print("\n--- Column coverage ---")
    total = len(df)
    for col in [
        "underlying_return",
        "spy_return_over_window",
        "hv_20d_entry",
        "VIX_at_entry",
        "vix_5d_delta_entry",
        "iv_rank_entry",
    ]:
        if col not in df.columns:
            print(f"  {col:<30} (column missing)")
            continue
        n = df[col].notna().sum()
        pct = n / total * 100 if total else 0
        print(f"  {col:<30} {n:>3}/{total:<3} ({pct:4.0f}%)")


def main():
    client = bigquery.Client(project=PROJECT_ID)
    sql = f"""
    SELECT *
    FROM `{LEDGER_TABLE}`
    WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
    """
    df = client.query(sql).to_dataframe()

    if df.empty:
        print("Ledger is empty — nothing to report.")
        return

    print(f"\n=== Forward Paper Ledger Snapshot ===")
    print(f"Table: {LEDGER_TABLE}")
    print(f"Executed trades (non-skipped, non-invalid-liquidity): {len(df)}")
    print(f"Date range: {df['scan_date'].min()} → {df['scan_date'].max()}")
    print(f"Unique tickers: {df['ticker'].nunique()}")

    print_pnl_table(df)
    print_direction(df)
    print_vix_buckets(df)
    print_hv_buckets(df)
    print_coverage(df)

    print("\n--- Reminder: do not act on these stats until N >= 100 trades across 2+ VIX regimes. ---\n")


if __name__ == "__main__":
    main()
