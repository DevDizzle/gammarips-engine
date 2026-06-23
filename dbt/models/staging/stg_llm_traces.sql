-- Lossless 1:1 projection of LLM call traces. trace_id is the natural key
-- (no surrogate needed); scan_date is already DATE.
with source as (
    select * from {{ source('profit_scout', 'llm_traces_v1') }}
)

select * from source
