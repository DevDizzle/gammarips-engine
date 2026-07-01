"""One-shot backfill: fill the OPPORTUNITY-SURFACE (MFE/MAE) + 3-DAY-LABEL columns
on existing enriched_option_outcomes rows for CLOSED windows (substrate must-fix #6).

    ################################################################################
    #  NOT YET EXECUTED.  This calls Polygon (per-contract option bars) and makes     #
    #  BigQuery WRITES (MERGE into a research table).  It is gammarips-review +        #
    #  OWNER gated.  Do NOT run until both sign off AND the must-fix #6 collector      #
    #  (forward-paper-trader main.py) is DEPLOYED (schema/semantics must match).       #
    ################################################################################

WHY (docs/DECISIONS/2026-07-01-momentum-persist-and-opportunity-surface.md):
The daily collector writes the opportunity-surface + 3-day-label columns only once
the multi-day HOLD WINDOW HAS CLOSED. A fresh scan_date labeled by the daily cron
still has an OPEN window, so those columns are written NULL (opp_status=WINDOW_OPEN)
and the per-scan_date claim/lock prevents a same-day re-run. This script fills them
in for every historical row whose window has since closed — the MFE/MAE profit-
potential surface + the interim -60/+80/HOLD=3 label the flagship finding lives on.

BYTE-IDENTICAL by construction: it IMPORTS the deployed collector functions
(_simulate_opportunity_surface, _simulate_contract with the 3-day overrides,
_multi_day_window_closed) rather than re-implementing the bar walk — same source of
truth as the live daily pass. Reuses the regime_scan_date backfill's import pattern.

LEAKAGE-SAFE: only bars within the (closed) hold window are read; the entry cost
basis mirrors the live 10:00 fill; the surface applies NO exit rule so exit stays a
free variable. Never touches forward_paper_ledger or any live surface.

IDEMPOTENT: computes into a staging table, then MERGEs on
(scan_date, ticker, recommended_contract). Re-running recomputes deterministic
values. By default only rows still needing a fill are processed
(opp_status IS NULL/WINDOW_OPEN OR realized_return_pct_3d IS NULL) whose window has
closed; --force recomputes all closed-window rows.

SCHEMA-SAFE (BLOCKER B, 2026-07-01): _merge ALTER-adds the opp/3d target columns
(reusing forward-paper-trader's shared ENRICHED_OUTCOMES_RESEARCH_COLUMNS /
_ensure_enriched_outcomes_columns) BEFORE the MERGE, so a first --confirm run on a
table that predates the columns no longer 500s with "Unrecognized name".

WINDOW GUARD: only windows that ended on a PRIOR trading day are filled
(_multi_day_window_closed uses strict `< today_et`), so an intraday run can never
read a partial final session. A window ending today is left for the next run.

SOFT-SKIP (not a hole): rows whose recommended_dte/volume/oi is NULL get NO 3-day
label (the reused _simulate_contract int()-casts those and the caller swallows the
TypeError) but STILL get an opportunity surface (which needs none of them). Fewer
3-day labels is expected attrition, not missing data.

RUNTIME: must run in the forward-paper-trader runtime so the imported bar-walk +
constants are byte-identical to the deployed collector:
    pip install -r forward-paper-trader/requirements.txt
    export POLYGON_API_KEY=$(gcloud secrets versions access latest \
        --secret=POLYGON_API_KEY --project=profitscout-fida8)

USAGE (from repo root):
    # PREVIEW — computes NOTHING against Polygon, just reports what WOULD run:
    python scripts/ledger_and_tracking/backfill_opportunity_surface.py --dry-run
    # EXECUTE (only after review + owner OK + collector deployed):
    python scripts/ledger_and_tracking/backfill_opportunity_surface.py --confirm \
        --start 2026-04-10 --end 2026-06-30
    # options: --limit N (test), --force (recompute all closed rows)

One-shot migration script (per .claude/rules/scripts-ledger.md): do NOT re-run
without explicit user approval.
"""

import argparse
import io
import json
import os
import sys
import uuid
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

# Columns this backfill writes (must match the collector's out-dict groups).
_OPP_COLS = [
    "opp_window_days", "opp_status", "opp_entry_timestamp", "opp_entry_price",
    "opp_peak_return", "opp_trough_return", "opp_minutes_to_peak",
    "opp_minutes_to_trough", "opp_bar_count", "opp_sim_version",
]
_D3_COLS = [
    "realized_return_pct_3d", "exit_reason_3d", "exit_day_3d",
    "exit_timestamp_3d", "entry_price_3d", "peak_premium_3d",
    "label_3d_sim_version", "label_3d_hold_days", "label_3d_stop_pct",
    "label_3d_target_pct",
]


