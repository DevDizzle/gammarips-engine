"""Create `overnight_signals_enriched_safe` — a leakage-safe view over the
enriched signal pool (substrate must-fix #4, upstream guard).

WHY THIS EXISTS
---------------
`overnight_signals_enriched` is the tournament candidate set — mostly point-in-
time features. But `win-tracker` MERGEs FORWARD-OUTCOME columns back onto it
(next_day_pct / day2_pct / day3_pct / peak_return_3d / is_win / outcome_tier,
plus the forward underlying closes next_day_close / day2_close / day3_close and
the outcome-write stamp performance_updated). An agent that wanders UPSTREAM
from the features view into this raw table and does `SELECT *` would leak the
future.

This view is the physical guard for that upstream table: it exposes everything
EXCEPT the win-tracker forward-outcome columns, so an agent can safely mine the
enriched pool's descriptive features without touching a realized outcome.

DESIGN CHOICE — EXPLICIT-DROP (denylist), not allowlist
-------------------------------------------------------
`overnight_signals_enriched` is a wide, drift-prone table: its schema is ensured
via `ALTER TABLE ADD COLUMN IF NOT EXISTS` on every enrichment run, and the
whole point of the enriched pool is to carry through ALL descriptive features.
An allowlist here would be brittle (it would silently drop every newly-added
legitimate feature). The leak surface, by contrast, is small and well-defined:
exactly the columns win-tracker writes back. So this view uses
`SELECT * EXCEPT(<forward-outcome columns>)`.

  >>> MAINTENANCE RULE: if win-tracker (or anything) ever writes a NEW forward-
  >>> outcome column onto overnight_signals_enriched, ADD it to
  >>> FORWARD_OUTCOME_DROP below and re-run --execute. <<<

For the OUTCOME-labeled research substrate, prefer `enriched_features_v1` (over
enriched_option_outcomes) — that one is a strict allowlist.

SAFETY / GATING
---------------
Read-only DDL that creates a VIEW (no data copied or mutated). Gated:
  - DRY-RUN by default: prints the DDL and validates the SELECT against the live
    table via a BigQuery dry-run (no bytes billed, nothing created).
  - Pass --execute to CREATE OR REPLACE the view.
REQUIRES gammarips-review before --execute. No deploy.

    python scripts/ledger_and_tracking/create_enriched_signals_safe_view.py
    python scripts/ledger_and_tracking/create_enriched_signals_safe_view.py --execute
"""

import argparse
import sys

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
BASE_TABLE = "overnight_signals_enriched"
VIEW_ID = "overnight_signals_enriched_safe"

BASE_REF = f"{PROJECT_ID}.{DATASET_ID}.{BASE_TABLE}"
VIEW_REF = f"{PROJECT_ID}.{DATASET_ID}.{VIEW_ID}"

# ---------------------------------------------------------------------------
# FORWARD-OUTCOME columns written back by win-tracker (see win-tracker/main.py
# temp_perf_updates schema + the MERGE into overnight_signals_enriched). These
# are realized AFTER scan_date and MUST NOT be exposed as features. Verified
# present on the live table as of 2026-07-01.
# ---------------------------------------------------------------------------
FORWARD_OUTCOME_DROP = [
    # Forward underlying returns (the win-tracker outcome tiers):
    "next_day_pct",
    "day2_pct",
    "day3_pct",
    "peak_return_3d",
    "is_win",
    "outcome_tier",
    # Forward underlying closing prices (the raw values behind the pct fields):
    "next_day_close",
    "day2_close",
    "day3_close",
    # Outcome-write telemetry (non-null only once the row has been labeled):
    "performance_updated",
]


# ---------------------------------------------------------------------------
# PRE-EXECUTE DENYLIST GUARD (#4 review, rec 2). A denylist (SELECT * EXCEPT)
# is only as safe as its drop-list is current: if win-tracker (or anything)
# adds a NEW forward-outcome column to overnight_signals_enriched and nobody
# updates FORWARD_OUTCOME_DROP, `SELECT * EXCEPT(...)` silently carries the new
# outcome through and the view leaks. The working tree can't verify the live
# schema, so before --execute we query INFORMATION_SCHEMA.COLUMNS and ABORT
# LOUDLY on any live column whose name matches a forward-outcome PATTERN yet is
# NOT already in FORWARD_OUTCOME_DROP. Fail-closed: a suspected leak stops the
# create until a human classifies the column (add to the drop-list, or confirm
# it is a genuine feature by widening the guard's known-safe set).
# ---------------------------------------------------------------------------
_FORWARD_OUTCOME_PATTERNS = (
    "next_day",
    "day2",
    "day3",
    "peak_return",
    "is_win",
    "outcome_tier",
    "performance_updated",
)


