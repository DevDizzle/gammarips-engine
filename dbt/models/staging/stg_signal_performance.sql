-- Lossless 1:1 projection of post-trade underlying-outcome tracking.
-- The live table has historical column drift across writer eras, so this is a
-- deliberate `select *` (plus a normalized scan_date + surrogate key) — the mart
-- references only the stable grain columns.
with source as (
    select * from {{ source('profit_scout', 'signal_performance') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker']) }} as signal_perf_id,
    cast(scan_date as date) as scan_date,
    * except (scan_date)
from source
