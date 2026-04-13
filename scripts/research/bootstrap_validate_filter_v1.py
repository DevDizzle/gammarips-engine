"""Bootstrap-validate the `filt_rrr` strategy from BRACKET_SWEEP_V2_FILTERED.

Strategy under test:
  filter:  risk_reward_ratio >= 0.42
  bracket: 15:55 entry / no target / -20% stop / 3-day hold

Method:
  1. Build per-signal returns under the best bracket on the filtered cohort.
  2. Bootstrap-resample the OOS returns 5000 times. Report 5/50/95 percentiles
     of the bootstrap distribution of OOS avg_return.
  3. Same for full cohort (train + OOS) for sanity.
  4. Compare to a bootstrap of the BASELINE (unfiltered) cohort under the
     same bracket — if the two CIs overlap, the filter doesn't help.
  5. Walk-forward stability: split the OOS cohort into halves chronologically
     and report avg_return per half — if one half is +20 and the other -5,
     the +8.28% headline is unstable.

Caches the precomp to /tmp/precomp_v1.pkl so reruns skip the 7-min build.

Output: docs/research_reports/FILT_RRR_BOOTSTRAP_V1.md
"""

from __future__ import annotations

import pickle
import sys
import time
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "research"))
sys.path.insert(0, str(REPO / "forward-paper-trader"))

from sweep_brackets_v1 import precompute_signal, simulate_one  # noqa: E402
import main as trader  # noqa: E402

PROJECT_ID = "profitscout-fida8"
LABELED_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIM_VERSION = "V3_MECHANICS_2026_04_07"
CACHE_PATH = Path("/tmp/signal_bars_v1.pkl")
PRECOMP_CACHE = Path("/tmp/precomp_v1.pkl")
REPORT_PATH = REPO / "docs/research_reports/FILT_RRR_BOOTSTRAP_V1.md"

BEST_ENTRY = "15:55"
BEST_TARGET = None
BEST_STOP = 0.20
BEST_HOLD = 3

N_BOOT = 5000
RNG = np.random.default_rng(42)


def load_pop_with_features(client: bigquery.Client) -> pd.DataFrame:
    sql = f"""
    SELECT
        ticker, scan_date, recommended_strike, recommended_expiration,
        direction, premium_score, recommended_volume, recommended_oi,
        recommended_spread_pct, recommended_dte, recommended_mid_price,
        risk_reward_ratio
    FROM `{LABELED_TABLE}`
    WHERE simulator_version = '{SIM_VERSION}'
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND exit_reason != 'FUTURE_TIMEOUT'
    """
    return client.query(sql).to_dataframe()


def build_or_load_precomp(cache: dict, pop: pd.DataFrame) -> tuple[list, dict]:
    """Build precomp from scratch (slow) or load from disk cache."""
    if PRECOMP_CACHE.exists():
        print(f"Loading cached precomp from {PRECOMP_CACHE}")
        with PRECOMP_CACHE.open("rb") as f:
            return pickle.load(f)

    print(f"Building precomp from scratch ({len(pop)} signals, ~7 min)…")
    out = []
    feat_idx: dict = {}
    t0 = time.time()
    for i, (_, row) in enumerate(pop.iterrows()):
        if i > 0 and i % 200 == 0:
            print(f"  {i}/{len(pop)} ({time.time() - t0:.0f}s, kept={len(out)})",
                  flush=True)
        scan_d = row["scan_date"]
        if isinstance(scan_d, datetime):
            scan_d = scan_d.date()
        key = (row["ticker"], scan_d.isoformat())
        bars = cache.get(key) or []
        if not bars:
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
            continue
        out.append(p)
        feat_idx[(p.ticker, p.scan_date)] = {
            "risk_reward_ratio": float(row["risk_reward_ratio"] or 0.0),
        }

    print(f"  precomp done: {len(out)} signals in {time.time() - t0:.0f}s")
    print(f"  caching to {PRECOMP_CACHE}")
    with PRECOMP_CACHE.open("wb") as f:
        pickle.dump((out, feat_idx), f)
    return out, feat_idx


def returns_under_best_bracket(precomp: list) -> tuple[np.ndarray, list]:
    """Run the best variant against each precomp signal. Returns (returns, scan_dates)."""
    rets = []
    dates = []
    for p in precomp:
        out = simulate_one(p, BEST_ENTRY, BEST_TARGET, BEST_STOP, BEST_HOLD)
        if out is None:
            continue
        rets.append(out["realized_return_pct"])
        dates.append(p.scan_date)
    return np.array(rets), dates


