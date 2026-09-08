# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## START HERE (2026-09-01)
**FIRST TASK — finish the secret migration.** Webapp PR #32 is MERGED (yaml declares
9 secrets as Secret Manager refs) but the Firebase Console still holds plain values and
**the console wins**, so nothing has changed yet. Safe resting state, not broken. Owner
runs the 2 commands in `~/workspace/GAMMARIPS-SECRET-MIGRATION.txt`. The sandbox
classifier blocks the agent from doing it. All 9 hash-verified identical first.

**OPEN OWNER QUESTION (blocks the last 3):** `GEMINI_API_KEY`, `GOOGLE_API_KEY` (same
key as each other) and `FMP_API_KEY` hold DIFFERENT values in the console than in Secret
Manager. enrichment-trigger, gammarips-mcp, overnight-report-generator and
signal-notifier all read them at `latest`, so syncing changes what four production
services get. Ask which is authoritative, then migrate.

**POSITIONING — DECIDED 2026-09-01, do not re-open.** AI-engineer content goes on the
owner's PERSONAL X + LinkedIn, NOT on @gammarips, and he scoped personal branding as
outside this project. Do not retool x-poster for it ([[x-poster-is-not-acquisition]]).
The "side income" framing was rejected as an implied-return claim; the agreed line is
"a hard live domain for your agent, with next-day ground truth".

NO-OWNER QUEUE (in order, each shippable alone):
1. Creator pitch + Stripe promo-code design (free Pro + rev share) ->
   `docs/GTM-CREATOR-PROGRAM.md`, short.
2. Reddit follow-ups (r/ClaudeAI, r/mcp, r/algotrading) + dev.to syndication ->
   `~/workspace/GAMMARIPS-POSTS.txt`. Owner posts.
3. Guide B2 ("How to trade options with Claude Code") + `scripts/blog/publish_guide.py`.
   Not published without `/ship`.

