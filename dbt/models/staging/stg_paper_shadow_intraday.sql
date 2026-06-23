-- Lossless 1:1 projection of the intraday-vs-3day-hold shadow (the 2x2).
with source as (
    select * from {{ source('profit_scout', 'paper_shadow_intraday') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'arm']) }} as shadow_intraday_id,
    *
from source
