Status: superseded
Type: policy
Tag: policy-adopted
Exit-context: SUPERSEDED — was a 3-day-hold trail; the live exit is same-day GIGO with NO trail
Source: docs/DECISIONS/2026-05-09-trailing-stop-25-at-30-pct.md (superseded by docs/DECISIONS/2026-06-17-v7-intraday-bracket.md)
Date: 2026-07-17

# The 25%-off-peak trailing stop is RETIRED (superseded by V7 no-trail)

The V5.3/V6 era ran a trailing stop: once peak premium reached `entry × 1.30`, a trail
activated at `peak × 0.75` (ratcheting up, never down), dominating the −60% hard stop while
the +80% target stayed. It added `trail_trigger_price` and `peak_premium` ledger columns.

This is **DEAD under V7.1**: the live exit is same-day GIGO with **no trail, no overnight**
([[v7-gigo-same-day-exit]]) — the trade flattens at 15:45 ET regardless. Kept as a superseded
note so a fresh session does not reintroduce a trail: the exit-velocity evidence
([[exit-velocity-same-day-lever]]) is what replaced it. The `peak_premium` concept survives
only in the RESEARCH opportunity surface ([[opportunity-surface-substrate]]), not as a live
exit rule.