def bootstrap_ci(values: np.ndarray, n_boot: int = N_BOOT) -> dict:
    if len(values) == 0:
        return {"n": 0, "mean": float("nan"), "p05": float("nan"),
                "p50": float("nan"), "p95": float("nan"),
                "p_positive": float("nan")}
    n = len(values)
    means = np.empty(n_boot)
    for i in range(n_boot):
        idx = RNG.integers(0, n, size=n)
        means[i] = values[idx].mean()
    return {
        "n": n,
        "mean": float(values.mean()),
        "p05": float(np.percentile(means, 5)),
        "p50": float(np.percentile(means, 50)),
        "p95": float(np.percentile(means, 95)),
        "p_positive": float((means > 0).mean()),
    }


def fmt_pct(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "  n/a"
    return f"{x * 100:+7.2f}%"


def main():
    print("Loading bar cache…")
    with CACHE_PATH.open("rb") as f:
        cache = pickle.load(f)
    print(f"  cache: {len(cache)} signals")

    print("Loading population from BQ…")
    client = bigquery.Client(project=PROJECT_ID)
    pop = load_pop_with_features(client)
    print(f"  population: {len(pop)} rows")

    precomp, feat_idx = build_or_load_precomp(cache, pop)

    # ----- baseline cohort -----
    print("\nSimulating baseline (unfiltered) cohort…")
    base_rets, base_dates = returns_under_best_bracket(precomp)
    print(f"  n = {len(base_rets)}")

    # ----- filt_rrr cohort -----
    print("Filtering to risk_reward_ratio >= 0.42…")
    filt_precomp = [
        p for p in precomp
        if (feat_idx.get((p.ticker, p.scan_date), {}).get("risk_reward_ratio", -1)
            >= 0.42)
    ]
    print(f"  filt_rrr precomp: {len(filt_precomp)} signals")
    filt_rets, filt_dates = returns_under_best_bracket(filt_precomp)
    print(f"  n = {len(filt_rets)}")

    # Chronological split — same 70/30 cutoff used in the sweep, computed over
    # the FILTERED cohort's scan_dates so OOS in this report matches the sweep.
    all_filt_dates = sorted(set(filt_dates))
    cutoff_idx = int(len(all_filt_dates) * 0.70)
    cutoff = all_filt_dates[cutoff_idx] if cutoff_idx < len(all_filt_dates) else all_filt_dates[-1]
    print(f"  filt_rrr cutoff: {cutoff}")

    filt_rets = np.array(filt_rets)
    filt_dates_arr = np.array(filt_dates)
    is_test_filt = filt_dates_arr >= cutoff
    filt_oos = filt_rets[is_test_filt]
    filt_train = filt_rets[~is_test_filt]
    print(f"  filt_rrr train n = {len(filt_train)}, OOS n = {len(filt_oos)}")

    # Same cutoff applied to baseline cohort.
    base_dates_arr = np.array(base_dates)
    is_test_base = base_dates_arr >= cutoff
    base_oos = base_rets[is_test_base]

    # ----- bootstraps -----
    print(f"\nRunning {N_BOOT}-sample bootstraps…")
    boot_filt_full = bootstrap_ci(filt_rets)
    boot_filt_oos = bootstrap_ci(filt_oos)
    boot_filt_train = bootstrap_ci(filt_train)
    boot_base_oos = bootstrap_ci(base_oos)

    # ----- walk-forward: split OOS into halves chronologically -----
    if len(filt_oos) >= 20:
        order = np.argsort(filt_dates_arr[is_test_filt])
        filt_oos_sorted = filt_oos[order]
        half = len(filt_oos_sorted) // 2
        oos_first = filt_oos_sorted[:half]
        oos_second = filt_oos_sorted[half:]
        wf_first = bootstrap_ci(oos_first)
        wf_second = bootstrap_ci(oos_second)
    else:
        wf_first = wf_second = None

    # ----- write report -----
    parts = ["# `filt_rrr` Bootstrap Validation\n",
             "Bootstrap CIs and walk-forward stability check for the strategy "
             "candidate identified in BRACKET_SWEEP_V2_FILTERED.md.\n",
             f"**Strategy:** filter `risk_reward_ratio >= 0.42`, bracket "
             f"`{BEST_ENTRY} / no target / -{int(BEST_STOP*100)}% stop / "
             f"{BEST_HOLD}-day hold`\n",
             f"**Bootstrap samples:** {N_BOOT}, RNG seed = 42 (deterministic)\n"]

    parts.append("## 1. Bootstrap CIs on filtered cohort\n")
    parts.append(
        "5/50/95 percentiles are over the bootstrap distribution of mean "
        "`realized_return_pct`. `P(>0)` is the fraction of bootstrap means "
        "that are positive — values close to 1.0 mean the result is robust to "
        "resampling, values near 0.5 mean it could go either way.\n"
    )
    parts.append("| cohort | n | mean | p05 | p50 | p95 | P(>0) |")
    parts.append("|---|---|---|---|---|---|---|")
    for label, b in [("filt_rrr full (train+OOS)", boot_filt_full),
                     ("filt_rrr train only", boot_filt_train),
                     ("**filt_rrr OOS only**", boot_filt_oos)]:
        parts.append(
            f"| {label} | {b['n']} | {fmt_pct(b['mean'])} | "
            f"{fmt_pct(b['p05'])} | {fmt_pct(b['p50'])} | {fmt_pct(b['p95'])} | "
            f"{b['p_positive']:.3f} |"
        )
    parts.append("")

    parts.append("## 2. Comparison to baseline (unfiltered) cohort\n")
    parts.append(
        "Same bootstrap on the unfiltered cohort under the **same** bracket. "
        "If filt_rrr's p05 sits above baseline's p95, the filter is doing real "
        "work. If the CIs overlap, the filter is just noise.\n"
    )
    parts.append("| cohort | n | mean | p05 | p50 | p95 | P(>0) |")
    parts.append("|---|---|---|---|---|---|---|")
    parts.append(
        f"| baseline OOS (no filter) | {boot_base_oos['n']} | "
        f"{fmt_pct(boot_base_oos['mean'])} | {fmt_pct(boot_base_oos['p05'])} | "
        f"{fmt_pct(boot_base_oos['p50'])} | {fmt_pct(boot_base_oos['p95'])} | "
        f"{boot_base_oos['p_positive']:.3f} |"
    )
    parts.append(
        f"| **filt_rrr OOS** | {boot_filt_oos['n']} | "
        f"{fmt_pct(boot_filt_oos['mean'])} | {fmt_pct(boot_filt_oos['p05'])} | "
        f"{fmt_pct(boot_filt_oos['p50'])} | {fmt_pct(boot_filt_oos['p95'])} | "
        f"{boot_filt_oos['p_positive']:.3f} |"
    )
    parts.append("")

    parts.append("## 3. Walk-forward stability (split OOS into halves)\n")
    parts.append(
        "If both halves are positive and CIs overlap, the strategy is "
        "time-stable. If one half is much better than the other, the "
        "+8.28% headline is being driven by a window-specific effect.\n"
    )
    if wf_first and wf_second:
        parts.append("| OOS half | n | mean | p05 | p50 | p95 | P(>0) |")
        parts.append("|---|---|---|---|---|---|---|")
        for lbl, w in [("first half", wf_first), ("second half", wf_second)]:
            parts.append(
                f"| {lbl} | {w['n']} | {fmt_pct(w['mean'])} | "
                f"{fmt_pct(w['p05'])} | {fmt_pct(w['p50'])} | {fmt_pct(w['p95'])} | "
                f"{w['p_positive']:.3f} |"
            )
    else:
        parts.append("_OOS sample too small for half-split._")
    parts.append("")

    parts.append("## 4. Verdict\n")
    p05 = boot_filt_oos["p05"]
    p_pos = boot_filt_oos["p_positive"]
    base_p95 = boot_base_oos["p95"]
    if p05 > 0 and boot_filt_oos["p05"] > base_p95:
        verdict = ("**STRONG.** filt_rrr OOS p05 is positive *and* sits above "
                   "baseline OOS p95 — the filter is doing real work and the "
                   "edge is robust to resampling. Recommend deploying.")
    elif p05 > 0:
        verdict = ("**MODERATE.** filt_rrr OOS p05 is positive (the edge is "
                   "robust to resampling within the cohort), but baseline's CI "
                   "overlaps. The filter helps, but the underlying signal is "
                   "noisier than the headline suggests. Consider deploying with "
                   "smaller position sizing.")
    elif p_pos > 0.8:
        verdict = ("**WEAK.** filt_rrr OOS mean is positive in 80%+ of bootstrap "
                   "resamples but p05 crosses zero. There's a real direction "
                   "but not enough signal-to-noise to bet capital on yet. "
                   "Collect more data before deploying.")
    else:
        verdict = ("**NOT VALIDATED.** The bootstrap distribution is too wide "
                   "to call this an edge. The +8.28% headline is selection "
                   "bias from the multi-cohort bracket sweep. Do not deploy.")
    parts.append(verdict + "\n")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(parts) + "\n")
    print(f"\nWrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
