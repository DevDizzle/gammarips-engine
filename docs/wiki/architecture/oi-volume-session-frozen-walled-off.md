Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md (DEFERRED item); CLAUDE.md "Current policy"
Date: 2026-07-17

# OI and volume are session-frozen snapshots — walled off from the judge

Recommended `oi` and `volume` on an enriched signal are **session-frozen snapshots** (the
scanner's scan-time read), not point-in-time-at-decision values. Because a point-in-time
feed would require richer Polygon data, they are DEFERRED as decision features and
**walled off from the tournament judge prompt** — they are used ONLY in the scanner's
relative ranking of the pool, never as an input the LLM conditions on.

This is the standing data-contract rule the 2026-06-04 bug-hunt left in place
([[pipeline-bug-hunt-2026-06-04]] stripped these fields from the judge prompt). The
distinct, allowed liquidity read is the pick-time [[live-oi-floor]], which re-fetches
LIVE OI at ~09:45 ET. Do not reintroduce the frozen snapshots into the judge or into a
trader gate.
