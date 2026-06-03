# 2026-06-03 — Persist sector/industry on signals + webapp internal-linking overhaul

**Status:** IMPLEMENTED + DEPLOYED 2026-06-03 (owner-directed). Engine: `enrichment-trigger` rev 00039 live (source deploy). Webapp: 3 commits on `main`, auto-deployed. `gammarips-review` audited the engine diff → GO (non-gating, no lookahead).
**Services / repos:** `enrichment-trigger` (engine); `gammarips-webapp` (separate Next.js repo, `/home/user/gammarips-webapp`, auto-deploys from `main`).
**Decision owner:** Evan — directed for organic-traffic / SEO (blog had no inbound links; detail pages were orphaned).
**Related:** [[2026-06-03-vix3m-fred-retry-and-carry-forward]] (shipped in the same `enrichment-trigger` working-tree deploy), [[2026-05-09-scanner-sector-detail-endpoint]] (where sector/industry originate).

## Problem

Two SEO gaps, one engine blocker:
1. **The blog was a true orphan.** Zero in-site HTML links pointed to `/blog` (only the XML sitemap + a Mailgun email link). GSC/GA4 (28d) showed **zero** `/blog` impressions or landing sessions — textbook orphan signature.
2. **Signal/report detail pages go orphan the day after their scan.** The `/signals` and `/reports` index lists only render *today's* scan, and `/reports/[date]` had **zero** outbound links (worst dead-end). These pages rank and get clicks (e.g. `/signals/aaoi` 24 impr, `/reports/2026-05-22` 20 impr) but had no internal inlink once a day passed. Also: the detail page only resolved the *latest* scan, so historical (ranking) ticker URLs 404'd.
3. **Same-sector related-signals matching was impossible** because `sector` was never persisted to the Firestore signal doc — even though it's SIC-mapped at scan time and already lives on the raw `overnight_signals` BQ table.

## Decision

### Engine — persist sector/industry (`enrichment-trigger/main.py`)
Purely additive, non-gating metadata passthrough. The value already flows from Polygon → SIC map → raw `overnight_signals` table → `get_signal_tickers()` SELECT; it was being dropped at the enriched-table write and the Firestore write.
- `get_signal_tickers()` SELECT — added `industry` (`sector` was already selected).
- `write_enriched_signals()` row dict — added `sector`/`industry` (BQ parity for cohort analysis).
- Idempotent `ALTER TABLE` — added `sector STRING, industry STRING` to `overnight_signals_enriched`.
- `sync_to_firestore()` `doc_data` — added `sector`/`industry` to `overnight_signals/{scan_date}_{ticker}`.

**Gating safety (review-confirmed GO):** neither field appears in any WHERE / HAVING / ORDER BY / ranking in `enrichment-trigger` or `signal-notifier`. No lookahead (point-in-time, same row as every other feature; not outcome-derived). ALTER is idempotent; columns NULLABLE; NULL-safe reads. Cannot change which signals pass the gates or what the LLM thesis sees (`industry` is never put in a prompt; `sector` was already in the `compute_flow_context` prompt path pre-change).

### Webapp — internal-linking overhaul + sector-ranked related signals (`gammarips-webapp`)
Three commits on `main`:
- `908be8a7` — de-orphan `/blog`: Blog link in footer + header nav; "From the Blog" homepage teaser; "How We Read This Flow" block on signal pages; "See the methodology live → /signals" on blog posts.
- `23515282` — site-wide mesh: `getMostRecentSignalForTicker` fallback so historical ticker pages resolve instead of 404ing; "Recent Signals" section on `/signals`; `/reports/[date]` breadcrumb + "Signals in this report" + prev/next chain + ticker auto-linking in prose (allow-list = that scan's tickers); signal↔report cross-links; shared `Breadcrumbs` (visible + `BreadcrumbList` JSON-LD); Scorecard → header nav; Daily Reports → footer; `/war-room` removed from sitemap (it 301s to `/pricing`); contextual links on `/signals` copy.
- `dadf47d0` — `getRelatedSignals` ranks same-sector siblings to the top of the same-direction pool; `OvernightSignal` gains `sector?`/`industry?`. Degrades gracefully to direction-only on sector-less docs.

## Rollout / behavior

- **No backfill needed.** Related-signals only matches *within a single scan day*, and a day's docs are all rewritten by one enrichment run. The **first enrichment cron after deploy** makes that day fully sector-aware; pre-deploy days stay sector-less and fall back to direction-only (== prior behavior).
- Webapp deployed before/independent of the engine — it tolerates missing `sector`.

## Follow-ups

- **Re-measure ~2–4 weeks:** rerun `scripts/seo/gsc_query.py --dim page` — success = `/blog`, `/signals/*`, `/reports/*` detail pages picking up non-zero impressions (today: absent).
- **Optional upgrade:** the related block titles "More Bullish/Bearish Flow" (accurate; sector is a silent ranking boost). Could surface explicit same-sector grouping once sector coverage on live docs is confirmed dense.
- **Verify after next cron:** Firestore `overnight_signals/{date}_{ticker}` carries non-null `sector`/`industry`.

## Notes

The engine change shipped in the same `enrichment-trigger` source deploy as the parallel FRED retry/carry-forward work (both review-cleared GO, no interaction). At time of writing the engine working tree is **uncommitted** — the sector hunks and the FRED work need committing to capture what rev 00039 is running.
