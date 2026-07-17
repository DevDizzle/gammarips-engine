Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a
Source: docs/DECISIONS/2026-06-19-market-holiday-standdown.md
Date: 2026-07-17

# Market-holiday stand-down — fail closed on any non-trading day

Cloud Scheduler fires on calendar time and does not know market holidays, so on
Juneteenth 2026 the crons emailed a "today's pick" and simulated a trade on a closed market.
Fix: a fail-closed **market-holiday stand-down** at the head of the two entry-day services
(`signal-notifier`, `forward-paper-trader`), using the authoritative NYSE calendar
(`pandas_market_calendars`). On any weekend or holiday the engine stands down completely —
**no email, no WhatsApp, no tournament, no simulated trade**.

The `signal-notifier` skip path writes a `todays_pick` skip doc
(`skip_reason="market_holiday"`) keyed to `get_previous_trading_day(run_day)` but does NOT
claim an email send, so it cannot suppress the next real trading morning
([[notifier-duplicate-send-guard]]).
