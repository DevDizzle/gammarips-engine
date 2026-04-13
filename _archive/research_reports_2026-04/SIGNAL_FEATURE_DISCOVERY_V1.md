# Signal Feature Discovery V1

**Source:** `profitscout-fida8.profit_scout.signals_labeled_v1`  
**Simulator:** `V3_MECHANICS_2026_04_07`  
**Win threshold:** `realized_return_pct >= +0.35`  
**Labeled rows:** 2162 total / 1563 executed

## 1. Cohort overview

- **Total labeled signals:** 2162
- **Distinct tickers:** 573
- **scan_date range:** 2026-02-18 → 2026-04-06
- **Distinct scan_dates:** 30

**Exit reason distribution (full population):**

| exit_reason | n | %  |
|---|---|---|
| FUTURE_TIMEOUT | 178 |   8.2% |
| INVALID_LIQUIDITY | 273 |  12.6% |
| NO_BARS | 148 |   6.8% |
| STOP | 789 |  36.5% |
| TARGET | 345 |  16.0% |
| TIMEOUT | 429 |  19.8% |

**Executed-trade summary** (exit_reason ∈ {TARGET, STOP, TIMEOUT}):

- n = 1563
- avg realized_return_pct =  -3.26%
- median realized_return_pct = -25.00%
- win rate (return >= +35%) = 22.6%

## 2. Univariate quintile analysis (numeric features)

For each numeric feature, executed trades are split into 5 quintiles by feature value. Features are ranked by **separation** (max-bucket avg return − min-bucket avg return) and **monotonicity** (1.0 = strictly monotonic across quintiles).

**Features ranked by absolute separation** (top 20 of 41):

| rank | feature | separation | monotonicity |
|---|---|---|---|
| 1 | `reversal_probability` |  +6.97% | 0.50 |
| 2 | `recommended_delta` |  +6.69% | 0.50 |
| 3 | `risk_reward_ratio` |  +6.24% | 0.00 |
| 4 | `macd_hist` |  +5.97% | 0.00 |
| 5 | `call_active_strikes` |  +5.86% | 0.00 |
| 6 | `close_loc` |  +5.80% | 0.00 |
| 7 | `recommended_volume` |  +5.69% | 1.00 |
| 8 | `recommended_spread_pct` |  +5.43% | 0.00 |
| 9 | `rsi_14` |  +5.42% | 0.50 |
| 10 | `macd` |  +5.20% | 0.00 |
| 11 | `mean_reversion_risk` |  +5.13% | 0.50 |
| 12 | `call_vol_oi_ratio` |  +5.09% | 0.00 |
| 13 | `catalyst_score` |  +5.06% | 0.33 |
| 14 | `dist_from_high` |  +5.01% | 0.00 |
| 15 | `recommended_oi` |  +4.81% | 1.00 |
| 16 | `resistance` |  +4.75% | 0.00 |
| 17 | `price_change_pct` |  +4.54% | 0.00 |
| 18 | `call_uoa_depth` |  +4.33% | 0.50 |
| 19 | `recommended_mid_price` |  +4.18% | 0.00 |
| 20 | `enrichment_quality_score` |  +4.18% | 0.00 |

**Detailed quintile breakdowns** for top-15 features:

### `reversal_probability`  (separation= +6.97%, monotonicity=0.50)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (0.049, 0.15] | 363 |  16.8% |  -7.02% | -25.00% |
| (0.15, 0.2] | 305 |  21.0% |  -4.29% | -25.00% |
| (0.2, 0.25] | 415 |  25.1% |  -1.21% | -16.50% |
| (0.25, 0.35] | 264 |  24.2% |  -2.78% | -22.26% |
| (0.35, 0.85] | 216 |  27.8% |  -0.05% | -17.77% |

### `recommended_delta`  (separation= +6.69%, monotonicity=0.50)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.867, -0.416] | 313 |  16.9% |  -5.39% | -25.00% |
| (-0.416, -0.284] | 312 |  26.6% |  -0.35% | -13.94% |
| (-0.284, 0.29] | 313 |  29.4% |  +0.25% | -12.10% |
| (0.29, 0.441] | 312 |  20.5% |  -6.43% | -25.00% |
| (0.441, 0.969] | 313 |  19.5% |  -4.40% | -25.00% |

