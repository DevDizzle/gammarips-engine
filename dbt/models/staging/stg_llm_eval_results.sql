-- Lossless projection of LLM eval results, deduped to the eval_id grain. The
-- source has ~2233 dup eval_ids (the eval runner re-runs and appends without an
-- idempotency key — a writer bug to fix separately); we keep the latest by
-- created_at so eval pass-rate / cost rollups don't double-count.
with source as (
    select * from {{ source('profit_scout', 'llm_eval_results_v1') }}
)

select * from source
qualify row_number() over (
    partition by eval_id order by created_at desc
) = 1
