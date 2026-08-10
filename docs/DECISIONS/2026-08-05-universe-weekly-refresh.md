# 2026-08-05 — Scan universe: one-time regeneration + weekly automated refresh

**Status:** refresh executed 2026-08-05 (owner go); weekly automation deployed same day
(`overnight-scanner` rev `00015-t78`, scheduler `refresh-universe-weekly` Sun 08:00 ET,
first fire 2026-08-09). Smoke test: service dry-run independently re-derived the exact
3,547-name set uploaded manually (0 added / 0 removed / 0 of 5,313 probes errored).
**Owner:** Evan (go on both, 2026-08-05).

## Incident during rollout (contained, hotfixed)

The first deployed revision (`00014-clw`) echoed the `POLYGON_API_KEY` in an error
response: the Secret Manager mount delivers the key with a trailing newline, `requests`
rejected it as an HTTP header value, and `requests.InvalidHeader` subclasses `ValueError`
so it took the guard-abort branch that surfaces error text. Cloud Run request logs prove
the only caller in the exposure window (~9 min) was our own smoke test from the
workstation IP — no third-party access. Hotfix in `00015-t78`: key stripped before use,
and the unauthenticated service now returns generic error bodies on both routes (details
go to logs only; only exact-`ValueError` guard messages are surfaced). The key does sit
in one Cloud Run log line + the session transcript, which raises the urgency of the
already-pending 07-06 rotation (owner queue).

## What changed

1. **One-time regeneration.** `gs://profit-scout-data/overnight-universe.txt` had been a
   hand-maintained static list, last modified **2026-02-13** with no regenerator — every
   listing after that date (SPCX case, GAP-013) was structurally invisible to the scanner
   (`overnight_scanner.py` membership check). Regenerated 2026-08-05 to **3,547
   point-verified active optionable US common stocks** (was 5,230 nominal, of which ~1,700
   had no listed options and ~80 no longer exist). Old file backed up:
   `universe-backups/overnight-universe-2026-02-13.txt`. Evidence + defect adjudication:
   `docs/research_reports/FINDINGS_LEDGER.md` §2026-08-05.
2. **Universe definition (unchanged in spirit, now explicit):** active Polygon `type=CS`
   common stocks (no ETFs, no ADRs — matches the original hand-curated design) with ≥1
   listed call expiring inside 75 days. Widening to ADRs/ETFs is a **product decision**,
   not a refresh; it would change pool composition and enrichment assumptions.
3. **Weekly automation:** `POST /refresh_universe` on `overnight-scanner` (module
   `src/enrichment/core/pipelines/universe_refresh.py`), Cloud Scheduler
   `refresh-universe-weekly`, **Sundays 08:00 ET** — slot pinned deliberately: refresh
   (15 req/s) + scan (20 req/s) must never overlap the Polygon plan cap. Moving the job
   into any scan/enrichment window requires redoing that math. Service + gunicorn
   timeouts raised 540→1200s (run is ~9 min). Manual CLI:
   `scripts/universe/refresh_universe.py` (same module).

## Safety guards (gammarips-review 2026-08-05: PASS WITH CONDITIONS, all landed)

- Upload happens only at the very end; any failure (guard, timeout, crash) leaves the
  live file untouched. Backup precedes every overwrite.
- Floor 3,000 names; shrink >15% aborts (`allow_shrink` override); growth >15% aborts
  (`allow_growth` override) — growth guard exists because probe errors fail OPEN and a
  degraded contracts endpoint would otherwise silently balloon the universe.
- Probe error budget: >3% fail-open probes aborts the write (silent-corruption guard).
- Generation-pinned compare-and-swap (`if_generation_match` + `source_generation`):
  concurrent runs lose with a 412 instead of clobbering.
- Removals are point-verified (never removed on bulk-walk evidence): Polygon's
  `next_url` cursor pagination provably skips rows — memory
  `polygon-next-url-cursor-skips-rows`.

## Research implication

**2026-08-05 is a pool-composition era boundary.** All history before it was drawn from
a universe frozen at 2026-02-13 (aging coverage, no post-Feb listings); after it, the
universe tracks reality weekly. Era-split analyses must treat the boundary accordingly.
