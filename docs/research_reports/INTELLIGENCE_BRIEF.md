# Intelligence Brief — GammaRips Signal Research

> **Read this first.** Two-page top-of-stack briefing for any session picking up the strategy work cold. Evidence base: `FINDINGS_LEDGER.md`. Strategy menu: `STRATEGY_PLAYBOOK.md`. Live handoff: `../../NEXT_SESSION_PROMPT.md`. Operator cheat: `../../CHEAT-SHEET.md`.

## 2026-05-06 update — Full literature audit of V5.3 stack (12 parameters across 3 services)

Triggered by the meta-principle adopted in this session: **for structural questions (microstructure, IV crush, term structure, vol risk premium, informed-flow horizon), cite literature; reserve our N=1,563 cohort for selection-style questions specific to our scanner's output.** Three parallel literature scans audited every parameter in the V5.3 stack against peer-reviewed and serious-practitioner sources. Verdict per parameter:

| Parameter | Service | Verdict | Strongest citation | Recommended action |
|---|---|---|---|---|
| `overnight_score >= 1` | enrichment-trigger | Partial (composite is overfit-bait, `>=1` is benign) | Novy-Marx 2015 NBER 21329 | Hold at `>=1`. Do NOT raise without per-flag IC analysis on live ledger. |
| `spread <= 10%` | enrichment-trigger | **Likely harming EV — too loose** | Muravyev & Pearson 2020 RFS; Mayhew 2002 JoF | **Tighten to `<= 8%`**. 10% admits exactly the thin / single-MM contracts where Cremers-Weinbaum predicts the options-flow signal flips off. Highest-confidence recalibration. |
| `directional UOA $ > $500K` | enrichment-trigger | Direction supported, threshold arbitrary | Easley/O'Hara/Srinivas 1998 JoF; Pan & Poteshman 2006 RFS | Replace flat $500K with **percentile-of-trailing-30d-call-dollar-volume** (e.g., >95th pct of own history) or market-cap-conditional. Easley-O'Hara framework defines "unusual" relative-to-self, not absolute. |
| `V/OI > 2.0` | signal-notifier | Partial — direction right, threshold heuristic | Pan & Poteshman 2006 RFS; Johnson & So 2012 JFE | Hold at 2.0. Add open-vs-close discrimination if feasible (Pan-Poteshman's signal lives in *opening* trades). Don't tighten without re-cut. |
| `moneyness 5-15% OTM` | signal-notifier | **Likely harming EV — upper bound is deep-OTM territory** | Augustin et al. 2022 J. Fin. Markets; Aretz et al. 2023 RoF | **Tighten upper bound to ~10% OTM** (or delta 0.20–0.40). Aretz et al.: ITM calls +7% / DOTM calls −27% systematic spread. At 9 DTE / 15% OTM, delta is ~0.10–0.15 — pure lottery zone. Highest-confidence recalibration after spread. |
| `VIX <= VIX3M` | signal-notifier | Coin flip (regime intuition sound, long-call P&L evidence mixed) | Cheng 2019 RFS; Johnson 2017 RFS | Keep as-is. Consider buffer (`VIX < 0.95 × VIX3M`) to reduce borderline-day skips. Log skipped-day counterfactual P&L. |
| `LIMIT 1` per day | signal-notifier | Rock-solid for current bankroll | Kelly 1956; Sinclair 2020 *Positional Option Trading* | Keep. Revisit only when bankroll ≥ $10k AND 50+ closed trades verify rank-2..5 EV. |
| **Earnings-overlap exclusion** | signal-notifier | Rock-solid (just adopted) | De Silva/Smith/So 2026 RoF | **Adopted today** (separate brief entry). |
| Entry = 10:00 ET | forward-paper-trader | Partial — defensibly inside post-open window | Heston/Korajczyk/Sadka 2010 JoF; Gao/Han/Li/Zhou 2018 JFE | Hold. 09:45 defensible; 09:30 worse (open-auction option spread spike); past 10:30 starts eating gap-fade window. |
| **Stop = −60% on option premium** | forward-paper-trader | **Unsupported as premium-level rule — likely harming EV** | Kaminski & Lo 2014 JFM; Han/Zhou/Zhu CICF WP | **No peer-reviewed paper supports fixed-% stops on option premium** (because option price is non-linear in underlying). Literature points to **underlying-based stops** (~−2.5–3% adverse on stock for calls, +2.5–3% for puts). Highest-confidence recalibration of the trader. |
| Target = +80% on option premium | forward-paper-trader | Coin flip — direction right, magnitude folk | Han et al.; trend-following York DP 1211 | Asymmetric-target *direction* is right for noisy serial-correlation signals. Magnitude is folk; **sweep target ∈ {+40, +60, +80, +100, +150}** on closed ledger when N>30. |
| Hold = 3 trading days | forward-paper-trader | **Rock-solid** | Pan & Poteshman 2006 RFS; Johnson & So 2012 JFE | Hold at 3. Possibly 2 (alpha peaks day-1/day-2 per Pan-Poteshman); never longer. |
| Exit = 15:50 ET | forward-paper-trader | Supported | Mu et al. 2025 J. Futures Mkts; option L-shape spread literature | Hold. 15:55 fine; 15:30 leaves intraday-momentum on the table (Gao et al.: predictability peaks last half-hour). |

**Headline (priority-ranked recalibrations):**

1. **`spread <= 10%` → `spread <= 8%`** (enrichment-trigger). Cleanest evidence; lowest blast radius; one-line change.
2. **`moneyness <= 0.15` → `moneyness <= 0.10`** (signal-notifier). Aretz et al. 2023 RoF empirically documents the EV cliff in deep-OTM long calls.
3. **`-60% premium stop` → underlying-based stop** (forward-paper-trader). Largest design change — touches the trader, requires `gammarips-review`, conflicts with the "phone-executable" CHEAT-SHEET routine (operator can arm a −60% option-premium GTC stop on Robinhood; an underlying-based stop requires a contingent order which Robinhood doesn't expose). Phase 2 candidate; not a quick win.
4. **`UOA $ > $500K` → trailing-30d percentile** (enrichment-trigger). Theoretically cleaner; requires backfilling per-ticker dollar-volume history. Phase 2.

**What stays unchanged:** hold = 3 days (rock-solid), exit = 15:50 (supported), `VIX ≤ VIX3M` (coin flip but defensible), `V/OI > 2` (heuristic but works), `LIMIT 1` (correct for bankroll), `overnight_score >= 1` (benign).

**Methodological note for these findings:** Same epistemic class as the earnings rule. Recommendations 1 and 2 are *exclusion-style tightenings* (kicking out parameter regions where literature explicitly documents EV decay) and do NOT require labeled_v1 backtesting. Recommendations 3 and 4 are larger redesigns; #3 in particular changes the operator routine, so user UX trumps marginal EV.

**Hypotheses added to backlog:** **H10** (earnings-overlap exclusion) — **adopted + deployed 2026-05-06**; **H11** (spread tightening 10% → 8%) — **adopted + deployed 2026-05-06**; **H12** (moneyness upper-bound 15% → 10%) — **adopted + deployed 2026-05-06**; **H13** (premium-stop → underlying-stop redesign) — Phase 2 (breaks Robinhood phone-executable routine); **H14** (UOA $ → trailing-percentile) — Phase 2.

H11/H12 deploy decision rationale: `docs/DECISIONS/2026-05-06-lit-audit-h11-h12-spread-moneyness.md`. Both are exclusion-style parameter tightenings, no labeled_v1 backtesting required per the methodological note in Hard Constraints below.

Full per-gate detail and citations: `2026-05-06-literature-audit-v5-3-stack.md` (TBD if user requests; not yet written — the table above is the operative reference).

## 2026-05-06 update — Earnings-overlap exclusion adopted as literature-anchored rule (no backtest)

V5.3 picked CDW BULL (260515C00125000, 8.6% OTM, 9 DTE) for 2026-05-06 entry. All gates cleared (V/OI 92.16, VIX 18.29 ≤ VIX3M 21.05, score 8). CDW reported pre-market: revenue beat (+9.2% YoY, +3.8% vs. consensus) but adjusted op income missed by 18.1%; stock gapped −5.5% to $129.27 by the open. Trade was dead on arrival — the V/OI 92x was earnings-event positioning, not informed directional flow.

**Decision: adopt earnings-overlap exclusion at signal-notifier as a hard rule.** Exclude any ticker whose scheduled earnings date falls inside `entry_day → entry_day+3`. This is a theory-driven exclusion filter (same epistemic class as the existing `VIX ≤ VIX3M` backwardation gate), not a selection filter — it does not require labeled_v1 backtesting. The literature has settled this at scale we cannot match on a 1,563-row regime-confounded cohort:

- **De Silva, Smith & So (2026, *Review of Finance*) "Losing is Optional"** — retail-flagged long-options trades through earnings lose **5–9% on average per event, 10–14% on high-vol names**. Sample population maps directly onto our setup (large-cap, OTM, short-dated, held through print).
- **Cao & Han (2013, *JFE*)** — long delta-hedged options on high-idiosyncratic-vol names earn ~−1.4%/month cross-sectionally; earnings concentrate this exposure into a binary event. Already in our evidence base as the volatility-idiosyncratic trap.
- **IV crush magnitude:** 30–60% in front-month on liquid single names (Dubinsky & Johannes 2006). Worse on OTM short-dated strikes — nearly pure vega.
- **No literature subset supports our trade structure through earnings.** Boundary conditions (Gao/Xing/Zhang 2018 small-cap pre-EA straddles) (a) require closing *before* the print, (b) target small-caps with transaction-cost edge, and (c) the post-2011 update (Khan & Khan SSRN 4832160) finds the edge has compressed to negative even there. We sit in the worst quadrant on every axis: liquid, OTM 5–15%, ~9 DTE, held through.

**Methodological note (added to Hard Constraints below):** Two filter classes carry different evidentiary bars. *Selection filters* (rank/pick winners from our cohort) need labeled_v1 screen + bootstrap + walk-forward + forward OOS — high overfitting risk. *Exclusion filters* (kick out known-broken setups, e.g., earnings overlap, VIX backwardation) are theory-driven and literature-anchored — deploy on mechanism, not on our backtest. Do not conflate the two. Do not backtest exclusion filters on labeled_v1 to "validate" them; the literature has better data than we do.

**Implementation status:** Rule adopted; signal-notifier code change applied 2026-05-06 (FMP `/v3/earning_calendar`, top-10 walk, window `[scan_date, entry_day + 2 trading days]`, fail-closed on calendar fetch failure / non-list payload / all-candidates-overlap). `gammarips-review` audit complete (APPROVE WITH CONDITIONS — three remediations landed in same PR: FMP non-list payload guard, window widened to scan_date for AMC-contamination coverage, TRADING-STRATEGY.md ORDER BY drift fixed). See `docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md`.

## 2026-04-17 update — V5.3 Target 80 deployed; V4 retired; cohort scan confirms exit-policy failure

Session produced three outcomes:

1. **Cohort scan on `signals_labeled_v1` (N=1,563 tradable)** found the 40%/−25% bracket has EV **−4.26%** per trade after fees. Zero of ~35 feature cohorts passed the train-bootstrap-positive AND test-positive gate. **The hedge-flag alpha claim (28/30 live-ledger trades) does NOT replicate** — train EV +0.38% crosses zero; test EV −12.00%. Full report: `2026-04-17-cohort-scan-labeled-v1.md`. Memory updated.

2. **Deep Research pass** modeled EV +1.8% to +3.2% per trade after applying: `V/OI > 2` (new positioning, not unwinding), moneyness 5–15% OTM (whale-leverage sweet spot), `VIX <= VIX3M` regime gate (skip day on backwardation), underlying-based stop (deferred to Phase 2 for mobile-executability), asymmetric +80% target (adopted).

3. **V5.3 "Target 80" deployed.** Entry 10:00 ET day-1, −60% option stop, +80% option target, 3-day hold, 15:50 ET day-3 exit; STOP wins on ambiguous bars. All three services redeployed 2026-04-17. Policy rows tagged `V5_3_TARGET_80`; V4 legacy rows preserved. See `docs/DECISIONS/2026-04-17-v5-3-target-80.md` and `CHEAT-SHEET.md`.

Phase 2 backlog: sweep/block classification, aggressor side, GEX, trailing stop. All deferred until V5.3 accumulates 4+ weeks of paper + real P&L evidence.

## 2026-04-16 update — V3 retired, V4 is sole active strategy

V3 was retired on 2026-04-16. V4 ("whale following") is now the only active pipeline. V3 services are paused; V3 data is preserved for historical reference. See `docs/DECISIONS/2026-04-16-v3-doc-archival.md`. All research posture is now oriented around V4 data collection (target N >= 500) and Phase 2 feature importance discovery.

## 2026-04-08 update — instrumentation pivot and the first three-way-positive (historical)

The research posture changed fundamentally on 2026-04-08. A session that started out as "run H1 (underlying relabel) with an SPY benchmark" produced three results that together reframed the entire problem:

1. **H1 was executed.** `scripts/research/relabel_underlying_v1.py` computed stock-side returns at 1×/2×/3×/5× leverage for all 1563 labeled signals plus an SPY benchmark over the same windows. Full report in `UNDERLYING_VS_OPTIONS_V1.md`. The headline finding: option bleed on the labeled cohort was −3.26% while stock 1× bleed was only −0.33% and SPY was −0.21% — **the options instrument alone accounts for ~89% of the bleed (−2.93 pp/trade)**. The volatility-idiosyncratic trap from Cao & Han is confirmed on our own data. But the signal alone has no measurable directional alpha in this single-regime dataset (alpha vs SPY: −0.16%), so a pure pivot to leveraged stock on the unfiltered cohort is not justified either.
2. **The V3.1 gate produces a fundamentally different cohort.** On the 29 real V3.1 trades the trader actually executed between 2026-02-19 and 2026-03-20, the cohort-wide numbers flip sign on every axis: option +2.91%, stock 1× +0.36%, SPY +0.01%, **directional alpha vs SPY +0.35%**. SPY floor is essentially zero, which means unlike the earlier bearish-VIX-20-25 subset from the labeled cohort (which turned out to be pure market beta), the V3.1-gate result is not SPY-drift capture. This is the **first three-way-positive (option, stock, alpha) in the entire research series**. Sample size is 29, CI still includes zero, and this is not validation — it is the first cohort-level result that is not contradictory. Full report: `BENCHMARKING_VALIDATION_V1.md`.
3. **The decision was to stop searching and start instrumenting.** The repeated filter-search → top-1 candidate → OOS collapse loop (most recently `filt_rrr`) is a methodological dead end on a single-regime 31-day dataset. We will not resolve it by ranking more candidates. Instead, `forward_paper_ledger_v3_hold2` was extended with 10 benchmarking columns that write inline on every trade (`underlying_return`, `spy_return_over_window`, `hv_20d_entry`, `VIX_at_entry`, `vix_5d_delta_entry`, `iv_rank_entry`, `iv_percentile_entry`, plus entry/exit prices for both underlying and SPY). The FMP dependency was retired (legacy endpoint deprecation); VIX now comes from FRED, SPY from Polygon. A daily Polygon IVR cache job was deployed (`polygon-iv-cache-daily` Cloud Scheduler → `/cache_iv` endpoint on `forward-paper-trader`, writes to `polygon_iv_history`). The existing 29 ledger rows were backfilled. Full context: `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`.

**Also on 2026-04-08: the war ended.** The Iran-shock ceasefire is a genuine regime boundary. **Note (2026-04-16):** V3 has been retired. V4 is now collecting the post-war data. The V3 pre-committed hypotheses (H9, epoch split) are superseded by V4's broader data collection approach — feature importance will be run on V4 data at N >= 500.

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
- **V4 is the active pipeline.** Do not add execution gates. Premium flags are features, not gates.
- **Do not run ML until N >= 500.** Feature importance on small samples is noise.
- **Multiple-comparison risk.** Any new filter or feature search MUST end with a bootstrap CI + walk-forward halving check. The `filt_rrr` autopsy in `FINDINGS_LEDGER.md` is the canonical example of why.
- **Label-leakage discipline.** Never include outcome columns as features. Full list in `.claude/agents/gammarips-researcher.md`.
- **Single source of truth.** Analysis reads from `forward_paper_ledger` and `overnight_signals_enriched`. Historical research uses `signals_labeled_v1` (frozen).
- **Selection filters vs. exclusion filters carry different evidentiary bars** (codified 2026-05-06).
  - *Selection filters* — rank/pick winners from our cohort (e.g., a new top-of-rank composite, an "earnings-momentum" feature). Need labeled_v1 screen + bootstrap + walk-forward + forward OOS in live ledger. High overfitting risk (Novy-Marx 2015). Default substrate: our cohort, with strict multiple-comparison discipline.
  - *Exclusion filters* — kick out known-broken parameter regions (e.g., earnings overlap, VIX backwardation, deep-OTM moneyness). Theory-driven, literature-anchored. Default substrate: peer-reviewed evidence; deploy on mechanism, not on our backtest. Do NOT backtest exclusion filters on labeled_v1 to "validate" them — the literature has decades and millions of trades; we have 1,563 rows in one regime.
  - Do not conflate the two. The CDW post-mortem and full-stack literature audit (both in 2026-05-06 entries above) are the canonical examples.
- **`signals_labeled_v1` is a screen, not a validator.** Useful for killing bad ideas cheaply (negative-EV on a long-options-graveyard regime ⇒ almost certainly garbage). NOT useful for confirming good ones (regime-confounded; positive-EV could be artifact). The `filt_rrr` autopsy is the canonical example: +8.28% OOS on labeled_v1 → collapse on forward.

## What you'll find in the rest of this directory

- **`FINDINGS_LEDGER.md`** — every numeric finding from the 12 source reports, organized by topic, with the actual tables preserved.
- **`STRATEGY_PLAYBOOK.md`** — strategy menu: each open hypothesis as a one-pager with thesis, mechanics, validation criteria, and prior evidence.
- **`handoffs/`** — deep research prompts and one-off investigation memos.
- **`_archive/research_reports_2026-04/`** — the 12 original per-experiment reports preserved verbatim. Cited by `FINDINGS_LEDGER.md` for full tables and audit trail.
