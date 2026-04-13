"""Single canonical EDA over `signals_labeled_v1`.

Reads ONLY from `profitscout-fida8.profit_scout.signals_labeled_v1` (the frozen
labeled dataset). Produces five sections of output, written to
`docs/research_reports/SIGNAL_FEATURE_DISCOVERY_V1.md`. The same script run
twice must produce a byte-identical report — that's the test that fixes the
"every EDA gives different numbers" problem.

Sections:
  1. Cohort overview
  2. Univariate quintile analysis (numeric features)
  3. Categorical / boolean feature breakdowns
  4. Premium-score stratification (n / win rate / avg return per score)
  5. Tree-based feature importance with chronological holdout

Determinism: all RNG seeds are fixed; the chronological train/test split is
defined by scan_date order, not random.

Usage:
    python scripts/research/analyze_signals_labeled_v1.py
"""

from __future__ import annotations

import io
import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO / "docs/research_reports/SIGNAL_FEATURE_DISCOVERY_V1.md"
PROJECT_ID = "profitscout-fida8"
LABELED_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIMULATOR_VERSION = "V3_MECHANICS_2026_04_07"
WIN_THRESHOLD = 0.35  # +35% net return counts as a win (matches xgboost script)
RANDOM_SEED = 42

# Columns we treat as outcome / metadata, NEVER as features.
OUTCOME_COLS = {
    "entry_day", "timeout_day", "entry_timestamp", "entry_price", "target_price",
    "stop_price", "exit_timestamp", "exit_price", "exit_reason",
    "realized_return_pct", "bars_to_exit", "simulator_version", "labeled_at",
    # post-hoc underlying-stock outcome cols already in the source table — these
    # would leak future info if used as features:
    "next_day_close", "next_day_pct", "day2_close", "day2_pct", "day3_close",
    "day3_pct", "peak_return_3d", "outcome_tier", "is_win", "performance_updated",
}

# Identifier / text columns — never used as features.
ID_COLS = {
    "ticker", "scan_date", "enriched_at", "recommended_contract",
    "recommended_expiration", "recommended_strike",  # strike is per-contract, not portable
    "thesis", "news_summary", "key_headline", "flow_intent_reasoning",
}

EXCLUDED_COLS = OUTCOME_COLS | ID_COLS


def load_labeled() -> pd.DataFrame:
    client = bigquery.Client(project=PROJECT_ID)
    sql = f"""
    SELECT *
    FROM `{LABELED_TABLE}`
    WHERE simulator_version = '{SIMULATOR_VERSION}'
    """
    return client.query(sql).to_dataframe()


def fmt_pct(x: float) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "  n/a"
    return f"{x * 100:+6.2f}%"


def fmt_int(x) -> str:
    return f"{int(x):>6d}"


def section_overview(df: pd.DataFrame) -> str:
    lines = ["## 1. Cohort overview", ""]
    n = len(df)
    lines.append(f"- **Total labeled signals:** {n}")
    lines.append(f"- **Distinct tickers:** {df['ticker'].nunique()}")
    lines.append(f"- **scan_date range:** {df['scan_date'].min()} → {df['scan_date'].max()}")
    lines.append(f"- **Distinct scan_dates:** {df['scan_date'].nunique()}")
    lines.append("")

    er = df["exit_reason"].value_counts(dropna=False).sort_index()
    lines.append("**Exit reason distribution (full population):**")
    lines.append("")
    lines.append("| exit_reason | n | %  |")
    lines.append("|---|---|---|")
    for r, c in er.items():
        lines.append(f"| {r} | {c} | {c / n * 100:5.1f}% |")
    lines.append("")

    # Restrict to actually-executed trades for return stats.
    executed = df[df["exit_reason"].isin(["TARGET", "STOP", "TIMEOUT"])].copy()
    n_x = len(executed)
    avg = executed["realized_return_pct"].mean()
    med = executed["realized_return_pct"].median()
    win_rate = (executed["realized_return_pct"] >= WIN_THRESHOLD).mean()

    lines.append("**Executed-trade summary** (exit_reason ∈ {TARGET, STOP, TIMEOUT}):")
    lines.append("")
    lines.append(f"- n = {n_x}")
    lines.append(f"- avg realized_return_pct = {fmt_pct(avg)}")
    lines.append(f"- median realized_return_pct = {fmt_pct(med)}")
    lines.append(f"- win rate (return >= +35%) = {win_rate * 100:.1f}%")
    lines.append("")
    return "\n".join(lines)


