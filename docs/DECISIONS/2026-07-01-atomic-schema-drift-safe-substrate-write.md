# 2026-07-01 — Atomic, schema-drift-safe write path for the research substrate

Substrate-readiness audit must-fix #1
(`.scratch/substrate_readiness_audit_2026-07-01.md`). Working-tree change only —
NOT deployed. Must pass `gammarips-review` before any deploy.

## Scope
Research-substrate writers ONLY. No change to execution policy, trade selection,
or mechanics. `forward_paper_ledger`, Firestore, `todays_pick`, and the webapp
paths are untouched.

- `forward-paper-trader/main.py` — `_write_shadow_records` (the shared writer for
  `paper_shadow_topscore`, `paper_shadow_intraday`, and `enriched_option_outcomes`).
- `enrichment-trigger/main.py` — `write_enriched_signals` (the load into
  `overnight_signals_enriched`).

## Problem (the schema-drift landmine, now in the substrate designed to grow features)
Both writers did **delete-then-load**: `DELETE ... WHERE scan_date = X` (not wrapped
in try/except), then a `WRITE_APPEND` load job with `ALLOW_FIELD_ADDITION` and
`autodetect` OFF. Failure mode: the load 500s **after** the DELETE has already
committed — e.g. a new record-dict key with no matching column (the confirmed
`forward_paper_ledger` landmine, `ALLOW_FIELD_ADDITION` without `autodetect=True`),
or a >10-min mid-run timeout — leaving that `scan_date`'s rows deleted with nothing
to reload = silent data loss. The enrichment writer's non-atomic delete-then-load
was also the confirmed origin of the 2026-06-10 `overnight_signals_enriched`
row doubling that propagated into the collector.

## Fix — stage, verify, then atomically replace
Rows are never deleted before a load has SUCCEEDED:

1. `CREATE TABLE <staging> LIKE <target> OPTIONS(expiration_timestamp = +1 day)` —
   clones the live schema/types (and partitioning) so the staged load is typed
   **exactly** as the live table (behavior-preserving); the TTL self-cleans if a
   run dies before the finally-drop.
2. Load the new rows into staging with `autodetect=True` + `ALLOW_FIELD_ADDITION`
   — a genuinely new feature column is ADDED to staging instead of 500-ing.
   `job.result()` raises on failure → the live table is still untouched.
3. Verify `job.output_rows == len(rows)` before touching the live table.
4. Propagate any staging column missing from the target via
   `ALTER TABLE <target> ADD COLUMN IF NOT EXISTS ...` (schema-drift safety on the
   live table; legacy API type names mapped to GoogleSQL DDL types).
5. Atomic replace inside one transaction:
   `BEGIN TRANSACTION; DELETE <target> WHERE scan_date = X; INSERT <target> (cols)
   SELECT cols FROM <staging>; COMMIT TRANSACTION;` — any failure rolls back the
   DELETE, so the original rows always survive.
6. Best-effort `DROP TABLE IF EXISTS <staging>` in a `finally` (the OPTIONS
   expiration is the safety net).

`autodetect` is flipped ON (was OFF/unset) and `ALLOW_FIELD_ADDITION` kept, so a
new field no longer 500s the load.

## Behavior preservation (no new columns)
When the batch introduces no new columns, staging is a pure schema clone loaded
with the live schema's types (identical typing to the old direct-to-target load),
step 4 is a no-op, and the transaction is `DELETE scan_date` + `INSERT` of exactly
the staged rows. Net effect is byte-for-byte the old delete-then-overwrite:
`scan_date` fully replaced, no duplicates, idempotent re-run. No column or
cohort/version metadata (`policy_version`, `labeled_at`, etc.) was removed or
renamed.

## Why staging + transaction, not a partition swap
`enriched_option_outcomes` / `paper_shadow_topscore` / `paper_shadow_intraday`
are DAY-partitioned on **`entry_day`**, not `scan_date` (the idempotency key), and
`overnight_signals_enriched` is unpartitioned — so a `$YYYYMMDD` partition-decorator
`WRITE_TRUNCATE` is not a clean uniform mechanism. Staging + a single-table
transaction is atomic and schema-drift-safe regardless of partitioning.

## Follow-ups
- A full MERGE-based upsert keyed on `(scan_date, ticker, recommended_contract)`
  was considered but is heavier and column-order-fragile; the transactional
  DELETE+INSERT is the surgical version. Revisit MERGE only alongside must-fix #7
  (uniqueness guard) if a stable per-row key is formalized.
- Must-fix #7 (post-load uniqueness assertion on
  `(scan_date, ticker, recommended_contract)` + per-scan_date lock) is separate
  and still open; this change removes the write-path race that produced the dup,
  but does not add the assertion.
- Not deployed. `gammarips-review` (lookahead/leakage/unsafe-write audit) required
  before `forward-paper-trader` or `enrichment-trigger` deploy.

See also: `docs/DECISIONS/2026-06-17-enriched-option-outcomes.md`,
`.scratch/substrate_readiness_audit_2026-07-01.md`, memory
`project_ledger_schema_drift_landmine`.
