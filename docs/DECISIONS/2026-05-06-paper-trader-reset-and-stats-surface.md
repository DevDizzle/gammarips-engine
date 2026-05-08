# 2026-05-06 — Paper-trader cohort reset + public live-stats surface

## Decision
Truncate `forward_paper_ledger` and start a fresh cohort tagged from `2026-05-07` forward. Surface public live-stats (trades, ROI, win rate, total invested) at `cohort_stats/current` in Firestore so the webapp can render a social-proof panel above the today's-pick card visible to all users (including unauthenticated). Add deep-links from the operator email and WhatsApp signal to `https://gammarips.com/signals/{TICKER}` so subscribers can reach the rationale page in one click.

## Why now
Same day as the V5.3 lit-audit deploys (earnings exclusion, spread 10→8%, moneyness 15→10%). The cohort selection materially changed; mixing pre-/post-audit trades in one statistical pool would muddy any future EV reading. Keeping the pre-audit 562 closed trades as a "baseline" was considered but rejected — they were generated under different filters (no earnings exclusion, looser spread, looser moneyness), so they're apples-to-oranges with the new cohort and the cohort-filter mental overhead exceeds the research value at this scale.

The public stats panel is a deliberate funnel mechanism per `project_email_only_delivery.md` ("paid users get the curated single pick via email + WhatsApp"). Free users see the live track record; if the numbers look good, they convert. Honest reporting is the funnel — no "Building track record" hedge copy on early-stage zeros.

## What changed

### `forward_paper_ledger` (BigQuery)
- 950 rows truncated 2026-05-06 (562 closed trades, scan dates 2026-04-13 through 2026-04-29, all `V5_3_TARGET_80`).
- BigQuery 7-day time travel covers undo if needed.
- Forward rows accumulate from `2026-05-07` (first auto-cron entry day after lit-audit deploys).

### `signal-notifier/main.py`
- New constant: `LIVE_COHORT_START_DATE = "2026-05-07"`.
- New constant: `PUBLIC_WEBAPP_BASE = "https://gammarips.com"`.
- `format_email_html`: today's-pick card is wrapped in an `<a href="{PUBLIC_WEBAPP_BASE}/signals/{TICKER}">` so the entire card is clickable and lands on the per-ticker rationale page. Added explicit "Read the full rationale →" affordance for clarity.
- `format_whatsapp_message`: adds `Why we picked it: {URL}` line so WhatsApp unfurls a preview card.
- New function: `compute_and_write_cohort_stats()` — queries the ledger filtered to the live cohort, writes `cohort_stats/current` Firestore doc. Non-fatal — failures NEVER affect the email path.
- New endpoint: `POST /refresh_stats` — ad-hoc seed / recovery for the stats doc, no email side-effects. Used to seed the empty-state doc immediately post-deploy.
- `run_notifier` calls `compute_and_write_cohort_stats()` once per run, before any pick logic. Stats reflect ledger state, not today's pick decision.

### `cohort_stats/current` (Firestore)
Schema (single doc, single source of truth, all readers consume same):
```json
{
  "cohort_start": "2026-05-07",
  "policy_version": "V5_3_TARGET_80",
  "as_of": <server timestamp>,
  "trades_closed": 0,
  "trades_won": 0,
  "win_rate": 0.0,
  "total_invested_usd": 0.0,
  "total_pl_usd": 0.0,
  "roi_pct": 0.0
}
```

`win_rate`, `roi_pct` ∈ [-∞, +∞] as decimals (multiply by 100 for display percentages). `trades_closed=0` is the empty-state immediately post-truncate.

### Docs
- `CHEAT-SHEET.md` — note about the email link.
- `docs/TRADING-STRATEGY.md` — cohort reset note + stats surface contract.
- `docs/research_reports/INTELLIGENCE_BRIEF.md` — entry deferred (this is operational/marketing, not research signal).
- `docs/EXEC-PLANS/2026-05-06-webapp-stats-and-deeplink-contract.md` — webapp-side handoff spec (separate file).

## Cadence
- Stats write fires once per `run_notifier` invocation = once per day at 09:00 ET (cron) + ad-hoc via `/refresh_stats`.
- `forward_paper_ledger` is written by `forward-paper-trader` post-day-3 evening when trades close.
- Net effect: stats panel updates every morning at 09:00 ET reflecting trades that closed the prior evening.
- If real-time intra-day updates are needed later, add the same `compute_and_write_cohort_stats()` call to `forward-paper-trader` post-ledger-write — gated by `gammarips-review` per CLAUDE.md.

## Validation posture
- Post-deploy seed: `curl -X POST https://signal-notifier-.../refresh_stats` once to write the initial all-zeros doc.
- First trade lands no earlier than 2026-05-07 evening (entry day-1 = 2026-05-07, exit day-3 = 2026-05-11 if no early stop/target). Webapp panel will show 0/0/0/$0 for ~5 trading days.
- After 30 closed trades, park-mode-completion gate trips per `project_finished_definition.md`.

## Files changed
- `signal-notifier/main.py` — cohort + webapp constants, email/whatsapp deep-links, stats writer, /refresh_stats endpoint.
- `CHEAT-SHEET.md` — minor note.
- `docs/TRADING-STRATEGY.md` — cohort + stats surface notes.
- `docs/EXEC-PLANS/2026-05-06-webapp-stats-and-deeplink-contract.md` — Phase 4 handoff (NEW).
- `forward_paper_ledger` (BQ) — truncated.
