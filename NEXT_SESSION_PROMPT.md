# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## START HERE (2026-09-15)
**GTM state, measured 09-15:** 0 external subs, 0 external MCP clients, 0 harness stars,
~20 human sessions/15d. Show HN never fired. Trader went LIVE 09-15, first real entry
09-16. **The plan of record is [[public-trace-export-is-the-gtm-asset]]:** daily
redacted `traces/` files in the harness repo (trader `scripts/export_trace.py`, branch
`traces/2026-09` pushed 09-16, timer 17:40 ET weekdays), then Show HN
Tue 09-23 / Wed 09-24 with the rewritten `gammarips-harness/docs/HN-SUBMISSION.txt`
(uncommitted on main). Needs >=3 live days in `traces/` and the branch merged first.

NO-OWNER QUEUE (in order, each shippable alone, all drafts to `~/workspace/GAMMARIPS-POSTS.txt`
unless noted):
1. Reddit posts (r/ClaudeAI, r/mcp, r/algotrading) + dev.to, hooked on `traces/2026-09-15.md`.
2. Managed setup offer copy: $1,000 one-time install of the open-source harness on the
   buyer's VM + broker + written rules, paper-first. Never "I build your bot". For /pricing
   on the HN day; goes through the webapp copywriter + `/ship`.
3. Creator pitch + Stripe promo-code design (free Pro + rev share) -> `docs/GTM-CREATOR-PROGRAM.md`.
4. Guide B2 ("How to trade options with Claude Code") + `scripts/blog/publish_guide.py`.

**Secrets: DONE 09-17.** 12 console rows deleted, rollout succeeded, 12 secret refs live, leaked
Gemini key deleted. Uncommitted follow-on: GOOGLE_API_KEY mounts stripped in enrichment-trigger,
overnight-report-generator (+ main.py) and gammarips-mcp deploy configs; commit with the next
change to each repo. Topic closed. The 08-28 $39 sub is KEPT, never mention it.

**POSITIONING — DECIDED 2026-09-01, do not re-open.** AI-engineer content goes on the
owner's PERSONAL X + LinkedIn, NOT on @gammarips ([[x-poster-is-not-acquisition]]).
The agreed line is "a hard live domain for your agent, with next-day ground truth".

## Active workstream — the 08-22 go plan (subs before 10-05)
Decision `docs/DECISIONS/2026-08-22-go-plan-outbound-plugin-founding-offer.md`. Owner
steps `~/workspace/GAMMARIPS-HN-LAUNCH.txt` (the old GO-RUNSHEET is archived; its
remaining items 7-10 + Q1/Q3 were folded in). Memory [[go-plan-2026-08-22]].
- DONE: plugin PR #3 (08-28), founding offer PR #29 live (08-28), GA4 attribution fixed
  and Realtime-verified (08-31), relaunch email sent (08-31, produced zero, list closed),
  placements 6a/6b opened 09-01 (awesome-mcp-servers #13396, awesome-claude-skills #1800).
- REMAINING: **Show HN** (window moved to 09-23/24, lead is the trace export, text in the
  harness repo; listings steps in `~/workspace/GAMMARIPS-HN-LAUNCH.txt`), 6c
  awesome-claude-code issue form (human only), plugin directory form, Connectors Directory.
- Measure by referral sessions + human MCP initializes (claude-code / cursor / codex UAs,
  non-cloud IPs), NEVER link count. Still zero external clients ever as of 09-01: every
  agent-client IP is owner infra (`gr-trader-vm` 8.234.242.149) or a Claude Code session.
- OAuth AS + `/pro` LIVE since 08-19 ([[oauth-as-built-2026-08-19]]). GitGuardian
  36370105 false positive: mark it.

## Owner queue
- **Merge webapp PR #34** — one-line `ai-catalog.json` 4.4.0 -> 4.5.0 sync. Merging deploys.
- Traces: branch `traces/2026-09` PUSHED 09-16 (09-14/15/16, timer live). PR -> main
  before the HN post, re-merge the morning of. `~/workspace/GAMMARIPS-TRACES.txt`.
- Show HN + the 6c issue form: `~/workspace/GAMMARIPS-HN-LAUNCH.txt`. Posts drafted in
  `~/workspace/GAMMARIPS-POSTS.txt` (personal X/LinkedIn today, Reddit x3 on the HN day).
- **All GTM moved to Grok Bot 09-16** ([[social-strategy-moved-to-grok-bot]]): run the prompt in
  `~/workspace/GROKBOT-SETUP-PROMPT.txt` from a workspace-root session. **x-poster KILLED 09-16:**
  all 9 scheduler jobs paused, service kept for rollback, do not unpause.
- Revoke + regenerate the 08-06 test MCP key (was pasted in chat).
- Run-sheet items 7-10 and Q1 (Team/Enterprise claude.ai org) / Q3 — all now in
  `~/workspace/GAMMARIPS-HN-LAUNCH.txt`.
- Record the 08-17 zero-trials gate disposition (Q3, [[mcp-monetization-killswitch]]).
  The 10-05 gate stands.
- **win-tracker redeploy (`d44a272`) + blog-generator redeploy** for the 08-25 cohort pin.
  The 08-31 newsletter + rubric fix rides on the same redeploy. x-poster is dead, skip it.

## Watch / dated checkpoints
- **Next NYSE holiday 2026-11-26:** confirm neither `forward-paper-trader-label-pool`
  (17:00 ET that day) nor `dbt-daily-build` (06:30 ET 11-27) pages. Both holiday-noise
  fixes deployed 09-08 (dbt-runner-00011, trader-00054). [[market-holiday-cron-noise-two-chains]]
- **Confirm `liquidity_rank`/`liquidity_score`/`listed_strikes` are non-NULL on a recent
  scan and the log says "liquid universe top-100".** They were NULL on 100/100 rows on
  08-25 (`_score_ticker` rebuilt the dict), making the enrichment liquid gate inoperative;
  pool was still correct. Fix `312e970` — check the deployed scanner rev first, the repo
  notes disagree on whether it shipped. Rollback = `LIQUID_UNIVERSE`/`ENRICH_LIQUID_ONLY`=false.

## Open engineering (small items archived to `docs/archive/` on demand; ask git log)
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
  until blog-generator is redeployed with the fixed prompt.
- P1 live 10:00 anchor pass — ACCEPTED, not built, owner $ (Polygon cost). Sized 08-31:
  only 31.7% of name-days have a real print at 10:00-10:04, so every opportunity sample
  is liquidity-selected. [[entry-mark-is-a-delayed-day-close]]

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
