Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: 3-day +80/−60 bracket-replay, realized option PnL; N=1,375, per-moneyness-bucket
Source: docs/DECISIONS/2026-06-02-moneyness-cap-widen-to-13.md; INTELLIGENCE_BRIEF 2026-06-02 (H17)
Date: 2026-07-17

# Moneyness cap widened to 0.13 — the 10–13% OTM increment is additive

Realized-option-PnL backtest (N=1,375): the 10–13% OTM increment adds **+8.9% mean** (90%
CI [+.014,+.163], flat cost), reliably present on ~82% of days (~4.5/day); the toxic
(0.14,0.15] bin is −15% (CI all-negative) and is excluded by stopping at 0.13. STRICT
`MONEYNESS_MAX` widened 0.10 → **0.13** (2026-06-02, owner-directed); the FALLBACK cap was
decoupled and pinned at 0.10 so deeper-OTM cannot leak onto low-conviction skip days; floor
unchanged 0.05.

This REVISITS the earlier H12 tightening (0.15→0.10). Mechanism correction: H12 cited the
Aretz/Augustin deep-OTM EV cliff, but that is a HOLD-TO-EXPIRY (VRP/theta) result; our trade
is a short bracket on a 7–45 DTE option where theta is negligible and we never ride to
expiry, so that literature does not bind here. Caveat: thin/single-regime; reversible.
