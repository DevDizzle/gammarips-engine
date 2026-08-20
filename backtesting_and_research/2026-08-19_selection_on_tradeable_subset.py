"""Re-score SELECTION on the TRADEABLE subset only (READ-ONLY research, 2026-08-19).

Owner question, after the execution-risk calibration: if roughly 63% of the pool is
untradeable by 10:00 ET, then most measured pool performance is fictional. Does the
engine's SELECTION have edge once the ghosts are stripped out?

Three things this answers:
  A. Is the whole-pool composite still negative when you keep only tradeable rows?
  B. Do the selection composites rank WITHIN a day once ghosts are gone? Pooled AND
     day-demeaned AUC, because the 2026-08-05 adjudication showed day-demeaning is the
     kill shot for between-day tape artifacts.
  C. Does the tournament pick beat a random tradeable pool draw, and does it even LAND
     on tradeable contracts?
  D. The 2026-08-05 pre-committed re-test: contract_score read 0.552 [0.515, 0.588] in
     the cap-50 era and was flagged for re-test once >=15 fresh closed-label days
     accrued (~late Aug). Check whether the days exist and run it.

TRADEABILITY LABEL is ENTRY-KNOWABLE: the count of date-validated prints by 10:00 ET on
entry day, taken from `option_minute_paths`. That is a number an agent HAS at the
decision, not a post-hoc outcome. See docs/EXECUTION-RISK-GUIDELINES.md §2 for the
calibration (0 prints -> 0.0% chance of a manageable day; 21+ -> 93.0%).

LEAKAGE: features come from `enriched_features_v1`, the leakage-safe view. iv_rank_entry
and iv_percentile_entry are post-entry and are NOT in it (memory
`iv-rank-entry-post-entry-leakage`). Do not add them.

Run:
    .venv/bin/python backtesting_and_research/2026-08-19_selection_on_tradeable_subset.py
"""

import db_dtypes  # noqa: F401 - registers the BQ DATE dtype used by the parquet cache
import os

import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
PROJECT = "profitscout-fida8"
HERE = os.path.dirname(os.path.abspath(__file__))
TAPE = os.path.join(HERE, "cache", "pm_entry_minute_paths.parquet")
FEAT = os.path.join(HERE, "cache", "tradeable_features.parquet")

N_BOOT = 10000
RNG = np.random.default_rng(11)

FEATURES = [
    "overnight_score", "contract_score", "premium_score", "catalyst_score",
    "recommended_delta", "recommended_oi", "recommended_volume", "volume_oi_ratio",
    "moneyness_pct", "recommended_dte", "recommended_iv", "risk_reward_ratio",
    "atr_normalized_move", "rsi_14",
]


def load_features() -> pd.DataFrame:
    if os.path.exists(FEAT):
        return pd.read_parquet(FEAT)
    from google.cloud import bigquery

    sql = f"""
    SELECT f.*, o.realized_return_pct, o.exit_reason, o.illiquid_exit,
           o.opp_peak_return, o.opp_trough_return
    FROM `{PROJECT}.profit_scout.enriched_features_v1` f
    JOIN `{PROJECT}.profit_scout.enriched_option_outcomes` o
      USING (scan_date, recommended_contract)
    WHERE f.scan_date >= '2026-04-10'
    """
    df = bigquery.Client(project=PROJECT).query(sql).to_dataframe()
    df.to_parquet(FEAT)
    return df


def prints_by_1000() -> pd.DataFrame:
    bars = pd.read_parquet(TAPE)
    loc = bars["ts"].dt.tz_convert(ET)
    bars["min_et"] = loc.dt.hour * 60 + loc.dt.minute
    d1 = bars[bars.day_index == 1]
    g = d1.groupby(["scan_date", "contract"])
    out = pd.DataFrame({
        "prints_by_1000": g.apply(lambda x: int((x["min_et"] <= 600).sum()),
                                  include_groups=False),
        "prints_day": g.size(),
    }).reset_index()
    out = out.rename(columns={"contract": "recommended_contract"})
    return out


