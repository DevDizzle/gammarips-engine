# Decision: V4 Fresh Start — No Gates, Collect Everything, Discover What Wins

**Date:** 2026-04-12
**Status:** Deployed
**Supersedes:** Nothing — V3.1 runs untouched as a live control

## Problem

V3.1 produced only 29 trades in 7 weeks. Two bottlenecks:

1. **Enrichment gate (`overnight_score >= 6`)** passes ~75 rows/day out of ~1,100. The pipeline is starved upstream.
2. **Premium score gate (`premium_score >= 2`)** filters out the vast majority of enriched signals for a modest win-rate lift (76.3% at score=0 vs 84% at score>=2, N=1,547 vs N=81). Individual flags are mixed: `high_rr` helps (+8.7pp), `bull_flow` (-5.3pp) and `high_atr` (-3.1pp) hurt. HEDGING vs DIRECTIONAL flow intent: 78.6% vs 77.3% — essentially identical.

With N=29, there is no statistical basis for tuning gates. The system needs data.

## Decision

Deploy V4 as a **completely independent parallel pipeline** alongside V3:

| | V3.1 (untouched) | V4 (new) |
|---|---|---|
| Enrichment service | `enrichment-trigger` | `enrichment-trigger-v4` |
| Enrichment table | `overnight_signals_enriched` | `overnight_signals_enriched_v4` |
| Enrichment gate | `overnight_score >= 6` | `score >= 1 AND spread <= 10% AND directional UOA > $500K` |
| Trader service | `forward-paper-trader` | `forward-paper-trader-v4` |
| Trader reads from | `overnight_signals_enriched` | `overnight_signals_enriched_v4` |
| Ledger table | `forward_paper_ledger_v3_hold2` | `forward_paper_ledger_v4_hold2` |
| Premium gate | `premium_score >= 2` | **None** |
| Vol/OI gate | `vol>=100 AND oi>=50 OR oi>=250` | **None** |
| Spread cap | None | `<= 0.10` (applied upstream in enrichment) |
| Trader-side filter | Premium + vol/oi | **None** — everything enriched is tradeable |

Both pipelines read from the same upstream `overnight_signals` table. They diverge at enrichment.

### What stays the same

- Bracket: +40% TP / -25% SL
- Hold days: 2
- Direction handling: both
- Gemini with full news grounding (flags computed and stored for discovery)
- Entry time: 15:00 ET on D+1
- Upstream scanner

### Spread cap rationale

Research on the V4 backtest dataset (7,480 signals with Polygon D+1/D+2/D+3 bars):

- 0-5% spread: +1.1% mean return, 28% win rate
- 5-10% spread: breakeven zone
- 10-20% spread: losses accelerate
- 30-40% spread: -14.5% mean, 15% win, 73% stop rate

Spread is the **only monotonic liquidity feature**. Volume and OI are anti-correlated with bracket outcome (counter-intuitive but consistent: crowded high-vol names have directional edge priced in). 10% cap is defensible; 5% would be tighter but may shrink universe too much for the data collection goal.

### No backfill

Fresh start. `forward_paper_ledger_v4_hold2` begins empty. V3 data remains in its own tables for comparison.

## 30-day plan

After collecting N >= 500 trades (estimated 60-90 days at 20-50+ trades/week):

1. Join `forward_paper_ledger_v4_hold2` with `overnight_signals_enriched_v4` on `recommended_contract` + `scan_date`
2. XGBoost classifier on `exit_reason` (TARGET/STOP/TIMEOUT) with all enriched features
3. SHAP values for per-feature contribution
4. Single decision tree (depth 3-4) for interpretable threshold rules
5. Bootstrap validation (1000 resamples) for confidence intervals
6. Output: empirically validated feature thresholds for a V5 gate

## What happens to V3

- If V4 works: sunset V3 (stop scheduler, keep tables)
- If V4 fails: kill V4, V3 continues unchanged
- Zero risk to current pipeline