def numeric_feature_columns(df: pd.DataFrame) -> list[str]:
    cols = []
    for c in df.columns:
        if c in EXCLUDED_COLS:
            continue
        if pd.api.types.is_bool_dtype(df[c]):
            continue  # treated separately as categorical
        if pd.api.types.is_numeric_dtype(df[c]):
            cols.append(c)
    return sorted(cols)


def boolean_or_string_columns(df: pd.DataFrame) -> list[str]:
    cols = []
    for c in df.columns:
        if c in EXCLUDED_COLS:
            continue
        if pd.api.types.is_bool_dtype(df[c]) or pd.api.types.is_string_dtype(df[c]):
            cols.append(c)
    return sorted(cols)


def quintile_table(executed: pd.DataFrame, col: str) -> tuple[pd.DataFrame, float, float]:
    """Return (per-bucket stats, monotonicity score, separation)."""
    s = executed[col]
    valid = executed.dropna(subset=[col, "realized_return_pct"])
    if len(valid) < 25:
        return None, None, None
    try:
        bins = pd.qcut(valid[col], q=5, duplicates="drop")
    except ValueError:
        return None, None, None
    if bins.nunique() < 3:
        return None, None, None
    grp = valid.groupby(bins, observed=True).agg(
        n=("realized_return_pct", "size"),
        win_rate=("realized_return_pct", lambda x: (x >= WIN_THRESHOLD).mean()),
        avg_return=("realized_return_pct", "mean"),
        median_return=("realized_return_pct", "median"),
    )
    grp = grp.reset_index().rename(columns={col: "bucket"})
    grp["bucket"] = grp["bucket"].astype(str)
    avgs = grp["avg_return"].values
    diffs = np.diff(avgs)
    if len(diffs) == 0:
        monotonicity = 0.0
    else:
        monotonicity = abs(np.sum(np.sign(diffs))) / len(diffs)
    separation = float(np.max(avgs) - np.min(avgs))
    return grp, monotonicity, separation


def section_univariate(executed: pd.DataFrame) -> str:
    lines = ["## 2. Univariate quintile analysis (numeric features)", ""]
    lines.append("For each numeric feature, executed trades are split into 5 quintiles "
                 "by feature value. Features are ranked by **separation** "
                 "(max-bucket avg return − min-bucket avg return) and "
                 "**monotonicity** (1.0 = strictly monotonic across quintiles).")
    lines.append("")

    rows = []
    for col in numeric_feature_columns(executed):
        result = quintile_table(executed, col)
        if result is None or result[0] is None:
            continue
        tbl, mono, sep = result
        rows.append((col, tbl, mono, sep))

    rows.sort(key=lambda r: (-abs(r[3]), -r[2]))

    lines.append(f"**Features ranked by absolute separation** (top 20 of {len(rows)}):")
    lines.append("")
    lines.append("| rank | feature | separation | monotonicity |")
    lines.append("|---|---|---|---|")
    for i, (col, _, mono, sep) in enumerate(rows[:20], 1):
        lines.append(f"| {i} | `{col}` | {fmt_pct(sep)} | {mono:.2f} |")
    lines.append("")

    lines.append("**Detailed quintile breakdowns** for top-15 features:")
    lines.append("")
    for col, tbl, mono, sep in rows[:15]:
        lines.append(f"### `{col}`  (separation={fmt_pct(sep)}, monotonicity={mono:.2f})")
        lines.append("")
        lines.append("| bucket | n | win_rate | avg_return | median |")
        lines.append("|---|---|---|---|---|")
        for _, r in tbl.iterrows():
            lines.append(f"| {r['bucket']} | {int(r['n'])} | "
                         f"{r['win_rate'] * 100:5.1f}% | "
                         f"{fmt_pct(r['avg_return'])} | {fmt_pct(r['median_return'])} |")
        lines.append("")
    return "\n".join(lines)


def section_categorical(executed: pd.DataFrame) -> str:
    lines = ["## 3. Categorical / boolean feature breakdowns", ""]
    cols = [c for c in boolean_or_string_columns(executed) if c not in
            ("ticker", "scan_date", "exit_reason", "entry_day", "timeout_day")]
    for col in sorted(cols):
        valid = executed.dropna(subset=[col, "realized_return_pct"])
        if valid[col].nunique() < 2 or len(valid) < 25:
            continue
        grp = valid.groupby(col, observed=True).agg(
            n=("realized_return_pct", "size"),
            win_rate=("realized_return_pct", lambda x: (x >= WIN_THRESHOLD).mean()),
            avg_return=("realized_return_pct", "mean"),
        ).reset_index().sort_values("avg_return", ascending=False)
        if grp["n"].max() < 10:
            continue
        lines.append(f"### `{col}`")
        lines.append("")
        lines.append(f"| {col} | n | win_rate | avg_return |")
        lines.append("|---|---|---|---|")
        for _, r in grp.iterrows():
            lines.append(f"| `{r[col]}` | {int(r['n'])} | "
                         f"{r['win_rate'] * 100:5.1f}% | {fmt_pct(r['avg_return'])} |")
        lines.append("")
    return "\n".join(lines)


