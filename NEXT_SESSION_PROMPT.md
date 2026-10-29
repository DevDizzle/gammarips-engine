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

## State (2026-10-29, about 14:10 ET): ALL ENGINE STEPS DONE

- Pause, Stripe archive, and the step 5 delete (owner "go") are DONE. Massive and FMP canceled by
  Evan. X API is usage-based. Log: `docs/SHUTDOWN-2026-10-29.md`.
- fida8 now holds: gammarips-webapp, evanparra-ai-site, irw-app (not GammaRips), 18 secrets for the
  webapp, Firestore, buckets, and the BigQuery datasets. 0 scheduler jobs, 0 functions.
- Deleted-item config (no secret values): `~/workspace/projects/_index/fida8-deleted-config-2026-10-29.json`.

## Next: the story page (a gammarips-webapp session)

Brief: `~/workspace/GAMMARIPS-STORY-PAGE-PROMPT.txt`. Owner decisions: real numbers, redirect every
old page, an end-to-end timeline for clients and employers. After it ships: delete the secrets the
site no longer uses (4 are dead now: FMP_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY,
WHATSAPP_GROUP_INVITE_URL), disable the Stripe webhook, and Evan removes mg.gammarips.com.

## Owner queue

1. Remove the `mcp` CNAME in Squarespace DNS (the mapping is deleted).
2. His calls: profitscout-lx6bb (unused, $3.84 a month), irw-app, the stale fida8 copy of
   evanparra-ai-site, the MCP listings, the GammaRips Grok Bot.

## Watch

- `profit_scout.llm_traces_v1` drops partitions after 180 days. Remove the expiry if the story
  needs the LLM traces.
- gammarips.com renews 2026-12-02 at Squarespace. The story page needs it.
