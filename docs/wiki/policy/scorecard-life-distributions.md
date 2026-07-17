Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (public presentation policy; the fixed exit is a measurement instrument, not the story)
Source: docs/DECISIONS/2026-07-08-scorecard-life-distribution.md
Date: 2026-07-17

# Public Track Record shows full-life distributions, not ROI under a fixed exit

The public `/scorecard` stops leading with ROI / win-rate under the fixed same-day GIGO
bracket and instead shows the **distribution of what every surfaced contract's premium did
from the morning it was surfaced to the day it expired** — the full opportunity surface with
the exit left as a free variable. This is a PRESENTATION policy change (public data
exposure); the live V7.1 trader, tournament, and labels are untouched.

Why: the fixed 1-day exit is a **measurement instrument, not a strategy**, so grading the
pool under one arbitrary exit contradicts the product's core claim ([[fixed-exit-composites-negative]]).
The honest, differentiated story is the two-sided distribution — the CEILING (peak premium
before expiration, strongly right-skewed) and the FLOOR (hold-to-settlement, mostly ruinous
with a fat right tail); the thesis lives in the gap. The NEGATIVE blind-buy baseline SURVIVES
as prose — it stays load-bearing for the data-not-advice posture. Any public data-exposure
change requires `gammarips-review` first.
