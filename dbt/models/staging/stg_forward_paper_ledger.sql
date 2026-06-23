-- Lossless 1:1 projection of the terminal paper-trade ledger.
-- Adds a stable surrogate trade_id and normalizes scan_date to DATE.
with source as (
    select * from {{ source('profit_scout', 'forward_paper_ledger') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker', 'recommended_contract']) }} as trade_id,
    cast(scan_date as date) as scan_date,
    * except (scan_date)
from source
