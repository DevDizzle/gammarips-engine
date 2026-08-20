Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: raw price legs on the day-1 tape (no bracket, no slippage), tradeable subset
Source: FINDINGS_LEDGER §2026-08-19 (entry hour)
Date: 2026-08-19

# The day's bleed concentrates in the first hour after entry

On the tradeable subset (11+ prints by 10:00 ET, N=548) the **10:00 → 11:00 window is
the single worst hour of the day: −5.32% mean**, while the other six windows sum to
about −2.5%. The live policy buys the worst hour on the clock every day. This
corroborates the 2026-06-22 entry-timing study ("at 10:00 you buy after the AM pop") on
the tradeable subset that study lacked power for (its liquid cell was N=55).

A later entry trades less loss for less opportunity: entering at 12:00 keeps median
same-day MFE +8.8% and skips the −5.32% hour, and the MFE:MAE ratio improves 0.59 → 0.70.
But by 15:00 the median best moment (+3.8%) sits below round-trip cost on most of this
pool. **Entering later removes a self-inflicted loss. It does not create an edge.**
Moving the entry is an OPEN owner call, flagged once; 10:00 ET remains the live entry
([[entry-1000-et]] has the policy status).

This is the fourth independent route to the same wall: a long OTM option held for a
fixed window bleeds regardless of selection or bracket ([[bracket-optimization-dead]],
[[option-pnl-not-underlying]], [[volatility-idiosyncratic-trap]]).
