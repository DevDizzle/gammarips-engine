# TRADING-STRATEGY.md

## Status
Current canonical strategy doc for forward paper trading.

## Objective
Validate a simple, high-conviction forward paper-trading policy that preserves alpha from the overnight options-flow scoring system without double-penalizing signals with a macro VIX gate.

## Thesis
The scanner finds stocks with unusual institutional options activity overnight and tags each one with a `direction` (BULLISH or BEARISH) reflecting where the smart-money flow is pointing. The trader follows that tag mechanically: it buys calls when `direction = BULLISH` and puts when `direction = BEARISH` (see `forward-paper-trader/main.py` `build_polygon_ticker`). We are not picking sides — we are following the scanner's read of the flow. The `is_tradeable` rule in `enrichment-trigger/main.py:599-625` requires HEDGING flow plus a high-risk-reward or high-ATR qualifier; HEDGING is a positive contributor to `premium_score`, not a skip reason. The premium-score formula is treated as load-bearing empirical work derived from the 287-signal backfill and must not be modified without fresh backtest analysis.

## Current policy: V3.1 Liquidity Quality Gate

See `docs/DECISIONS/2026-04-07-v3-1-liquidity-quality-gate.md` for the full rationale.

### Eligibility
A signal is eligible for forward paper execution when:
- `premium_score >= 2`
- `(recommended_volume >= 100 AND recommended_oi >= 50) OR recommended_oi >= 250`
- `recommended_strike IS NOT NULL AND recommended_expiration IS NOT NULL`

### Why both metrics must clear a floor (changed from V3)
The original V3 gate used an OR between vol and oi (`vol >= 250 OR oi >= 500`). This shape admitted contracts where one metric was high but the other was effectively zero — e.g. CEG vol=500/oi=0, EA vol=5037/oi=0, FTNT vol=252/oi=1. In the v3 backfill, 7 of 10 such asymmetric trades came back `INVALID_LIQUIDITY` because Polygon couldn't find minute bars at entry; the few that did "execute" did so on `oi=0` contracts where the simulator's mid-bar prices materially overstate real Robinhood fills (the simulator does not model bid-ask spread). V3.1 requires *both* a daily volume floor and an open-interest floor, with a single fallback for contracts with a genuinely deep book (oi >= 250) even on light-volume days.

### Explicit non-rule
- **No macro VIX gate** in the current V3 policy.
- VIX may still be logged as telemetry/context, but it is not a reason to skip a trade.

### Deduplication
- One trade per `ticker` per `scan_date`.

### Intended purpose
This policy exists to answer a narrow question:
> Does dropping the macro VIX gate while keeping only high-conviction, sufficiently liquid premium signals produce better forward results out of sample?

## Execution defaults (locked)
- entry at 15:00 ET (3:00 PM) on the trading day after `scan_date` (T+1)
- fixed +40% target / -25% stop brackets
- max hold of **2 trading days**
- writes to `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`

These are locked production constants in `forward-paper-trader/main.py`. The 3-day shadow variant and its `forward_paper_ledger_v3` table were deleted on 2026-04-08 after concluding that the 2-day and 3-day hold windows were statistically tied on n=29 and the 2-day variant has better capital velocity for retail Robinhood execution. The HTTP endpoint no longer exposes `hold_days` or `ledger_table` knobs — to change either, edit the constants and write a decision note.

## Benchmarking and self-instrument validation (2026-04-08)

As of Cloud Run revision `forward-paper-trader-00025-kvs`, every executed ledger row writes three parallel P&L streams inline:

1. **The option return** — the realized bracket outcome (`realized_return_pct`), the thing the trader actually trades.
2. **The underlying return** — `(stock_exit_price / stock_entry_price - 1) * direction_sign`, computed at the exact same entry/exit timestamps. This is the apples-to-apples P&L of "what if we had traded the stock instead of the option," and it isolates the options instrument's contribution to P&L from the signal's directional call.
3. **The SPY return over the same window** — the noise floor. Directional alpha is then `underlying_return - spy_return_over_window` (signed) or `underlying_return - sign * spy_return_over_window` (directional). Either way, the alpha is computable from the row itself without any retroactive join.

Plus regime context: `VIX_at_entry` (from FRED VIXCLS, daily close on entry day), `vix_5d_delta_entry`, `hv_20d_entry` (20-day annualized realized vol on the underlying, from Polygon daily bars), `iv_rank_entry` / `iv_percentile_entry` (queried at trade time from the new `polygon_iv_history` table — pending cache warmup through ~2026-05-06).

The purpose of this instrumentation is to end the filter-search loop. Every retroactive analysis on the pre-war cohort has produced a different "winning filter" because the mean of any subset of 1500 trades from a single regime is dominated by sampling noise. With inline benchmarking, future analysis is always a comparison (signal vs SPY, option vs stock), never a search over candidates. The V3.1 gate is **frozen** during the accumulation period; no filter tuning is permitted until the ledger has ≥100 trades across both the pre-war and post-war epochs. See `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`.

## What changed from V2

## What changed from V2
### V2 thesis
- premium score plus macro regime awareness
- VIX-based gating / skip logic
- more conservative filtering designed to avoid bad market regimes

### V3 thesis (The Canonical Strategy)
- premium score already captures enough options-market information that hard VIX gating may suppress real winners
- the right control knob is **signal quality + liquidity**, not broad macro disqualification

