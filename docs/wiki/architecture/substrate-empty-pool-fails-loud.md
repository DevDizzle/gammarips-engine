Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-07-01-substrate-integrity-hardening.md
Date: 2026-07-17

# Degraded substrate fails LOUD (empty pool → 500 + freshness monitor)

`run_label_enriched_pool` now returns a NON-2xx (endpoint 500) on a real NYSE trading day
when `pool_size == 0`, `labeled == 0`, OR `wins+losses == 0` — a silent empty/degraded pool
is treated as a failure, not a no-op, plus a freshness monitor. This is the guardrail that
was MISSING when the autodetect labeler outage silently stalled `enriched_option_outcomes`
for four days ([[autodetect-outage-class]]) — the failure did return 500s, but nobody was
watching, so the freshness monitor closes the loop.

Scope: research substrate + collector reliability + input hardening ONLY. The live-pick
path, `_write_ledger_records`, `_simulate_contract`, and `todays_pick` are untouched. Builds
on the atomic staging write path ([[atomic-substrate-write-path]]) and the scan-date regime
fix ([[regime-scan-date-leakage-fix]]). Owner doctrine: eval the DATA, not just the LLM text
([[pipeline-bug-hunt-2026-06-04]]).
