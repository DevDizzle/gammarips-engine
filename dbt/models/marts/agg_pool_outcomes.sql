-- Canonical full-pool counterfactual performance, on OPTION PnL, by
-- regime x direction (ROLLUP grand totals). This is the leakage-safe EV view of
-- "what the whole enriched pool would have returned" — the research counterpart
-- to agg_paper_performance (which is the 1-pick/day live ledger).
{{ config(materialized='table') }}

with o as (
    select * from {{ ref('fct_enriched_option_outcomes') }}
)

select
    regime_name,
    direction,

    count(*) as labeled_candidates,
    countif(is_winner) as winning_candidates,
    safe_divide(countif(is_winner), countif(is_labeled)) as win_rate,
    avg(if(is_labeled, option_return_pct, null)) as expectancy_pct,
    stddev(if(is_labeled, option_return_pct, null)) as return_stddev,

    -- how often the live selectors picked from this cell
    countif(was_tournament_pick) as tournament_picks,
    countif(was_topscore_pick) as topscore_picks
from o
group by rollup (regime_name, direction)
