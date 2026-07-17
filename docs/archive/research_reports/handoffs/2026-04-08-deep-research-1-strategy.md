# Deep Research Prompt #1 — Signal-to-Profitable-Options Strategy

Paste everything below the `---` line into Google Deep Research.

---

## Background

I run a quantitative options-trading research pipeline that generates overnight directional signals on US equities and converts them into long-options trades the following day. I have a large body of empirical data showing the signal generator has a real directional edge on the underlying stocks, but the resulting options trades lose money in every bracket configuration I've tested. I need help diagnosing the gap and finding strategies that have actually worked for similar directional-signal-to-options-translation problems.

I am asking for **academic literature, practitioner research, and well-documented strategy patterns** — not generic options-trading advice. I have already done my own quantitative work and need outside perspective on what I'm missing.

## What the data looks like

I have two BigQuery tables.

### Raw scanner output: `overnight_signals` (71,687 rows, 2026-02-21 to 2026-04-07)

One row per (ticker, scan_date) for every stock that survives an overnight scoring scanner. Columns:

- Identification: `ticker`, `scan_date`, `scan_timestamp`, `direction` ('BULLISH'|'BEARISH'), `sector`, `industry`
- Underlying: `underlying_price`, `price_change_pct` (intraday move), `day_volume`
- Options flow: `call_dollar_volume`, `put_dollar_volume`, `total_options_dollar_volume`, `call_vol_oi_ratio`, `put_vol_oi_ratio`, `call_active_strikes`, `put_active_strikes`, `call_uoa_depth`, `put_uoa_depth` (UOA = unusual options activity)
- Scoring: `overnight_score` (raw scanner score), `original_score`, `cluster_size`, `cluster_boost` (signals get a boost when many tickers in the same sector show the same direction)
- Picked contract: `recommended_contract`, `recommended_strike`, `recommended_expiration`, `recommended_dte`, `recommended_mid_price`, `recommended_spread_pct`, `recommended_delta`, `recommended_gamma`, `recommended_theta`, `recommended_vega`, `recommended_iv`, `recommended_volume`, `recommended_oi`, `contract_score`
- Signal categorization: `signals` (array of qualitative tags from the scanner)

### Enriched / labeled subset: `overnight_signals_enriched` (2,316 rows, 2026-02-18 to 2026-04-06)

A filtered subset that adds AI-enriched features and outcome labels. Beyond the raw columns above, it has:

- Technical indicators on the underlying: `rsi_14`, `macd`, `macd_hist`, `atr_14`, `ema_21`, `sma_50`, `sma_200`, `above_sma_50`, `above_sma_200`, `golden_cross`, `stochd_14_3_3`, `atr_normalized_move`, `close_loc`, `dist_from_low`, `dist_from_high`, `support`, `resistance`, `high_52w`, `low_52w`
- AI/LLM enrichment: `enrichment_quality_score`, `reversal_probability`, `mean_reversion_risk`, `move_overdone` (bool), `flow_intent` (categorical: e.g. accumulation, distribution), `catalyst_type` (e.g. 'Technical Breakout', 'Analyst Upgrade', 'Guidance Cut', 'Earnings'), `catalyst_score`, `key_headline`, `news_summary`, `thesis`
- Hand-crafted "premium score" composite: `premium_score` (0-5 integer), built from boolean flags `premium_hedge`, `premium_high_rr`, `premium_bull_flow`, `premium_high_atr`, `premium_bear_flow`. `is_tradeable = (premium_hedge AND premium_high_rr) OR (premium_hedge AND premium_high_atr)`. `is_premium_signal` is similar.
- Risk metric: `risk_reward_ratio` (continuous, derived from technical levels)
- Realized outcomes (forward-fill labels at +1, +2, +3 trading days): `next_day_close`, `next_day_pct`, `day2_close`, `day2_pct`, `day3_close`, `day3_pct`, `peak_return_3d`, `outcome_tier` (categorical: 'home_run', 'win', 'flat', 'wrong'), `is_win`

