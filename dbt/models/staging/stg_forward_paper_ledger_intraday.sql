-- Lossless 1:1 projection of the V7 intraday mark-to-market snapshots.
-- Adds a surrogate snapshot id and normalizes the date columns to DATE.
with source as (
    select * from {{ source('profit_scout', 'forward_paper_ledger_intraday') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['scan_date', 'snapshot_date', 'ticker']) }} as intraday_snapshot_id,
    cast(scan_date as date) as scan_date,
    safe_cast(entry_day as date) as entry_day,
    safe_cast(exit_day as date) as exit_day,
    cast(snapshot_date as date) as snapshot_date,
    * except (scan_date, entry_day, exit_day, snapshot_date)
from source
