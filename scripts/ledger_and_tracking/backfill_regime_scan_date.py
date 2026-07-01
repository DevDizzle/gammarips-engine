"""One-shot IN-PLACE backfill: correct the regime as-of on enriched_option_outcomes.

    ################################################################################
    #  NOT YET EXECUTED.  This is a BigQuery WRITE (in-place UPDATE of a research    #
    #  table).  It is gammarips-review + OWNER gated.  Do NOT run it until both       #
    #  sign off AND the leakage-fix collector (forward-paper-trader main.py,          #
    #  substrate must-fix #2) is DEPLOYED — the schema/semantics must match.          #
    ################################################################################

WHY (substrate must-fix #2, docs/DECISIONS/2026-07-01-regime-scan-date-leakage-fix.md):
The regime columns on `enriched_option_outcomes` were stamped at ENTRY-DAY CLOSE
(16:00) but filed as point-in-time FEATURES. The trade enters 10:00 and exits 15:45
the SAME day, so VIX_at_entry / SPY_trend_state / vix_5d_delta_entry are realized
AFTER the trade closes — a future-leak for any agent conditioning on them, and
non-deterministic between the daily cron and backfill. Selection happens at
scan-time, so the leakage-correct regime FEATURE is as-of SCAN_DATE close.

WHAT THIS DOES (surgical, in-place, idempotent — labels are NOT re-simulated):
  STEP A (table-wide, once): migrate the legacy entry-day-close regime into the new
          oc_*_at_close TELEMETRY columns, only where those are still NULL
          (COALESCE) — so no entry-close data is ever silently dropped.
  STEP B (per scan_date): recompute the SCAN_DATE-close regime with the SAME
          production helper the fixed collector uses (forward-paper-trader
          get_regime_context, anchored <= scan_date), and write it to the new
          FEATURE columns vix_at_scan / spy_trend_at_scan / vix_5d_delta_at_scan.
  STEP C (OPTIONAL, destructive, left commented out): drop the legacy
          VIX_at_entry / SPY_trend_state / vix_5d_delta_entry columns ONLY AFTER
          verifying STEP A migrated every row. Requires a SEPARATE explicit OK.

Byte-identical regime by construction: this REUSES forward-paper-trader's
get_regime_context rather than re-implementing it, so backfilled rows match what
the deployed collector writes going forward (no parallel/divergent logic). Because
get_regime_context filters bars `<= target_ts` internally, anchoring it to
scan_date GUARANTEES the anchor bar is <= scan_date (the leakage guard).

WRITES ONLY to profitscout-fida8.profit_scout.enriched_option_outcomes (a research
table). NEVER touches forward_paper_ledger or any live surface. Idempotent: STEP A
uses COALESCE; STEP B overwrites deterministic values; safe to re-run.

RUNTIME: must run in the forward-paper-trader runtime environment so the import +
regime computation are byte-identical to the deployed collector:
    pip install -r forward-paper-trader/requirements.txt
    export POLYGON_API_KEY=...        # required for the SPY 10-day SMA
    # (VIX comes from FRED, no key needed)

USAGE (from repo root):
    # PREVIEW — reads only, computes regime, writes NOTHING:
    python scripts/ledger_and_tracking/backfill_regime_scan_date.py --dry-run
    # EXECUTE (only after review + owner sign-off + deploy):
    python scripts/ledger_and_tracking/backfill_regime_scan_date.py --confirm
    # window override:
    ... --start 2026-04-10 --end 2026-07-01

ONE-SHOT migration script (per .claude/rules/scripts-ledger.md): do NOT re-run
without explicit user approval.
"""

import argparse
import os
import sys
from datetime import datetime, date

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "enriched_option_outcomes"
TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Import the PRODUCTION regime helper so backfilled rows are byte-identical to the
# deployed collector (no re-implementation drift). forward-paper-trader/ must be on
# sys.path and its deps installed (see the module header RUNTIME note).
_FPT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "forward-paper-trader",
)
sys.path.insert(0, _FPT_DIR)

