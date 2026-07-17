Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (identity note; the exit it names is [[v7-gigo-same-day-exit]])
Source: CLAUDE.md "Current policy"; docs/DECISIONS/2026-06-22-v7-1-tilted-gigo-cohort-reset.md
Date: 2026-07-17

# V7.1 "Tilted GIGO" is the live policy

The live trading policy is **V7.1 "Tilted GIGO"**: `policy_version='V7_1_TILTED_GIGO'`,
`LIVE_COHORT_START_DATE='2026-06-26'`. Every ledger write and every cohort reader stamps
and filters on this label; never mix it with prior-era rows in analysis.

V7.1 is a composite of three unchanged pieces:
- **V6 SELECTION** — the randomized bracket tournament ([[bracket-tournament-selection]]),
  unchanged since 2026-06-04.
- **V7 EXIT** — the same-day get-in-get-out bracket ([[v7-gigo-same-day-exit]]), which is
  the only thing V7 changed (2026-06-17); V6's −60/+80/3-day hold is DEAD.
- **".1 Tilted"** — the 60-day-momentum enrichment pre-rank tilt
  ([[momentum-60d-enrichment-tilt]]) added 2026-06-19; the cohort was reset to isolate its
  effect.

Every claim about "what the engine runs today" resolves to one of the linked notes.