The signal generation cadence is: scan runs overnight, signal is "surfaced" the next trading day, the trade is intended to be entered that same day at 15:00 ET and held for 2 trading days.

## What I've measured empirically

I labeled every signal under a frozen V3 simulator (entry at 15:00 ET on the day the signal is surfaced, +40% target / −25% stop, 2-day hold) and ran extensive analysis. Key findings, all on chronological holdouts (older 70% train, newer 30% OOS):

1. **The directional read on the underlying is genuinely good.** The stock moves in the predicted direction roughly 74% of the time over the 2-3 day window.
2. **The options trades lose money anyway.** Across the full 1552-signal cohort, the production bracket (`+40% / −25% / 2-day`) produces a 22.6% win rate and a negative average return. I swept 840 bracket variants (4 entry times × 7 targets × 5 stops × 6 holds, including no-target and no-stop variants and holds out to 15 trading days). **Zero of 840 are profitable in-sample. Zero of 840 are profitable out-of-sample.** The least-bad bracket (`15:55 entry / no target / −20% stop / 3-day hold`) is −1.99% OOS avg per trade.
3. **The "premium_score" composite filter is anti-predictive.** Higher premium_score signals have *worse* outcomes than lower ones. Specifically: `premium_score=0` cohort is −0.74%, `premium_score=1` is −5.86%, `premium_score=2` is −3.66%. The production filter (`premium_score >= 2 AND is_tradeable`) cuts the cohort to ~46 trades and produces an OOS avg of −5.53% — i.e. it is **3.54 percentage points worse than no filter at all**.
4. **The single most promising filter I found does not survive bootstrap validation.** I searched ~800 univariate and pairwise filters. The best survivor was `risk_reward_ratio >= 0.42`, which looked like +8.28% OOS on n=155. But: it's −3.37% on its own training set (n=471), breakeven (−0.48%) over the full history (n=626), and the +8.28% OOS is concentrated in the most recent ~78 trades (second OOS half = +17.51%, first OOS half = −1.06%). Almost certainly recency artifact, not a real edge.
5. **Liquidity filtering helps but doesn't fix it.** Restricting to `oi >= 50 AND volume >= 100 AND mid_price >= 1.00 AND spread_pct <= 0.20` (114 trades) gets the cohort from −2.15% to roughly breakeven (+0.96%), confirming that some apparent "edge" in the wider cohort was simulator-artifact wins on un-fillable contracts.
6. **The contract picker has a 41.6% NULL rate** on `recommended_strike` in the broader population — i.e. for many tradeable signals, the picker fails to find a contract it wants to recommend. The labeled cohort filters those out, but it's a known structural issue.
7. **Win/loss asymmetry on the option side is brutal.** Even when the underlying moves +1% in the right direction over 2 days, the option position frequently loses 5-10% due to a combination of theta decay, bid-ask slippage on the +2% entry slippage I model (matching live execution), and the picker selecting deeper OTM contracts than the move can support.

## What I've ruled out

- **Bracket optimization.** Every reasonable target/stop/hold combination has been tested, including no-stop and no-target variants and 15-day holds. None produce a profit on the full cohort or any large filtered subcohort.
- **Single-feature filtering.** I exhaustively scanned every numeric feature at decile thresholds in both directions plus all categorical/boolean features. No single filter passes bootstrap validation.
- **Two-feature filter combinations.** Same conclusion. The top combo I found was a recency artifact.
- **Premium score formula tweaks.** The premium score components are individually mostly noise; the composite is anti-predictive. No simple re-weighting fixes it.

## What I'm asking for

I want a synthesis-style report (NOT a generic options trading primer) that addresses the following questions, drawing on academic finance literature, quant practitioner publications, and well-documented options trading research:

### Tier 1 — most important questions

1. **The signal-to-options-translation problem in the literature.** When a directional stock signal has empirically demonstrated edge (~74% directional accuracy on the underlying over a 1-3 day horizon) but loses money when traded as long options, what are the documented causes? Theta decay is obvious; what are the less-obvious ones? Are there published frameworks for quantifying "how much underlying move do you need to overcome theta + slippage on a given contract" — i.e. the **breakeven move** as a function of DTE, delta, IV, and bid-ask spread? Specific papers, books, or blog posts to read.

