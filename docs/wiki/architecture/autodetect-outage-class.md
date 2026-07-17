Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-07-07-labeler-staging-autodetect-outage.md (folds the 2026-07-02 enrichment outage)
Date: 2026-07-17

# NEVER autodetect on a staged BQ load — the all-NULL-column mistype landmine

BigQuery `autodetect` infers an **all-NULL column as STRING**. When a staged JSONL load
carries only nulls for a FLOAT column (e.g. `recommended_spread_pct`, permanently NULL since
the quote outage — [[spread-gate-retired]]), autodetect proposes a FLOAT→STRING relaxation
that FAILS the load against the real table. This is a whole CLASS of outage, not one bug:
- **2026-07-02** — broke `enrichment-trigger`: every enrichment load failed → 0 enriched →
  **no pick that day**.
- **2026-07-02→07-06** — the "latent sibling" in the labeler: `/label_enriched_pool` failed
  nightly (`recommended_spread_pct changed type FLOAT→STRING`), silently stalling
  `enriched_option_outcomes` (the paid substrate) at scan 2026-06-30 for four days.

Fix and standing rule: staged loads bind to the **cloned live schema** (`CREATE TABLE LIKE`
the target) with `autodetect=False`; never re-enable autodetect on any enrichment / substrate
writer. Fix the whole landmine class, not the instance. Pairs with
[[atomic-substrate-write-path]].
