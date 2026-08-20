Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: V7.1 same-day bracket replayed on the day-1 minute tape (no NBBO exists)
Source: FINDINGS_LEDGER §2026-08-19 (execution); docs/EXECUTION-RISK-GUIDELINES.md
Date: 2026-08-19

# Execution risk is exit certainty, not spread

The measurable execution problem on this pool is not "you pay a wide spread twice", it is
"you cannot transact when you need to". Four measured facts (day-1 tape, 4,292 legs):

- **The stop is not a stop.** Over N=547 breach events the realised fill sits median
  **−3.1%** past the intended −30% level, p10 −14.5%, worst −44.0%. On sub-10-print
  contracts the median is **−10.3%**. The slippage is one-sided, so it deepens the tail
  without touching the mean opportunity.
- **Prints by 10:00 ET is the dominant observable, and it is near-deterministic.** 0
  prints by 10:00 gives a 0.0% chance of 60+ prints for the rest of the day; 21+ gives
  93.0%. About 63% of the pool is effectively untradeable by 10:00 and about 14% is
  comfortably manageable.
- **Premium does NOT predict liquidity.** Median traded minutes falls as premium rises
  (<$0.50 → 12 min, >$5 → 6 min). Never use price or name recognition as a liquidity
  proxy. Count prints.
- **Modelled round-trip spread is second-order.** A percentage bracket is
  scale-invariant, so adverse-fill replays move the result only 2-4 points with no clean
  liquidity gradient. Do not spend effort modelling round-trip spread cost.

Context: no spread is measurable at all (`bid`/`ask`/`spread_pct` NULL in all 64,550
`pool_liquidity_snapshot` reads, [[spread-gate-retired]]), and 15:30-16:00 is the
thinnest block of the session (51.6% of legs printing), so the live 15:45 flat exit is
planned into the day's worst liquidity. No number is validated against a real fill yet.
See [[ghost-rows-flatter-pool-composites]] for the measurement-side consequence.
