"""READ-ONLY compare: day-trade (10:00->15:45 flat) vs 3-day hold, for BOTH the
Tournament pick and the deterministic top-score pick.

Reads paper_shadow_intraday (up to 2 rows/day, arm in {TOURNAMENT, TOP_SCORE} —
the SAME picks the topscore shadow tracks, but day-traded). Prints, per arm,
intraday-flat vs that pick's live 3-day bracket; then the cross view
(Tournament-intraday vs top-score-intraday). Together with the 3-day topscore
shadow this completes the 2x2: {Tournament, top-score} x {3-day, intraday}.

STRICTLY read-only: queries paper_shadow_intraday only, never writes/mutates any
table. Does NOT touch forward_paper_ledger / todays_pick / signal_performance.

Run:
    python scripts/ledger_and_tracking/shadow_intraday_compare.py

See docs/DECISIONS/2026-06-08-intraday-hold-shadow.md.
"""

from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "profitscout-fida8"
SHADOW_INTRADAY_TABLE = f"{PROJECT_ID}.profit_scout.paper_shadow_intraday"
DECISION_THRESHOLD = 15  # paired closes before acting on this comparison


def _load() -> pd.DataFrame:
    client = bigquery.Client(project=PROJECT_ID)
    sql = f"""
    SELECT entry_day, arm, ticker, direction, same_pick,
           intraday_return_pct, intraday_illiquid,
           hold_3day_return_pct, hold_3day_exit_reason
    FROM `{SHADOW_INTRADAY_TABLE}`
    """
    return client.query(sql).to_dataframe()


def _stats(s: pd.Series) -> dict:
    r = s.dropna()
    if len(r) == 0:
        return {"n": 0, "mean": None, "median": None, "win_pct": None}
    return {"n": int(len(r)), "mean": float(r.mean()),
            "median": float(r.median()), "win_pct": float((r > 0).mean() * 100.0)}


def _line(label: str, st: dict) -> str:
    if st["n"] == 0:
        return f"  {label:22s}: n=0"
    return (f"  {label:22s}: n={st['n']:3d}  mean={st['mean']*100:+6.2f}%  "
            f"median={st['median']*100:+6.2f}%  win%={st['win_pct']:5.1f}")


def _arm_block(arm: str, df: pd.DataFrame) -> None:
    a = df[df["arm"] == arm]
    paired = a.dropna(subset=["intraday_return_pct", "hold_3day_return_pct"])
    print(f"\n=== {arm}: intraday-flat vs 3-day hold (same pick) ===")
    print(f"paired entry_days (both horizons closed): {len(paired)}")
    print(_line(f"{arm} INTRADAY_FLAT", _stats(paired["intraday_return_pct"])))
    print(_line(f"{arm} HOLD_3DAY", _stats(paired["hold_3day_return_pct"])))
    if len(paired) > 0:
        spread = paired["intraday_return_pct"] - paired["hold_3day_return_pct"]
        print(f"  mean (intraday - 3day) spread: {spread.mean()*100:+6.2f}%  "
              f"(intraday beats 3day on {int((spread > 0).sum())}/{len(paired)} days)")


def _cross_block(df: pd.DataFrame) -> int:
    # Tournament-intraday vs top-score-intraday on paired days (both arms present).
    pivot = df.pivot_table(index="entry_day", columns="arm",
                           values="intraday_return_pct", aggfunc="first")
    if not {"TOURNAMENT", "TOP_SCORE"}.issubset(pivot.columns):
        print("\n=== CROSS (intraday): TOURNAMENT vs TOP_SCORE === (need both arms)")
        return 0
    paired = pivot.dropna(subset=["TOURNAMENT", "TOP_SCORE"])
    print(f"\n=== CROSS (intraday day-trade): TOURNAMENT vs TOP_SCORE ===")
    print(f"paired entry_days (both arms closed): {len(paired)}")
    print(_line("TOURNAMENT intraday", _stats(paired["TOURNAMENT"])))
    print(_line("TOP_SCORE  intraday", _stats(paired["TOP_SCORE"])))
    if len(paired) > 0:
        spread = paired["TOURNAMENT"] - paired["TOP_SCORE"]
        print(f"  mean (tournament - top_score) spread: {spread.mean()*100:+6.2f}%  "
              f"(tournament beats top_score on {int((spread > 0).sum())}/{len(paired)} days)")
    return int(len(paired))


def main() -> None:
    df = _load()
    if len(df) == 0:
        print("No intraday shadow rows yet. (Runs on HAS_PICK days; written in arrears.)")
        print(f"\nDO NOT ACT until N >= {DECISION_THRESHOLD} paired closes.")
        return

    clean = df[df["intraday_illiquid"] != True]  # noqa: E712  (drop stale same-day marks)
    for arm in ("TOURNAMENT", "TOP_SCORE"):
        _arm_block(arm, clean)
    n_cross = _cross_block(clean)

    print(f"\nDO NOT ACT until N >= {DECISION_THRESHOLD} paired closes. "
          f"Current cross paired N = {n_cross}.")


if __name__ == "__main__":
    main()
