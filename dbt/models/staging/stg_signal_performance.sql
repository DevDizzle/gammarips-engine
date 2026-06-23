-- Lossless projection of post-trade underlying-outcome tracking, deduped to the
-- (scan_date, ticker) grain. The source has ~315 dup pairs across writer eras; we
-- keep the latest by check_date (the table's only recency signal — an ISO date
-- string, so lexical desc = most-recent check). Underlying-based, NOT option PnL.
with source as (
    select * from {{ source('profit_scout', 'signal_performance') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker']) }} as signal_perf_id,
    cast(scan_date as date) as scan_date,
    * except (scan_date)
from source
qualify row_number() over (
    partition by scan_date, ticker order by check_date desc
) = 1
