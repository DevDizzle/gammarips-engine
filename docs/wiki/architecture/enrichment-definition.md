Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md; docs/DECISIONS/2026-08-20-score-floor-accepted-print-floor-25-shipped.md; CLAUDE.md "Current policy"
Date: 2026-07-17

# "Enriched" = overnight_score ≥ 1 + directional UOA > $500K (all directions)

`enrichment-trigger` defines the "enriched" pool with exactly two admission criteria:
- **`overnight_score >= 1`** — the accepted floor (owner call 2026-08-20). The floor is
  cosmetic: the UOA bar, the BULLISH gate, and the top-50 cap do the filtering.
- **directional UOA > $500K**.

**History (the ≥4 floor never ran).** A raise to `>= 4` was decided on 2026-06-05 but
never reached production: the `deploy.sh` env pin has set `MIN_ENRICHMENT_SCORE=1` since
2026-04-20, and the env wins over the code default. The owner accepted the de-facto
floor of 1 on 2026-08-20. The difference is measured cosmetic — removing ≥4 changes the
top-50 pool on 1 of 20 days, 6 slots (`FINDINGS_LEDGER.md` §2026-07-28 (evening) —
tradeability), and
`overnight_score` AUC is ~0.51.

The no-ceiling fact stands: the score floor is a FLOOR, not a ceiling. EV inverts at
`>= 7`, so a higher threshold is worse, not better.

At this cheap scan/UOA stage the pool is **all directions**; the BULLISH-only narrowing and
the top-N cap happen downstream at the grounded-LLM stage
([[bullish-only-hard-gate]], [[enrichment-cost-fix-topn-thinking-cap]]).

The old spread gate is retired ([[spread-gate-retired]]). This definition writes
`overnight_signals_enriched`; the raw-scan SEO pages are a separate, unaffected surface.
