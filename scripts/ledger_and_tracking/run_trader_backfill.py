"""Replay the V3.1 forward paper trader over a date range.

The trader's HTTP API is locked: 2-day hold, V3.1 quality gate, writes to
forward_paper_ledger_v3_hold2. The only thing this script controls is which
target_date(s) to replay. The trader is idempotent — re-running the same
scan_date is safe.
"""

import argparse
import datetime
import time

import requests

DEFAULT_URL = "https://forward-paper-trader-406581297632.us-central1.run.app/"


def parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def main():
    parser = argparse.ArgumentParser(description="Replay the V3.1 forward paper trader over a date range.")
    parser.add_argument("--start", type=parse_date, required=True, help="First scan_date to replay (YYYY-MM-DD)")
    parser.add_argument("--end", type=parse_date, required=True, help="Last scan_date to replay (YYYY-MM-DD)")
    parser.add_argument("--url", default=DEFAULT_URL, help="forward-paper-trader Cloud Run URL")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to pause between requests")
    args = parser.parse_args()

    print(f"Backfilling from {args.start} to {args.end}")

    # Iterate every calendar date in the window. Do NOT skip weekends:
    # the overnight scanner sometimes stamps scan_date on a Saturday calendar date
    # (e.g. 2026-02-21), and the trader itself returns "No eligible signals found"
    # cheaply for true non-trading days, so it's safer to call for everything.
    current_date = args.start
    while current_date <= args.end:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Triggering paper trader for scan_date: {date_str}")

        try:
            resp = requests.post(
                args.url,
                json={"target_date": date_str},
                headers={"Content-Type": "application/json"},
                timeout=600,
            )
            if resp.status_code == 200:
                print(f"  Success: {resp.json().get('message')}")
            else:
                print(f"  Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"  Error triggering {date_str}: {e}")

        time.sleep(args.sleep)
        current_date += datetime.timedelta(days=1)


if __name__ == "__main__":
    main()