### V4 thesis (Whale Following — Active Data Collection)
- V3.1 produced only 29 trades in 7 weeks — upstream enrichment gate and premium_score gate starve the pipeline.
- Research showed premium_score does not reliably separate winners (score=0 wins 76.3% vs score>=2 at 84%, but at the cost of 1,547 trades). Vol/OI are anti-correlated with bracket outcome.
- V4 enrichment filter: `overnight_score >= 1 AND recommended_spread_pct <= 0.10 AND directional UOA > $500K`. This is the "whale following" strategy — eating off institutional unusual options activity. Enrichment floor lowered from 6 to 1. ~70 tickers/day, ~9 minute enrichment runtime.
- Trader has **no filters** — all enriched signals execute.
- Premium flags still computed and stored — they become features for post-hoc discovery, not gates.
- Runs as independent Cloud Run services (`enrichment-trigger-v4`, `forward-paper-trader-v4`) with own tables (`overnight_signals_enriched_v4`, `forward_paper_ledger_v4_hold2`). V3 untouched as live control.
- Shares upstream `overnight_signals` table and `polygon_iv_history` cache with V3.
- **Status:** Deployed 2026-04-12. Collecting data for 30-day tree-based feature importance analysis (target N >= 500).
- See `docs/DECISIONS/2026-04-12-v4-fresh-start.md` for full rationale.

### V5 thesis (High Liquidity Broad Net - Cancelled)
- Attempted to compensate for lower conviction (`premium_score = 1`) using extremely high liquidity gates.
- **Status:** Cancelled. Exhaustive minute-by-minute backtesting proved that `premium_score = 1` yields negative expectancy across all liquidity tiers. High liquidity cannot compensate for a lack of ML conviction. V3 (`premium_score >= 2`) remains the undisputed canonical strategy.

### V6 thesis (Structural Premium Wrapper - Proposed)
- Attempt to salvage `premium_score = 1` signals by applying strict structural and volatility gates instead of purely liquidity.
- **Ruleset:** `close_loc < 0.25` (Bearish) or `> 0.75` (Bullish), Mean Reversion Gate `40 <= RSI_14 <= 60` (reject over-extended setups), and Volatility Cap `atr_pct < 0.05` (reject highly erratic underlyings).
- **Status:** Proposed. Requires full backtesting and forward-paper validation.

## What should be logged
Every ledger row should preserve enough information to analyze the policy later. As of 2026-04-08 the canonical ledger schema on `forward_paper_ledger_v3_hold2` includes:

**Identity and policy:**
- `policy_version`, `policy_gate`, `scan_date`, `ticker`, `recommended_contract`, `direction`, `premium_score`
- `recommended_volume`, `recommended_oi`, `recommended_dte`, `recommended_spread_pct`

**Execution:**
- `entry_timestamp`, `entry_price`, `target_price`, `stop_price`
- `exit_timestamp`, `exit_reason`, `realized_return_pct`
- `is_skipped`, `skip_reason`

**Benchmarking (new 2026-04-08):**
- `underlying_entry_price`, `underlying_exit_price`, `underlying_return` (signed by direction)
- `spy_entry_price`, `spy_exit_price`, `spy_return_over_window` (unsigned)
- `hv_20d_entry` (20-day annualized realized volatility on the underlying)

**Regime context (new 2026-04-08):**
- `VIX_at_entry` (telemetry), `SPY_trend_state` (telemetry), `vix_5d_delta_entry`
- `iv_rank_entry`, `iv_percentile_entry` — queried at trade time from `polygon_iv_history`; remain NULL until the cache has ≥20 days of history per ticker (~2026-05-06)

## Current validation posture
- **Gate is frozen through the accumulation period.** V3.1 is not tuned, filtered, or narrowed between 2026-04-08 and the pickup session ~4-6 weeks later. This is the precondition for a valid pre-war vs post-war epoch comparison.
- **Two-regime split is the next analysis.** The war ceasefire on 2026-04-08 is the natural epoch boundary. At pickup, split the ledger by `entry_day < '2026-04-09'` vs `entry_day >= '2026-04-09'` and compare expectancy on each side. This is the first two-regime dataset we will ever have had.
- Keep V2 and V3 cohorts separate.
- Do not mix policy runs in one ambiguous ledger without version metadata.
- Favor clean forward evidence over short-window backtest confidence.
- **Do not run filter searches on the pre-war cohort.** 29 trades from a single regime cannot distinguish signal from noise, and every prior attempt produced a different top-1 candidate that failed out-of-sample.

### Pre-committed hypotheses for the N≥100 revisit

These are the only questions permitted at the next session. Testing any *other* candidate filter constitutes a new search and is not allowed until these four are settled. Documented in `NEXT_SESSION_PROMPT.md` and `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`.

1. **Epoch split (pre-war vs post-war).** Is the mean option return, mean underlying return, and directional alpha vs SPY meaningfully different across the 2026-04-08 boundary? Report numbers; do not rank filters.
2. **VIX bucket (only if N_post_war ≥ 30).** Does the `VIX_at_entry < 25` vs `≥ 25` split hold in the post-war epoch? Both the labeled cohort and the 29-trade real-ledger snapshot flagged a VIX-25 breakpoint; this test asks whether it is regime-general or a war-regime artifact.
3. **Underlying-vs-option return gap.** Is `AVG(realized_return_pct) - AVG(underlying_return)` still around −2.93 pp (the instrument bleed measured in the labeled cohort), narrower, or wider? If the gap has closed, the options instrument is behaving normally again in the post-war regime.
4. **IVR hypotheses are DEFERRED** until the `polygon_iv_history` cache has ≥252 days of history (~2027-04-08). Don't test IVR on a ~30-day cold cache.

## Open questions
- Should `recommended_dte` remain a hard filter or only logged as telemetry?
- Should spread quality later become part of the gate?
- Should the sweet-spot gate itself be split into "broad" and "sniper" sub-cohorts for reporting?
