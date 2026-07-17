Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: CLAUDE.md "Current policy"; docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md
Date: 2026-07-17

# Ledger cohort/version labels — 5 / 6 / 7 mapping

`signal_ranker_runs` and the ledger carry integer cohort labels that map to selection eras.
When reading historical rows, never mix cohorts; filter to the era you mean:
- **5** = two-stage scorer→picker (V5.4).
- **6** = single judge (`judge_v6`).
- **7** = bracket tournament ([[bracket-tournament-selection]]), the current selection era.

The `policy_version` string on `forward_paper_ledger` is the other axis: the live value is
`V7_1_TILTED_GIGO` ([[v7-1-tilted-gigo-live-policy]]); prior strings include `V7_INTRADAY`,
`V6_TOURNAMENT`, `V5_3_TARGET_80`. For execution-history context: the V5.4 single-judge era
is in `docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md`. Keep this
metadata explicit on every ledger write.
