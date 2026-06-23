-- Lossless projection of the counterfactual option-PnL label set, deduped to the
-- (scan_date, ticker, recommended_contract) grain. The source has ~145 dup rows
-- from label backfill re-runs; we keep the latest by labeled_at. Source date
-- columns are already DATE.
with source as (
    select * from {{ source('profit_scout', 'enriched_option_outcomes') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker', 'recommended_contract']) }} as outcome_id,
    *
from source
qualify row_number() over (
    partition by scan_date, ticker, recommended_contract order by labeled_at desc
) = 1
