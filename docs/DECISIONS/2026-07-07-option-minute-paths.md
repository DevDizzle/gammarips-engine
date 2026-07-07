# 2026-07-07 — `option_minute_paths` companion table (must-fix #6g / MCP RM-002 + TF-14)

## Status
Shipped 2026-07-07. Table created + FULL history backfilled (144,448 bars,
2,675 contract-days, entry days 2026-04-13 → 2026-07-01; 419 contract-days
legitimately empty — the no-print illiquid tail) + topped up through
2026-07-06. Daily top-up endpoint on forward-paper-trader
(`POST /persist_minute_paths`) + Cloud Scheduler `option-minute-paths-refresh`.

## Context
The excursion substrate stored only MFE/MAE **extremes** (`opp_*`), so when a
bracket's target AND stop were both crossed inside the window, first-crossing
order was unrecoverable — `estimate_exit_rule` resolved those rows by a
minutes-to-extreme heuristic (~10.5% of classifications), and trailing rules
could not be scored at all. This was engine must-fix #6g (known-deferred) and
the trader harness's GAP-002.

## Decision
Persist the minute tape the labeler already replays from:

1. **`profit_scout.option_minute_paths`** — one row per (contract, entry_day,
   ts): per-minute OHLCV premium bars over each enriched-pool candidate's
   3-trading-day excursion window. Partition `entry_day`, cluster `contract`.
   DDL: `scripts/ledger_and_tracking/create_option_minute_paths.py`.
   **LOAD JOBS ONLY with the explicit schema** (daily reconcile DELETEs by
   scan_date — streaming buffers would block that; autodetect banned per the
   2026-07-02 outage rule).
2. **Backfill** — `scripts/ledger_and_tracking/backfill_option_minute_paths.py`
   (executed 2026-07-07): one Polygon minute-aggs range call per labeled
   (contract, entry_day) from `enriched_option_outcomes`.
3. **Daily top-up** — `forward-paper-trader/minute_paths.py` behind
   `POST /persist_minute_paths`: each evening reconciles the last 3
   scan_dates' pools (window `[entry_day .. min(exit_day_3d, today)]`,
   DELETE-then-LOAD per scan_date, idempotent). Pool comes from
   `overnight_signals_enriched` so it is independent of labeler lag. Fully
   walled: called only from its own endpoint; the trader/labeler paths never
   import it. Token-gated with the same `POOL_LIQ_REFRESH_TOKEN` secret as
   the notifier's pool-liquidity endpoint (scan_dates override refused
   without the token).
4. **Cloud Scheduler `option-minute-paths-refresh`** — daily ~17:40 ET
   weekdays (after the 17:00 labeler + 17:20 outcomes refresh), with the
   `X-Refresh-Token` header.

## What it unlocks (MCP)
- **`replay_contract(contract, date, target_pct?, stop_pct?)`** — per-session
  minute path served table-first (upstream fallback for non-pool contracts),
  with an optional exact first-crossing readout off the 10:00 ET anchor.
- **`estimate_exit_rule` exact resolution** — both-levels-crossed rows now
  resolve by exact first touch (same-bar → STOP-first, the labeler's
  pessimistic rule). Measured on the +40/−30 3d bracket: heuristic share
  0.1045 → **0.0** (212/212 ambiguous rows resolved; 90 TARGET / 122 STOP).
- **`estimate_exit_rule(rule='trailing')` (TF-14)** — bar-by-bar SQL replay
  of a hard-stop + trailing-giveback (+optional activation) rule, horizons
  same_day (day-1 bars ≤15:45 ET) and 3d. Conservative bar mechanics: trail
  rides the PRIOR-bar peak; touch fills at min(bar open, level). The entry
  anchor (`opp_entry_price`) already embeds the engine's entry-slippage fill;
  no EXIT slippage is applied (results are entry-net, exit-gross).

## Leakage classification
**REALIZED TAPE — never a feature.** Same class as the `opp_*` opportunity
surface: research/label substrate for CLOSED windows. Never joined into
`enriched_features_v1` or any as-of ≤ scan_date surface; never read by the
selection path or the live trader. Serving closed-window bars to agents is
data-vendor product (the historical tape, explicitly timestamped), consistent
with the opportunity-surface posture.

## Recovery path
If a reconcile dies between its DELETE and LOAD on a window's LAST (day-3)
pass, that scan_date drops out of the next evening's last-3 set and stays
empty until manually re-run. Recovery: POST /persist_minute_paths with the
`X-Refresh-Token` header and `{"scan_dates": ["YYYY-MM-DD"]}` (token-gated
override, ≤10 dates). `--max-instances=1` + the daily cadence make the
overlap/double-run case remote.

## Cost / blast radius
Backfill ≈ 3.1k Polygon calls (one-time). Daily ≈ 150 calls + ~6k rows.
Failure mode = stale minute paths (MCP replay falls back upstream; exit-rule
scoring reports coverage via `n_excluded_no_bars` / heuristic share) — never
a missed pick, never a broken label run. Kill switch = pause the Scheduler job.

## Revisit when
- The pool cap or window length changes (row volume scales linearly).
- A real quote feed lands (bars could then carry NBBO context — new columns,
  explicit schema change, never autodetect).
- Same-day arbitrary-bracket scoring is requested (the minute data now
  supports it; deliberately not built in this pass).
