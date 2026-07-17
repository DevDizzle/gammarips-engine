Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md; CLAUDE.md "Current policy"
Date: 2026-07-17

# "Enriched" = overnight_score ≥ 4 + directional UOA > $500K (all directions)

`enrichment-trigger` defines the "enriched" pool with exactly two admission criteria:
- **`overnight_score >= 4`** — this is a FLOOR, not a ceiling. EV inverts at `>= 7`, so a
  higher threshold is worse, not better; hold the floor at 4.
- **directional UOA > $500K**.

At this cheap scan/UOA stage the pool is **all directions**; the BULLISH-only narrowing and
the top-N cap happen downstream at the grounded-LLM stage
([[bullish-only-hard-gate]], [[enrichment-cost-fix-topn-thinking-cap]]).

The old spread gate is retired ([[spread-gate-retired]]). This definition writes
`overnight_signals_enriched`; the raw-scan SEO pages are a separate, unaffected surface.
