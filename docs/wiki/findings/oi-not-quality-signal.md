Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: realized option PnL, 3-day bracket; OI is a fillability gate not a quality lever
Source: INTELLIGENCE_BRIEF 2026-06-02; FINDINGS_LEDGER §recommended_oi quintile
Date: 2026-07-17

# Open interest is a fillability gate, not a quality signal

On the realized-option-PnL cohort, higher recommended `recommended_oi` is monotonically
WORSE by quintile — it is NOT a pick-quality lever. An earlier leaked-label audit (using an
UNDERLYING peak label) mistakenly fingered `OI ≥ 10` as the single worst gate; on real
option PnL that flips to neutral/positive because OI is a **fillability** condition and the
FILLED cohort is already conditioned on it.

Practical rules: do NOT relax the OI/vol fillability floor (unlike V/OI, which IS an
anti-edge — [[voi-ratio-anti-edge]]); but also do NOT read high OI as conviction. And note
the stored OI/volume are session-frozen snapshots walled off from the judge
([[oi-volume-session-frozen-walled-off]]); the only decision-time liquidity read is the
live pick-time [[live-oi-floor]].