def _rows_to_process(client, start: date, end: date, force: bool, limit: int | None):
    fill_filter = "" if force else (
        "AND (opp_status IS NULL OR opp_status = 'WINDOW_OPEN' "
        "OR realized_return_pct_3d IS NULL)"
    )
    lim = f"LIMIT {int(limit)}" if limit else ""
    sql = f"""
    SELECT
      scan_date, entry_day, ticker, direction, recommended_contract,
      recommended_strike, recommended_expiration, recommended_dte,
      recommended_volume, recommended_oi, recommended_spread_pct,
      is_premium_signal, premium_score
    FROM `{TABLE}`
    WHERE scan_date BETWEEN @start AND @end
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      {fill_filter}
    ORDER BY scan_date, ticker
    {lim}
    """
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("start", "DATE", start),
        bigquery.ScalarQueryParameter("end", "DATE", end),
    ])
    return [dict(r) for r in client.query(sql, job_config=cfg).result()]


def _compute(mod, client, row: dict, today_et: date) -> dict | None:
    """Compute the opp-surface + 3-day arm for one row; None if window still open."""
    entry_day = row["entry_day"] or mod.get_next_trading_day(row["scan_date"])
    if not mod._multi_day_window_closed(entry_day, mod.OPP_WINDOW_DAYS, today_et):
        return None  # window not closed yet — leave for a later run

    out = {
        "scan_date": row["scan_date"],
        # Use the ticker EXACTLY as stored (do NOT .upper()): the collector writes
        # ticker un-uppercased (forward-paper-trader _write_enriched_outcomes:
        # `"ticker": rec["ticker"]` = the raw overnight_signals_enriched value), and
        # `row["ticker"]` here is read back from that same enriched_option_outcomes
        # row. The MERGE key `T.ticker = S.ticker` is CASE-SENSITIVE, so uppercasing
        # would silently miss any non-uppercase stored ticker and update nothing.
        "ticker": row["ticker"],
        "recommended_contract": row["recommended_contract"],
    }

    opp = mod._simulate_opportunity_surface(row, entry_day, mod.OPP_WINDOW_DAYS)
    out.update({k: opp.get(k) for k in _OPP_COLS if k != "opp_sim_version"})
    out["opp_sim_version"] = mod.OPP_SIM_VERSION

    exit_day_3d = mod.get_nth_next_trading_day(entry_day, mod.LABEL_3D_HOLD_DAYS - 1)
    d3_closed = mod._multi_day_window_closed(entry_day, mod.LABEL_3D_HOLD_DAYS, today_et)
    if d3_closed:
        # SOFT-SKIP on null dte/vol/oi: the 3-day arm reuses _simulate_contract,
        # which int()-casts recommended_dte/volume/oi and RAISES on NULL. That
        # TypeError is caught just below (rec3={}), so such a row simply gets NO
        # 3-day label while its opportunity surface (which needs none of those
        # fields) still fills. Fewer rows carry a 3-day label — this is expected
        # attrition, NOT a data hole. (In practice the daily collector already
        # filters dte/vol/oi NOT NULL, so these should be rare.)
        try:
            rec3 = mod._simulate_contract(
                client, row, entry_day, exit_day_3d,
                None, None, None, pick_doc=None,
                hold_days=mod.LABEL_3D_HOLD_DAYS, stop_pct=mod.LABEL_3D_STOP_PCT,
                target_pct=mod.LABEL_3D_TARGET_PCT, exit_hhmm=mod.LABEL_3D_EXIT_HHMM,
                use_trail=False, fetch_benchmarks=False,
            )
        except Exception as e:  # noqa: BLE001
            print(f"    3-day sim failed for {out['ticker']} {row['scan_date']}: {e}")
            rec3 = {}
        out.update({
            "realized_return_pct_3d": rec3.get("realized_return_pct"),
            "exit_reason_3d": rec3.get("exit_reason"),
            "exit_day_3d": exit_day_3d,
            "exit_timestamp_3d": rec3.get("exit_timestamp"),
            "entry_price_3d": rec3.get("entry_price"),
            "peak_premium_3d": rec3.get("peak_premium"),
            "label_3d_sim_version": mod.LABEL_3D_SIM_VERSION,
            "label_3d_hold_days": int(mod.LABEL_3D_HOLD_DAYS),
            "label_3d_stop_pct": float(mod.LABEL_3D_STOP_PCT),
            "label_3d_target_pct": float(mod.LABEL_3D_TARGET_PCT),
        })
    return out


