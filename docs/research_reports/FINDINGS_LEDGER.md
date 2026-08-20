# Findings Ledger — GammaRips Signal Research

> **Distilled to the wiki (2026-07-17).** The one-claim compiled-knowledge versions of these
> findings now live in [`docs/wiki/`](../wiki/_index/REGISTRY.md) (findings/ + literature/).
> Start there for the current state of a lever; this file stays the **canonical evidence
> base with the full tables and N** that each note cites — it is provenance, not the index.
>
> Durable evidence base. Every numeric claim in `INTELLIGENCE_BRIEF.md` should be traceable to a row in this file. Originals preserved in `_archive/research_reports_2026-04/`. (`STRATEGY_PLAYBOOK.md` is archived at `../archive/research_reports/`.)

## Index (added 2026-08-20)

Read this file by section, never whole. Status legend: **LIVE-DOCTRINE** (claim still governs), **CLOSED-NULL** (tested, dead, do not re-propose), **HISTORICAL** (V3-V5-era evidence, cited by wiki notes, not current doctrine).

| Section | One-line claim | Status | Wiki note |
|---|---|---|---|
| §Cohort definitions | `signals_labeled_v1`: N=1,563 executed, Feb-Apr 2026, frozen V3 mechanics | HISTORICAL | — |
| §Bracket Sweeps | 0/840 bracket variants profitable on the whole-pool cohort | LIVE-DOCTRINE | [[bracket-optimization-dead]] |
| §Premium-Score Validation | premium_score is anti-predictive; the production filter made it worse | CLOSED-NULL | [[premium-score-anti-predictive]] |
| §Filter Discovery | ~800 univariate filters and top pair combos; none survive bootstrap | CLOSED-NULL | — |
| §Dead-ends — option-PnL gate discovery | five 2026-06-05 gate candidates dead; direction was the only robust lever | CLOSED-NULL | [[bullish-direction-asymmetry]] |
| §Momentum lever + exploit falsification + pool-cap (2026-06-19) | mom_60 tilt shipped; ride-recent-winners falsified; cap-25 coverage | HISTORICAL (tilt graded retire-worthy OOS 07-28; owner kept it) | [[momentum-60d-enrichment-tilt]], [[ride-winners-mean-reverts]], [[pool-cap-coverage]] |
| §Bootstrap Validation — `filt_rrr` autopsy | the canonical multiple-comparison failure; regime artifact, not edge | LIVE-DOCTRINE (method rule) | — |
| §Univariate Feature Quintiles | per-feature quintile tables; `recommended_oi` is the monotonic loser | HISTORICAL | [[oi-not-quality-signal]] |
| §Tree-Based Feature Importance | GBM and tree importance on N=1,563 is noise | HISTORICAL | — |
| §Liquidity Findings | liquidity gating lifts the cohort to breakeven, not profit | HISTORICAL | — |
| §Execution Mechanics | pre-Iran intraday sweep and Monte Carlo parameters | HISTORICAL | — |
| §Scoring v2 spec | V3-era regime-aware execution spec; template only | HISTORICAL | — |
| §Regime Context | the Feb-Apr 2026 cohort is regime-confounded (Iran shock) | LIVE-DOCTRINE (caveat) | — |
| §Reading list / §Source mapping | literature anchors; originals-to-sections map | reference | — |
| §2026-06-22 — Entry-timing | earlier-than-10:00 entries are a thin-tape mirage; keep 10:00 | LIVE-DOCTRINE (amended by §2026-08-19 entry hour) | [[entry-1000-et]] |
| §2026-07-06 — ITM vs delta | the pool is delta-calibrated; zero directional edge at expiration | LIVE-DOCTRINE | [[pool-delta-calibrated]] |
| §2026-07-06 — excursion vs IV null | path-calibrated too; the giveback is the durable finding | LIVE-DOCTRINE | [[path-calibrated-giveback]] |
| §2026-07-06 — harvest curve | pops are late (day 2-3); every fixed-target rule is negative | LIVE-DOCTRINE | [[three-day-harvest-curve]] |
| §2026-07-28 — pool-of-50 composition | mom_60 retire-grade OOS; delta ceiling validated; zero underlying alpha | LIVE-DOCTRINE | [[momentum-60d-enrichment-tilt]] |
| §2026-07-28 (evening) — tradeability | ghost-pool mechanism quantified; name-level liquidity predictors unused | LIVE-DOCTRINE | [[live-oi-floor]] |
| §2026-08-05 — trader-handoff adjudication | catalyst/ATR "inversions" refuted at scale (between-day artifact) | CLOSED-NULL | [[catalyst-atr-inversion-refuted]] |
| §2026-08-19 — PM entry / overnight | no morning pop on tradeable contracts; the overnight hold deletes the stop | CLOSED-NULL | [[overnight-hold-breaks-the-stop]] |
| §2026-08-19 (execution) | execution risk is exit certainty, not spread; stop fills slip one-sided | LIVE-DOCTRINE | [[execution-risk-is-exit-certainty]] |
| §2026-08-19 (tradeable subset) | ghosts flattered the pool (-4.67% vs -9.59%); contract_score re-test FAILS | LIVE-DOCTRINE | [[ghost-rows-flatter-pool-composites]], [[contract-score-lead-dead]] |
| §2026-08-19 (bracket sweep, tradeable) | 0/432 on the honest substrate; the ghost objection is closed | LIVE-DOCTRINE | [[bracket-optimization-dead]] |
| §2026-08-19 (pool construction) | ghost-free pool of 50 impossible; outcome: PRINT_FLOOR_MIN=25 deployed 2026-08-20 | LIVE-DOCTRINE | [[live-oi-floor]] |
| §2026-08-19 (entry hour) | 10:00-11:00 carries the whole day's bleed; later entry is an open owner call | LIVE-DOCTRINE (owner call open) | [[first-hour-bleed]] |

---

> **Era banner.** Sections from here through §Source mapping are the Feb-Apr 2026 (V3-V5, `signals_labeled_v1`) era: historical evidence that wiki notes cite, not current doctrine. The dated entries from §2026-06-22 onward are the live-ledger era.

## Cohort definitions

### `signals_labeled_v1` — canonical labeled cohort

- **Source table:** `profitscout-fida8.profit_scout.signals_labeled_v1` (frozen, do not regenerate)
- **Population:** every row in `overnight_signals_enriched` with `recommended_strike IS NOT NULL AND recommended_expiration IS NOT NULL`. No premium_score, liquidity, or is_tradeable filtering. Dedup: one row per (ticker, scan_date), keep highest `premium_score`, tiebreak on highest `recommended_volume`.
- **Schema:** all 78 columns from `overnight_signals_enriched` plus 13 outcome columns (`entry_day`, `timeout_day`, `entry_timestamp`, `entry_price`, `target_price`, `stop_price`, `exit_timestamp`, `exit_price`, `exit_reason`, `realized_return_pct`, `bars_to_exit`, `simulator_version`, `labeled_at`).
- **Simulator version:** `V3_MECHANICS_2026_04_07` (frozen).
- **Window:** scan_date 2026-02-18 → 2026-04-06, 30 distinct scan_dates, 573 distinct tickers.
- **Sample sizes:** 2162 labeled / 1563 executed (exit_reason ∈ {TARGET, STOP, TIMEOUT}).
- **Verification:** simulator parity confirmed against 5 live ledger rows (INTU, CAKE, SEI, IQV, NFLX) — 5/5 bit-for-bit match on entry_price, exit_price, exit_reason, realized_return_pct.

### V3 simulator mechanics (frozen)

- `entry_day` = first trading day after `scan_date` (the day the trade is surfaced).
- Entry bar: first Polygon minute bar at-or-after 15:00 ET on `entry_day`; fall back to last bar before 15:00 if no late-session prints; mark `INVALID_LIQUIDITY` if zero printed bars.
- Slippage: `base_entry = entry_bar.close * 1.02` (+2%).
- Brackets: `target = base_entry * 1.40`, `stop = base_entry * 0.75`.
- If both target and stop touched in the same bar, **stop wins**.
- Force exit: `timeout_day = entry_day + 2 trading days`, at 15:59 ET. Use last bar at-or-before that boundary.
- Skip and label `FUTURE_TIMEOUT` if `timeout_day >= today`.

### Exit reason distribution (full population)

| exit_reason | n | % |
|---|---|---|
| FUTURE_TIMEOUT | 178 | 8.2% |
| INVALID_LIQUIDITY | 273 | 12.6% |
| NO_BARS | 148 | 6.8% |
| STOP | 789 | 36.5% |
| TARGET | 345 | 16.0% |
| TIMEOUT | 429 | 19.8% |

### Executed-trade summary

- n = 1563
- avg `realized_return_pct` = **−3.26%**
- median = **−25.00%**
- win rate (return ≥ +35%) = **22.6%**

Source: `_archive/research_reports_2026-04/SIGNAL_FEATURE_DISCOVERY_V1.md` §1.

---

## Bracket Sweeps

### V1 — full unfiltered cohort

- **Variants tested:** 840 (4 entry times × 7 targets × 5 stops × 6 holds; includes no-target and no-stop variants and 15-day holds)
- **Cohort:** 1552 executed signals, 464 OOS (chronological 70/30 split)
- **Variants with positive in-sample avg_return:** 0 / 840
- **Variants with positive OOS avg_return:** 0 / 840

#### Top 10 by OOS avg_return

| rank | variant | n | avg | win% | OOS n | **OOS avg** | OOS win% |
|---|---|---|---|---|---|---|---|
| 1 | 15:55 / tgt=none / stop=-20% / hold=3d | 1552 | −2.15% | 21.3% | 464 | **−1.99%** | 19.6% |
| 2 | 15:45 / tgt=none / stop=-20% / hold=3d | 1552 | −2.41% | 21.3% | 464 | **−2.30%** | 19.4% |
| 3 | 15:30 / tgt=none / stop=-20% / hold=3d | 1552 | −2.47% | 21.3% | 464 | **−2.58%** | 19.0% |
| 4 | 15:55 / tgt=+150% / stop=-20% / hold=3d | 1552 | −1.34% | 22.0% | 464 | **−2.60%** | 20.0% |
| 5 | 15:55 / tgt=+200% / stop=-20% / hold=3d | 1552 | −1.81% | 21.5% | 464 | **−2.64%** | 19.6% |
| 6 | 15:45 / tgt=+200% / stop=-20% / hold=5d | 1552 | −2.01% | 17.5% | 464 | **−2.69%** | 17.5% |
| 7 | 15:55 / tgt=+200% / stop=-20% / hold=5d | 1552 | −1.80% | 17.6% | 464 | **−2.72%** | 17.5% |
| 8 | 15:45 / tgt=none / stop=-20% / hold=5d | 1552 | −3.66% | 16.6% | 464 | **−2.73%** | 17.0% |
| 9 | 15:55 / tgt=none / stop=-20% / hold=5d | 1552 | −3.51% | 16.8% | 464 | **−2.79%** | 17.0% |
| 10 | 15:45 / tgt=+200% / stop=-20% / hold=3d | 1552 | −2.09% | 21.5% | 464 | **−2.95%** | 19.4% |

#### Best per dimension (OOS)

| dimension | best variant | OOS avg |
|---|---|---|
| entry_time=15:00 | 15:00 / tgt=none / stop=-20% / hold=5d | −3.17% |
| entry_time=15:30 | 15:30 / tgt=none / stop=-20% / hold=3d | −2.58% |
| entry_time=15:45 | 15:45 / tgt=none / stop=-20% / hold=3d | −2.30% |
| entry_time=15:55 | 15:55 / tgt=none / stop=-20% / hold=3d | **−1.99%** |
| target=none | 15:55 / tgt=none / stop=-20% / hold=3d | −1.99% |
| target=+25% | 15:55 / tgt=+25% / stop=-20% / hold=5d | −6.05% |
| target=+50% | 15:55 / tgt=+50% / stop=-20% / hold=5d | −3.71% |
| target=+200% | 15:55 / tgt=+200% / stop=-20% / hold=3d | −2.64% |
| stop=none | 15:55 / tgt=none / stop=none / hold=5d | −8.16% |
| stop=-20% | 15:55 / tgt=none / stop=-20% / hold=3d | −1.99% |
| stop=-50% | 15:00 / tgt=none / stop=-50% / hold=5d | −8.69% |
| stop=-75% | 15:45 / tgt=none / stop=-75% / hold=5d | −9.33% |
| hold=2d | 15:55 / tgt=+150% / stop=-20% / hold=2d | −3.17% |
| hold=3d | 15:55 / tgt=none / stop=-20% / hold=3d | **−1.99%** |
| hold=5d | 15:45 / tgt=+200% / stop=-20% / hold=5d | −2.69% |
| hold=15d | 15:55 / tgt=+50% / stop=-20% / hold=15d | −4.16% |

**Best overall:** `15:55 / tgt=none / stop=-20% / hold=3d` → OOS avg **−1.99%**, win 19.6%, n=464. (Used as the "least-bad bracket" reference throughout the rest of this ledger.)

#### Realistic 1-trade-per-scan_date strategy

For each scan_date, pick the highest `premium_score` signal (tiebreak: highest OI). 27 picks one per scan_date.

- All-cohort avg: −9.49%, win 18.5%
- OOS avg: −3.61%, OOS win 22.2%, n=9
- Cumulative P&L at $1000/trade: **−$2,563** over 27 trades
- Max drawdown: **−$2,550**

Source: `_archive/research_reports_2026-04/BRACKET_SWEEP_V1.md`.

### V2 — re-sweep on filtered cohorts

Same 840-variant grid, three pre-filters:

- `baseline` — no filter (sanity check)
- `filt_rrr` — `risk_reward_ratio >= 0.42`
- `filt_combo` — `risk_reward_ratio >= 0.42 AND enrichment_quality_score <= 6.8`

| cohort | n (OOS) | best variant | OOS avg | OOS win% |
|---|---|---|---|---|
| baseline | 1552 (464) | 15:55 / tgt=none / stop=-20% / hold=3d | **−1.99%** | 19.6% |
| filt_rrr | 626 (155) | 15:55 / tgt=none / stop=-20% / hold=3d | **+8.28%** | 31.6% |
| filt_combo | 133 (34) | 15:30 / tgt=none / stop=-75% / hold=10d | **+50.64%** | 47.1% |

**Critical:** the bracket optimum did NOT shift dramatically under filtering — the same `15:55 / tgt=none / stop=-20% / hold=3d` is still best on filt_rrr. The filt_combo result is a 34-row OOS slice and should be treated with extreme suspicion. Both filter results were later disproven (see Bootstrap Validation below).

