"""One-shot remediation of the 2026-06-10 UPSTREAM row doubling (substrate #7e).

    ################################################################################
    #  NOT YET EXECUTED.  STEP 2 is a BigQuery WRITE (in-place dedup of the LIVE    #
    #  overnight_signals_enriched table) and STEP 3 re-labels the research table.   #
    #  Both are gammarips-review + OWNER gated.  Do NOT run until both sign off.     #
    #  Default mode is --dry-run (reads only, writes/calls NOTHING).                 #
    ################################################################################

WHY (substrate audit must-fix #7, adversarial correction):
The 145 duplicate rows observed on enriched_option_outcomes for the 2026-06-10
cohort are NOT a collector race — they are a faithful copy of an UPSTREAM
doubling. overnight_signals_enriched for scan_date 2026-06-10 is fully doubled
(658 rows == 329 tickers x 2). The counterfactual labeler (forward-paper-trader
/label_enriched_pool) reads that pool 1:1, so it dutifully wrote each contract
twice. Fixing only the research table would leave the source poisoned and any
re-label would re-double. The fix must be at the SOURCE, then re-label.

The atomic, schema-drift-safe write path (must-fix #1, now live in
enrichment-trigger.write_enriched_signals) prevents NEW doublings going forward;
this script cleans up the one pre-existing 06-10 hole.

WHAT THIS DOES:
  STEP 1 (read-only): report the current row/ticker counts for scan_date 06-10 on
          overnight_signals_enriched and confirm the doubling (rows == 2 x tickers).
  STEP 2 (WRITE, --confirm): dedup overnight_signals_enriched for scan_date 06-10 —
          keep exactly ONE row per ticker (latest enriched_at) — via the same
          stage -> verify -> single-transaction replace pattern the live writer
          uses (original rows survive any failure; no dup on success).
  STEP 3 (--confirm): re-label scan_date 06-10 so enriched_option_outcomes matches
          the deduped source. Because the per-scan_date lock (must-fix #7d) would
          otherwise skip a re-run, this first DELETES the Firestore claim doc
          label_pool_runs/2026-06-10, then POSTs to the DEPLOYED
          /label_enriched_pool endpoint (idempotent atomic replace per scan_date).

WRITES ONLY to:
  - profit_scout.overnight_signals_enriched  (STEP 2 dedup)
  - profit_scout.enriched_option_outcomes    (STEP 3 re-label, via the endpoint)
  - Firestore label_pool_runs/2026-06-10       (STEP 3 claim delete, escape hatch)
NEVER touches forward_paper_ledger, todays_pick, or any live-pick surface.

RUNTIME: run from the repo root. STEP 2 uses a local BigQuery client; STEP 3 uses
`gcloud auth print-identity-token` to call the deployed service (same pattern as
backfill_enriched_option_outcomes.py). The service must be deployed with the
must-fix #1/#3/#7 changes for STEP 3 to behave as documented.

USAGE:
    # PREVIEW (default) — reads + reports only, writes/calls NOTHING:
    python scripts/ledger_and_tracking/dedup_enriched_060_source.py --dry-run
    # EXECUTE (only after review + owner sign-off):
    python scripts/ledger_and_tracking/dedup_enriched_060_source.py --confirm

ONE-SHOT migration script (per .claude/rules/scripts-ledger.md): do NOT run
without explicit user approval.
"""

import argparse
import subprocess
import sys
import uuid
from datetime import date

import requests
from google.cloud import bigquery, firestore

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
ENRICHED_TABLE = f"{PROJECT_ID}.{DATASET_ID}.overnight_signals_enriched"
SCAN_DATE = "2026-06-10"  # the confirmed doubled scan_date

SERVICE_URL = "https://forward-paper-trader-406581297632.us-central1.run.app"
RELABEL_ENDPOINT = "/label_enriched_pool"


def _id_token() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-identity-token"], text=True
    ).strip()


def step1_report(client: bigquery.Client) -> tuple[int, int]:
    """Read-only: total rows + distinct tickers for SCAN_DATE. Returns (rows, tickers)."""
    sql = f"""
    SELECT COUNT(*) AS n_rows, COUNT(DISTINCT UPPER(ticker)) AS tickers
    FROM `{ENRICHED_TABLE}`
    WHERE scan_date = @scan_date
    """
    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("scan_date", "DATE", date.fromisoformat(SCAN_DATE)),
    ])
    r = list(client.query(sql, job_config=cfg).result())[0]
    rows, tickers = int(r["n_rows"]), int(r["tickers"])
    ratio = (rows / tickers) if tickers else 0.0
    print("=== STEP 1: source counts (read-only) ===")
    print(f"    {ENRICHED_TABLE}  scan_date={SCAN_DATE}")
    print(f"    rows                 : {rows}")
    print(f"    distinct tickers     : {tickers}")
    print(f"    rows / tickers       : {ratio:.2f}  (2.00 == fully doubled)")
    if rows == tickers:
        print("    -> already deduped (rows == tickers); STEP 2 is a no-op.")
    elif tickers and rows == 2 * tickers:
        print("    -> confirmed fully doubled; STEP 2 will halve to one row/ticker.")
    else:
        print("    -> UNEXPECTED shape; inspect manually before running STEP 2.")
    return rows, tickers


