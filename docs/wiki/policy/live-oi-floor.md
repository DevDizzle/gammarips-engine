Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (a pick-time liquidity refresh, not an edge)
Source: docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md; docs/DECISIONS/2026-07-28-tournament-liquidity-upgrade.md; docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md; docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md
Date: 2026-08-12

# The two-tier slate floor at the ~09:52 ET pick

`signal-notifier` re-fetches live liquidity per candidate at the pick moment and applies
**two floors** before the tournament sees the slate:

1. **PRIMARY — early prints.** Drop a contract whose entry-day print count is a KNOWN int
   below `PRINT_FLOOR_MIN` (default 1). The count is date-validated against
   `day.last_updated`, because Polygon serves the prior session's bar rather than a zero
   ([[polygon-snapshot-never-zero-day-bar]] in auto-memory). A fetch failure is UNKNOWN,
   not zero: that row is KEPT and falls through to the OI floor (fail-open per row).
2. **SECONDARY — live OI.** Drop effective OI below `OI_FLOOR` (live env **1000**,
   in-code default 200).

Survivors are soft-tilted by effective OI (fillability).

**A dropped candidate does not come back.** `FAILSOFT_RESTORE_MODE=none` (default, since
2026-08-12) means a name that failed either floor never reaches the judge and can never
become the pick. `TOURNEY_MIN` (8) is a SOFT target — it sizes the restore in the two
rollback modes (`empty_only`, `always`) and does nothing else. The old always-on restore
is why the judge picked sub-floor contracts on 08-11 and 08-12
([[no-liquid-candidates-no-pick]] has the mechanism and the cost).

Fail-soft means fail-soft on ERROR, not on thinness: any exception in the floor returns
the input pool untouched, and both kill switches (`LIQUIDITY_TILT=false`,
`PRINT_FLOOR_ENABLED=false`) restore earlier behavior bit-identically. A *successful*
measurement of "nothing cleared" is the one case allowed to empty the slate.

This is the ONE liquidity screen at pick time; it is distinct from the removed selection
gates ([[selection-gates-removed]]) because it reads point-in-time liquidity on the entry
morning, not the frozen overnight snapshot ([[oi-volume-session-frozen-walled-off]]). It
gates STRICT days only — the fallback path bypasses it. Neither floor measures **spread
or dollar depth**, which is what actually decides whether the position can be exited
([[spread-gate-retired]]); both are proxies, and a 44.6%-spread contract cleared them on
2026-08-12. The cohort was reset when the OI floor landed (06-25) and again when the
print floor started firing (08-07); the 08-12 restore change did NOT reset it.