# New FEATURE columns (scan-date close) and new TELEMETRY columns (entry-day close).
FEATURE_COLS = ["vix_at_scan", "spy_trend_at_scan", "vix_5d_delta_at_scan"]
TELEMETRY_COLS = ["oc_vix_at_close", "oc_spy_trend_at_close", "oc_vix_5d_delta_at_close"]
# Legacy entry-close columns that were mislabeled as features (migrated -> telemetry).
LEGACY_MAP = {
    "oc_vix_at_close": ("VIX_at_entry", "FLOAT64"),
    "oc_spy_trend_at_close": ("SPY_trend_state", "STRING"),
    "oc_vix_5d_delta_at_close": ("vix_5d_delta_entry", "FLOAT64"),
}
_COL_TYPE = {
    "vix_at_scan": "FLOAT64", "spy_trend_at_scan": "STRING", "vix_5d_delta_at_scan": "FLOAT64",
    "oc_vix_at_close": "FLOAT64", "oc_spy_trend_at_close": "STRING", "oc_vix_5d_delta_at_close": "FLOAT64",
}


def _existing_columns(client) -> set[str]:
    return {f.name for f in client.get_table(TABLE).schema}


def _ensure_columns(client, cols: set[str], dry_run: bool) -> None:
    """ADD COLUMN IF NOT EXISTS for any corrected column not yet on the table.

    Belt-and-suspenders: the deployed collector's atomic write path also adds these
    on its first post-deploy run. Harmless if they already exist.
    """
    missing = [c for c in (FEATURE_COLS + TELEMETRY_COLS) if c not in cols]
    if not missing:
        print("  columns: all corrected columns already present")
        return
    adds = ", ".join(f"ADD COLUMN IF NOT EXISTS `{c}` {_COL_TYPE[c]}" for c in missing)
    ddl = f"ALTER TABLE `{TABLE}` {adds}"
    if dry_run:
        print(f"  [dry-run] would run: {ddl}")
        return
    client.query(ddl).result()
    print(f"  columns: added {missing}")


def _migrate_legacy_telemetry(client, cols: set[str], dry_run: bool) -> None:
    """STEP A — move the legacy entry-close regime into oc_*_at_close (COALESCE).

    Only touches rows where the telemetry column is still NULL, so re-running is a
    no-op and no entry-close value is ever dropped before it is preserved.
    """
    sets = []
    for oc, (legacy, _t) in LEGACY_MAP.items():
        if legacy in cols:
            sets.append(f"`{oc}` = COALESCE(`{oc}`, `{legacy}`)")
    if not sets:
        print("  STEP A: no legacy entry-close columns present; nothing to migrate")
        return
    where = " OR ".join(f"`{oc}` IS NULL" for oc in LEGACY_MAP)
    sql = f"UPDATE `{TABLE}` SET {', '.join(sets)} WHERE {where}"
    if dry_run:
        print(f"  STEP A [dry-run] would run:\n    {sql}")
        return
    job = client.query(sql)
    job.result()
    print(f"  STEP A: migrated legacy entry-close -> telemetry ({job.num_dml_affected_rows} rows)")


def _scan_dates(client, start: date, end: date) -> list[date]:
    sql = f"""
    SELECT DISTINCT scan_date AS d
    FROM `{TABLE}`
    WHERE scan_date BETWEEN @start AND @end
    ORDER BY d
    """
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("start", "DATE", start),
        bigquery.ScalarQueryParameter("end", "DATE", end),
    ])
    return [r["d"] for r in client.query(sql, job_config=cfg).result()]


