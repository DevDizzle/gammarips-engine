Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (selection layer; exit is [[v7-gigo-same-day-exit]])
Source: docs/DECISIONS/2026-06-04-bracket-tournament.md; CLAUDE.md "Current policy"
Date: 2026-07-17

# The daily pick is a randomized bracket tournament (one signal/day or none)

Selection is a **randomized bracket tournament** run at the `signal-judge` Cloud Run
service (`tournament_v1`, version 7, `gemini-3.1-pro-preview`). It produces **one signal
per day or none** — the trader then simulates ONLY the ticker written to
`todays_pick/{scan_date}` (max one ledger row per day).

Mechanics: **3 independent brackets**, each shuffles the capped pool into batches of ≤10,
**top-2 advance** per batch (94→20→4→1). The **consensus** winner across the 3 brackets is
the pick, and agreement sets confidence: **3/3 = high, 2/3 = medium, 1/3 = low**.

The prompt is dead-simple ("make money buying a single option, sell for profit in 3
days") plus the daily report for context plus per-contract JSON — **no memory, no rubric,
no weights**. It is **fail-closed on error: no fallback** (a judge error produces no pick,
never a degraded pick).

Inputs to the tournament: the enriched pool after the [[bullish-only-hard-gate]] and the
[[tourney-pool-cap-edge-rank]] soft pre-rank, past the two safety rails
([[earnings-exclusion-rail]], [[regime-rail-vix-term]]) and the [[live-oi-floor]], each
candidate [[assert-no-leakage-gate]]-checked.
