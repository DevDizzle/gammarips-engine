Status: retired
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-01-ranker-v2-voi-first.md (superseded by the tournament selection era)
Date: 2026-07-17

# V/OI-first deterministic ranker — retired (the ranker era is over)

On 2026-05-01 the `signal-notifier` LIMIT-1 `ORDER BY` was changed from "biggest directional
UOA dollar-volume wins" to "highest directional V/OI wins" — a deterministic SQL ranker
choosing the daily pick.

Retired: the entire deterministic-ranker era ended when selection became an LLM Scorer→Picker
(V5.4), then a single judge (V6), then the randomized bracket tournament
([[bracket-tournament-selection]]). And V/OI itself was later proven an anti-edge on realized
option PnL ([[voi-ratio-anti-edge]]). Kept as a retired note so V/OI is not reintroduced as a
rank key.