def step2_dedup(client: bigquery.Client, dry_run: bool) -> None:
    """Dedup SCAN_DATE to one row per ticker via stage -> verify -> tx-replace."""
    print("\n=== STEP 2: dedup overnight_signals_enriched (WRITE) ===")
    staging = f"{ENRICHED_TABLE}__dedup_{SCAN_DATE.replace('-', '')}_{uuid.uuid4().hex[:8]}"

    # Keep the latest enriched_at per ticker (dups are byte-identical copies, so
    # any deterministic pick is equivalent; latest is the least-surprising choice).
    stage_ddl = f"""
    CREATE TABLE `{staging}`
    OPTIONS(expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)) AS
    SELECT * EXCEPT(_rn) FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY UPPER(ticker)
            ORDER BY enriched_at DESC, recommended_contract
        ) AS _rn
        FROM `{ENRICHED_TABLE}`
        WHERE scan_date = '{SCAN_DATE}'
    )
    WHERE _rn = 1
    """
    if dry_run:
        print("  [dry-run] would stage deduped rows via:")
        print("    " + " ".join(stage_ddl.split()))
        print("  [dry-run] would then, in ONE transaction:")
        print(f"    DELETE FROM `{ENRICHED_TABLE}` WHERE scan_date = '{SCAN_DATE}';")
        print(f"    INSERT INTO `{ENRICHED_TABLE}` (<cols>) SELECT <cols> FROM <staging>;")
        print("  [dry-run] would then DROP the staging table. Nothing written.")
        return

    client.query(stage_ddl).result()
    try:
        staged = client.get_table(staging)
        n_staged = staged.num_rows
        n_tickers = int(list(client.query(
            f"SELECT COUNT(DISTINCT UPPER(ticker)) AS t FROM `{ENRICHED_TABLE}` "
            f"WHERE scan_date = '{SCAN_DATE}'"
        ).result())[0]["t"])
        if n_staged != n_tickers:
            raise RuntimeError(
                f"dedup staging mismatch: staged {n_staged} rows != {n_tickers} distinct "
                f"tickers for {SCAN_DATE}; aborting BEFORE touching the live table."
            )
        cols = ", ".join(f"`{f.name}`" for f in staged.schema)
        client.query(
            "BEGIN TRANSACTION;\n"
            f"DELETE FROM `{ENRICHED_TABLE}` WHERE scan_date = '{SCAN_DATE}';\n"
            f"INSERT INTO `{ENRICHED_TABLE}` ({cols}) SELECT {cols} FROM `{staging}`;\n"
            "COMMIT TRANSACTION;"
        ).result()
        print(f"  deduped {SCAN_DATE}: replaced with {n_staged} rows (one per ticker).")
    finally:
        try:
            client.query(f"DROP TABLE IF EXISTS `{staging}`").result()
        except Exception as e:  # noqa: BLE001 — cleanup must not mask the result
            print(f"  WARNING: staging cleanup failed for {staging} (non-fatal): {e}")


def step3_relabel(dry_run: bool) -> None:
    """Clear the per-scan_date lock, then re-label SCAN_DATE via the endpoint."""
    print("\n=== STEP 3: re-label enriched_option_outcomes for the deduped day ===")
    claim_path = f"label_pool_runs/{SCAN_DATE}"
    url = SERVICE_URL.rstrip("/") + RELABEL_ENDPOINT
    if dry_run:
        print(f"  [dry-run] would DELETE Firestore claim {claim_path} (unblock the lock).")
        print(f"  [dry-run] would POST {url}  body={{'target_date': '{SCAN_DATE}'}}")
        print("  [dry-run] nothing called.")
        return

    # The per-scan_date lock (must-fix #7d) would skip a re-run; clear it first.
    db = firestore.Client(project=PROJECT_ID)
    db.collection("label_pool_runs").document(SCAN_DATE).delete()
    print(f"  cleared claim {claim_path}")

    headers = {"Authorization": f"Bearer {_id_token()}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"target_date": SCAN_DATE}, timeout=600)
    body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
    print(f"  re-label response ({resp.status_code}): {body or resp.text[:300]}")
    if resp.status_code != 200:
        raise RuntimeError(f"re-label failed for {SCAN_DATE}: {resp.status_code} {resp.text[:300]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true", default=True,
                     help="read + report only; write/call NOTHING (default)")
    grp.add_argument("--confirm", action="store_true",
                     help="EXECUTE the dedup + re-label (review + owner sign-off required)")
    args = ap.parse_args()
    dry = not args.confirm

    print(f"remediation target: {ENRICHED_TABLE}  scan_date={SCAN_DATE}")
    print(f"mode: {'DRY-RUN (no writes/calls)' if dry else 'EXECUTE (writing + re-labeling)'}\n")

    client = bigquery.Client(project=PROJECT_ID)
    rows, tickers = step1_report(client)

    if tickers and rows == tickers and not dry:
        print("\nNothing to do: source is already deduped. Skipping STEP 2/3.")
        return 0

    step2_dedup(client, dry)
    step3_relabel(dry)

    print("\n=== DONE ===")
    if dry:
        print("DRY RUN — nothing written/called. Re-run with --confirm after review + owner OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
