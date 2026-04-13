# Strategy Playbook — GammaRips

> Forward-looking design space. Each section is a strategy candidate with thesis, mechanics, validation criteria, and the prior evidence that supports or refutes it. Read alongside `INTELLIGENCE_BRIEF.md` (top-of-stack) and `FINDINGS_LEDGER.md` (evidence base).

The strategy hypotheses are stable-IDed (H1, H2, …) so future sessions can reference them by ID. Order is the recommended experiment sequence.

---

## H1 — Underlying-leverage relabel + SPY benchmark

**Status:** highest priority. Not yet run.

**Thesis.** The directional read on the underlying is real (~74% accuracy). The losses come from the option wrapper (theta + slippage + variance risk premium). If we strip the wrapper and trade the stock directly with leverage, the directional edge should translate ~1:1 into P&L.

**Mechanics.**
- For every signal in `signals_labeled_v1`, fetch Polygon stock minute bars (not options bars) and compute the underlying return from `entry_timestamp` to `exit_timestamp` at 1×/2×/3×/5× leverage.
- For the same windows, compute SPY's return as a regime benchmark.
- Report side-by-side: `option_return`, `stock_return_1x`, `stock_return_3x`, `spy_return`, `signal_alpha = stock_return_1x − spy_return`.

**Validation criteria.**
- **Confirms H1:** signal-side stock alpha vs SPY > 0 over the cohort. The directional read has *relative* edge even in the Iran regime — strongest possible evidence the signal works.
- **Refutes H1:** signal-side stock returns are no better than SPY (or worse) over the cohort. Either the signal has no real edge, or the regime ate it indiscriminately.
- Bootstrap CIs on the alpha. Walk-forward halving (the Mar 26–Apr 6 V-bottom window will dominate any naive average).

**Prior evidence.**
- Underlying directional accuracy ≈ 74% (`FINDINGS_LEDGER.md` §Cohort).
- Option-side P&L: −1.99% OOS on the least-bad bracket, 0/840 profitable. Asymmetry is on the wrapper, not the direction.
- Volatility-idiosyncratic trap (Cao & Han 2013) predicts exactly this gap: directional read intact, option wrapper systematically overpriced.

**Concrete next action.** Write `scripts/research/relabel_underlying_v1.py`. Reuse `fetch_minute_bars` from `forward-paper-trader/main.py`. Output `docs/research_reports/UNDERLYING_VS_OPTIONS_V1.md`. ETA: 30 min code + ~5 min Polygon fetches.

---

## H2 — VIX stratification

**Status:** not yet run.

**Thesis.** The Iran-window dataset is a single regime sample. If we slice it by VIX level on entry day, we can ask whether the signal works in calm vs panic conditions. If high-VIX losses dominate while low-VIX subcohorts are breakeven or positive, the signal is regime-conditional, not broken.

**Mechanics.**
- Pull historical VIX (FRED or yfinance). Join to `signals_labeled_v1` on `entry_day`.
- Bucket: VIX < 20, 20-25, 25-30, 30+.
- Report n / win rate / avg return / OOS avg per bucket.

**Validation criteria.**
- **Supports regime-conditionality:** clean monotonic degradation as VIX climbs, with the lowest bucket near or above breakeven.
- **Refutes:** all VIX buckets negative — signal has structural problems independent of regime.

**Prior evidence.**
- Cohort window had VIX peak 35.3, average 25.4 (`FINDINGS_LEDGER.md` §Regime Context).
- The earlier `SPEC-SCORING-V2` design proposed VIX>25 as a hard skip rule. We never validated that threshold on the post-Iran data.

**Concrete next action.** `scripts/research/stratify_by_vix_v1.py`. Reads `signals_labeled_v1`, joins VIX, writes a VIX-bucket EDA report.

---

## H3 — IV–RV spread filter

**Status:** not yet run. **Most direct test of the variance-risk-premium thesis.**

**Thesis.** The volatility-idiosyncratic trap says we lose because we buy options when implied vol is far above subsequent realized vol. If we filter to signals where `recommended_iv − rv_30d <= 5pts`, the surviving cohort should have material upside on the option side.

**Mechanics.**
- Compute 30-day historical realized volatility per ticker (from Polygon daily bars or yfinance).
- Use `recommended_iv` already in `signals_labeled_v1`.
- Define `iv_rv_spread = recommended_iv − rv_30d`.
- Stratify cohort by spread: ≤0, 0-3, 3-5, 5-8, 8+.

**Validation criteria.**
- **Confirms thesis:** low-VRP buckets are positive, high-VRP buckets are catastrophically negative.
- **Refutes:** no relationship between VRP and option return. Either the regime swamped the relationship, or theta/picker are doing the damage instead.

**Prior evidence.**
- Cohort sat in 9pt market-wide IV-RV spread (3× normal) — `FINDINGS_LEDGER.md` §Regime Context.
- `recommended_iv >= 0.998` (q90) is in the bottom-10 anti-edge filters at **−13.90% OOS** — direct evidence that the highest-IV signals are the worst trades.

