-- Lossless projection of the raw overnight scan, deduped to the (scan_date,
-- ticker) grain. The source appends re-scans (≈1940 dup pairs), so we keep the
-- latest row per ticker per day by scan_timestamp. scan_date / recommended_
-- expiration are already DATE in the source.
with source as (
    select * from {{ source('profit_scout', 'overnight_signals') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker']) }} as signal_id,
    *
from source
qualify row_number() over (
    partition by scan_date, ticker order by scan_timestamp desc
) = 1
