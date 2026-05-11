# 2026-05-09 — Report wiring fix + 5/8 V5.4 backfill (UHS → URI)

## Decision

Three coupled changes landed on 2026-05-09 to ensure V5.4 actually consumes
the literature-grounded report on Monday 2026-05-11's first live cron, and to
replace the lingering V5.3 pick on the public surface.

1. **Cron re-sequence:** `overnight-report-generator-trigger` moved from
   `15 8 * * 1-5` (08:15 ET) to `0 7 * * 1-5` (07:00 ET) via
   `gcloud scheduler jobs update http`. New ordering: 05:30 enrichment-trigger
   → 07:00 report-generator → 07:30 signal-notifier (V5.4 ranker call).
   Previously the report ran 45 min AFTER the pick, so V5.4 was reading empty
   `report_md` by structural design.
2. **Dual-write report-generator:** `daily_reports/{report_date}` AND
   `daily_reports/{underlying_scan_date}` are now both written with identical
   content. Mirrors the `todays_pick` dual-write pattern (memo
   2026-04-28). Resolves the key mismatch where signal-notifier reads
   `daily_reports/{scan_date}` (`signal-notifier/main.py:556`) but the
   generator wrote under `report_date` only.
3. **5/8 backfill:** ran V5.4 ranker (signal-ranker /rank, dry_run=false)
   against scan_date 2026-05-07. V5.3's UHS BEARISH pick was replaced by
   V5.4's URI BULLISH pick (HIGH confidence, runner-up TFC). Both
   `todays_pick/2026-05-07` and `todays_pick/2026-05-08` rewritten with the
   V5.4 doc, including `v5_4_backfill: True` and `v5_4_run_id:
   v5_4_2026-05-07_2ba60c17` for audit trail.

## Why

- **V5.4 promotion (2026-05-08) was incomplete in plumbing.** The spec
  assumed the Picker received `report_md`, but the cron sequencing + key
  mismatch meant the Picker was running with empty report_md and `regime_alignment`
  leaning neutral by default (`signal-notifier/main.py:552`). The
  literature-grounded `report_v2` work earlier today would have been wasted
  effort without these two changes.
- **The lingering UHS pick on the public surface** showed a V5.3
  `policy_version` even though V5.3 was retired. Replacing with a V5.4 pick
  matches what would have actually happened at 07:30 ET Friday if V5.4 had
  been fully wired.

## Lookahead / fidelity

- Report v2 backfill at scan_date=2026-05-07 was generated at 14:23 UTC on
  2026-05-09 from BQ rows timestamped on or before 5/7 close. No
  forward-looking data leaked into the report payload.
- `signal_ranker_runs` row written with `run_id=v5_4_2026-05-07_2ba60c17`,
  `created_at=2026-05-09 14:44:38` (post-hoc). The run itself only consumed
  scan_date=5/7 enriched candidates + the freshly-generated 5/7 report +
  empty ledger summary (truncated post-V5.4-promotion).
- VIX values on the URI pick doc (`vix3m_at_enrich=20.35`,
  `vix_now_at_decision=17.08`) carried forward from the original V5.3 doc
  since these were 5/7-close values applied at the original 7:30 ET Friday
  decision moment.

## V5.4 vs V5.3 on 2026-05-07

| Field | V5.3 | V5.4 |
|---|---|---|
| Ticker | UHS | URI |
| Direction | BEARISH | BULLISH |
| Strike | 180 | 880 |
| Mid | $10.25 | $98.52 |
| DTE | 7 | 28 |
| V/OI | 3.48 | 5.0 |
| OTM% | 5.5% | 6.8% |
| Confidence | — | HIGH |
| Runner-up | — | TFC |

The V5.4 Picker explicitly cited the report's "infrastructure names
delivering fundamental beats" framing — first observed evidence that report
v2's structured fields are materially driving Picker reasoning.

## Audit

`gammarips-review` ran a supplementary audit on the dual-write + cron change
mid-session: PASS, with one MEDIUM (idempotency hole — backfill could
silently leave the scan-key doc unwritten if `report_date` already existed).
Fixed in the same session: idempotency check now requires both keys to exist
before skipping. Re-deployed to land the fix.

## Side effect — DRY_RUN flipped on signal-ranker

`signal-ranker` deployed env was `DRY_RUN=true` (held over from initial
promotion). Updated to `DRY_RUN=false` so the backfill (and Monday's first
live cron) writes the row to `signal_ranker_runs` for cohort attribution.
This is the going-forward state, not a backfill-specific change.

## Out of scope (carried forward)

- Webapp `/reports/{date}` page renders both keys identically; no UI change
  needed.
- Observability gap (low-severity gammarips-review finding): no alert if
  signal-notifier reads empty `report_md` on a weekday morning.
  Recommendation: add a log-based metric on the warn line at
  `signal-notifier/main.py:569`. Not blocking.
- The 72-entry `_SIC_TO_SECTOR` dict in scanner still falls back to "Other"
  for SICs outside its mapping — separate scanner sector-fix decision note
  on the same date.

## Files

- `overnight-report-generator/main.py` — dual-write + idempotency fix.
- Cron config: `overnight-report-generator-trigger` schedule.
- Cloud Run env: `signal-ranker` `DRY_RUN=false`.
- Firestore: `daily_reports/{2026-05-07,2026-05-08}` (both v2),
  `todays_pick/{2026-05-07,2026-05-08}` (V5.4 URI).
- BQ: `signal_ranker_runs` row `v5_4_2026-05-07_2ba60c17`.
- `docs/DECISIONS/2026-05-09-report-wiring-fix-and-5-8-backfill.md` — this note.
