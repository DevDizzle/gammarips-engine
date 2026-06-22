# 2026-06-22 — Duplicate-send guard re-keyed on ET run-day (holiday collision fix)

## Incident
The daily pick email did not fire the morning of Mon 2026-06-22. The pick itself
(TTWO BULLISH) was selected, written to `todays_pick/{2026-06-18, 2026-06-22}`,
and shown on gammarips.com; the forward-paper-trader was unaffected. Only the
operator email + WhatsApp + paid-subscriber fan-out were silently suppressed.

## Root cause
`signal-notifier`'s duplicate-send guard `claim_email_send()` keyed its Firestore
claim doc (`email_sends/{id}`) on **`scan_date`**. Across a market holiday the
same `scan_date` is the "previous trading day" for two consecutive mornings:

- **Fri 2026-06-19 (Juneteenth):** the notifier cron ran with PRE-holiday-guard
  code (the market-holiday stand-down shipped later that same day), processed
  `scan_date=2026-06-18`, sent the email on a closed market, and wrote claim
  `email_sends/2026-06-18` (claimed_at 2026-06-19 07:31 ET).
- **Mon 2026-06-22:** no scan occurred over the holiday + weekend, so the run
  re-processed the SAME `scan_date=2026-06-18`. The stale Friday claim already
  existed → the guard suppressed the legitimate Monday send.

This was a one-time residue of Friday's pre-guard holiday send. The holiday guard
now stands down (and does NOT claim) on closed-market mornings, so the exact
collision is mostly self-resolving — but the `scan_date` keying left a latent gap
worth closing properly.

## Fix
Re-key the claim doc on the **ET run-day** (`datetime.now(est).date()`) instead of
`scan_date`. The guard's only purpose is "send at most once this morning" — there
is exactly one notifier run per morning, so keying on the wall-clock send-day
dedups same-morning Cloud Scheduler retries (the original 2026-06-11 purpose)
while never colliding across days or holidays. The claim doc body now stores both
`run_day` and `scan_date` for audit. Fail-OPEN behavior unchanged (Firestore raise
→ send). No trading gate, selection, leakage surface, ledger write, or the
market-holiday stand-down path was touched. `gammarips-review`: SHIP.

## Immediate remediation (same morning, pre-10:00 ET entry)
Re-emitted the already-decided TTWO pick from the stored `todays_pick` doc via a
one-shot (`.scratch/resend_2026-06-22.py`) reusing the production `format_email_html`
builder — operator email + 1/1 subscriber fan-out delivered at 09:50 ET. NO
re-run of the randomized tournament (the pick was already public; re-picking could
have changed it), and the dedup claim was not touched.

## Operator note
To force a deliberate resend, delete `email_sends/{TODAY_ET}` (the send-day doc id),
**not** `email_sends/{scan_date}`. Supersedes the operator gotcha in the
2026-06-11 duplicate-send-guard decision.

See also: `docs/DECISIONS/2026-06-11-notifier-duplicate-send-guard.md`,
`docs/DECISIONS/2026-06-19-market-holiday-standdown.md`.
