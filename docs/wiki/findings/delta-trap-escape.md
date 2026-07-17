Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: realized 3-day OPTION PnL; N=1,375 fills, 33 scan-dates, single 2026-Q2 regime
Source: docs/DECISIONS/2026-06-09-narrative-vs-physics-roi.md
Date: 2026-07-17

# Delta is the only contract feature that separates won from lost — "enough delta"

On realized 3-day OPTION PnL, among the 738 right-direction trades, **36% still lost the
option** (the two-label trap). What separates won from lost:
- **Move magnitude dominates** (winners' underlyings moved 6.63% vs 4.08%) — but that is an
  OUTCOME, not a tradeable input.
- **Delta is the only CONTRACT feature that cleanly separates won from lost** (0.191 vs
  0.122, CI [+0.003,+0.141]) and is the single most OOS-stable finding (H1 +0.067 ≈ H2
  +0.069). NO narrative feature (overnight_score, catalyst_score) separates them.

Acted on as picker prior Q19: prefer **"enough delta"** to monetize a modest (~5%) move —
NOT a target band (the mid-delta "band" did NOT survive cross-conditioning on moneyness;
positive cells were far-OTM small-N). Deep-OTM lottery tickets are the named failure mode.
Neither narrative NOR broad physics (theta, convexity, IV-rank, spread) is a reliable lever
on this regime; do NOT gut the story layer, do NOT add a broad physics tilt. Single regime;
re-confirm cross-regime. Related delta-band conditioner: [[momentum-60d-enrichment-tilt]].
