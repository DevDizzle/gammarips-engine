Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (a pick-time liquidity refresh, not an edge)
Source: docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md; CLAUDE.md "Current policy"
Date: 2026-07-17

# Live-OI floor at the ~09:45 ET pick

`signal-notifier` re-fetches **live open interest at the ~09:45 ET pick moment** and drops
contracts below `OI_FLOOR` (default **1000**), so the tournament selects on FRESH
liquidity rather than the stale scan-time snapshot. It is **fail-soft**: if the live fetch
comes back empty or errors, it falls back to the top-8 by the existing rank rather than
skipping the day.

This is the ONE liquidity screen that survives at pick time; it is distinct from the old
selection gates that were removed ([[selection-gates-removed]]) because it reads
point-in-time OI at the entry morning, not the frozen overnight snapshot
([[oi-volume-session-frozen-walled-off]]). The cohort was reset when this landed.