def _update_scan_date_features(client, get_regime_context, vix_cache_reset, d: date,
                               dry_run: bool) -> int:
    """STEP B — recompute the SCAN_DATE-close regime and set the FEATURE columns.

    get_regime_context(d) anchors bars `<= d` internally (the leakage guard), so
    the returned regime is as-of scan_date close by construction.
    """
    # The production helper caches the VIX frame in-process (per Cloud Run
    # invocation). In this long-lived loop the cache would freeze to the FIRST
    # date's 60-day window and mis-date every later row — reset it per date.
    vix_cache_reset()
    vix, spy_trend, vix_5d = get_regime_context(d)

    sql = f"""
    UPDATE `{TABLE}`
    SET vix_at_scan = @vix,
        spy_trend_at_scan = @spy,
        vix_5d_delta_at_scan = @delta
    WHERE scan_date = @d
    """
    params = [
        bigquery.ScalarQueryParameter("vix", "FLOAT64", float(vix) if vix is not None else None),
        bigquery.ScalarQueryParameter("spy", "STRING", spy_trend),
        bigquery.ScalarQueryParameter("delta", "FLOAT64", float(vix_5d) if vix_5d is not None else None),
        bigquery.ScalarQueryParameter("d", "DATE", d),
    ]
    delta_str = f"{vix_5d:+.2f}" if vix_5d is not None else "n/a"
    vix_str = f"{vix:.2f}" if vix is not None else "n/a"
    if dry_run:
        print(f"  [dry-run] {d}: vix_at_scan={vix_str} spy={spy_trend} vix_5d={delta_str} "
              f"(would UPDATE)")
        return 0
    job = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params))
    job.result()
    n = job.num_dml_affected_rows or 0
    print(f"  {d}: vix_at_scan={vix_str} spy={spy_trend} vix_5d={delta_str} -> {n} rows")
    return n


def main():
    ap = argparse.ArgumentParser(description="Regime scan-date leakage backfill (must-fix #2)")
    ap.add_argument("--start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date(2026, 4, 10), help="earliest scan_date to backfill")
    ap.add_argument("--end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date.today(), help="latest scan_date to backfill")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true",
                     help="read + compute only; write NOTHING")
    grp.add_argument("--confirm", action="store_true",
                     help="EXECUTE the writes (review + owner sign-off required)")
    args = ap.parse_args()
    dry = args.dry_run

    # Reuse the deployed regime logic (byte-identical to the fixed collector).
    try:
        from main import get_regime_context, _VIX_CACHE  # type: ignore
    except Exception as e:  # noqa: BLE001
        print(f"FATAL: could not import forward-paper-trader main.get_regime_context: {e}")
        print("       Run inside the forward-paper-trader runtime (see module header).")
        sys.exit(2)

    def _vix_cache_reset():
        _VIX_CACHE["df"] = None

    client = bigquery.Client(project=PROJECT_ID)
    mode = "DRY-RUN (no writes)" if dry else "EXECUTE (writing)"
    print(f"=== regime scan-date backfill on {TABLE} ===")
    print(f"    mode  : {mode}")
    print(f"    window: {args.start} .. {args.end}\n")

    cols = _existing_columns(client)
    _ensure_columns(client, cols, dry)
    cols = cols if dry else _existing_columns(client)  # refresh after any ADD COLUMN

    _migrate_legacy_telemetry(client, cols, dry)

    dates = _scan_dates(client, args.start, args.end)
    print(f"\n  STEP B: recompute scan-date regime for {len(dates)} scan_date(s)")
    total = 0
    for d in dates:
        total += _update_scan_date_features(client, get_regime_context, _vix_cache_reset, d, dry)

    print("\n=== SUMMARY ===")
    print(f"  scan_dates processed : {len(dates)}")
    if dry:
        print("  DRY RUN — nothing written. Re-run with --confirm after review + owner OK.")
    else:
        print(f"  feature rows updated : {total}")
    print("\n  STEP C (DROP legacy VIX_at_entry / SPY_trend_state / vix_5d_delta_entry)")
    print("         is intentionally NOT performed here — it is destructive. Only after")
    print("         verifying STEP A migrated every row, run (with a SEPARATE explicit OK):")
    for _oc, (legacy, _t) in LEGACY_MAP.items():
        print(f"           ALTER TABLE `{TABLE}` DROP COLUMN IF EXISTS `{legacy}`;")


if __name__ == "__main__":
    main()
