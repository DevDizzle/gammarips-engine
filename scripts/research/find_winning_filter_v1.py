"""Search `signals_labeled_v1` for filters that produce a profitable cohort.

Uses per-signal returns from the best bracket variant identified by the V1
sweep (`/tmp/sweep_signal_detail_v1.pkl`, bracket `15:55 / no target / -20%
stop / 3-day hold`) joined to the full feature set in `signals_labeled_v1`.

Searches:
  1. Univariate numeric thresholds at deciles, both directions (>=, <=)
  2. Categorical / boolean breakdowns
  3. Top-K univariate filters intersected pairwise
  4. Production-filter audit (premium_score >= 2 AND is_tradeable)

Headline metric: out-of-sample (chronological holdout, newer 30%) avg_return,
with a minimum-n floor to suppress overfit candidates.

Output: docs/research_reports/WINNING_FILTER_DISCOVERY_V1.md  (overwritten)
Run: python scripts/research/find_winning_filter_v1.py
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
PROJECT_ID = "profitscout-fida8"
LABELED_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIM_VERSION = "V3_MECHANICS_2026_04_07"
DETAIL_PATH = Path("/tmp/sweep_signal_detail_v1.pkl")
REPORT_PATH = REPO / "docs/research_reports/WINNING_FILTER_DISCOVERY_V1.md"

# Floors. A filter must beat both before being reported as a candidate.
MIN_N_TOTAL = 100
MIN_N_OOS = 30

# Numeric features to scan. Outcome / metadata columns are excluded.
NUMERIC_FEATURES = [
    "enrichment_quality_score", "reversal_probability", "mean_reversion_risk",
    "atr_14", "rsi_14", "ema_21", "recommended_delta", "recommended_volume",
    "macd", "recommended_oi", "macd_hist", "recommended_vega", "recommended_theta",
    "overnight_score", "recommended_mid_price", "recommended_gamma", "sma_50",
    "call_dollar_volume", "contract_score", "recommended_spread_pct",
    "put_dollar_volume", "put_vol_oi_ratio", "put_active_strikes",
    "recommended_dte", "call_uoa_depth", "catalyst_score", "recommended_iv",
    "underlying_price", "call_vol_oi_ratio", "atr_normalized_move",
    "price_change_pct", "risk_reward_ratio", "call_active_strikes",
    "put_uoa_depth", "close_loc", "dist_from_low", "dist_from_high",
    "stochd_14_3_3", "high_52w", "low_52w", "support", "resistance",
]

CATEGORICAL_FEATURES = [
    "direction", "flow_intent", "catalyst_type",
    # NOTE: `outcome_tier` and `is_win` are LABELS (derived from realized
    # return), not features. Including them = look-ahead leakage. Excluded.
]

BOOLEAN_FEATURES = [
    "premium_bear_flow", "premium_bull_flow", "is_tradeable", "golden_cross",
    "above_sma_50", "premium_high_rr", "is_premium_signal", "premium_high_atr",
    "premium_hedge", "above_sma_200", "move_overdone",
]

INT_FEATURES_AS_CATEGORICAL = ["premium_score"]


@dataclass
class FilterResult:
    label: str
    n: int
    n_oos: int
    avg: float
    win_rate: float
    avg_oos: float
    win_rate_oos: float

    @property
    def is_candidate(self) -> bool:
        return self.n >= MIN_N_TOTAL and self.n_oos >= MIN_N_OOS


def evaluate(df: pd.DataFrame, mask: pd.Series, label: str) -> FilterResult:
    sub = df[mask]
    sub_oos = sub[sub["is_test"]]
    return FilterResult(
        label=label,
        n=len(sub),
        n_oos=len(sub_oos),
        avg=float(sub["realized_return_pct"].mean()) if len(sub) else float("nan"),
        win_rate=float((sub["realized_return_pct"] > 0).mean()) if len(sub) else float("nan"),
        avg_oos=float(sub_oos["realized_return_pct"].mean()) if len(sub_oos) else float("nan"),
        win_rate_oos=float((sub_oos["realized_return_pct"] > 0).mean()) if len(sub_oos) else float("nan"),
    )


def fmt_pct(x: float) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "    n/a"
    return f"{x * 100:+7.2f}%"


def fmt_p(x: float) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "  n/a"
    return f"{x * 100:5.1f}%"


def load_data() -> pd.DataFrame:
    detail = pd.read_pickle(DETAIL_PATH)
    detail["scan_date"] = pd.to_datetime(detail["scan_date"]).dt.date

    client = bigquery.Client(project=PROJECT_ID)
    feature_cols = (
        NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOLEAN_FEATURES
        + INT_FEATURES_AS_CATEGORICAL + ["ticker", "scan_date"]
    )
    cols_sql = ", ".join(f"`{c}`" for c in feature_cols)
    sql = f"""
    SELECT {cols_sql}
    FROM `{LABELED_TABLE}`
    WHERE simulator_version = '{SIM_VERSION}'
    """
    feats = client.query(sql).to_dataframe()
    feats["scan_date"] = pd.to_datetime(feats["scan_date"]).dt.date

    df = detail.merge(feats, on=["ticker", "scan_date"], how="left",
                      suffixes=("", "_f"))
    print(f"Loaded {len(df)} signals (test cohort: {df['is_test'].sum()})")
    return df


def search_univariate_numeric(df: pd.DataFrame) -> list[FilterResult]:
    results: list[FilterResult] = []
    deciles = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    for col in NUMERIC_FEATURES:
        if col not in df.columns:
            continue
        vals = df[col].dropna()
        if len(vals) < MIN_N_TOTAL:
            continue
        for q in deciles:
            try:
                t = float(vals.quantile(q))
            except Exception:
                continue
            for op, mask_fn, sym in [
                (">=", lambda c, t: df[c] >= t, ">="),
                ("<=", lambda c, t: df[c] <= t, "<="),
            ]:
                mask = mask_fn(col, t)
                results.append(evaluate(df, mask.fillna(False),
                                        f"`{col}` {sym} {t:.4g} (q{int(q*100)})"))
    return results


def search_categorical(df: pd.DataFrame) -> list[FilterResult]:
    results: list[FilterResult] = []
    for col in CATEGORICAL_FEATURES + INT_FEATURES_AS_CATEGORICAL:
        if col not in df.columns:
            continue
        for val, sub in df.groupby(col, dropna=True):
            results.append(evaluate(df, df[col] == val, f"`{col}` == {val!r}"))
    for col in BOOLEAN_FEATURES:
        if col not in df.columns:
            continue
        for val in [True, False]:
            results.append(evaluate(df, df[col] == val, f"`{col}` == {val}"))
    return results


def search_pairs(df: pd.DataFrame, top_filters: list[FilterResult],
                 univariate_masks: dict) -> list[FilterResult]:
    results: list[FilterResult] = []
    labels = [f.label for f in top_filters]
    for a, b in combinations(labels, 2):
        mask = univariate_masks[a] & univariate_masks[b]
        results.append(evaluate(df, mask, f"{a}  AND  {b}"))
    return results


def build_univariate_masks(df: pd.DataFrame) -> dict:
    """Re-derive masks for the univariate filters so we can intersect them."""
    masks: dict = {}
    deciles = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    for col in NUMERIC_FEATURES:
        if col not in df.columns:
            continue
        vals = df[col].dropna()
        if len(vals) < MIN_N_TOTAL:
            continue
        for q in deciles:
            try:
                t = float(vals.quantile(q))
            except Exception:
                continue
            masks[f"`{col}` >= {t:.4g} (q{int(q*100)})"] = (df[col] >= t).fillna(False)
            masks[f"`{col}` <= {t:.4g} (q{int(q*100)})"] = (df[col] <= t).fillna(False)
    for col in CATEGORICAL_FEATURES + INT_FEATURES_AS_CATEGORICAL:
        if col not in df.columns:
            continue
        for val in df[col].dropna().unique():
            masks[f"`{col}` == {val!r}"] = df[col] == val
    for col in BOOLEAN_FEATURES:
        if col not in df.columns:
            continue
        for val in [True, False]:
            masks[f"`{col}` == {val}"] = df[col] == val
    return masks


def render_table(rows: list[FilterResult]) -> str:
    out = ["| filter | n | OOS n | avg | win% | **OOS avg** | **OOS win%** |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(
            f"| {r.label} | {r.n} | {r.n_oos} | {fmt_pct(r.avg)} | {fmt_p(r.win_rate)} | "
            f"**{fmt_pct(r.avg_oos)}** | **{fmt_p(r.win_rate_oos)}** |"
        )
    return "\n".join(out)


def main():
    df = load_data()

    # Baseline cohort.
    baseline = evaluate(df, pd.Series(True, index=df.index), "ALL (no filter)")
    production = evaluate(
        df,
        ((df["premium_score"] >= 2) & (df["is_tradeable"] == True)).fillna(False),  # noqa: E712
        "PRODUCTION (`premium_score >= 2 AND is_tradeable`)",
    )

    print("Searching univariate numeric filters…")
    uni_num = search_univariate_numeric(df)
    print(f"  {len(uni_num)} candidates")

    print("Searching categorical / boolean filters…")
    cat = search_categorical(df)
    print(f"  {len(cat)} candidates")

    all_uni = [r for r in uni_num + cat if r.is_candidate]
    all_uni.sort(key=lambda r: r.avg_oos, reverse=True)
    print(f"  {len(all_uni)} survive n>={MIN_N_TOTAL}, OOS n>={MIN_N_OOS}")

    print("Searching 2-feature combinations of top 20 univariate filters…")
    masks = build_univariate_masks(df)
    top20 = all_uni[:20]
    pairs = [r for r in search_pairs(df, top20, masks) if r.is_candidate]
    pairs.sort(key=lambda r: r.avg_oos, reverse=True)
    print(f"  {len(pairs)} pair candidates")

    # ----- write report -----
    parts: list[str] = []
    parts.append("# Winning Filter Discovery V1\n")
    parts.append(
        f"**Source per-signal returns:** `/tmp/sweep_signal_detail_v1.pkl` (bracket: `15:55 / no target / -20% stop / 3-day hold`)  \n"
        f"**Source features:** `{LABELED_TABLE}`  \n"
        f"**Cohort size:** {len(df)} signals ({df['is_test'].sum()} OOS)  \n"
        f"**Bracket source:** `BRACKET_SWEEP_V1.md` best variant  \n"
        f"**Filter floor:** n ≥ {MIN_N_TOTAL} total AND OOS n ≥ {MIN_N_OOS}  \n"
    )

    parts.append("## 1. Baselines\n")
    parts.append(render_table([baseline, production]))
    parts.append("")
    delta = (production.avg_oos - baseline.avg_oos) * 100
    parts.append(
        f"_Production filter delta vs. unfiltered (OOS avg): "
        f"**{delta:+.2f} percentage points**._  "
        f"{'Negative = production filter is destroying edge.' if delta < 0 else 'Positive = production filter is adding edge.'}\n"
    )

    parts.append("## 2. Top 30 univariate filters by OOS avg_return\n")
    parts.append(
        "All numeric/categorical/boolean filters that survived the n-floor, "
        "ranked by chronological-holdout OOS avg_return. The top of this list "
        "is where any single-feature edge lives.\n"
    )
    parts.append(render_table(all_uni[:30]))
    parts.append("")

    parts.append("## 3. Bottom 10 univariate filters (anti-edge — what to AVOID)\n")
    parts.append(
        "Same set, ranked the opposite way. If any of these match the production "
        "filter conditions, that's a smoking gun for why production loses money.\n"
    )
    parts.append(render_table(all_uni[-10:][::-1]))
    parts.append("")

    parts.append("## 4. Top 30 two-feature combinations\n")
    parts.append(
        "Pairwise intersections of the top 20 univariate filters. Combinations "
        "that survive the n-floor (most won't — intersections shrink the cohort fast).\n"
    )
    if pairs:
        parts.append(render_table(pairs[:30]))
    else:
        parts.append("_No pair survived the n-floor._")
    parts.append("")

    parts.append("## 5. Recommendation\n")
    if all_uni and all_uni[0].avg_oos > 0:
        best = all_uni[0]
        best_pair = pairs[0] if pairs and pairs[0].avg_oos > best.avg_oos else None
        rec = best_pair if best_pair else best
        parts.append(
            f"**Best filter found:** `{rec.label}`\n"
            f"- n = {rec.n} ({rec.n_oos} OOS)\n"
            f"- Full-cohort avg = {fmt_pct(rec.avg)}, win% = {fmt_p(rec.win_rate)}\n"
            f"- **OOS avg = {fmt_pct(rec.avg_oos)}, OOS win% = {fmt_p(rec.win_rate_oos)}**\n"
            f"\n_Compare to production OOS avg = {fmt_pct(production.avg_oos)}._\n"
        )
    else:
        parts.append(
            "**No filter produced a positive OOS avg_return at the n-floor.** "
            "This means there is no single-feature or two-feature subset of "
            "`signals_labeled_v1` that, under the best bracket from the V1 sweep, "
            "is profitable on the chronological-holdout cohort with reasonable n. "
            "The signal generator itself — not the filter — is the binding constraint.\n"
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(parts) + "\n")
    print(f"\nWrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
