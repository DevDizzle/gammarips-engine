# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## START HERE (next session)
2026-08-31. GA4 PURCHASE ATTRIBUTION IS FIXED AND VERIFIED. The 08-29 diagnosis
was right that MP was broken and wrong about why: the property had never attested
the **User Data Collection Acknowledgement**, so GA4 refuses to create a
Measurement Protocol secret at all and the stream held ZERO. The value stored on
2026-02-02 could never have been valid. Owner authorized the attestation, secret
minted (id 15534172427), `GA_API_SECRET` at v2, `apphosting.yaml` moved it out of
the dead `secretEnv:` into `env:`. **Proven by GA4 Realtime ingesting a test
purchase** (baseline 0 -> 1). Live rev `gammarips-webapp-build-2026-08-31-003`.
Tools: `scripts/gtm/ga4_mp_secret.py` (list/attest/mint, never prints the value),
`scripts/gtm/ga4_mp_verify.py` (send + Realtime poll). Memory
[[ga4-mp-204-is-not-ingestion-proof]]. Historical events are NOT recoverable;
conversion data starts 08-31.

FIRST TASK: finish the secret migration. Webapp PR #32 is MERGED (yaml declares
9 secrets as Secret Manager refs) but the Firebase Console still holds the plain
values and the CONSOLE WINS, so nothing has changed yet. Safe resting state, not
a broken one. Owner runs the two commands in
`~/workspace/GAMMARIPS-SECRET-MIGRATION.txt` (delete 9 console rows, then a
rollout). The classifier blocked the agent from doing it, including the
single-variable form for STRIPE_SECRET_KEY. All 9 were hash-verified identical to
Secret Manager first.

OPEN OWNER QUESTION (blocks the last 3): `GEMINI_API_KEY`, `GOOGLE_API_KEY`
(same key as each other) and `FMP_API_KEY` have DIFFERENT values in the console
than in Secret Manager. enrichment-trigger, gammarips-mcp,
overnight-report-generator and signal-notifier all read them at `latest`, so
syncing changes what four production services get. Ask which value is
authoritative, then migrate.

ALSO 2026-08-31, all in this session:
- **Relaunch email SENT to 206** (owner ran it). Mailgun click tracking had
  rewritten the `claude mcp add` line into a tracking redirect and broken the
  only CTA; tracking is now OFF and attribution comes from `utm_source=relaunch`
  ([[mailgun-click-tracking-breaks-commands]]). Runner:
  `scripts/gtm/send_relaunch.sh`.
- **GA4 is majority bot traffic and the numbers were wrong twice.** An Alibaba
  Cloud Singapore scraper (388 IPs in 600 requests, headless Chrome, no bot UA,
  targets `/signals/*`). Bot share is **50.1%**, not the 82%/97% previously
  written: the `country` dimension is event-scoped and its rows do not divide
  into the deduplicated total. `scripts/seo/ga4_query.py` now filters by default
  and prints raw vs kept; `scripts/seo/bot_filter.py` holds the evidence.
  [[ga4-singapore-scraper-and-the-country-row-trap]]
- **Weekly newsletter: prompt fixed, NOT DEPLOYED.** It asked Gemini for a
  cherry-picked winner with FOMO copy selling "our curated daily GammaRips pick"
  and named dead V6, and the rubric passed it. Featured-trade section removed,
  prohibitions rewritten, subject+preheader now scored, 10 new rubric entries.
  Verified: old draft now FAILS 4 ways, fresh render PASSES.
  **`libs/gammarips_content` is vendored at deploy time into BOTH x-poster and
  blog-generator, so both need a redeploy.** Also
  `content-blast-mon-0530` has been PAUSED since the last real blast on
  2026-07-05 — 8 Sundays of drafts, zero sends. Do not unpause before the
  redeploy. [[weekly-newsletter-blast-paused]],
  [[newsletter-prompt-was-a-generation-behind]]
- Show HN: owner says later this week. Text is in harness `docs/HN-SUBMISSION.txt`.
- Least-privilege SA migration planned, not started:
  [[least-privilege-service-accounts-plan]].

NO-OWNER QUEUE (in order, each shippable alone):
1. MCP repo `src/`: `title` + `readOnlyHint` on all 9 tools (Connectors Directory
   gate), `open_past_due` false stall, row-cap audit, and the stale `get_pool`
   docstring (`src/tools/v4.py:92-102` still states the retired $500K UOA gate;
   every connected agent reads it). Own commit, redeploy per that repo. NOT done
   2026-08-25: the granted paths covered content/README/skills only.
