# Benchmarking Validation V1 — the first three-way-positive

**Date:** 2026-04-08
**Cohort:** 29 executed trades in `forward_paper_ledger_v3_hold2`, policy version `V3_1_LIQUIDITY_QUALITY`, scan dates 2026-02-19 through 2026-03-20. 22 unique tickers. **This cohort is entirely pre-war (Iran ceasefire: 2026-04-08).**
**Methodology:** self-benchmarked ledger as of Cloud Run revision `forward-paper-trader-00025-kvs`. Every row has `realized_return_pct` (the option bracket outcome), `underlying_return` (the signed stock return over the exact same entry → exit window, computed from Polygon minute bars), `spy_return_over_window` (SPY return over the same window, unsigned), and regime context (`VIX_at_entry`, `SPY_trend_state`, `vix_5d_delta_entry`, `hv_20d_entry`).

> **This report is not a deployment recommendation and is not an edge validation.** N = 29. Every one of these numbers has a 95% CI wide enough to include zero. The purpose of this report is to document that the V3.1-gate real-trade cohort is the **first** cohort-level result in the entire research series where option, stock, and SPY-relative alpha all move positive simultaneously — a pattern that is harder to fake on a 29-row sample than any single metric alone. The decision-grade validation of this finding depends on the post-war accumulation period. See `NEXT_SESSION_PROMPT.md`.

## Headline numbers

```
Instrument                          N      mean    median    win%
Option return (bracketed)          29   +2.91%  -10.11%   48.3%
Underlying return 1x (signed)      29   +0.36%   -0.14%   44.8%
SPY return over window             29   +0.01%   +0.22%   55.2%
Alpha: underlying - SPY            29   +0.35%   +0.12%   51.7%
```

- **Option return +2.91% mean, 48.3% win rate.** Matches the independently-computed `calc_metrics.py` result from the user's own session ($844.68 on $1000/trade over 29 trades = +2.91%). These are not new numbers — the new part is the three columns below them.
- **Underlying return 1× (signed) +0.36% mean, 44.8% win rate.** This is the signed stock return over the exact same entry → exit window. Signed means: a bullish signal is long the stock, a bearish signal is short the stock. +0.36% is the P&L the same trades would have produced on the underlying instrument.
- **SPY return over the same windows +0.01% mean.** The noise floor is essentially zero. SPY's cumulative return over these 29 windows is flat.
- **Directional alpha vs SPY +0.35%.** `underlying_return − spy_return_over_window`. The signal-attributable P&L after subtracting pure market-beta exposure. Positive.

## Contrast vs the unfiltered labeled cohort

The same analysis on the full 1563-row `signals_labeled_v1` cohort (every V3-mechanics signal in the Feb 18 – Apr 6 window, *not* V3.1-gated):

| Cohort | N | Option mean | Stock 1× mean | SPY mean | Directional alpha |
|---|---:|---:|---:|---:|---:|
| Full labeled (unfiltered) | 1563 | −3.26% | −0.33% | −0.21% | −0.16% |
| **V3.1 gate (real trades)** | **29** | **+2.91%** | **+0.36%** | **+0.01%** | **+0.35%** |

**Every metric flips sign** when you restrict to what the V3.1 gate actually takes. The signals the gate rejects are responsible for the entire negative cohort-level result on the unfiltered labeled set. The 89% of bleed that the labeled analysis attributed to the options instrument (−2.93 pp/trade = option −3.26% minus stock −0.33%) is concentrated in the rejected-by-V3.1 population. The gate-passing trades look different.

This is not a filter-discovery result. The V3.1 gate was decided on 2026-04-07 on entirely different grounds (liquidity quality + an audit of asymmetric OI failures). It was not tuned to produce this outcome. The self-benchmarking layer that makes this comparison possible was built on 2026-04-08.

## Why SPY floor at zero matters

An earlier research cut on the labeled cohort (`UNDERLYING_VS_OPTIONS_V1.md`) found a subset — bearish signals × VIX 20-25 — that looked positive on the option side (+4.48%, win 46%, bootstrap CI excludes zero) and positive on the stock side (+0.78%, CI excludes zero). But the directional alpha CI for that subset included zero (−0.31%, +0.58%, P(>0) = 72%), and SPY in the same VIX 20-25 windows was −0.65%. Interpretation: the bearish-VIX-20-25 P&L was dominated by SPY drift capture — you could have made the same money by shorting SPY in those windows, and the signal contributed essentially zero edge.

The V3.1 real-trade cohort is **structurally different** on exactly this axis. SPY over the 29 windows is +0.01% — not −0.65%. There is no drift for the signal to piggyback on. The +0.36% underlying return and the +0.35% directional alpha are therefore not beta capture. They are attributable to the signal selecting the right direction on the right names at the right time, not to holding any particular side of the market. That is a much harder pattern to fake with N=29 than any single column being positive.

## By direction

| Direction | N | Option mean | Stock 1× mean | Opt win% | Stock win% |
|---|---:|---:|---:|---:|---:|
| BULLISH | 3 | +7.98% | +1.46% | 66.7% | 66.7% |
| BEARISH | 26 | +2.33% | +0.24% | 46.2% | 42.3% |

Both directions are positive on both instruments. The cohort is overwhelmingly bearish (26 of 29 = 90%), which reflects the war-regime market more than any gate property — bearish flow was the dominant institutional setup during the Feb-Mar shock window. Whether the gate continues to produce mostly-bearish signals post-ceasefire is itself an open question for the pickup session.

**Do not interpret the bullish N=3 result as meaningful.** Three trades is three trades.

## By VIX bucket

