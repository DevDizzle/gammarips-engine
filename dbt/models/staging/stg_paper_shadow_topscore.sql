-- Lossless 1:1 projection of the top-score vs tournament shadow.
with source as (
    select * from {{ source('profit_scout', 'paper_shadow_topscore') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'arm']) }} as shadow_topscore_id,
    *
from source