### `risk_reward_ratio`  (separation= +6.24%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.041, 0.06] | 332 |  20.8% |  -5.55% | -25.00% |
| (0.06, 0.17] | 298 |  20.5% |  -4.76% | -25.00% |
| (0.17, 0.42] | 312 |  19.2% |  -5.25% | -25.00% |
| (0.42, 1.254] | 306 |  26.8% |  +0.70% |  -9.45% |
| (1.254, 163.25] | 312 |  26.0% |  -1.08% | -15.00% |

### `macd_hist`  (separation= +5.97%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-39.467, -1.342] | 313 |  22.0% |  -4.12% | -25.00% |
| (-1.342, -0.252] | 312 |  18.9% |  -6.35% | -25.00% |
| (-0.252, 0.135] | 312 |  21.5% |  -3.41% | -25.00% |
| (0.135, 0.958] | 312 |  26.9% |  -0.37% | -14.21% |
| (0.958, 31.312] | 313 |  23.6% |  -2.00% | -18.56% |

### `call_active_strikes`  (separation= +5.86%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.001, 5.0] | 363 |  23.1% |  -0.52% |  -7.58% |
| (5.0, 10.0] | 301 |  21.9% |  -1.93% | -12.59% |
| (10.0, 18.0] | 299 |  19.1% |  -6.38% | -25.00% |
| (18.0, 34.0] | 296 |  22.6% |  -4.27% | -25.00% |
| (34.0, 271.0] | 304 |  26.0% |  -3.82% | -25.00% |

### `close_loc`  (separation= +5.80%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.001, 0.126] | 248 |  22.6% |  -2.64% | -24.26% |
| (0.126, 0.214] | 248 |  29.8% |  +1.00% |  -9.99% |
| (0.214, 0.312] | 249 |  20.9% |  -4.80% | -25.00% |
| (0.312, 0.481] | 244 |  23.4% |  -2.28% | -21.18% |
| (0.481, 1.0] | 247 |  20.2% |  -3.92% | -18.50% |

### `recommended_volume`  (separation= +5.69%, monotonicity=1.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (9.999, 28.0] | 317 |  22.4% |  +0.29% |  -1.96% |
| (28.0, 125.0] | 309 |  22.3% |  -2.47% | -20.05% |
| (125.0, 509.2] | 312 |  21.8% |  -4.21% | -25.00% |
| (509.2, 2050.2] | 312 |  22.4% |  -4.57% | -25.00% |
| (2050.2, 43234.0] | 313 |  24.0% |  -5.40% | -25.00% |

### `recommended_spread_pct`  (separation= +5.43%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.001, 0.0723] | 313 |  21.7% |  +0.24% |  -1.96% |
| (0.0723, 0.167] | 312 |  19.9% |  -3.25% | -15.21% |
| (0.167, 0.255] | 313 |  22.7% |  -3.01% | -25.00% |
| (0.255, 0.333] | 328 |  24.1% |  -5.18% | -25.00% |
| (0.333, 0.4] | 297 |  24.6% |  -5.12% | -25.00% |

### `rsi_14`  (separation= +5.42%, monotonicity=0.50)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (12.525, 33.656] | 313 |  17.6% |  -6.70% | -25.00% |
| (33.656, 40.707] | 312 |  20.8% |  -2.85% | -17.93% |
| (40.707, 49.3] | 312 |  25.3% |  -1.36% | -20.08% |
| (49.3, 61.147] | 312 |  23.1% |  -4.05% | -25.00% |
| (61.147, 89.501] | 313 |  26.2% |  -1.28% | -16.21% |

### `macd`  (separation= +5.20%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-301.111, -6.366] | 313 |  23.6% |  -2.24% | -19.06% |
| (-6.366, -2.084] | 312 |  22.8% |  -2.12% | -16.50% |
| (-2.084, -0.186] | 312 |  16.7% |  -6.62% | -25.00% |
| (-0.186, 2.648] | 312 |  26.9% |  -1.42% | -25.00% |
| (2.648, 81.001] | 313 |  23.0% |  -3.85% | -25.00% |