# ------------------------------------------------------------------ stats
def auc(y, x):
    """Rank AUC of score x against binary label y. NaN-safe."""
    m = ~(pd.isna(x) | pd.isna(y))
    y, x = np.asarray(y)[m], np.asarray(x)[m]
    n1, n0 = int(y.sum()), int((1 - y).sum())
    if n1 == 0 or n0 == 0:
        return np.nan
    r = pd.Series(x).rank().to_numpy()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def auc_ci(df, feat, label="win", by="scan_date", n=N_BOOT, demean=False):
    d = df[[by, feat, label]].dropna()
    if demean:
        d = d.copy()
        d[feat] = d[feat] - d.groupby(by)[feat].transform("mean")
    groups = [g for _, g in d.groupby(by)]
    groups = [g for g in groups if g[label].nunique() > 1]
    if len(groups) < 5:
        return np.nan, np.nan, np.nan, 0, 0
    allrows = pd.concat(groups)
    obs = auc(allrows[label].to_numpy(), allrows[feat].to_numpy())
    k = len(groups)
    vals = np.empty(n)
    for b in range(n):
        pick = RNG.integers(0, k, k)
        s = pd.concat([groups[i] for i in pick])
        vals[b] = auc(s[label].to_numpy(), s[feat].to_numpy())
    return (obs, float(np.nanpercentile(vals, 5)), float(np.nanpercentile(vals, 95)),
            k, len(allrows))


def mean_ci(df, col, by="scan_date", n=N_BOOT):
    groups = [g[col].dropna().to_numpy() for _, g in df.groupby(by)]
    groups = [g for g in groups if len(g)]
    if len(groups) < 5:
        return np.nan, np.nan, np.nan, 0
    obs = np.concatenate(groups).mean()
    k = len(groups)
    means = np.empty(n)
    for b in range(n):
        pick = RNG.integers(0, k, k)
        means[b] = np.concatenate([groups[i] for i in pick]).mean()
    return obs, float(np.percentile(means, 5)), float(np.percentile(means, 95)), k


def pct(x, d=2):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x*100:+.{d}f}%"


