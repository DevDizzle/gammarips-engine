Status: retired
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md
Date: 2026-07-17

# V5.4 promoted to canonical (2026-05-08) — retired era marker

On 2026-05-08 the operator promoted V5.4 direct-to-product (no parallel proving period),
retired V5.3 across every surface, and truncated `forward_paper_ledger` for a clean cohort.
The rationale was product-story: V5.4's lit-anchored 60/25/15 weighting + multi-input Picker
beat V5.3's deterministic 4-key SQL `ORDER BY`, and the paid funnel needs ONE pick to market.

Retired era marker: V5.4 itself was later collapsed to a single judge (V6), then the bracket
tournament (V7), so "V5.4 is the product" is history. Cohort/version lineage is in
[[ledger-cohort-version-labels]]; the cohort-reset-on-promotion habit is
[[cohort-reset-on-filter-change]].
