Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-07-07-pool-liquidity-snapshot.md
Date: 2026-07-17

# pool_liquidity_snapshot — interval liquidity read for the MCP (cache-first)

`profit_scout.pool_liquidity_snapshot` is a scheduled interval job (`signal-notifier`
`/refresh_pool_liquidity` + `pool-liquidity-refresh` scheduler) that re-reads liquidity for
the ENTIRE current enriched pool and persists it, so the MCP's `get_pool_liquidity` /
`get_contract_snapshot` serve **cache-first** rather than making N live Polygon fetches at
the busiest minute.

Why: the trader dogfood harness ranked fresh decision-time liquidity as its top ask
(GAP-001 / RM-001a); the on-demand per-contract read spent the SAME `POLYGON_API_KEY` as the
production 10:00 ET entry path and did not persist. This extends the existing ~09:45 ET
live-OI refresh plumbing ([[live-oi-floor]]) into an interval, cached surface — a data
product for the paid MCP, distinct from the pick-time OI floor that actually gates the day.
