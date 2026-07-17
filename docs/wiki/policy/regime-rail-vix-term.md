Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (a regime skip-day rail, not a selection edge)
Source: CLAUDE.md "Current policy"; docs/DECISIONS/2026-06-03-vix3m-fred-retry-and-carry-forward.md
Date: 2026-07-17

# Safety rail 2 — regime fail-closed when VIX > VIX3M

`signal-notifier` fails closed and takes no new position when the VIX term structure is in
**backwardation (`VIX > VIX3M`)** — i.e. a position is only opened when `VIX <= VIX3M`.
Backwardation flags acute near-term stress where long-call P&L historically degrades; the
rail skips the day rather than trade into it.

The VIX3M read is sourced from FRED with a retry + carry-forward on missing data (so a
single FRED gap does not silently disable the rail). This is one of exactly two safety rails
kept after the 2026-06-04 gate purge ([[earnings-exclusion-rail]] is the other); it is a
regime EXCLUSION, literature-defensible but graded "coin flip" in the V5.3 lit audit, kept
for its downside protection ([[literature-audit-v5-3-stack]]).
