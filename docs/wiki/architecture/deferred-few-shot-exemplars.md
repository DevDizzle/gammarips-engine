Status: active
Type: architecture
Tag: untested-hypothesis
Exit-context: n/a (deferred picker-input idea)
Source: docs/DECISIONS/2026-05-09-DEFERRED-few-shot-picker-exemplars.md
Date: 2026-07-17

# DEFERRED — few-shot exemplars for the picker

Showing the picker "what ripped yesterday" as few-shot exemplars (so it pattern-matches
today's pick toward winning structure) is DEFERRED, not killed. The mechanism is sound
(few-shot exemplar prompting is well-established), but it needs a real closed-trade base
first.

Trigger to revisit: the ledger has **≥15 closed trades (≥5 winners AND ≥5 losers**, ideally
with ≥3 time-exits) so the exemplars represent genuine winning and losing structure rather
than noise. Note the current tournament deliberately runs with **no memory / no exemplars**
([[bracket-tournament-selection]]) — quant.md is injected but `exemplars.md` is deliberately
excluded ([[picker-case-memory]]) — so re-adding exemplars would be a real selection-design
change requiring the full evidentiary bar.
