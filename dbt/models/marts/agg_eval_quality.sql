-- Eval pass-rate / score rollup by service x evaluator (ROLLUP grand totals).
{{ config(materialized='table') }}

with e as (
    select * from {{ ref('fct_llm_eval_results') }}
)

select
    service,
    evaluator,

    count(*) as eval_count,
    countif(passed) as passed_count,
    -- pass rate over rows where `passed` is non-null (some evals are score-only)
    safe_divide(countif(passed), countif(passed is not null)) as eval_pass_rate,
    avg(score) as avg_score
from e
group by rollup (service, evaluator)