2. Creator pitch + Stripe promo-code design (free Pro + rev share) ->
   `docs/GTM-CREATOR-PROGRAM.md`, short.
3. Reddit follow-ups (r/ClaudeAI, r/mcp, r/algotrading) + the dev.to syndication post
   -> `~/workspace/GAMMARIPS-POSTS.txt`. Owner posts.
4. Guide B2 ("How to trade options with Claude Code") + `scripts/blog/publish_guide.py`
   (plan §B9). Not published without `/ship`.


## Active workstream — the 08-22 go plan (subs before 10-05)
Decision `docs/DECISIONS/2026-08-22-go-plan-outbound-plugin-founding-offer.md`. Owner
steps in order: `~/workspace/GAMMARIPS-GO-RUNSHEET.txt`. Memory `go-plan-2026-08-22`.
- Harness PR #3 (plugin `gammarips` + free-tier GIF): OPEN, owner merges, then the
  community plugin form. Bundled server = `/mcp` + Bearer (free tools need no key,
  verified). Plugin name is immutable.
- Webapp PR #29 `offer/founding-100` ($29 first 100, 30-day trial, $299/yr): OPEN,
  DO NOT MERGE. Needs the owner's two Stripe price ids, then merge = deploy.
- Relaunch email drafted (`~/workspace/GAMMARIPS-RELAUNCH-EMAIL.txt`, rubric PASS) +
  `scripts/gtm/relaunch_email.py`. The sandbox blocks sending; the owner runs it, only
  after the offer is live. Prospects `~/workspace/GAMMARIPS-PROSPECTS.csv`.
- Placements staged (branch names in the run-sheet): awesome-mcp-servers,
  awesome-claude-skills, awesome-claude-code = issue form only. Prior PR #1956 was
  CLOSED, say so.
- Show HN after the attribution checkout + plugin merge, week of 08-25. Text: harness
  `docs/HN-SUBMISSION.txt`. Mechanics `docs/GTM-DISTRIBUTION-PLAYBOOK.md`.
- Measure by referral sessions + human MCP initializes (claude-code / cursor / codex
  UAs, non-cloud IPs), NEVER link count. Baseline 08-22: ~2,700 `/mcp` POSTs, all bots.
- OAuth AS + `/pro` LIVE since 08-19 (memory `oauth-as-built-2026-08-19`); webapp copy
  PR #28 MERGED. Guides B3-B6 CUT 08-22, B2 stays (per-client OAuth sign-in
  verification gates B4/B5). GitGuardian 36370105 false positive: mark it.
- Connectors Directory needs a Team/Enterprise claude.ai org (owner Q1) + queue item 3.
  Creator program (free Pro + promo code, rev share): design after the offer ships.

## Owner queue
- **Finish the secret migration**: 2 commands in
  `~/workspace/GAMMARIPS-SECRET-MIGRATION.txt` (delete 9 console rows, then a
  rollout). PR #32 is merged but the console still wins until they are deleted.
- **Answer: which value is authoritative** for `GEMINI_API_KEY`/`GOOGLE_API_KEY`
  and `FMP_API_KEY`, console or Secret Manager? Blocks the last 3 migrations.
- Show HN, "later this week" (owner, 08-31). Harness `docs/HN-SUBMISSION.txt`.
- ✅ Relaunch email SENT to 206 on 08-31. ✅ GA4 MP secret minted and verified.
- Cancel the 08-28 test sub before Sep 4 18:26 UTC (real card, converts to $39).
- Run-sheet items 5-10 and questions Q1/Q3 (`~/workspace/GAMMARIPS-GO-RUNSHEET.txt`).
- Revoke + regenerate the 08-06 test MCP key (pasted in chat).
- Record the 08-17 zero-trials gate disposition (run-sheet Q3, memory
  `mcp-monetization-killswitch`). The 10-05 gate stands.
- win-tracker redeploy (`d44a272`) + x-poster / blog-generator redeploy for the
  2026-08-25 cohort pin. **The 08-31 newsletter + rubric fix rides on the same
  redeploy** (`libs/gammarips_content` is vendored into both at deploy time).
- Organic Social halved (67→35 sessions/28d); x-poster lane needs its own look.
- Small: restore `blog_posts/building-options-flow-pipeline-ai-agents` to `published`;
  lx6bb stray docs call; Cursor listing v4; X pins/bio; Stripe MCP.

