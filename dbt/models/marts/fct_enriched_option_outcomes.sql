-- Analytics-ready counterfactual option-PnL labels (the ~50x research label set).
-- option_return_pct is the canonical option PnL; regime attached by date range.
-- Selection flags (was_tournament_pick / was_topscore_pick) let you compare the
-- live pick against the full counterfactual pool.
{{ config(materialized='table') }}

with outcomes as (
    select * from {{ ref('stg_enriched_option_outcomes') }}
),

regime as (
    select * from {{ ref('dim_regime') }}
)

select
    o.*,
    o.realized_return_pct as option_return_pct,
    (o.realized_return_pct is not null) as is_labeled,
    (o.realized_return_pct is not null and o.realized_return_pct > 0) as is_winner,
    upper(o.direction) = 'BULLISH' as is_bullish,
    r.regime_name
from outcomes o
left join regime r
    on o.entry_day between r.start_date and r.end_date
