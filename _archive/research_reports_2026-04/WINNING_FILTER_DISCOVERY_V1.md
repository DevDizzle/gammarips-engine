# Winning Filter Discovery V1

**Source per-signal returns:** `/tmp/sweep_signal_detail_v1.pkl` (bracket: `15:55 / no target / -20% stop / 3-day hold`)  
**Source features:** `profitscout-fida8.profit_scout.signals_labeled_v1`  
**Cohort size:** 1552 signals (464 OOS)  
**Bracket source:** `BRACKET_SWEEP_V1.md` best variant  
**Filter floor:** n ≥ 100 total AND OOS n ≥ 30  

## 1. Baselines

| filter | n | OOS n | avg | win% | **OOS avg** | **OOS win%** |
|---|---|---|---|---|---|---|
| ALL (no filter) | 1552 | 464 |   -2.15% |  21.3% | **  -1.99%** | ** 19.6%** |
| PRODUCTION (`premium_score >= 2 AND is_tradeable`) | 46 | 7 |   -1.88% |  23.9% | **  -5.53%** | ** 14.3%** |

_Production filter delta vs. unfiltered (OOS avg): **-3.54 percentage points**._  Negative = production filter is destroying edge.

## 2. Top 30 univariate filters by OOS avg_return

All numeric/categorical/boolean filters that survived the n-floor, ranked by chronological-holdout OOS avg_return. The top of this list is where any single-feature edge lives.

| filter | n | OOS n | avg | win% | **OOS avg** | **OOS win%** |
|---|---|---|---|---|---|---|
| `move_overdone` == True | 148 | 31 |   -1.64% |  25.0% | ** +14.55%** | ** 35.5%** |
| `dist_from_low` <= 0.08102 (q20) | 246 | 35 |   -2.19% |  24.4% | ** +11.31%** | ** 40.0%** |
| `enrichment_quality_score` <= 6.4 (q10) | 167 | 48 |   -1.01% |  21.0% | ** +10.12%** | ** 29.2%** |
| `recommended_delta` >= 0.4984 (q90) | 156 | 48 |   -1.71% |  23.1% | **  +9.74%** | ** 31.2%** |
| `catalyst_type` == 'Technical Breakout' | 212 | 60 |   +2.38% |  20.3% | **  +9.42%** | ** 23.3%** |
| `call_vol_oi_ratio` >= 0.7962 (q90) | 156 | 52 |   -1.64% |  23.1% | **  +9.15%** | ** 28.8%** |
| `risk_reward_ratio` >= 0.42 (q60) | 626 | 155 |   -0.48% |  25.2% | **  +8.28%** | ** 31.6%** |
| `recommended_delta` >= 0.4414 (q80) | 311 | 97 |   -0.28% |  24.4% | **  +7.54%** | ** 28.9%** |
| `reversal_probability` >= 0.65 (q90) | 195 | 48 |   -1.43% |  25.1% | **  +7.47%** | ** 29.2%** |
| `underlying_price` >= 379.7 (q90) | 156 | 38 |   -0.07% |  22.4% | **  +7.13%** | ** 21.1%** |
| `rsi_14` >= 69.83 (q90) | 156 | 43 |  +11.56% |  28.2% | **  +7.02%** | ** 20.9%** |
| `recommended_volume` <= 15 (q10) | 159 | 46 |   +3.02% |  26.4% | **  +6.74%** | ** 30.4%** |
| `put_vol_oi_ratio` >= 0.7893 (q90) | 156 | 55 |   -2.40% |  22.4% | **  +6.64%** | ** 25.5%** |
| `enrichment_quality_score` <= 6.8 (q20) | 362 | 96 |   +0.75% |  23.5% | **  +6.60%** | ** 26.0%** |
| `call_active_strikes` <= 5 (q20) | 355 | 86 |   -0.60% |  24.5% | **  +6.51%** | ** 26.7%** |
| `put_vol_oi_ratio` <= 0.164 (q30) | 466 | 106 |   -0.77% |  22.5% | **  +6.49%** | ** 29.2%** |
| `put_active_strikes` <= 7 (q30) | 531 | 123 |   +0.56% |  24.7% | **  +6.25%** | ** 31.7%** |
| `put_active_strikes` <= 9 (q40) | 651 | 160 |   -0.04% |  23.7% | **  +6.12%** | ** 28.1%** |
| `put_dollar_volume` <= 2.487e+06 (q30) | 466 | 126 |   +1.34% |  23.0% | **  +5.95%** | ** 27.8%** |
| `dist_from_low` <= 0.4624 (q60) | 738 | 86 |   -3.01% |  23.0% | **  +5.87%** | ** 31.4%** |
| `atr_14` >= 20.98 (q90) | 156 | 36 |   -1.32% |  19.9% | **  +5.80%** | ** 19.4%** |
| `mean_reversion_risk` >= 0.28 (q90) | 163 | 44 |   -0.32% |  23.3% | **  +5.80%** | ** 25.0%** |
| `call_active_strikes` <= 10 (q40) | 654 | 170 |   +1.27% |  25.4% | **  +5.78%** | ** 28.8%** |
| `risk_reward_ratio` >= 0.27 (q50) | 783 | 198 |   -1.63% |  23.5% | **  +5.65%** | ** 27.8%** |
| `recommended_delta` >= 0.3718 (q70) | 466 | 134 |   -1.41% |  21.9% | **  +5.60%** | ** 27.6%** |
| `put_dollar_volume` <= 3.686e+05 (q10) | 156 | 33 |   +5.17% |  26.9% | **  +5.35%** | ** 33.3%** |
| `dist_from_high` >= 0.8512 (q70) | 370 | 49 |   +0.33% |  21.6% | **  +5.32%** | ** 30.6%** |
| `dist_from_low` <= 0.3337 (q50) | 616 | 74 |   -2.45% |  23.9% | **  +5.25%** | ** 31.1%** |
| `reversal_probability` >= 0.3 (q70) | 477 | 122 |   +0.53% |  22.2% | **  +5.19%** | ** 23.0%** |
| `macd_hist` >= 0.9592 (q80) | 311 | 54 |   -0.42% |  20.3% | **  +5.10%** | ** 18.5%** |

