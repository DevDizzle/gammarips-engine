-- Analytics-ready paper-trade fact. One row per terminal trade/skip record.
-- Derived flags are the single source of truth for "did this trade complete /
-- win / lose", gated on is_completed_trade so skip rows never pollute counts.
-- `option_return_pct` is an explicit alias for the OPTION premium return — the
-- canonical PnL for this project (underlying_return is kept for context only).
{{ config(materialized='table') }}

with ledger as (
    select * from {{ ref('stg_forward_paper_ledger') }}
)

select
    l.*,

    -- canonical PnL aliasing (option premium return, never the underlying)
    l.realized_return_pct as option_return_pct,

    -- completion / outcome flags
    (not coalesce(l.is_skipped, false) and l.realized_return_pct is not null)
        as is_completed_trade,
    (not coalesce(l.is_skipped, false) and l.realized_return_pct is not null
        and l.realized_return_pct > 0) as is_winner,
    (not coalesce(l.is_skipped, false) and l.realized_return_pct is not null
        and l.realized_return_pct < 0) as is_loser
from ledger l