Source: `_archive/research_reports_2026-04/BRACKET_SWEEP_V2_FILTERED.md`.

---

## Premium-Score Validation

Honest validation of the load-bearing `premium_score` formula on the unconditioned cohort. The live ledger only ever sees `premium_score >= 2`; this table shows what every score level produces under the same simulator.

| premium_score | n | win rate | avg return | median |
|---|---|---|---|---|
| 0 | 1115 | 22.2% | **−3.84%** | −25.00% |
| 1 | 396 | 22.7% | **−2.48%** | −16.69% |
| 2 | 51 | 31.4% | **+3.77%** | −6.56% |
| 3 | 1 | 0.0% | −25.00% | −25.00% |

The score=2 row looks positive at +3.77%, but n=51 total / very few OOS — see filter-discovery section for the production filter result on the V1-best bracket.

### Production filter test (the smoking gun)

| filter | n | OOS n | OOS avg | OOS win% |
|---|---|---|---|---|
| ALL (no filter) | 1552 | 464 | **−1.99%** | 19.6% |
| **PRODUCTION** (`premium_score >= 2 AND is_tradeable`) | 46 | 7 | **−5.53%** | 14.3% |

**Production filter delta vs unfiltered: −3.54 percentage points worse.** The production filter is destroying edge.

### Premium component flags (`SIGNAL_FEATURE_DISCOVERY_V1` §3)

| flag | True n | True avg | False n | False avg |
|---|---|---|---|---|
| `premium_hedge` | 273 | −0.75% | 1290 | −3.79% |
| `premium_high_rr` | 170 | −0.93% | 1393 | −3.55% |
| `premium_high_atr` | 10 | −3.86% | 1553 | −3.26% |
| `premium_bull_flow` | 38 | **−6.72%** | 1525 | −3.18% |
| `premium_bear_flow` | 10 | −1.63% | 1553 | −3.27% |
| `is_premium_signal` | 448 | −1.82% | 1115 | −3.84% |
| `is_tradeable` | 46 | +2.32% | 1517 | −3.43% |
| `move_overdone` | 148 | −0.76% | 1415 | −3.52% |

`premium_hedge` and `premium_high_rr` are the only individually positive components. `premium_bull_flow` is **anti-predictive**.

### `direction` and `flow_intent`

| direction | n | win rate | avg |
|---|---|---|---|
| BEARISH | 820 | 23.7% | −1.90% |
| BULLISH | 743 | 21.4% | −4.76% |

| flow_intent | n | avg |
|---|---|---|
| MECHANICAL | 6 | +8.27% (n too small) |
| HEDGING | 273 | −0.75% |
| DIRECTIONAL | 1229 | −3.63% |
| MIXED | 55 | −8.70% |

### `premium_score = 1` structural analysis (Apr 1 2026 study, n=188 with vol≥250)

Earlier study comparing winners vs losers within score=1:
- Winners avg RSI 43.31, MACD hist −0.078; losers RSI 39.84, MACD hist −0.270 → **deeply oversold (RSI<40) signals mean-revert into the −25% stop**.
- Winners median `close_loc` 0.20, losers 0.23 → bearish winners close in bottom 20% of daily range (structural weakness).
- Winners avg ATR/price 5.7%, losers 6.2% → **high-beta underlyings (ATR > 6%) trip the −25% stop on intraday noise**.

This drove the original V6 "Structural Sniper" hypothesis: filter score=1 by `40 ≤ RSI ≤ 60`, `close_loc < 0.25` (bearish) or `> 0.75` (bullish), `atr_pct < 0.05`. The hypothesis was later partially tested via `XGBOOST_PATTERN_DISCOVERY_REPORT` and the raw tree logic produced **−3.76% avg, 33% win rate over 225 simulated executions** — negative expectancy out of sample. The structural framing remains a candidate but the simple gates do not work in isolation.

Sources: `_archive/research_reports_2026-04/SIGNAL_FEATURE_DISCOVERY_V1.md` §3-4, `_archive/research_reports_2026-04/PREMIUM_SCORE_1_STRUCTURAL_ANALYSIS.md`.

---

## Filter Discovery

### Univariate filter scan (~800 candidates)

Top 10 univariate filters by OOS avg_return on the V1-best bracket (`15:55 / no target / -20% stop / 3-day hold`), n-floor n≥100 total AND OOS n≥30:

| filter | n | OOS n | OOS avg | OOS win% |
|---|---|---|---|---|
| `move_overdone == True` | 148 | 31 | **+14.55%** | 35.5% |
| `dist_from_low <= 0.081` (q20) | 246 | 35 | **+11.31%** | 40.0% |
| `enrichment_quality_score <= 6.4` (q10) | 167 | 48 | **+10.12%** | 29.2% |
| `recommended_delta >= 0.498` (q90) | 156 | 48 | **+9.74%** | 31.2% |
| `catalyst_type == 'Technical Breakout'` | 212 | 60 | **+9.42%** | 23.3% |
| `call_vol_oi_ratio >= 0.796` (q90) | 156 | 52 | **+9.15%** | 28.8% |
| **`risk_reward_ratio >= 0.42`** (q60) | 626 | 155 | **+8.28%** | 31.6% |
| `recommended_delta >= 0.441` (q80) | 311 | 97 | **+7.54%** | 28.9% |
| `reversal_probability >= 0.65` (q90) | 195 | 48 | **+7.47%** | 29.2% |
| `underlying_price >= 379.7` (q90) | 156 | 38 | **+7.13%** | 21.1% |

### Bottom 10 univariate filters (anti-edge — what to AVOID)

| filter | n | OOS n | OOS avg | OOS win% |
|---|---|---|---|---|
| `recommended_delta <= −0.469` (q10) | 156 | 44 | **−13.92%** | 6.8% |
| `recommended_iv >= 0.998` (q90) | 155 | 32 | **−13.90%** | 9.4% |
| `recommended_delta <= −0.416` (q20) | 311 | 92 | **−13.68%** | 8.7% |
| `call_active_strikes >= 52.9` (q90) | 156 | 60 | **−13.64%** | 6.7% |
| `catalyst_type == 'Analyst Downgrade'` | 155 | 43 | **−13.20%** | 9.3% |
| `put_active_strikes >= 50` (q90) | 159 | 54 | **−13.05%** | 5.6% |
| `price_change_pct <= −5.659` (q10) | 156 | 59 | **−12.94%** | 11.9% |
| `macd <= −10.74` (q10) | 156 | 30 | **−12.27%** | 6.7% |
| `put_uoa_depth >= 1.01e8` (q90) | 156 | 32 | **−12.23%** | 6.2% |
| `catalyst_type == 'Guidance Cut'` | 113 | 32 | **−11.48%** | 12.5% |

### Top pairwise combinations

| filter | n | OOS n | OOS avg |
|---|---|---|---|
| `risk_reward_ratio >= 0.42` AND `enrichment_quality_score <= 6.8` | 133 | 34 | **+27.86%** |
| `enrichment_quality_score <= 6.8` AND `put_active_strikes <= 9` | 171 | 30 | **+26.53%** |
| `recommended_delta >= 0.441` AND `put_active_strikes <= 9` | 153 | 42 | **+25.93%** |
| `call_vol_oi_ratio >= 0.796` AND `put_active_strikes <= 9` | 106 | 30 | **+23.43%** |
| `enrichment_quality_score <= 6.8` AND `put_dollar_volume <= 2.49e6` | 126 | 33 | **+21.66%** |

⚠ **All of these are suspect for the same reason as `filt_rrr`** — small OOS samples concentrated in the regime-recovery window. Bootstrap before taking any of them seriously.

Source: `_archive/research_reports_2026-04/WINNING_FILTER_DISCOVERY_V1.md`.

---

## Dead-ends — option-PnL gate discovery (2026-06-05, workflow `wf_16b5c00d-347`)

Multi-agent fan-out over 8 feature families + walk-forward / day-block-bootstrap validation on the REAL option-PnL bracket-replay label (`analysis_option_pnl.parquet`, **N=1375 FILLED**, entry_day 2026-04-13…05-29, 33 days). Full-pool baseline mean `realized_ret = -0.0044` (win 0.413). **The only robust, leakage-clean, breadth-viable lever was DIRECTION** (bullish-only EV +0.0411 / win 0.470 / ~26 per day; bearish -0.0771) — and the owner declined to bake in bullish-only (the bearish penalty is almost certainly regime-conditional, untestable here: `vix3m_at_enrich` had near-zero variance 19.45–21.51, single 2026-Q1/Q2 war-chop window). Decision: keep all directions, shelve "exclude bearish" to an N≥15 live-cohort revisit; deploy the `overnight_score >= 4` floor only (**correction 2026-08-20: that floor never ran in production** — see the method caveats below). Everything below was tested as an EV gate and FAILED:

| # | Candidate gate | Verdict |
|---|---|---|
| 1 | Trend overlays (`above_sma_50/200`, `MACD>0`, `ema_21`) standalone | **DEAD.** Redundant with direction; ~+0.02 increment is day-block-bootstrap noise; goes negative in the recent third. |
| 2 | `vix3m_at_enrich <= 21.12` regime conditioner | **DEAD.** No variance in this data — it's a period selector, not a regime gate; the edge is 100% from kept null-vix rows in the first 5 days. |
| 3 | `moneyness_pct > 5%` OTM keep-null | **DEAD.** Null/recency artifact — strip the null trick and it falls below bullish-only; walk-forward inverts. |
| 4 | Catalyst-type exclusion | **DEAD.** Selection artifact; CI overlaps baseline; picked from 18-category dispersion (multiple comparisons). |
| 5 | `call+put_active_strikes >= 10` | **Not a gate.** Clean and NOT a recency artifact, but the increment over bullish-only is within day-block noise — best used as a tournament TIE-BREAKER, not a gate. |

**Method caveats:** thin (33 days, single regime); 76% of exits are TIMEOUT (3-day option drift dominates, the bracket rarely fires); mild liquidity-survivorship bias (INVALID_LIQUIDITY / CACHE_EMPTY dropped). PROPOSAL pending `gammarips-review` + N≥15 lock; only the `score >= 4` floor was decided for ship. **Correction 2026-08-20: the `>= 4` floor never ran in production.** The `deploy.sh` env pin `MIN_ENRICHMENT_SCORE=1` (set 2026-04-20) overrode the code default, and the env wins. The owner accepted the de-facto floor of 1 on 2026-08-20 — measured cosmetic (see §2026-07-28 (evening) — tradeability, and `docs/DECISIONS/2026-08-20-score-floor-accepted-print-floor-25-shipped.md`). Full context: `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`.

---

## Momentum lever + exploit falsification + pool-cap coverage (2026-06-19)

**Data:** frozen 1,375 FILLED option-PnL set (`analysis_option_pnl.parquet`) + new 686-ticker adjusted underlying daily-bar cache (`backtesting_and_research/cache/poly_daily_underlying/`, Dec2024–Jun2026). Bullish baseline +4.11% EV / 47.0% win (reproduced). Evaluated on OPTION PnL; `mom_60` anchored ≤ scan_date (leakage-safe); bootstrap 95% CIs (5000 resamples).

### Underlying momentum — REAL lever (SHIPPED 2026-06-19 as a soft edge-rank tilt)
- Quintile by trailing-N underlying return; Q5−Q1 spread POSITIVE at every N (no reversal anywhere): N=20 +11.9pp, 60 +7.7pp, 126 +10.5pp, 189 +6.8pp, 252 +9.4pp.
- **60-day top-quintile (`mom_60 ≥ +0.35`): ~+11.4% EV / 55.9% win; marginal lift over the bullish pool +8.4pp, CI clears zero.** Walk-forward (split 2026-05-04): H1 +16.9% / H2 +7.5%, both clear zero.
- Literal YoY (252d ≥ +50%): +5.45% in-sample, monotone in threshold, BUT marginal lift +1.6pp CI does NOT clear zero AND collapses out-of-sample (H2 −0.22%) → 60-day is the tradeable horizon, not YoY.
- Not redundant: corr(mom_60, overnight_score) = +0.29; high-mom beats low within every score stratum.
- Implementation: `docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`. Memory `project_momentum_60d_lever`.

### Recent-option-WINNER persistence — FALSIFIED (anti-edge)
- Recent winners underperform non-winners in every cell (whole-pool K=10: winners −2.5% vs non +0.3%; bullish K=5: winners −1.1% vs non +6.8%). In-pool ∩ recent-winner never beats the +4.11% baseline. 0/17 comparisons cleared zero in the exploit direction (< chance). Recent option winners MEAN-REVERT. The one stable cell pointed the OTHER way (buy recent losers; proxy-based, not promoted). Memory `project_exploit_winners_falsified`.

### Pool-cap coverage (ceiling test)
- Best-name capture vs full pool by edge-rank top-N: N=10 56% / 15 80% / 20 89% / **25 93.5%** / 50 100%. Ceiling-EV shortfall-vs-full CI touches zero only at N≥25. 50 almost never binds (4/46 days >50 candidates). → cap 50→25 safe on coverage; LLM-pick-quality untested (needs forward A/B). `docs/DECISIONS/2026-06-19-pool-cap-coverage.md`; memory `project_pool_cap_coverage`.

---

## Bootstrap Validation — the `filt_rrr` autopsy

Bootstrap CIs (5000 samples, RNG seed 42) on the `risk_reward_ratio >= 0.42` strategy under bracket `15:55 / no target / -20% stop / 3-day hold`.

### CIs on filtered cohort

| cohort | n | mean | p05 | p50 | p95 | P(>0) |
|---|---|---|---|---|---|---|
| filt_rrr full (train+OOS) | 626 | **−0.48%** | −3.37% | −0.54% | +2.66% | 0.390 |
| filt_rrr train only | 471 | **−3.37%** | −6.38% | −3.48% | −0.14% | 0.044 |
| **filt_rrr OOS only** | 155 | **+8.28%** | +0.73% | +7.95% | +16.66% | 0.968 |

### Comparison to baseline (same bracket)

| cohort | n | mean | p05 | p50 | p95 | P(>0) |
|---|---|---|---|---|---|---|
| baseline OOS (no filter) | 464 | −1.99% | −5.48% | −2.06% | +1.88% | 0.191 |
| **filt_rrr OOS** | 155 | +8.28% | +0.73% | +7.95% | +16.66% | 0.968 |

### Walk-forward stability — split OOS into halves

| OOS half | n | mean | p05 | p50 | p95 | P(>0) |
|---|---|---|---|---|---|---|
| **first half** | 77 | **−1.06%** | −7.43% | −1.07% | +5.94% | 0.401 |
| **second half** | 78 | **+17.51%** | +4.22% | +17.01% | +32.68% | 0.991 |

