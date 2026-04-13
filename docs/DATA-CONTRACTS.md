# DATA-CONTRACTS.md

## Purpose
Document the key data objects used by the current forward-trading workflow.

## Core source table
### `profitscout-fida8.profit_scout.overnight_signals_enriched`
Primary upstream table for V3 paper-trader selection.

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

## Forward ledger target — `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`

Canonical V3.1 forward paper-trading ledger. Written by `forward-paper-trader/main.py:run_forward_paper_trading` via delete-then-load JSON-L. One row per (scan_date, ticker) per trader invocation. Executed trades and skipped candidates both land here with `is_skipped` marking the distinction.

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
- `VIX_at_entry` — daily VIX close on entry day. Sourced from FRED (`VIXCLS`) as of 2026-04-08. Telemetry only.
- `SPY_trend_state` — `"BULLISH"` or `"BEARISH"`, based on SPY close > 10-day SMA on entry day. Sourced from Polygon daily bars.
- `vix_5d_delta_entry` — VIX 5-trading-day change at entry. Positive = rising vol regime.

**Execution:**
- `entry_timestamp`, `entry_price`, `target_price`, `stop_price`
- `exit_timestamp`, `exit_reason`, `realized_return_pct`

**Benchmarking (added 2026-04-08, all FLOAT64 nullable):**
- `underlying_entry_price` — stock price at `entry_timestamp`. Polygon minute bar, at-or-after the entry stamp.
- `underlying_exit_price` — stock price at `exit_timestamp`. Polygon minute bar, at-or-before the exit stamp.
- `underlying_return` — `(underlying_exit_price / underlying_entry_price - 1) * direction_sign`. Signed so that a winning directional bet on the stock is positive.
- `spy_entry_price` — SPY price at `entry_timestamp`. Cached per `(entry_day, timeout_day)` window per trader invocation.
- `spy_exit_price` — SPY price at `exit_timestamp`.
- `spy_return_over_window` — `(spy_exit_price / spy_entry_price - 1)`. Unsigned. The noise floor for each trade.
- `hv_20d_entry` — 20-day annualized realized volatility on the underlying, computed from the trailing Polygon daily bars at entry.
- `iv_rank_entry` — queried at trade time from `polygon_iv_history` (trailing 252 trading days of ATM 30d IV on the underlying). `NULL` when the cache has fewer than 20 observations for the ticker. Expected to start populating around 2026-05-06.
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

## V4 enriched table — `profitscout-fida8.profit_scout.overnight_signals_enriched_v4`

Same schema as `overnight_signals_enriched`. Populated by `enrichment-trigger-v4` (Cloud Scheduler `enrichment-trigger-v4-daily`, 05:30 ET Mon-Fri). Enrichment gate is relaxed: `overnight_score >= 1`, `recommended_spread_pct <= 0.10`, and directional UOA > $500K. ~70 tickers/day. Created 2026-04-12.

All premium flags (`premium_hedge`, `premium_high_rr`, `premium_bull_flow`, `premium_bear_flow`, `premium_high_atr`, `premium_score`) are still computed and stored — they are features for post-hoc discovery, not gates.

## V4 forward ledger — `profitscout-fida8.profit_scout.forward_paper_ledger_v4_hold2`

Same schema as `forward_paper_ledger_v3_hold2`. Populated by `forward-paper-trader-v4` (Cloud Scheduler `forward-paper-trader-v4-trigger`, 16:30 ET Mon-Fri). No trader-side filters — all signals from `overnight_signals_enriched_v4` are executed. Same bracket mechanics (`+40% / −25% / 2-day hold`, 15:00 ET entry). Created 2026-04-12.

## Shared IV cache — `polygon_iv_history`

The `polygon_iv_history` table is shared between V3 and V4 pipelines. Both `polygon-iv-cache-daily` (V3) and `polygon-iv-cache-v4-daily` (V4) write to this table. The table's idempotent delete-before-append pattern is per `as_of_date`, so both jobs can safely write on the same day.

## Cohort separation rule
Do not mix V2, V3, V3.1, and V4 observations without explicit policy metadata. The canonical V3 ledger is `forward_paper_ledger_v3_hold2` (V3.1, 2-day hold). The V4 ledger is `forward_paper_ledger_v4_hold2` (no-gate data collection, 2-day hold). The 3-day shadow table was deleted 2026-04-08.

## Current policy contract (V3.1, frozen through the accumulation period)

See `docs/DECISIONS/2026-04-07-v3-1-liquidity-quality-gate.md` for the full rationale.

```
premium_score >= 2
AND (
      (recommended_volume >= 100 AND recommended_oi >= 50)
      OR recommended_oi >= 250
)
AND recommended_strike IS NOT NULL
AND recommended_expiration IS NOT NULL
```

This gate is **frozen** between 2026-04-08 and the pickup session ~4-6 weeks later. No tuning, no additional filters, no bracket changes. See `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`.

## Notes
- `VIX_at_entry`, `vix_5d_delta_entry`, and `SPY_trend_state` are retained as telemetry only. None of them gate execution.
- The `signals_labeled_v1` research table (frozen, `V3_MECHANICS_2026_04_07`) is not the same as `forward_paper_ledger_v3_hold2`. The labeled table is a backfilled simulation over 1563 historical signals; the ledger table is the live forward-paper cohort.
- If the existing table name must be reused, always write `policy_version` and `policy_gate` before trusting mixed data.
