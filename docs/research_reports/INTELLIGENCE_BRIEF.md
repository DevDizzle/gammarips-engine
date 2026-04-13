# Intelligence Brief — GammaRips Signal Research

> **Read this first.** Two-page top-of-stack briefing for any session picking up the strategy work cold. Evidence base: `FINDINGS_LEDGER.md`. Strategy menu: `STRATEGY_PLAYBOOK.md`. Live handoff: `../../NEXT_SESSION_PROMPT.md`.

## 2026-04-08 update — instrumentation pivot and the first three-way-positive

The research posture changed fundamentally on 2026-04-08. A session that started out as "run H1 (underlying relabel) with an SPY benchmark" produced three results that together reframed the entire problem:

1. **H1 was executed.** `scripts/research/relabel_underlying_v1.py` computed stock-side returns at 1×/2×/3×/5× leverage for all 1563 labeled signals plus an SPY benchmark over the same windows. Full report in `UNDERLYING_VS_OPTIONS_V1.md`. The headline finding: option bleed on the labeled cohort was −3.26% while stock 1× bleed was only −0.33% and SPY was −0.21% — **the options instrument alone accounts for ~89% of the bleed (−2.93 pp/trade)**. The volatility-idiosyncratic trap from Cao & Han is confirmed on our own data. But the signal alone has no measurable directional alpha in this single-regime dataset (alpha vs SPY: −0.16%), so a pure pivot to leveraged stock on the unfiltered cohort is not justified either.
2. **The V3.1 gate produces a fundamentally different cohort.** On the 29 real V3.1 trades the trader actually executed between 2026-02-19 and 2026-03-20, the cohort-wide numbers flip sign on every axis: option +2.91%, stock 1× +0.36%, SPY +0.01%, **directional alpha vs SPY +0.35%**. SPY floor is essentially zero, which means unlike the earlier bearish-VIX-20-25 subset from the labeled cohort (which turned out to be pure market beta), the V3.1-gate result is not SPY-drift capture. This is the **first three-way-positive (option, stock, alpha) in the entire research series**. Sample size is 29, CI still includes zero, and this is not validation — it is the first cohort-level result that is not contradictory. Full report: `BENCHMARKING_VALIDATION_V1.md`.
3. **The decision was to stop searching and start instrumenting.** The repeated filter-search → top-1 candidate → OOS collapse loop (most recently `filt_rrr`) is a methodological dead end on a single-regime 31-day dataset. We will not resolve it by ranking more candidates. Instead, `forward_paper_ledger_v3_hold2` was extended with 10 benchmarking columns that write inline on every trade (`underlying_return`, `spy_return_over_window`, `hv_20d_entry`, `VIX_at_entry`, `vix_5d_delta_entry`, `iv_rank_entry`, `iv_percentile_entry`, plus entry/exit prices for both underlying and SPY). The FMP dependency was retired (legacy endpoint deprecation); VIX now comes from FRED, SPY from Polygon. A daily Polygon IVR cache job was deployed (`polygon-iv-cache-daily` Cloud Scheduler → `/cache_iv` endpoint on `forward-paper-trader`, writes to `polygon_iv_history`). The existing 29 ledger rows were backfilled. Full context: `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`.

**Also on 2026-04-08: the war ended.** The Iran-shock ceasefire is a genuine regime boundary. By the next pickup session in ~4-6 weeks, the ledger should have ~50-60 total trades — roughly half pre-war, half post-war — the first two-regime dataset we will have ever had. The entire strategy posture until the pickup is: **V3.1 gate frozen, no filter searches permitted, let the ledger accumulate self-benchmarked post-war data, revisit at N≥100 with pre-committed hypotheses**. See `NEXT_SESSION_PROMPT.md` for the decision tree and the four pre-committed tests.

**New hypothesis added to the open list below: H9 — Does the V3.1 gate's three-way-positive expectancy survive the war → post-war regime transition?**

## Where we are

We have a signal generator (`overnight_signals_enriched`) that hits **~74% directional accuracy on the underlying** over a 1-3 day window. We have built a forward paper trader that converts those signals into long options trades. The trader loses money in **every** bracket configuration we have tested. This is not a bracket-tuning problem.

Two external Deep Research reports (Apr 2026) reframe the problem (full text in `handoffs/2026-04-08-deep-research-1-strategy-output.md` and `handoffs/2026-04-08-deep-research-2-regime-output.md`):