### `mean_reversion_risk`  (separation= +5.13%, monotonicity=0.50)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.001, 0.04] | 346 |  22.8% |  -2.86% | -25.00% |
| (0.04, 0.09] | 305 |  22.0% |  -3.93% | -22.48% |
| (0.09, 0.15] | 305 |  17.0% |  -5.88% | -25.00% |
| (0.15, 0.23] | 299 |  25.8% |  -0.75% | -22.19% |
| (0.23, 0.72] | 308 |  25.3% |  -2.92% | -25.00% |

### `call_vol_oi_ratio`  (separation= +5.09%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (0.016399999999999998, 0.123] | 313 |  23.0% |  -0.95% | -12.46% |
| (0.123, 0.199] | 312 |  22.4% |  -3.33% | -25.00% |
| (0.199, 0.303] | 313 |  20.4% |  -6.04% | -25.00% |
| (0.303, 0.52] | 312 |  22.1% |  -3.74% | -25.00% |
| (0.52, 66.041] | 313 |  24.9% |  -2.26% | -18.21% |

### `catalyst_score`  (separation= +5.06%, monotonicity=0.33)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (0.099, 0.75] | 325 |  21.2% |  -3.20% | -16.28% |
| (0.75, 0.85] | 855 |  22.7% |  -3.69% | -25.00% |
| (0.85, 0.88] | 64 |  25.0% |  +1.36% |  -3.43% |
| (0.88, 1.0] | 264 |  24.6% |  -1.93% | -14.32% |

### `dist_from_high`  (separation= +5.01%, monotonicity=0.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (0.0022, 0.24] | 249 |  18.5% |  -3.31% | -16.26% |
| (0.24, 0.41] | 249 |  20.9% |  -4.48% | -25.00% |
| (0.41, 0.66] | 245 |  26.9% |  -1.03% | -22.19% |
| (0.66, 1.03] | 249 |  28.1% |  +0.53% | -10.11% |
| (1.03, 10.974] | 244 |  22.5% |  -4.37% | -25.00% |

### `recommended_oi`  (separation= +4.81%, monotonicity=1.00)

| bucket | n | win_rate | avg_return | median |
|---|---|---|---|---|
| (-0.001, 2.0] | 332 |  23.2% |  -0.74% | -10.86% |
| (2.0, 16.0] | 297 |  22.2% |  -1.97% | -12.75% |
| (16.0, 96.0] | 310 |  24.2% |  -2.77% | -22.67% |
| (96.0, 775.6] | 311 |  19.9% |  -5.39% | -25.00% |
| (775.6, 92920.0] | 313 |  23.3% |  -5.55% | -25.00% |

## 3. Categorical / boolean feature breakdowns

### `above_sma_200`

| above_sma_200 | n | win_rate | avg_return |
|---|---|---|---|
| `False` | 816 |  22.2% |  -2.76% |
| `True` | 718 |  23.3% |  -3.88% |

### `above_sma_50`

| above_sma_50 | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 577 |  25.1% |  -2.65% |
| `False` | 985 |  21.1% |  -3.60% |

### `direction`

| direction | n | win_rate | avg_return |
|---|---|---|---|
| `BEARISH` | 820 |  23.7% |  -1.90% |
| `BULLISH` | 743 |  21.4% |  -4.76% |

### `flow_intent`

| flow_intent | n | win_rate | avg_return |
|---|---|---|---|
| `MECHANICAL` | 6 |  33.3% |  +8.27% |
| `HEDGING` | 273 |  24.9% |  -0.75% |
| `DIRECTIONAL` | 1229 |  22.3% |  -3.63% |
| `MIXED` | 55 |  16.4% |  -8.70% |

### `golden_cross`

| golden_cross | n | win_rate | avg_return |
|---|---|---|---|
| `False` | 649 |  23.7% |  -2.18% |
| `True` | 885 |  21.9% |  -4.09% |

### `is_premium_signal`

| is_premium_signal | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 448 |  23.7% |  -1.82% |
| `False` | 1115 |  22.2% |  -3.84% |

### `is_tradeable`

| is_tradeable | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 46 |  28.3% |  +2.32% |
| `False` | 1517 |  22.4% |  -3.43% |

### `move_overdone`

