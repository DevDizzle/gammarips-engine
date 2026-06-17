# 2026-06-11 — signal-notifier duplicate-send guard

## Symptom
The daily pick email fired **twice** (operator + every paid subscriber got two
copies). Observed on 2026-06-11 for `SMMT BEARISH`; two `Successfully sent email`
bursts ~3 minutes apart in the signal-notifier Cloud Run logs, both requests 200.

## Root cause
Not a code loop. The **whole pipeline ran twice** because Cloud Scheduler retried
a job it believed had timed out:

- `signal-notifier-job` was configured with `attemptDeadline: 180s`, `retryCount: 3`,
  `minBackoffDuration: 30s`.
- `run_notifier()` routinely takes **3+ minutes** — it makes a blocking call to the
  `signal-judge` service (min-instances=0 → cold start) which runs 3 bracket
  tournaments (~39 LLM calls).
- First request overran 180s → Scheduler marked it failed → fired a retry ~30s
  later → the `/` endpoint re-ran the entire pipeline with **no dedup guard** →
  second email + WhatsApp + subscriber fan-out.

Ruled out: dual-write loop, duplicate scheduler jobs, fan-out double-loop.

## Fix (two layers)
1. **Stop the trigger (config):** widened the scheduler attempt deadline so a
   normal run finishes before Scheduler retries.
   ```
   gcloud scheduler jobs update http signal-notifier-job \
     --project=profitscout-fida8 --location=us-central1 --attempt-deadline=600s
   ```
2. **Make double-send impossible (code):** `claim_email_send(scan_date)` in
   `signal-notifier/main.py` — a transactional Firestore claim on
   `email_sends/{scan_date}` taken right before the outbound block. If the claim
   already exists, the run suppresses email + WhatsApp + subscriber fan-out and
   returns success (so Scheduler stops retrying). `todays_pick` is written before
   the claim and its `.set()` is idempotent, so the webapp stays correct on a
   suppressed retry.
   - **Fail-open:** if Firestore raises, the claim returns `True` (send proceeds).
     A rare duplicate is preferable to a Firestore blip silencing the daily pick.
   - Concurrency-safe: overlapping first-run + retry serialize through the
     transaction; exactly one acquires the claim.

## Operator contract changes
- **Forcing a deliberate resend:** a manual re-trigger for a `scan_date` that has
  already sent (e.g. `curl -d '{"target_date":"..."}'` or a backfill) is now
  **suppressed**. To intentionally resend, delete `email_sends/{scan_date}` in
  Firestore first, then re-trigger.
- **Claim-before-send tradeoff:** the claim is committed before `send_email`. If
  the process dies between claiming and a successful send, the retry sees the
  claim taken and suppresses → zero emails that day. This is the intended
  tradeoff: a rare missed pick (already the service's worst-case on every
  fail-closed branch) beats subscriber-facing duplicate spam.

## Scope / non-impact
No change to execution policy, trader mechanics, gates, or ledger schema. New
Firestore collection `email_sends` is internal bookkeeping only — not read by any
downstream surface.

## Audit
`gammarips-review` invoked before deploy (notifier is production, outward-facing).