1. **Volatility-idiosyncratic trap (Cao & Han 2013, JFE).** Overnight gap and UOA scanners systematically select stocks with extreme idiosyncratic volatility. Options on those stocks are systematically overpriced by market makers as compensation for hedging difficulty. We are buying the most overpriced volatility in our universe at the moment when the variance risk premium is highest. The directional read is real; the option premium consumes the edge before the move can play out.
2. **The Feb–Apr 2026 dataset is regime-confounded.** The labeled cohort sits inside a once-in-decade geopolitical shock window: Operation Epic Fury (Feb 28), Strait of Hormuz closure (Mar 4), Brent → $120/bbl, VIX peak 35.3, IV–RV spread ~9pts (3× normal), VIX term structure backwardation in March, V-shaped reversal Mar 31 (+2.91%). We **cannot** conclude the signal generator is broken from this cohort alone — every conclusion of the form "filter X works" or "bracket Y fails" is conflated with "this regime broke long-options strategies in general."

The open question is: **does the directional signal have real edge on a tradeable instrument**, where "tradeable instrument" probably is not naked long options.

## What we know is true

- **Directional accuracy on the underlying ≈ 74%** over the 1-3 day signal window. (`FINDINGS_LEDGER.md` §Cohort)
- **0/840 bracket variants are profitable in-sample, 0/840 out-of-sample.** Best is `15:55 / no target / -20% stop / 3-day hold` at **−1.99% OOS** on n=464. (§Bracket Sweeps)
- **Premium_score is anti-predictive on the unconditioned cohort.** Score 0 → −3.84%, Score 1 → −2.48%, Score 2 → +3.77% (n=51 only — small sample, treat with caution). The production filter (`premium_score >= 2 AND is_tradeable`) on the V1-best bracket produces **−5.53% OOS, n=46**, which is **−3.54 pp worse than no filter at all**. (§Premium-Score Validation)
- **The `filt_rrr` candidate is a regime artifact, not an edge.** Headline +8.28% OOS collapses to −3.37% on its own training set, −0.48% over the full history, and the entire OOS lift comes from the second walk-forward half (+17.51%) which corresponds exactly to the Mar 26–Apr 6 V-bottom recovery from the Iran shock. (§Filter Discovery, §Bootstrap Validation)
- **Liquidity gating helps but does not fix it.** `oi >= 50 AND vol >= 100 AND mid_price >= 1 AND spread_pct <= 0.20` lifts the 1552-trade cohort from −2.15% to **+0.96%, n=114** — breakeven, not profitable. (§Liquidity Findings)
- **Contract picker has a 41.6% NULL rate** on `recommended_strike` in the broader population. Known structural issue.
- **Theta + slippage asymmetry on the option side is brutal.** A +1% underlying move over 2 days routinely produces a −5% to −10% option result.
- **The dataset window (Feb 18 – Apr 6, 2026)** sits inside the Iran shock + record VRP environment. Treat all numeric findings as conditional on that regime.

## What we know does NOT work

- Bracket optimization. 840 variants tested — including no-target, no-stop, and 15-day holds. None are profitable on the full cohort.
- Premium-score filtering as currently implemented (`>= 2 AND is_tradeable`).
- Single-feature filtering. ~800 univariate filters scanned at deciles. None survive bootstrap.
- Two-feature filter combinations. The top combo (`risk_reward_ratio >= 0.42 AND enrichment_quality_score <= 6.8`, +27.86% OOS on n=34) is in the same regime-artifact territory as `filt_rrr`. Do not deploy.
- Premium-score formula tweaks. The components are individually mostly noise; the composite is anti-predictive.
- Morning entries (09:45, 10:00, 10:30, 11:00). Earlier `ROBUSTNESS_SWEEP_REPORT` work showed all morning entries had negative or near-zero EV. (Caveat: that work was on a smaller pre-Iran cohort.)

## Open hypotheses (ranked, with stable IDs)

These are the live experiments. See `STRATEGY_PLAYBOOK.md` for the full mechanics of each.

