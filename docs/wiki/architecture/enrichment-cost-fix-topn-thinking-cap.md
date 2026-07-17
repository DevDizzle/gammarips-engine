Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-12-enrich-topN-thinking-cap.md
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
cheap scan/UOA query — grounding is BULLISH-top-50). `TOURNEY_POOL_CAP` was raised to 50 so
all grounded-enriched names seed the tournament ([[tourney-pool-cap-edge-rank]]).
`overnight_signals_enriched` shrinks ~344→~50 (raw-scan SEO pages unaffected;
haystack/shadow-tracker depth narrows).
