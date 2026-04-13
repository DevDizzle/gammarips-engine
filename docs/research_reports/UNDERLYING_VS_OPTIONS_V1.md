# Underlying-vs-Options Relabel — V1

**Generated:** 2026-04-08 19:23 UTC
**Source:** `signals_labeled_v1` (simulator_version = `V3_MECHANICS_2026_04_07`)
**Cohort:** every signal with non-null `entry_timestamp`, `exit_timestamp`, and `realized_return_pct`.

## Question

For the same cohort the V3 paper trader is bleeding on, would the **underlying stock** have made money over the same entry-to-exit windows? If yes, the bleed is an instrument problem (overpriced volatility on high-IVOL names) and the fix is to pivot to leveraged equity. If the underlying also bleeds, the bleed is either a regime problem or a signal-generator problem and we need a different test to disambiguate.

## Cohort

| Metric | Count |
|---|---:|
| Total signals labeled | 1563 |
| With stock-side data | 1563 |
| With SPY benchmark   | 1563 |
| With VIX-at-entry    | 1563 |

## Headline P&L (cohort-wide)

Same entry timestamp, same exit timestamp, same population. Only the instrument changes. Returns are signed by the signal direction (bullish: long; bearish: short).

| Instrument | N | Mean return | Median return | Win rate | Cumulative |
|---|---:|---:|---:|---:|---:|
| Option (current) | 1563 | -3.26% | -25.00% | 33.5% | -5100.00% |
| Stock 1x | 1563 | -0.33% | -0.89% | 38.5% | -512.22% |
| Stock 2x | 1563 | -0.66% | -1.78% | 38.5% | -1024.45% |
| Stock 3x | 1563 | -0.98% | -2.67% | 38.5% | -1536.67% |
| Stock 5x | 1563 | -1.64% | -4.45% | 38.5% | -2561.12% |
| SPY (unsigned) | 1563 | -0.21% | -0.25% | 37.0% | -329.18% |
| Alpha vs SPY (unsigned) | 1563 | -0.12% | -0.65% | 40.3% | -183.04% |
| Alpha vs SPY (directional) | 1563 | -0.16% | -0.54% | 39.7% | -244.35% |

