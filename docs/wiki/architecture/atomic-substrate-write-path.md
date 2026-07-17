Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-07-01-atomic-schema-drift-safe-substrate-write.md
Date: 2026-07-17

# Substrate writers stage-verify-replace — never delete-then-load

The research-substrate writers (`_write_shadow_records` for `paper_shadow_topscore` /
`paper_shadow_intraday` / `enriched_option_outcomes`, and `write_enriched_signals` for
`overnight_signals_enriched`) must **stage, verify, then atomically replace** — rows are
never deleted before a load has SUCCEEDED.

Why: the old delete-then-load (unguarded `DELETE WHERE scan_date=X`, then a
`WRITE_APPEND` + `ALLOW_FIELD_ADDITION` load) could 500 AFTER the DELETE committed —
a new record-dict key with no column, or a mid-run timeout — leaving that scan_date's rows
deleted with nothing to reload = **silent data loss**. The same non-atomic path caused the
2026-06-10 `overnight_signals_enriched` row-doubling. `ALLOW_FIELD_ADDITION` without
`autodetect=True` is a confirmed `forward_paper_ledger` landmine. Bind staged loads to the
CLONED live schema (`CREATE TABLE LIKE`), never `autodetect` ([[autodetect-outage-class]]).
