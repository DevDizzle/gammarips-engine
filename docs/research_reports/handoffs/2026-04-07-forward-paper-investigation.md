# Forward Paper Trader Issue Investigation

## Problem
The `forward-paper-trader` service (writing to `profitscout-fida8.profit_scout.forward_paper_ledger_v3`) stopped logging records after April 1, 2026. The Cloud Run logs indicated it was running daily but finding "0 eligible signals."

## Root Cause Analysis
The failure to log records is due to two distinct logic bugs in date calculation functions within `main.py`.

### 1. Default Target Date Bug (The Cron Failure)
The Cloud Scheduler triggers the service daily without passing a specific `target_date`. The service attempts to determine the scan date (which should be the previous trading day, since execution is evaluated on T+1).

**Flawed Logic:**
```python
# Old code attempting to find the previous trading day
target_date = get_trading_day_offset(datetime.now(est).date() - timedelta(days=7), 5)
```
**Why it failed:** `get_trading_day_offset`'s math is flawed. When tested on Monday, April 6th, `get_trading_day_offset(base - 7_days, 5)` returned `2026-04-06` (the current day) instead of the previous trading day (Thursday, April 2nd). Because the overnight scanner generates signals for the previous day, querying BigQuery for signals on the *current* day correctly returns 0 results.

### 2. Entry Day Offset Bug (The Execution Failure)
When the service successfully finds a signal (e.g., when manually passing a `target_date` of `2026-04-06`), it attempts to calculate the execution day.

**Flawed Logic:**
```python
# Old code attempting to find the execution day (T+1)
entry_day = get_trading_day_offset(target_date, 1)
```
**Why it failed:** Calling `get_trading_day_offset(date, 1)` returns the *same day* if the provided date is a valid trading day, not the next trading day. The trader was attempting to simulate execution on the same day the signal was generated (T+0), which violates the strategy's T+1 execution rule.

## Implemented Fixes (Local Workspace)

**1. Replaced Default Target Date Logic:**
Added a robust `get_previous_trading_day()` function.
```python
def get_previous_trading_day(base_date: date) -> date:
    start_date = base_date - timedelta(days=10)
    schedule = nyse.schedule(start_date=start_date, end_date=base_date)
    valid_dates = [d.date() for d in schedule.index if d.date() < base_date]
    return valid_dates[-1] if valid_dates else None

# Updated default logic
target_date = get_previous_trading_day(datetime.now(est).date())
```

**2. Fixed Entry Day Calculation:**
Swapped the broken offset function for the existing, correct `get_next_trading_day()` function.
```python
# Updated entry day logic
entry_day = get_next_trading_day(target_date) # target_date + 1 trading day
```

## Side Effects
During manual testing of the endpoint with `target_date="2026-04-06"`, two corrupted records were inserted into BigQuery. An attempt to delete them via `DELETE FROM` failed because the rows are still in BigQuery's streaming buffer.

## Next Steps
1. Deploy the corrected `main.py` to the `forward-paper-trader` Cloud Run service in `profitscout-fida8`.
2. Write a backfill script to process the missing days (April 2nd, 3rd, and 6th) to ensure the ledger is complete and accurate.