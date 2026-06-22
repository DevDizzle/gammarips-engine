# 2026-06-22 — V7.1 "Tilted GIGO" cohort reset (ledger truncate + policy_version relabel)

## What changed
Owner-directed. The forward paper-trading ledger was **truncated** and a fresh
cohort started under a new label **`policy_version = 'V7_1_TILTED_GIGO'`** (was
`V7_INTRADAY`), tracking from the first momentum-tilt-enriched pick.

- **Execution mechanics: UNCHANGED.** Still the V7 "Get In, Get Out" same-day
  intraday OCO bracket (10:00 ET entry / +40% TP / −30% stop / flat 15:45 ET, no
  trail, no overnight). The ".1 Tilted" denotes the upstream change only: the
  enrichment edge-rank now applies the 60-day momentum soft pre-rank tilt
  (`enrichment-trigger` rev `00045-f89`, deployed 2026-06-19; see
  `docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`). Selection (the bracket
  tournament) and the trader are byte-identical.
- **`LIVE_COHORT_START_DATE` → `2026-06-23`** (first entry of the first pick whose
  pool was enriched AFTER the tilt deploy).

## Why the cohort starts 06-23, not today (TTWO is excluded)
Today's live pick (TTWO BULLISH, scan_date 2026-06-18, entry 2026-06-22) is a
**confirmed pre-tilt pick**. The tilt deployed 2026-06-19; over the Juneteenth +
weekend gap no new scan ran, and this morning's 05:30 ET enrichment **refused to
re-enrich** scan_date 06-18 ("stale, >3 days old, skipping"). So TTWO's pool was
enriched 06-19 morning, before the tilt existed — the live tilt never touched it.
To keep the cohort's attribution clean (its purpose is to measure whether the
tilt earns its keep at N≥15), TTWO is excluded. The 06-23 start-date floor in the
cohort_stats + ledger_trades queries excludes it regardless of its row label.

## Truncate
All 12 pre-reset rows (10 `V7_INTRADAY` + 2 `V6_TOURNAMENT`/DINO) were dumped to
`.scratch/forward_paper_ledger_pre_v7_1_truncate_2026-06-22.json` before
`TRUNCATE TABLE profitscout-fida8.profit_scout.forward_paper_ledger`. TRUNCATE
preserves the table schema (no schema-drift risk — this is a value relabel, not a
new field; see `project_ledger_schema_drift_landmine`).

## Blast radius (relabel `V7_INTRADAY` → `V7_1_TILTED_GIGO`)
5 services carry the label:
- `forward-paper-trader/main.py` — `POLICY_VERSION` constant (stamps ledger rows).
- `signal-notifier/main.py` — `todays_pick` doc field + cohort_stats/ledger_trades
  query filters + the Firestore stat docs + `LIVE_COHORT_START_DATE`.
- `win-tracker/main.py`, `x-poster/app/tools.py`, `blog-generator/app/tools.py` —
  closed-trade read filters (post-trade tracking/social). No V7_1 trade CLOSES
  until ~06-23 evening, so these are non-urgent but redeployed for consistency.

## Note on TTWO's row today
The trader writes TTWO's row at the 16:30 ET trigger. With `forward-paper-trader`
deployed on the new label, that row is `V7_1_TILTED_GIGO`/entry-06-22 but is
EXCLUDED everywhere by the 06-23 floor. Optional tidy-up: delete that single
sub-cohort row so a naive label-only BQ query stays pure.

## Gates
Execution is unchanged + the tilt was already `gammarips-review`-PASS; this is a
relabel + reset, not a new strategy. No leakage surface touched. `gammarips-review`
re-run on the relabel diff. N≥15 revisit lock on the tilt remains.
