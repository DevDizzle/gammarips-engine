# GammaRips Exploratory Pattern Discovery (Tree-Based Modeling)

## What We Did
We extracted historical trading signals from the BigQuery table `profitscout-fida8.profit_scout.overnight_signals_enriched` and joined them with official outcomes from `profitscout-fida8.profit_scout.forward_paper_ledger_v3`. 

- **Target Variable:** A "Win" was defined as realizing a return of **>= 35%** (a practical proxy for hitting a +40% target with slight slippage). 
- **Dataset Size:** 26 trades from the V3 forward paper ledger.
- **Features Used:** `close_loc`, `rsi_14`, `atr_14`, `recommended_spread_pct`, `recommended_iv`, `recommended_volume`, `premium_score`, `recommended_dte`, `underlying_price`, `macd`, `dist_from_low`, and `dist_from_high`. Empty columns were imputed using median values.
- **Model Parameters:** We used an exploratory **Random Forest** (100 estimators, max depth 5, balanced class weights) to extract pure feature importance and a shallow **Decision Tree** (max depth 4, balanced) to extract specific, human-readable logic paths.

## What We Found
The overall win rate for hitting the target in this cohort was **42.3%**.

### 1. Feature Importances (Random Forest)
The top structural and technical drivers of explosive trades were:
1. `recommended_dte` (0.1918)
2. `recommended_iv` (0.1246)
3. `dist_from_high` (0.0977)
4. `recommended_volume` (0.0939)
5. `atr_14` (0.0918)
6. `rsi_14` (0.0868)

### 2. Extracted Decision Rules (New Patterns)
The decision tree identified a highly profitable "Structural Sniper" sub-segment centered heavily on contract maturity and momentum.

**Pattern 1: The Mean Reversion Sweet Spot (Shorter DTE + Cooling Momentum)**
- **Rule:** `recommended_dte <= 28.5` AND `rsi_14 <= 53.0`
- **Result:** This single combined path captured 10 trades, achieving an **80% win rate** with an average realized return of **+31%**. 
- **Sub-segment:** Within this group, if `close_loc > 0.21`, the win rate historically jumped to 100% (5 out of 5) with an exact +40% average return. If `close_loc <= 0.21`, it maintained a solid 60% win rate (+22% average return).

**Pattern 2: The Stalled/Extended Traps (Longer DTE or Overheated RSI)**
- **Rule A:** `recommended_dte <= 28.5` AND `rsi_14 > 53.0` (Win Rate: 28.5%, Avg Return: -3.5%)
- **Rule B:** `recommended_dte > 28.5` (Win Rate: 11.1%, Avg Return: -6.4%)

## What We Learned
- **DTE Over Everything:** Surprisingly, `recommended_dte` was the strongest predictor of a +40% move in 3 days. Contracts expiring further out (> 28 days) simply do not have the gamma convexity required to hit a +40% target within a 3-day hold window.
- **Overbought Traps:** Trades entered when `rsi_14` is above 53 struggle. Explosive options trades in our dataset require "room to run"—entering when momentum is already elevated prevents the underlying from generating the necessary structural push to trigger a gamma rip.
- **Context:** The ideal setup is a highly liquid contract expiring in 2-4 weeks, where the underlying stock has cooled off (`rsi_14` ~40-50) and is not pinned near its absolute lows (`close_loc > 0.21`).

## High-Value Actions
To convert these insights into production-ready execution logic, I recommend the following:

1. **Implement a "Gamma Convexity Gate":** Modify the downstream execution policy to strictly filter out trades where `recommended_dte > 28` if the strategy requires a +40% target in 3 days. The math shows these contracts move too slowly for our bracket order.
2. **Create a "V6 Structural Sniper" Strategy/Gate:**
   We should codify a new `premium_score` or execution flag specifically checking for this exact tree logic:
   - `recommended_dte BETWEEN 14 AND 28` (14 is our existing minimum gate)
   - `rsi_14 <= 55.0`
   - `close_loc > 0.20`
   
   *Next Step:* I recommend we isolate these logic parameters and run a large-scale backtest (`sweep_v6_structural_sniper.py`) across our historical datasets to confirm the expectancy out-of-sample before adding it to production.

### 3. V6 Structural Sniper Backtest Results
We executed `sweep_v6_structural_sniper.py` on the broader `overnight_signals_enriched` dataset, removing the `is_tradeable` constraint to test the raw tree logic out-of-sample across 225 simulated executions. 

**Bracket:** +40% Target / -25% Stop
**Max Hold:** 3 Days
**Entry Time:** 15:00 ET

**Results:**
- **Total Trades:** 225
- **Win Rate:** 33.33%
- **Avg Return:** -3.76%
- **Hits Target:** 37
- **Hits Stop:** 102
- **Timeouts:** 86

**Conclusion:**
The raw tree logic (`recommended_dte BETWEEN 14 AND 28`, `rsi_14 <= 55.0`, `close_loc > 0.20`) has a **negative expectancy** out-of-sample without further gating. The initial 80% win rate was heavily overfitted to a small cohort of already-filtered V3 trades. To salvage this setup, we must implement the proposed "V6 Structural Premium Wrapper" which introduces strict volatility caps (`atr_pct < 0.05`), explicit mean-reversion bands (`RSI_14` between 40-60), and momentum extremes, rather than deploying the raw tree logic to production.