- **H1 — Underlying-leverage relabel + SPY benchmark.** For every signal, compute the stock return (not option return) from `entry_timestamp` to `exit_timestamp` at 1×/2×/3× leverage, alongside SPY's return over the same window. The right metric is **signal-side avg − SPY avg**. Highest priority. If signal-side > SPY-side, the directional read has relative edge even in this regime — the strongest possible evidence the signal works. Concrete script: `scripts/research/relabel_underlying_v1.py`. ETA 30 min + ~5 min Polygon fetches.
- **H2 — VIX stratification.** Pull historical VIX, join to `signals_labeled_v1` on `entry_day`, bucket into VIX <20, 20-25, 25-30, 30+. If high-VIX buckets dominate the losses and low-VIX buckets are breakeven or positive, the signal is regime-conditional, not broken.
- **H3 — IV–RV spread filter.** Compute 30-day RV per ticker, join with `recommended_iv`, filter to `iv_rv_spread <= 5`. If the low-VRP subcohort is positive while the high-VRP subcohort is negative, we have directly confirmed the variance-risk-premium thesis on our own data.
- **H4 — Regime gating meta-rules.** Compute VIX term structure (VX1/VX2), 14-day SPX ADX, 10-day Efficiency Ratio. Apply each as a filter on the existing cohort and see which (if any) reverses expectancy.
- **H5 — Bull-call-spread alternative.** For each signal, simulate buying the 0.70-delta call and selling the 0.30-delta call (put-side equivalent for bearish), close at same exit time. We have all the bar data needed.
- **H6 — Deep-ITM long options.** Rebuild the contract picker with `delta >= 0.70`, `dte >= 30`, `spread_pct <= 0.10`. Behaves like leveraged stock with a hard floor.
- **H7 — Earlier entry time.** Re-run the V1 sweep with entry times 9:45, 10:00, 10:30, 11:00, 12:00 — Deep Research cites studies that post-gap momentum is captured in the first 30 minutes, and 15:00 means buying after the IV spike has had all day to mean-revert. We can do this immediately on the cached bars. **Note:** this directly contradicts the older `ROBUSTNESS_SWEEP_REPORT` finding; the contradiction itself is interesting and worth resolving.
- **H8 — Pre-Iran historical relabel.** Resolved on 2026-04-08: `overnight_signals_enriched` only goes back to 2026-02-18. Historical backfill from another source would be a separate infrastructure project. Deferred indefinitely in favor of H9 (forward accumulation).
- **H9 — Does the V3.1 gate's three-way-positive survive the war → post-war regime transition? (NEW 2026-04-08, highest priority)** On the 29 pre-war V3.1 trades, option +2.91% / stock +0.36% / alpha vs SPY +0.35%. The war ended 2026-04-08. At the next pickup session (~4-6 weeks), split the ledger by `entry_day < '2026-04-09'` vs `entry_day >= '2026-04-09'`. If the post-war epoch is also three-way-positive, the V3.1 gate is selecting a regime-general positive expectancy subset. If the post-war epoch flips negative on stock or alpha, the pre-war positive was regime-dependent and the gate needs narrowing. This is the only hypothesis permitted to run before N≥100. See `NEXT_SESSION_PROMPT.md` for the full decision tree.

## Hard constraints

- **The Feb–Apr 2026 dataset is regime-confounded.** Do not draw signal-quality conclusions from it alone. Do not deploy any strategy backtested only on this 6-week window.
- **Do not modify `forward-paper-trader/main.py`** until a hypothesis is validated end-to-end with bootstrap CIs and cross-regime evidence.
- **Stop the bleed.** The production trader writes systematically losing rows to `forward_paper_ledger_v3_hold2`. Either pause the trader or remove the `premium_score >= 2 AND is_tradeable` filter without replacement before the next cron run, so the dataset doesn't keep accumulating known-anti-edge ledger rows.
- **Multiple-comparison risk.** Any new filter or feature search MUST end with a bootstrap CI + walk-forward halving check. The `filt_rrr` autopsy in `FINDINGS_LEDGER.md` is the canonical example of why.
- **Label-leakage discipline.** Never include outcome columns as features. Full list in `.claude/agents/gammarips-researcher.md`.
- **Single source of truth.** All new analysis reads from `signals_labeled_v1` (BigQuery) or the cached pickles, never from the live ledger. New reports are deterministic and overwrite cleanly.

## What you'll find in the rest of this directory

- **`FINDINGS_LEDGER.md`** — every numeric finding from the 12 source reports, organized by topic, with the actual tables preserved.
- **`STRATEGY_PLAYBOOK.md`** — strategy menu: each open hypothesis as a one-pager with thesis, mechanics, validation criteria, and prior evidence.
- **`handoffs/`** — deep research prompts and one-off investigation memos.
- **`_archive/research_reports_2026-04/`** — the 12 original per-experiment reports preserved verbatim. Cited by `FINDINGS_LEDGER.md` for full tables and audit trail.