# ------------------------------------------------------------------- main
def main():
    feat = load_features()
    tape = prints_by_1000()
    feat["scan_date"] = pd.to_datetime(feat["scan_date"]).dt.date
    tape["scan_date"] = pd.to_datetime(tape["scan_date"]).dt.date
    df = feat.merge(tape, on=["scan_date", "recommended_contract"], how="inner")

    print(f"enriched_option_outcomes joined rows : {len(feat):,}")
    print(f"with a day-1 minute tape             : {len(df):,} "
          f"({df.scan_date.nunique()} scan dates, "
          f"{df.scan_date.min()} .. {df.scan_date.max()})")

    df = df[df.realized_return_pct.notna()].copy()
    df["ret"] = df["realized_return_pct"].astype(float)
    if df["ret"].abs().median() > 1.5:      # stored as percent, not fraction
        df["ret"] = df["ret"] / 100.0
    df["win"] = (df["ret"] > 0).astype(int)
    print(f"with a closed V7.1 same-day label    : {len(df):,}")

    df["tier"] = pd.cut(df.prints_by_1000, [-1, 0, 2, 5, 10, 20, 1e9],
                        labels=["0", "1-2", "3-5", "6-10", "11-20", "21+"])
    df["tradeable"] = df.prints_by_1000 >= 11
    df["semi"] = df.prints_by_1000 >= 6

    # ------------------------------------------------------------------ A
    print("\n" + "=" * 84)
    print("A. POOL COMPOSITE BY TRADEABILITY  (V7.1 same-day bracket, entry-knowable)")
    print("=" * 84)
    print(f"  {'prints by 10:00':<18}{'n':>6}{'days':>6}{'mean':>10}"
          f"{'90% CI (day-clustered)':>26}{'median':>10}{'win%':>7}")
    for t, g in df.groupby("tier", observed=True):
        m, lo, hi, k = mean_ci(g, "ret")
        ci = f"[{pct(lo,1)}, {pct(hi,1)}]"
        print(f"  {str(t):<18}{len(g):>6}{g.scan_date.nunique():>6}{pct(m):>10}"
              f"{ci:>26}{pct(g['ret'].median()):>10}{g['win'].mean()*100:>6.1f}%")
    for name, sub in [("ALL rows", df), ("TRADEABLE (11+)", df[df.tradeable]),
                      ("semi (6+)", df[df.semi])]:
        m, lo, hi, k = mean_ci(sub, "ret")
        print(f"  {name:<18}{len(sub):>6}{sub.scan_date.nunique():>6}{pct(m):>10}"
              f"{f'[{pct(lo,1)}, {pct(hi,1)}]':>26}"
              f"{pct(sub['ret'].median()):>10}{sub['win'].mean()*100:>6.1f}%")

    # ------------------------------------------------------------------ B
    print("\n" + "=" * 84)
    print("B. SELECTION RANKING POWER — AUC vs a positive same-day return")
    print("=" * 84)
    print("  Day-demeaned is the honest column: it strips between-day pool composition,")
    print("  which is what killed catalyst_score and ATR on 2026-08-05.")
    for name, sub in [("UNTRADEABLE (0-5 prints)", df[df.prints_by_1000 <= 5]),
                      ("TRADEABLE (11+ prints)", df[df.tradeable])]:
        print(f"\n  -- {name}: n={len(sub)}, {sub.scan_date.nunique()} days, "
              f"base rate {sub['win'].mean()*100:.1f}%")
        print(f"  {'feature':<22}{'pooled AUC':>12}{'90% CI':>20}"
              f"{'demeaned':>11}{'90% CI':>20}")
        for f in FEATURES:
            if f not in sub.columns:
                continue
            o1, l1, h1, k1, n1 = auc_ci(sub, f)
            o2, l2, h2, k2, n2 = auc_ci(sub, f, demean=True)
            if np.isnan(o1):
                continue
            star = ""
            if not np.isnan(l2) and (l2 > 0.50 or h2 < 0.50):
                star = "  <-- excludes 0.50"
            print(f"  {f:<22}{o1:>12.3f}{f'[{l1:.3f}, {h1:.3f}]':>20}"
                  f"{o2:>11.3f}{f'[{l2:.3f}, {h2:.3f}]':>20}{star}")

    # ------------------------------------------------------------------ C
    print("\n" + "=" * 84)
    print("C. THE TOURNAMENT PICK vs THE TRADEABLE POOL")
    print("=" * 84)
    if "was_tournament_pick" in df.columns:
        pk = df[df.was_tournament_pick == True]  # noqa: E712
        print(f"  picks with a closed label + tape: {len(pk)} "
              f"over {pk.scan_date.nunique()} days")
        print("\n  Where does the pick LAND? (share of picks by tradeability tier)")
        vc = pk["tier"].value_counts(normalize=True).sort_index()
        base = df["tier"].value_counts(normalize=True).sort_index()
        print(f"  {'tier':<10}{'picks':>9}{'pool':>9}{'lift':>9}")
        for t in base.index:
            p, b = vc.get(t, 0.0), base.get(t, 0.0)
            print(f"  {str(t):<10}{p*100:>8.1f}%{b*100:>8.1f}%"
                  f"{(p-b)*100:>8.1f}pp")
        print(f"\n  picks landing on TRADEABLE (11+): {pk.tradeable.mean()*100:.1f}%"
              f"   pool base: {df.tradeable.mean()*100:.1f}%")

        print("\n  Return, pick vs pool, matched on the SAME days:")
        for name, sub_p, sub_d in [
            ("all rows", pk, df),
            ("tradeable only", pk[pk.tradeable], df[df.tradeable]),
        ]:
            days = set(sub_p.scan_date)
            pool = sub_d[sub_d.scan_date.isin(days)]
            if len(sub_p) < 5:
                print(f"  {name:<18} n={len(sub_p)} — too few to read")
                continue
            mp, lp, hp, _ = mean_ci(sub_p, "ret")
            mo, lo_, ho, _ = mean_ci(pool, "ret")
            print(f"  {name:<18}pick n={len(sub_p):<4} {pct(mp)} "
                  f"[{pct(lp,1)}, {pct(hp,1)}]   pool n={len(pool):<5} {pct(mo)}"
                  f"   diff {pct(mp-mo)}")

    # ------------------------------------------------------------------ D
    print("\n" + "=" * 84)
    print("D. PRE-COMMITTED RE-TEST — contract_score, cap-50 era (flagged 2026-08-05)")
    print("=" * 84)
    print("  Commitment: era-B (06-11..07-27) read 0.552 [0.515, 0.588] pooled,")
    print("  0.564 day-demeaned. Re-test on >=15 FRESH closed-label days after 07-27.")
    fresh = df[df.scan_date > pd.Timestamp("2026-07-27").date()]
    nd = fresh.scan_date.nunique()
    print(f"\n  fresh closed-label days available: {nd}  (need 15)")
    if nd >= 15:
        for f in ["contract_score", "overnight_score"]:
            o1, l1, h1, k1, n1 = auc_ci(fresh, f)
            o2, l2, h2, k2, n2 = auc_ci(fresh, f, demean=True)
            print(f"  {f:<18} n={n1:<5} days={k1:<3} pooled {o1:.3f} "
                  f"[{l1:.3f}, {h1:.3f}]   demeaned {o2:.3f} [{l2:.3f}, {h2:.3f}]")
        ft = fresh[fresh.tradeable]
        if ft.scan_date.nunique() >= 5:
            o2, l2, h2, k2, n2 = auc_ci(ft, "contract_score", demean=True)
            print(f"  {'contract_score':<18} TRADEABLE only: n={n2} days={k2} "
                  f"demeaned {o2:.3f} [{l2:.3f}, {h2:.3f}]")
    else:
        print(f"  NOT DUE YET. {15 - nd} more closed-label days needed. Do not")
        print("  run the test early and do not read a partial result as the answer.")

    print("\ndone.")


if __name__ == "__main__":
    main()
