"""One-shot backfill: populate mom_60 (+ anchor/lookback dates) on existing rows
from the underlying_daily_bars BQ cache — leakage-safe (substrate must-fix #5d).

    ################################################################################
    #  NOT YET EXECUTED.  This makes BigQuery WRITES (in-place UPDATE of research     #
    #  tables) and DEPENDS on the underlying_daily_bars cache being loaded first.     #
    #  It is gammarips-review + OWNER gated.  Do NOT run until both sign off AND       #
    #  create_underlying_daily_bars.py + load_underlying_daily_bars.py have run.       #
    ################################################################################

WHY (docs/DECISIONS/2026-07-01-momentum-persist-and-opportunity-surface.md):
Going forward, enrichment persists mom_60 point-in-time. This script backfills the
lever onto rows that predate that change, computed from BQ infra (NOT the stale
local parquet) so the flagship finding is reproducible over the full history.

LEAKAGE GUARD (the whole point): mom_60 for a (ticker, scan_date) is derived using
ONLY bar-cache sessions with date <= scan_date. The anchor is the last such
session; the lookback is the LB-th session before the anchor. Because every bar
used is <= scan_date, no post-scan (future) price can enter — a naive "60d return
as of this row" that pulls post-scan bars would leak; this cannot.

METHOD NOTE: sessions are taken from the bar cache's OWN dates (ROW_NUMBER over
date DESC), not a re-derived NYSE calendar — self-consistent and reproducible. For
a liquid name this equals the calendar sessions the live enrichment
_resolve_momentum_dates uses; a name MISSING bars on some sessions (halt/illiquid)
could differ by those gaps. Acceptable + documented; the live forward path uses the
calendar, this audit/backfill path uses the realized cache.

WHAT: for each target table with (ticker, scan_date), UPDATE mom_60 /
mom_anchor_date / mom_lookback_date / mom_lookback_days. Idempotent (recomputes
deterministic values). Only overwrites where a cache-derived value exists (a
missing lookback → row untouched, stays NULL).

TARGETS (default both):
    profitscout-fida8.profit_scout.enriched_option_outcomes
    profitscout-fida8.profit_scout.overnight_signals_enriched
Restrict with --table.

WRITES ONLY to those research tables. NEVER touches forward_paper_ledger or any
live surface.

USAGE (from repo root):
    # PREVIEW — reads only, writes NOTHING:
    python scripts/ledger_and_tracking/backfill_mom_60.py --dry-run
    # EXECUTE (only after review + owner OK + cache loaded):
    python scripts/ledger_and_tracking/backfill_mom_60.py --confirm
    # options: --lookback 60  --table enriched_option_outcomes

One-shot migration script (per .claude/rules/scripts-ledger.md): do NOT re-run
without explicit user approval.
"""

import argparse
import sys

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
BARS = f"{PROJECT_ID}.{DATASET_ID}.underlying_daily_bars"

# scan_date is a DATE in enriched_option_outcomes and a DATE (or DATETIME) in
# overnight_signals_enriched; DATE(scan_date) normalizes both.
DEFAULT_TABLES = ["enriched_option_outcomes", "overnight_signals_enriched"]
_MOM_COLS = {
    "mom_60": "FLOAT64",
    "mom_anchor_date": "DATE",
    "mom_lookback_date": "DATE",
    "mom_lookback_days": "INT64",
}


def _ensure_columns(client, table: str, dry: bool) -> None:
    present = {f.name for f in client.get_table(table).schema}
    missing = [c for c in _MOM_COLS if c not in present]
    if not missing:
        print(f"    columns: all mom columns already present on {table}")
        return
    adds = ", ".join(f"ADD COLUMN IF NOT EXISTS `{c}` {_MOM_COLS[c]}" for c in missing)
    ddl = f"ALTER TABLE `{table}` {adds}"
    if dry:
        print(f"    [dry-run] would run: {ddl}")
        return
    client.query(ddl).result()
    print(f"    columns: added {missing}")


