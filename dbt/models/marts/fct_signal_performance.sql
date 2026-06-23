-- Analytics-ready post-trade underlying-outcome tracking. Underlying-based (NOT
-- option PnL) — for context only. Passthrough due to historical column drift;
-- only the stable grain + is_win are relied on downstream.
{{ config(materialized='table') }}

select *
from {{ ref('stg_signal_performance') }}
