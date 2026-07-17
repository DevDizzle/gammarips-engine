Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-03-sector-persistence-and-webapp-internal-linking.md
Date: 2026-07-17

# Sector/industry persisted on signal docs (SEO internal-linking)

`enrichment-trigger` persists `sector`/`industry` onto the Firestore signal doc (it is
SIC-mapped at scan time and already on the raw `overnight_signals` BQ table,
[[scanner-sector-detail-fetch]]). Without it, same-sector related-signals matching was
impossible and the webapp blog/detail pages were SEO orphans.

The paired webapp overhaul (separate repo, auto-deploys `main`) added blog inbound links,
related-signals blocks, and historical-ticker URL resolution so detail pages don't 404 the
day after their scan. This shipped in the same enrichment-trigger deploy as the VIX3M FRED
retry/carry-forward ([[regime-rail-vix-term]]); owner-directed for organic/SEO traffic,
`gammarips-review` GO (non-gating, no lookahead).
