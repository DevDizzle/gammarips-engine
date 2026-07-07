# 2026-07-07 — Interval pool-liquidity snapshot (`pool_liquidity_snapshot`) for the MCP

## Status
Shipped 2026-07-07 (signal-notifier `/refresh_pool_liquidity` + Cloud Scheduler
`pool-liquidity-refresh` + BQ `profit_scout.pool_liquidity_snapshot` +
gammarips-mcp cache-first `get_contract_snapshot` / new `get_pool_liquidity`).

## Context
The gammarips-trader dogfood harness (MCP "user zero") ranked fresh decision-time
liquidity as its **top ask** (GAP-001 / RM-001a in the trader repo's
`docs/MCP-ROADMAP.md`). Doctrine hard-exclusion §3 requires a fresh liquidity
read at ~10:00 ET on the day's shortlist. RM-001a (`get_contract_snapshot`,
shipped 07-06) gave an on-demand per-contract read, but (a) checking a 3–5 name
shortlist was N separate upstream fetches at the busiest minute, (b) each fetch
spends the SAME `POLYGON_API_KEY` the production 10:00 ET entry path uses, and
(c) contract snapshots weren't persisted, so nothing could serve them cheaply.

## Decision
Extend the plumbing that already exists — the notifier's ~09:45 ET live-OI
refresh (`_fetch_live_oi`, 2026-06-25 OI floor) — into a **scheduled interval
job** that re-reads liquidity for the ENTIRE current enriched pool and persists
it:

1. **`signal-notifier/pool_liquidity.py`** — a NEW module (deliberately not a
   refactor of `_fetch_live_oi`; see leakage wall below). Fetches the full
   Polygon option snapshot per pool contract (OI, session volume, last trade,
   day OHLC, IV/greeks) plus an underlying-price fallback chain
   (`option_snapshot` → today's delayed day-agg close → prev close), and
   appends one row per (contract, `as_of`) to
   **`profit_scout.pool_liquidity_snapshot`** via `insert_rows_json` against a
   pre-created EXPLICIT schema (no load jobs, no autodetect — the 2026-07-02
   enrichment outage rule). Table is partitioned by `DATE(as_of)`, clustered by
   `contract` (DDL: `scripts/ledger_and_tracking/create_pool_liquidity_snapshot.py`,
   executed 2026-07-07).
2. **`POST /refresh_pool_liquidity`** on signal-notifier — self-gates to NYSE
   trading days ~09:15–16:05 ET (the ~09:22 firing is the pre-open pass,
   `is_preopen=true`); in-process 120s min-interval spam guard
   (max-instances=1 makes it effective). **Token-gated (review FIX-1):**
   `POOL_LIQ_REFRESH_TOKEN` is secret-mounted via deploy.sh (`--set-secrets`
   REPLACES the set — the mount must stay in the script or the next deploy
   silently strips it); every call must send it as `X-Refresh-Token`
   (`hmac.compare_digest`), and the dangerous knobs (`force`, `scan_date` —
   which can spin the Polygon meter or rewrite which pool MCP clients see as
   "latest") are refused unless token-authenticated even if the secret is
   unset. Interim posture until 2026-07-02-service-auth-hardening executes.
3. **Cloud Scheduler `pool-liquidity-refresh`** — `2-52/10 9-16 * * 1-5`
   America/New_York → the endpoint, with the `X-Refresh-Token` header.
   ~48 firings/day (handler no-ops outside its window and on holidays).
   The `:x2` offset (review FIX-2) keeps passes clear of the ~09:45 ET pick
   run on the same max-instances=1 service: the 09:42 pass finishes by
   ~09:43 and the next fires at 09:52.
4. **MCP serves it cache-first** — `get_contract_snapshot` reads the newest
   cache row when < `SNAPSHOT_CACHE_FRESH_S` (900s) old, `live=true` (or a
   cache miss / non-pool contract) forces the upstream fetch, and the new
   **`get_pool_liquidity(scan_date?, contracts?)`** returns the latest row per
   contract for the whole pool / a shortlist in ONE metered call. Every
   response carries `retrieved_from` + `as_of` (+ `cache_age_seconds`) so
   staleness is always explicit.

## Leakage wall (the part that is physics)
Everything this job fetches is **entry-day-live telemetry** (the 09:15+ tape).
Classification: **TELEMETRY — never a feature.**

- The table must NEVER be joined into `overnight_signals_enriched`,
  `enriched_features_v1`, or any as-of ≤ scan_date feature surface.
- It must never reach the tournament / signal-judge selection path. The pick
  path keeps its own C1-walled fetch (`_fetch_live_oi` extracts OI + volume
  only, everything else discarded at fetch time). **Do not deduplicate the two
  fetch paths — the wall is the point.** `run_notifier()` does not import
  `pool_liquidity`.
- MCP/agents consume it as a live liquidity read with explicit `as_of`
  provenance — decision-time freshness, not a backtest feature. (Post-entry
  analysis of *past* snapshots is fine — they're timestamped telemetry, same
  class as `oc_*` regime telemetry.)

## Quote fields (RM-001b posture)
`bid/ask/mid/spread_pct` exist in the table schema but are written NULL — the
current Polygon plan serves NO options quotes
(2026-06-05-engine-quote-outage-and-gate.md). The MCP **omits** them from
responses while NULL (a missing field is honest; a NULL reads like a data bug).
If the quote-feed purchase (owner $ call) lands, populate them in
`pool_liquidity.py:_fetch_contract_row` and they flow through automatically.
If declined, this stays the permanent documented posture.

## Cost / blast radius
~50 contracts + ≤50 underlying-price fallbacks per pass × ~40 passes/day ≈
4k Polygon calls/day (flat-rate plan; unmetered) + ~2k streamed BQ rows/day
(negligible). The endpoint is fully fail-soft and independent of the pick
path: a total failure means stale cache rows (the MCP falls back to live
upstream fetches), never a missed pick. Kill switch = pause the Scheduler job.

## Revisit when
- The quote feed is purchased (populate RM-001b fields end-to-end).
- Service-auth hardening executes (fold the endpoint behind OIDC and drop the
  token check).
- The pool cap changes materially (>100 contracts → rethink fan-out width).