def section_premium_score(executed: pd.DataFrame) -> str:
    lines = ["## 4. Premium-score stratification", ""]
    lines.append("Honest validation of the load-bearing `premium_score` formula. "
                 "The live ledger only ever sees `premium_score >= 2`; this table "
                 "shows what every score level produces under the same simulator.")
    lines.append("")
    grp = executed.dropna(subset=["premium_score"]).groupby("premium_score").agg(
        n=("realized_return_pct", "size"),
        win_rate=("realized_return_pct", lambda x: (x >= WIN_THRESHOLD).mean()),
        avg_return=("realized_return_pct", "mean"),
        median_return=("realized_return_pct", "median"),
    ).reset_index()
    lines.append("| premium_score | n | win_rate | avg_return | median_return |")
    lines.append("|---|---|---|---|---|")
    for _, r in grp.iterrows():
        lines.append(f"| {int(r['premium_score'])} | {int(r['n'])} | "
                     f"{r['win_rate'] * 100:5.1f}% | "
                     f"{fmt_pct(r['avg_return'])} | {fmt_pct(r['median_return'])} |")
    lines.append("")
    return "\n".join(lines)


def section_tree(executed: pd.DataFrame) -> str:
    """GradientBoostingRegressor with chronological holdout + shallow tree rules."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.tree import DecisionTreeRegressor, export_text
    from scipy.stats import spearmanr

    lines = ["## 5. Tree-based feature importance (chronological holdout)", ""]

    feat_cols = numeric_feature_columns(executed)
    df = executed.dropna(subset=["realized_return_pct"]).copy()
    df = df.sort_values("scan_date").reset_index(drop=True)
    df = df.dropna(subset=feat_cols, how="all")

    # Drop columns that are entirely null in the executed cohort.
    feat_cols = [c for c in feat_cols if df[c].notna().any()]

    # Median imputation per feature (deterministic). Fall back to 0.0 if median
    # itself is NaN (shouldn't happen after the all-null drop above, but be safe).
    X = df[feat_cols].copy()
    for c in feat_cols:
        med = X[c].median()
        if pd.isna(med):
            med = 0.0
        X[c] = X[c].fillna(med)
    y = df["realized_return_pct"].values

    if len(df) < 60:
        lines.append(f"_Insufficient data for chronological-holdout model "
                     f"(n={len(df)} < 60). Skipping section._")
        lines.append("")
        return "\n".join(lines), []

    split_idx = int(len(df) * 0.70)
    X_tr, X_te = X.iloc[:split_idx], X.iloc[split_idx:]
    y_tr, y_te = y[:split_idx], y[split_idx:]

    train_dates = df["scan_date"].iloc[:split_idx]
    test_dates = df["scan_date"].iloc[split_idx:]
    lines.append(f"**Train:** {len(X_tr)} rows, scan_date "
                 f"{train_dates.min()} → {train_dates.max()}")
    lines.append(f"**Test:**  {len(X_te)} rows, scan_date "
                 f"{test_dates.min()} → {test_dates.max()}")
    lines.append("")

    gbm = GradientBoostingRegressor(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        random_state=RANDOM_SEED,
    )
    gbm.fit(X_tr.values, y_tr)
    pred_tr = gbm.predict(X_tr.values)
    pred_te = gbm.predict(X_te.values)
    r2_tr = 1 - np.sum((y_tr - pred_tr) ** 2) / np.sum((y_tr - y_tr.mean()) ** 2)
    r2_te = 1 - np.sum((y_te - pred_te) ** 2) / np.sum((y_te - y_te.mean()) ** 2)
    rho_te, _ = spearmanr(pred_te, y_te)

    lines.append(f"**GradientBoostingRegressor** (200 trees, depth 3, lr 0.05, seed={RANDOM_SEED})")
    lines.append("")
    lines.append(f"- In-sample R²:        {r2_tr:+.4f}")
    lines.append(f"- Out-of-sample R²:    {r2_te:+.4f}")
    lines.append(f"- OOS Spearman ρ:      {rho_te:+.4f}  _(rank correlation pred vs actual)_")
    lines.append("")

    importances = sorted(zip(feat_cols, gbm.feature_importances_),
                         key=lambda kv: -kv[1])
    lines.append("**Top 15 features by GBM importance:**")
    lines.append("")
    lines.append("| rank | feature | importance |")
    lines.append("|---|---|---|")
    top_features = []
    for i, (col, imp) in enumerate(importances[:15], 1):
        lines.append(f"| {i} | `{col}` | {imp:.4f} |")
        top_features.append(col)
    lines.append("")

    # Shallow decision tree for human-readable rules (trained on full data, not split).
    dt = DecisionTreeRegressor(max_depth=3, min_samples_leaf=20, random_state=RANDOM_SEED)
    dt.fit(X.values, y)
    tree_text = export_text(dt, feature_names=list(feat_cols), decimals=3)
    lines.append("**Shallow decision tree** (depth 3, min_samples_leaf=20, full data):")
    lines.append("")
    lines.append("```")
    lines.append(tree_text.rstrip())
    lines.append("```")
    lines.append("")
    return "\n".join(lines), top_features


def section_findings(executed: pd.DataFrame, univariate_top: list[str],
                     gbm_top: list[str]) -> str:
    """Mechanical summary: features that show up in BOTH univariate separation
    and GBM importance are the most credible."""
    lines = ["## 6. Findings & next steps", ""]
    overlap = [c for c in gbm_top[:10] if c in univariate_top[:15]]
    lines.append("**Features that rank in both top-10 GBM importance AND top-15 "
                 "univariate separation** (the 'real signal' candidates):")
    lines.append("")
    if overlap:
        for c in overlap:
            lines.append(f"- `{c}`")
    else:
        lines.append("- _none — no feature ranks in both lists, suggesting the "
                     "tree model is finding interactions rather than monotonic effects_")
    lines.append("")

    n_x = len(executed)
    win_rate = (executed["realized_return_pct"] >= WIN_THRESHOLD).mean()
    avg = executed["realized_return_pct"].mean()
    lines.append(f"**Headline:** unconditional cohort of {n_x} executed trades has "
                 f"avg return {fmt_pct(avg)} and win rate {win_rate * 100:.1f}%.")
    lines.append("")
    lines.append("**Next steps (out of scope for this study; user decision):**")
    lines.append("- Compare overlap features against the current `premium_score` flags. "
                 "If overlap features beat the score on the chronological holdout, "
                 "draft a candidate V4 gate around them.")
    lines.append("- Investigate any feature in the GBM top-10 with **negative** "
                 "monotonicity in its quintile table — it may carry a non-linear edge "
                 "that monotonic features miss.")
    lines.append("- Sample-size check: if `n` for executed trades is small relative "
                 "to feature count, re-run with a larger labeled cohort before "
                 "making any policy changes.")
    lines.append("")
    return "\n".join(lines)


def main():
    df = load_labeled()
    if df.empty:
        print("ERROR: signals_labeled_v1 is empty for current simulator_version", file=sys.stderr)
        sys.exit(1)

    executed = df[df["exit_reason"].isin(["TARGET", "STOP", "TIMEOUT"])].copy()
    executed = executed.dropna(subset=["realized_return_pct"])

    parts = [f"# Signal Feature Discovery V1\n",
             f"**Source:** `{LABELED_TABLE}`  \n"
             f"**Simulator:** `{SIMULATOR_VERSION}`  \n"
             f"**Win threshold:** `realized_return_pct >= {WIN_THRESHOLD:+.2f}`  \n"
             f"**Labeled rows:** {len(df)} total / {len(executed)} executed\n",
             section_overview(df),
             section_univariate(executed)]

    # Cache the univariate ranking for the findings section.
    rows = []
    for col in numeric_feature_columns(executed):
        result = quintile_table(executed, col)
        if result is None or result[0] is None:
            continue
        rows.append((col, result[2]))  # (col, separation)
    rows.sort(key=lambda r: -abs(r[1]))
    univariate_top = [r[0] for r in rows[:15]]

    parts.append(section_categorical(executed))
    parts.append(section_premium_score(executed))
    tree_section, gbm_top = section_tree(executed)
    parts.append(tree_section)
    parts.append(section_findings(executed, univariate_top, gbm_top))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(parts) + "\n")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
