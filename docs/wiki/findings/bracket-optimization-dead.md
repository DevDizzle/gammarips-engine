Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: 840 bracket variants incl. no-target / no-stop / 15-day holds; signals_labeled_v1
Source: FINDINGS_LEDGER §Bracket Sweeps; INTELLIGENCE_BRIEF "what does NOT work"
Date: 2026-07-17

# Bracket optimization is a dead end — it is not a bracket-tuning problem

**0/840 bracket variants are profitable in-sample and 0/840 out-of-sample** on the labeled
cohort; the best is `15:55 / no-target / −20% stop / 3-day` at −1.99% OOS (n=464). Removing
the target, removing the stop, and 15-day holds were all tried. The trader loses money in
every bracket configuration tested — **this is not a bracket-tuning problem**, it is the
option-instrument bleed ([[option-pnl-not-underlying]], [[volatility-idiosyncratic-trap]]).

This is why the program pivoted from bracket search to (a) selection-within-pool and (b)
capital VELOCITY: the V7 same-day exit was NOT chosen for higher per-trade EV but for
turnover + tail reduction ([[exit-velocity-same-day-lever]]). Do not re-run brute-force
bracket sweeps expecting a profitable configuration to appear.

**REPLICATED on the tradeable subset, 2026-08-19.** The objection that the 840-variant
sweep ran on a ghost-contaminated whole-pool cohort was legitimate (about 58% of such rows
are fabricated-flat ([[ghost-rows-flatter-pool-composites]]), and the bracket fires on
8.8% of 0-2-print rows against 35.8% of tradeable ones). It did not change the answer: **0 of 432 variants profitable** on
TRADEABLE (11+ prints by 10:00, 591 legs / 50 days) AND on SEMI (6+ prints, 985 legs / 56
days), full period, in-sample, and out-of-sample. Cross-half rank correlation of variant
means is 0.575-0.581, so the grid orders consistently and there is simply nothing above
zero in it. Live V7.1 (+40/-30/15:45) is not the argmax even inside the losing set
(-9.76% against about -6.0% for the best variants), but every top variant sits ON the
tightest-stop boundary, whose extrapolation is "do not hold" rather than a better bracket.
**Doctrine now holds on every substrate measured. Re-open only with new data, never with a
new slice.** See FINDINGS_LEDGER §2026-08-19 (bracket sweep, tradeable).
