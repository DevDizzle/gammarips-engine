-- Analytics-ready enriched signal fact. One row per (scan_date, ticker).
-- Adds a couple of leakage-safe convenience dimensions used in edge research.
{{ config(materialized='table') }}

with enriched as (
    select * from {{ ref('stg_overnight_signals_enriched') }}
)

select
    e.*,
    upper(e.direction) = 'BULLISH' as is_bullish,
    abs(e.recommended_delta) as abs_delta
from enriched e