**Verdict (as written in the original report):** "MODERATE." But the walk-forward halving clearly disproves the edge:

- Train cohort: −3.37% (P(>0) = 4.4%)
- Full history: −0.48% (essentially breakeven)
- OOS first half: −1.06%
- OOS second half: +17.51%

The entire +8.28% OOS headline is driven by ~78 trades in the second half of OOS — which corresponds exactly to the **2026-03-26 → 2026-04-06 V-bottom recovery from the Iran shock** (see Regime Context below). This is a regime artifact, not an edge.

Source: `_archive/research_reports_2026-04/FILT_RRR_BOOTSTRAP_V1.md`.

---

## Univariate Feature Quintiles (top 15 by separation)

From `SIGNAL_FEATURE_DISCOVERY_V1` §2. Features ranked by separation (max-bucket avg − min-bucket avg) on the executed cohort (n=1563, V3 mechanics, win threshold ≥+35%).

| rank | feature | separation | monotonicity |
|---|---|---|---|
| 1 | `reversal_probability` | +6.97% | 0.50 |
| 2 | `recommended_delta` | +6.69% | 0.50 |
| 3 | `risk_reward_ratio` | +6.24% | 0.00 |
| 4 | `macd_hist` | +5.97% | 0.00 |
| 5 | `call_active_strikes` | +5.86% | 0.00 |
| 6 | `close_loc` | +5.80% | 0.00 |
| 7 | `recommended_volume` | +5.69% | **1.00** |
| 8 | `recommended_spread_pct` | +5.43% | 0.00 |
| 9 | `rsi_14` | +5.42% | 0.50 |
| 10 | `macd` | +5.20% | 0.00 |
| 11 | `mean_reversion_risk` | +5.13% | 0.50 |
| 12 | `call_vol_oi_ratio` | +5.09% | 0.00 |
| 13 | `catalyst_score` | +5.06% | 0.33 |
| 14 | `dist_from_high` | +5.01% | 0.00 |
| 15 | `recommended_oi` | +4.81% | **1.00** |

Two cleanly monotonic features: `recommended_volume` (worse with higher volume) and `recommended_oi` (worse with higher OI). Both **negatively correlated** with returns — i.e. the system bleeds more on the most-liquid contracts. This is the opposite of what a naive liquidity-gating intuition predicts.

### `recommended_oi` quintile breakdown (the monotonic loser)

| bucket | n | win rate | avg |
|---|---|---|---|
| (0, 2] | 332 | 23.2% | −0.74% |
| (2, 16] | 297 | 22.2% | −1.97% |
| (16, 96] | 310 | 24.2% | −2.77% |
| (96, 776] | 311 | 19.9% | −5.39% |
| (776, 92920] | 313 | 23.3% | **−5.55%** |

### `recommended_volume` quintile breakdown

| bucket | n | win rate | avg |
|---|---|---|---|
| (10, 28] | 317 | 22.4% | +0.29% |
| (28, 125] | 309 | 22.3% | −2.47% |
| (125, 509] | 312 | 21.8% | −4.21% |
| (509, 2050] | 312 | 22.4% | −4.57% |
| (2050, 43234] | 313 | 24.0% | **−5.40%** |

The "high-volume contract is overpriced" interpretation lines up cleanly with the volatility-idiosyncratic-trap thesis from the Deep Research strategy report.

Source: `_archive/research_reports_2026-04/SIGNAL_FEATURE_DISCOVERY_V1.md` §2.

---

## Tree-Based Feature Importance

### GBM, chronological holdout (signals_labeled_v1)

`GradientBoostingRegressor(n_estimators=200, max_depth=3, lr=0.05, seed=42)`

- Train: 1094 rows (scan_date 2026-02-18 → 2026-03-19)
- Test: 469 rows (scan_date 2026-03-19 → 2026-03-31)
- In-sample R²: +0.4366
- **Out-of-sample R²: −0.0656**
- OOS Spearman ρ: +0.0398

Top 15 features by GBM importance:

| rank | feature | importance |
|---|---|---|
| 1 | `recommended_delta` | 0.0871 |
| 2 | `price_change_pct` | 0.0598 |
| 3 | `rsi_14` | 0.0585 |
| 4 | `risk_reward_ratio` | 0.0567 |
| 5 | `contract_score` | 0.0448 |
| 6 | `macd_hist` | 0.0445 |
| 7 | `recommended_volume` | 0.0438 |
| 8 | `atr_normalized_move` | 0.0388 |
| 9 | `call_dollar_volume` | 0.0345 |
| 10 | `recommended_mid_price` | 0.0328 |
| 11 | `dist_from_high` | 0.0313 |
| 12 | `recommended_spread_pct` | 0.0298 |
| 13 | `recommended_iv` | 0.0269 |
| 14 | `call_active_strikes` | 0.0260 |
| 15 | `recommended_oi` | 0.0258 |

**Features in both top-10 GBM importance AND top-15 univariate separation** (the "real signal" candidates):

- `recommended_delta`
- `rsi_14`
- `risk_reward_ratio`
- `macd_hist`
- `recommended_volume`

OOS R² of −0.07 means the model has **no out-of-sample predictive power** on returns. These features point at directions, but they don't predict magnitude.

### Shallow decision tree (depth 3, full data)

```
|--- risk_reward_ratio <= 0.425
|   |--- recommended_oi <= 12.500
|   |   |--- recommended_volume <= 266.000  → +0.005
|   |   |--- recommended_volume >  266.000  → −0.109
|   |--- recommended_oi >  12.500
|   |   |--- put_vol_oi_ratio <= 0.068      → +0.119
|   |   |--- put_vol_oi_ratio >  0.068      → −0.085
|--- risk_reward_ratio >  0.425
|   |--- call_uoa_depth <= 212698
|   |   |--- close_loc <= 0.296             → +0.219
|   |   |--- close_loc >  0.296             → +0.068
|   |--- call_uoa_depth >  212698
|   |   |--- call_dollar_volume <= 8.97e7   → −0.010
|   |   |--- call_dollar_volume >  8.97e7   → −0.123
```

### Earlier xgboost study on V3 forward ledger (n=26, severely overfit)

Random forest top features on a 26-trade V3 forward ledger sample (the dataset is far too small to generalize):

1. `recommended_dte` (0.1918)
2. `recommended_iv` (0.1246)
3. `dist_from_high` (0.0977)
4. `recommended_volume` (0.0939)
5. `atr_14` (0.0918)
6. `rsi_14` (0.0868)

The "Structural Sniper" tree branch `recommended_dte <= 28.5 AND rsi_14 <= 53.0` showed 80% in-sample win rate on n=10 — pure overfit. Tested out-of-sample on 225 signals: **33.3% win rate, −3.76% avg return**. Negative expectancy. Do not use the raw tree logic.

Sources: `_archive/research_reports_2026-04/SIGNAL_FEATURE_DISCOVERY_V1.md` §5, `_archive/research_reports_2026-04/XGBOOST_PATTERN_DISCOVERY_REPORT.md`.

---

## Liquidity Findings

### Liquidity-gated subcohorts on V1-best bracket

| filter | n | avg | win% |
|---|---|---|---|
| ALL (no filter) | 1552 | −2.15% | 21.3% |
| `oi >= 50` | 740 | −3.55% | 19.5% |
| `oi >= 100` | 616 | **−5.89%** | 17.9% |
| `oi >= 50 AND vol >= 100` | 657 | −3.00% | 19.5% |
| `mid_price >= 1.00` | 1309 | −2.60% | 21.5% |
| `spread_pct <= 0.20` | 735 | −0.08% | 24.6% |
| `oi>=50 AND vol>=100 AND mid>=1 AND spread<=0.20` | 114 | **+0.96%** | 26.3% |

The full liquidity-stack lifts the cohort from −2.15% to **breakeven (+0.96%)** on n=114. Confirms that *some* of the "edge" in the wider cohort is simulator-artifact wins on un-fillable contracts. But: still not profitable, just less negative.

### Picker NULL rate

`recommended_strike` is NULL for **41.6%** of `overnight_signals_enriched` rows in the broader population. The labeled cohort filters those out, but it's a known structural issue tracked in `docs/DECISIONS/2026-04-07-v3-1-liquidity-quality-gate.md`.

### Earlier upstream-liquidity sweep (small-cohort, pre-Iran)

From the older `UPSTREAM_LIQUIDITY_REPORT` (premium_score≥2 cohort, n=45 base, 15:00 ET entry, +40/−25/3D bracket):

| Gate | Pass count | Realized win | Realized stop | **Realized EV** |
|---|---|---|---|---|
| `V>25 \| OI>50` | 19 valid | 52.6% | 31.6% | **+12.59%** |
| `V>100 \| OI>250` | 17 valid | 47.1% | 35.3% | **+9.37%** |

This was the original justification for the V3 production filter `recommended_volume >= 100 OR recommended_oi >= 250`. The +12% / +9% EV was measured on tiny n in a different (pre-Iran) regime and does not reproduce on the larger 1552-trade cohort.

Sources: `_archive/research_reports_2026-04/BRACKET_SWEEP_V1.md` §5, `_archive/research_reports_2026-04/UPSTREAM_LIQUIDITY_REPORT.md`.

---

## Execution Mechanics

### Intraday robustness sweep (pre-Iran cohort, small n)

From `ROBUSTNESS_SWEEP_REPORT`. Top configurations (Base scenario, 2% entry slippage):

| Cohort | Entry | Target | Stop | Hold | Win | Stop | EV |
|---|---|---|---|---|---|---|---|
| HEDGE_HIGH_RR | 15:00 | +50% | −40% | 3D | 42.8% | 14.2% | **+14.89%** (n=14) |
| HEDGE_HIGH_RR | 15:00 | +40% | −40% | 3D | 50.0% | 14.2% | **+12.88%** (n=14) |
| **SCORE_GTE_2** | **15:00** | **+40%** | **−25%** | **3D** | **52.6%** | **31.5%** | **+12.59%** (n=19) |
| HEDGE_HIGH_RR | 15:00 | +40% | −25% | 3D | 50.0% | 28.5% | +12.09% (n=14) |

#### Key findings from this earlier study

- **Morning entries (09:45 → 11:00) all have negative or near-zero EV** (range −8.5% to +1.5%). Stop-out rate at 09:45 is over 50%.
- **Tight targets (+15-20%) destroy edge.** Required asymmetry forces +35-40% targets.
- **1-day holds are catastrophic** (−7% to −8% EV). Setup needs 2-3 days to develop.
- **Widening the stop improves EV.** Moving from −25% to −40% stop dropped stop-out rate from 28.5% → 14.2% and increased EV +12.0% → +12.8%.
- **Stress scenario (5% entry slippage + 5% timeout penalty):** the 15:00/+40/−25/3D config retained **+6.6% EV**.

⚠ This entire study used pre-Iran small-n cohorts. The Feb-Apr 2026 sweeps (`BRACKET_SWEEP_V1`) directly contradict every positive number above. The contradiction is the regime — the same mechanics that produced +12.59% EV on n=19 pre-Iran produced −1.99% on n=464 inside the Iran window.

### Monte Carlo simulation parameters (proposed)

From `MONTE_CARLO_UPDATE_PLAN`. The proposed distribution was based on the SCORE_GTE_2 cohort entering at 15:00 ET with +40/−25:

- Target hits: 52.6% → +40%
- Stop hits: 31.5% → −25%
- Timeouts: 15.9% → ~+5% or 0%
- EV per trade: +12.6%
- Account: $2,500 start, runway/harvest phases, 8 trades/month, 10,000 sim lifetimes

⚠ These parameters are derived from the same pre-Iran small-n cohort and **should not be used for production sizing**. Update with current dataset distributions before any Monte Carlo work.

Source: `_archive/research_reports_2026-04/INTRADAY_SIMULATION_PLAN.md`, `_archive/research_reports_2026-04/MONTE_CARLO_UPDATE_PLAN.md`, `_archive/research_reports_2026-04/ROBUSTNESS_SWEEP_REPORT.md`.

---

## Scoring v2 spec (`SPEC-SCORING-V2`)

Forward-looking spec for a regime-aware execution policy. **Not yet implemented in production.** Key elements preserved here for the strategy-design pass:

### Eligibility rules (upstream)
- `premium_score >= 2`
- `direction == 'BEARISH'` (current iteration optimized for bearish flow)
- `recommended_volume >= 100 OR recommended_oi >= 250`

### Skip conditions (regime gates)
- `VIX > 25.0` at entry → SKIP
- `recommended_dte < 14` → SKIP

### Execution rules
- Entry: 15:00 ET, +2% slippage
- Target: +40%, Stop: −25%, Hold: 3 trading days
- Intrabar tie: stop wins

### Logging requirements
Forward paper ledger must include `is_skipped`, `skip_reason`, `VIX_at_entry`, `SPY_trend_state`, full execution columns. Skipped trades MUST be logged.

### Validation protocol
- 30 forward paper trades OR 30 calendar days, whichever later
- Frozen policy during validation window
- No loosening of filters or bracket tweaking

**Status as written:** Live capital NO. Production NO. Forward paper YES. The spec was the basis for the V3 forward paper trader (V3 retired 2026-04-16). The Iran-window data has invalidated the EV numbers used to justify it; the architectural framework (eligibility / skip / execution / logging separation) remains useful as a template for any regime-aware v2.

Source: `_archive/research_reports_2026-04/SPEC-SCORING-V2.md`.

---

## Regime Context (Feb–Apr 2026)

The labeled cohort sits inside one of the most hostile windows in modern history for long options. Source: external Deep Research report #2 (preserved in `handoffs/2026-04-08-deep-research-2-regime.md` as the prompt; full output should be saved alongside).

### Timeline of major events

| Date | Event | Effect |
|---|---|---|
| 2026-02-28 | **Operation Epic Fury** — US/Israeli strikes on Iran nuclear and missile sites | Initial shock, vol spike |
| 2026-03-04 | **Strait of Hormuz closure** | Largest oil supply disruption per IEA; Brent → $120/bbl, Asian LNG +140% |
| 2026-03-18 → 25 | **6-session chop window** | No directional follow-through, alternating ± days |
| 2026-03-26 → 04-06 | **V-bottom recovery** | The window the `filt_rrr` "edge" rode |
| 2026-03-31 | **Single-day +2.91% reversal** | Largest move of the year, came right after a 3-day bearish flush |
| 2026-04-07 → 08 | **Ceasefire signals** | At the very end of the data window |

### Regime metrics

