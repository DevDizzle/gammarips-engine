# 2026-07-01 — Regime feature re-anchored to scan_date (fix the entry-close leak)

Substrate-readiness audit must-fix #2
(`.scratch/substrate_readiness_audit_2026-07-01.md`). Working-tree change only —
NOT deployed, backfill NOT run. Must pass `gammarips-review` before any deploy AND
before the backfill executes.

## Scope
Research substrate ONLY (`enriched_option_outcomes` + its collector + schema). No
change to execution policy, trade selection, or mechanics. `forward_paper_ledger`,
`_write_ledger_records`, `_simulate_contract`, Firestore/`todays_pick`, and the
webapp/live-pick paths are untouched. The live ledger keeps `VIX_at_entry` /
`SPY_trend_state` / `vix_5d_delta_entry` as-is (it records the single pick and
those are documented ledger telemetry — see `docs/DATA-CONTRACTS.md`).

- `forward-paper-trader/main.py` — `run_label_enriched_pool` (compute scan-date
  regime) and `_write_enriched_outcomes` (persist the corrected column groups).
- `scripts/ledger_and_tracking/create_enriched_option_outcomes.py` — schema of
  record + docstrings.
- `scripts/ledger_and_tracking/backfill_regime_scan_date.py` — NEW, unexecuted,
  ready-to-run in-place backfill (review + owner gated).

## Problem (the real leak the adversarial audit caught)
`enriched_option_outcomes` filed `VIX_at_entry` / `SPY_trend_state` /
`vix_5d_delta_entry` under **FEATURES / regime**, but they were computed by
`get_regime_context(entry_day)` = the latest VIX/VIX3M/SPY close **≤ entry_day**.
The label cron runs 17:00 ET on entry_day, so it captures entry_day's OWN 16:00
close. But the V7 trade enters 10:00 and exits 15:45 the **same** entry_day — so
those values are realized **after** the trade closed. A headless agent conditioning
on them **leaks the future**. It was also **non-deterministic**: the daily cron
could catch only scan_date's close (if FRED hadn't published entry_day yet) while
backfill deterministically caught entry_day's close — mixed as-of semantics across
rows, which poisons fits and defeats replay.

## Fix — regime FEATURE is as-of scan_date close; entry-close becomes telemetry
Selection happens at scan-time (overnight into entry_day), so the real
decision-point regime is as-of **scan_date's close** (the prior close).

1. `run_label_enriched_pool` now computes a second regime tuple
   `get_regime_context(target_date)` (target_date == scan_date) alongside the
   existing entry-day tuple, and passes both into `_write_enriched_outcomes`.
2. New FEATURE columns (leakage-safe, SAFE as model inputs), as-of scan_date:
   `vix_at_scan`, `spy_trend_at_scan`, `vix_5d_delta_at_scan`. (`vix3m_at_enrich`
   was already scan-time from the enriched row — unchanged.)
3. The entry-day-close regime is KEPT (no silent data loss) but re-homed to the
   OUTCOME/telemetry group under unambiguous names: `oc_vix_at_close`,
   `oc_spy_trend_at_close`, `oc_vix_5d_delta_at_close`. Benchmarking only.
4. The misleading `*_at_entry` feature columns are dropped from the collector's
   output and from the create-script schema of record; existing rows are migrated
   by the backfill (below).

### Leakage guard
`get_regime_context` filters bars `<= target_ts` internally, so anchoring it to
scan_date **guarantees** the anchor bar ≤ scan_date — the same mechanism as the
technicals window-bound. This also makes cron and backfill agree (scan_date's close
is always published by label time), removing the as-of drift.

## Backfill (NOT run — review + owner gated)
`backfill_regime_scan_date.py` is an in-place, idempotent UPDATE (labels are NOT
re-simulated):
- STEP A: `oc_* = COALESCE(oc_*, <legacy entry-close col>)` table-wide — preserves
  every entry-close value before anything is dropped.
- STEP B: per scan_date, recompute the scan-date regime with the SAME production
  `get_regime_context` (byte-identical to the fixed collector — no re-implementation
  drift) and set the new FEATURE columns. It resets the in-process `_VIX_CACHE`
  per date (the helper caches per Cloud Run invocation; a long-lived loop would
  otherwise freeze the VIX frame to the first date's window).
- STEP C: dropping the legacy `*_at_entry` columns is destructive and left as a
  commented, separately-approved final step (only after STEP A is verified).

Runs in the forward-paper-trader runtime (its `requirements.txt` + `POLYGON_API_KEY`).

## Column grouping after this change (enriched_option_outcomes)
- Regime FEATURES (as-of scan_date close, SAFE): `vix_at_scan`,
  `spy_trend_at_scan`, `vix_5d_delta_at_scan`, `vix3m_at_enrich`.
- Regime TELEMETRY (entry-day close, NEVER a feature): `oc_vix_at_close`,
  `oc_spy_trend_at_close`, `oc_vix_5d_delta_at_close`.
- Legacy (deprecated, migrated then droppable): `VIX_at_entry`, `SPY_trend_state`,
  `vix_5d_delta_entry`.

## Follow-ups
- Not deployed; backfill not run. `gammarips-review` required before the
  `forward-paper-trader` deploy AND before the backfill executes.
- New columns are safe on the live table via must-fix #1's atomic/ADD-COLUMN write
  path (`_write_shadow_records`), already in the working tree.
- Must-fix #4 (features-only view + machine-readable data contract) is where these
  feature-vs-telemetry tags should become BQ column descriptions + a documented
  contract in `docs/DATA-CONTRACTS.md`; still open.

See also: `docs/DECISIONS/2026-06-17-enriched-option-outcomes.md`,
`docs/DECISIONS/2026-07-01-atomic-schema-drift-safe-substrate-write.md`,
`.scratch/substrate_readiness_audit_2026-07-01.md`, memory
`project_agent_data_readiness`, `project_substrate_audit_2026_07_01`.
