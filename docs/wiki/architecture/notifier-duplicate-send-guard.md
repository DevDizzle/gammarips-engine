Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-11-notifier-duplicate-send-guard.md; docs/DECISIONS/2026-06-22-dedup-claim-rekey-runday.md
Date: 2026-07-17

# Pick-email duplicate-send guard — transactional claim keyed on the ET run-day

`signal-notifier` guards against duplicate pick sends with a transactional Firestore claim
(`email_sends/{id}`) plus a 600s deadline (the original double-send was a Scheduler retry
firing the email twice). The claim key was **re-keyed from `scan_date` to the ET RUN-DAY**
after a holiday collision: across a market holiday the same `scan_date` is the "previous
trading day" for two mornings, so a stale Friday (Juneteenth) claim on `scan_date=2026-06-18`
suppressed the legitimate Monday send. The market-holiday stand-down
([[market-holiday-standdown]]) now stands down WITHOUT claiming on closed-market mornings, and
run-day keying closes the latent gap.

Operational gotcha: to force a resend, delete the claim doc for TODAY's ET run-day. Pairs with
the dual-write of `todays_pick` under both `{scan_date}` and `{entry_day}` doc ids so
downstream readers (x-poster) get "today's pick" without calendar math.