- VIX peak: **35.3**, average: **25.4** (vs ~16 in late 2025)
- VVIX peak: **141**
- SKEW: **147.6**
- IV–RV spread: **~9 points** (IV ~23%, RV ~14%) — **3× normal**, record-high vega tax on every long-option position
- VIX term structure: **BACKWARDATION** in March (extremely rare; signals acute panic; predicts mean-reverting V-rallies, not sustained trends)

### Implications for the dataset

- **Regime-confounded.** Every numeric finding in this ledger is conditional on this regime. The Iran shock + record VRP almost certainly explains the entire option-side P&L gap independent of any signal-quality issues.
- **The `filt_rrr` recency artifact is fully explained.** The +17.51% second-half OOS corresponds exactly to the V-bottom recovery window. It is not an edge — the cohort rode the largest single-day reversal of the year.
- **Cannot conclude the signal generator is broken from this cohort alone.** Need either (a) underlying-relabel + SPY benchmark to isolate signal alpha from regime drift, or (b) a pre-Iran historical relabel for comparison.

### What we were doing on the wrong side of the trade

1. Buying overpriced volatility on high-IVOL stocks (volatility-idiosyncratic trap, Cao & Han 2013)
2. In a regime where the entire market's VRP was ~9 points (~3× normal)
3. At the entry time (15:00 ET) most likely to miss post-gap momentum and catch IV mean-reversion
4. With +40%/−25%/2-day brackets that cannot survive even a single chop window
5. Filtered to the highest-premium-score signals — exactly the most overpriced options
6. In the same 6-week window as the largest geopolitical shock since 2022

It is not surprising the strategy lost money. It is surprising the loss is not catastrophic. The least-bad bracket holding at −1.99% under these conditions is actually evidence that there *is* signal underneath — the question is whether a different instrument can capture it.

Source: `handoffs/2026-04-08-deep-research-2-regime.md` (prompt) and the external Deep Research output that should be saved alongside.

---

## Reading list (Deep Research surfaced)

- **Cao & Han (2013), JFE** — "Cross-section of option returns and idiosyncratic stock volatility" — the volatility-idiosyncratic trap
- **Goyal & Saretto (2009)** — option return predictability via IV-RV spread
- **Sinclair, "Positional Option Trading" (2020)** — practitioner reference for instrument choice on directional reads
- **Bailey & López de Prado (2014)** — Deflated Sharpe Ratio; directly addresses our 840-variant overfitting concern
- **GEX literature** — Squeezemetrics, dealer gamma exposure as a regime classifier

---

## Source mapping (originals → ledger sections)

| Original report | Sections in this ledger |
|---|---|
| `BRACKET_SWEEP_V1.md` | Bracket Sweeps §V1, Liquidity Findings, Premium-Score |
| `BRACKET_SWEEP_V2_FILTERED.md` | Bracket Sweeps §V2 |
| `WINNING_FILTER_DISCOVERY_V1.md` | Filter Discovery |
| `FILT_RRR_BOOTSTRAP_V1.md` | Bootstrap Validation |
| `SIGNAL_FEATURE_DISCOVERY_V1.md` | Cohort, Premium-Score, Univariate Quintiles, Tree-Based Importance |
| `XGBOOST_PATTERN_DISCOVERY_REPORT.md` | Tree-Based Importance §earlier study |
| `PREMIUM_SCORE_1_STRUCTURAL_ANALYSIS.md` | Premium-Score §structural |
| `INTRADAY_SIMULATION_PLAN.md` | Execution Mechanics §intraday |
| `MONTE_CARLO_UPDATE_PLAN.md` | Execution Mechanics §monte carlo |
| `ROBUSTNESS_SWEEP_REPORT.md` | Execution Mechanics §robustness |
| `UPSTREAM_LIQUIDITY_REPORT.md` | Liquidity Findings §upstream |
| `SPEC-SCORING-V2.md` | Scoring v2 spec |

---

## 2026-06-22 — Entry-timing (10:00 ET vs earlier): RESOLVED — thin-tape mirage, KEEP 10:00

Tested whether the fixed 10:00 ET entry systematically bleeds vs an earlier fill (prompted by TTWO 06-22 buying the morning pop and round-tripping). Re-simulated the identical V7 GIGO bracket (+40% TP / −30% stop / 15:45 flat) from open(9:30)/9:45/10:00/VWAP entries on the option-premium path.

- **Substrate:** `enriched_option_outcomes` (46 days, 04-13..06-18) ⨝ fetched 1-min OPTION bars (2,694 contract-days). Scripts: `backtesting_and_research/entry_timing_backtest.py` + `entry_timing_fill_realism.py`. Sim validated vs production `realized_return_pct` (corr **0.922**). Leakage-safe (varies execution time only).
- **Gross signal (real but not capturable):** 10:00 is the WORST entry tested; open beats it **+7.0pp** (paired, day-clustered CI [+2.1,+11.5], walk-forward stable; N=315/25d), 9:45 +3.4pp. Mechanism: at 10:00 you buy after the AM pop → TP-hit 13% vs 30%, timeout 48% vs 37%.
- **Fill-realism KILLS it.** No NBBO on this Polygon plan → spread estimated from OHLC. Corwin-Schultz unreliable (trade-print bars understate spread → ~11bps, not credible). Under the model-free **adverse-bar fill** (buy entry-bar high / sell exit-bar low), in the **LIQUID subset (n_bars≥120, N=55 — the tradeable names): open Δ=+0.6% [−0.10,+0.10]; 9:45 negative, CI incl 0.** The edge lives ENTIRELY in illiquid contracts (median 66 traded min/session of 390; 77% <120 bars) where the early "fill price" isn't real.
- **Decision:** do NOT change the live 10:00 entry. TTWO 06-22 was variance. Caveat: liquid N=55 + single regime → "no liquid edge" itself underpowered, but the thin-vs-liquid asymmetry is the tell; burden of proof was on the edge and it didn't clear. Memory: `project_entry_timing_1000_bleeds`.

---

## 2026-07-06 — ITM-at-expiration vs delta null: NO DIRECTIONAL EDGE (pre-committed H1 rejected); hold-to-exp floor is tail-dependent

Trader-independent pool ROI study (read-only; scripts `.scratch/retro_itm_*.py`, extract cached in session scratchpad). Substrate: `enriched_option_outcomes` (3,094 rows, verified unique, all BULLISH calls) ⨝ `underlying_daily_bars` (max session 2026-07-01). Contract identity from structured strike/expiration columns, validated 0-mismatch vs OCC parse.

### Universe / exclusions
Expired (exp ≤ 07-01): 2,149 of 3,094 (945 not yet expired). Metric-A universe 2,146 per-signal / 1,896 unique (1 halted ticker, 2 NULL delta; fallback prior-close used 3×). Entry-priced (B/C) universe 1,316 / 1,237 (830 lack `opp_entry_price`: NO_BARS 762, NO_POST_ENTRY_BARS 68 — the illiquid tail; ITM% differs only 41.3→40.0 between universes, so selection bias on A is small). Data bug: 41 rows with `recommended_delta`≈0.0 on ITM-at-scan contracts (impossible; missing-delta-as-zero).

### A. ITM% vs delta null (δ = scan-time `recommended_delta`, leakage-safe)
| Variant | N | ITM% | mean δ | ITM−δ | p |
|---|---|---|---|---|---|
| Per-signal | 2,146 | 41.29% [39.2,43.4] | .4207 | −0.8pp | p(≥obs)=.787 |
| Per-unique | 1,896 | 40.72% | .4165 | −0.9pp | .814 |
| Cleaned δ≥0.05, per-signal | 2,105 | 40.95% | .4287 | **−1.9pp** | p(≤obs)=.031 |
Null = Poisson-binomial on per-contract δ. Bucket calibration near-perfect: δ 0.2–0.46 N=878 ITM 35.2% vs .365; δ 0.46+ N=380 52.4% vs .547; cleaned low-δ N=106 11.3% vs .123. Months: Apr +4.7pp / May −2.0pp / Jun −3.3pp (noise). Era: pre-06-12 +0.5pp; post-06-12 N=68 −21pp but UNSTABLE (short-DTE, one fortnight, structurally truncated — re-run ≥200 expired era rows, ~mid-Aug). Since N(d1) > P(ITM)=N(d2) by ~3–5pp at pool IV/DTE, ITM≈δ−2pp ≈ zero risk-neutral edge.

### B/C. Beyond-breakeven & floor ROI (hold-to-expiry intrinsic, option PnL, N=1,316)
Beyond-breakeven 28.0% [25.7,30.5]. Floor ROI: mean +15.6% (bootstrap [+1.2,+31.3]) but median −100%, 60.0% expire worthless, p75 +27.2%, p90 +266%, max +3,893% (TLN 420C). Mean minus top-1/5/10/25 trades: +12.7/+4.9/−0.6/−12.0%. Months: Apr +57.5% / May −1.3% / Jun −0.1%; halves +39.5% → −8.3%. No fill friction included; real-money floor lower. Verified the moonshot bars are genuine (no split/discontinuity artifacts).

### Verdict & rules
The scanner surfaces FAIRLY-PRICED contracts: realized ITM converts at the market-implied rate even in a max-bullish regime. Do NOT publish "beats market odds" ITM claims or the floor mean (top-10-trade- and single-month-dependent). Product framing stands: curation + opportunity surface; exit is the free variable; ROI lives in the trading layer. Ceiling (through-expiry MFE) unmeasured — requires the to-expiration follow collector (`opp_window_days`=3 everywhere today).

---

## 2026-07-06 — Excursion path vs entry-IV null (retro #2): PATH-CALIBRATED too; the GIVEBACK is the real finding

Companion to the ITM-vs-delta study (same universe, N=1,303 entry-priced expired calls, delta≥0.05; scripts `.scratch/retro_excursion_*.py`; intrinsic-bound peaks from underlying daily HIGHs vs per-contract GBM(σ=recommended_iv, μ=0, B=2,000, Brownian-bridge highs) nulls; percentile-PIT method).

- **H1 FATNESS (realized peaks fatter than entry-IV-implied) — REJECTED at the mean.** Mean implied-percentile of realized peak **0.5095** (clustered 95% CI [0.489, 0.529] — straddles 0.5); KS vs uniform p=0.50. Raw surface is huge (peak p90 +445%, P(peak≥+100%)=36.1%) but implied says 35.5% — **exactly as fat as IV priced**. Pre-registered tail check nominally passes (13.7% ≥ own implied p90 vs 10%) but decays Apr 17.2% → Jun 10.4% (second WF half 10.7% = null) — regime, not structure. Only texture: DTE 22–45d tail 19.5% (post-hoc, directionally persistent across halves, underpowered).
- **H2 SHARPNESS (peaks arrive earlier than the timing null) — NOT SUPPORTED on the bound.** Mean timing percentile 0.5096 [0.478, 0.541]; halves contradict (0.554 late / 0.460 early). Raw: median days-to-peak **7 of a 10-day life** (back third, as a driftless max-process implies); P(peak ≤3 td)=19.5% vs implied 19.0%. CAVEAT: intrinsic bound late-biases true option-price peaks (theta/vega) → H2 is INCONCLUSIVE for option prices, refuted only for underlying paths. Needs the to-expiration follow collector (GAP-002/RM-002).
- **G GIVEBACK — the finding.** Median giveback (peak−terminal) +60 ROI pts; conditional on peak ≥+50% (N=571): median +155 pts, median share of peak retained at expiry **31%**, 37.8% round-trip to a LOSS; across all ever-profitable contracts **48.5% die at a loss at expiry**. Direct quantitative support for surface+discretionary-exit: the pool reliably produces large touchable peaks and holding surrenders ~70–90% of them.
- **Verdict:** the pool IS the positive right-skewed big-peak distribution the owner wants — and it is precisely the distribution its own IV prices (neither fatter nor earlier). Sellable, verified facts = curation + the giveback numbers, NOT an IV-beating anomaly. Do not publish "excursions beat IV". Drift/robustness: μ=4%/yr immaterial; per-unique identical; entry-day post-10:00 excluded both legs (5.3% day-0-peak contamination noted).

---

## 2026-07-06 — 3-day harvest-curve study (retro #3): the pop is real but LATE and not rule-able; tournament picks are the one positive-EV lead (N=24)

Owner hypothesis (pre-committed): "enter 10:00 day-1, harvest your own target within 3 days, strongest on tournament/tilted names." Data: `enriched_option_outcomes` opportunity surface (REAL option minute bars, 3-trading-day window incl. entry day, touch-based bar-high MFE off a realistic 10:00 fill +2%; semantics verified in `_simulate_opportunity_surface`). N=2,029 OK rows (scans 04-10→06-26; 880 NO_BARS + 85 NO_POST_ENTRY + 100 PENDING-BACKFILL excluded). Scripts `.scratch/retro_harvest_*.py`.

