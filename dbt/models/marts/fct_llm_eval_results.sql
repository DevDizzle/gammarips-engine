-- Analytics-ready eval-result fact. One row per (trace, evaluator).
{{ config(materialized='table') }}

with results as (
    select * from {{ ref('stg_llm_eval_results') }}
)

select
    r.*,
    coalesce(r.passed, false) as is_passed
from results r
