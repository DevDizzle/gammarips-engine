-- Daily time spine required by the dbt Semantic Layer (MetricFlow) for
-- time-based metric aggregation.
{{ config(materialized='table') }}

with days as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2026-01-01' as date)",
        end_date="cast('2027-01-01' as date)"
    ) }}
)

select cast(date_day as date) as date_day
from days
