Status: superseded
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-01-daily-cadence-fallback.md (removed by docs/DECISIONS/2026-06-04-bracket-tournament.md)
Date: 2026-07-17

# Daily-cadence fallback — introduced 2026-06-01, REMOVED 2026-06-04

The daily-cadence fallback (surface a trade on every tradeable day) re-queried with the
pure-conviction gates relaxed — dropping `V/OI > 2` and widening the moneyness band — to
surface the best FILLABLE candidate when the strict stack left zero. Its motivating case
(scan 2026-05-26: 24 candidates scoring 7–8, all rejected by conviction/liquidity gates on a
day with real fillable signal) was correct in spirit.

But it was **REMOVED on 2026-06-04** with the whole selection-gate stack
([[selection-gates-removed]]): once all enriched signals reach the tournament and V/OI is a
proven anti-edge ([[voi-ratio-anti-edge]]), there is no strict stack to fall back FROM. Kept
as a superseded note so the "relax gates on empty days" pattern is not reintroduced — the
tournament already sees the broad pool.
