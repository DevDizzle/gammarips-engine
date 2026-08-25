# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## START HERE (next session)
Owner has ~90 min of clicks pending in `~/workspace/GAMMARIPS-GO-RUNSHEET.txt`
(items 1-5 in order: test checkout, merge harness PR #3, Stripe prices + merge webapp
PR #29, send the relaunch email, Show HN). Do not re-ask. If he is not ready, work the
NO-OWNER QUEUE and leave the run-sheet as is.

NO-OWNER QUEUE (in order, each shippable alone):
1. WEBAPP COPY REWRITE — the last copy surface, and the only one left. The other
   three repos are DONE (2026-08-25, branches below). Spec:
   `docs/GTM-COPY-REWRITE-BRIEF.md`. Read `../gammarips-webapp/CLAUDE.md` FIRST,
   branch, run `gammarips-copywriter`, `/ship` from `~/workspace`. Merging to main
   auto-deploys production, so treat the merge as the ship.
2. MCP repo `src/`: `title` + `readOnlyHint` on all 9 tools (Connectors Directory
   gate), `open_past_due` false stall, row-cap audit. Own commit, redeploy per that
   repo. NOT done 2026-08-25: the granted paths covered content/README/skills only.
3. Creator pitch + Stripe promo-code design (free Pro + rev share) ->
   `docs/GTM-CREATOR-PROGRAM.md`, short.
4. Reddit follow-ups (r/ClaudeAI, r/mcp, r/algotrading) + the dev.to syndication post
   -> `~/workspace/GAMMARIPS-POSTS.txt`. Owner posts.
5. Guide B2 ("How to trade options with Claude Code") + `scripts/blog/publish_guide.py`
   (plan §B9). Not published without `/ship`.

DONE 2026-08-25, ALL UNPUSHED AND UNDEPLOYED — review then ship:
- `gammarips-mcp` `fix/moneyness-claim-and-exit-horizons` 3c2b732 — moneyness claim
  retired (it contradicted the repo's own education.py), causal frames removed,
  cohort bounds, exit-lab horizons, new `selection-research-closed` playbook,
  funnel sentence in README + SKILL + start-here.
- `gammarips-mcp-serverjson` `fix/funnel-copy-sync` 2cba0a6 — same sentence, per the
  MCP's sync rule.
- `gammarips-harness` `fix/hn-opener-liquid-funnel` 992e980 — the Show HN opener.
  Branched off main so PR #3 keeps its scope.
- Engine master: scanner NULL-column fix DEPLOYED (`overnight-scanner-00017-n7z`),
  VIX as-of fix `6a799fd` (NOT deployed), compliance whole-phrase matcher `a7fe472`
  (NOT deployed, needs x-poster + blog-generator redeploy), moneyness ruling ADR
  `6a797b5`.

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
- Run-sheet items 1-10 and questions Q1-Q3 (`~/workspace/GAMMARIPS-GO-RUNSHEET.txt`).
- Revoke + regenerate the 08-06 test MCP key (pasted in chat).
- Record the 08-17 zero-trials gate disposition (run-sheet Q3, memory
  `mcp-monetization-killswitch`). The 10-05 gate stands.
- win-tracker redeploy (`d44a272`) + x-poster / blog-generator redeploy for the
  2026-08-25 cohort pin.
- Compliance substring misfires (`'for you'` hit the relaunch email on "for your
  agent"; `libs/gammarips_content/.../compliance.py`).
- Organic Social halved (67→35 sessions/28d); x-poster lane needs its own look.
- Small: restore `blog_posts/building-options-flow-pipeline-ai-agents` to `published`;
  lx6bb stray docs call; Cursor listing v4; X pins/bio; Stripe MCP.

## Watch / dated checkpoints
- ✅ FIRST LIQUID SCAN VERIFIED 2026-08-25. `overnight_signals` scan_date 08-24 =
  100 rows, all `universe_mode='LIQUID_TOP_N'`, 43 BULLISH (08-21 was 1,973 mover
  rows). Funnel shape correct. Trader harness traded 37 names that morning.
  **But `liquidity_rank`/`liquidity_score`/`listed_strikes` were NULL on 100/100
  rows** — `_score_ticker` rebuilt the dict and dropped them. So the enrichment
  `liquidity_rank <= LIQUID_TOP_N` gate matched nothing and `_scan_is_ranked()`
  fell back to NO liquid gate. Pool was still right (the scanner restricts the
  universe upstream), gate was inoperative, columns dead. Fixed `312e970`,
  NOT deployed and NOT compile-checked. **Next: deploy the scanner, then confirm
  the three columns are non-NULL on the next scan and the log says "liquid
  universe top-100".** Rollback = `LIQUID_UNIVERSE`/`ENRICH_LIQUID_ONLY`=false.
- 🔴 Attribution test checkout (run-sheet item 1) gates Show HN.
- Owner's 08-13 trial conversion: `invoice.paid` + `proUntil` refresh, unconfirmed.
- ~08-27 threshold re-fit: confirm the 08-19 `pool_liquidity_snapshot` closes it.
- Mid-Aug ITM check (needs ≥200 expired post-06-12-era rows).

## Open engineering
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
