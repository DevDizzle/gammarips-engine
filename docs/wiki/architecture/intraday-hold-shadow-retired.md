Status: retired
Type: architecture
Tag: architecture-fact
Exit-context: RETIRED — the live policy IS the intraday exit, so the shadow's 2×2 collapsed
Source: docs/DECISIONS/2026-06-08-intraday-hold-shadow.md (retired by docs/DECISIONS/2026-06-17-v7-intraday-bracket.md)
Date: 2026-07-17

# paper_shadow_intraday — the day-trade shadow, retired by V7

`paper_shadow_intraday` was a research-only shadow answering "does the edge survive a same-day
day-trade?" — get in 10:00 ET, out flat 15:45 ET, no stop, no 3-day hold. Together with the
top-score shadow ([[paper-shadow-topscore]]) it formed a 2×2 matrix: {Tournament, top-score} ×
{3-day, intraday}, four experiments.

Retired by V7: when the live exit BECAME the same-day intraday bracket
([[v7-gigo-same-day-exit]]), both arms of this shadow are now intraday and its
`hold_3day_return_pct` is no longer a 3-day hold — the experiment collapsed. It was left
running walled-off/harmless but is no longer valid; the day-trade question is now answered by
the live cohort itself. (Its finding fed the V7 decision: same-day frees capital ~2.5× and
halves the tail, [[exit-velocity-same-day-lever]].)