2. **The right options-instrument for a 1-3 day directional read.** For a swing-trading horizon of 1-3 trading days with a directional thesis, what does the practitioner literature say about contract selection? Specifically:
   - **DTE choice:** what's the published wisdom on weeklies (3-7 DTE) vs short-term (14-21 DTE) vs front-month (30-45 DTE) for short-horizon directional trades? What's the tradeoff curve between gamma, theta, and slippage?
   - **Delta choice:** ITM vs ATM vs OTM. There's a well-known argument for high-delta (0.70+) ITM contracts on short-horizon directional trades — what's the empirical evidence?
   - **Vertical spreads as an alternative:** would a debit call/put spread fundamentally change the math for this problem? Quantitative comparison of long-call vs bull-call-spread expectancy on short-horizon directional signals.

3. **What features actually predict short-horizon options profitability** (as distinct from features that predict the underlying's direction). The literature on "options return predictability" (Goyal & Saretto, Cao & Han, Choy, Boyer & Vorkink, etc.) — what are the established cross-sectional predictors of *option* returns, separate from underlying-direction predictors? Specifically: implied vol rank/percentile, IV-vs-realized-vol skew, term structure slope, options skew/smile features, dealer gamma exposure (GEX), volume-weighted-average-strike features. Which of these are computable from publicly available options data, and which require dealer flow data I don't have?

4. **Overnight gap / pre-market scanner literature.** My signal pipeline is fundamentally an "overnight gap with options-flow confirmation" scanner. What does the academic and practitioner literature say about (a) edge persistence in overnight gap strategies post-2010, (b) the role of unusual options activity (UOA) as a filter, and (c) optimal entry timing relative to the gap (pre-market, opening cross, first 30 min, EOD)? Specific studies and their findings.

### Tier 2 — useful but secondary

5. **Survivorship and selection bias in self-built signal pipelines.** When a quant builds a multi-stage pipeline (raw scanner → enrichment → filter → execution), at what stage do most edges silently disappear? Are there published autopsies of pipeline-decay problems I could learn from?

6. **The "right answer" might be to NOT trade long options.** What does the literature say about when a directional signal should be traded as (a) shares/CFDs, (b) long options, (c) options spreads, (d) skipped entirely? Are there published decision frameworks for instrument selection given a known signal accuracy and edge size?

7. **Position sizing and Kelly under noisy edge estimates.** Given that the per-trade edge estimate has a wide bootstrap CI (the headline was +8.28% but the lower bound was +0.73%), what's the right Kelly fraction or position size? The standard Kelly formula assumes you know the edge precisely. Are there documented approaches for sizing under estimation uncertainty?

### Tier 3 — exploratory

8. **AI-enriched features in modern quant trading.** I have a column called `enrichment_quality_score` that, surprisingly, is *anti*-predictive in my data (lower-quality enrichment correlates with better trades). Is there published research on integrating LLM-generated features with quantitative features? Has anyone documented the failure mode where LLM enrichment overfits to publicly-available news and misses idiosyncratic edge?

9. **Practitioner blogs and YouTube channels worth following on this specific problem.** I am specifically looking for *quantitatively-oriented* options traders who publish backtests and walk through methodology, not generic "options education" or "wheel strategy" content. Names, channels, substacks.

## Output format I want

A structured report with:
- An executive summary of the most likely cause of my problem (1-2 paragraphs)
- A ranked list of the most promising research directions, each with: the question, the relevant literature, the specific change I should consider making to my pipeline
- A reading list of 5-15 specific papers, books, or articles, with short annotations explaining why each is relevant
- A list of features I should consider adding to `overnight_signals_enriched` based on the literature review, prioritized by expected impact
- Honest pushback if the literature suggests my pipeline architecture is fundamentally wrong for what I'm trying to do

I am not looking for a sales pitch on any specific tool or platform. I am not looking for generic options education. I have read the standard texts (Hull, Natenberg, Sinclair) and am looking for newer or more specialized work.
