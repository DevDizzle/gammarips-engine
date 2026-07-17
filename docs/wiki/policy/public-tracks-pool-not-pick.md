Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (public surface scope)
Source: docs/DECISIONS/2026-07-03-pool-track-record-and-generator-depicking.md
Date: 2026-07-17

# Public surfaces track the POOL; the daily pick is private

Owner call: the public scorecard tracks **everything the engine produces daily** — the
~50-candidate enriched pool — NOT the single tournament pick. The pick leaves every public
surface: content generators (x-poster, blog) are de-picked, and the daily pick is the
operator's PRIVATE signal (off the public product to avoid liquidity-stampede + scalping
optics, and because an operator trading into a published pick is an SEC scalping-fraud
fact pattern).

Mechanics: `win-tracker` `/pool_outcomes` aggregates `enriched_option_outcomes` (whole
labeled pool — same-day + 3-day labels + opportunity surfaces) → Firestore
`pool_outcomes/current` (values are FRACTIONS, fail-loud on degraded substrate, idempotent
recompute from BQ truth so an unauth trigger can only refresh, not poison). Daily
`pool-outcomes-refresh` 17:20 ET after the 17:00 label cron. The public Track Record shows
pool distribution tiles with the NEGATIVE blind-buy baseline published prominently
([[scorecard-life-distributions]], [[fixed-exit-composites-negative]]).
