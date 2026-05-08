# 2026-05-06 — Move signal-notifier cron from 09:00 ET to 07:30 ET

## Decision
Cloud Scheduler job `signal-notifier-job` cron expression changed from `0 9 * * 1-5` to `30 7 * * 1-5` (timezone unchanged: `America/New_York`). Operator email + WhatsApp push + webapp+MCP `todays_pick` doc + cohort_stats refresh all fire at 07:30 ET on trading days starting 2026-05-07.

`x-poster-signal-0905` (Twitter post) was **not** moved — it stays at 09:05 ET. Twitter is a marketing surface, not a delivery surface; tweet timing optimizes for Twitter audience, not subscriber freshness.

## Why now
The pipeline ran with a 3-hour idle gap between enrichment-trigger finishing (~05:58 ET, 28-min run) and signal-notifier firing (09:00). Closing the gap gives subscribers more pre-market planning time without changing any code path or risking data freshness.

Original 09:00 ET was a conservative buffer left from earlier pipeline iterations. The current pipeline doesn't need it:
- Enrichment-trigger writes `overnight_signals_enriched` by ~06:00 ET; signal-notifier reads from there.
- The earnings-overlap exclusion (deployed earlier today) means we never pick an option through earnings — so there's no concern about late-arriving AMC earnings shifting the right answer between 06:00 and 09:00.
- VIX (FRED) and FMP earnings calendar are both available overnight.
- agent-arena (06:00 cron) and overnight-report-generator (08:15 cron) are NOT in signal-notifier's read path; they're independent.

## What changed
- `gcloud scheduler jobs update http signal-notifier-job --schedule='30 7 * * 1-5'`
- `CHEAT-SHEET.md` updated to 07:30 ET in the routine table.
- `docs/TRADING-STRATEGY.md` "Publication timing" updated.
- `docs/GLOSSARY.md` `signal-notifier` row updated (also reflects current gate values: 5–10% OTM, earnings exclusion).
- Webapp follow-up: `src/app/page.tsx` ProLock description, FAQ copy, hero copy, and `docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md` references to "09:00 ET" — handled in the existing `feat/landing-unified-v5-3-panel` PR (or a follow-up).

## Why not earlier (e.g. 06:30)?
06:30 ET would have given even more lead time but bleeds into "too early to read" for many subscribers. 07:30 splits the difference: well before market open (09:30) and the V5.3 entry (10:00), but post-coffee for most US time zones. East coast subs get 2 hours, West coast subs get pre-5:00 AM — full lead with no part of the audience iced out by sleep.

## Why move x-poster (we didn't)
- Twitter morning audience peaks 09:00–11:00 ET. 09:05 catches it.
- Twitter is a discovery / marketing pulse, not a delivery channel — there's no SLA on freshness.
- Per `docs/TRADING-STRATEGY.md` "Publication timing": delivery surfaces (email / WhatsApp / webapp / MCP) reveal at the same moment. Twitter is not a delivery surface — it's a public-broadcast amplifier. Decoupled timing is correct.
- If later we want Twitter freshness too, change `x-poster-signal-0905` → `x-poster-signal-0735` separately. One-line cron edit.

## Risks
- Subscribers' morning email-check habits: 07:30 ET is borderline early for some. Acceptable; no one complained that 09:00 was too late, but no one will complain that 07:30 is "too early" either — they read it when they wake up either way.
- Pipeline drift: if enrichment-trigger ever takes >90 min, signal-notifier fires before fresh data is ready. Current run is ~28 min, leaving ~62 min buffer. Add monitoring if drift becomes a concern.
- Webapp copy drift: any landing-page text that says "09:00 ET" is now stale. Sweep the webapp repo for these and ship a copy update PR alongside the unified-panel PR. Tracked via the unified-panel feature branch.

## Smoke check
First fire: 2026-05-07 07:30 ET. Verify via:
```bash
gcloud run services logs read signal-notifier --project=profitscout-fida8 --region=us-central1 --limit=20 \
  | grep -E '(Running V5.3|Earnings calendar|cohort_stats|Successfully sent)'
```

Expect lines for: notifier start (07:30:0X), cohort_stats write, earnings-calendar fetch, todays_pick write, email send.
