-- Lossless 1:1 projection of the raw overnight scan.
-- scan_date / recommended_expiration are already DATE in the source.
with source as (
    select * from {{ source('profit_scout', 'overnight_signals') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker']) }} as signal_id,
    *
from source