## 3. Bottom 10 univariate filters (anti-edge — what to AVOID)

Same set, ranked the opposite way. If any of these match the production filter conditions, that's a smoking gun for why production loses money.

| filter | n | OOS n | avg | win% | **OOS avg** | **OOS win%** |
|---|---|---|---|---|---|---|
| `recommended_delta` <= -0.4685 (q10) | 156 | 44 |   -8.55% |  19.9% | ** -13.92%** | **  6.8%** |
| `recommended_iv` >= 0.9976 (q90) | 155 | 32 |   +0.32% |  16.1% | ** -13.90%** | **  9.4%** |
| `recommended_delta` <= -0.416 (q20) | 311 | 92 |   -9.69% |  18.3% | ** -13.68%** | **  8.7%** |
| `call_active_strikes` >= 52.9 (q90) | 156 | 60 |   -5.37% |  17.9% | ** -13.64%** | **  6.7%** |
| `catalyst_type` == 'Analyst Downgrade' | 155 | 43 |   -5.11% |  21.9% | ** -13.20%** | **  9.3%** |
| `put_active_strikes` >= 50 (q90) | 159 | 54 |   -7.38% |  15.7% | ** -13.05%** | **  5.6%** |
| `price_change_pct` <= -5.659 (q10) | 156 | 59 |   -8.52% |  18.6% | ** -12.94%** | ** 11.9%** |
| `macd` <= -10.74 (q10) | 156 | 30 |   -5.31% |  19.2% | ** -12.27%** | **  6.7%** |
| `put_uoa_depth` >= 1.01e+08 (q90) | 156 | 32 |   -8.32% |  15.4% | ** -12.23%** | **  6.2%** |
| `catalyst_type` == 'Guidance Cut' | 113 | 32 |   -6.55% |  23.0% | ** -11.48%** | ** 12.5%** |

## 4. Top 30 two-feature combinations