| VIX bucket | N | Opt mean | Stock mean | SPY mean |
|---|---:|---:|---:|---:|
| <20 | 2 | +40.00% | +2.87% | −0.30% |
| 20−25 | 13 | +6.13% | +1.50% | −0.46% |
| 25−30 | 14 | −5.38% | −1.05% | +0.49% |
| 30+ | 0 | — | — | — |

Same VIX-25 breakpoint pattern that the earlier labeled-cohort analysis flagged, now visible on the real-trade cohort. VIX < 25 is strongly positive (N=15, option mean ≈ +11%, weighted). VIX ≥ 25 is strongly negative (N=14, option mean −5.38%). No trades fell in the panic ≥30 bucket.

**Do not act on this.** 15 trades in a bucket is still 15 trades. The VIX-25 hypothesis is one of the four pre-committed tests for the N ≥ 100 revisit, not a deploy-now rule. But it is the second independent cohort in which the VIX-25 breakpoint has appeared, which is worth noting.

## By HV_20d bucket (underlying volatility)

| HV bucket | N | Opt mean | Stock mean |
|---|---:|---:|---:|
| <30% | 3 | +18.33% | +2.01% |
| 30−50% | 8 | −1.64% | −0.49% |
| 50−80% | 6 | +9.54% | +1.20% |
| 80%+ | 12 | −1.23% | +0.10% |

Non-monotonic. Tiny N per bucket. **Do not interpret.** Displayed for completeness and as a reminder that with 29 trades and 4 buckets, you will always find a narrative — the right response is to not go looking for one.

## Statistical caveats (read these)

1. **N = 29.** 95% CI on the option return is roughly [−8%, +14%] given per-trade variance. 95% CI on the stock return is roughly [−1.6%, +2.3%]. Both include zero. The stock CI excluding zero on this sample would require mean +0.8% or better, not +0.36%.
2. **Single regime.** Every trade is inside the Iran shock / high VRP window (Feb 19 – Mar 20). The ceasefire was 2026-04-08. The pre-war cohort is structurally incomparable to any normal-regime cohort.
3. **Selection is not causation.** The V3.1 gate selects a subset with observably-positive expectancy on this cohort. That is consistent with several causal stories, only one of which is "the gate is selecting real-alpha signals." Other possibilities: the gate accidentally selects for names that happened to mean-revert favorably in this specific regime; the liquidity filter happens to correlate with some unobserved regime-specific variable; the OI floor biases toward large-cap HEDGING flow which benefited from the specific war-fear positioning that was rolling off through March. The only way to distinguish is out-of-sample in a different regime, which is exactly what the next 4-6 weeks of post-war data provides.
4. **Direction imbalance.** 26 bearish vs 3 bullish. The bearish-heavy skew may not persist into the post-war regime. If the post-war cohort is more balanced, cohort-level means will move for that reason alone.

## Explicit non-conclusions

This report is **not** evidence that:

- The V3.1 gate has a real positive edge. The N is too small and the single-regime confound is too large to claim that.
- The signal generator works in normal regimes. We have zero data from a normal regime.
- The pivot to leveraged stock is justified. The +0.36% stock-side mean is within CI of zero; leveraging a near-zero bleed to 2×/3×/5× multiplies the downside as fast as the upside.
- IVR / IV-HV spread matters. We have zero data on that — the IVR cache has only 1 day of history as of this report.
- Any specific signal feature (premium_score, direction, HV bucket, etc.) predicts profitability. None of the subgroups above can be acted on.

## What this report IS evidence of

- The V3.1 gate is **not** trivially broken — its cohort-level expectancy on the pre-war window is not uniformly negative like the full unfiltered population's is.
- The instrumentation works. Every benchmarking column populated on every executed row. The self-benchmarking architecture is ready to accept post-war data and produce a clean two-regime comparison at the revisit point.
- The "instrument bleed is the dominant problem" thesis from the Deep Research brief is visible in the data: option return − stock return for the V3.1 cohort is +2.91% − 0.36% = +2.55 pp. The options instrument is **helping** (not hurting) on this cohort, which is the opposite of the labeled-cohort finding (−2.93 pp instrument drag). That flip is either a gate effect (the liquidity floor is selecting names where options track underlying well) or a regime artifact (the 2-day +40%/−25% bracket happened to catch the post-Iran-shock bounce-back moves on both sides). Either way, it is another fact that becomes testable only on post-war data.

## Decision posture

- **V3.1 gate is frozen** through the accumulation period (2026-04-08 → pickup session ~4-6 weeks later). No tuning, no filter additions, no bracket changes.
- **The `current_ledger_stats.py` script is the weekly monitor.** It prints these numbers (and the VIX/HV stratifications) in the same shape every run. Run it weekly. Do not act on its output.
- **The pre-committed hypotheses for the revisit session** are documented in `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md` and `NEXT_SESSION_PROMPT.md`:
  1. Pre-war vs post-war epoch split
  2. VIX < 25 vs ≥ 25 in the post-war epoch (only if post-war N ≥ 30)
  3. Underlying-vs-option return gap (is the instrument bleed back?)
  4. IVR is DEFERRED to the 12-month mark

## Reproduce

```bash
python scripts/ledger_and_tracking/current_ledger_stats.py
```

Or raw SQL:

```sql
SELECT
  COUNT(*) AS n,
  AVG(realized_return_pct) AS option_mean,
  AVG(underlying_return) AS stock_mean,
  AVG(spy_return_over_window) AS spy_mean,
  AVG(underlying_return - spy_return_over_window) AS alpha_unsigned
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
```

Expected on 2026-04-08: N=29 (plus any re-runs of 2026-02-19 during smoke testing). Post-pickup: N ≫ 29 with a clean epoch boundary at `entry_day = 2026-04-09`.
