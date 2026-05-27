# 2026-05-15 — Trader resurrection + EOD mark-to-market

## Status
SHIPPED. Revision `forward-paper-trader-00035-72h`. First V5.4 ledger row written same day (OKTA, scan_date 2026-05-12, realized −1.96% TIMEOUT).

## What was broken

V5.4 was promoted 2026-05-08 with `forward_paper_ledger` truncated to start fresh. Four trading days later (2026-05-15) the ledger was still empty. Three latent bugs compounded:

1. **Missing dependency.** The 2026-05-12 pipeline-alignment commit (c82fba2) added `firestore.Client()` to `forward-paper-trader/main.py:286` (reading `todays_pick/{scan_date}`) but never added `google-cloud-firestore` to `requirements.txt`. `bigquery` no longer transitively exposes the firestore submodule, so every gunicorn boot died at `ImportError: cannot import name 'firestore'`. The trader 503'd on every cron from 2026-05-12 21:06 UTC through 2026-05-15 13:00 UTC.

2. **REQUIRED columns rejected legitimate skip rows.** `_build_skip_record` writes `ticker=None`, `recommended_contract=None`, `direction=None` for the MISSING / NO_PICK / FETCH_FAILED skip paths. Those three columns were `STRING REQUIRED` in the ledger schema, so the BQ JSON load failed before the row could be written. Any V5.4 no-pick day would have crashed.

3. **`get_canonical_scan_date` walkback was off by one.** Logic walked back `HOLD_DAYS + 1 = 4` trading days from today, predicated on the V5.3-era assumption that the cron fired before market close. The V5.4 cron runs at 16:30 ET (post-close), so the 15:50 ET TIMEOUT bar on `exit_day = today` is already final. The +1 buffer made the trader always one day behind; paired with the in-progress-window guard at `main.py:377` using `>=` (inclusive of today), the trader would have refused to simulate even with the math corrected.

## What changed

### Code

`forward-paper-trader/main.py`:
- New module constant `INTRADAY_TABLE`.
- New helper `get_nth_previous_trading_day(base_date, n)`.
- `get_canonical_scan_date` walkback `range(HOLD_DAYS + 1)` → `range(HOLD_DAYS)`; docstring rewritten.
- In-progress-window guard `>=` → `>` (strict future); comment + log message updated.
- New function `run_mark_to_market()` + Flask route `POST /mark_to_market`. Discovers open V5.4 positions by iterating the last `HOLD_DAYS` entry_day candidates and reading each `todays_pick/{scan_date}` doc. For each open position: fetches Polygon minute bars from `entry_day → today`, derives `entry_price` with the same `× 1.02` slippage the trader uses, computes peak high + current EOD mid + unrealized return + trail-armed status, writes one row to `forward_paper_ledger_intraday`. Read-only against the canonical ledger.

`forward-paper-trader/requirements.txt`:
- Added `google-cloud-firestore==2.19.0`.

### BigQuery

- `ALTER COLUMN ticker / recommended_contract / direction DROP NOT NULL` on `profitscout-fida8.profit_scout.forward_paper_ledger`. Skip rows are now schema-legal.
- Created `profitscout-fida8.profit_scout.forward_paper_ledger_intraday` (partitioned by `snapshot_date`). One row per open V5.4 position per snapshot.

### Cloud Scheduler

- New job `forward-paper-trader-mtm` at `15 16 * * 1-5 America/New_York`, POST to `/mark_to_market`. Fires ~15 min before the existing `forward-paper-trader-trigger` exit cron.

## Why

- **Restore the ledger.** Without these fixes the trader silently never wrote a row, and the public webapp `cohort_stats/current` panel stayed at 0/0/0/$0 indefinitely despite the picker working.
- **Daily-state observability.** The trader is batch — it writes a single ledger row at end-of-hold-window. Between entry day and exit day there was no record that an "open position" existed. Daily MTM gives the webapp's live panel a story to tell ("Day 2 of 3 · +12%") without changing the trader's exit logic.
- **Cron-time consistency.** The V5.4 cron at 16:30 ET post-close means today's 15:50 ET TIMEOUT bar is final. Walking back HOLD_DAYS (not HOLD_DAYS+1) and using a strict `>` guard makes the trader simulate the trade whose exit_day == today, instead of always being one day behind.

## How to apply

- Trader cron at 16:30 ET Mon–Fri closes the trade whose `exit_day = today` (writes one realized row to `forward_paper_ledger`).
- MTM cron at 16:15 ET Mon–Fri snapshots all currently-open positions (writes up to `HOLD_DAYS` rows to `forward_paper_ledger_intraday`).
- Both crons are idempotent (delete-then-load on their own date key). Safe to re-fire.
- Webapp's live-stats panel still reads `cohort_stats/current` (rewritten by `signal-notifier` at 7:30 AM ET Mon–Fri). Webapp's future "Live positions" panel reads `forward_paper_ledger_intraday WHERE snapshot_date = (SELECT MAX(...))` left-joined to the ledger.

## Not changed

- V5.4 execution policy: entry 10:00 ET day-1, stop −60%, target +80%, trail at +30% gain / 25% off peak, hold 3 trading days, exit 15:50 ET day-3. Unchanged.
- No new execution gates on the trader. Gates remain in `enrichment-trigger` + `signal-notifier`.
- No new vendors. No FMP creep. No new secret mounts.
- `signal_ranker_runs`, `signal_performance`, `cohort_stats/current` schemas unchanged.

## Audit trail
- `gammarips-review` round 1: BLOCK on line 377 guard `>=` (would have prevented simulation even with new walkback).
- `gammarips-review` round 2: APPROVE after `>` fix + entry-bar fallback parity fix.

## Validation
- Post-deploy smoke test: `POST /` returned 200, ledger gained one row (OKTA, −1.96%, TIMEOUT). `POST /mark_to_market` returned 200 with `rows_written=1` (the same OKTA position before its 16:30 ET realized close).
- `cohort_stats/current` Firestore doc force-refreshed: `trades_closed=1, roi_pct=-1.96%, total_invested_usd=467.16`.
- Two more V5.4 picks (KBR scan_date=2026-05-13, HTZ scan_date=2026-05-14) are open and will close on the natural cron cadence (Mon 5/18 and Tue 5/19 16:30 ET respectively). No backfill needed.

Related: [`2026-05-12-v5-4-pipeline-alignment.md`](2026-05-12-v5-4-pipeline-alignment.md), [`2026-05-08-v5-3-retired-v5-4-promoted.md`](2026-05-08-v5-3-retired-v5-4-promoted.md), [`2026-05-09-DEFERRED-alpaca-agent-execution.md`](2026-05-09-DEFERRED-alpaca-agent-execution.md).
