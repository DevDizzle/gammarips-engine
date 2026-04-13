# Decision: ledger benchmarking columns, FRED+Polygon data sources, and FMP retirement

- **Date:** 2026-04-08
- **Status:** accepted for forward validation
- **Supersedes:** none (additive; the V3.1 gate from `2026-04-07-v3-1-liquidity-quality-gate.md` is unchanged)

## Context

Two parallel problems motivated this decision.

**Problem 1 — the 31-day single-regime dataset cannot support filter searches.** After the V3.1 gate locked on 2026-04-07, a research session attempted to use the labeled cohort (`signals_labeled_v1`, 1563 rows from 2026-02-18 → 2026-04-06) to find improvement filters. Multiple top-1 candidates surfaced (`premium_score ≥ 2`, `risk_reward_ratio ≥ 0.42`, VIX 20-25 bearish subset) and none survived out-of-sample or walk-forward validation. The pattern was the same each time: rank N candidates on one slice, pick the best, watch it collapse when re-tested. The binding constraint is not the gate or the brackets — it is that `overnight_signals_enriched` only goes back to 2026-02-18 (31 calendar days) and every single trade in that window is contaminated by the Iran-shock regime documented in `docs/research_reports/handoffs/2026-04-08-deep-research-2-regime-output.md`. No filter search is statistically valid on a 31-day single-regime sample regardless of methodology.

**Problem 2 — the forward ledger writes option outcomes without any benchmark or context.** The only decision-relevant columns on `forward_paper_ledger_v3_hold2` prior to this decision were `realized_return_pct`, `exit_reason`, and `VIX_at_entry`. There was no way to tell, from a row alone, what the underlying stock did over the same window, what SPY did, or what the signal's own "noise floor" looked like. Every retroactive analysis required re-fetching bars from Polygon and re-joining VIX from FMP, and every conclusion was conflated with regime drift because the benchmark wasn't stored inline.

A separate, smaller problem made the VIX half of the existing telemetry silently broken: FMP's legacy historical-price endpoint was retired for non-grandfathered subscriptions, and `get_regime_context` had been returning `(None, None)` on every invocation. `VIX_at_entry` coverage across the 29 real V3.1 trades was 0% at the start of the session.

And finally: **the ceasefire on 2026-04-08 is a genuine regime boundary.** Every pre-war trade is contaminated; every post-war trade from this point forward is in a structurally different volatility environment. We need the ledger to carry enough inline context to support a clean pre-war vs post-war comparison at the next revisit, without requiring retroactive re-labeling.

## Decision

Adopt a self-benchmarking ledger — every executed trade writes the option's realized return AND the underlying stock's return over the same window AND the SPY return over the same window AND the regime context at entry, all inline, at trade time. Backfill the 29 existing rows once. Add a daily ATM 30-DTE IV cache so `iv_rank_entry` / `iv_percentile_entry` can be computed at trade time once the cache accumulates enough history. Retire the broken FMP dependency from `forward-paper-trader` and replace it with FRED (for VIX) and Polygon (for SPY daily bars and the stock-bar fetches that the benchmarking layer needs).

The V3.1 entry gate and the +40% / −25% / 2-day bracket are **unchanged**. No filters were added, removed, or tuned. Every new field is a diagnostic column or a passive regime annotation, never a gate.

### Ledger schema additions — `forward_paper_ledger_v3_hold2`

Ten new `FLOAT64` columns (nullable), added via `ALTER TABLE ADD COLUMN IF NOT EXISTS`:

| Column | Source | Purpose |
|---|---|---|
| `underlying_entry_price` | Polygon minute bar at `entry_timestamp` | Stock price when the option was bought |
| `underlying_exit_price` | Polygon minute bar at `exit_timestamp` | Stock price when the option was sold |
| `underlying_return` | Computed, signed by direction | The apples-to-apples return if we had traded the underlying |
| `spy_entry_price` | Polygon SPY minute bar at `entry_timestamp` (cached per scan_date) | Market snapshot at entry |
| `spy_exit_price` | Polygon SPY minute bar at `exit_timestamp` | Market snapshot at exit |
| `spy_return_over_window` | Computed, unsigned | Noise-floor benchmark inline on every trade |
| `hv_20d_entry` | Computed from 20 Polygon daily bars on the underlying | 20-day realized volatility; with `recommended_iv` enables inline IV−HV spread |
| `vix_5d_delta_entry` | Derived from the FRED VIX history already being pulled | Is vol rising or falling at entry? |
| `iv_rank_entry` | Computed from `polygon_iv_history` at trade time | Where current IV sits in trailing 252-day range (pending cache warmup) |
| `iv_percentile_entry` | Same source | Complement to IVR |

