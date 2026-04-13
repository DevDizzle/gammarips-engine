"""Write the BRACKET_SWEEP_V1.md report from the sweep results.

Reads `/tmp/sweep_results_v1.parquet` and `/tmp/sweep_signal_detail_v1.pkl`
and produces `docs/research_reports/BRACKET_SWEEP_V1.md`. Deterministic and
re-runnable: same inputs → byte-identical output.

Sections:
  1. Sweep overview (variants tried, sample sizes)
  2. Top 20 variants by chronological-OOS avg_return
  3. Best variant deep-dive — per premium_score, per recommended_oi quintile,
     per recommended_dte quintile, per direction
  4. Red-flag check — does the best variant concentrate in the
     simulator-artifact buckets the V3.1 decision warned about?
  5. Practical-strategy summary — assuming 1 trade per scan_date (highest
     premium_score), what's the expectancy?

Usage:
    python scripts/research/write_sweep_report_v1.py
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path("/tmp/sweep_results_v1.parquet")
DETAIL_PATH = Path("/tmp/sweep_signal_detail_v1.pkl")
REPORT_PATH = REPO / "docs/research_reports/BRACKET_SWEEP_V1.md"


def fmt_pct(x: float) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "  n/a"
    return f"{x * 100:+7.2f}%"


def fmt_p(x: float) -> str:
    return f"{x * 100:5.1f}%"


def variant_label(row) -> str:
    tgt = "none" if row["target_pct"] < 0 else f"+{int(row['target_pct'] * 100)}%"
    stp = "none" if row["stop_pct"] < 0 else f"-{int(row['stop_pct'] * 100)}%"
    return f"{row['entry_time']} / tgt={tgt} / stop={stp} / hold={int(row['hold_days'])}d"


def section_overview(df: pd.DataFrame) -> str:
    lines = ["## 1. Sweep overview", ""]
    lines.append(f"- **Variants tested:** {len(df)}")
    lines.append(f"- **Min n_executed across variants:** {df['n_executed'].min()}")
    lines.append(f"- **Max n_executed across variants:** {df['n_executed'].max()}")
    lines.append(f"- **Median n_executed:** {int(df['n_executed'].median())}")
    lines.append(f"- **Variants with **positive in-sample avg_return:** "
                 f"{int((df['avg_return'] > 0).sum())} / {len(df)}")
    lines.append(f"- **Variants with **positive OOS avg_return:** "
                 f"{int((df['test_avg'] > 0).sum())} / {len(df)}")
    lines.append("")
    return "\n".join(lines)


def section_top20(df: pd.DataFrame) -> str:
    lines = ["## 2. Top 20 variants by **out-of-sample** avg_return", ""]
    lines.append("Sorted by chronological-holdout test_avg (newer 30% of scan_dates). "
                 "OOS is the only number that matters; in-sample is shown for sanity.")
    lines.append("")
    lines.append("| rank | variant | n | avg | win% | **OOS n** | **OOS avg** | **OOS win%** | OOS targ/stop/to |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    sorted_df = df.sort_values("test_avg", ascending=False).head(20).reset_index(drop=True)
    for i, r in sorted_df.iterrows():
        lines.append(
            f"| {i + 1} | {variant_label(r)} | {int(r['n_executed'])} | "
            f"{fmt_pct(r['avg_return'])} | {fmt_p(r['win_rate'])} | "
            f"{int(r['test_n'])} | **{fmt_pct(r['test_avg'])}** | "
            f"{fmt_p(r['test_win_rate'])} | "
            f"{int(r['test_target'])}/{int(r['test_stop'])}/{int(r['test_timeout'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def section_top_by_dimension(df: pd.DataFrame) -> str:
    lines = ["## 3. Best OOS variant per dimension", ""]
    lines.append("For each value of one dimension, the best OOS variant across all "
                 "other dimensions. This shows whether one knob dominates or whether "
                 "the result is a multi-knob interaction.")
    lines.append("")
    for dim in ["entry_time", "target_pct", "stop_pct", "hold_days"]:
        lines.append(f"### Best per `{dim}`")
        lines.append("")
        lines.append("| value | best variant | OOS avg | OOS win% | OOS n |")
        lines.append("|---|---|---|---|---|")
        for val in sorted(df[dim].unique()):
            sub = df[df[dim] == val]
            if sub.empty:
                continue
            best = sub.sort_values("test_avg", ascending=False).iloc[0]
            label_val = (
                "none" if dim in ("target_pct", "stop_pct") and val < 0
                else (f"+{int(val * 100)}%" if dim == "target_pct"
                      else f"-{int(val * 100)}%" if dim == "stop_pct"
                      else f"{int(val) if dim == 'hold_days' else val}")
            )
            lines.append(
                f"| {label_val} | {variant_label(best)} | "
                f"{fmt_pct(best['test_avg'])} | {fmt_p(best['test_win_rate'])} | "
                f"{int(best['test_n'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def section_best_deep_dive(detail: pd.DataFrame, best_label: str) -> str:
    lines = [f"## 4. Best variant deep-dive: `{best_label}`", ""]
    n = len(detail)
    win = (detail["realized_return_pct"] > 0).mean()
    avg = detail["realized_return_pct"].mean()
    lines.append(f"- n = {n}, all-cohort avg = {fmt_pct(avg)}, win% = {fmt_p(win)}")
    test_n = detail["is_test"].sum()
    if test_n > 0:
        test = detail[detail["is_test"]]
        lines.append(f"- OOS n = {int(test_n)}, OOS avg = {fmt_pct(test['realized_return_pct'].mean())}, "
                     f"OOS win% = {fmt_p((test['realized_return_pct'] > 0).mean())}")
    lines.append("")

    def break_by(col, bucketize=False):
        sub = lines[:]
        sub.append(f"### Breakdown by `{col}`" + (" (quintiles)" if bucketize else ""))
        sub.append("")
        sub.append(f"| {col} | n | avg_return | win% |")
        sub.append("|---|---|---|---|")
        d = detail.dropna(subset=[col]).copy()
        if bucketize:
            try:
                d["__b"] = pd.qcut(d[col], q=5, duplicates="drop")
            except ValueError:
                return ""
            grp_col = "__b"
        else:
            grp_col = col
        grp = d.groupby(grp_col, observed=True).agg(
            n=("realized_return_pct", "size"),
            avg=("realized_return_pct", "mean"),
            wr=("realized_return_pct", lambda x: (x > 0).mean()),
        ).reset_index()
        for _, r in grp.iterrows():
            sub.append(f"| {r[grp_col]} | {int(r['n'])} | {fmt_pct(r['avg'])} | {fmt_p(r['wr'])} |")
        sub.append("")
        return "\n".join(sub[len(lines):])

    lines.append(break_by("premium_score"))
    lines.append(break_by("direction"))
    lines.append(break_by("recommended_oi", bucketize=True))
    lines.append(break_by("recommended_volume", bucketize=True))
    lines.append(break_by("recommended_dte", bucketize=True))
    lines.append(break_by("recommended_spread_pct", bucketize=True))
    lines.append(break_by("recommended_mid_price", bucketize=True))
    return "\n".join(lines)


def section_red_flag(detail: pd.DataFrame) -> str:
    lines = ["## 5. Red-flag check (simulator-artifact concentration)", ""]
    lines.append("Per the V3.1 decision note, the simulator's mid-bar pricing materially "
                 "overstates fillable prices on illiquid contracts. If the best variant "
                 "concentrates its winners in low-OI / high-spread / low-mid-price "
                 "buckets, those wins are likely fictional.")
    lines.append("")

    winners = detail[detail["realized_return_pct"] > 0]
    losers = detail[detail["realized_return_pct"] <= 0]
    if len(winners) == 0:
        lines.append("_No winners — section not applicable._")
        return "\n".join(lines)

    def stat(col):
        return (winners[col].median(), losers[col].median(),
                winners[col].mean(), losers[col].mean())

    lines.append("| feature | winners median | losers median | winners mean | losers mean | flag |")
    lines.append("|---|---|---|---|---|---|")
    for col, lo_is_bad in [
        ("recommended_oi", True),
        ("recommended_volume", True),
        ("recommended_spread_pct", False),
        ("recommended_mid_price", True),
        ("recommended_dte", None),
    ]:
        wm, lm, wma, lma = stat(col)
        flag = ""
        if lo_is_bad is True and wm < lm * 0.5:
            flag = " ⚠ winners much lower"
        elif lo_is_bad is False and wm > lm * 1.5:
            flag = " ⚠ winners much higher"
        lines.append(f"| `{col}` | {wm:.3f} | {lm:.3f} | {wma:.3f} | {lma:.3f} |{flag} |")
    lines.append("")

    # Concrete cohort comparison: how do returns look if we exclude the most
    # suspicious buckets?
    lines.append("**Returns excluding suspicious buckets:**")
    lines.append("")
    lines.append("| filter | n | avg | win% |")
    lines.append("|---|---|---|---|")
    for label, mask in [
        ("ALL", pd.Series([True] * len(detail), index=detail.index)),
        ("oi >= 50", detail["recommended_oi"] >= 50),
        ("oi >= 100", detail["recommended_oi"] >= 100),
        ("oi >= 50 AND vol >= 100", (detail["recommended_oi"] >= 50) & (detail["recommended_volume"] >= 100)),
        ("mid_price >= 1.00", detail["recommended_mid_price"] >= 1.00),
        ("spread_pct <= 0.20", detail["recommended_spread_pct"] <= 0.20),
        ("oi>=50 AND vol>=100 AND mid>=1 AND spread<=0.20",
         (detail["recommended_oi"] >= 50) & (detail["recommended_volume"] >= 100) &
         (detail["recommended_mid_price"] >= 1.00) & (detail["recommended_spread_pct"] <= 0.20)),
    ]:
        sub = detail[mask]
        if len(sub) == 0:
            lines.append(f"| {label} | 0 | n/a | n/a |")
            continue
        lines.append(f"| {label} | {len(sub)} | {fmt_pct(sub['realized_return_pct'].mean())} | "
                     f"{fmt_p((sub['realized_return_pct'] > 0).mean())} |")
    lines.append("")
    return "\n".join(lines)


def section_one_per_week(detail: pd.DataFrame) -> str:
    """Realistic 1-trade-per-scan_date strategy: pick highest premium_score signal."""
    lines = ["## 6. Realistic 1-trade-per-scan_date strategy", ""]
    lines.append("User goal is 1 trade per scan_date (or even 1 per week). For each "
                 "scan_date, pick the highest `premium_score` signal (tiebreak: highest "
                 "`recommended_oi`). This is the realistic execution path under the "
                 "best variant.")
    lines.append("")
    if "scan_date" not in detail.columns:
        lines.append("_Detail data missing scan_date; skipping._")
        return "\n".join(lines)

    # Pick top-1 per scan_date
    picked = (detail.sort_values(["scan_date", "premium_score", "recommended_oi"],
                                  ascending=[True, False, False])
              .groupby("scan_date").head(1))
    n = len(picked)
    avg = picked["realized_return_pct"].mean()
    win = (picked["realized_return_pct"] > 0).mean()
    test = picked[picked["is_test"]]
    lines.append(f"- **Picks:** {n} (one per scan_date)")
    lines.append(f"- **All-cohort avg:** {fmt_pct(avg)}, win% = {fmt_p(win)}")
    if len(test) > 0:
        lines.append(f"- **OOS avg:** {fmt_pct(test['realized_return_pct'].mean())}, "
                     f"OOS win% = {fmt_p((test['realized_return_pct'] > 0).mean())}, "
                     f"OOS n = {len(test)}")
    lines.append("")

    # Cumulative equity assuming $1000 risked per trade
    capital_per_trade = 1000.0
    pnl = picked.sort_values("scan_date")["realized_return_pct"].values * capital_per_trade
    cum_pnl = np.cumsum(pnl)
    if len(cum_pnl) > 0:
        lines.append(f"- **Cumulative P&L** at $1000/trade: ${cum_pnl[-1]:+,.0f} over {n} trades "
                     f"(avg ${pnl.mean():+,.1f}/trade)")
        lines.append(f"- **Max drawdown** in cumulative curve: ${(cum_pnl - np.maximum.accumulate(cum_pnl)).min():+,.0f}")
    lines.append("")
    return "\n".join(lines)


def main():
    df = pd.read_parquet(RESULTS_PATH)
    detail = pd.read_pickle(DETAIL_PATH)

    sorted_df = df.sort_values("test_avg", ascending=False).reset_index(drop=True)
    best = sorted_df.iloc[0]
    best_label = variant_label(best)

    parts = [
        f"# Bracket Sweep V1\n",
        f"**Source bars:** `/tmp/signal_bars_v1.pkl` (cached Polygon minute bars, 15-day window)  \n"
        f"**Sweep results:** `/tmp/sweep_results_v1.parquet`  \n"
        f"**Per-signal detail (best variant):** `/tmp/sweep_signal_detail_v1.pkl`  \n"
        f"**Variants tried:** {len(df)}  \n"
        f"**Best OOS variant:** `{best_label}`\n",
        section_overview(df),
        section_top20(df),
        section_top_by_dimension(df),
        section_best_deep_dive(detail, best_label),
        section_red_flag(detail),
        section_one_per_week(detail),
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(parts) + "\n")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
