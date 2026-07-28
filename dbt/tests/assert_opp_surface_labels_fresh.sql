-- Alarm test: the opportunity-surface labeler ("gated backfill") has stalled.
--
-- The daily label cron writes opp_status=WINDOW_OPEN for a 3-trading-day window
-- that has not yet closed; a follow-up pass must fill it once the window closes
-- (worst case ~6 calendar days after scan_date: Fri scan -> window ends Wed,
-- +1-day lag by design; an in-window market holiday adds a day, and the 06:30 ET
-- dbt build runs before any same-day fill — hence the 10-day threshold, review
-- 2026-07-28). Any row older than 10 calendar days still carrying
-- WINDOW_OPEN (or NULL, the outage signature) means opp/3-day labels are no
-- longer being collected — the exact failure mode that silently ran
-- 2026-06-26 -> 2026-07-28 (950 rows dark; FINDINGS_LEDGER 2026-07-28).
--
-- Returning rows = test FAILURE -> dbt build exits non-zero -> dbt-daily-build
-- cron logs ERROR -> Cloud Monitoring scheduler-failure policy emails the
-- operator.

select
    scan_date,
    count(*) as stuck_rows
from {{ source('profit_scout', 'enriched_option_outcomes') }}
where
    scan_date <= date_sub(current_date('America/New_York'), interval 10 day)
    and (opp_status is null or opp_status = 'WINDOW_OPEN')
group by scan_date