### Data source changes

- **VIX** (daily close, trailing window for `VIX_at_entry` and `vix_5d_delta_entry`): **FMP → FRED**. New source: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS`. No API key required, no rate limits, full history back to 1990. Cached in-process per trader invocation.
- **SPY** (daily close, 10-day SMA for `SPY_trend_state`): **FMP → Polygon** `/v2/aggs/ticker/SPY/range/1/day`. Uses the existing `POLYGON_API_KEY` already mounted in the trader's service account.
- **Stock minute bars** (for `underlying_entry_price`, `underlying_exit_price`): **Polygon** minute aggregates, same endpoint already used for option minute bars. Reuses `fetch_minute_bars`.
- **SPY minute bars** (for `spy_entry_price`, `spy_exit_price`): **Polygon** minute aggregates, cached per `(entry_day, timeout_day)` pair so SPY is fetched at most once per scan_date per trader invocation.
- **Underlying daily bars** (for `hv_20d_entry`): **Polygon** `/v2/aggs/ticker/{T}/range/1/day`. ~35 calendar days per fetch. Computed server-side inside `benchmark_context.fetch_hv_20d`.
- **Underlying ATM 30-DTE IV** (for the `polygon_iv_history` cache): **Polygon** `/v3/snapshot/options/{T}` chain snapshot. Written daily via the new `/cache_iv` endpoint (see below).

The FMP API key is no longer read by any code path in `forward-paper-trader/`. The `FMP_API_KEY` secret mount has been removed from `forward-paper-trader/deploy.sh`. Other services (enrichment-trigger, win-tracker, overnight-report-generator) may still use FMP — this cleanup is scoped to `forward-paper-trader/` only.

### New table — `polygon_iv_history`

One row per (ticker, as_of_date) in `profitscout-fida8.profit_scout.polygon_iv_history`. Clustered by `ticker`, partitioned by `as_of_date`. Schema:

```
ticker           STRING    REQUIRED
as_of_date       DATE      REQUIRED
atm_iv_30d       FLOAT64
dte_used         INTEGER
strike_used      FLOAT64
underlying_px    FLOAT64
contract_symbol  STRING
source           STRING    // "polygon_snapshot"
fetched_at       TIMESTAMP REQUIRED
```

Populated daily by the new `POST /cache_iv` endpoint on `forward-paper-trader`, triggered by Cloud Scheduler job `polygon-iv-cache-daily` at 16:30 ET Mon-Fri. Watchlist = any ticker that appeared in `overnight_signals_enriched` in the trailing 30 days (~500 tickers). Idempotent per `as_of_date` (DELETE-then-LOAD). Initial smoke test: 497 rows written, 496 with IV populated, IV range 4.7% – 417.4%, mean 59.7%, average DTE used 32.5.

At trade time, `benchmark_context.fetch_iv_rank_from_bq(ticker, entry_day)` queries the trailing 252 trading days of this table and computes IVR / IVP. Returns `(None, None)` if fewer than 20 observations exist for the ticker in the window — so `iv_rank_entry` and `iv_percentile_entry` will remain null on every trade for the first ~20 trading days after the cache goes live (approximately through 2026-05-06). This is correct behavior, not a bug. IVR is undefined on a cold cache.

### New code paths

- **`forward-paper-trader/benchmark_context.py`** — new module, ~400 lines. Owns the non-blocking benchmarking layer: HV-20d compute, SPY-bar cache, Polygon chain snapshot, ATM-IV extractor, IVR BQ query, price-at-timestamp locators. Imports only stdlib + pypi + the BigQuery client. Hermetic — does not import from `src/` so the trader's Docker build stays isolated from the enrichment service.
- **`forward-paper-trader/main.py`** — one new function (`run_iv_cache_update`), one new route (`POST /cache_iv`), ten new keys populated in the `record` dict during the main trading simulation, one data-source swap in `get_regime_context` (FMP → FRED+Polygon).
- **`scripts/ledger_and_tracking/create_polygon_iv_history.py`** — one-shot DDL script.
- **`scripts/ledger_and_tracking/backfill_benchmarks_v1.py`** — one-shot backfill of the 29 existing rows (already executed).
- **`scripts/ledger_and_tracking/current_ledger_stats.py`** — read-only weekly snapshot. Prints cohort stats stratified by VIX bucket, HV bucket, and direction. **Does not rank filters. Does not search for winners.**

### What the session produced (forward-looking, not a conclusion)

Running `current_ledger_stats.py` on the post-backfill ledger gave the first three-way-positive result in the entire research series:

```
Option return (bracketed)          29   +2.91%   win 48.3%
Underlying return 1x (signed)      29   +0.36%   win 44.8%
SPY return over window             29   +0.01%   win 55.2%
Alpha: underlying − SPY            29   +0.35%   win 51.7%
```

Every axis is positive. SPY floor is essentially zero, which means the underlying-return positive is not SPY-drift capture (unlike the earlier bearish-VIX-20-25 subset from the labeled cohort, which turned out to be pure market beta). Sample size is still 29 and the 95% CI on the stock return is roughly [−1.6%, +2.3%] — CI includes zero. **This is not validation. It is the first cohort-level result in the research series where option, stock, and alpha all move positive simultaneously with a flat benchmark.** The instrumentation exists specifically so that 4-6 weeks from now we can test whether this pattern survives the post-war regime.

See `docs/research_reports/BENCHMARKING_VALIDATION_V1.md` for the full cohort report.

## Rationale

- **Self-benchmarking is the only way out of the filter-search trap.** As long as every analysis has to re-fetch bars from Polygon and join VIX from a side source, each new question produces a new top-1 candidate and no structural progress. Storing the noise floor inline on every trade turns every future analysis into a comparison, not a search.
- **The war ending today is a natural experiment and a genuine regime boundary.** At the revisit point in 4-6 weeks the ledger will have ~50-60 trades, roughly half pre-war and half post-war — the first two-regime dataset we will ever have had. The instrumentation has to be in place *before* the post-war trades start landing, otherwise the post-war cohort gets the same "do we re-fetch bars?" problem the pre-war cohort did. Doing this now is not overhead; it is the precondition for any meaningful revisit analysis.
- **FMP is broken and the fix is cheaper than the workaround.** FRED's VIXCLS CSV endpoint requires no API key, has no rate limits, and returns the full history back to 1990 in a single HTTP call. Polygon's daily-bar endpoint is already paid for and already reliable. Switching costs ~50 lines of code and removes one production dependency. Continuing to debug FMP rotation or migration would cost more.
- **IVR needs a long pre-warmup and starting it now is the only way to have it at the 12-month mark.** The cache has to accumulate ~252 trading days of per-ticker history before IVR becomes decision-grade. Whatever month we start, we're on that clock. Starting today means by 2027-04-08 we have a full year of IVR on every active ticker. Delaying would push that out by the same amount. The intermediate state (cache is warm enough for diagnostic use, ~30-60 days after start) will land in the middle of the post-war accumulation period, where it's useful but not yet decision-grade.
- **Hermetic trader Docker build.** The Polygon chain fetcher was copied into `benchmark_context.py` rather than cross-imported from `src/enrichment/core/clients/polygon_client.py` to preserve the trader's deployment independence. The duplication is ~80 lines of a stable, well-tested pattern; the coupling savings are worth the duplication cost.
- **Non-blocking benchmarking layer is the only acceptable failure mode.** Every new fetch in the signal loop is wrapped in `try/except → log + null`. A Polygon outage, a FRED CSV 500, or a missing underlying quote can never block a trade from being written to the ledger. The benchmarking layer runs in the shadow of the main trading path, not ahead of it.

## Cohort impact

No cohort change. The V3.1 gate is unchanged and no signals that were previously tradeable are now filtered. Every existing ledger row still exists; only additional columns were added. The 29 rows backfilled non-destructively via explicit `UPDATE` statements per row.

| Field | Coverage before | Coverage after |
|---|---:|---:|
| `VIX_at_entry` | 0/29 (FMP broken) | **29/29** (FRED restored) |
| `vix_5d_delta_entry` | 0/29 (column didn't exist) | **29/29** |
| `underlying_entry_price` | 0/29 | **29/29** |
| `underlying_exit_price` | 0/29 | **29/29** |
| `underlying_return` | 0/29 | **29/29** |
| `spy_entry_price` | 0/29 | **29/29** |
| `spy_exit_price` | 0/29 | **29/29** |
| `spy_return_over_window` | 0/29 | **29/29** |
| `hv_20d_entry` | 0/29 | **29/29** |
| `iv_rank_entry` | 0/29 | 0/29 (cache cold; expected to warm ~2026-05-06) |
| `iv_percentile_entry` | 0/29 | 0/29 (same) |

## Consequences

- Every trade from Cloud Run revision `forward-paper-trader-00025-kvs` onward writes the full benchmarking payload inline. Rollback is a one-command Cloud Run revision switch if anything in the benchmarking layer ever blocks a trade.
- `iv_rank_entry` / `iv_percentile_entry` will populate gradually as `polygon_iv_history` accumulates. Do **not** treat null IVR as a bug during the warmup period.
- Cloud Scheduler job `polygon-iv-cache-daily` runs at 16:30 ET Mon-Fri against `POST /cache_iv` on `forward-paper-trader`. First scheduled run: 2026-04-09 16:30 ET. Health check: `SELECT COUNT(*), MIN(as_of_date), MAX(as_of_date), COUNT(DISTINCT ticker) FROM polygon_iv_history` on any subsequent day should show one new row-count per ticker per trading day.
- The existing 29 backfilled rows give us a pre-war reference cohort. The trades that accumulate from 2026-04-09 onward are the post-war cohort. At N=100+ total trades (roughly 6-8 weeks), the pickup session runs the pre-committed hypotheses documented in `NEXT_SESSION_PROMPT.md`. Until then, the gate is frozen and no filter searches are permitted.
- Scanner selection analyses (`docs/research_reports/INTELLIGENCE_BRIEF.md` open questions) remain out of scope until the ledger has accumulated enough data. Not blocked by this decision.

## Follow-up

- **Do not touch the V3.1 gate during the accumulation period.** This is the single most important follow-up. The entire value of the self-benchmarking ledger is that it runs on a frozen gate — gate changes during accumulation would invalidate the pre-war vs post-war comparison.
- **Run `current_ledger_stats.py` weekly** for vibes-level monitoring. Do not rank filters from its output. Do not act on any single-week result. Its purpose is to catch operational breakages (trader stopped running, IVR cache broke) not to inform strategy changes.
- **At the pickup session (~4-6 weeks from 2026-04-08):** run the pre-committed hypotheses documented in the rewritten `NEXT_SESSION_PROMPT.md`. Pre-war vs post-war epoch split is hypothesis #1. VIX < 25 vs ≥ 25 in the post-war epoch is hypothesis #2 (only if post-war N ≥ 30). Underlying-vs-option return gap is hypothesis #3. IVR hypotheses remain DEFERRED — the cache will have only ~20-30 days of history at pickup, not the 252 days needed to test IVR meaningfully.
- **IVR becomes decision-grade at the 12-month mark** (~2027-04-08) when every actively-traded ticker in the watchlist has a full trailing-year of history. Until then, treat IVR columns as diagnostic only.
- **Revisit the trader Docker build strategy** if a third benchmarking feature needs a Polygon helper — at that point the duplication cost may exceed the coupling cost and a shared package under `forward-paper-trader/` makes sense. Not urgent.
- **Clean up FMP everywhere else** (enrichment-trigger, win-tracker, overnight-report-generator) as a separate work item — this decision is scoped to `forward-paper-trader/` only and does not audit other services' FMP usage.
