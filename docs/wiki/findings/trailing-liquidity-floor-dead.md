Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: fill-model / liquidity screen (exit-agnostic); V5.4-eligible cohort
Source: docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md; INTELLIGENCE_BRIEF 2026-05-27 (H15)
Date: 2026-07-17

# Trailing-liquidity volume floors do not separate fillable from unfillable — dead approach

H15 (add a per-day volume floor to the `active_days_20d ≥ 5` gate) was tested and REJECTED.
Trailing daily volume — as a count OR a floor — does not separate fillable from unfillable
contracts: any floor that rejects the dead names (EQIX, BLK) also rejects real fills (OKTA,
BBY) and darkens ≥42% of days; the +80% winner HTZ had only 3 active days; dead BLK had the
MOST trailing activity (12 days) yet never printed. A quote-based fill model also dead-ended
(no Polygon NBBO on our tier, [[spread-gate-retired]]).

Resolution: `INVALID_LIQUIDITY` is accepted as a paper-only artifact that overstates
real-world un-fillability; the `active_days_20d ≥ 5` gate was left untouched but flagged as
possibly net-harmful for the eventual go-live diagnostic. **Do not pursue another
trailing-liquidity gate variant — the approach is dead.** (This whole gate class was later
removed anyway, [[selection-gates-removed]].)
