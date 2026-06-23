-- Analytics-ready LLM-call fact. One row per trace, with derived token/error
-- columns. is_error keys off the error column (writer-vocabulary-agnostic).
{{ config(materialized='table') }}

with traces as (
    select * from {{ ref('stg_llm_traces') }}
)

select
    t.*,
    coalesce(t.input_tokens, 0) + coalesce(t.output_tokens, 0) as total_tokens,
    (t.error is not null) as is_error
from traces t
