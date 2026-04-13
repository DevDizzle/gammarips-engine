"""Re-sweep brackets on filtered cohorts.

Reuses precompute_signal / simulate_one from sweep_brackets_v1, but applies a
selection filter to the signal population BEFORE the sweep. The point is to
find the bracket optimum on a population that already has positive expectancy,
since the V1 sweep optimum was found on a 78%-loser cohort and may not
generalize to a filtered (positive) one.

Three cohorts compared:
  baseline   — unfiltered (matches BRACKET_SWEEP_V1.md)
  filt_rrr   — risk_reward_ratio >= 0.42  (highest-n positive single filter)
  filt_combo — risk_reward_ratio >= 0.42 AND enrichment_quality_score <= 6.8
               (top 2-feature combo from WINNING_FILTER_DISCOVERY_V1)

Output: docs/research_reports/BRACKET_SWEEP_V2_FILTERED.md
Run:    python scripts/research/sweep_brackets_filtered_v1.py
"""

from __future__ import annotations

import pickle
import sys
import time
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "research"))
sys.path.insert(0, str(REPO / "forward-paper-trader"))

from sweep_brackets_v1 import (  # noqa: E402
    precompute_signal, simulate_one,
    ENTRY_TIMES, TARGET_PCTS, STOP_PCTS, HOLD_DAYS,
)

PROJECT_ID = "profitscout-fida8"
LABELED_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIM_VERSION = "V3_MECHANICS_2026_04_07"
CACHE_PATH = Path("/tmp/signal_bars_v1.pkl")
REPORT_PATH = REPO / "docs/research_reports/BRACKET_SWEEP_V2_FILTERED.md"

import main as trader  # noqa: E402  # forward-paper-trader/main.py
from datetime import datetime


def load_population(client: bigquery.Client) -> pd.DataFrame:
    sql = f"""
    SELECT
        ticker, scan_date, recommended_strike, recommended_expiration,
        direction, premium_score, recommended_volume, recommended_oi,
        recommended_spread_pct, recommended_dte, recommended_mid_price,
        risk_reward_ratio, enrichment_quality_score, is_tradeable
    FROM `{LABELED_TABLE}`
    WHERE simulator_version = '{SIM_VERSION}'
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND exit_reason != 'FUTURE_TIMEOUT'
    """
    return client.query(sql).to_dataframe()


def build_precomp(cache: dict, df: pd.DataFrame) -> list:
    out = []
    skipped_no_bars = 0
    skipped_no_entry = 0
    t0 = time.time()
    n_total = len(df)
    for i, (_, row) in enumerate(df.iterrows()):
        if i > 0 and i % 200 == 0:
            print(f"    precomp progress: {i}/{n_total} "
                  f"({time.time() - t0:.0f}s, kept={len(out)})", flush=True)
        scan_d = row["scan_date"]
        if isinstance(scan_d, datetime):
            scan_d = scan_d.date()
        key = (row["ticker"], scan_d.isoformat())
        bars = cache.get(key) or []
        if not bars:
            skipped_no_bars += 1
            continue
        entry_day = trader.get_next_trading_day(scan_d)
        exp_d = row["recommended_expiration"]
        if isinstance(exp_d, (pd.Timestamp, datetime)):
            exp_d = exp_d.date()
        meta = {
            "ticker": row["ticker"],
            "scan_date": scan_d,
            "entry_day": entry_day,
            "expiration": exp_d,
            "premium_score": int(row["premium_score"] or 0),
            "direction": row["direction"],
            "recommended_volume": int(row["recommended_volume"] or 0),
            "recommended_oi": int(row["recommended_oi"] or 0),
            "recommended_spread_pct": float(row["recommended_spread_pct"] or 0.0),
            "recommended_dte": int(row["recommended_dte"] or 0),
            "recommended_mid_price": float(row["recommended_mid_price"] or 0.0),
        }
        p = precompute_signal(bars, meta)
        if p is None:
            skipped_no_entry += 1
            continue
        out.append(p)
    print(f"  precomp: {len(out)} signals "
          f"(skipped {skipped_no_bars} no_bars, {skipped_no_entry} no_entry)")
    return out