def _mom_cte(table: str, lb: int) -> str:
    """CTE computing (ticker, scan_date) -> mom_60 + anchor/lookback from the cache.

    anchor  = latest cache session with date <= scan_date (rn = 1)
    lookback = the lb-th session before anchor (rn = lb + 1)
    """
    return f"""
    WITH keys AS (
      SELECT DISTINCT ticker, DATE(scan_date) AS scan_date
      FROM `{table}`
      WHERE ticker IS NOT NULL AND scan_date IS NOT NULL
    ),
    ranked AS (
      SELECT
        k.ticker, k.scan_date, b.date AS bar_date, b.close AS bar_close,
        ROW_NUMBER() OVER (
          PARTITION BY k.ticker, k.scan_date ORDER BY b.date DESC
        ) AS rn
      FROM keys k
      JOIN `{BARS}` b
        ON b.ticker = k.ticker AND b.date <= k.scan_date
    ),
    mom AS (
      SELECT
        a.ticker, a.scan_date,
        a.bar_date AS anchor_date, a.bar_close AS anchor_close,
        l.bar_date AS lookback_date, l.bar_close AS lookback_close,
        SAFE_DIVIDE(a.bar_close, l.bar_close) - 1 AS mom_60
      FROM ranked a
      JOIN ranked l
        ON l.ticker = a.ticker AND l.scan_date = a.scan_date AND l.rn = {lb} + 1
      WHERE a.rn = 1 AND l.bar_close > 0
    )
    """


def _preview(client, table: str, lb: int) -> None:
    sql = _mom_cte(table, lb) + """
    SELECT
      COUNT(*) AS derivable_keys,
      COUNTIF(mom_60 IS NOT NULL) AS with_mom,
      ROUND(AVG(mom_60), 4) AS avg_mom_60,
      ROUND(MIN(mom_60), 4) AS min_mom_60,
      ROUND(MAX(mom_60), 4) AS max_mom_60
    FROM mom
    """
    r = list(client.query(sql).result())[0]
    print(f"    [dry-run] derivable (ticker,scan_date) keys: {r['derivable_keys']} "
          f"(with mom_60: {r['with_mom']}); "
          f"avg={r['avg_mom_60']} min={r['min_mom_60']} max={r['max_mom_60']}")


def _update(client, table: str, lb: int) -> int:
    sql = _mom_cte(table, lb) + f"""
    UPDATE `{table}` T
    SET mom_60 = m.mom_60,
        mom_anchor_date = m.anchor_date,
        mom_lookback_date = m.lookback_date,
        mom_lookback_days = {lb}
    FROM mom m
    WHERE T.ticker = m.ticker AND DATE(T.scan_date) = m.scan_date
    """
    job = client.query(sql)
    job.result()
    return job.num_dml_affected_rows or 0


def main():
    ap = argparse.ArgumentParser(description="Backfill mom_60 from underlying_daily_bars (must-fix #5d)")
    ap.add_argument("--lookback", type=int, default=60,
                    help="MOM_LOOKBACK_DAYS trading sessions (default 60, matches enrichment)")
    ap.add_argument("--table", choices=DEFAULT_TABLES, default=None,
                    help="restrict to one target table (default: both)")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true", help="read only; write NOTHING")
    grp.add_argument("--confirm", action="store_true", help="EXECUTE the UPDATEs (review + owner OK)")
    args = ap.parse_args()
    dry = args.dry_run
    tables = [args.table] if args.table else DEFAULT_TABLES

    client = bigquery.Client(project=PROJECT_ID)

    # Guard: the bar cache must exist + be non-empty, else every mom would be NULL.
    try:
        n_bars = list(client.query(f"SELECT COUNT(*) AS n FROM `{BARS}`").result())[0]["n"]
    except Exception as e:  # noqa: BLE001
        print(f"FATAL: bar cache {BARS} not readable ({e}). Run create_/load_underlying_daily_bars.py first.")
        sys.exit(2)
    if n_bars == 0:
        print(f"FATAL: bar cache {BARS} is EMPTY. Run load_underlying_daily_bars.py first.")
        sys.exit(2)

    print(f"=== mom_60 backfill (lookback={args.lookback} sessions) ===")
    print(f"    bar cache rows: {n_bars}")
    print(f"    mode          : {'DRY-RUN (no writes)' if dry else 'EXECUTE (writing)'}\n")

    for t in tables:
        table = f"{PROJECT_ID}.{DATASET_ID}.{t}"
        print(f"  target: {table}")
        _ensure_columns(client, table, dry)
        if dry:
            _preview(client, table, args.lookback)
        else:
            n = _update(client, table, args.lookback)
            print(f"    rows updated: {n}")
        print()

    if dry:
        print("DRY RUN — nothing written. Re-run with --confirm after review + owner OK.")


if __name__ == "__main__":
    main()
