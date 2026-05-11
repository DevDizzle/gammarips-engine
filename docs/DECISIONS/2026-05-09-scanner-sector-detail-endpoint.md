# 2026-05-09 — overnight-scanner sector fetch moved to Polygon detail endpoint

## Decision

`src/enrichment/core/pipelines/overnight_scanner.py` no longer pre-loads
sector/industry metadata for the entire stock universe. Instead, it fetches
per-ticker SIC details for movers only (typically ~100-300 tickers), called
after pass-2 options enrichment and before scoring/cluster boost.

## Why

`overnight_signals.sector` has been NULL on every row since at least
2026-03-16 (earliest date checked — possibly older). Root cause confirmed
against the live Polygon API on 2026-05-09: the list endpoint
`/v3/reference/tickers` returns `sic_description: None` for every ticker,
even AAPL, regardless of `market`/`active`/`type`/`limit` query params or a
direct `?ticker=AAPL` filter. The detail endpoint
`/v3/reference/tickers/{ticker}` still returns SIC correctly. This is a
silent Polygon API change; our scanner kept loading 12,590 tickers across
13 paginated pages and writing all-NULL sectors downstream.

## Mechanical change

- Replaced `_load_metadata_from_polygon(poly)` (universe-wide, paginated list
  scrape) with `_load_metadata_for_tickers(poly, tickers)` (per-ticker detail
  fetch).
- Moved the call site from before pass-1 (universe-wide context, ~12K
  tickers) to between pass-2 and scoring (movers only, ~100-300 tickers).
- Cluster boost logic (`_apply_cluster_boost`) is unchanged — it iterates the
  scored list and uses `metadata.get(s['ticker'], {})` lookup, which works
  the same with the smaller per-mover dict.
- Latency cost: ~10 sec per scan at the existing 20 calls/sec rate limit.
  Tractable for an overnight job; no change to API plan or rate limit budget.

## Self-healing

If Polygon ever restores SIC on the list endpoint, the per-ticker detail
fetch continues to return correct data — just redundant. No code change
needed to revert.

## Backfill

Pre-existing NULL rows in `overnight_signals` are NOT backfilled. Sector
data appears from the next scanner run forward. The downstream report
generator (`overnight-report-generator/main.py`) gracefully handles empty
`sector_concentration` and self-heals once the scanner repopulates the
column.

## Out of scope

- The `_SIC_TO_SECTOR` mapping dict has 72 entries; SIC descriptions outside
  the dict fall back to `"Other"`. This is a graceful degradation — better
  than NULL — but the dict could be extended over time by sampling which
  SICs hit the "Other" fallback most often. Tracked separately.
- No retroactive backfill of historical reports' `sector_concentration`
  fields. The report-generator v2 self-heals starting from the next run.

## Files

- `src/enrichment/core/pipelines/overnight_scanner.py` — function rename +
  call-site move.
- `docs/DECISIONS/2026-05-09-scanner-sector-detail-endpoint.md` — this note.

## Audit

`gammarips-review` should audit before deploy. Specific checks:

1. Confirm metadata is loaded BEFORE `_apply_cluster_boost` is called.
2. Confirm rate limit (20/sec) handles the worst-case mover count without
   stalling the overnight scan past its 03:00 ET window.
3. Confirm the function works when `enriched` is small (e.g., 5 tickers) —
   no division-by-zero or empty-list edge cases.
