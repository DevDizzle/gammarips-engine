-- Market-regime dimension (seed-backed). Joined into facts by date range.
{{ config(materialized='table') }}

select
    regime_name,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date,
    description
from {{ ref('regimes') }}