**Concrete next action.** `scripts/research/iv_rv_filter_v1.py`. Compute RV from Polygon daily aggs, add as a feature column, repeat the cohort EDA from `analyze_signals_labeled_v1.py` stratified by the new feature.

---

## H4 — Regime gating meta-rules

**Status:** not yet run. Multiple sub-hypotheses.

**Thesis.** Even if the signal generator works in normal regimes, we need a meta-rule that pauses the strategy during toxic windows. Three candidate gates:
- **VIX term structure (VX1/VX2 ratio):** ratio < 1.0 = backwardation = panic. Don't trade when backwardated.
- **14-day ADX on SPX:** ADX < 15 = no trend = chop. Don't trade in chop.
- **10-day Efficiency Ratio:** low ER = whipsaw. Don't trade.

**Mechanics.**
- Compute each indicator on SPX daily bars.
- Apply each as a binary skip filter on `signals_labeled_v1`.
- Report what fraction of trades each filter skips and what the surviving cohort's avg return is.

**Validation criteria.**
- **Successful gate:** removes ≥30% of trades AND lifts the surviving cohort's avg return materially (towards or above breakeven).
- **Failed gate:** removes trades but cohort avg doesn't improve, or improves only because of a tiny n.
- All candidates must pass bootstrap CI + walk-forward halving — these are very easy to overfit.

**Prior evidence.**
- VIX term structure went into backwardation in March 2026 — exactly the toxic window. Coincides with the worst part of the cohort.
- The 6-session chop window Mar 18-25 mauled most variants in the bracket sweep.

**Concrete next action.** `scripts/research/regime_gates_v1.py`. Compute three indicators, run as filters, report.

---

## H5 — Bull-call-spread alternative

**Status:** not yet run. **Highest-leverage architectural alternative if H1 fails.**

**Thesis.** A debit vertical spread (long lower-strike + short higher-strike) is theta-neutral, vega-neutral, and capped on both ends. It substitutes capped upside for the elimination of the variance-risk-premium tax. If naked options lose money on the cohort and verticals are positive on the same cohort, the wrapper choice is the entire problem.

**Mechanics.**
- For each bullish signal: simulate buying the 0.70-delta call and selling the 0.30-delta call on the same expiration.
- For each bearish signal: same with puts.
- Use the same entry/exit timestamps as the existing labels. Compute spread P&L using mid-prices from Polygon options chains at entry and exit times.
- Compare side-by-side with the existing `realized_return_pct`.

**Validation criteria.**
- **Confirms:** spreads positive on the same cohort where naked options are negative. Deployment-ready architectural fix.
- **Refutes:** spreads also negative. Then the problem is something else (signal direction or timing).

**Prior evidence.**
- Theta + slippage asymmetry on naked options is brutal even when the underlying moves in the right direction (`FINDINGS_LEDGER.md`).
- Spread structures are the literature's standard answer to "high IV environment + directional signal" (Sinclair 2020).

**Concrete next action.** `scripts/research/spread_relabel_v1.py`. Requires fetching adjacent-strike option chains for each signal — more Polygon work than H1, but still tractable.

---

## H6 — Deep-ITM long options

**Status:** not yet run. Architectural alternative #2.

**Thesis.** Deep-ITM long options (delta ≥ 0.70, DTE ≥ 30) behave like leveraged stock with a hard floor. Minimal theta, minimal vega, near-1.0 directional exposure. Captures the underlying read without paying the IV tax.

