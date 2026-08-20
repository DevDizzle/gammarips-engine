Status: active
Type: finding
Tag: policy-adopted
Exit-context: same-day GIGO and 3-day mechanics both tested with 10:00 ET entries
Source: FINDINGS_LEDGER §2026-06-22 (entry-timing resolved); INTELLIGENCE_BRIEF hard constraints
Date: 2026-07-17

# Enter around 10:00 ET, not at the open

The reference entry is **10:00 ET**. It skips the opening-auction chaos and the first
half-hour's spread blowout while still riding the morning OI build from the overnight
sweep (which is why the old scan-time liquidity gates were removed —
[[selection-gates-removed]]).

The 2026-06-22 entry-timing study RESOLVED the long-standing "earlier entry" question:
earlier entries are a **thin-tape mirage** — apparent edge came from illiquid fills that
would not have executed. KEEP 10:00. This is adopted policy rather than a large measured
edge, and it holds under both the live same-day exit ([[v7-gigo-same-day-exit]]) and the
retired 3-day bracket.

**Amended 2026-08-19 (later-entry question OPENED).** The earlier-entry question stays
CLOSED. The new fact runs the other way: on the tradeable subset (11+ prints by 10:00,
N=548) the 10:00→11:00 window is the single worst hour of the day at −5.32% mean, and
the other six windows sum to about −2.5% ([[first-hour-bleed]]). A later entry loses
less and gains less (a 12:00 entry keeps median same-day MFE +8.8%). The 06-22 "keep
10:00" verdict was a power limitation (liquid N=55), not a confirmation. Moving the
entry later is an OPEN owner call, flagged once. No code change was made and 10:00 ET
remains the live entry. See FINDINGS_LEDGER §2026-08-19 (entry hour).
