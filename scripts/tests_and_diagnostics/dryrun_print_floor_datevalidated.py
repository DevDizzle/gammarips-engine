"""DRY RUN: replay the date-validated early-print floor over recent sessions.

READ-ONLY against BigQuery. Deploy gate for the 2026-08-07 stale-day-bar fix
(docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md).

Why this exists: the fix converts a stale prior-session day bar into a KNOWN
ZERO, which the existing PRINT_FLOOR_MIN=1 floor then drops. Roughly half the
pool carries a stale bar at the ~09:52 read, so the floor goes from dropping
NOTHING (it has never fired since go-live) to dropping a large share of every
slate, with the fail-soft restore absorbing the difference. That behavioral
delta is the actual deploy risk, and it is not something the unit tests can
show. This script measures it on real snapshots.

It replays PRODUCTION code paths (`_validate_day_bar_volume`, `_edge_rank_and_cap`,
`_liquidity_refresh_and_rank`) against persisted `pool_liquidity_snapshot` reads
rather than reimplementing them in SQL, so the numbers reflect what the service
would actually have done.

    .venv/bin/python scripts/tests_and_diagnostics/dryrun_print_floor_datevalidated.py
    .venv/bin/python scripts/tests_and_diagnostics/dryrun_print_floor_datevalidated.py --days 20
"""

from __future__ import annotations

import argparse
import os
import sys
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "signal-notifier"))

import main  # noqa: E402

# CLAUDE.md workstation footgun: the shell exports PROJECT_ID for another
# project. Pin it explicitly — never rely on a getenv fallback here.
PROJECT_ID = "profitscout-fida8"

QUERY = f"""
WITH reads AS (
  SELECT
    DATE(s.as_of, "America/New_York")           AS read_date,
    s.as_of,
    s.scan_date,
    s.contract,
    s.underlying                                AS ticker,
    s.day_volume,
    s.day_last_updated,
    s.open_interest                             AS live_oi,
    ROW_NUMBER() OVER (
      PARTITION BY DATE(s.as_of, "America/New_York"), s.contract
      ORDER BY s.as_of
    ) AS rn
  FROM `{PROJECT_ID}.profit_scout.pool_liquidity_snapshot` s
  WHERE s.fetch_status = "ok"
    AND s.as_of >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @lookback_days DAY)
    AND EXTRACT(HOUR FROM s.as_of AT TIME ZONE "America/New_York") * 60
      + EXTRACT(MINUTE FROM s.as_of AT TIME ZONE "America/New_York")
        BETWEEN 585 AND 600          -- the 09:45-10:00 ET pick window
)
SELECT
  r.read_date, r.as_of, r.contract, r.ticker,
  r.day_volume, r.day_last_updated, r.live_oi,
  e.direction, e.recommended_delta, e.risk_reward_ratio,
  e.atr_normalized_move, e.overnight_score, e.recommended_oi
FROM reads r
JOIN `{PROJECT_ID}.profit_scout.overnight_signals_enriched` e
  ON e.recommended_contract = r.contract AND e.scan_date = r.scan_date
WHERE r.rn = 1
ORDER BY r.read_date, r.contract
"""


def _ns(ts) -> int | None:
    """BQ TIMESTAMP -> Polygon-style epoch nanoseconds (what the fix parses)."""
    if ts is None or pd.isna(ts):
        return None
    return int(ts.timestamp() * 1_000_000_000)


def _replay_day(day_df: pd.DataFrame) -> dict:
    """Replay one session's slate through the real cap + floor, pre and post fix."""
    read_dt_et = day_df["as_of"].iloc[0].tz_convert(main.est).to_pydatetime()

    df = day_df.copy()
    # PRE-fix: the raw day.volume, exactly as _fetch_live_oi used to return it.
    df["_prefix_volume"] = df["day_volume"]
    # POST-fix: the same value through the production validator.
    df["_postfix_volume"] = [
        main._validate_day_bar_volume(
            int(row.day_volume) if pd.notna(row.day_volume) else None,
            _ns(row.day_last_updated),
            row.contract,
            read_dt_et,
        )
        for row in df.itertuples()
    ]

    pool50_zero = int((df["_postfix_volume"] == 0).sum())

    # Real edge-rank cap -> the slate the tournament actually sees.
    capped = main._edge_rank_and_cap(df, main.TOURNEY_POOL_CAP)

    out = {
        "read_date": day_df["read_date"].iloc[0],
        "read_et": read_dt_et.strftime("%H:%M"),
        "pool_n": len(df),
        "pool50_known_zero": pool50_zero,
        "capped_n": len(capped),
        "capped_known_zero": int((capped["_postfix_volume"] == 0).sum()),
    }

    for tag in ("prefix", "postfix"):
        slate = capped.copy()
        slate["_today_volume"] = slate[f"_{tag}_volume"]
        # Stub the network refresh: the replayed columns ARE the refresh result.
        with patch.object(main, "_refresh_live_oi_batch", side_effect=lambda d: d.copy()):
            survivors = main._liquidity_refresh_and_rank(slate)
        restored_col = survivors.get("_print_floor_restored")
        n_restored = (
            int(pd.Series(restored_col).fillna(False).astype(bool).sum())
            if restored_col is not None else 0
        )
        # THE metric for the second wall: how many ZERO-PRINT names the fail-soft
        # restore hands back to the judge. Those are the rows Fix 2a must catch.
        if restored_col is not None and len(survivors):
            restored_rows = survivors[pd.Series(restored_col).fillna(False).astype(bool).values]
            n_zero_restored = sum(
                1 for _, r in restored_rows.iterrows() if main._known_prints(r) == 0
            )
        else:
            n_zero_restored = 0
        out[f"{tag}_survivors"] = len(survivors)
        out[f"{tag}_restored"] = n_restored
        out[f"{tag}_zero_restored"] = n_zero_restored
        out[f"{tag}_genuine"] = len(survivors) - n_restored
        out[f"{tag}_top"] = survivors.iloc[0]["ticker"] if len(survivors) else None
    return out


