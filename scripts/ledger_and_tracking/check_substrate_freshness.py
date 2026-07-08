"""Read-only freshness monitor for the enriched_option_outcomes label substrate.

    ################################################################################
    #  SAFETY NET for the untracked label-pool cron SPOF (substrate must-fix #3b).  #
    #  READ-ONLY: this script runs SELECTs only. It NEVER writes, dedups, or          #
    #  backfills anything. Safe to run anytime.                                       #
    #                                                                                 #
    #  MEANT TO BE WIRED to Cloud Scheduler / monitoring (a morning cron + an alert  #
    #  policy on the non-zero exit) — but it is NOT wired up here. Committing the     #
    #  scheduler job / alert policy is a separate, gammarips-review-gated step.       #
    ################################################################################

WHY (substrate must-fix #3, docs/DECISIONS/2026-07-01 substrate integrity pass):
enriched_option_outcomes is written by a daily Cloud Run cron
(forward-paper-trader /label_enriched_pool). That cron is a single point of
failure and — before must-fix #3a — a Polygon minute-bar outage would write a
full pool of INVALID_LIQUIDITY rows (NULL label) and still return HTTP 200, so a
naive row-presence check PASSED a silently-degraded day. This monitor is the
independent morning safety net: it asserts the JUST-CLOSED NYSE trading session
produced a pool that is BOTH present AND well-labeled.

WHAT IT ASSERTS, for the just-closed NYSE trading day (= the entry_day whose
session most recently closed before "now"; enriched_option_outcomes carries an
`entry_day` DATE column, so we key on it directly — unambiguous vs the scan_date
offset):
  1. row count >= 1                       (the pool exists at all)
  2. label fill-rate >= MIN_FILL_RATE     (COUNT(realized_return_pct)/COUNT(*))
     default 0.80                         (catches the all-INVALID_LIQUIDITY /
                                           Polygon-outage degradation)

EXIT CODE: 0 == healthy; non-zero == alert (prints a clear ALERT line). Wire the
non-zero exit to your alerting channel.

USAGE (from repo root):
    python scripts/ledger_and_tracking/check_substrate_freshness.py
    # override the day to check (an entry_day / trading session date):
    python scripts/ledger_and_tracking/check_substrate_freshness.py --entry-day 2026-06-30
    # loosen/tighten the fill-rate floor:
    python scripts/ledger_and_tracking/check_substrate_freshness.py --min-fill-rate 0.9

Read-only per .claude/rules/scripts-ledger.md — do NOT add write/mutate logic here.
"""

import argparse
import sys
from datetime import date, datetime, timedelta

import pandas_market_calendars as mcal
import pytz
from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "enriched_option_outcomes"
TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

DEFAULT_MIN_FILL_RATE = 0.80

_nyse = mcal.get_calendar("NYSE")
_est = pytz.timezone("America/New_York")


def _last_closed_session(now_utc: datetime) -> date | None:
    """Most recent NYSE session whose market_close is strictly before `now_utc`.

    Uses the calendar's real close times (handles half-days), so a run at any hour
    resolves to the trading day whose session has actually ended.
    """
    start = (now_utc.date() - timedelta(days=14))
    sched = _nyse.schedule(start_date=start, end_date=now_utc.date())
    if sched.empty:
        return None
    closed = sched[sched["market_close"] < now_utc]
    if closed.empty:
        return None
    return closed.index[-1].date()


def _pool_health(client: bigquery.Client, entry_day: date) -> dict:
    """Read-only: total rows + labeled rows for one entry_day (trading session)."""
    sql = f"""
    SELECT
        COUNT(*) AS total,
        COUNTIF(realized_return_pct IS NOT NULL) AS labeled
    FROM `{TABLE}`
    WHERE entry_day = @entry_day
    """
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("entry_day", "DATE", entry_day),
    ])
    row = list(client.query(sql, job_config=cfg).result())[0]
    total = int(row["total"] or 0)
    labeled = int(row["labeled"] or 0)
    fill = (labeled / total) if total else 0.0
    return {"total": total, "labeled": labeled, "fill_rate": fill}


def main() -> int:
    ap = argparse.ArgumentParser(description="enriched_option_outcomes freshness monitor (read-only)")
    ap.add_argument("--entry-day", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=None, help="trading-session date to check (default: just-closed NYSE session)")
    ap.add_argument("--min-fill-rate", type=float, default=DEFAULT_MIN_FILL_RATE,
                    help=f"minimum labeled/total ratio (default {DEFAULT_MIN_FILL_RATE})")
    args = ap.parse_args()

    now_utc = datetime.now(pytz.utc)
    entry_day = args.entry_day or _last_closed_session(now_utc)
    if entry_day is None:
        print("ALERT: could not resolve a just-closed NYSE trading session to check.")
        return 2

    client = bigquery.Client(project=PROJECT_ID)
    h = _pool_health(client, entry_day)

    print(f"=== substrate freshness: {TABLE} ===")
    print(f"    entry_day (just-closed session): {entry_day}")
    print(f"    rows           : {h['total']}")
    print(f"    labeled (PnL)  : {h['labeled']}")
    print(f"    fill-rate      : {h['fill_rate']*100:.1f}%  (floor {args.min_fill_rate*100:.0f}%)")

    problems: list[str] = []
    if h["total"] < 1:
        problems.append(f"no rows for the just-closed session {entry_day} "
                        f"(label-pool cron missed/failed, or empty/degraded pool)")
    elif h["fill_rate"] < args.min_fill_rate:
        problems.append(f"label fill-rate {h['fill_rate']*100:.1f}% below floor "
                        f"{args.min_fill_rate*100:.0f}% for {entry_day} "
                        f"(likely a Polygon minute-bar outage -> all-INVALID_LIQUIDITY)")

    if problems:
        for p in problems:
            print(f"ALERT: {p}")
        print("ACTION: check the /label_enriched_pool cron + Polygon; the day may need a re-label.")
        return 1

    print("OK: substrate is fresh and well-labeled for the just-closed session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
