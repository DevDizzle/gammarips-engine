-- Canonical performance rollup. THE single definition of win_rate / expectancy /
-- profit factor for the project, computed on OPTION PnL (option_return_pct), not
-- the underlying. Sliced by policy_version x direction with ROLLUP grand totals
-- (the (null, null) row is the overall figure). Consumers read this instead of
-- re-deriving metrics in each script.
{{ config(materialized='table') }}

with trades as (
    select * from {{ ref('fct_paper_trades') }}
)

select
    policy_version,
    direction,

    count(*) as total_records,
    countif(is_skipped) as skip_records,
    countif(is_completed_trade) as completed_trades,
    countif(is_winner) as winning_trades,
    countif(is_loser) as losing_trades,

    -- win rate over completed trades only
    safe_divide(countif(is_winner), countif(is_completed_trade)) as win_rate,

    -- expectancy = mean OPTION return per completed trade
    avg(if(is_completed_trade, option_return_pct, null)) as expectancy_pct,
    -- dispersion + tails for the same population
    stddev(if(is_completed_trade, option_return_pct, null)) as return_stddev,
    min(if(is_completed_trade, option_return_pct, null)) as worst_return_pct,
    max(if(is_completed_trade, option_return_pct, null)) as best_return_pct,

    -- profit factor = gross wins / gross losses (abs)
    safe_divide(
        sum(if(is_winner, option_return_pct, 0)),
        abs(sum(if(is_loser, option_return_pct, 0)))
    ) as profit_factor
from trades
group by rollup (policy_version, direction)
