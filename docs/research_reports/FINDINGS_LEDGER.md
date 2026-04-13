# Findings Ledger — GammaRips Signal Research

> Durable evidence base. Every numeric claim in `INTELLIGENCE_BRIEF.md` and `STRATEGY_PLAYBOOK.md` should be traceable to a row in this file. Originals preserved in `_archive/research_reports_2026-04/`.

---

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

**Status as written:** Live capital NO. Production NO. Forward paper YES. The spec was the basis for the V3 forward paper trader currently running. The Iran-window data has invalidated the EV numbers used to justify it; the architectural framework (eligibility / skip / execution / logging separation) remains useful as a template for any regime-aware v2.

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
