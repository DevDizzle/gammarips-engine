Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: 3-day hold, +80/−60 bracket-replay labels (option PnL); N=1,375 fills, ~33 days
Source: docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md; INTELLIGENCE_BRIEF 2026-06-05; FINDINGS_LEDGER §direction/flow_intent
Date: 2026-07-17

# Bullish direction asymmetry — the one robust lever

On the realized-option-PnL bracket-replay (workflow `wf_16b5c00d-347`, N=1,375 FILLED, 33
days, baseline mean −0.44%), the ONLY robust, leakage-clean, breadth-viable lever was
**DIRECTION**: BULLISH EV **+4.11%** (win 0.470, ~26/day) vs BEARISH **−7.71%**. Five other
feature families (trend overlays, vix3m conditioner, moneyness>5%, catalyst exclusion,
active-strikes≥10) were dead-ends.

Caveat: the bearish leg was measured in one 2026 Q1/Q2 war-chop window with near-zero
`vix3m_at_enrich` variance, so "bearish is broken" is regime-conditional in principle — the
research call was to NOT bake in bullish-only and revisit at N≥15 live. That said, the
engine DOES run a bullish-only HARD gate today ([[bullish-only-hard-gate]]) as an
owner-directed policy override. This is a 3-day-era finding; do not extrapolate the
magnitude to the live same-day exit ([[fixed-exit-composites-negative]]).
