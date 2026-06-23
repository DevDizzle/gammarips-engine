-- Lossless 1:1 projection of the counterfactual option-PnL label set.
-- Date columns are already DATE in the source DDL; just add a surrogate key.
with source as (
    select * from {{ source('profit_scout', 'enriched_option_outcomes') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker', 'recommended_contract']) }} as outcome_id,
    *
from source
