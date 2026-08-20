Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (identity note; the exit it names is [[v7-gigo-same-day-exit]])
Source: CLAUDE.md "Current policy"; docs/DECISIONS/2026-06-22-v7-1-tilted-gigo-cohort-reset.md; docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md
Date: 2026-07-17

# V7.1 "Tilted GIGO" is the live policy

The live trading policy is **V7.1 "Tilted GIGO"**: `policy_version='V7_1_TILTED_GIGO'`.
The cohort start is the `LIVE_COHORT_START_DATE` constant in `signal-notifier/main.py`
(2026-08-13 as of the 2026-08-12 reset). Read the constant, do not cache the date in a
doc. Every ledger write and every cohort reader stamps and filters on this label; never
mix it with prior-era rows in analysis.

V7.1 is a composite of three unchanged pieces:
- **V6 SELECTION** — the randomized bracket tournament ([[bracket-tournament-selection]]),
  unchanged since 2026-06-04.
- **V7 EXIT** — the same-day get-in-get-out bracket ([[v7-gigo-same-day-exit]]), which is
  the only thing V7 changed (2026-06-17); V6's −60/+80/3-day hold is DEAD.
- **".1 Tilted"** — the 60-day-momentum enrichment pre-rank tilt
  ([[momentum-60d-enrichment-tilt]]) added 2026-06-19; the cohort was reset to isolate its
  effect.

Every claim about "what the engine runs today" resolves to one of the linked notes.

**Amended 2026-08-20 (cohort history).** The cohort has reset four times (06-25, 07-28,
08-07, 08-12) while `policy_version` stayed `V7_1_TILTED_GIGO`. The current cohort is
the fail-soft-restore-closed cohort, start 2026-08-13 (owner call 2026-08-12,
docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md). Rows from earlier resets
stay in the ledger and the cohort date filter excludes them.