def _merge(client, computed: list[dict], mod) -> int:
    """Load computed rows into staging, then MERGE on the 3 identity keys."""
    if not computed:
        return 0
    # BLOCKER B (2026-07-01): guarantee the opp + 3d target columns EXIST with
    # explicit types BEFORE the MERGE (and before CREATE TABLE ... LIKE clones the
    # target into staging). The MERGE's `SET T.<col> = S.<col>` references these
    # columns on the target; without this ALTER the first --confirm run 500s with
    # "Unrecognized name" on a table that predates them. Reuses the SAME shared
    # column->type list/helper as the daily collector (BLOCKER A) so both write
    # paths agree on names/types. Idempotent — a no-op once the columns exist.
    mod._ensure_enriched_outcomes_columns(client, TABLE)
    staging = f"{PROJECT_ID}.{DATASET_ID}._stg_opp_backfill_{uuid.uuid4().hex[:8]}"
    client.query(
        f"CREATE TABLE `{staging}` LIKE `{TABLE}` "
        f"OPTIONS(expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 1 DAY))"
    ).result()
    try:
        jsonl = "\n".join(json.dumps(r, default=str) for r in computed)
        client.load_table_from_file(
            io.BytesIO(jsonl.encode("utf-8")), staging,
            job_config=bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
                autodetect=True,
            ),
        ).result()
        set_cols = _OPP_COLS + _D3_COLS
        set_clause = ", ".join(f"`{c}` = S.`{c}`" for c in set_cols)
        merge_sql = f"""
        MERGE `{TABLE}` T
        USING `{staging}` S
          ON T.scan_date = S.scan_date
         AND T.ticker = S.ticker
         AND T.recommended_contract = S.recommended_contract
        WHEN MATCHED THEN UPDATE SET {set_clause}
        """
        job = client.query(merge_sql)
        job.result()
        return job.num_dml_affected_rows or 0
    finally:
        try:
            client.query(f"DROP TABLE IF EXISTS `{staging}`").result()
        except Exception as e:  # noqa: BLE001
            print(f"    staging cleanup failed for {staging} (non-fatal): {e}")


def main():
    ap = argparse.ArgumentParser(description="Backfill opportunity-surface + 3-day label (must-fix #6)")
    ap.add_argument("--start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date(2026, 4, 10))
    ap.add_argument("--end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date.today())
    ap.add_argument("--limit", type=int, default=None, help="cap rows (for a test run)")
    ap.add_argument("--force", action="store_true", help="recompute ALL closed-window rows")
    ap.add_argument("--batch", type=int, default=200, help="MERGE batch size")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--dry-run", action="store_true", help="report only; no Polygon, no writes")
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
    rows = _rows_to_process(client, args.start, args.end, args.force, args.limit)
    print(f"=== opportunity-surface + 3-day backfill ===")
    print(f"    mode  : {'DRY-RUN (no writes)' if args.dry_run else 'EXECUTE (writing)'}")
    print(f"    window: {args.start} .. {args.end}")
    print(f"    rows candidate for fill: {len(rows)}\n")

    if args.dry_run:
        # Only assess how many windows are CLOSED (no Polygon calls).
        closable = sum(
            1 for r in rows
            if fpt._multi_day_window_closed(
                r["entry_day"] or fpt.get_next_trading_day(r["scan_date"]),
                fpt.OPP_WINDOW_DAYS, today_et)
        )
        print(f"  [dry-run] {closable}/{len(rows)} rows have a CLOSED opp window and would be "
              f"recomputed (Polygon + MERGE). Re-run with --confirm after review + owner OK.")
        return

    computed, total = [], 0
    for i, r in enumerate(rows):
        c = _compute(fpt, client, r, today_et)
        if c is not None:
            computed.append(c)
        if len(computed) >= args.batch:
            total += _merge(client, computed, fpt)
            print(f"  ... merged batch through row {i+1}/{len(rows)} (cum updated={total})")
            computed = []
    total += _merge(client, computed, fpt)

    print("\n=== SUMMARY ===")
    print(f"  candidate rows : {len(rows)}")
    print(f"  rows updated   : {total}")


if __name__ == "__main__":
    main()
