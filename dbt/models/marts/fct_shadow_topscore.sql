-- Analytics-ready top-score vs tournament shadow. One row per arm per day.
{{ config(materialized='table') }}

select
    s.*,
    s.realized_return_pct as option_return_pct,
    (s.realized_return_pct is not null and s.realized_return_pct > 0) as is_winner
from {{ ref('stg_paper_shadow_topscore') }} s
