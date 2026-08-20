"""Live paper-cohort definition for the PUBLISHING services.

Shared by `x-poster` and `blog-generator` (both vendor this lib at deploy time).

WHY THIS EXISTS (2026-08-07): the live cohort is a **(policy label, start date)
PAIR**. The label alone is NOT sufficient, and treating it as sufficient is a
publishing hazard, not just an analytics nit.

Since 2026-07-28 the engine's cohort resets are DATE-FILTER resets rather than
ledger truncations, so rows from disowned cohorts stay in `forward_paper_ledger`
carrying the SAME `policy_version`. Every query that filtered on the label alone
silently swept them back in. On 2026-08-07 that meant:

  * `blog-generator`'s 30-trade unlock gate counted 30 all-time closes under the
    V7.1 label and would have tripped on Monday 2026-08-10 — publishing a
    "30 trades in the books" milestone built on a cohort the engine had just
    repudiated. Its own code comment already said prior cohorts "would falsely
    trip the 30-trade unlock gate"; the intent was right and the SQL did not
    implement it.
  * the same defect in `gammarips-mcp` served the disowned 2026-07-29 cohort as
    live receipts on the paid surface for ~10 days.

MIRRORS `signal-notifier/main.py::LIVE_COHORT_START_DATE`. These services run as
separate Cloud Run units and cannot import the notifier, so this is a mirrored
constant — when the engine resets its cohort, THIS MUST MOVE WITH IT, and both
publishers must be redeployed to pick it up. Constants drifting apart is the
whole defect: the MCP said "since 2026-06-26" through two resets.

Cohort history: 2026-06-26 (live-OI floor) -> 2026-07-29 (tournament liquidity
upgrade) -> 2026-08-10 (stale-day-bar fix; the 07-29 cohort's primary print
floor never actually fired) -> 2026-08-13 (fail-soft restore closed; 2 of the
08-10 cohort's 3 entries were sub-floor restores the new code cannot select)
-> 2026-08-21 (PRINT_FLOOR_MIN raised 1 -> 25; ghosts scrubbed from the slate).
See `docs/DECISIONS/2026-08-20-score-floor-accepted-print-floor-25-shipped.md`.
"""

from __future__ import annotations

LIVE_POLICY_VERSION = "V7_1_TILTED_GIGO"
LIVE_COHORT_START_DATE = "2026-08-21"

# SQL fragment for a ledger query that has already bound/most commonly filters
# on `policy_version`. Entry-dated in ET to match the engine's own cohort
# membership. Append to a WHERE clause; requires no query parameters so it is
# safe to concatenate (it interpolates only module constants, never caller
# input — do NOT rewrite this to take user input).
LIVE_COHORT_SQL = (
    f"policy_version = '{LIVE_POLICY_VERSION}' "
    f"AND DATE(entry_timestamp, 'America/New_York') >= DATE('{LIVE_COHORT_START_DATE}')"
)

# For rows that have no entry (skips) the floor must land on scan_date instead.
LIVE_COHORT_SQL_BY_SCAN_DATE = (
    f"policy_version = '{LIVE_POLICY_VERSION}' "
    f"AND scan_date >= DATE('{LIVE_COHORT_START_DATE}')"
)

__all__ = [
    "LIVE_POLICY_VERSION",
    "LIVE_COHORT_START_DATE",
    "LIVE_COHORT_SQL",
    "LIVE_COHORT_SQL_BY_SCAN_DATE",
]
