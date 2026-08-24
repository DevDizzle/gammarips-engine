# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

## START HERE (next session)
Owner has ~90 min of clicks pending in `~/workspace/GAMMARIPS-GO-RUNSHEET.txt`
(items 1-5 in order: test checkout, merge harness PR #3, Stripe prices + merge
webapp PR #29, send the relaunch email, Show HN). Do not re-ask. If he is not ready,
work the NO-OWNER QUEUE below and leave the run-sheet as is.

NO-OWNER QUEUE (in this order, each shippable alone):
1. WEBAPP COPY REWRITE. The funnel changed 08-24, so the site is factually
   wrong: it sells a market-wide unusual-activity scan that finds the best
   candidates, and neither half is true now. Spec is
   `docs/GTM-COPY-REWRITE-BRIEF.md` (positioning, allowed claims with their
   conditions, banned phrasings, page list, process). Read
   `../gammarips-webapp/CLAUDE.md` first, branch, run `gammarips-copywriter`,
   `/ship` from `~/workspace`. Also covers x-poster + blog-generator prompts.
2. Fix the report-vs-regime VIX as-of mismatch (Open engineering, first red item).
   It is visible in the HN demo GIF.
3. MCP repo: add `title` + `readOnlyHint` to all 9 tools (Connectors Directory
   gate). Own review gate, own commit, redeploy per that repo.
4. Draft the creator pitch + Stripe promo-code design (free Pro + rev share) into
   `docs/GTM-CREATOR-PROGRAM.md`, short.
5. Draft the Reddit follow-ups (r/ClaudeAI, r/mcp, r/algotrading) and the dev.to
   syndication post into `~/workspace/GAMMARIPS-POSTS.txt`. Owner posts.
6. Guide B2 ("How to trade options with Claude Code") as markdown + the publish
   script `scripts/blog/publish_guide.py` (plan §B9). Not published without `/ship`.
7. Fix the `'for you'` compliance substring misfire.

## Active workstream — the 08-22 go plan (subs before 10-05)
Decision: `docs/DECISIONS/2026-08-22-go-plan-outbound-plugin-founding-offer.md`.
Owner steps, in order: `~/workspace/GAMMARIPS-GO-RUNSHEET.txt`. Memory `go-plan-2026-08-22`.
- Harness PR #3 (plugin `gammarips` + real free-tier GIF): OPEN, owner merges, then the
  community plugin form. Bundled server = `/mcp` + Bearer header (free tools need no
  key, verified). Plugin name is immutable.
- Webapp PR #29 `offer/founding-100` ($29 first 100, 30-day trial, $299/yr): OPEN,
  DO NOT MERGE yet. Needs the two Stripe price ids from the owner, then merge = deploy.
- Relaunch email: draft `~/workspace/GAMMARIPS-RELAUNCH-EMAIL.txt` (rubric PASS),
  script `scripts/gtm/relaunch_email.py` (dry run default). The session sandbox
  classifier blocks running it, the owner runs it. Send only after the offer is live.
- Prospect list `~/workspace/GAMMARIPS-PROSPECTS.csv` (GitHub-derived, read-only).
- Placements staged: awesome-mcp-servers branch `add-gammarips-mcp-2026-08` (prior
  PR #1956 was CLOSED, say so), awesome-claude-skills branch `add-gammarips-harness`,
  awesome-claude-code = issue form only. Compare URLs in the run-sheet.
- Show HN: after the attribution test checkout + plugin merge. Week of 08-25.
  Text: harness `docs/HN-SUBMISSION.txt`. Mechanics: `docs/GTM-DISTRIBUTION-PLAYBOOK.md`.
- Measure placements by referral sessions and human MCP initializes (claude-code /
  cursor / codex UAs from non-cloud IPs), never link count. 7-day baseline 08-22:
  ~2,700 `/mcp` POSTs, all monitors and crawlers, zero external humans.

## Research (parked behind GTM, state intact)
1. Liquid-universe funnel: DONE 08-22, RULE 2 (null on signal, +0.4pp CI
   [-1.7, 2.1]); executability UNFILLABLE 40.5% -> 6.1%. Ledger §2026-08-22,
   brief top entry, wiki [[liquid-universe-uoa-null]]. OWNER CALL RESOLVED
   08-24: SHIPPED on executability grounds, with the $500K UOA floor dropped.
   DECIDED, do not re-raise. See Live posture.
2. Pool-vs-benchmark: DONE 08-22, ALL THREE FAIL (A-B -1.33pp [-3.78, 1.04]).
   Pre-committed consequence: the scan is not a selection edge, selection
   research is CLOSED, product = surface data. Ledger §2026-08-22, brief top
   entry, wiki [[selection-research-closed]]. Control tape in
   `control_minute_paths`. No prod change. Never re-open selection research.
Open owner call (flagged once): later same-day entry ([[first-hour-bleed]]).

## OAuth + GTM residue
- OAuth AS + `/pro` LIVE since 08-19 (memory `oauth-as-built-2026-08-19`). Webapp copy
  PR #28 `copy/oauth-live` is MERGED (seen 08-22 when `offer/founding-100` was cut).
- Guides B3-B6 CUT 08-22. B2 (Claude Code) stays. Per-client OAuth sign-in
  verification still gates B4/B5. GitGuardian 36370105 false positive: mark it.
- Connectors Directory needs a Team/Enterprise claude.ai org (owner Q1) and `title` +
  `readOnlyHint` on all 9 MCP tools (today 0 titles, 1 hint). MCP repo task.
- Creator program (free Pro + promo code, rev share): design the Stripe promo + the
  pitch after the offer ships.

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
- Small: restore `blog_posts/building-options-flow-pipeline-ai-agents` to
  `published`; lx6bb stray docs call; Cursor listing v4; X pins/bio; Stripe MCP.

## Watch / dated checkpoints
- 🔴 FIRST LIQUID SCAN 2026-08-24 23:00 ET. Next morning: `overnight_signals`
  scan_date 08-24 = ~100 rows, all `universe_mode='LIQUID_TOP_N'`,
  `liquidity_rank` 1..100 (was ~2,000 mover rows). Then the 08-25 05:30 ET
  enrichment log says "liquid universe top-100" + "UOA floor NONE"; pool ~40-50.
  Rollback: `LIQUID_UNIVERSE=false` + `ENRICH_LIQUID_ONLY=false`.
- 🔴 Attribution test checkout (run-sheet item 1) gates Show HN.
- Owner's 08-13 trial conversion: `invoice.paid` + `proUntil` refresh, unconfirmed.
- ~08-27 threshold re-fit: confirm the 08-19 `pool_liquidity_snapshot` closes it.
- Mid-Aug ITM check (needs ≥200 expired post-06-12-era rows).

## Open engineering
- 🔴 Daily report narrative vs `get_regime_context` disagree on VIX for the same
  date (14.89 "risk-on" vs 16.01, SPY BEARISH) — seen live in the 08-22 demo. The
  report generator reads a different as-of. Find and fix the as-of.
- 🔴 Deploy the LLM cost-accounting fix `a2fb621` (signal-judge real change, then
  enrichment-trigger + overnight-report-generator redeploy). Verify per
  `docs/DECISIONS/2026-08-17-llm-cost-accounting-fix.md`.
- 🔴 No spread/depth measurement exists (Polygon NBBO entitlement, owner $ call).
- FALLBACK picks bypass the liquidity floor (`POLICY_GATE_FALLBACK` takes `df.iloc[0]`).
- MCP repo: tool `title` + annotations for all 9 tools; `open_past_due` false stall;
  row-cap audit (`labels`, `positions`, `signal_performance`); QUALIFY dedup;
  `freshness_note` copy; surface EXECUTION-RISK-GUIDELINES through `get_playbook`.
- P1 live 10:00 anchor pass — ACCEPTED, not built, owner $ (Polygon cost).
- Audit snapshot `day.*` readers and `next_url` pagination; x-poster IAM audit.
- Smaller: `iv_rank_entry` view exclusion; earnings-rail stamp (GAP-014); UNDATABLE
  split; substrate rows (41 delta-0 ITM, 7 NO_BARS); service-auth hardening; webapp
  old-MCP-host refs + 3 tsc errors; blog non-blocking pair; `gammarips-eval` config.

## Live posture
- LIQUID-UNIVERSE FUNNEL LIVE 2026-08-24 (`docs/DECISIONS/2026-08-24-liquid-universe-funnel.md`):
  the scan takes the 100 most liquid names, not price movers, and the $500K UOA
  floor is gone. Ships on FILLS (UNFILLABLE 40.5% -> 6.1%), NEVER on edge.
  Cohort 2026-08-25, `policy_version` unchanged. Revs scanner-00016-rs5 /
  enrichment-00050-q54 / notifier-00064-prb. Follow-up: public copy still says
  market-wide UOA scan: rewrite spec is `docs/GTM-COPY-REWRITE-BRIEF.md`.
- V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + wiki `REGISTRY.md` + `CHEAT-SHEET.md`.
  Cohort start: `LIVE_COHORT_START_DATE` in `signal-notifier/main.py` (never hardcode).
- Owner trades LIVE (Robinhood since 07-09). Daily crons run; MCP paywall ENFORCE.
- Health: operator digest 07:15 ET weekdays; SEO auth via the `seo-auth` skill.