def run_sweep(precomp: list, label: str) -> pd.DataFrame:
    if not precomp:
        return pd.DataFrame()
    all_dates = sorted({p.scan_date for p in precomp})
    cutoff_idx = int(len(all_dates) * 0.70)
    cutoff = all_dates[cutoff_idx] if cutoff_idx < len(all_dates) else all_dates[-1]
    print(f"  cohort '{label}': {len(precomp)} signals, cutoff={cutoff}")

    variants = list(product(ENTRY_TIMES, TARGET_PCTS, STOP_PCTS, HOLD_DAYS))
    rows = []
    t0 = time.time()
    for vi, (et, tgt, stp, hd) in enumerate(variants):
        rets, rets_test = [], []
        target_n = stop_n = timeout_n = 0
        target_n_test = stop_n_test = timeout_n_test = 0
        for p in precomp:
            out = simulate_one(p, et, tgt, stp, hd)
            if out is None:
                continue
            r = out["realized_return_pct"]
            rets.append(r)
            er = out["exit_reason"]
            if er == "TARGET":
                target_n += 1
            elif er == "STOP":
                stop_n += 1
            else:
                timeout_n += 1
            if p.scan_date >= cutoff:
                rets_test.append(r)
                if er == "TARGET":
                    target_n_test += 1
                elif er == "STOP":
                    stop_n_test += 1
                else:
                    timeout_n_test += 1
        if not rets:
            continue
        a = np.array(rets)
        at = np.array(rets_test) if rets_test else np.array([0.0])
        rows.append({
            "cohort": label,
            "entry_time": et,
            "target_pct": tgt if tgt is not None else -1.0,
            "stop_pct": stp if stp is not None else -1.0,
            "hold_days": hd,
            "n": len(rets),
            "avg": float(a.mean()),
            "win_rate": float((a > 0).mean()),
            "test_n": len(rets_test),
            "test_avg": float(at.mean()),
            "test_win_rate": float((at > 0).mean()),
            "test_target": target_n_test,
            "test_stop": stop_n_test,
            "test_timeout": timeout_n_test,
        })
    print(f"    {len(variants)} variants in {time.time() - t0:.0f}s")
    return pd.DataFrame(rows)