- **Harvest curve (pool):** P(touch +15%)=55.0%, +20%=51.0% [48.8,53.2], +50%=30.7%, +100%=13.7%, +200%=3.7%; median peak +21.0%, p90 +122%. Real surface, coin-flip reliability.
- **Timing:** meaningful pops are LATE — given peak≥+20%: day-1 14.8% / day-2 33.1% / day-3 52.1% (≥+50%: day-3 63.7%). Only 9.1% of the pool clears +15% on day 1. Day-1 global peaks are mostly dead contracts (median +3.6%). Day-3-heaviness suggests the 3-day window truncates the surface (collector). "A few hours from entry" = the exception, not the pattern.
- **Fixed-target rule EV (limit +X% else window-end; exact for X≤80): NEGATIVE at every X** — −8.2% @+15, −7.2% @+20, −4.1% @+50, −2.4% @+80 (conservative fill-pad variant worse). Monotonically improving in X: cheap targets amputate the tail that pays for the ~half that never pops (E[terminal|no fill] ≈ −30 to −37%). Stop-risk: **P(trough≤−30%)=50.6%** (67.6% post-06-12); trough≤−60%: 22.2%.
- **Cohorts:** tilt (mom_60≥.35∧band) lifts touch rates (+20%: +9.3pt [4.5,14.1]) but FAILS walk-forward at +50% (H2 −0.6pt) — regime, consistent with the known mom_60 fragility. **Tournament picks (N=24, all eras): the ONLY cohort with positive rule EV (+11.0% @X=75–80; hold-to-window-end mean +10.3%, WR 54.2%)** — but pick-vs-pool touch deltas' CIs span zero; V7.1-era picks N=2. A lead to accrue toward N≥30, not a result.
- **Anecdote grounding (owner's "star killers"):** FCEL 06-24 peaked **+1,234%** (day 3) but the live same-day GIGO exit realized **−47.8%** on that very path — the sharpest recorded proof that the exit, not the pick, is the problem. FCEL 06-26 pick +137% (day 2), PANW 06-25 +268% (day 3), U 06-26 +88.7% (day 3, after −28% trough). All peaked day 2–3; none "hours in." V 07-06 not yet recorded anywhere.
- **Ops follow-ups:** (a) opp backfill PENDING for scans 06-29/06-30 (100 rows, windows now closed — run the gated backfill); (b) 7 tournament-pick rows have NO labels at all (NO_BARS) — engineer look; (c) researcher read `forward_paper_ledger` read-only for pick membership (explicitly directed, flagged per role rules).
- **Verdict: half-supported.** The surface exists and is worth selling WITH the risk side attached; no "harvest at +X%" claim or policy may ship; the honest personal-trading read: expect −30% drawdowns on half of paths, expect the pop on day 2–3 if it comes, and let the pick cohort accrue N before believing the +10% pick EV.

---

## 2026-07-28 — Pool-of-50 composition hunt (workflow `wf_e301233a-c66`): mom_60 tilt retire-grade; delta CEILING is the only validated rank component; pool has zero underlying alpha; surface labeler dark since 06-26

Six pre-committed hypothesis families on pool composition/ordering; every claimed signal adversarially verified by 2 independent lenses (leakage/regime + independent stats recompute). Substrate: `enriched_option_outcomes` N=3,944 (scans 04-10..07-24, 71 days; GIGO-valid 2,993 — 24.1% INVALID_LIQUIDITY excluded, era-skewed Apr 41% → Jul 8%), opp-surface-valid 2,029 (labels END 06-26), `overnight_signals_enriched` join 100%, `polygon_iv_history` (04-08+), `pool_liquidity_snapshot` (07-07+, 15 scan days).

### Verified actionable
1. **mom_60 +1.25 edge-rank tilt: RETIRE-GRADE (confirmed + strengthened by verification).** IS(<06-02) GIGO +2.90pp [+0.90,+4.97] flips OOS −2.55pp [−6.42,+1.28]; day-matched OOS −2.9pp; under the schema-correct `illiquid_exit` exclusion −3.80pp CI[−7.47,−0.03] significantly negative. Surface OOS +0.5pp (zero). Live cohort −3.1pp. Second lens caveat: H1 ex-policy-week mom was GOOD (+3.0pp) → regime-flipping, not robustly ANTI — but not earning its weight either. Since ~06-15 the delta band covers 100% of the pool → mom_60 is the ONLY active ordering ingredient: the published order encodes a dead lever.
2. **Delta band: the validated content is the 0.46 CEILING, on the surface only.** Day-matched P(opp_peak≥+40%) +9.3pp [+2.1,+16.4] (41 contrast days); survives leave-one-ticker-out, within-ticker contrast (+8.1pp [+1.7,+14.4]), all 9 neighboring bin edges, top-5 tail removal. Refinements from verification: off-band is 88% delta>0.46 → real claim is in-band vs >0.46 = +10.9pp*; the 0.20 floor is UNVALIDATED (n=61 ns); partly mechanical %-vol leverage (P40 monotone in |delta|: 42.7% @0.20-0.28 → 18.3% @0.60+); GIGO effect zero; only evaluable through ~06-10 (labeler stall); drops to +7.6pp ns without May.
3. **The 50-cap ALWAYS binds now (structural, verified).** Capped era (06-11+): pre-cap BULLISH candidates min 63 / median 139 / max 242 vs cap 50 — 0/30 days slack, ~2.8× oversubscription. SUPERSEDES the 06-19 "cap almost never binds" coverage note. The 139→50 selection is the real composition lever and currently runs on the dead mom ordering.
4. **Pool underlyings have ZERO alpha vs SPY (verified).** Full −0.11pp/trade [−0.28,+0.04] (N=2,993/71d); live cohort ≥06-26 −0.27pp [−0.52,−0.01]; monthly Apr +0.14 / May +0.22 / Jun −0.19 / Jul −0.34. Clean non-illiquid subsample consistent. Clean GIGO option bleed −7.2pp is mostly NOT underlying drag → vol pricing/theta/bracket asymmetry.
5. **GIGO losses are SELECTION kills, not noise kills (verified).** P(entry-day green close | STOP) = 9.5% [6.4,15.3] (N=346 stops); ~85% of lost dollars from names that genuinely fell; green-loss share FELL H1→H2 (recent regime MORE selection-driven). Better underlying selection, not execution tuning, is the binding constraint.
6. **~53% of the published 50 fails the live-OI≥1000 floor at pick time** (15 snapshot days). OI-build (Δ next-morning OI / scan volume) does NOT predict returns (NULL, leaning anti) but strongly predicts tradability: INVALID_LIQUIDITY 21.5% (OI flat/down) vs 3.0% (OI up), +18.5pp [+13.8,+23.1], stable in every window split. Product implication: a tradability flag/filter on the published pool is justified by fillability, not PnL.

### Nulls / refuted / anti (verified)
- **Re-selection persistence (streak≥2): REFUTED by both lenses** — +3.8pp collapses to +0.25pp removing 5 tickers' repeat rows; H2-only; within-day permutation p=0.32. NULL.
- **Pool breadth / dynamic cap: NULL + moot** (cap always binds; era-confounded thin-day pattern). **Crowding: NULL** (SPY-beta + era3 dummy absorb it; contemporaneous metric anyway).
- **IV-richness: NULL both directions.** Scan-anchored IV rank/percentile and IV-vs-HV (Goyal-Saretto style) all flat on GIGO + surface. Cao-Han cheap-vol preference unsupported on this pool. Absolute `recommended_iv`≥q90 junk-tail: trough −10pp directionally bad but ATR-confounded (corr +0.85) — defensive-trim-grade only, no gate.
- **DTE 22–45d "fatter tail" (07-06 hint): ANTI.** Short DTE ≤10 carries the surface (P40 44.7% vs 27.6%; p90 peak 163% vs 87%, CIs non-overlapping) at symmetric risk (median trough −54.2% vs −24.4%) = gamma leverage, not edge; ≤10d is a bracket-exit drag (STOP 36.9%, GIGO −9.7%). 22-45d carries survivability (TIMEOUT 90%). Bands serve different consumers → tag on the published pool, never gate.
- **Active-strikes ≥10: NULL at 2.5× N** — volatility widener (P40 +4.0pp ns, trough −7.5pp*, GIGO consistently negative). **Catalyst mid-band 0.5-0.8: NULL** (+1.1pp ns, post-06-12-only pattern — the "fragile-conditional" doctrine tag is now "unsupported as gate"). **put_uoa_depth q90 anti-edge: did NOT reproduce** (−1.0pp vs old −12%; small-N artifact).
- **Dip-preference (scan-day move <0 beats gappers): WEAKENED to watch-item.** Full-period +4.0pp GIGO vs up-moves 0-15%, but ~72% of it is the 06-08..06-14 policy-transition week; ex-week +1.2pp [−1.2,+3.7]; surface advantage ex-week none. Sign-consistent 4/4 months (p=0.065) — accrue, don't ship.

### Leakage / data discoveries
- **`iv_rank_entry` / `iv_percentile_entry` are POST-ENTRY CONTAMINATED.** Computed at label time (17:00 ET) with `as_of_date <= entry_day` against the polygon-iv-cache written 16:30 ET close — "current IV" post-dates the 10:00 entry by ~6h on a same-day-exit trade. Their apparent "rich vol is better" effect (+9.1pp P40) is the label echoing itself; the scan-anchored construct is null. Code: `forward-paper-trader/benchmark_context.py:488-513` + scheduler timings. `hv_20d_entry` includes entry-day close (mild). → Tag both as post-entry telemetry and EXCLUDE from `enriched_features_v1` and all future feature searches.
- **Opportunity-surface + 3-day labelers STALLED since 06-26.** 950/3,944 rows (24.1%; scans 06-29..07-24) WINDOW_OPEN/null although every 3-day window has closed. The monetized surface metric is dark for the entire live V7.1 era; blocks all surface research on the current regime. Backfill = top ops priority.
- **`pool_liquidity_snapshot` quote columns 100% NULL** (31,400/31,400 rows; bid/ask/mid/spread_pct) — RM-001b confirmed still fully blocked; the fetcher populates OI/greeks/day-bars only. Needs a quote-capable endpoint/entitlement, not waiting.

Provenance: workflow `wf_e301233a-c66` (12 agents: 6 finders + 6 adversarial verifiers, ~641K tokens, 165 tool calls). Full structured output archived in the session task output; per-agent transcripts under the session workflows dir.

---

## 2026-07-28 (evening) — Entry-day contract tradeability study: the ghost-pool mechanism, quantified (15 days, N=750)

Trigger: owner real-money kill on UNP 260821C310 (6 contracts all day, ~30% effective spread) + trader-side measurement (`gammarips-trader/docs/POOL-LIQUIDITY-FINDING-2026-07-28.txt`, one session, 48% of pool under 50 contracts). Engine-side study on `pool_liquidity_snapshot` (scans 07-06..07-24, 15 complete entry days × 50, joins 100%). Label: entry-day max non-stale `day_volume` per recommended contract.

> **2026-08-07 STATUS: this study is CORRECT and must NOT be re-run.** The stale-day-bar defect found 2026-08-07 (`docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md`) did **not** contaminate it — note the label above says "**non-stale** `day_volume`". The 52%-zero bucket matches the independently measured stale-bar rate at the 09:45-10:00 ET read (~50%), which is only possible if this study date-validated the bar. Raw `day.volume` is **never 0 and never NULL** in 49,285 snapshot reads, so a naive read cannot produce a 52%-zero bucket at all. What broke was downstream: `signal-notifier::_fetch_live_oi` shipped the floor against the *raw* field, so the production print floor dropped **zero** candidates from go-live 2026-07-29 to 2026-08-07. **A research-to-production translation gap, not a research defect** — the incoming trader handoff's proposal to re-run this on "date-validated prints" is redundant work. **Real exposure on this finding:** the scripts + labeled data below live in a session scratchpad and may no longer exist. Confirm the print construction survives somewhere before relying on these thresholds again.

- **The measurement replicates structurally: 42.8% of pool rows trade <50 contracts on entry day (daily median 42%, range 28–70%), 22.3% GHOST (<10), 8.9% trade zero.** Every one of 15 days.
- **The trader doc's causal claims are half-right.** OI and sweep volume DO carry rank signal (Spearman +0.48/+0.52, same-sign 15/15 days) — the doc's "OI does not predict" was an N=1 over-claim. What is actually broken is the picker's SATURATION: `min(oi/200)*5` (`overnight_scanner.py:476`) is maxed by 87% of the delivered pool and 16% of maxed contracts are still ghosts. OI≥1000 still leaves 23.9% under-50. Sweep volume is non-monotonic at the top (vol≥2000 → 13.6% ghosts — the one-off-sweep signature).
- **The two strongest predictors are NAME-level and completely unused by the pipeline:** underlying share volume (rho +0.585; tercile P(≥50) 27%→87%) and chain breadth/active strikes (+0.554; 30%→87%). `prior_day_pool_volume` +0.594 but only 24% coverage (repeats are rare). Best scan-time GHOST rule (in-sample-fitted, ~825 cuts searched, disclose accordingly): `und_day_vol≤2.5M AND active_strikes_total≤15 AND rec_oi≤1000` → precision 0.60 / recall 0.59, flags 22% of pool; as admission gate keeps 78% and cuts kept-ghost rate 22.3%→11.6%.
- **Pick-time is near-deterministic but time-shifted:** at the 09:52 snapshot (delayed feed; prints through ~09:37; 09:45 shows NOTHING — first fresh data 09:52), early≥5 prints → 96.3% finish ≥50; early≥20 → 100%; early==0 (52% of pool) → 40.6% ghost / 68.1% under-50. A 0-print veto on the tournament pick would have blocked the owner's UNP entry.
- **Score floor is cosmetic:** among BULLISH+UOA>$500K (median 142 qualified/day), removing score≥4 changes the top-50 pool on 1 of 20 days (6 slots total). It neither causes the liquidity problem nor filters anything the cap doesn't. overnight_score rho with entry-day volume +0.196 (weakest meaningful predictor).
- **Sim-PnL-on-ghosts is untrustworthy (research hygiene rule):** INVALID_LIQUIDITY catches only 37% of ghosts; the other 105 sim-"filled" ghosts show mean −2.8% with 79% illiquid_exit — stale marks, not safe trades. A human pays the ~30% spread. Do NOT use sim PnL on tradeability-label ghosts in any future returns study.

Scripts + labeled data in session scratchpad (`label_data.csv`, `full_labeled.csv`, `analyze*.py`). Thresholds are 15-day in-sample — re-fit rolling before/after any deploy. Deployment via docs/DECISIONS + gammarips-engineer + gammarips-review.

---

## 2026-08-05 — Trader-handoff adjudication: catalyst/ATR "inversion" study at scale (N=3,040, 74 days) + defect triage

Trigger: gammarips-trader handoff (5 entry days 07-24→07-30, 176 joined rows) claiming `catalyst_score` AUC 0.346 and `atr_normalized_move` 0.362 against 3-td MFE ≥ +20% off the 10:00 ET anchor, plus 4 data-defect reports. Replicated at full history by gammarips-researcher (read-only); defects diagnosed by gammarips-engineer (read-only).

**Substrate:** `enriched_option_outcomes` `opp_status='OK'`, features via `enriched_features_v1` (`iv_rank_entry`/`iv_percentile_entry` excluded per the 07-28 contamination finding), `catalyst_type` joined from `overnight_signals_enriched_safe`. Scans 2026-04-10→07-29 (150 WINDOW_OPEN rows ≥07-30 excluded — fill frontier, not stall; see triage below). **N=3,040 OK rows, 74 entry days.** Target `opp_peak_return ≥ 0.20`. Pooled base rate 50.7%; per-day 0.17→0.89 (p25 0.39 / p75 0.58); monthly 0.45–0.55. Day-clustered bootstrap: 1,000 resamples over entry days. Population caveat: fillable subset only (960 NO_BARS + 94 NO_POST_ENTRY_BARS ≈25% carry no surface — non-random illiquid tail); oversize pools 06-05→06-10 (133–175 rows/day) up-weight era A. Nulls: catalyst_score 1.4%, moneyness 4.4%, volume_oi_ratio 12.9%, catalyst_type 1.5%.

| feature | pooled AUC | day-clustered 95% CI | days <0.50 | trader window (N=230) | verdict |
|---|---|---|---|---|---|
| catalyst_score | 0.465 | [0.439, 0.493] | 40/74 | 0.376 | between-day composition artifact; within-day NULL |
| atr_normalized_move | 0.503 | [0.475, 0.531] | 29/74 | 0.391 | NULL |
| rsi_14 | 0.503 | [0.474, 0.534] | — | 0.379 | NULL (the tape-artifact tell) |
| contract_score | 0.514 | [0.484, 0.542] | — | — | NULL pooled; era-B lead below |
| overnight_score | 0.512 | [0.485, 0.542] | — | — | NULL (cap-era 0.488) |
| recommended_delta | 0.475 | [0.451, 0.501] | — | — | mild inversion ≈ known %-vol-leverage mechanics |
| volume_oi_ratio | 0.456 | [0.427, 0.481] | — | — | within-day median 0.524 → same day-composition artifact; 12.9% null |
| recommended_iv / risk_reward_ratio / moneyness_pct | 0.488 / 0.506 / 0.489 | — | — | — | NULL |

Trader-window replications confirm their measurements were accurate; the window was unrepresentative (base 0.613, one tape). Of 10 features, 2 pooled CIs excluded 0.50 and **both dissolved under day-demeaning**.

**Decompositions (catalyst_score):** day-demeaned AUC **0.499** (Jun–Jul 0.491 [0.464, 0.521]) — discrimination vanishes when each day's pool mean is removed. Day-level Spearman(pool-mean CS, day base rate) = **−0.381 (p=0.001, 74 days)**: high-catalyst-heavy pool days are lower-base-rate days — regime/composition correlation, not per-contract information. Monthly AUC Apr 0.499 / May 0.506 / Jun 0.469 / Jul 0.465; walk-forward halves (split 06-08) 0.506 [0.476, 0.538] / 0.469 [0.436, 0.509] — sign flips. **IV-crush mechanism (H4): NOT SUPPORTED** — between-type AUC 0.485, within-type N-weighted 0.472, type-demeaned 0.472 [0.446, 0.500] (CI touches 0.50); earnings-adjacent types (Beat/Miss/Guidance, N=372, mean CS 0.867) base 0.465 vs 0.514 rest, Δ −4.9pp CI [−10.5, +1.4] crosses zero; per-type scatter (Guidance Raise 0.395 n=86 but Guidance Cut 0.800 n=20, Regulatory 0.596 n=99). **One-finding-or-two (H5): neither** — Spearman(CS, atr_move) +0.180; CS AUC within atr terciles 0.490/0.449/0.449; atr within CS terciles 0.530/0.500/0.492. Three simultaneous window "inversions" (CS, atr, rsi) were correlated day effects on 5 shared-tape days.

**Era stability:** A pre-cap 04-10→06-10 (N=1,500/41d, base 0.485): CS 0.451. B cap-50 06-11→07-27 (N=1,446/31d, base 0.522): CS 0.488. C tradeability-picker 07-28→29 (N=94/2d, base 0.628): too thin. No non-null hypothesis is era-stable. **Exception worth a pre-committed re-test: contract_score era-B 0.552 [0.515, 0.588], day-demeaned 0.564 [0.529, 0.598], 21/31 days >0.50, median day AUC 0.590** (era-A 0.501). Post-hoc slice out of ~50 feature×slice looks (Deflated-Sharpe framing applies) and the boundary coincides with a mechanical pool change → re-run once ≥15 fresh closed-label days accrue (~late Aug); if it holds it reverses "the composite doesn't separate."

**Recommendation recorded: NO ranker re-fit, no pool tilt from this evidence.** Do not down-rank high-catalyst or high-ATR contracts within a day's pool. Day-level catalyst telemetry (rho −0.38) = accrue only. Note: the 07-28 entry's "opp labels dark since 06-26" is **resolved** — labels continuous through scan 07-29.

**Defect triage (same handoff, diagnosis-only):**
- **"Opp surface stalled after 07-29" — NOT a stall.** `run_fill_closed_windows` (17:30 ET cron) fills only windows whose last session is strictly `< today` (`forward-paper-trader/main.py:1167`, deliberate leakage guard vs partial-final-session MFE). Steady state: newest filled scan = today −4 trading days; 07-29 was exactly the frontier at sampling. Fill cron HTTP 200 daily 07-28→08-04, merged 50/day; exactly 150 WINDOW_OPEN rows total (scans 07-30→08-03), zero older stuck. Consumer-side fix (MCP repo): derive window-close date and serve `FILL_PENDING` vs stale in `src/tools/substrate.py`.
- **"Duplicate minute bars" — zero duplicates in BQ.** `option_minute_paths` stores one 3-session path per (scan_date, contract); a contract in 2–3 consecutive pools owns a session 2–3× by design (PYPL 3×69=207). GROUP-BY-HAVING>1 over (scan_date, contract, ts) for bar_date ≥07-27: empty. Writer is DELETE-then-LOAD idempotent (`forward-paper-trader/minute_paths.py:188-203`), single 08-04 ingest. Bug is the MCP read (`../gammarips-mcp/src/tools/contract_history.py:206-213` — no scan_date restriction/dedup); fix = QUALIFY ROW_NUMBER. No BQ cleanup needed.
- **CSCO 08-05 "earnings contradiction" — rail worked; narrative overclaimed.** Rail window [scan_date, entry+2td] = [08-04, 08-07] (`signal-notifier/main.py:2350-2352`): 14 reporters found, removed ETSY+AMD, CSCO not among them; calendar fetch succeeded (fail-closed path not taken). MCP earnings view tests print-on/before-expiry (08-21) → true for CSCO's mid-Aug print. The judge LLM receives no earnings data and wrote "cleanly avoids near-term earnings traps" — overclaim. Fix: stamp pick notification with the rail's actual clearance window + expiry re-check line. CSCO's precise date not in BQ (calendar responses never persisted); bounded (08-07, 08-21].
- **The one real engine defect (from the SPCX universe question): the scan universe is a frozen static file.** `_load_universe()` (`src/enrichment/core/pipelines/overnight_scanner.py:301-313`) reads `gs://profit-scout-data/overnight-universe.txt` — 5,230 tickers, last modified **2026-02-13**, no regenerator anywhere in the repo; membership check at `overnight_scanner.py:332` discards everything else. Polygon's full-market snapshot (~11K tickers incl. same-day listings) delivers SPCX nightly; it dies at that line. No other filter (price/IPO/index/history) exists; downstream is already IPO-friendly (neutral momentum for <60-session names). Fix: regenerate + recurring refresh (zero-code); durable: derive from Polygon options-contracts reference (cached daily). Do NOT simply drop the check — full-snapshot movers would blow the 540s Cloud Run timeout at 20 req/s.

**Universe refresh EXECUTED same day (owner go):** `overnight-universe.txt` regenerated to **3,547 point-verified active optionable US common stocks** (SPCX in; CS-only criterion preserved — no ETFs/ADRs, confirmed the old list's design). All 1,780 removals point-verified legitimate: ~1,700 old names had NO listed options (never could signal — the effective universe was always ~3,450), the rest delisted/acquired (BLD, NUVL, SCVL, LC, IAC, SATS confirmed dead tickers). Old file backed up (`universe-backups/overnight-universe-2026-02-13.txt`); tool `scripts/universe/refresh_universe.py`; recurring job queued (runtime ~9 min > scanner 540s). **Vendor discovery en route: Polygon `next_url` cursor pagination silently and deterministically SKIPS rows** (RDDT dropped from the /v3/reference/tickers bulk walk while point lookups return it; /v3/reference/options/contracts bulk walk lost it too, and unfiltered limit=1000 pages of that endpoint time out server-side). Derivation therefore uses explicit keyset paging + per-name probes, removals point-verified, probe errors fail open. Production `next_url` trust (`polygon_client.py:215` Pass 2 chains, `benchmark_context.py`) flagged for completeness audit — memory `polygon-next-url-cursor-skips-rows`.

Scripts (throwaway, read-only BQ): session scratchpad `opp_study.csv`, `analyze.py`, `decompose.py`, `followup.py`.

---

## 2026-08-19 — PM entry / "catch the morning pop": REFUTED. The morning pop does not exist on tradeable contracts, and the overnight hold breaks the stop

Owner question: is it better to enter in the afternoon and catch the next morning pop, than
to enter in the morning? Tested the live V7.1 GIGO bracket (+40% TP / -30% stop, 2%
slippage each way, TIMEOUT > STOP > TARGET) under three entry/exit rules on the option
premium path.

- **Substrate:** `profit_scout.option_minute_paths` (the enriched-pool minute tape, day_index
  1/2/3, regular session only). 337,264 bars, 4,292 (scan_date, contract) legs, 87 scan
  dates, 2026-04-10 → 2026-08-17. Script:
  `backtesting_and_research/2026-08-19_pm_entry_overnight_study.py` (read-only).
- **Arms.** A = LIVE, enter 10:00 ET day-1, flat 15:45 ET day-1. B = PM, enter 15:45 ET
  day-1, hold overnight, exit day-2 at 09:35 / 10:00 / 10:30 / 11:00 / 12:00 / 15:45.
  C = CONTROL, enter 10:00 ET day-1 but hold to day-2 10:00. C separates "PM entry" from
  "overnight hold". Cadence is one trade per day in every arm, so capital velocity is
  approximately equal and the V7 velocity lever does not decide this comparison.
- **Gap handling.** Options do not trade overnight, so the stop cannot execute in the gap.
  On the first bar of a new session the stop fills at the open when the open is already
  through it. The target stays capped at the limit price. A symmetric variant is reported
  alongside.

### Method defect caught and fixed mid-study (record it, it recurs)

Version 1 of the walk carried the last seen close forward when the timeout day had no print
near the exit time. That invented a near-flat exit (slippage only) for every illiquid leg
and flattered whichever arm held the thinner tape. It read as PM +1.55%. The fix requires a
real print within 15 minutes at BOTH ends of every arm. A leg with no print near its exit
time is UNFILLABLE, not flat. Tape quality that forced this: median 11 traded minutes per
day-2 leg out of 390, 71% of legs under 30 bars, **73% of all bars single-print
(o==h==l==c)**, and the first day-2 print lands after 10:15 on 25% of legs.

### Fill availability (15-minute tolerance, symmetric)

| anchor | legs with a real print | % |
|---|---|---|
| within 15m of 10:00 ET day-1 | 2,017 | 47.0% |
| within 15m of 15:45 ET day-1 | 1,793 | 41.8% |
| **intersection (both arms fillable)** | **1,074 (64 days)** | 25.0% |

Zero legs expire on day-1, so expiry does not block the overnight hold.

### The premise fails on its own terms: there is no morning pop where you can trade

Raw price legs, no bracket, no slippage. LIQUID = day-1 and day-2 both >= 120 traded
minutes and premium >= $1.00 (N=103).

| leg | n | mean | trim99 | median | LIQUID mean | LIQUID median |
|---|---|---|---|---|---|---|
| day-1 10:00 -> 15:45 (AM session) | 1,317 | -4.56% | -4.84% | -7.69% | -2.58% | -4.65% |
| day-1 15:45 -> day-2 09:30 (GAP) | 1,411 | -0.73% | -1.02% | -0.40% | -4.43% | -5.59% |
| day-2 09:30 -> 10:00 (MORNING POP) | 1,150 | +8.19% | +5.08% | **+0.00%** | **-3.60%** | -2.94% |
| day-1 15:45 -> day-2 10:00 (PM total) | 1,271 | +3.48% | +2.70% | -1.44% | **-7.72%** | -12.04% |

The whole-set +8.19% morning mean is two penny options: MBLY 260807C8.5 at +2,100% and CHWY
260618C21 at +1,400%, both under $0.60. The median morning move is exactly 0.00%. By premium
bucket the mean falls monotonically: +22.9% under $0.25, +2.8% at $2-5, +2.9% above $5. On
liquid contracts both the overnight gap AND the first 30 minutes are NEGATIVE.

### Bracketed head-to-head, paired difference vs the live arm (day-clustered bootstrap, 90% CI)

| tier | n legs / days | PM -> d2 10:00 | PM -> d2 15:45 | C (AM entry, held overnight) |
|---|---|---|---|---|
| ALL fillable | 1,074 / 64 | +2.03% [-2.1, +6.0] | +0.93% [-3.2, +4.9] | -0.98% [-2.4, +0.3] |
| LIQUID >=60 min/day, prem >=$0.50 | 361 / 49 | +0.61% [-5.0, +6.2] | -1.34% [-7.0, +4.0] | -1.93% [-4.3, +0.3] |
| DEEP >=120 min/day, prem >=$1.00 | 103 / 40 | -6.45% [-17.6, +4.4] | -8.96% [-19.6, +1.1] | **-5.55% [-10.1, -1.6]** |
| **ENTRY-KNOWABLE** day-1 >=120 min, prem >=$1.00 | 168 / 45 | -5.44% [-15.0, +4.2] | **-8.25% [-17.0, -0.2]** | **-4.87% [-8.7, -1.4]** |

The sign flips with liquidity. The apparent PM gain lives only in the tier that includes
contracts nobody can trade, which is the same thin-tape mirage the 2026-06-22 entry-timing
study found. LIQUID and DEEP screen partly on day-2 bar count, which is not knowable at
entry. ENTRY-KNOWABLE screens on day-1 liquidity only, so it is the tier that describes a
rule the trader could actually run. Every PM variant is negative in it.

### The decisive result is the tail, not the mean

| tier | arm | mean | win% | p05 | share worse than -30% |
|---|---|---|---|---|---|
| ENTRY-KNOWABLE | A. LIVE 10:00 -> 15:45 d1 | -4.42% | 39.3% | **-31.4%** | 29.2% |
| ENTRY-KNOWABLE | B. PM 15:45 -> d2 10:00 | -9.86% | 35.7% | **-53.0%** | 38.7% |
| ENTRY-KNOWABLE | B. PM 15:45 -> d2 15:45 | -13.33% | 30.7% | -53.8% | 56.4% |
| ENTRY-KNOWABLE | C. AM entry held to d2 10:00 | -9.29% | 36.3% | -51.3% | 52.4% |

The live arm's p05 is -31.4% because the -30% stop IS the floor. Every overnight arm prints
p05 near -53%. The stop cannot execute in the gap, so the protection the live policy pays for
stops existing. The tail deepens by about 22 percentage points.

Exit mix shifts as expected: A = TIMEOUT 55% / STOP 32% / TARGET 13%. PM -> d2 10:00 =
TIMEOUT 48% / STOP 32% / TARGET 20%. The extra target hits are the cheap-contract pops.

### Control arm C is the cleanest signal in the study

C keeps the 10:00 entry and changes ONLY the hold. It is significantly worse in both liquid
tiers (-5.55% [-10.1, -1.6] and -4.87% [-8.7, -1.4], both CIs exclude zero). **The damage is
the overnight hold, not the entry time.** This independently re-confirms the same-day exit
lever ([[v7-gigo-same-day-exit]]) on a substrate and a question that study never touched.

### Robustness and stability

Symmetric gap fills (target also fills at a gapped open, favourable to the challenger) move
the ALL-tier paired difference to +3.45% [-0.4, +7.4], still no signal. Month means on the
intersection set: Apr +1.08, May +3.85, Jun +4.71, Jul -0.84, Aug +1.44 (Apr/May n=5/11, do
not read them). Tournament picks only, both arms fillable, N=14: A mean -12.69% / median
-12.29% / win 21%; PM -> 10:00 mean -7.95% but median -16.97% and win 43%, so the mean is one
winner; PM -> d2 15:45 mean -15.48% / median -31.40%. N=14 decides nothing.

### Verdict and caveats

**Do NOT move the entry to the afternoon. Do NOT hold overnight.** The premise fails twice
over: on tradeable contracts the overnight gap is negative (-4.4%) and the morning half-hour
is also negative (-3.6%), and the overnight hold removes the stop that caps the live policy's
tail. Keep V7.1 as it is.

Caveats. Single regime (Apr-Aug 2026, 64-45 usable days). Liquid N is small (103-168) so
"PM is worse" carries a wide CI, but the burden of proof was on the challenger and every
liquid-tier variant is negative on both mean and tail. No NBBO on this Polygon plan, so no
spread model exists and no arm pays a spread, the same limit the 2026-06-22 study hit. The
result is an entry/exit-timing finding only. It does not bear on selection.

---

## 2026-08-19 (execution) — Execution-risk calibration: the stop is the failure point, not the spread

Owner question: what guidelines minimise EXECUTION risk for the autonomous traders? Built
the measured mapping from the fields an agent can see at decision time to the execution
risk they imply. Guidelines document: `docs/EXECUTION-RISK-GUIDELINES.md`. Script:
`backtesting_and_research/2026-08-19_execution_risk_calibration.py` (read-only).

**Hard constraint confirmed first: we have NO spread.** `bid`, `ask`, `mid`, `spread_pct`
and `last_trade_price` are NULL in **all 64,550 `pool_liquidity_snapshot` reads**
([[spread-gate-retired]]). True crossing cost is unmeasurable. Every number below is a
print-based proxy.

### Print density (day-1 tape, 4,292 legs)

Median leg trades **9 minutes out of 390**. 51.7% under 10 traded minutes, 73.0% under 30,
86.1% under 60, 94.9% under 120. Session coverage by 30-min block (share of legs printing):
09:30-10:00 63.0% / 10:30-11:30 66.0% / 11:30-13:00 66.9% / 14:30-15:30 57.1% /
**15:30-16:00 51.6% (thinnest block of the day)**. The live 15:45 flat exit is planned into
the worst liquidity of the session.

### Inter-print price uncertainty (the spread substitute, 114,267 steps)

By gap between consecutive prints, median |move|: 1 min **1.6%**, 5-14 min 3.0%,
15-29 min 4.2%, 30-59 min 5.6%, 60+ min **8.2%** (p90 26.7%, p99 62.7%). By the leg's
all-day print count, median |move| between its own prints: <10 prints **6.2%** (p90 19.7%,
median gap 40 min) falling monotonically to 200+ prints **1.5%** (p90 2.6%, gap 1 min).
Context: median same-day peak under V7.1 is +3.8%. **On the thin half of the pool the
uncertainty between two consecutive prints exceeds the median same-day opportunity.**

### Stop reliability — the sharpest asymmetry (N=547 breach events)

For every leg entered 10:00 ET whose -30% stop level breached, the realised fill against
the intended stop:

| traded minutes | legs | median | p10 | p01 | median gap before the breach |
|---|---|---|---|---|---|
| <10 | 48 | **-10.3%** | -24.1% | -38.5% | 89 min |
| 10-29 | 125 | -5.1% | -23.7% | -35.1% | 18 min |
| 30-59 | 159 | -3.0% | -11.5% | -27.7% | 10 min |
| 60-119 | 131 | -2.5% | -8.0% | -13.0% | 4 min |
| 120-199 | 61 | -1.7% | -6.6% | -11.2% | 2 min |
| 200+ | 23 | -1.8% | -6.6% | -9.3% | 1 min |

All legs: median **-3.1%**, p10 **-14.5%**, p01 **-30.4%**, worst **-44.0%**. **33.6% of
stops fill more than 5% past the level, 10.1% more than 15% past.** A -30% stop on a
sub-10-print contract is a -40% stop at median-to-p10 and a -54% stop in the tail. The
slippage is one-sided, so it deepens the tail without touching the mean opportunity.

### Prints by 10:00 ET is near-deterministic (the dominant observable)

| prints by 10:00 | share of pool | P(60+ prints left) | median prints left |
|---|---|---|---|
| 0 | 36.6% | **0.0%** | 2 |
| 1-2 | 26.1% | 0.5% | 5 |
| 3-5 | 13.2% | 2.6% | 17 |
| 6-10 | 10.2% | 13.5% | 32 |
| 11-20 | 9.3% | 50.6% | 60 |
| 21+ | 4.7% | **93.0%** | 138 |

Roughly **14% of the pool is comfortably manageable; about 63% is effectively untradeable
by 10:00**. Independently corroborates the 2026-07-28 ghost study (early >=5 prints ->
96.3% finish >=50 contracts; early >=20 -> 100%) on a different label and a longer window.

### Anti-heuristic: premium does NOT predict liquidity

Median traded minutes by premium: <$0.50 = 12, $0.50-1 = 11, $1-2 = 13, $2-5 = 10,
**>$5 = 6**. P(60+ minutes all day) is flat at 12-17% across every premium bucket.
Expensive contracts print LESS. Do not use premium or name recognition as a liquidity
proxy.

### NULL RESULT — the round trip is second-order

Replayed the identical V7.1 bracket on identical legs (N=1,317) under three fill
conventions: PAPER (flat 2% each way), ADVERSE (buy entry-bar high, sell exit-bar low),
UNCERT (pay half the leg's own median inter-print move each way). Tier drag is about 2 to 4
points with **no clean liquidity gradient**, because a percentage bracket is
scale-invariant: a higher entry scales the stop and the target with it. ADVERSE reads
*better* than PAPER on thin tiers (-0.3% vs -3.4% at <10 prints) purely because
single-print bars have h==l==c, which is the proxy going blind exactly where risk is
highest. **Conclusion: the execution problem is not "you pay a wide spread twice", it is
"you cannot transact when you need to."** Do not spend effort modelling round-trip spread
cost. Caveat: this replay needs a real print at both 10:00 and 15:45, so it selects the
most liquid members of every thin tier (the <10 cell is 70 legs).

### Caveats

Single regime (Apr-Aug 2026). Stop-slippage N is 547 events and only 23 in the deepest
tier, so the tier ORDER is safe (monotonic, large) but the precise levels are not. **No
number here is validated against a real fill** — everything comes from the trade tape, not
from our own executions. The live Robinhood lane is the first source of real fill data; the
first job once it accrues is to compare realised fills against these priors and re-fit.

---

## 2026-08-19 (tradeable subset) — The ghosts were FLATTERING the pool, not hiding it. Pool composite goes -4.67% -> -9.59% when you keep only tradeable rows. Pre-committed contract_score re-test FAILS

Owner call after the execution-risk calibration: if ~63% of the pool is untradeable by
10:00, re-score selection on the tradeable subset only. Script:
`backtesting_and_research/2026-08-19_selection_on_tradeable_subset.py` (read-only).

- **Universe:** `enriched_features_v1` (leakage-safe view) joined to `enriched_option_outcomes`
  and to the day-1 minute tape. N=3,776 closed V7.1 same-day labels, 87 scan dates,
  2026-04-10 to 2026-08-17, 58 tournament picks with both a label and a tape.
- **Tradeability label is ENTRY-KNOWABLE:** count of date-validated prints by 10:00 ET.
  TRADEABLE = 11 or more (the tier where P(60+ prints left) first exceeds 50%).

### A. The result inverts the hypothesis, and the mechanism is measurement

| prints by 10:00 | n | mean | 90% CI | median | win% |
|---|---|---|---|---|---|
| 0 | 1,158 | -2.23% | [-3.4, -1.1] | -1.96% | 27.7% |
| 1-2 | 1,020 | -3.51% | [-5.0, -1.9] | -1.96% | 32.9% |
| 3-5 | 564 | -5.46% | [-7.5, -3.2] | -5.60% | 39.0% |
| 6-10 | 436 | -6.13% | [-9.3, -3.0] | -7.82% | 41.1% |
| 11-20 | 398 | -9.81% | [-13.5, -6.3] | -14.75% | 30.2% |
| 21+ | 200 | -9.17% | [-14.0, -3.8] | -14.62% | 33.0% |
| **ALL** | **3,776** | **-4.67%** | [-6.4, -3.0] | -1.96% | 32.9% |
| **TRADEABLE 11+** | **598** | **-9.59%** | [-13.4, -5.7] | -14.75% | 31.1% |

Monotonic and the opposite of the prior. **The ghost rows are fabricated near-flat and drag
the whole-pool composite toward zero.** Verified signature: **33.7% of 0-print rows carry
the EXACT no-move return of -1.9608%** (= 1/1.02 - 1, the exit filling at the entry bar's
own close because nothing printed in between), 20.7% of the 1-2 tier likewise, 16.8% of the
whole pool. 0-print rows are 70.6% `illiquid_exit` and 86.0% TIMEOUT. The gradient SURVIVES
deleting every `illiquid_exit` row (0-print -3.44% -> 21+ -9.17%), because production's own
flag catches only 37% of ghosts (2026-07-28 rule).

**Consequence: every whole-pool performance number this program has published is optimistic
by construction.** The honest harvestable composite under V7.1 is about **-9.6%**, not -4.7%.

### The ghost tier looks better only through NON-PARTICIPATION

| tier | n | STOP | TARGET | TIMEOUT | mean |
|---|---|---|---|---|---|
| GHOST 0-2 | 2,178 | 8.8% (-39.2%) | 5.2% (+37.2%) | 86.0% (**-1.54%**) | -2.83% |
| mid 3-10 | 1,000 | 23.8% (-36.3%) | 10.6% (+37.2%) | 65.6% (-1.60%) | -5.75% |
| TRADEABLE 11+ | 598 | 35.8% (-34.3%) | 12.2% (+37.2%) | 52.0% (-3.56%) | -9.59% |

On a ghost the bracket essentially never fires and the position exits at a stale mark worth
-1.5%. That is not performance, it is the absence of a trade.

### B. Selection ranking power on the tradeable subset: NO EVIDENCE

Pooled and day-demeaned AUC vs a positive same-day return, day-clustered 90% CI, 14
leakage-safe features x 2 methods x 2 subsets = **56 looks**. Only 3 CIs excluded 0.50
(TRADEABLE demeaned: `overnight_score` 0.537 [0.505, 0.573], `recommended_oi` 0.545
[0.505, 0.581], `recommended_volume` 0.542 [0.502, 0.584]). **At a 90% CI, 56 looks produce
about 5.6 spurious exclusions by chance. Three hits is BELOW chance.** Nothing here is
evidence of ranking power. Stripping ghosts did NOT reveal a hidden selection edge.

### C. The tournament pick DOES tilt toward tradeable, and may add value

Picks land on TRADEABLE (11+) **32.8%** of the time against a pool base of **15.8%** — a
2.1x lift, which is the live OI + print floors working ([[live-oi-floor]]). But **48.2% of
picks still land on 0-2-print contracts**, so the floors are not close to sufficient.

Return, matched on the same days: pick -5.43% [-9.6, -1.2] vs pool -6.27%, **diff +0.84pp**
(n=58). Tradeable only: pick -5.90% [-15.1, +3.4] vs pool -10.31%, **diff +4.41pp** (n=19).
The tradeable-subset lift is the larger number but n=19 and the CI crosses zero.
**Directional only, not a result.**

### D. PRE-COMMITTED RE-TEST FAILED — contract_score era-B lead is dead

The 2026-08-05 adjudication flagged one lead: cap-50-era `contract_score` AUC 0.552
[0.515, 0.588] pooled / 0.564 day-demeaned, to be re-tested on >=15 FRESH closed-label days
after 07-27. **The 15 days now exist (N=737) and the lead does not survive:**

| feature | pooled | demeaned |
|---|---|---|
| `contract_score` | **0.481** [0.457, 0.505] | **0.484** [0.459, 0.510] |
| `overnight_score` | 0.522 [0.484, 0.563] | 0.517 [0.479, 0.557] |
| `contract_score`, TRADEABLE only (n=183) | — | 0.463 [0.389, 0.545] |

Clean out-of-sample rejection of a pre-registered hypothesis. **Close it. Do not re-slice
the cap-50 era looking for it again.**

### The one constructive finding: the surface is real, the fixed bracket destroys it

SAME-DAY excursion (10:00 entry incl. 2% slip -> 15:45), the correct window for V7.1. The
3-day `opp_*` surface INVERTS this comparison, exactly as memory
`same-day-vs-3day-window-mismatch` warns (3-day says tradeable has MORE upside, +29.5% vs
+18.3% median peak; same-day says upside is EQUAL and downside is much worse):

| tier | n | median MFE | median MAE | P(MFE>=+40%) | P(MAE<=-30%) | stop:target |
|---|---|---|---|---|---|---|
| GHOST 0-2 | 221 | +11.3% | -14.2% | 14.9% | 20.8% | 1.39 |
| mid 3-10 | 545 | +10.1% | -19.3% | 12.5% | 28.6% | 2.29 |
| **TRADEABLE 11+** | 551 | **+10.6%** | **-23.2%** | **12.7%** | **37.6%** | **2.96** |

A tradeable contract's median same-day best moment is **+10.6%** against a **+40%** target it
reaches 12.7% of the time, while it visits -30% **37.6%** of the time. Unconditional
same-day touch rates on the tradeable tier: +20% is touched **32%**, +30% 19%, +40% 13%;
-20% 57%, -30% 38%, -40% 25%, -50% 13%.

**Read this as a SHAPE, not as EV.** Touch rates ignore path order, and
[[bracket-optimization-dead]] is settled doctrine (0/840 variants profitable in-sample AND
out-of-sample). What is genuinely new is that the 840-variant sweep ran on
`signals_labeled_v1`, a whole-pool cohort that this entry now shows is ~58% fabricated-flat
rows, and no bracket work has ever been run on a tradeability-labelled subset. **That is an
owner call, flagged once here, not a recommendation to re-run brute force.**

### Caveats

Single regime (Apr-Aug 2026). TRADEABLE n=598 over 51 days; the 21+ tier is 200 rows. The
tradeability label needs a day-1 minute tape, so legs with no tape at all are absent
entirely (they are, if anything, worse than the 0-print tier). Section C's tradeable pick
comparison is n=19. Nothing here is validated against a real fill.

---

## 2026-08-19 (bracket sweep, tradeable) — 0/432 profitable. The 840-sweep verdict REPLICATES on the honest substrate. Bracket optimization is dead here too

Owner call: re-run the bracket sweep on the tradeable subset, because
[[bracket-optimization-dead]] (0/840) was measured on `signals_labeled_v1`, a whole-pool
cohort now shown to be ~58% ghost-contaminated, where the bracket mostly never fires
(STOP fires on 8.8% of 0-2-print rows against 35.8% on tradeable). The concern was
legitimate. **The answer did not change.** Script:
`backtesting_and_research/2026-08-19_bracket_sweep_tradeable.py` (read-only).

- **Grid:** target x stop x same-day exit time = 9 x 8 x 6 = **432 variants**
  (`None` disables a leg, so no-target and no-stop are both in the grid).
- **Conventions:** production 2% slippage each way, TIMEOUT > STOP > TARGET, and a REAL
  print required within 15 min at BOTH the entry and the exit anchor (the stale-exit rule).
- **Protocol:** chronological 60/40 holdout, matched to the original sweep so the verdicts
  are comparable.

### Result

| tier | legs | days | variants | positive full-period | positive in-sample | positive OOS | **profitable in BOTH halves** |
|---|---|---|---|---|---|---|---|
| TRADEABLE (11+ prints) | 591 | 50 | 432 | **0** | **0** | **0** | **0 of 432** |
| SEMI (6+ prints) | 985 | 56 | 432 | **0** | **0** | **0** | **0 of 432** |

Best in-sample config carried out-of-sample: TRADEABLE `+20% / -15% / 12:00` reads
**-6.02%** in-sample and **-6.14%** [-8.5, -3.7] out-of-sample. SEMI `+25% / -15% / 13:00`
reads -6.23% in-sample and -4.95% [-7.3, -2.6] out-of-sample. Stable and negative.

**The grid is not noise, which makes the verdict stronger.** Rank correlation of variant
means across the two halves is **0.575 (TRADEABLE) / 0.581 (SEMI)**. Variants order
consistently across time. There is simply no configuration above zero to find. Contrast
with a noise grid, where the correlation would sit near 0 and the "best" would be random.

### Secondary finding: the LIVE bracket is not the argmax even inside the losing set

On TRADEABLE, live V7.1 (`+40 / -30 / 15:45`) reads **-9.76%** [-13.3, -6.2]. The best
variants read about **-6.0%**, a spread of roughly **3.7pp per trade**. Every one of the
top 12 variants shares **stop = -15%** (the TIGHTEST stop in the grid) with a midday exit,
and every one shows p05 = **-16.7%**, which is exactly the -15% stop plus round-trip
slippage. Target choice barely moves the result (+20% through +50% cluster inside 0.2pp),
which independently reproduces the earlier "no target between +30% and +60% is
distinguishable" finding on a different substrate.

**Read the boundary honestly.** The optimum sits ON the tightest-stop edge of the grid,
which is the classic signature of an optimum that lies outside it: the extrapolation of
"cut faster and smaller" is "do not hold the position at all." This is a
lose-less result, not an edge, and it is the same velocity + tail-reduction lever V7
already banked ([[exit-velocity-same-day-lever]]). **Do not read it as a proposal to
re-cut the live bracket to -15%.**

One reason not to, quantified: tightening the stop raises the stop-hit FREQUENCY, and the
2026-08-19 execution calibration measured stop slippage at the -30% level (median -1.7% to
-2.5% on tradeable tiers), not at -15%. A -15% stop fires far more often, so it pays that
slippage far more often. The sweep does not model that, so its -6% is optimistic relative
to a real -15% implementation.

### What this closes and what it leaves open

**CLOSED:** the ghost-contamination objection to [[bracket-optimization-dead]]. The
doctrine now holds on both the whole-pool cohort (0/840) and the tradeability-labelled
subset (0/432, two tiers, in-sample and out-of-sample). It is not a bracket-tuning problem
on any substrate we have measured. Do not re-open it again without new data, not merely a
new slice.

**STILL OPEN, and it is the question that actually decides "are the picks good":** the pool
has never been compared to a BENCHMARK. Every AUC test to date asks "can we rank WITHIN the
50?" (answer: no). None asks "is the 50 better than 50 random optionable contracts on the
same day?" We hold no option minute tape for non-pool contracts, so this needs a fresh
Polygon pull (order of 20 control contracts x 87 days). Until it is run, selection quality
versus an alternative is **unknown**, not refuted. Note the pending
`POLYGON_API_KEY` rotation in the owner queue before any new pull.

### Caveats

Single regime (Apr-Aug 2026). TRADEABLE is 591 legs over 50 days, and the out-of-sample
half is 233. The grid is same-day only, which is correct for V7.1 and is also supported by
the 2026-08-19 overnight result. Nothing here is validated against a real fill.

---

## 2026-08-19 (pool construction) — The owner is right: ghosts are removable with fields we ALREADY collect. But 50 slots and a ghost-free pool cannot both hold

Owner challenge: no contract in the pool of 50 should ever be a ghost, there is plenty of
liquid supply, and the selection logic filters the good ones out. **The first two claims
are correct in direction. The third is half right, and the supply has a hard ceiling.**

### The scan-time fields that predict tradeability are ALREADY in the scanner output

`overnight_signals` (204,991 rows, 89 days) carries `day_volume` (underlying share volume)
and `call_active_strikes`. Those are the exact two NAME-level predictors the 2026-07-28
study ranked strongest (rho +0.585 and +0.554) and called "completely unused by the
pipeline". They are still unused for ranking. No new vendor and no new field are needed.

### Validation on our own labeled pool (N=4,292 contracts, 87 days)

Ghost = 2 or fewer prints by 10:00 ET. Tradeable = 11 or more.

| filter | n | % GHOST | % TRADEABLE |
|---|---|---|---|
| **no filter (what we ship today)** | 4,292 | **62.7%** | 14.0% |
| `und_vol>=2.5M` | 3,131 | 53.5% | 18.6% |
| `call_active_strikes>=15` | 1,455 | 42.5% | 29.8% |
| `recommended_oi>=1000` | 1,548 | 34.0% | 29.5% |
| `und_vol>=2.5M AND strikes>=15` | 1,399 | 41.7% | 30.8% |
| **`und_vol>=2.5M AND strikes>=15 AND oi>=1000`** | 593 | **11.5%** | 55.1% |
| **`und_vol>=5M AND strikes>=25 AND oi>=2000`** | 224 | **4.0%** | 75.9% |
| *for contrast:* `overnight_score>=7` | 1,780 | 51.6% | 19.0% |
| *for contrast:* `contract_score>=9` | 2,291 | 59.7% | 16.5% |

**The two scores we actually rank on are near-useless for tradeability** (51.6% and 59.7%
ghost against a 62.7% base). Three fields we already collect take it to 4.0%. The owner's
"archaic business logic" read is fair: `contract_score` picks the CONTRACT within a ticker
and was correctly recalibrated 2026-07-28 (log-OI ramp saturating ~3000), but **nothing in
the pipeline ranks the TICKER on liquidity**, and the ticker is where the ghost risk lives.

### The ceiling: supply per day (BULLISH candidates, 88 days)

| liquidity bar | median/day | p10 | min | days able to fill 50 | days able to fill 25 | ghost% |
|---|---|---|---|---|---|---|
| UOA>$500K only (today) | 318 | 221 | 178 | **100%** | 100% | 62.7% |
| + `und_vol>=2.5M` + `strikes>=15` | 62 | 29 | 21 | 65% | 95% | 41.7% |
| + `oi>=1000` | **22** | 10 | 5 | **9%** | 45% | **11.5%** |
| `und_vol>=5M`+`strikes>=25`+`oi>=2000` | 8 | 3 | 0 | 1% | 6% | 4.0% |

**A pool of 50 with no ghosts does not exist in this market on most days.** At the bar that
gets ghosts to 11.5% the median supply is 22 names. The UOA gate is NOT the binding
constraint at the tighter bars (identical counts with and without it) — liquidity is.

### Why shrinking the pool costs nothing measurable

The same session established that within-pool ranking has **no demonstrated edge**
(14 leakage-safe features x pooled and day-demeaned AUC x 2 subsets = 56 looks, 3 CIs
excluding 0.50 against ~5.6 expected by chance), and that the pre-registered
`contract_score` lead **failed** its out-of-sample re-test (0.552 -> 0.481). If we cannot
rank inside the pool, a pool of 50 that is 63% untradeable is strictly worse than a pool of
22 that is 89% tradeable. **We give up nothing we can measure and we delete most of the
ghost problem.**

Tournament feasibility: `TOURNEY_MIN` is 8. At the `oi>=1000` bar the median day supplies
22 and p10 supplies 10, so the tournament still runs on most days.
[[no-liquid-candidates-no-pick]] already covers the thin-day path.

### Recommended shape (owner call, NOT deployed)

Rank the pool on liquidity FIRST, then apply the flow signal inside the liquid set, and let
the pool size float instead of forcing 50. Suggested bar:
`und_vol>=2.5M AND call_active_strikes>=15 AND recommended_oi>=1000` — 22 names/day median,
11.5% ghost, 55.1% tradeable, a **5.5x** reduction in ghost rate against today.

This is a selection-policy change. Thresholds above are fitted on 87 days in one regime
and must be re-fit rolling.

### OUTCOME (recorded 2026-08-20)

The recommended admission-floor design was built the same day and lost review. The review
found a `next_url`-lossy enumeration leg and an unreachable fail-open guard. The design was
reverted and is NOT ADOPTED (`docs/DECISIONS/2026-08-19-pool-liquidity-floor-and-cap-20.md`).
In its place the owner adopted `PRINT_FLOOR_MIN` 1 to 25 on `signal-notifier` (2026-08-19).
The raise DEPLOYED 2026-08-20 (`signal-notifier-00062-wvm`, env verified `=25`), and the
cohort reset to `LIVE_COHORT_START_DATE='2026-08-21'` (the fifth reset). See
`docs/DECISIONS/2026-08-20-score-floor-accepted-print-floor-25-shipped.md`. The evidence
tables above stand unchanged.

### Caveats

The ghost label needs a day-1 minute tape, which exists for pool contracts only. So the
filter is validated on contracts we DID select, not on the ones we passed over. The supply
counts come from scanner rows and assume the passed-over names behave like the selected
ones at the same liquidity level. That assumption is untested and is the main risk in the
supply table.

---

## 2026-08-19 (entry hour) — We enter at 10:00, which is the single worst hour of the day. Every other hour is roughly flat

Owner question: should we stop looking overnight and enter in the afternoon instead? The
intraday-signal half is not answerable (we have never collected intraday flow). The
entry-hour half is, on the day-1 tape. TRADEABLE subset only (11+ prints by 10:00, N=599),
raw prices, no bracket, no slippage.

### Where the money goes, hour by hour

| window | n | mean | median | win% |
|---|---|---|---|---|
| **10:00 -> 11:00** | 548 | **-5.32%** | **-6.89%** | 37.2% |
| 11:00 -> 12:00 | 511 | -0.89% | -0.86% | 45.4% |
| 12:00 -> 13:00 | 468 | -1.32% | -1.80% | 40.4% |
| 13:00 -> 14:00 | 439 | +0.81% | -0.34% | 44.9% |
| 14:00 -> 14:30 | 432 | +0.07% | -0.06% | 43.3% |
| 14:30 -> 15:00 | 433 | -0.32% | -0.68% | 43.2% |
| 15:00 -> 15:45 | 487 | -0.80% | -1.33% | 41.1% |

**The entire day's bleed is the first hour.** The other six windows sum to about -2.5%
against the first hour's -5.32% alone. This corroborates the 2026-06-22 entry-timing study
("at 10:00 you buy after the AM pop") on the tradeable subset it lacked power for (that
study's liquid cell was N=55, this is N=548).

### Enter at T, exit 15:45

| entry | n | mean | median | win% | median MFE | median MAE | MFE:MAE |
|---|---|---|---|---|---|---|---|
| 10:00 | 551 | -8.66% | -10.71% | 32.5% | +12.8% | -21.6% | 0.59 |
| 12:00 | 508 | -2.05% | -4.25% | 39.8% | +8.8% | -13.8% | 0.64 |
| 14:00 | 472 | -1.34% | -1.91% | 41.7% | +5.8% | -8.3% | 0.70 |
| 14:30 | 464 | -1.26% | -2.22% | 37.5% | +4.7% | -6.9% | 0.68 |
| 15:00 | 487 | -0.80% | -1.33% | 41.1% | +3.8% | -5.4% | 0.70 |

**A later entry loses less AND gains less.** The MFE:MAE ratio improves from 0.59 to 0.70,
which is a genuine improvement in shape. But the absolute opportunity collapses with the
window: a 15:00 entry offers a median best-moment of +3.8%, which is below the round-trip
cost on most of this pool. **Entering later removes a self-inflicted loss. It does not
create an edge.**

### Reading

Two separable claims, and only the first is actionable today:

1. **The 10:00 entry is a defect worth fixing.** It is not a strategy question. We buy the
   worst hour on the clock every day, and the 2026-06-22 study reached the same conclusion
   from the other direction before fill realism killed its proposed fix. A midday entry
   keeps most of the opportunity (12:00 median MFE +8.8%) and skips the -5.32% hour.
2. **A short afternoon hold is not a strategy.** The ratio gets better and the size gets
   too small to clear costs.

Everything measured today stays consistent with one explanation:
**a long OTM option held for a fixed window bleeds to theta and spread regardless of
selection or bracket** ([[option-pnl-not-underlying]], [[volatility-idiosyncratic-trap]],
[[bracket-optimization-dead]]). This is the fourth independent route to that same wall.

### NOT answered

Whether an INTRADAY signal (flow detected during the session, entered minutes later)
behaves differently. We have never collected intraday flow, so there is no substrate. It
needs a new Polygon feed tier. **Cheaper and more decisive first: the pool-versus-benchmark
test, which is still the only experiment that would tell us whether selection carries any
value at all.**

### Caveats

Single regime. Raw prices, no bracket and no slippage, so every number here is optimistic
against a real implementation. Tradeable subset only, which is the honest one but also the
smallest (N=599).
