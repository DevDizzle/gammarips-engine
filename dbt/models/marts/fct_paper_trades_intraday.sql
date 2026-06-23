-- Analytics-ready intraday mark-to-market fact (V7 GIGO). One row per open
-- position per trading day. unrealized_return_pct is the live OPTION PnL.
{{ config(materialized='table') }}

with snapshots as (
    select * from {{ ref('stg_forward_paper_ledger_intraday') }}
)

select
    s.*,
    s.unrealized_return_pct as option_unrealized_return_pct,
    (s.unrealized_return_pct is not null and s.unrealized_return_pct > 0)
        as is_unrealized_winner
from snapshots s
