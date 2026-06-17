# 2026-06-17 — V7 INTRADAY bracket (get-in-get-out): V6 selection + same-day exit

**Status:** IMPLEMENTED — pending `gammarips-review` re-sign + deploy. **FULL CUTOVER, owner-directed 2026-06-17: V6 is DEAD; V7 is the SOLE live policy.** `forward_paper_ledger` + `cohort_stats` + the public Scorecard are repointed to `V7_INTRADAY`, and the V6 picks are re-simulated (backfilled) under the V7 exit so the track record reflects V7. (This SUPERSEDES the earlier "parallel-first" draft of this note — the owner chose to flip live in place, not shadow.) The G-Stack 30-day-OOS ceremony is owner-waived; the leakage/correctness audit is not (passed: mechanics/trail-inertness/bracket/relabel/backfill all clean).

## Problem
The V6 exit is a **+80% target / −60% stop / 3-day hold**. On the realized-option-PnL pool it is a slight loser (day-weighted mean −0.63% over the full enriched pool; −0.24% on the 3-day bracket baseline for bullish fills), and it **gives back early gains** — the owner watches picks (TER, ANET) spike intraday then fade over the 3-day hold. The metric we never scored is **velocity of capital**: capital tied up 3 days per trade turns over far slower than a same-day exit that frees it for tomorrow's signal.

## Evidence (`backtesting_and_research/exit_velocity_sweep.py`)
Re-replayed the 1,375 FILLED fills (846 BULLISH) under a grid of exit policies on the SAME cached minute bars, **every exit charged 2% slippage** (so higher-velocity policies pay their round-trips), day-level bootstrap CIs (effective N = ~33 scan-dates, not rows):

| Policy | Mean/trade | Win% | Days held | Return/capital-day | Worst (p5) |
|---|---|---|---|---|---|
| BASELINE 80/60, 3-day | +2.0% | 44% | 2.49 | +0.82% | −61% |
| GIGO +40/−30, **same-day** | +2.6% | 38% | 1.0 | **+2.64%** | **−34%** |
| GIGO +30/−30, same-day | +2.4% | 38% | +2.40% | −34% |
| GIGO ride/−30, same-day | +2.8% | 38% | +2.83% | −34% |

Findings: (1) **The lever is SAME-DAY EXIT, not the target magnitude** — every H1 target from +30 to "let it ride" lands ~+2.4–2.8%/trade; a small target with a 2–3 day hold is the *worst* policy (clearly negative). (2) Same-day is per-trade ~tied with the 3-day hold but frees capital ~2.5× faster → **~3× return-per-capital-day**, and it **halves the disaster tail (−34% vs −61%)**. (3) −30% stop beats −40% on the tail; magnitude within H1 is noise. (4) HONEST LIMIT: the per-trade *improvement* is NOT statistically significant at the day level (CIs include 0, single regime, 33 days) — the case rests on **velocity + tail reduction**, not higher per-trade EV.

## Decision
**V7 = V6 selection UNCHANGED + an intraday OCO bracket.** The signal-judge tournament still picks the daily ticker/contract; only the trader's exit changes:
- Entry: 10:00 ET (unchanged)
- **Take-profit: +40%** limit
- **Stop: −30%**
- **Time-exit: 15:45 ET same day** (flat no matter what), **no trail**, **no overnight hold**
- First leg to fire wins; conservative intrabar ordering (stop before target), 2% slippage both sides (production-faithful).
- Cohort tag `policy_version='V7_INTRADAY'`.

## Roll-out — FULL CUTOVER (owner-directed)
V6 is retired. The live trader (`forward-paper-trader`) now writes `policy_version='V7_INTRADAY'`; every cohort reader (`signal-notifier` cohort_stats + ledger_trades, `win-tracker`, `x-poster`, `blog-generator`) filters `V7_INTRADAY`. The V6 picks (scan_dates 2026-06-05..) are re-simulated under the V7 exit via the trader's idempotent delete-then-load, so `forward_paper_ledger` ends with V7 rows only and the public Scorecard reflects V7. `LIVE_COHORT_START_DATE=2026-06-04` still brackets the relabeled picks. Reversible only by revert + re-backfill (not a one-line flip) — accepted, owner-directed.

## Degenerate experiment (handle)
With same-day exit, `paper_shadow_intraday` (the V6-era 3-day-vs-intraday 2×2, `docs/DECISIONS/2026-06-08-intraday-hold-shadow.md`) COLLAPSES — both arms are now intraday and `hold_3day_return_pct` is no longer a 3-day hold. The intraday shadow is **retired by V7** (the live policy IS the intraday exit). Left running (walled-off, harmless) but no longer a valid experiment; retire/repurpose later.

## Out of scope (noted)
Selection is untouched ("keep our picks"). A tighter OI/volume liquidity floor for fast intraday fills is a plausible *selection-side* follow-up (fast in/out needs fillable contracts) but is NOT in V7.

## Caveats
Single regime (2026-Q2 war-chop), pre-V6 all-directions pool (bullish subset N=846), ~33 effective days, per-trade improvement not significant (velocity + tail is the case). Backtest is on the enriched POOL, not the live picks (exit mechanics generalize). 2% slippage modeled per side. Source: `backtesting_and_research/exit_velocity_sweep.py`. On promotion, update `docs/TRADING-STRATEGY.md` + `CHEAT-SHEET.md`.
