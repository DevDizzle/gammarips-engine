Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: contrast of the 3-day opp_* window vs the live same-day GIGO window
Source: 2026-08-14 option_minute_paths window study (memory same-day-vs-3day-window-mismatch); FINDINGS_LEDGER §2026-08-19 (tradeable subset)
Date: 2026-08-14

# Quoting a 3-day statistic at a same-day decision inverts the answer

The harvest / surface / exit_rule views (and the MCP `query_outcomes` tools built on
them) are locked to a **3 trading day** window. The live policy
([[v7-gigo-same-day-exit]]) exits the **same day** at 15:45 ET. The two windows give
opposite answers to the same question. Measured 2026-08-14 on `option_minute_paths`
(delta 0.35-0.65, N=2,112, 10:00 ET entry):

| statistic | 3-day | same-day |
|---|---|---|
| median peak return | +21.4% | **+3.8%** |
| median MAE | −36.3% | **−11.0%** |
| touch-EV maximum | +50% | **falls monotonically from +20%** |

Under the full same-day bracket EV the flat **+40% target is already the argmax**, and no
target between +30% and +60% is distinguishable (t=−0.88): there is no free EV in
re-targeting. A live example of the inversion: the 3-day surface says tradeable contracts
have MORE upside than ghosts (+29.5% vs +18.3% median peak) while the same-day window
says upside is equal and downside much worse ([[ghost-rows-flatter-pool-composites]]).

Rule: always state the window with the number, and never carry a 3-day statistic into a
same-day decision. This is the window-mismatch instance of the program's exit-context
doctrine (see WIKI-SCHEMA on `Exit-context`).
