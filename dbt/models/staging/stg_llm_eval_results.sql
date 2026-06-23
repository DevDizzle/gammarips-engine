-- Lossless 1:1 projection of LLM eval results. eval_id is the natural key.
with source as (
    select * from {{ source('profit_scout', 'llm_eval_results_v1') }}
)

select * from source
