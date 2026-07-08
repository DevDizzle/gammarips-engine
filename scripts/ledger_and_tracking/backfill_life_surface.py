"""One-shot backfill: fill the FULL-LIFE (surfaced -> expiration) surface columns
on existing enriched_option_outcomes rows for EXPIRED contracts.

WHY (scorecard redesign, owner-approved 2026-07-08): the public Track Record is
moving off the arbitrary fixed-exit ROI/win-rate to the distribution of what each
surfaced contract did over its WHOLE life — peak/trough excursion to expiration
plus the hold-to-settlement mark. The daily /label_life_surface cron only labels
newly-expired contracts going forward; this script fills the ~2,300 historical
rows whose contracts have already expired so the distribution has day-one mass.

BYTE-IDENTICAL by construction: IMPORTS the deployed collector functions
(_simulate_life_surface, _underlying_closes_at_expiry, _merge_life_rows,
_ensure_enriched_outcomes_columns) from forward-paper-trader/main.py rather than
re-implementing anything — same source of truth as the daily pass. Same pattern
as backfill_opportunity_surface.py.

LEAKAGE-SAFE: only contracts whose expiration is strictly before today ET are
labeled (final session complete); the anchor is the stored opp_entry_price
(the 10:00 ET post-surfacing fill); the surface applies NO exit rule. Writes
ONLY life_* columns on enriched_option_outcomes — never forward_paper_ledger or
any live surface.

IDEMPOTENT: deterministic values MERGEd on (scan_date, ticker,
recommended_contract) via the shared staged-load helper (explicit schema, never
autodetect). By default only rows with life_status IS NULL are processed;
--force recomputes all expired rows.

RUNTIME: must run in the forward-paper-trader runtime so the imported logic is
byte-identical to the deployed collector:
    pip install -r forward-paper-trader/requirements.txt
    export POLYGON_API_KEY=$(gcloud secrets versions access latest \
        --secret=POLYGON_API_KEY --project=profitscout-fida8)

USAGE (from repo root):
    # PREVIEW — no Polygon calls, no DATA writes (it does run the idempotent
    # ADD COLUMN IF NOT EXISTS schema-ensure so the life_status filter parses):
    python scripts/ledger_and_tracking/backfill_life_surface.py --dry-run
    # EXECUTE (after gammarips-review + owner OK):
    python scripts/ledger_and_tracking/backfill_life_surface.py --confirm
    # options: --limit N (test run), --force (recompute all expired rows)

One-shot migration script (per .claude/rules/scripts-ledger.md): do NOT re-run
without explicit user approval.
"""

import argparse
import os
import sys
from datetime import datetime, date

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE = f"{PROJECT_ID}.{DATASET_ID}.enriched_option_outcomes"

# Import the deployed collector logic (byte-identical to the daily pass).
_FPT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "forward-paper-trader",
)
sys.path.insert(0, _FPT_DIR)


def _rows_to_process(client, today_et: date, force: bool, limit: int | None):
    fill_filter = "" if force else "AND life_status IS NULL"
    lim = f"LIMIT {int(limit)}" if limit else ""
    # QUALIFY dedup: ~145 documented duplicate identity keys in the table —
    # two identical source keys would abort a whole MERGE batch. Lossless
    # (values are deterministic per key). NULL-contract rows are excluded:
    # they can never match the MERGE ON clause and would re-queue forever.
    sql = f"""
    SELECT scan_date, entry_day, ticker, direction, recommended_contract,
           recommended_strike, recommended_expiration,
           opp_entry_price, opp_peak_return, opp_trough_return, opp_status
    FROM `{TABLE}`
    WHERE recommended_expiration IS NOT NULL
      AND recommended_strike IS NOT NULL
      AND recommended_contract IS NOT NULL
      AND recommended_expiration < @today
      {fill_filter}
    QUALIFY ROW_NUMBER() OVER (
      PARTITION BY scan_date, ticker, recommended_contract
      ORDER BY labeled_at DESC) = 1
    ORDER BY recommended_expiration, scan_date, ticker
    {lim}
    """
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("today", "DATE", today_et),
    ])
    return [dict(r) for r in client.query(sql, job_config=cfg).result()]


