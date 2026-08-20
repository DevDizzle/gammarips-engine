Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-12-enrich-topN-thinking-cap.md; docs/DECISIONS/2026-08-17-llm-cost-accounting-fix.md
Date: 2026-07-17

# Enrichment cost fix (2026-06-12) — top-N BULLISH + thinking_budget=0

The ~$38/day Gemini bill was NOT the tournament (~$1) — it was `enrichment-trigger`
grounding all ~344 UOA names with **uncapped thinking** (~2M output tokens/day). The trace
logger HID it by dropping `thoughts_token_count`, so cost must be read from Cloud
Monitoring `token_count`, NOT the trace table.

Fix: enrichment now edge-ranks to the **top `ENRICH_TOP_N` (default 50) BULLISH** names
(`_edge_select_top_n`, confirmed |delta| lever, leakage-safe) and grounds only those with
**`thinking_budget=0`**. This moves the [[bullish-only-hard-gate]] and the cap UPSTREAM of
the grounded LLM (so the "all directions" [[enrichment-definition]] applies only to the
cheap scan/UOA query — grounding is BULLISH-top-50). The same note recorded a
`TOURNEY_POOL_CAP` raise to 50, but the raise never reached the live service: the live
cap is the code default 12 ([[tourney-pool-cap-edge-rank]]).
`overnight_signals_enriched` shrinks ~344→~50 (raw-scan SEO pages unaffected;
haystack/shadow-tracker depth narrows).

**Amended 2026-08-20.** The Monitoring-only cost rule holds for trace rows BEFORE
2026-08-17 only. The 2026-08-17 fix prices `trace_logger` from the Cloud Billing Catalog
and instruments `signal-judge`, so `cost_usd` is trustworthy from 2026-08-17 onward
([[llm-cost-from-billing-catalog]]).
