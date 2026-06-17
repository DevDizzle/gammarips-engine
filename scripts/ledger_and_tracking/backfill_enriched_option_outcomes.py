"""One-shot backfill for enriched_option_outcomes (HTTP driver).

Enumerates every enriched BULLISH scan_date in a window (read-only BigQuery) and
drives the DEPLOYED forward-paper-trader `/label_enriched_pool` endpoint once per
date. The labeling itself runs inside the Cloud Run container — which has the
runtime deps and the mounted POLYGON_API_KEY secret — so this script needs
neither locally. The endpoint replays the +80/-60/trail bracket on the full
enriched pool and writes one outcome row per candidate, idempotently per
scan_date (delete-then-load). Mechanics are byte-identical to the live trader
(same _simulate_contract).

This regenerates the frozen 1,375-trade study (realized_label.pkl, dead at
2026-05-29) on current data AND extends it through the V6 era — de-staling the
strategy's lever basis.

WRITES ONLY to profit_scout.enriched_option_outcomes (a research table), via the
endpoint, which targets the research table exclusively. NEVER touches
forward_paper_ledger or any live surface.

Run from the repo root AFTER the service is deployed:
    python scripts/ledger_and_tracking/backfill_enriched_option_outcomes.py
    # window override / preview:
    ... --start 2026-04-10 --end 2026-06-13
    ... --dry-run        # list dates, call nothing

Auth: uses `gcloud auth print-identity-token` (same pattern that works for the
other service endpoints). Dates whose 3-day hold window hasn't closed return a
SKIP from the endpoint guard and are reported, not written.

ONE-SHOT migration script (per .claude/rules/scripts-ledger.md): do NOT re-run
without explicit user approval.
"""

import argparse
import subprocess
from datetime import datetime, date

import requests
from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
SERVICE_URL = "https://forward-paper-trader-406581297632.us-central1.run.app"
ENDPOINT = "/label_enriched_pool"
DEFAULT_START = date(2026, 4, 10)  # earliest enriched coverage (locked scope)
BULLISH_ONLY = True                # mirrors ENRICHED_OUTCOMES_BULLISH_ONLY


def _id_token() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-identity-token"], text=True
    ).strip()


def _enriched_scan_dates(client, start: date, end: date) -> list[date]:
    bull = 'AND UPPER(direction) = "BULLISH"' if BULLISH_ONLY else ""
    sql = f"""
    SELECT DISTINCT DATE(scan_date) AS d
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) BETWEEN "{start}" AND "{end}"
      {bull}
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND recommended_dte IS NOT NULL
      AND recommended_volume IS NOT NULL
      AND recommended_oi IS NOT NULL
    ORDER BY d
    """
    return [r["d"] for r in client.query(sql).result()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=DEFAULT_START)
    ap.add_argument("--end", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
                    default=date.today())
    ap.add_argument("--dry-run", action="store_true",
                    help="list the scan_dates that would be labeled, call nothing")
    ap.add_argument("--service-url", default=SERVICE_URL)
    args = ap.parse_args()

    client = bigquery.Client(project=PROJECT_ID)
    dates = _enriched_scan_dates(client, args.start, args.end)
    print(f"Backfill window: {args.start} .. {args.end}  ({len(dates)} enriched scan_dates)")
    if args.dry_run:
        for d in dates:
            print(f"  would label: {d}")
        print("DRY RUN — nothing called.")
        return

    url = args.service_url.rstrip("/") + ENDPOINT

    tot_pool = tot_labeled = tot_wins = tot_losses = tot_errors = 0
    no_outcome = skipped = failed = 0
    for i, d in enumerate(dates, 1):
        # Re-mint the ID token per date: the run can exceed a token's ~60-min
        # lifetime (pre-2026-06-12 pools are ~170 contracts/date), so a token
        # minted once up front would expire mid-backfill and 401 later dates.
        headers = {"Authorization": f"Bearer {_id_token()}", "Content-Type": "application/json"}
        try:
            resp = requests.post(url, headers=headers,
                                 json={"target_date": d.isoformat()}, timeout=600)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"[{i}/{len(dates)}] {d}  REQUEST FAILED: {e}")
            continue
        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if resp.status_code != 200 or body.get("status") != "success":
            # The endpoint returns 500 + message for un-closed hold windows (a
            # legitimate skip) and other errors — report, don't abort.
            msg = body.get("message", resp.text[:200])
            skipped += 1
            print(f"[{i}/{len(dates)}] {d}  SKIP/ERR ({resp.status_code}): {msg}")
            continue
        tot_pool += body["pool_size"]; tot_labeled += body["labeled"]
        tot_wins += body["wins"]; tot_losses += body["losses"]; tot_errors += body["errors"]
        no_outcome += body["labeled"] - body["wins"] - body["losses"]
        print(f"[{i}/{len(dates)}] {d}  pool={body['pool_size']} labeled={body['labeled']} "
              f"wins={body['wins']} losses={body['losses']} errors={body['errors']}")

    print("\n=== BACKFILL SUMMARY ===")
    print(f"  scan_dates ok        : {len(dates) - skipped - failed} (skip {skipped}, fail {failed})")
    print(f"  candidates labeled   : {tot_labeled} / {tot_pool} pool rows")
    print(f"  wins / losses        : {tot_wins} / {tot_losses}")
    print(f"  no realized outcome  : {no_outcome} (no bars / INVALID_LIQUIDITY)")
    print(f"  sim errors (skipped) : {tot_errors}")
    fill = (tot_wins + tot_losses) / tot_labeled * 100 if tot_labeled else 0.0
    print(f"  fill-rate (had PnL)  : {fill:.1f}%")


if __name__ == "__main__":
    main()