**Mechanics.**
- For each signal, find the contract on the recommended expiration with delta closest to 0.85 (instead of the picker's existing logic).
- Re-run V3 mechanics on these contracts.
- Compare avg return and win rate to the existing cohort.

**Validation criteria.**
- **Confirms:** deep-ITM cohort positive (or at least materially less negative) on the same windows.
- **Refutes:** still negative. Then the wrapper isn't the issue at all — the direction is.

**Prior evidence.**
- The current picker has a 41.6% NULL rate and selects OTM short-dated contracts — the worst possible choice per the literature.
- `recommended_delta` >= 0.4984 (q90) was a top-5 univariate filter at **+9.74% OOS** (regime-suspect, but suggestive).
- Bottom-10 filter list: `recommended_delta <= -0.469` is at **−13.92% OOS** — high-magnitude delta in either direction is worse than low-magnitude. Inconsistent with H6 prior. Investigate carefully.

**Concrete next action.** Likely depends on having a richer Polygon options-chain pull than the current picker uses. May require rebuilding the contract picker before this can be backtested.

---

## H7 — Earlier entry time (re-test 9:45–11:00)

**Status:** not yet run. **Cheap to test on existing cached bars.**

**Thesis.** Deep Research #1 cites studies showing post-gap momentum is captured in the first 30 minutes. The current 15:00 entry means buying after the IV spike has had all day to mean-revert. Earlier entries may catch the move before the option premium fades.

**Mechanics.**
- The cached bar window (`/tmp/signal_bars_v1.pkl`) covers full trading days.
- Re-run the V1 sweep with entry times 9:45, 10:00, 10:30, 11:00, 12:00 in addition to the existing 15:00, 15:30, 15:45, 15:55.
- Report best variant per entry time.

**Validation criteria.**
- **Supports H7:** clear monotonic improvement at earlier entry times, with the best earlier-entry variant materially above the −1.99% baseline.
- **Refutes H7:** earlier entries are worse (this is what the older `ROBUSTNESS_SWEEP_REPORT` found pre-Iran).

**Prior evidence.**
- `ROBUSTNESS_SWEEP_REPORT` (pre-Iran small cohort): morning entries had EV between −8.5% and +1.5%, 09:45 stop-out rate over 50%. Catastrophic.
- Deep Research #1 (post-Iran literature review): the opposite — early entries should outperform.
- These two contradict each other directly. Resolving the contradiction is the value of running the experiment.

**Concrete next action.** Edit `scripts/research/sweep_brackets_v1.py` to include earlier entry times in the variant grid. Re-run. Cheap.

---

## H8 — Pre-Iran historical relabel

**Status:** not yet run. Most ambitious. Highest payoff.

**Thesis.** If `overnight_signals_enriched` extends earlier than 2026-02-18, we can label that earlier window under the same V3 mechanics and ask: did the strategy work in the calmer regime? Pre-Iran positive + post-Iran negative is the cleanest possible proof that the regime is the entire problem.

**Mechanics.**
- Check the date range of `overnight_signals_enriched` and `overnight_signals` (raw scanner).
- If pre-Feb-2026 data exists, build a parallel `signals_labeled_v1_historical` cohort with the same simulator.
- Compare cohort-level P&L pre vs post Iran.

**Validation criteria.**
- **Confirms regime hypothesis:** pre-Iran cohort breakeven or positive on the V1-best bracket.
- **Refutes:** pre-Iran also negative. Then the signal generator has structural issues independent of regime.

**Prior evidence.**
- The earlier small-n studies (`UPSTREAM_LIQUIDITY_REPORT`, `ROBUSTNESS_SWEEP_REPORT`) reported +9% to +12% EV on pre-Iran cohorts. Those were small n and may not survive a clean re-label, but they're a positive signal that the pre-Iran behavior is meaningfully different.

**Concrete next action.** Query `overnight_signals_enriched` for distinct scan_date histogram. If meaningful pre-Feb-2026 rows exist, write `scripts/research/relabel_historical_v1.py` (port of `build_labeled_signals_v1.py` against the earlier window).

---

## Instrument-selection decision tree

Based on the volatility-idiosyncratic trap (Cao & Han 2013) and the Deep Research #1 findings, the literature's three "right answers" for a directional signal with ~74% accuracy on the underlying are, in priority:

```
Is the directional signal real on the underlying?
├── No  → skip the trade
└── Yes → Is implied vol much higher than realized vol?
         ├── No (IV ≈ RV)        → naked long options OK (deep ITM, ≥30 DTE)
         └── Yes (IV >> RV)      → Is the signal high-conviction?
                                  ├── Yes → trade the underlying with leverage
                                  └── No  → sell credit spreads (harvest the IV)
```

This is the framework that should drive the instrument choice for any deployed strategy. The current pipeline does the worst possible thing on every branch: buys naked OTM short-dated options when IV is at maximum spread vs RV.

---

## Regime gating rules (draft, to be tested in H4)

These are the meta-rules from Deep Research #2 that should be tested as filters and, if any pass validation, used as production skip conditions.

| Indicator | Threshold | Action |
|---|---|---|
| VIX term structure (VX1/VX2) | < 1.0 (backwardation) | SKIP all trades |
| 14-day SPX ADX | < 15 (no trend) | SKIP all trades |
| 10-day Efficiency Ratio | < 0.30 (chop) | SKIP all trades |
| IV–RV spread (per signal) | > 5 points | SKIP that signal |
| Single-day SPX move | \|move\| > 2% in last 3 days | Wait 1 day before any new entry |

None of these are validated yet. They are the experimental design space, not production rules.

---

## Reading list

- **Cao & Han (2013), JFE** — "Cross-section of option returns and idiosyncratic stock volatility" — the volatility-idiosyncratic trap; core diagnosis
- **Goyal & Saretto (2009)** — option return predictability via IV-RV spread; basis for H3
- **Sinclair (2020), "Positional Option Trading"** — practitioner reference for instrument choice on directional reads
- **Bailey & López de Prado (2014)** — Deflated Sharpe Ratio; addresses the 840-variant overfitting concern; should be used to size confidence in any future filter discovery
- **Squeezemetrics / GEX literature** — dealer gamma exposure as a regime classifier; possible H4 extension

The full Deep Research outputs that surfaced these references should be saved alongside the prompts in `handoffs/`.
