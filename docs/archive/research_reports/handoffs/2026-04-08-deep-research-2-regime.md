# Deep Research Prompt #2 — Market Regime Context for the Test Period

Paste everything below the `---` line into Google Deep Research.

---

## What I need

I have a quantitative options-trading dataset spanning **roughly mid-February 2026 through early April 2026** (about 7 weeks). Within that window, my directional-options strategies have been losing money in every configuration I test, despite the signal generator showing ~74% directional accuracy on the underlying stocks. Before I conclude that the signals themselves are broken, I need to understand whether this period was an unusually difficult one for short-horizon directional options strategies, and whether there are observable market-regime variables I should be incorporating as features into my signal pipeline.

I am looking for a **rigorous, source-cited characterization of the US equity market and macro environment from late Q4 2025 through Q2 2026**, with specific attention to features that would matter for a 1-3 day directional swing trader using long options.

## What the data window actually covers

- `overnight_signals` table: 71,687 raw signals from 2026-02-21 through 2026-04-07
- `overnight_signals_enriched` table: 2,316 filtered signals from 2026-02-18 through 2026-04-06
- The labeled subset I've been doing analysis on covers ~1,552 trades from this window with realized 2-day options outcomes

The user's hypothesis (which is what motivates this prompt) is that the broader market context starting in **late Q4 2025 and continuing through Q1/Q2 2026** has been unusually choppy / range-bound / news-whipsawed, including geopolitical events such as **Iran-related conflict**, and that this regime may be incompatible with short-horizon directional options strategies even when the underlying directional read is correct.

## What I want to know

### Tier 1 — direct context I need

1. **Daily characterization of the US equity market from October 2025 through April 2026.** What was the SPX/QQQ trend, drawdown, and realized volatility over this period? Identify and date any drawdown events larger than 5%, any ≥3-day chop ranges (sequences of indecisive sideways action), and any sharp single-day reversals. Use the most authoritative sources you can find — financial news archives, Federal Reserve data, market structure publications.

2. **Volatility regime over the same window.** What did the VIX, VVIX, SKEW index, and realized vs implied volatility look like? Were there sustained periods of:
   - High implied vol with low realized vol (= vol crush risk for long options)?
   - Inverted term structure (= short-term IV > long-term IV, often a signal of fear)?
   - Compressed realized vol (= directional moves too small to overcome theta on long options)?
   Specific dates and levels where possible.

3. **Major news events and macro catalysts in this window** that would have affected short-horizon directional strategies:
   - **Iran / Middle East conflict events.** The user specifically mentioned this. Date, characterize, and assess the market impact of any Iran-related military or diplomatic events from late 2025 through Q2 2026. How long did the market take to digest each shock?
   - **Federal Reserve actions.** FOMC meetings, dot plot changes, rate decisions, and any inter-meeting communications.
   - **Earnings season impact.** Q4 2025 earnings (reported Jan-Feb 2026) and Q1 2026 earnings (reported Apr-May 2026). Were there sector-specific earnings trends? Were there major outliers that caused sector rotation?
   - **Tariff / trade policy news.** Any major US trade actions in this window.
   - **Other geopolitical or fiscal events** that moved the market.

4. **Sector rotation and breadth.** During this period, was the rally/selloff broad or narrow? Were specific sectors (energy on Iran news, tech on rate moves, regional banks, etc.) doing the heavy lifting? A scanner-based signal pipeline that doesn't account for sector regime can show good underlying directional accuracy in aggregate while losing money because the picks are concentrated in the wrong sector at the wrong time.

### Tier 2 — historical comparison

5. **Historical periods that look similar to the late-2025-to-early-2026 environment** (chop, range-bound, news-driven whipsaw, geopolitical overhang). What did short-horizon directional options strategies do during those analog periods? Specific examples I'd find useful:
   - The 2015-2016 China devaluation / Brexit lead-up chop
   - The 2018 Q4 selloff and 2019 Q1 chop
   - The 2022 H1 rate-shock chop
   - Any other periods with sustained sideways action and elevated realized volatility
   What's the published evidence on directional swing trading performance during regimes like these?

6. **Regime indicators that could be added as features.** What are the well-documented quantitative regime variables that distinguish "trending markets where directional strategies work" from "choppy markets where they don't"? I'm looking for things I could compute daily and add as a feature column. Candidates I'm aware of but want validated:
   - VIX level and rate of change
   - VIX term structure slope (e.g. VX1/VX2)
   - SPX 20-day realized volatility
   - SPX 20-day ADX (trend strength)
   - Breadth indicators: % of S&P stocks above their 50-day MA, advance/decline line
   - Sector dispersion / correlation regime
   - Hindenburg Omen or similar deterioration signals
   - Credit spreads (HYG vs IEF, or specific OAS levels)
   Which of these are best-documented as regime classifiers? Are there published thresholds for what "choppy" looks like quantitatively?

### Tier 3 — strategic implications

7. **What kinds of strategies historically *do* work during choppy / news-driven regimes?** The default answer is "wait for trend to return" — but I need to actively make money trading. What's the literature on:
   - Mean-reversion strategies on short horizons during chop regimes
   - Volatility-selling strategies (short premium, iron condors, credit spreads) during high-IV-low-RV regimes
   - News-driven event-window strategies (event-time anchoring rather than calendar-time)
   - Pair trades / sector-relative strategies that are regime-neutral
   What does the literature say about expected Sharpe for each during regimes that look like late-2025/early-2026?

8. **Should I be turning my long-options strategy off during certain regimes?** Is there documented evidence on regime-conditional strategy gating — i.e. a meta-rule like "only take long-options directional trades when VIX < X and realized vol > Y and the SPX 20-day ADX > Z"? Specific published decision rules.

## Output format I want

A structured report with:
- An executive summary characterizing the late-Q4-2025 through Q2-2026 market regime in 2-3 paragraphs
- A timeline of major events affecting US equities from October 2025 through April 2026, with dates, descriptions, and short impact assessments
- A quantitative table of regime indicators (VIX avg, realized vol avg, max drawdown, % of trading days that were ranged vs trending) for this window vs a longer-term baseline
- An honest answer to the question "was this an unusually difficult period for short-horizon directional options trading?" — yes/no with evidence
- A prioritized list of regime features I should add to my signal pipeline, with formulas or data sources for each
- A short reading list of 5-10 sources I should bookmark for ongoing regime monitoring (Fed publications, market structure newsletters, vol research, etc.)

Cite sources for everything. Where you have to reason from limited data, say so explicitly. I am specifically interested in **what has actually happened** in this window, not what might happen — I'll do my own forward modeling once I understand the regime I've been trading in.

## One important caveat about the date

The window I'm asking about (late 2025 through Q2 2026) may include dates that are in the model's training cutoff or beyond it. For events after your knowledge cutoff, please:
1. Be explicit about which events you are uncertain about due to recency
2. Use the most recent reliable sources you can access
3. Flag any claims that are extrapolations rather than documented facts

I would rather you tell me "I don't have reliable information about the Iran-related events in March 2026" than guess.
