-- Analytics-ready intraday-vs-3day-hold shadow. One row per arm per day; carries
-- BOTH the intraday and the 3-day-hold return so the exit-design delta is a column.
{{ config(materialized='table') }}

select
    s.*,
    (s.intraday_return_pct is not null and s.intraday_return_pct > 0) as is_intraday_winner,
    (s.hold_3day_return_pct is not null and s.hold_3day_return_pct > 0) as is_hold_winner,
    s.intraday_return_pct - s.hold_3day_return_pct as intraday_minus_hold_pct
from {{ ref('stg_paper_shadow_intraday') }} s
