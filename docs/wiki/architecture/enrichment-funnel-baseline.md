Status: superseded
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-01-enrichment-funnel-deferred.md
Date: 2026-07-17

# Enrichment funnel baseline (~2,264 raw → ~75/day) — tightening once deferred

EDA on 2026-05-01 measured the V5.3-era funnel: ~2,264 raw `overnight_signals`/day →
**~75/day** after the enrichment-trigger gates (`overnight_score≥1`, `spread≤10%`,
directional UOA>$500K) — much wider than the assumed ~6/day. A proposed tightening to
compress the grounded pool to ~20–30/day for cost was DEFERRED pending 30 closed trades.

Superseded by the real cost fix: enrichment now edge-ranks to the top-50 BULLISH names and
grounds only those with `thinking_budget=0` ([[enrichment-cost-fix-topn-thinking-cap]]), and
the enrichment floor moved from `≥1` to `≥4` ([[enrichment-definition]]). The specific ~75/day
figure is a V5.3-era baseline, not the current funnel width.
