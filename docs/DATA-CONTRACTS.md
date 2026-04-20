# DATA-CONTRACTS.md

## Purpose
Document the key data objects used by the current forward-trading workflow.

## Enriched signals table — `profitscout-fida8.profit_scout.overnight_signals_enriched`

Primary upstream table for paper-trader execution. Populated by `enrichment-trigger` (Cloud Scheduler `enrichment-trigger-daily`, 05:30 ET Mon-Fri). Enrichment gate: `overnight_score >= 1`, `recommended_spread_pct <= 0.10`, and directional UOA > $500K. ~70 tickers/day.

All premium flags (`premium_hedge`, `premium_high_rr`, `premium_bull_flow`, `premium_bear_flow`, `premium_high_atr`, `premium_score`) are still computed and stored — they are features for post-hoc discovery, not gates.

Expected fields used by policy logic include:
- `scan_date`
- `ticker`
- `recommended_contract`
- `direction`
- `premium_score`
- `is_premium_signal`
- `recommended_volume`
- `recommended_oi`
- `recommended_dte`
- `recommended_spread_pct`
- `implied_volatility` / `recommended_iv` if available
- any market context fields needed for telemetry

**V5.3 quality-gate columns (added 2026-04-17, NULLABLE):**
- `volume_oi_ratio` — `recommended_volume / NULLIF(recommended_oi, 0)` at focal strike. Notifier requires > 2.0 (new positioning, not unwinding).
- `moneyness_pct` — `abs(recommended_strike - underlying_price) / underlying_price`. Notifier requires 5–15% OTM. Falls back to Polygon scan_date close when `underlying_price` is missing.
- `vix3m_at_enrich` — FRED `VXVCLS` close at or before `scan_date`. Notifier requires `VIX <= VIX3M` (skip day if backwardated). Fail-closed on NULL.

Schema is ensured idempotently via `ALTER TABLE ADD COLUMN IF NOT EXISTS` on every enrichment run. Old rows retain NULL and are automatically excluded by the notifier's fail-closed filter.

## Forward ledger — `profitscout-fida8.profit_scout.forward_paper_ledger`

Active forward paper-trading ledger. Written by `forward-paper-trader/main.py:run_forward_paper_trading` via delete-then-load JSON-L. One row per (scan_date, ticker) per trader invocation. No trader-side filters — all signals from `overnight_signals_enriched` are executed. **V5.3 "Target 80" mechanics (adopted 2026-04-17):** 10:00 ET entry, −60% stop, +80% target, 3-day hold, 15:50 ET exit; STOP wins over TARGET on ambiguous bars. Rows tagged `policy_version = V5_3_TARGET_80`. Legacy V4 rows (`V4_NO_GATE_SPREAD_ONLY`) are preserved as historical reference. Populated by Cloud Scheduler `forward-paper-trader-trigger` at 16:30 ET Mon-Fri.

### Columns

**Identity:**
- `scan_date`, `ticker`, `recommended_contract`, `direction`
- `is_premium_signal`, `premium_score`

**Policy metadata:**
- `policy_version`, `policy_gate`
- `is_skipped`, `skip_reason`

**Recommended contract fields (from `overnight_signals_enriched`):**
- `recommended_dte`, `recommended_volume`, `recommended_oi`, `recommended_spread_pct`

**Regime context:**
- `VIX_at_entry` — daily VIX close on entry day. Sourced from FRED (`VIXCLS`). Telemetry only.
- `SPY_trend_state` — `"BULLISH"` or `"BEARISH"`, based on SPY close > 10-day SMA on entry day. Sourced from Polygon daily bars.
- `vix_5d_delta_entry` — VIX 5-trading-day change at entry. Positive = rising vol regime.

**Execution:**
- `entry_timestamp`, `entry_price`, `target_price`, `stop_price`
- `exit_timestamp`, `exit_reason`, `realized_return_pct`

**Benchmarking (all FLOAT64 nullable):**
- `underlying_entry_price` — stock price at `entry_timestamp`. Polygon minute bar, at-or-after the entry stamp.
- `underlying_exit_price` — stock price at `exit_timestamp`. Polygon minute bar, at-or-before the exit stamp.
- `underlying_return` — `(underlying_exit_price / underlying_entry_price - 1) * direction_sign`. Signed so that a winning directional bet on the stock is positive.
- `spy_entry_price` — SPY price at `entry_timestamp`. Cached per `(entry_day, timeout_day)` window per trader invocation.
- `spy_exit_price` — SPY price at `exit_timestamp`.
- `spy_return_over_window` — `(spy_exit_price / spy_entry_price - 1)`. Unsigned. The noise floor for each trade.
- `hv_20d_entry` — 20-day annualized realized volatility on the underlying, computed from the trailing Polygon daily bars at entry.
- `iv_rank_entry` — queried at trade time from `polygon_iv_history` (trailing 252 trading days of ATM 30d IV on the underlying). `NULL` when the cache has fewer than 20 observations for the ticker.
- `iv_percentile_entry` — same source, complement metric.

## IV cache table — `profitscout-fida8.profit_scout.polygon_iv_history`

One row per (ticker, as_of_date). Populated daily by `forward-paper-trader/main.py:run_iv_cache_update` via the `POST /cache_iv` endpoint (Cloud Scheduler `polygon-iv-cache-daily`, 16:30 ET Mon-Fri). Watchlist = tickers seen in `overnight_signals_enriched` in the trailing 30 days.

**Clustering:** `ticker`. **Partition:** `as_of_date` (DAY).

| Column | Type | Notes |
|---|---|---|
| `ticker` | STRING REQUIRED | Underlying symbol |
| `as_of_date` | DATE REQUIRED | Snapshot date (ET close) |
| `atm_iv_30d` | FLOAT | Implied volatility of the ATM call whose expiration is closest to 30 DTE. NULL if no usable contract. |
| `dte_used` | INT64 | Actual DTE of the contract sampled (typically 28–35) |
| `strike_used` | FLOAT | Strike of the sampled contract |
| `underlying_px` | FLOAT | Underlying stock price at snapshot time |
| `contract_symbol` | STRING | Polygon contract symbol (e.g. `O:AAPL260508C00260000`) |
| `source` | STRING | `"polygon_snapshot"` |
| `fetched_at` | TIMESTAMP REQUIRED | When the row was written |

Idempotent per `as_of_date`: the endpoint issues `DELETE FROM polygon_iv_history WHERE as_of_date = CURRENT_DATE()` before appending, so re-triggering on the same day does not double-write.

## Current policy contract (V5.3 Target 80 — no trader-side gates)

All signals that pass the enrichment filter (`overnight_score >= 1 AND recommended_spread_pct <= 0.10 AND directional UOA > $500K`) are simulated by the paper trader. Human alerting is gated separately in `signal-notifier` by V5.3 quality filters (`volume_oi_ratio > 2`, `moneyness_pct BETWEEN 0.05 AND 0.15`, `VIX <= VIX3M`) with `LIMIT 1`. Premium flags are computed and stored as features for post-hoc discovery. See `docs/DECISIONS/2026-04-17-v5-3-target-80.md`.

## Notes
- `VIX_at_entry`, `vix_5d_delta_entry`, and `SPY_trend_state` are retained as telemetry only. None of them gate execution.
- The `signals_labeled_v1` research table (frozen, `V3_MECHANICS_2026_04_07`) is a backfilled simulation over 1563 historical signals — it is NOT the live forward-paper ledger.
- Always write `policy_version` and `policy_gate` to ledger rows for traceability.
