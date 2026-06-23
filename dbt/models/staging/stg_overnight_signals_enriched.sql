-- Lossless projection of the enriched signal pool, deduped to the (scan_date,
-- ticker) grain. The source has ≈329 dup pairs (re-enrichment runs), so we keep
-- the latest row per ticker per day by enriched_at. Adds a surrogate signal_id
-- and normalizes date columns to DATE.
with source as (
    select * from {{ source('profit_scout', 'overnight_signals_enriched') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker']) }} as signal_id,
    cast(scan_date as date) as scan_date,
    safe_cast(recommended_expiration as date) as recommended_expiration,
    * except (scan_date, recommended_expiration)
from source
qualify row_number() over (
    partition by scan_date, ticker order by enriched_at desc
) = 1