## Watch / dated checkpoints
- Liquid scan verified 08-25, but `liquidity_rank`/`liquidity_score`/
  `listed_strikes` were NULL on 100/100 rows (`_score_ticker` rebuilt the dict),
  so the enrichment liquid gate was inoperative. Pool was still correct. Fix
  `312e970`. **Confirm the three columns are non-NULL on a recent scan and the log
  says "liquid universe top-100"** — check the deployed scanner rev first, the
  repo notes disagree on whether it shipped. Rollback = `LIQUID_UNIVERSE`/
  `ENRICH_LIQUID_ONLY`=false.
- ✅ Attribution unblocked 08-31 (see START HERE). Show HN no longer gated on it.
- Owner's 08-13 trial conversion: `invoice.paid` + `proUntil` refresh, unconfirmed.
- ~08-27 threshold re-fit: confirm the 08-19 `pool_liquidity_snapshot` closes it.
- Mid-Aug ITM check (needs ≥200 expired post-06-12-era rows).

## Open engineering
- Least-privilege service accounts: 12/16 Cloud Run services run as the default
  compute SA with `roles/editor`. Owner-approved to plan, not urgent, build logs
  are NOT public. Plan + order in [[least-privilege-service-accounts-plan]].
- `content-blast-mon-0530` PAUSED since the last real blast 2026-07-05. Do not
  unpause until x-poster + blog-generator are redeployed with the fixed prompt.
- 3 console/Secret-Manager key mismatches (see Owner queue) keep GEMINI/GOOGLE/FMP
  values printing in Cloud Build logs.
- ✅ VIX as-of mismatch FIXED `6a799fd`, not deployed. `_level_and_trend` dropped the
  observation date and `macro_regime` stamped `as_of: scan_date` on every field. FRED
  publishes each close after the session, so the value was routinely 1-3 days older
  than its label. Neither number was wrong, the label was. Now carries `vix_as_of`,
  `vix3m_as_of`, `ust10y_as_of`, `macro_stale_days`, and the prompt requires the
  narrative to cite the observation date. **Residual:** `get_regime_context`'s own
  `lag_note` still does not mention the FRED difference (gammarips-mcp `src/`).
- 🔴 Deploy the LLM cost-accounting fix `a2fb621` (signal-judge real change, then
  enrichment-trigger + overnight-report-generator redeploy). Verify per
  `docs/DECISIONS/2026-08-17-llm-cost-accounting-fix.md`.
- 🔴 No spread/depth measurement exists (Polygon NBBO entitlement, owner $ call).
- FALLBACK picks bypass the liquidity floor (`POLICY_GATE_FALLBACK` takes `df.iloc[0]`).
- MCP repo: tool `title`/annotations; `open_past_due` false stall; row-cap audit
  (`labels`, `positions`, `signal_performance`); QUALIFY dedup; `freshness_note` copy;
  surface EXECUTION-RISK-GUIDELINES through `get_playbook`.
- P1 live 10:00 anchor pass — ACCEPTED, not built, owner $ (Polygon cost).
- Audit snapshot `day.*` readers and `next_url` pagination; x-poster IAM audit.
- Smaller: `iv_rank_entry` view exclusion; earnings-rail stamp (GAP-014); UNDATABLE
  split; substrate rows (41 delta-0 ITM, 7 NO_BARS); service-auth hardening; webapp
  old-MCP-host refs + 3 tsc errors; blog non-blocking pair; `gammarips-eval` config.

## Live posture
- LIQUID-UNIVERSE FUNNEL LIVE 2026-08-24 (`docs/DECISIONS/2026-08-24-liquid-universe-funnel.md`):
  the scan takes the 100 most liquid names, not movers; the $500K UOA floor is gone.
  Ships on FILLS (no-fill at 10:00 ET 40.5% -> 6.1%), NEVER on edge — that framing is a
  forbidden claim. Cohort 2026-08-25, `policy_version` unchanged. Revs
  scanner-00016-rs5 / enrichment-00050-q54 / notifier-00064-prb.
- Selection research CLOSED (both 08-22 studies: pool = matched random, no signal on
  top of liquidity). Wiki [[selection-research-closed]] + [[liquid-universe-uoa-null]].
  NEVER re-open. Open owner call, flagged once: later entry ([[first-hour-bleed]]).
- V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + wiki `REGISTRY.md` + `CHEAT-SHEET.md`.
  Cohort start: `LIVE_COHORT_START_DATE` in `signal-notifier/main.py` (never hardcode).
- Owner trades LIVE (Robinhood since 07-09). Daily crons run; MCP paywall ENFORCE.
- Health: operator digest 07:15 ET weekdays; SEO auth via the `seo-auth` skill.
