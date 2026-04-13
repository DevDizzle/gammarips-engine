# Premium Score 1 Structural Analysis & V6 Hypothesis

## Date: April 1, 2026
## Status: Research Completed / V6 Proposed

## Context
After establishing V3 (`premium_score >= 2`, moderate liquidity) as the canonical forward-paper strategy, we hypothesized that we could capture the massive volume of `premium_score = 1` signals by applying ultra-high liquidity filters (V5).

Exhaustive minute-by-minute backtesting of the `+40% / -25%` execution bracket on `premium_score = 1` signals proved that liquidity alone cannot compensate for lower ML conviction. Across all liquidity tiers, the expectancy remained negative (avg returns between -0.69% and -8.80%), leading to the cancellation of the V5 deployment.

## The Structural Analysis
To understand if `premium_score = 1` signals had any redeeming qualities, we analyzed the structural and technical features of the **Winners** versus the **Losers** from a 60-day historical dataset (188 executions with Vol >= 250).

### Key Findings

1. **The Mean Reversion Trap (RSI & MACD)**
   - **Winners:** Average RSI of 43.31, MACD Histogram -0.078
   - **Losers:** Average RSI of 39.84, MACD Histogram -0.270
   - **Takeaway:** Signals on underlyings that are already deeply oversold (RSI < 40) or overbought (RSI > 60) tend to mean-revert and hit the `-25%` stop loss. Winning signals occur when the trend is established but not over-extended.

2. **Daily Closing Location (`close_loc`)**
   - **Winners:** Median 0.20
   - **Losers:** Median 0.23
   - **Takeaway:** Winners close in the bottom 20% of their daily range (for Bearish signals), indicating absolute structural weakness going into the overnight session.

3. **Volatility Tax (`atr_pct`)**
   - **Winners:** Average daily ATR is 5.7% of the underlying price.
   - **Losers:** Average daily ATR is 6.2% of the underlying price.
   - **Takeaway:** High-beta, highly volatile underlyings (ATR > 6%) frequently trigger the tight `-25%` option stop loss due to intraday noise.

## The V6 Hypothesis (Structural Premium Wrapper)
Instead of filtering `premium_score = 1` signals by liquidity, **V6** will filter them by pure structural momentum and volatility constraints.

**Proposed V6 Gates:**
1. **Conviction:** `premium_score >= 1`
2. **Structural Momentum:** `close_loc < 0.25` (Bearish) or `> 0.75` (Bullish)
3. **Mean Reversion Gate:** `40 <= RSI_14 <= 60` (Reject over-extended setups)
4. **Volatility Cap:** `atr_pct < 0.05` (Reject erratic underlyings)
5. **Execution:** Standard mechanical bracket (`+40% target / -25% stop`)

## Next Steps
- Leave V3 as the primary strategy and V4 running as an experimental parallel tracker.
- Future agents/quants can implement the V6 hypothesis by referencing this report and running `backtesting_and_research/analyze_premium_winners.py` to validate out-of-sample before deploying `forward-paper-trader-v6`.