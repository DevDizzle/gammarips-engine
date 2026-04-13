### 📋 GammaRips Exploratory Pattern Discovery Prompt (XGBoost)

You are the Gemini CLI orchestrating the GammaRips Engine. We are entering a strict research phase to discover new structural alpha in our options data. 

Before taking action, you MUST assume the **`gammarips-researcher`** persona by reading `.gemini/roles/gammarips-researcher.md`. This means prioritizing out-of-sample discipline, rigorous hypothesis testing, and keeping research separate from production execution policy.

### The Objective
Currently, our `premium_score` relies on 5 core flags. We need to look closely at the `profitscout-fida8.profit_scout.overnight_signals_enriched` table and our historical outcome data to identify *new* non-linear patterns that signify explosive breakout trades. 

Your goal is to use a tree-based machine learning model (like XGBoost or a Random Forest classifier) as an exploratory tool to extract new, highly profitable decision rules (patterns) from the data.

### Task Execution Plan
To keep the main context window lean, you MUST delegate the heavy data extraction, model training, and backtesting tasks to the `generalist` sub-agent. Instruct the `generalist` to perform the following:

1. **Data Pipeline:**
   - Write a script to extract historical signals from `overnight_signals_enriched` and join them with their known outcomes (from `forward_paper_ledger_v3` or historical datasets).
   - Define the target variable: A "Win" (e.g., hitting a +40% target before a -25% stop within 3 days).

2. **Exploratory Modeling (XGBoost / Tree-based):**
   - Train an exploratory XGBoost or Random Forest model on the structural, technical, and options features (e.g., `close_loc`, `rsi_14`, `atr_pct`, `recommended_spread_pct`, `recommended_iv`).
   - Extract the **Feature Importance** to see what actually drives the wins.
   - Extract the **Top 3-5 specific decision tree paths** (e.g., "If close_loc > 0.8 AND rsi_14 < 60 AND volume > 500").

3. **Parallel Validation Backtests:**
   - Take the top 3 discovered patterns and run parallel historical backtests against the dataset to verify their expectancy and win rate.

### Required Output
Once the `generalist` completes the experiments, synthesize the results into a comprehensive Markdown report containing:
- **What We Did:** A brief summary of the dataset size, the features used, and the model parameters.
- **What We Found:** The specific decision tree rules (the new patterns) and their associated win rates/expectancy.
- **What We Learned:** High-level insights into what actually drives breakout trades in our dataset.
- **High-Value Actions:** Concrete recommendations on how we can codify these new patterns into a new `premium_score` flag or a specialized "V6 Structural Sniper" gate.