def main():
    ap = argparse.ArgumentParser(description="Backfill full-life (surfaced->expiration) surface")
    ap.add_argument("--limit", type=int, default=None, help="cap rows (for a test run)")
    ap.add_argument("--force", action="store_true", help="recompute ALL expired rows")
    ap.add_argument("--batch", type=int, default=200, help="MERGE batch size")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true",
                     help="report only; no Polygon calls, no DATA writes "
                          "(does run the idempotent ADD COLUMN IF NOT EXISTS "
                          "schema-ensure, needed for the life_status filter)")
    grp.add_argument("--confirm", action="store_true", help="EXECUTE (review + owner OK)")
    args = ap.parse_args()

    try:
        import main as fpt  # forward-paper-trader/main.py  # noqa: N813
    except Exception as e:  # noqa: BLE001
        print(f"FATAL: could not import forward-paper-trader main: {e}")
        print("       Run inside the forward-paper-trader runtime (see module header).")
        sys.exit(2)

    if args.confirm and not os.environ.get("POLYGON_API_KEY", "").strip():
        print("FATAL: POLYGON_API_KEY not in env — required for --confirm (see header).")
        sys.exit(2)

    client = bigquery.Client(project=PROJECT_ID)
    today_et = datetime.now(fpt.est).date()

    # Schema-ensure BEFORE the life_status filter — on the very first run the
    # life columns do not exist yet and the SELECT would otherwise 400.
    fpt._ensure_enriched_outcomes_columns(client, TABLE)

    rows = _rows_to_process(client, today_et, args.force, args.limit)
    with_entry = sum(1 for r in rows if r.get("opp_entry_price") is not None)
    print("=== full-life surface backfill ===")
    print(f"    mode  : {'DRY-RUN (no writes)' if args.dry_run else 'EXECUTE (writing)'}")
    print(f"    expired unlabeled rows : {len(rows)}")
    print(f"    with opp entry anchor  : {with_entry} (rest get life_status=NO_ENTRY)\n")

    if args.dry_run:
        print(f"  [dry-run] {with_entry} rows would fetch Polygon daily bars + MERGE; "
              f"{len(rows) - with_entry} would be stamped NO_ENTRY. "
              f"Re-run with --confirm after review + owner OK.")
        return

    closes = fpt._underlying_closes_at_expiry(
        client, [r for r in rows if r.get("opp_entry_price") is not None]
    )
    print(f"    settlement marks found : "
          f"{sum(1 for v in closes.values() if v is not None)}/{len(closes)}")

    computed, statuses, total = [], {}, 0
    for i, r in enumerate(rows):
        entry_day = r["entry_day"] or fpt.get_next_trading_day(r["scan_date"])
        exp = r["recommended_expiration"]
        # datetime-first coercion (datetime IS a date subclass — the reversed
        # check would keep a time component and miss the closes dict key).
        exp_date = exp.date() if isinstance(exp, datetime) else exp
        life = fpt._simulate_life_surface(
            r, entry_day, closes.get((r["ticker"], exp_date.isoformat()))
        )
        statuses[life["life_status"]] = statuses.get(life["life_status"], 0) + 1
        computed.append({
            "scan_date": r["scan_date"],
            # ticker EXACTLY as stored — the MERGE key is case-sensitive (see
            # backfill_opportunity_surface.py's note).
            "ticker": r["ticker"],
            "recommended_contract": r["recommended_contract"],
            **life,
        })
        if len(computed) >= args.batch:
            total += fpt._merge_life_rows(client, computed)
            print(f"  ... merged batch through row {i+1}/{len(rows)} (cum updated={total})")
            computed = []
    total += fpt._merge_life_rows(client, computed)

    print("\n=== SUMMARY ===")
    print(f"  candidate rows : {len(rows)}")
    print(f"  rows updated   : {total}")
    print(f"  statuses       : {statuses}")


if __name__ == "__main__":
    main()
