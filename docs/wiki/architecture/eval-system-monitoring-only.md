Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-09-eval-system-v1.md
Date: 2026-07-17

# The LLM eval system is monitoring-first, non-gating

The `gammarips-eval` service (and the trace-logging it consumes) is **monitoring-only and
never gates** a pick, a report, or a deploy. It exists because the production LLM services
(enrichment grounding, the report generator, the tournament) had no standing measurement of
prompt/response/token-cost/latency; the eval layer logs and scores that output but does not
sit in any decision path.

Consequence: a bad eval score is a signal to investigate, not an automatic block. Nothing
gates a deploy (`gammarips-review` is optional and owner-invoked since 2026-08-19). See
`docs/EVAL-SYSTEM.md` for the current design. Cost caveat: `llm_traces_v1.cost_usd` is
trustworthy only for rows from 2026-08-17 onward. For earlier rows read Cloud Monitoring
`token_count` instead ([[llm-cost-from-billing-catalog]],
[[enrichment-cost-fix-topn-thinking-cap]]).