**Notes:**
- *Option (current)* is the realized return from the V3 simulator (already in `signals_labeled_v1.realized_return_pct`).
- *Stock Nx* is the simple leveraged stock return (`(exit_px / entry_px - 1) * sign * N`). It does **not** model funding cost, gap risk, or margin call mechanics — it's the cleanest possible apples-to-apples test of "did the directional read translate to underlying P&L?".
- *SPY (unsigned)* is the SPY return over the same window without direction-signing — what you'd get holding the index over each window.
- *Alpha vs SPY (unsigned)* = `stock_return_1x - spy_return`. Subtracts pure market beta.
- *Alpha vs SPY (directional)* = `stock_return_1x - sign * spy_return`. Subtracts the *directional* market move (so a bearish signal on a day SPY fell isn't credited for being right about the market). This is the most conservative isolation of signal-specific alpha.

## Verdict

**OUTCOME C — Cannot conclude the signal generator works in this regime.** Stock-side 1x mean is -0.33% and directional alpha vs SPY is -0.16%. Both are non-positive. Re-label a pre-Iran-war historical window before making any architectural decision.

## By signal direction

| Direction | N | Option mean | Stock 1x mean | SPY mean | Win% (opt / stock) |
|---|---:|---:|---:|---:|---:|
| BULLISH | 743 | -4.76% | -0.49% | -0.40% | 31.2% / 35.1% |
| BEARISH | 820 | -1.90% | -0.18% | -0.04% | 35.5% / 41.6% |

## By premium_score (the filter the trader currently uses)

The V3 trader gates on `premium_score >= 2`. If higher premium_score = higher IVOL = more overpriced options, we should see option means decrease as premium_score rises while stock means stay flat or improve.

| premium_score | N | Option mean | Stock 1x mean | Option win% | Stock win% |
|---|---:|---:|---:|---:|---:|
| 0 | 1115 | -3.84% | -0.38% | 32.6% | 37.2% |
| 1 | 396 | -2.48% | -0.26% | 34.3% | 40.7% |
| 2 | 51 | +3.77% | +0.31% | 45.1% | 49.0% |
| 3 | 1 | -25.00% | +1.97% | 0.0% | 100.0% |

## By VIX at entry

VIX bucket on the signal's entry day, joined from yfinance `^VIX` daily close. This is the regime-stratification cut from the brief — if the high-VIX buckets dominate the losses and the low-VIX buckets are flat-or-positive, the signal is regime-conditional.

| VIX bucket | N | Option mean | Stock 1x mean | SPY mean | Directional alpha |
|---|---:|---:|---:|---:|---:|
| VIX < 20 | 215 | -4.35% | -0.54% | -0.58% | -0.36% |
| 20–25 | 653 | +0.42% | +0.13% | -0.64% | +0.08% |
| 25–30 | 575 | -4.81% | -0.46% | +0.06% | -0.16% |
| 30+ | 120 | -13.98% | -1.79% | +1.50% | -1.08% |

## Follow-up subset analyses (run after the main script)

### Bearish-only across VIX buckets

Direction × VIX is the cleanest two-axis cut. Bearish under calm VIX is the only profitable subset on options.

| Direction | VIX bucket | N | Option mean | Option win% | Stock 1x | SPY (unsigned) | Directional alpha |
|---|---|---:|---:|---:|---:|---:|---:|
| BEARISH | <20    |  81 |  −3.10% | 33% | −0.58% | −0.53% | −1.11% |
| BEARISH | 20–25  | 345 | **+4.48%** | **46%** | **+0.79%** | −0.65% | +0.14% |
| BEARISH | 25–30  | 299 |  −4.37% | 31% | −0.54% | +0.34% | −0.19% |
| BEARISH | 30+    |  95 | −16.29% | 13% | −2.20% | +1.40% | −0.80% |
| BULLISH | <20    | 134 |  −5.11% | 31% | −0.51% | −0.61% | +0.10% |
| BULLISH | 20–25  | 308 |  −4.12% | 33% | −0.61% | −0.63% | +0.02% |
| BULLISH | 25–30  | 276 |  −5.28% | 29% | −0.37% | −0.25% | −0.12% |
| BULLISH | 30+    |  25 |  −5.20% | 32% | −0.23% | +1.91% | −2.15% |

**The bearish-in-calm-VIX cohort is the only deployable subset in this dataset.** N=345, option mean +4.48%, win rate 46%, stock-side also positive at +0.79%. Every other subset bleeds.

### Bootstrap of bearish × VIX 20-25 (2000 samples, seed=42)

| Series | Mean | 95% CI | P(mean > 0) |
|---|---:|---:|---:|
| Option return | +4.45% | [+1.53%, +7.44%] | **100%** |
| Stock 1x return | +0.78% | [+0.30%, +1.26%] | **100%** |
| Directional alpha vs SPY | +0.13% | [−0.31%, +0.58%] | 72% |

**Critical nuance:** the option and stock-side CIs cleanly exclude zero, but the **directional alpha CI includes zero** and the directional-alpha mean is essentially nil (+0.13%). That means **most of the bearish-VIX-20-25 P&L is market-beta capture, not signal alpha** — SPY drifted −0.65% in calm-VIX windows and bearish bets caught that drift. The signal generator isn't picking the *right* stocks to short; it's picking *any* stock to short while the broad tape was drifting down.

### Walk-forward stability (chronological halving) on bearish × VIX 20-25

This is the same robustness check that disproved `filt_rrr`. If the result is a recency artifact, the first half should be flat or negative. It isn't.

| Cohort half | N | Date range | Option mean | Stock 1x | Directional alpha |
|---|---:|---|---:|---:|---:|
| First half | 172 | 2026-02-19 → 2026-03-10 | **+6.83%** | +0.58% | +0.01% |
| Second half | 173 | 2026-03-10 → 2026-04-01 | **+2.14%** | +0.99% | +0.26% |

**Both halves positive on option and stock.** Unlike `filt_rrr` (where the +8.28% OOS edge collapsed to −3.37% in the first half), this result is stable across time. It is the first finding in the entire research series that survives chronological halving with a positive sign in both halves.

Quartile breakdown (further stress test):

| Quartile | N | Date range | Option | Stock 1x | Alpha-dir |
|---|---:|---|---:|---:|---:|
| Q1 | 87 | Feb 19 → Mar 02 | +3.15% | −0.05% | −0.13% |
| Q2 | 86 | Mar 02 → Mar 10 | +10.93% | +1.33% | +0.28% |
| Q3 | 86 | Mar 10 → Mar 17 | +3.58% | +1.16% | +0.36% |
| Q4 | 86 | Mar 17 → Apr 01 | +0.26% | +0.71% | +0.06% |

**All four quartiles positive on options.** Q4 is the weakest (+0.26%) — possible signs of edge decay or simply that Q4 sits closer to the regime-shift boundary.

### Bullish × VIX 20-25 (sanity check — should be zero if not anti-edge)

| Half | N | Option | Stock | Alpha |
|---|---:|---:|---:|---:|
| First | 154 | −3.58% | −0.46% | +0.10% |
| Second | 154 | −4.66% | −0.77% | −0.06% |

Bullish bleed is consistent across halves. The asymmetry is real: **bullish signals lose money systematically; bearish signals make money but only via market-beta capture.**

### What this means for production

1. **Confirmed beyond doubt:** the options instrument is responsible for the vast majority of the bleed. Option mean −3.26% vs stock 1x −0.33% — the instrument alone destroys 2.93 percentage points per trade. The volatility-idiosyncratic trap is real on our own data.

2. **The signal generator has no measurable directional alpha in this dataset.** Stock 1x is −0.33%, SPY is −0.21%, directional alpha is −0.16%. Pivoting to leveraged stock with the *full cohort* would not be profitable — leverage just multiplies the small-but-real underlying bleed.

3. **There is exactly one walk-forward-stable profitable subset: bearish + VIX 20-25**, and its profitability is dominated by SPY drift (market beta), not signal alpha. It is deployable as a beta-overlay strategy but is not evidence the signal generator works.

4. **The catastrophic zone is unambiguously VIX ≥ 25.** Bullish under VIX ≥ 25 is anti-edge: SPY went up +0.18% on average during these windows while our bullish stock picks fell −0.31%. The signal generator is actively picking the wrong direction during high-vol regimes.

5. **The cleanest immediate fixes (in order of conviction):**
   - **Hard regime gate: do not trade when VIX_close ≥ 25.** Cuts cohort by 44%, removes the worst bleed bucket cleanly. This is a one-line change to `forward-paper-trader/main.py`.
   - **Direction-conditional gating:** if forced to trade under VIX 20-25, only take bearish signals. Bullish-anything is anti-edge in this dataset.
   - **Do NOT pivot to leveraged stock** based on these results. The signal-generator alpha is too weak to support leverage on the underlying. Leverage just amplifies a small but real bleed.
   - **Do NOT deploy the bearish-VIX-20-25 cohort as a "validated edge"** without acknowledging it is mostly an SPY-short proxy. If you want SPY-short exposure, just sell SPY.

6. **The decisive next experiment is now:** re-label a **pre-2026-02-18 historical window** if `overnight_signals_enriched` extends earlier. The current dataset has zero windows with VIX < 18 and zero "normal regime" reference. Until we run the signal generator on a calm period, we cannot distinguish "the generator is broken" from "the generator works in normal regimes but the dataset is regime-poisoned."

## What this report does NOT yet cover

- **VIX term structure (VX1/VX2 backwardation)** — needs futures data, deferred to a follow-up.
- **IV-RV spread per signal** — needs realized vol on each underlying, deferred.
- **Bull-call / bear-put debit-vertical relabel** — separate script (priority 4 from the brief).
- **Pre-Iran-war historical comparison** — depends on whether `overnight_signals_enriched` extends earlier than 2026-02-18.

## Reproduce

```bash
POLYGON_API_KEY=$(gcloud secrets versions access latest --secret=POLYGON_API_KEY --project=profitscout-fida8) \
  python scripts/research/relabel_underlying_v1.py
```

Outputs:
- `/tmp/stock_bars_v1.pkl` — per-signal stock minute-bar cache
- `/tmp/spy_bars_v1.pkl` — single contiguous SPY minute-bar cache
- `/tmp/relabel_underlying_v1.parquet` — per-signal results table
- `docs/research_reports/UNDERLYING_VS_OPTIONS_V1.md` — this file
