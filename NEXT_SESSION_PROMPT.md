# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place, never append dated blocks. Hard cap ~100 lines.
> Rules in `CLAUDE.md`.

## START HERE: GammaRips is SHUT DOWN (owner call 2026-10-29)

Decision: `docs/DECISIONS/2026-10-29-shutdown.md`. Inventory, costs, and the delete list:
`docs/SHUTDOWN-2026-10-29.md`. Owner acts: `~/workspace/GAMMARIPS-SHUTDOWN-OWNER-STEPS.txt`.
The pre-shutdown handoff is archived at `docs/archive/NEXT_SESSION_PROMPT-pre-shutdown-2026-10-29.md`.
It is a record, not a queue. Every item in it is dead.

- **Do not resume a job, redeploy a service, or "fix" a stale table.** Stale data is correct now.
- The 2026-10-15 freeze to 2026-12-31 is superseded. No engine work is planned.
- The trader session stopped gr-trader-vm on 10-29 (`gammarips-trader/docs/DECISIONS/2026-10-29-wind-down.md`).

## State (2026-10-29)

- DONE: step 1 inventory, step 2 pause. All 26 scheduler jobs in profitscout-fida8 are PAUSED.
  Config saved: `~/workspace/projects/_index/fida8-scheduler-jobs-enabled-2026-10-29.json`.
- DONE: Stripe measured. 0 active subscriptions, 0 trials. No subscriber note.
- Last data: the 10-29 scan, enrichment, and report. The 10-28 outcome labels.
- Still deployed and idle: 13 GammaRips Cloud Run services, including gammarips-mcp (it serves
  stale data until the delete).

## Owner queue (his acts, details in the owner steps file)

1. Stripe: deactivate the payment link and the promotion code. Archive 6 prices and the product.
   Keep the webhook until the story page ships.
2. Massive: cancel fully.
3. X API tier and FMP plan: check, cancel a paid one. Not measured.
4. Say "go" for step 5. Then remove the `mcp` CNAME in Squarespace DNS after the MCP delete.
5. His calls: profitscout-lx6bb (unused, $3.84 a month), irw-app, the stale fida8 copy of
   evanparra-ai-site, the MCP listings, the GammaRips Grok Bot.

## Step 5, after "go" (this session's act)

Delete the items marked "Delete" in the Step 5 columns of `docs/SHUTDOWN-2026-10-29.md`. Check each
item against DO NOT TOUCH first. Keep: gammarips-webapp, its 14 secrets, Firestore, the BigQuery
datasets, the shared repo `cloud-run-source-deploy`, the shared build buckets, the default compute
service account, evanparra-ai-site, irw-app, tt-staging-evidence, billing_export, the `texttimeline`
AR repo. After the delete, update the shutdown doc and this file.

## Watch

- `profit_scout.llm_traces_v1` drops partitions after 180 days. Remove the expiry if the story
  needs the LLM traces.
- gammarips.com renews 2026-12-02 at Squarespace. The story page needs it.
