Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-08-17-llm-cost-accounting-fix.md
Date: 2026-08-17

# LLM cost is priced from the Billing Catalog; cost_usd is trustworthy from 2026-08-17

`libs/trace_logger/pricing.py` prices from the **Cloud Billing Catalog API** (the rate
card that actually bills), with the re-verify command in its docstring. An unknown model
logs **NULL, never a guess**, and prefix matching takes the longest match. `signal-judge`
is traced since the same fix (one row per LLM attempt, thinking tokens folded into
`output_tokens`). The measured tournament cost is **~$0.25 per run-day** median.

The reason this note exists: before 2026-08-17 the trace table priced Flash ~26x low from
a docs page, so 30 days of enrichment logged $0.216 against a real ~$5.59: a cost column
that reconciled perfectly with itself and was wrong by an order of magnitude, the exact
failure class the doctrine warns about. **Read any `llm_traces_v1.cost_usd` row before
2026-08-17 as unreliable**; recompute from `input_tokens`/`output_tokens` (always
correct) or read Cloud Monitoring `token_count`
([[enrichment-cost-fix-topn-thinking-cap]] records the pre-fix rule,
[[eval-system-monitoring-only]] the consumer-side caveat). Historical rows are left as
written; a recompute is an open owner call.
