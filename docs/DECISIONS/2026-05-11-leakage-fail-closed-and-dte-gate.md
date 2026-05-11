# 2026-05-11 — Date-leakage fail-closed + DTE 7-30 gate at signal-notifier

## Decision

Three coupled fixes landed on 2026-05-11 in response to the morning's VAL
incident — the inaugural live V5.4 pick shipped a `confidence=low` signal
that the system's own leakage detector had already flagged.

1. **overnight-report-generator stamps the underlying-scan_date doc by
   scan_date instead of report_date.** The dual-write at
   `overnight-report-generator/main.py:614-616` previously wrote the same
   entry-day-stamped body under both keys. The doc keyed at
   `daily_reports/{underlying_scan_date}` now has its `title`, `headline`,
   `content`, and `scan_date` field rewritten via simple string replacement
   of `report_date` → `underlying_scan_date`. The public doc at
   `daily_reports/{report_date}` is unchanged.

2. **signal-ranker fail-closes on mass leakage.** New
   `RankResponse.skip` / `RankResponse.skip_reason` fields. When EVERY top-5
   candidate scores 1/1/1 (the prescribed scorer pattern on leakage detection
   per `scorer_v4.md:29`), the Picker is short-circuited and the response is
   returned with `skip=True, skip_reason="mass_leakage"`. `persist_run` still
   writes the audit trail to `signal_ranker_runs` with `picker_chose=False`
   on every row.

3. **signal-notifier adds a hard DTE 7-30 gate.** New constants `DTE_MIN=7`
   and `DTE_MAX=30` in `signal-notifier/main.py`, applied as
   `recommended_dte BETWEEN {DTE_MIN} AND {DTE_MAX}` in the candidate query.
   signal-notifier also now handles `RankResponse.skip=True` by writing
   `todays_pick` with `skip_reason=v5_4_mass_leakage`, sending no email, and
   posting a standby message to WhatsApp.

## Why

**The VAL incident (2026-05-11, run_id `v5_4_2026-05-08_9bb373e3`).** Both
top-5 candidates were scored 1/1/1 with reasoning prefixed `"LEAKAGE: ...
report dated 2026-05-11 ... three days after scan_date 2026-05-08."` The
Scorer behaved correctly per the prompt. The Picker then chose VAL out of
two leakage-flagged candidates because nothing in code prevented it.

Root cause: the 2026-05-09 dual-write fix (DECISIONS memo
`2026-05-09-report-wiring-fix-and-5-8-backfill.md`) wrote the **same body**
to both Firestore keys. The body contains references to `report_date` (entry
day, 2026-05-11). When the Scorer reads the doc fetched by `scan_date`
(2026-05-08), it sees a future-dated reference and correctly trips the
leakage rule from `scorer_v4.md:29`. This was a temporal-contract bug in the
2026-05-09 fix, not in the Scorer.

The DTE gate is a separate but adjacent issue: VAL was a 40-DTE contract.
Both `scorer_v4.md:18` and `picker_v3.md:69` already call DTE 7-30 the
structural sweet spot for the +80%/3-day bracket — but signal-notifier had
no hard DTE filter, so 40-DTE contracts could reach the LLM and survive
soft scoring. The hard band closes that hole.

## How

**Files changed:**
- `overnight-report-generator/main.py` — build `underlying_doc_data` variant
  before second `.set()` call.
- `signal-ranker/app/schemas.py` — `RankResponse.pick/runner_up/justification`
  now default to `""`, `confidence` is `Literal[...] | None = None`,
  new `skip: bool = False` and `skip_reason: str | None = None` fields.
- `signal-ranker/app/agent.py` — mass-leakage detection before Picker,
  short-circuit with `RankResponse(skip=True, skip_reason="mass_leakage")`.
- `signal-ranker/app/tools.py` — `persist_run` accepts
  `picker_output: PickerOutput | None`, writes audit row with empty picker
  fields on the skip path.
- `signal-notifier/main.py` — new `DTE_MIN/DTE_MAX` constants, new
  `recommended_dte BETWEEN` clause, new `v5_4_mass_leakage` skip branch
  after the ranker call.

**Test status:** signal-ranker unit tests (25) pass after edits.

**Deploy ordering (when run):**
1. signal-ranker (publishes new schema) — must precede signal-notifier so
   the new `skip` field is in the response payload before notifier reads it.
2. signal-notifier — picks up DTE gate + skip handling.
3. overnight-report-generator — fixes the future-dated body. Could go first
   but ordering doesn't matter for correctness.

`gammarips-review` audit required before deploy per
`.claude/rules/forward-paper-trader.md` — execution-path code changed.

## What was NOT changed

- `forward-paper-trader/main.py` — untouched. The trader has no signal-quality
  gates per `CLAUDE.md` ground rules.
- The trader's 7-30 DTE knowledge — already implicit in
  `scorer_v4.md:18` and `picker_v3.md:69`. The gate adds enforcement; it
  doesn't change policy.
- The dual-write contract for `todays_pick` — separate pattern, unaffected.

## Forensic record of the bad signal

VAL BULLISH was emitted at 2026-05-11 07:30 ET as the first live V5.4 pick.
Per the policy in `docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`,
the trader still entered at 10:00 ET on 2026-05-11 because the system
shipped a `has_pick=True` doc. Whether the resulting paper trade should be
voided in ledger analysis is a separate decision — defer to operator. The
`signal_ranker_runs` row preserves the leakage-flagged scorer reasoning for
audit.
