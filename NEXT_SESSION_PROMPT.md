# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## START HERE (2026-10-15)
**10-15:** rule set B contract floor SHIPPED (scanner rev 00018-d42) and the stock-move study
ran, NOT PASS (both in Owner queue). **09-28:** tournament + paper cohort + eval RETIRED (5
jobs paused, `docs/DECISIONS/2026-09-28-retire-tournament-paper-cohort-eval.md`). gammarips-mcp
rev 00054 answers `GET /mcp` with 405. Report-gen rev 00023 has Gemini timeouts. Trader
pool-freshness guard: `~/workspace/TRADER-POOL-FRESHNESS-PROMPT.txt`.
**GTM, measured 09-15:** 0 external subs, 0 external MCP clients, ~20 human sessions/15d.
Trader LIVE since 09-15. Plan of record [[public-trace-export-is-the-gtm-asset]]: daily
redacted `traces/` files in the harness repo, then Show HN (`gammarips-harness/docs/HN-SUBMISSION.txt`,
uncommitted). Needs >=3 live days in `traces/` and the branch merged first.

NO-OWNER QUEUE (in order, drafts to `~/workspace/GAMMARIPS-POSTS.txt`): 1. Reddit posts
(r/ClaudeAI, r/mcp, r/algotrading) + dev.to hooked on `traces/2026-09-15.md`. 2. Managed setup
offer copy ($1,000 install of the open-source harness, paper-first, never "I build your bot";
webapp copywriter + `/ship`). 3. Creator pitch + Stripe promo-code design ->
`docs/GTM-CREATOR-PROGRAM.md`. 4. Guide B2 + `scripts/blog/publish_guide.py`.

**Secrets: DONE 09-17, topic closed.** Mount strip deployed for report-gen and gammarips-mcp
(09-28). enrichment-trigger still mounts the dead key until its next deploy. The 08-28 $39 sub is KEPT, never mention it.

**POSITIONING — DECIDED 2026-09-01, do not re-open.** AI-engineer content goes on the
owner's PERSONAL X + LinkedIn, NOT on @gammarips ([[x-poster-is-not-acquisition]]).
The agreed line is "a hard live domain for your agent, with next-day ground truth".

## Active workstream — the 08-22 go plan (subs before 10-05)
Decision `docs/DECISIONS/2026-08-22-go-plan-outbound-plugin-founding-offer.md`. Owner
steps `~/workspace/GAMMARIPS-HN-LAUNCH.txt` (the old GO-RUNSHEET is archived; its
remaining items 7-10 + Q1/Q3 were folded in). Memory [[go-plan-2026-08-22]].
- DONE: plugin PR #3, founding offer PR #29, GA4 attribution (08-31), relaunch email
  (zero, list closed), placements 6a/6b (09-01).
- REMAINING: **Show HN** (window moved to 09-23/24, lead is the trace export, text in the
  harness repo; listings steps in `~/workspace/GAMMARIPS-HN-LAUNCH.txt`), 6c
  awesome-claude-code issue form (human only), plugin directory form, Connectors Directory.
- Measure by referral sessions + human MCP initializes (claude-code / cursor / codex UAs,
  non-cloud IPs), NEVER link count. Still zero external clients ever as of 09-01: every
  agent-client IP is owner infra (`gr-trader-vm` 8.234.242.149) or a Claude Code session.
- OAuth AS + `/pro` LIVE since 08-19 ([[oauth-as-built-2026-08-19]]). GitGuardian
  36370105 false positive: mark it.

## Owner queue
- **Stock-move study DONE 10-15, NOT PASS** (`FINDINGS_LEDGER.md` §2026-10-15 stock-move study,
  brief top block). Wide era null (best IC t 2.5, 0/30 pass BH, best excess +0.14 pts vs +1.0).
  Holdout = six-week mega-cap regime (same 10 names in the top decile daily), not a feature.
  Selection research CLOSED again. ONE owner decision open: shadow rank column (log dollar
  volume within the liquid 100) read by the trader's fixed-N drift test, or nothing. Never a
  universe change on a six-week read.
