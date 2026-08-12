Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (a selection-time stand-down rule)
Source: docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md; docs/research_reports/handoffs/2026-08-12-tournament-liquidity-regression.txt
Date: 2026-08-12

# When nothing is tradeable, the engine says nothing

If every candidate fails the two-tier slate floor ([[live-oi-floor]]), `signal-notifier`
fails closed with `skip_reason="no_liquid_candidates"` and publishes no pick. It does not
manufacture a slate out of the reject pile.

**Why the rule exists.** From 2026-07-28 to 2026-08-12 the fail-soft floor restored
dropped candidates up to `TOURNEY_MIN=8` "so the tournament never starves to zero", and
`_print_floor_restored` was popped before `/rank`. The judge therefore chose from names
that had failed a liquidity floor, could not tell which ones, and picked them roughly in
proportion to their share of the slate — 08-11 ALC (26.1% spread, owner entered, -$312)
and 08-12 MDB (44.6% spread, the worst ever measured on a pick, rationale: "securely
execute" on a 15-lot bid). A floor on slate SIZE with no floor on slate QUALITY is not a
reliability property; it guarantees an output when the correct output is the empty set.

**The interlock.** A no-pick day needs EVIDENCE, not the absence of a crash. A total
Polygon failure does NOT raise: the batch completes with `live_oi=None` on every row, and
the OI floor would then judge the slate on stale frozen scan-time OI and sweep it to zero.
So `stats["measured"]` also requires the live read to answer for at least
`LIVE_FETCH_MIN_OK_FRAC` (0.5) of the slate. Five paths leave it False (exception, both
kill switches, empty input pool, degraded read) and none of them can return an empty
slate. Measured cost: 1 no-pick day per ~15 sessions (2026-07-24 in the replay).

The operator gets an email on a stand-down, with the counts. `post_to_openclaw` has been a
no-op since 2026-07-03, so a WhatsApp-only stand-down would be silent, and a silent
morning cannot be told apart from a dead cron.

Same family as the other stand-downs — [[regime-rail-vix-term]],
[[earnings-exclusion-rail]], [[market-holiday-standdown]], [[mass-leakage-fail-closed]].
The daily-cadence guarantee died with the V5.4 fallback ([[daily-cadence-fallback-removed]]);
this is one more day the engine is allowed to be silent, and a no-pick day is the most
credible thing a signal service can say.