def main_cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=14,
                    help="calendar-day lookback (default 14 ~= 10 sessions)")
    args = ap.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID)
    job_cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("lookback_days", "INT64", args.days),
    ])
    df = client.query(QUERY, job_config=job_cfg).to_dataframe()
    if df.empty:
        print("No snapshot reads in the 09:45-10:00 ET window for that lookback.")
        return

    rows = [_replay_day(g) for _, g in df.groupby("read_date", sort=True)]
    res = pd.DataFrame(rows)

    print(f"\nDate-validated print floor — dry run over {len(res)} sessions")
    print(f"PRINT_FLOOR_MIN={main.PRINT_FLOOR_MIN}  OI_FLOOR={main.OI_FLOOR}  "
          f"TOURNEY_MIN={main.TOURNEY_MIN}  TOURNEY_POOL_CAP={main.TOURNEY_POOL_CAP}  "
          f"PRINT_VALID_AFTER_ET_MIN={main.PRINT_VALID_AFTER_ET_MIN}\n")

    hdr = (f"{'date':<12}{'read':>6}{'pool0/50':>10}{'cap0/12':>9}"
           f"{'PRE surv':>9}{'PRE rst':>8}{'POST surv':>10}{'POST rst':>9}"
           f"{'POST real':>10}  {'pick changes':<14}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        changed = "" if r["prefix_top"] == r["postfix_top"] else \
            f"{r['prefix_top']} -> {r['postfix_top']}"
        print(f"{str(r['read_date']):<12}{r['read_et']:>6}"
              f"{r['pool50_known_zero']:>7}/{r['pool_n']:<3}"
              f"{r['capped_known_zero']:>6}/{r['capped_n']:<3}"
              f"{r['prefix_survivors']:>9}{r['prefix_restored']:>8}"
              f"{r['postfix_survivors']:>10}{r['postfix_restored']:>9}"
              f"{r['postfix_genuine']:>10}  {changed:<14}")

    n = len(res)
    print(f"\n  pool-of-50 known-zero, mean      {res['pool50_known_zero'].mean():.1f}"
          f" / 50  ({100 * res['pool50_known_zero'].mean() / res['pool_n'].mean():.0f}%)")
    print(f"  capped slate known-zero, mean    {res['capped_known_zero'].mean():.1f}"
          f" / {res['capped_n'].mean():.0f}")
    print(f"  PRE-fix  floor drops             "
          f"{(res['capped_n'] - res['prefix_survivors']).sum()} across {n} sessions")
    print(f"  POST-fix floor drops             "
          f"{(res['capped_n'] - res['postfix_survivors']).sum()} across {n} sessions")
    print(f"  POST-fix genuinely-clearing, mean {res['postfix_genuine'].mean():.1f}"
          f"  (fail-soft restores: {res['postfix_restored'].mean():.1f}/session)")
    starved = int((res["postfix_genuine"] < main.TOURNEY_MIN).sum())
    print(f"  sessions where fail-soft carries the slate: {starved}/{n}")
    zr = res["postfix_zero_restored"]
    print(f"  ZERO-PRINT names restored to the judge:     {int(zr.sum())} total, "
          f"{int((zr > 0).sum())}/{n} sessions (max {int(zr.max())}/session)")
    print("    ^ this is what the tournament_v1_2 'early_volume 0 = untradeable' "
          "sentence exists to catch.")
    changed = int((res["prefix_top"] != res["postfix_top"]).sum())
    print(f"  sessions where the top-ranked slate name changes: {changed}/{n}")
    print("\nNOTE: 'top' is the floor's OI-desc ordering, NOT the tournament pick "
          "(the judge selects). Treat it as a slate-composition signal only.\n")


if __name__ == "__main__":
    main_cli()
