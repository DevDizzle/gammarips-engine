Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md
Date: 2026-08-07

# Polygon's option snapshot never returns a zero-volume day bar

Polygon `v3/snapshot/options/{underlying}/{contract}` **never** serves a zero-volume
`day` bar. When a contract has not printed yet today it returns the **prior session's**
bar (yesterday's non-zero total, with `day.last_updated` dated yesterday). Verified over
49,285 `pool_liquidity_snapshot` reads: `day.volume` is never 0 and never NULL, and ~44%
of the pool carries a stale bar at the 09:45-10:00 ET read.

Consequence: `day.volume` alone can never mean "no prints today", so a floor written
against it silently never fires. This is exactly how the early-print floor was a
structural no-op for its whole first cohort (2026-07-29 → 2026-08-07). Always read
`day.last_updated`, compare its ET date to the read date, and treat an earlier date as a
known zero ([[live-oi-floor]] does this now).

Two implementation traps: (1) guard the early-session window, because pre-open and for
~20 min after the open on the delayed plan EVERY bar is legitimately the prior session's
(`PRINT_VALID_AFTER_ET_MIN` exists for this); (2) keep known-zero and UNKNOWN distinct,
because a fetch failure must stay `None`/fail-open or a vendor outage becomes a mass
drop. Same
vendor-returns-something-plausible family as the `next_url` pagination skip.