def fmt_pct(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "  n/a"
    return f"{x * 100:+7.2f}%"


def fmt_p(x):
    return f"{x * 100:5.1f}%"


def variant_label(r):
    tgt = "none" if r["target_pct"] < 0 else f"+{int(r['target_pct'] * 100)}%"
    stp = "none" if r["stop_pct"] < 0 else f"-{int(r['stop_pct'] * 100)}%"
    return f"{r['entry_time']} / tgt={tgt} / stop={stp} / hold={int(r['hold_days'])}d"


def render_top(df: pd.DataFrame, k: int = 15) -> str:
    if df.empty:
        return "_(empty cohort)_\n"
    s = df.sort_values("test_avg", ascending=False).head(k).reset_index(drop=True)
    lines = ["| rank | variant | n | avg | win% | **OOS n** | **OOS avg** | **OOS win%** | OOS T/S/TO |",
             "|---|---|---|---|---|---|---|---|---|"]
    for i, r in s.iterrows():
        lines.append(
            f"| {i + 1} | {variant_label(r)} | {int(r['n'])} | "
            f"{fmt_pct(r['avg'])} | {fmt_p(r['win_rate'])} | "
            f"{int(r['test_n'])} | **{fmt_pct(r['test_avg'])}** | "
            f"{fmt_p(r['test_win_rate'])} | "
            f"{int(r['test_target'])}/{int(r['test_stop'])}/{int(r['test_timeout'])} |"
        )
    return "\n".join(lines)


def main():
    print("Loading bar cache…")
    with CACHE_PATH.open("rb") as f:
        cache = pickle.load(f)
    print(f"  cache: {len(cache)} signals")

    print("Loading population from BQ…")
    client = bigquery.Client(project=PROJECT_ID)
    pop = load_population(client)
    print(f"  population: {len(pop)} rows")

    # Build precomp ONCE on the full population (slow: ~7 min for ~2k signals
    # because trading-calendar lookups dominate). Filter after.
    print(f"\n[precomp] building once on {len(pop)} signals (one-time cost)…")
    full_precomp = build_precomp(cache, pop)

    # Build a (ticker, scan_date) -> filter-feature lookup so we can subset
    # the precomp list by cohort filter without rebuilding.
    feat_idx = {(r["ticker"], r["scan_date"]): r for _, r in pop.iterrows()}

    def filter_precomp(predicate) -> list:
        out = []
        for p in full_precomp:
            row = feat_idx.get((p.ticker, p.scan_date))
            if row is None:
                continue
            try:
                if predicate(row):
                    out.append(p)
            except Exception:
                continue
        return out

    cohorts_predicates = {
        "baseline": lambda r: True,
        "filt_rrr": lambda r: pd.notna(r["risk_reward_ratio"])
                              and r["risk_reward_ratio"] >= 0.42,
        "filt_combo": lambda r: pd.notna(r["risk_reward_ratio"])
                                and pd.notna(r["enrichment_quality_score"])
                                and r["risk_reward_ratio"] >= 0.42
                                and r["enrichment_quality_score"] <= 6.8,
    }

    cohort_results: dict[str, pd.DataFrame] = {}
    for name, pred in cohorts_predicates.items():
        sub_precomp = filter_precomp(pred)
        print(f"\n[{name}] {len(sub_precomp)} signals after filter")
        cohort_results[name] = run_sweep(sub_precomp, name)

    parts = ["# Bracket Sweep V2 — Filtered Cohorts\n",
             "Re-runs the V1 sweep grid against three signal selections to test "
             "whether the bracket optimum shifts when the population is pre-filtered "
             "to a positive-expectancy cohort.\n",
             "**Filters:**",
             "- `baseline` — no filter (sanity check vs. BRACKET_SWEEP_V1.md)",
             "- `filt_rrr` — `risk_reward_ratio >= 0.42`",
             "- `filt_combo` — `risk_reward_ratio >= 0.42 AND enrichment_quality_score <= 6.8`\n"]

    for name in ["baseline", "filt_rrr", "filt_combo"]:
        df = cohort_results[name]
        parts.append(f"## Cohort: `{name}`\n")
        if df.empty:
            parts.append("_Empty cohort, skipped._\n")
            continue
        n_uniq = df["n"].iloc[0]
        n_test = df["test_n"].iloc[0]
        parts.append(f"- Signals: {n_uniq} ({n_test} OOS)\n")
        parts.append("### Top 15 by OOS avg\n")
        parts.append(render_top(df, k=15))
        parts.append("")
        best = df.sort_values("test_avg", ascending=False).iloc[0]
        parts.append(f"**Best variant:** `{variant_label(best)}` → "
                     f"OOS avg = {fmt_pct(best['test_avg'])}, "
                     f"OOS win% = {fmt_p(best['test_win_rate'])}, "
                     f"OOS n = {int(best['test_n'])}\n")

    parts.append("## Cross-cohort comparison: best variant per cohort\n")
    parts.append("| cohort | best variant | n | OOS n | OOS avg | OOS win% |")
    parts.append("|---|---|---|---|---|---|")
    for name in ["baseline", "filt_rrr", "filt_combo"]:
        df = cohort_results[name]
        if df.empty:
            parts.append(f"| {name} | (empty) | - | - | - | - |")
            continue
        b = df.sort_values("test_avg", ascending=False).iloc[0]
        parts.append(
            f"| {name} | {variant_label(b)} | {int(b['n'])} | {int(b['test_n'])} | "
            f"**{fmt_pct(b['test_avg'])}** | {fmt_p(b['test_win_rate'])} |"
        )
    parts.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(parts) + "\n")
    print(f"\nWrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
