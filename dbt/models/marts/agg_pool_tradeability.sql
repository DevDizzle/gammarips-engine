-- Standing pool-tradeability metric (trader doc R5 + the 2026-07-28 entry-day
-- tradeability study, FINDINGS_LEDGER "2026-07-28 (evening)"): per scan_date,
-- how much of the published pool's recommended contracts actually traded on
-- entry day. Label = entry-day MAX NON-STALE day_volume per contract (stale =
-- day_last_updated date != as_of date — yesterday's tape echo); entry day =
-- the pool's snapshot day. Floors: <50 = thin (the trader's 48%-of-pool
-- measurement), <10 = GHOST. Study baseline: 42.8% under 50 / 22.3% ghost.
-- TELEMETRY rollup only — never a feature, never joined to selection.
{{ config(materialized='table') }}

with snap as (
    select
        scan_date,
        contract,
        date(as_of) as snap_date,
        day_volume,
        date(day_last_updated) as vol_date
    from {{ source('profit_scout', 'pool_liquidity_snapshot') }}
),

entry_day as (
    -- Entry day = the first snapshot day for each scan_date's pool (the
    -- fetcher only snapshots the CURRENT pool, so this is the session the
    -- pool was live for entry).
    select scan_date, min(snap_date) as entry_day
    from snap
    group by scan_date
),

per_contract as (
    -- Entry-day max non-stale day_volume per recommended contract. A contract
    -- with zero non-stale reads traded nothing on entry day -> volume 0.
    select
        s.scan_date,
        e.entry_day,
        s.contract,
        coalesce(max(if(s.vol_date = s.snap_date, s.day_volume, null)), 0)
            as entry_day_volume
    from snap s
    join entry_day e
      on s.scan_date = e.scan_date
     and s.snap_date = e.entry_day
    group by s.scan_date, e.entry_day, s.contract
)

select
    scan_date,
    entry_day,
    count(*) as pool_contracts,
    countif(entry_day_volume < 50) as contracts_under_50,
    countif(entry_day_volume < 10) as contracts_under_10,
    safe_divide(countif(entry_day_volume < 50), count(*)) as pct_under_50,
    safe_divide(countif(entry_day_volume < 10), count(*)) as pct_under_10
from per_contract
group by scan_date, entry_day