| move_overdone | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 148 |  26.4% |  -0.76% |
| `False` | 1415 |  22.2% |  -3.52% |

### `premium_bear_flow`

| premium_bear_flow | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 10 |  30.0% |  -1.63% |
| `False` | 1553 |  22.5% |  -3.27% |

### `premium_bull_flow`

| premium_bull_flow | n | win_rate | avg_return |
|---|---|---|---|
| `False` | 1525 |  22.9% |  -3.18% |
| `True` | 38 |  10.5% |  -6.72% |

### `premium_hedge`

| premium_hedge | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 273 |  24.9% |  -0.75% |
| `False` | 1290 |  22.1% |  -3.79% |

### `premium_high_atr`

| premium_high_atr | n | win_rate | avg_return |
|---|---|---|---|
| `False` | 1553 |  22.7% |  -3.26% |
| `True` | 10 |  10.0% |  -3.86% |

### `premium_high_rr`

| premium_high_rr | n | win_rate | avg_return |
|---|---|---|---|
| `True` | 170 |  27.1% |  -0.93% |
| `False` | 1393 |  22.0% |  -3.55% |

## 4. Premium-score stratification

Honest validation of the load-bearing `premium_score` formula. The live ledger only ever sees `premium_score >= 2`; this table shows what every score level produces under the same simulator.

| premium_score | n | win_rate | avg_return | median_return |
|---|---|---|---|---|
| 0 | 1115 |  22.2% |  -3.84% | -25.00% |
| 1 | 396 |  22.7% |  -2.48% | -16.69% |
| 2 | 51 |  31.4% |  +3.77% |  -6.56% |
| 3 | 1 |   0.0% | -25.00% | -25.00% |

## 5. Tree-based feature importance (chronological holdout)

**Train:** 1094 rows, scan_date 2026-02-18 → 2026-03-19
**Test:**  469 rows, scan_date 2026-03-19 → 2026-03-31

**GradientBoostingRegressor** (200 trees, depth 3, lr 0.05, seed=42)

- In-sample R²:        +0.4366
- Out-of-sample R²:    -0.0656
- OOS Spearman ρ:      +0.0398  _(rank correlation pred vs actual)_

**Top 15 features by GBM importance:**

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

**Shallow decision tree** (depth 3, min_samples_leaf=20, full data):

```
|--- risk_reward_ratio <= 0.425
|   |--- recommended_oi <= 12.500
|   |   |--- recommended_volume <= 266.000
|   |   |   |--- value: [0.005]
|   |   |--- recommended_volume >  266.000
|   |   |   |--- value: [-0.109]
|   |--- recommended_oi >  12.500
|   |   |--- put_vol_oi_ratio <= 0.068
|   |   |   |--- value: [0.119]
|   |   |--- put_vol_oi_ratio >  0.068
|   |   |   |--- value: [-0.085]
|--- risk_reward_ratio >  0.425
|   |--- call_uoa_depth <= 212698.500
|   |   |--- close_loc <= 0.296
|   |   |   |--- value: [0.219]
|   |   |--- close_loc >  0.296
|   |   |   |--- value: [0.068]
|   |--- call_uoa_depth >  212698.500
|   |   |--- call_dollar_volume <= 89675796.000
|   |   |   |--- value: [-0.010]
|   |   |--- call_dollar_volume >  89675796.000
|   |   |   |--- value: [-0.123]
```

## 6. Findings & next steps

**Features that rank in both top-10 GBM importance AND top-15 univariate separation** (the 'real signal' candidates):

- `recommended_delta`
- `rsi_14`
- `risk_reward_ratio`
- `macd_hist`
- `recommended_volume`

**Headline:** unconditional cohort of 1563 executed trades has avg return  -3.26% and win rate 22.6%.

**Next steps (out of scope for this study; user decision):**
- Compare overlap features against the current `premium_score` flags. If overlap features beat the score on the chronological holdout, draft a candidate V4 gate around them.
- Investigate any feature in the GBM top-10 with **negative** monotonicity in its quintile table — it may carry a non-linear edge that monotonic features miss.
- Sample-size check: if `n` for executed trades is small relative to feature count, re-run with a larger labeled cohort before making any policy changes.

