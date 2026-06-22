# 2026-06-19 — Market-holiday stand-down guard

## Context
Juneteenth (Fri 2026-06-19) is an NYSE holiday. Cloud Scheduler fires on calendar
time and does not know about market holidays, so the daily crons ran anyway:
`signal-notifier` emailed subscribers a "today's pick" recommendation and
`forward-paper-trader` executed on a closed market. Recommending a trade on a day
the market is shut looks unprofessional and pollutes the ledger/surfaces.

The engine already had an authoritative NYSE calendar (`nyse = mcal.get_calendar("NYSE")`,
pandas_market_calendars) used by the `get_*_trading_day` helpers — but nothing
checked whether *today* is a trading day before emailing/trading.

## Decision
Add a fail-closed **market-holiday stand-down** at the head of the two services
that fire on the entry day. On any non-trading day (weekend or holiday, per the
NYSE calendar), the engine stands down: **no email, no WhatsApp, no tournament,
no simulated trade.**

- **signal-notifier** — new `is_trading_day(d)` helper; guard is the first
  statement in `run_notifier`. If `datetime.now(est).date()` is not a trading day,
  write a `todays_pick` skip doc with `skip_reason="market_holiday"` and return
  before the email/WhatsApp/tournament path. The skip doc is keyed to
  `get_previous_trading_day(run_day)` — the SAME `scan_date`/doc id the next real
  trading day's run will use — so that run cleanly overwrites the placeholder
  (and its entry-day mirror) and `getLatestTodaysPick()` (orderBy scan_date desc)
  never surfaces a stale "markets closed" doc that could hide the next real pick.
- **forward-paper-trader** — same `is_trading_day(d)` helper; guard near the top
  of `run_forward_paper_trading`. On a non-trading run day, write ONE skip row via
  the existing `_build_skip_record(target_date, "MARKET_HOLIDAY", ...)` +
  `_write_ledger_records` path (no Polygon/FRED calls, no simulation). `skip_reason`
  is an existing column — no schema change, no `ALLOW_FIELD_ADDITION` landmine.
- **webapp** — `market_holiday` added to the `TodaysPick.skip_reason` union and to
  `SKIP_REASON_COPY`, so the landing card renders a clean "markets closed" state
  instead of a recommendation.

Decision: send NOTHING on holidays (no standing-down email) — the only surface
that changes is the webapp card. (Other skip reasons like regime/earnings still
email a rationale; a known-in-advance holiday is inbox noise, so it's silent.)

## Safety / review
`gammarips-review` PASS (2026-06-19): no leakage (calendar-only gate), fail-closed
correct (half-days correctly counted as sessions; ET timezone correct), doc-keying
overwrites cleanly with no orphan (Juneteenth Fri→Mon walk verified), no schema
drift, idempotent against Scheduler retries (returns 200 before the
`email_sends/{scan_date}` claim; trader DELETE-then-load keyed on scan_date).

## Notes
- Casing is intentionally service-local: `"market_holiday"` in the Firestore doc
  (matches the other notifier-written snake_case reasons the webapp keys on) vs
  `"MARKET_HOLIDAY"` in the ledger (matches the trader's UPPER_SNAKE convention).
- This is a stand-down/availability guard, not a selection or execution-mechanic
  change — the tournament and trader mechanics are untouched.
