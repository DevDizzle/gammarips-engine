Status: retired
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-08-v5-4-locked-spec.md (superseded by docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md)
Date: 2026-07-17

# V5.4 Scorer→Picker LLM pair — retired (collapsed to single judge, then tournament)

V5.4 (spec locked 2026-05-08) replaced V5.3's deterministic SQL ranker with a **Scorer→Picker
LLM pair**, keeping V5.3's hard gates deterministic and upstream. It was the first
LLM-selection era.

Retired: the two-stage Scorer→Picker was collapsed to a **single judge** (V6, 2026-06-04,
ledger cohort label 5→6) and then to the **randomized bracket tournament** (label 7,
[[bracket-tournament-selection]]). The current selection prompt is deliberately
memory/rubric/weight-free — the opposite of V5.4's 60/25/15 weighted scoring. Kept as a
retired note so the Scorer→Picker architecture is recognized as history.