def _matches_forward_outcome_pattern(name: str) -> bool:
    low = name.lower()
    if low.endswith("_close"):
        return True
    return any(p in low for p in _FORWARD_OUTCOME_PATTERNS)


def suspicious_forward_outcome_columns(client: bigquery.Client) -> list[str]:
    """Live columns matching a forward-outcome pattern but NOT in the drop-list.

    Non-empty => the denylist is stale and the view would leak. Read-only:
    a single INFORMATION_SCHEMA.COLUMNS scan (0 bytes billed).
    """
    sql = (
        f"SELECT column_name FROM "
        f"`{PROJECT_ID}.{DATASET_ID}`.INFORMATION_SCHEMA.COLUMNS "
        f"WHERE table_name = @tbl"
    )
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("tbl", "STRING", BASE_TABLE)]
    )
    drop = set(FORWARD_OUTCOME_DROP)
    suspicious = [
        row["column_name"]
        for row in client.query(sql, job_config=job_config).result()
        if row["column_name"] not in drop
        and _matches_forward_outcome_pattern(row["column_name"])
    ]
    return sorted(suspicious)


def build_select_sql() -> str:
    drop = ", ".join(FORWARD_OUTCOME_DROP)
    return f"SELECT * EXCEPT({drop})\nFROM `{BASE_REF}`"


def build_create_ddl() -> str:
    select_sql = build_select_sql()
    description = (
        "Leakage-safe view over overnight_signals_enriched (substrate must-fix "
        "#4). SELECT * EXCEPT the win-tracker forward-outcome columns "
        "(next_day_pct/day2_pct/day3_pct/peak_return_3d/is_win/outcome_tier + "
        "the *_close forward prices + performance_updated). Use this instead of "
        "the raw table so an agent mining the enriched pool cannot leak the "
        "future. New forward-outcome columns must be added to the EXCEPT list."
    )
    return (
        f"CREATE OR REPLACE VIEW `{VIEW_REF}`\n"
        f"OPTIONS(description=\"\"\"{description}\"\"\")\n"
        f"AS\n{select_sql}\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Actually CREATE OR REPLACE the view (default: dry-run validate only).",
    )
    args = ap.parse_args()

    client = bigquery.Client(project=PROJECT_ID)
    ddl = build_create_ddl()
    select_sql = build_select_sql()

    print("=" * 72)
    print(f"View: {VIEW_REF}")
    print(f"Forward-outcome columns dropped: {len(FORWARD_OUTCOME_DROP)}")
    print("  " + ", ".join(FORWARD_OUTCOME_DROP))
    print("=" * 72)
    print(ddl)
    print("=" * 72)

    if not args.execute:
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = client.query(select_sql, job_config=job_config)
        print("DRY-RUN OK: SELECT validated against the live table.")
        print(f"  would process ~{job.total_bytes_processed:,} bytes (0 billed).")
        print("Re-run with --execute (after gammarips-review) to create the view.")
        return 0

    # Fail-closed on a stale denylist before creating the view (#4 review, rec 2).
    suspicious = suspicious_forward_outcome_columns(client)
    if suspicious:
        print("=" * 72, file=sys.stderr)
        print(
            "ABORT: live columns match a forward-outcome pattern but are NOT in "
            "FORWARD_OUTCOME_DROP — the view would LEAK them:",
            file=sys.stderr,
        )
        for name in suspicious:
            print(f"  {name}", file=sys.stderr)
        print(
            "Add each genuine forward-outcome column to FORWARD_OUTCOME_DROP (or "
            "confirm it is a real feature and widen the guard), then re-run "
            "--execute.",
            file=sys.stderr,
        )
        print("=" * 72, file=sys.stderr)
        return 1

    client.query(ddl).result()
    print(f"CREATED/REPLACED view: {VIEW_REF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
