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
