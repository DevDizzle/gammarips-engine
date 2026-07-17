Status: retired
Type: policy
Tag: policy-adopted
Exit-context: RETIRED — was +80% target / −60% stop / 3-day hold; the live exit is same-day GIGO
Source: docs/DECISIONS/2026-04-17-v5-3-target-80.md (superseded by docs/DECISIONS/2026-06-17-v7-intraday-bracket.md)
Date: 2026-07-17

# V5.3 "Target 80" exit is retired (+80/−60/3-day)

V5.3 "Target 80" (2026-04-17) set the exit that governed the program for two months:
entry 10:00 ET, **+80% option target / −60% option stop / 3-day hold / 15:50 ET exit**, STOP
winning on ambiguous bars, later joined by a trailing stop ([[trailing-stop-retired-v7]]).
It came from the Apr-2026 Deep Research recommendation to abandon the pure 3-day timeout and
capture asymmetric profit-taking.

This whole exit is **DEAD under V7.1** — replaced by the same-day GIGO bracket
([[v7-gigo-same-day-exit]]) after the exit-velocity sweep showed same-day frees capital ~2.5×
faster and halves the tail ([[exit-velocity-same-day-lever]]). Kept as a retired note so the
+80/−60/3-day numbers are recognized as history, not current policy.
