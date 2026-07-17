Status: active
Type: architecture
Tag: untested-hypothesis
Exit-context: n/a (deferred real-money execution path)
Source: docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md
Date: 2026-07-17

# DEFERRED — Alpaca agent for real-money execution

An Alpaca-based agent to trade the daily pick programmatically and grow the account is
DEFERRED, documented so the path is captured before context fades. **Implementing it
prematurely is the worst-case outcome** (real money on an unmeasured edge).

Trigger to revisit: positive expectancy demonstrated on the data AND the operator confirming
he can make money trading it manually (later refined to N≥30 paper EV≥0 AND ≥15
operator-confirmed manual matches). Note the operator is now trading LIVE manually on
Robinhood (since 2026-07-09) via his own harness, which is the intermediate step; a live PDT
/ margin constraint must be reconfirmed with counsel before any programmatic real-money path.
Do not build this on an unvalidated edge.