Pairwise intersections of the top 20 univariate filters. Combinations that survive the n-floor (most won't — intersections shrink the cohort fast).

| filter | n | OOS n | avg | win% | **OOS avg** | **OOS win%** |
|---|---|---|---|---|---|---|
| `risk_reward_ratio` >= 0.42 (q60)  AND  `enrichment_quality_score` <= 6.8 (q20) | 133 | 34 |   +2.86% |  27.8% | ** +27.86%** | ** 44.1%** |
| `enrichment_quality_score` <= 6.8 (q20)  AND  `put_active_strikes` <= 9 (q40) | 171 | 30 |   +4.81% |  24.6% | ** +26.53%** | ** 36.7%** |
| `recommended_delta` >= 0.4414 (q80)  AND  `put_active_strikes` <= 9 (q40) | 153 | 42 |   +5.49% |  27.5% | ** +25.93%** | ** 40.5%** |
| `call_vol_oi_ratio` >= 0.7962 (q90)  AND  `put_active_strikes` <= 9 (q40) | 106 | 30 |   +2.76% |  27.4% | ** +23.43%** | ** 40.0%** |
| `enrichment_quality_score` <= 6.8 (q20)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 126 | 33 |   +5.67% |  23.8% | ** +21.66%** | ** 33.3%** |
| `recommended_delta` >= 0.4414 (q80)  AND  `put_active_strikes` <= 7 (q30) | 136 | 35 |   +3.32% |  27.2% | ** +19.47%** | ** 40.0%** |
| `risk_reward_ratio` >= 0.42 (q60)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 183 | 55 |   +1.74% |  24.0% | ** +18.44%** | ** 38.2%** |
| `risk_reward_ratio` >= 0.42 (q60)  AND  `recommended_delta` >= 0.4414 (q80) | 146 | 47 |   -0.26% |  26.0% | ** +17.39%** | ** 42.6%** |
| `call_active_strikes` <= 5 (q20)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 140 | 40 |   +0.64% |  24.3% | ** +16.42%** | ** 37.5%** |
| `risk_reward_ratio` >= 0.42 (q60)  AND  `put_active_strikes` <= 9 (q40) | 249 | 64 |   -0.84% |  23.7% | ** +13.88%** | ** 34.4%** |
| `risk_reward_ratio` >= 0.42 (q60)  AND  `put_vol_oi_ratio` <= 0.164 (q30) | 210 | 45 |   -3.75% |  22.4% | ** +13.37%** | ** 37.8%** |
| `risk_reward_ratio` >= 0.42 (q60)  AND  `put_active_strikes` <= 7 (q30) | 206 | 51 |   -1.61% |  23.8% | ** +12.92%** | ** 39.2%** |
| `call_active_strikes` <= 5 (q20)  AND  `put_active_strikes` <= 7 (q30) | 247 | 60 |   -0.94% |  23.1% | ** +11.83%** | ** 33.3%** |
| `put_vol_oi_ratio` <= 0.164 (q30)  AND  `put_active_strikes` <= 7 (q30) | 256 | 54 |   +1.42% |  25.8% | ** +11.81%** | ** 38.9%** |
| `recommended_delta` >= 0.4414 (q80)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 163 | 45 |   +1.52% |  25.2% | ** +11.39%** | ** 31.1%** |
| `dist_from_low` <= 0.08102 (q20)  AND  `dist_from_low` <= 0.4624 (q60) | 246 | 35 |   -2.19% |  24.4% | ** +11.31%** | ** 40.0%** |
| `put_active_strikes` <= 9 (q40)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 380 | 94 |   +1.99% |  23.9% | ** +10.95%** | ** 31.9%** |
| `call_active_strikes` <= 5 (q20)  AND  `put_active_strikes` <= 9 (q40) | 290 | 73 |   -0.78% |  23.4% | ** +10.76%** | ** 30.1%** |
| `put_active_strikes` <= 7 (q30)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 332 | 77 |   +2.08% |  25.0% | ** +10.41%** | ** 36.4%** |
| `enrichment_quality_score` <= 6.4 (q10)  AND  `enrichment_quality_score` <= 6.8 (q20) | 167 | 48 |   -1.01% |  21.0% | ** +10.12%** | ** 29.2%** |
| `recommended_delta` >= 0.4984 (q90)  AND  `recommended_delta` >= 0.4414 (q80) | 156 | 48 |   -1.71% |  23.1% | **  +9.74%** | ** 31.2%** |
| `put_vol_oi_ratio` <= 0.164 (q30)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 274 | 60 |   +2.79% |  24.1% | **  +9.11%** | ** 33.3%** |
| `rsi_14` >= 69.83 (q90)  AND  `put_dollar_volume` <= 2.487e+06 (q30) | 108 | 30 |  +12.17% |  28.7% | **  +8.66%** | ** 20.0%** |
| `recommended_delta` >= 0.4414 (q80)  AND  `put_vol_oi_ratio` <= 0.164 (q30) | 135 | 32 |   -1.15% |  28.1% | **  +7.98%** | ** 40.6%** |
| `risk_reward_ratio` >= 0.42 (q60)  AND  `dist_from_low` <= 0.4624 (q60) | 303 | 30 |   -4.21% |  24.1% | **  +7.10%** | ** 36.7%** |
| `put_vol_oi_ratio` <= 0.164 (q30)  AND  `put_active_strikes` <= 9 (q40) | 302 | 66 |   -0.59% |  23.2% | **  +7.05%** | ** 33.3%** |
| `put_active_strikes` <= 7 (q30)  AND  `put_active_strikes` <= 9 (q40) | 531 | 123 |   +0.56% |  24.7% | **  +6.25%** | ** 31.7%** |
| `put_active_strikes` <= 9 (q40)  AND  `dist_from_low` <= 0.4624 (q60) | 382 | 45 |   -1.14% |  24.9% | **  +3.41%** | ** 35.6%** |
| `put_active_strikes` <= 7 (q30)  AND  `dist_from_low` <= 0.4624 (q60) | 323 | 34 |   -0.98% |  24.8% | **  +1.51%** | ** 41.2%** |

## 5. Recommendation

**Best filter found:** ``risk_reward_ratio` >= 0.42 (q60)  AND  `enrichment_quality_score` <= 6.8 (q20)`
- n = 133 (34 OOS)
- Full-cohort avg =   +2.86%, win% =  27.8%
- **OOS avg =  +27.86%, OOS win% =  44.1%**

_Compare to production OOS avg =   -5.53%._

