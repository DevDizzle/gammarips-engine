Status: superseded
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md (removed by docs/DECISIONS/2026-06-04-bracket-tournament.md)
Date: 2026-07-17

# active_days_20d liquidity gate — introduced 2026-05-19, REMOVED 2026-06-04

The `active_days_20d >= 5` gate rejected any finalist whose contract had fewer than 5 of the
prior 20 sessions with volume > 0 (fail-closed on a Polygon error). Trigger: the 2026-05-14
KBR pick cleared every point-in-time gate but marked INVALID_LIQUIDITY (the "323 contracts"
was one block trade; the contract printed on only 4 of 21 prior days).

Superseded twice over: (1) trailing-liquidity floors were later shown NOT to separate
fillable from unfillable ([[trailing-liquidity-floor-dead]]), and INVALID_LIQUIDITY was
accepted as a paper-only artifact; (2) the gate was REMOVED on 2026-06-04 with the rest of
the selection-gate stack ([[selection-gates-removed]]), because scan-time liquidity chokes
the names that only fill the next morning. Decision-time liquidity now comes from the live
pick-time [[live-oi-floor]], not a trailing-days gate. Do not reintroduce a trailing
active-days gate.
