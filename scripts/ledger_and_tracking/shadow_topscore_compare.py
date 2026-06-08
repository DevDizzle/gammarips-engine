"""READ-ONLY compare: deterministic top-score baseline vs the live Tournament.

Pivots the two arms (TOURNAMENT, TOP_SCORE) of paper_shadow_topscore by
entry_day over CLOSED, paired rows and prints a side-by-side EV view. This is a
research baseline — the question it answers is whether the gutted no-gate V6
Tournament actually beats blindly trading the highest overnight_score signal
(which a labeled-scan retrospective showed returned -6.09% mean option PnL /
33% win — worse than random — the score-inversion effect).

STRICTLY read-only: queries paper_shadow_topscore, never writes or mutates any
table. Does NOT touch forward_paper_ledger / todays_pick / signal_performance.

Run:
    python scripts/ledger_and_tracking/shadow_topscore_compare.py

See docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md.
"""

from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "profitscout-fida8"
SHADOW_TABLE = f"{PROJECT_ID}.profit_scout.paper_shadow_topscore"
DECISION_THRESHOLD = 15  # paired closes before acting on this comparison

# CLOSED = realized PnL present and not a non-trade outcome.
EXCLUDED_REASONS = ("INVALID_LIQUIDITY", "SKIPPED")


def _load_closed() -> pd.DataFrame:
    client = bigquery.Client(project=PROJECT_ID)
    sql = f"""
    SELECT scan_date, entry_day, arm, ticker, overnight_score, same_pick,
           realized_return_pct, illiquid_exit, exit_reason
    FROM `{SHADOW_TABLE}`
    WHERE realized_return_pct IS NOT NULL
      AND exit_reason NOT IN UNNEST(@excluded)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("excluded", "STRING", list(EXCLUDED_REASONS)),
        ]
    )
    return client.query(sql, job_config=job_config).to_dataframe()


def _arm_stats(s: pd.Series) -> dict:
    r = s.dropna()
    if len(r) == 0:
        return {"n": 0, "mean": None, "median": None, "win_pct": None}
    return {
        "n": int(len(r)),
        "mean": float(r.mean()),
        "median": float(r.median()),
        "win_pct": float((r > 0).mean() * 100.0),
    }


def _print_block(title: str, df: pd.DataFrame) -> None:
    # Pivot to one row per entry_day with both arms' returns side by side.
    pivot = df.pivot_table(
        index="entry_day", columns="arm", values="realized_return_pct", aggfunc="first"
    )
    paired = pivot.dropna(subset=["TOURNAMENT", "TOP_SCORE"]) \
        if {"TOURNAMENT", "TOP_SCORE"}.issubset(pivot.columns) else pivot.iloc[0:0]
    n_paired = int(len(paired))

    print(f"\n=== {title} ===")
    print(f"paired entry_days (both arms closed): {n_paired}")

    for arm in ("TOURNAMENT", "TOP_SCORE"):
        col = paired[arm] if arm in paired.columns else pd.Series(dtype=float)
        st = _arm_stats(col)
        if st["n"] == 0:
            print(f"  {arm:11s}: n=0")
        else:
            print(f"  {arm:11s}: n={st['n']:3d}  mean={st['mean']*100:+6.2f}%  "
                  f"median={st['median']*100:+6.2f}%  win%={st['win_pct']:5.1f}")

    if n_paired > 0:
        spread = (paired["TOURNAMENT"] - paired["TOP_SCORE"])
        print(f"  mean T-S spread on paired days: {spread.mean()*100:+6.2f}%  "
              f"(T beats S on {int((spread > 0).sum())}/{n_paired} days)")


def main() -> None:
    df = _load_closed()
    if len(df) == 0:
        print("No closed shadow rows yet. (Shadow runs paired-only on HAS_PICK days.)")
        print(f"\nDO NOT ACT until N >= {DECISION_THRESHOLD} paired closes.")
        return

    # %same_pick measured over distinct entry_days (same_pick is per-day, same on
    # both arms — take the TOURNAMENT row as the canonical per-day flag).
    per_day = df[df["arm"] == "TOURNAMENT"].drop_duplicates("entry_day")
    if len(per_day) > 0 and per_day["same_pick"].notna().any():
        same_pct = float(per_day["same_pick"].fillna(False).mean() * 100.0)
        print(f"days where top_score == tournament pick: {same_pct:.1f}% "
              f"({int(per_day['same_pick'].fillna(False).sum())}/{len(per_day)})")

    # All closed paired days.
    _print_block("ALL CLOSED (paired)", df)

    # Clean-EV view: exclude any day where EITHER arm had illiquid_exit=True.
    bad_days = set(df[df["illiquid_exit"] == True]["entry_day"].tolist())  # noqa: E712
    clean = df[~df["entry_day"].isin(bad_days)]
    _print_block("CLEAN-EV (excl. illiquid_exit on either arm)", clean)

    pivot = df.pivot_table(
        index="entry_day", columns="arm", values="realized_return_pct", aggfunc="first"
    )
    n_paired = int(pivot.dropna(subset=[c for c in ("TOURNAMENT", "TOP_SCORE") if c in pivot.columns]).shape[0]) \
        if {"TOURNAMENT", "TOP_SCORE"}.issubset(pivot.columns) else 0

    print(f"\nDO NOT ACT until N >= {DECISION_THRESHOLD} paired closes. "
          f"Current paired N = {n_paired}.")


if __name__ == "__main__":
    main()