- **Pool contract floor SHIPPED 10-15 (rule set B: mid >= 1.50, delta <= 0.50, OI >= 500):**
  `docs/DECISIONS/2026-10-15-contract-premium-floor.md`. CHECK 10-16 AM: first scan log
  ("Contract floor" lines, pool about 40 names, no mid below $1.50), then the trader funnel
  rejection rate from 10-16 on. Rollback = three env vars to 0 + redeploy.
  [[trader-funnel-log-is-pool-quality-ground-truth]]
- Webapp revamp PR #36 SHIPPED 10-02 (merge `1deb327`, live ~9 min later). Open:
  owner review of /disclosures #01 wording; new og-image; traces merge fills /scorecard.
- Traces branch `traces/2026-09` pushed 09-16 (timer live): PR -> main before the HN post
  (`~/workspace/GAMMARIPS-TRACES.txt`). Show HN + 6c form: `~/workspace/GAMMARIPS-HN-LAUNCH.txt`
  (also run-sheet 7-10, Q1, Q3). Posts: `~/workspace/GAMMARIPS-POSTS.txt`.
- **All GTM moved to Grok Bot 09-16** ([[social-strategy-moved-to-grok-bot]]): prompt in
  `~/workspace/GROKBOT-SETUP-PROMPT.txt`, workspace-root session. x-poster KILLED 09-16.
- Revoke + regenerate the 08-06 test MCP key (pasted in chat). Record the 08-17 zero-trials
  gate disposition ([[mcp-monetization-killswitch]]); the 10-05 gate stands.
- win-tracker (`d44a272`) + blog-generator redeploy for the 08-25 cohort pin + newsletter fix.

## Watch / dated checkpoints
- **Billing export (from ~10-05):** Cloud Run weekly cost should drop well below $12.9/wk after the
  09-28 MCP fix. Rollback env var `MCP_GET_STREAM_ENABLED=true`. [[vertex-cost-measurement-method]]
- **Next NYSE holiday 2026-11-26:** confirm neither `forward-paper-trader-label-pool`
  (17:00 ET that day) nor `dbt-daily-build` (06:30 ET 11-27) pages. Both holiday-noise
  fixes deployed 09-08 (dbt-runner-00011, trader-00054). [[market-holiday-cron-noise-two-chains]]

## Open engineering (small items archived to `docs/archive/` on demand; ask git log)
- 🔴 No spread/depth measurement exists (Polygon NBBO entitlement, owner $ call).
- MCP `get_regime_context` `lag_note` does not mention the FRED publication difference.
- `relaunch_email.py` mails Mailgun-suppressed addresses (14 of 30 failures on the 08-31
  send). Fix before any future send. [[dormant-list-is-dead]]
- Least-privilege service accounts: 12/16 Cloud Run services run as the default compute
  SA with `roles/editor`. Plan + order in [[least-privilege-service-accounts-plan]].
- `content-blast-mon-0530` PAUSED since 07-05; unpause only after the blog-generator redeploy.
- P1 live 10:00 anchor pass — ACCEPTED, not built, owner $ (Polygon cost). Sized 08-31:
  only 31.7% of name-days have a real print at 10:00-10:04, so every opportunity sample
  is liquidity-selected. [[entry-mark-is-a-delayed-day-close]]

## Live posture
- LIQUID-UNIVERSE FUNNEL LIVE 2026-08-24 (`docs/DECISIONS/2026-08-24-liquid-universe-funnel.md`):
  100 most liquid names, not movers; $500K UOA floor gone. Ships on FILLS (no-fill 40.5%
  -> 6.1%), NEVER on edge — that framing is a forbidden claim. Cohort 08-25. Revs
  scanner-00016-rs5 / enrichment-00050-q54 / notifier-00064-prb.
- Selection research CLOSED (08-22: pool = matched random; 08-31 exception null; 10-15
  owner-reopened stock-move study NOT PASS). [[selection-research-closed]]. Do not re-open.
- No engine execution policy since 09-28 (V7.1 RETIRED, `docs/DECISIONS/2026-09-28-retire-tournament-paper-cohort-eval.md`). The engine is a data pipeline
  for the MCP and the VM trader. Keep `pool-liquidity-refresh` and all data jobs enabled.
- Owner trades LIVE (Robinhood since 07-09). Daily crons run; MCP paywall ENFORCE.
- Health: operator digest 07:15 ET weekdays; SEO auth via the `seo-auth` skill.
