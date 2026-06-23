-- LLM cost / latency / error rollup by service x model_id (ROLLUP grand totals).
-- The dbt-side view of the spend the project otherwise watches via Cloud
-- Monitoring token_count.
{{ config(materialized='table') }}

with t as (
    select * from {{ ref('fct_llm_traces') }}
)

select
    service,
    model_id,

    count(*) as trace_count,
    countif(is_error) as error_count,
    safe_divide(countif(is_error), count(*)) as error_rate,

    sum(input_tokens) as total_input_tokens,
    sum(output_tokens) as total_output_tokens,
    sum(total_tokens) as total_tokens,

    sum(cost_usd) as total_cost_usd,
    safe_divide(sum(cost_usd), count(*)) as avg_cost_per_trace,

    avg(latency_ms) as avg_latency_ms,
    approx_quantiles(latency_ms, 100)[offset(95)] as p95_latency_ms
from t
group by rollup (service, model_id)
