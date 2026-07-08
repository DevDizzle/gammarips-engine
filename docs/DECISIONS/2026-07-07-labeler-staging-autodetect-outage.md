# 2026-07-07 — Labeler staging autodetect outage (07-02→07-06) and fix

## Status
Fixed 2026-07-07 (`forward-paper-trader/main.py:_write_shadow_records` step 2)
and RECOVERED: scans 2026-07-01 (50 labeled, 8W/37L) and 2026-07-02
(50 labeled, 22W/26L) re-run locally through the fixed path; substrate current
again. Incremental gammarips-review: SHIP.

## What happened
The daily `/label_enriched_pool` cron failed every evening from 2026-07-02
through 2026-07-06 with:

```
400 Provided Schema does not match Table ..._stg_enriched_option_outcomes_...
Field recommended_spread_pct has changed type from FLOAT to STRING
```

`enriched_option_outcomes` silently stalled at scan 2026-06-30 — the paid
substrate's labels stopped accruing for four scan days (the failure DID
return 500s to the cron per must-fix #3a, but nobody was watching the pager).

## Root cause — the 2026-07-02 landmine class, second location
This is the same autodetect-mistypes-all-NULL-columns bug that broke
enrichment on 2026-07-02 (`2026-07-02` decision / `3a04bee`), recurring in
the OTHER staged-write path. The atomic shadow writer (2026-07-01) created
its staging table correctly (`CREATE TABLE LIKE` the target → FLOAT), but the
load used `autodetect=True` + `ALLOW_FIELD_ADDITION`. When the 07-02
enrichment fix made `recommended_spread_pct` properly all-NULL, every staged
JSONL load carried only `null`s for that field — BigQuery autodetect infers
an all-null field as STRING, proposed a FLOAT→STRING relaxation against the
typed staging table, and the load 500'd. The two fixes were siblings: the
07-02 fix removed autodetect from enrichment's staging load; this one removes
it from the labeler's.

## Fix
`_write_shadow_records` step 2 now:
1. Diffs the row dicts' keys against the staging schema (which is LIKE-cloned
   from the target, so existing columns keep live types).
2. For genuinely NEW keys, `ALTER TABLE ADD COLUMN` on STAGING with the type
   derived from the PYTHON values (bool→BOOL before int→INT64 — bool is an
   int subclass — float→FLOAT64, else STRING). Deterministic typing from code
   we control, not BQ inference over serialized JSON.
3. Loads with `schema=<staging schema>` explicitly. No autodetect, no
   ALLOW_FIELD_ADDITION.

All atomicity guarantees unchanged (staging-only until the verified
transactional swap; failure = loud stall, target untouched). Applies to all
three `_write_shadow_records` callers (enriched outcomes, topscore shadow,
shadow intraday).

## Rule (now enforced at both known locations)
**NEVER autodetect on a staged load, anywhere.** An all-NULL column — which
`recommended_spread_pct` permanently is on this data plan — autodetects to
STRING and poisons the load. If a third staged-write path is ever added, it
inherits this rule.

## Watch item
The evening cron will label scan 2026-07-06 tonight (17:00 ET) — it needs the
FIXED code deployed on forward-paper-trader before then, or one more manual
re-run tomorrow.