## Active workstream — the 08-22 go plan (subs before 10-05)
Decision `docs/DECISIONS/2026-08-22-go-plan-outbound-plugin-founding-offer.md`. Owner
steps `~/workspace/GAMMARIPS-HN-LAUNCH.txt` (the old GO-RUNSHEET is archived; its
remaining items 7-10 + Q1/Q3 were folded in). Memory [[go-plan-2026-08-22]].
- DONE: plugin PR #3 (08-28), founding offer PR #29 live (08-28), GA4 attribution fixed
  and Realtime-verified (08-31), relaunch email sent (08-31, produced zero, list closed),
  placements 6a/6b opened 09-01 (awesome-mcp-servers #13396, awesome-claude-skills #1800).
- REMAINING: **Show HN** (unblocked, text corrected, window Wed 09-02 / Thu 09-03 8-10am
  ET, steps `~/workspace/GAMMARIPS-HN-LAUNCH.txt`), 6c awesome-claude-code issue form
  (human only), plugin directory form, Connectors Directory.
- Measure by referral sessions + human MCP initializes (claude-code / cursor / codex UAs,
  non-cloud IPs), NEVER link count. Still zero external clients ever as of 09-01: every
  agent-client IP is owner infra (`gr-trader-vm` 8.234.242.149) or a Claude Code session.
- OAuth AS + `/pro` LIVE since 08-19 ([[oauth-as-built-2026-08-19]]). GitGuardian
  36370105 false positive: mark it.

## Owner queue
- Secret migration (2 commands) + the 3-key authoritative-value answer. See START HERE.
- **Merge webapp PR #34** — one-line `ai-catalog.json` 4.4.0 -> 4.5.0 sync. Merging deploys.
- **Cancel the 08-28 test sub before Sep 4 18:26 UTC** — real card, converts to $39.
- Show HN + the 6c issue form: `~/workspace/GAMMARIPS-HN-LAUNCH.txt`.
- Run-sheet items 7-10 and Q1 (Team/Enterprise claude.ai org) / Q3 — all now in
  `~/workspace/GAMMARIPS-HN-LAUNCH.txt`.
- Revoke + regenerate the 08-06 test MCP key (was pasted in chat).
- Record the 08-17 zero-trials gate disposition (Q3, [[mcp-monetization-killswitch]]).
  The 10-05 gate stands.
- **win-tracker redeploy (`d44a272`) + x-poster / blog-generator redeploy** for the
  08-25 cohort pin. The 08-31 newsletter + rubric fix rides on the same redeploy
  (`libs/gammarips_content` is vendored into both at deploy time).
- Organic Social halved (67→35 sessions/28d); x-poster lane needs its own look.
- Small: restore `blog_posts/building-options-flow-pipeline-ai-agents` to `published`;
  lx6bb stray docs call; Cursor listing v4; X pins/bio; Stripe MCP.

## Watch / dated checkpoints
- **Next NYSE holiday 2026-11-26:** confirm neither `forward-paper-trader-label-pool`
  (17:00 ET that day) nor `dbt-daily-build` (06:30 ET 11-27) pages. Both holiday-noise
  fixes deployed 09-08 (dbt-runner-00011, trader-00054). [[market-holiday-cron-noise-two-chains]]
- **Confirm `liquidity_rank`/`liquidity_score`/`listed_strikes` are non-NULL on a recent
  scan and the log says "liquid universe top-100".** They were NULL on 100/100 rows on
  08-25 (`_score_ticker` rebuilt the dict), making the enrichment liquid gate inoperative;
  pool was still correct. Fix `312e970` — check the deployed scanner rev first, the repo
  notes disagree on whether it shipped. Rollback = `LIQUID_UNIVERSE`/`ENRICH_LIQUID_ONLY`=false.
- Owner's 08-13 trial conversion: `invoice.paid` + `proUntil` refresh, unconfirmed.
- ~08-27 threshold re-fit: confirm the 08-19 `pool_liquidity_snapshot` closes it.
- Mid-Aug ITM check (needs ≥200 expired post-06-12-era rows).

## Open engineering
- 🔴 Deploy the LLM cost-accounting fix `a2fb621` (signal-judge real change, then
  enrichment-trigger + overnight-report-generator redeploy). Verify per
  `docs/DECISIONS/2026-08-17-llm-cost-accounting-fix.md`.
- 🔴 No spread/depth measurement exists (Polygon NBBO entitlement, owner $ call).
- VIX as-of mismatch FIXED `6a799fd`, **not deployed**. Residual: `get_regime_context`'s
  own `lag_note` still does not mention the FRED publication difference (gammarips-mcp).
- FALLBACK picks bypass the liquidity floor (`POLICY_GATE_FALLBACK` takes `df.iloc[0]`).
- `relaunch_email.py` mails Mailgun-suppressed addresses (14 of 30 failures on the 08-31
  send). Fix before any future send. [[dormant-list-is-dead]]
- Least-privilege service accounts: 12/16 Cloud Run services run as the default compute
  SA with `roles/editor`. Plan + order in [[least-privilege-service-accounts-plan]].
- `content-blast-mon-0530` PAUSED since the last real blast 2026-07-05. Do not unpause
  until x-poster + blog-generator are redeployed with the fixed prompt.
- P1 live 10:00 anchor pass — ACCEPTED, not built, owner $ (Polygon cost). Sized 08-31:
  only 31.7% of name-days have a real print at 10:00-10:04, so every opportunity sample
  is liquidity-selected. [[entry-mark-is-a-delayed-day-close]]
- Audit snapshot `day.*` readers and `next_url` pagination; x-poster IAM audit.
- Smaller: `iv_rank_entry` view exclusion; earnings-rail stamp (GAP-014); UNDATABLE
  split; substrate rows (41 delta-0 ITM, 7 NO_BARS); service-auth hardening; webapp
  old-MCP-host refs + 3 tsc errors; blog non-blocking pair; `gammarips-eval` config.

## Live posture
- LIQUID-UNIVERSE FUNNEL LIVE 2026-08-24 (`docs/DECISIONS/2026-08-24-liquid-universe-funnel.md`):
  100 most liquid names, not movers; $500K UOA floor gone. Ships on FILLS (no-fill 40.5%
  -> 6.1%), NEVER on edge — that framing is a forbidden claim. Cohort 08-25. Revs
  scanner-00016-rs5 / enrichment-00050-q54 / notifier-00064-prb.
- Selection research CLOSED (both 08-22 studies: pool = matched random). The one
  owner-approved exception RAN 08-31 and returned null (p=0.923, 0/12 specs); exception
  spent. `FINDINGS_LEDGER.md` §2026-08-31. NEVER re-open. [[selection-research-closed]]
- V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + wiki `REGISTRY.md` + `CHEAT-SHEET.md`.
  Cohort start: `LIVE_COHORT_START_DATE` in `signal-notifier/main.py` (never hardcode).
- Owner trades LIVE (Robinhood since 07-09). Daily crons run; MCP paywall ENFORCE.
- Health: operator digest 07:15 ET weekdays; SEO auth via the `seo-auth` skill.
