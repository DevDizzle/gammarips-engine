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
