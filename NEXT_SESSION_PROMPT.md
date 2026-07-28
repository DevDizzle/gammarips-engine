# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Rule: `.claude/rules/next-session-prompt.md`.

## Active workstream — 2026-07-17 simplification replan: LANDED
Built + shipped in one autonomous session (07-17 night). Plan of record:
`docs/EXEC-PLANS/2026-07-17-simplification-replan.md`; digest: memory
`simplification-replan-2026-07-17`.
- **MCP v4 LIVE** at `https://mcp.gammarips.com` (branded Cloud Run domain +
  Google cert; rev `gammarips-mcp-00040-lmq`). 29→9 tools; paywall correct
  (`get_pool` preview free / full pro — a build defect that served the paid pool
  free was caught + fixed). Plus **wiki-brain**: 26 free methodology pages via
  `get_playbook` (`get_playbook("methodology")`). Two `gammarips-review` PASSes.
  Canonical repo reconciled = `DevDizzle/gammarips-mcp` (`0d9c883`: v4 code +
  **Cursor plugin v4** + branded listing); local-repo→serverjson mis-wire fixed,
  serverjson reset. GTM entry = plugins (Claude/Cursor) + the open-source harness.
- **Harness PUBLIC** — `github.com/DevDizzle/gammarips-harness` (scrub-clean,
  points at mcp.gammarips.com). The clone-me GTM artifact.
- **Trader** run-time skills + v4 rename → merged to `master` (`8a9f79c`).
- **Engine wiki** 73/73 DECISIONS distilled → merged to `master` (PR #36); live
  policy now answers from `docs/wiki/_index/REGISTRY.md` + a thin CLAUDE.md pointer.
- **Webapp** `landing/video-led` branch READY (v4 surface + branded URL +
  TOOL_COUNT/PRICE constants). **Video DECOUPLED (owner call 07-21):** hero is now
  a static agent-session terminal ("Agentic Trading" eyebrow + live tool chips), so
  the branch no longer waits on the video — it merges via `/ship` NOW to correct the
  live site's stale v4 surface (main still says "23 tools" + old unbranded endpoint).
  Video drops in later as a one-line iframe swap (comment left in `hero.tsx`).

## Owner queue
- **Cohort reset applied 07-28 (review adjudication — owner may override):**
  `LIVE_COHORT_START_DATE` → 2026-07-29 (public panel restarts under the new
  selection; 22 prior rows kept in ledger, not truncated). Override = constant
  revert + DECISIONS note.
- **Surface `expected_liquidity` via MCP `get_pool` + webapp** (engine-side field
  ships in the 07-28 tradeability build; MCP is a separate repo — wire it next
  session so subscribers see CLEAN/THIN before entry).
- **Cursor plugin listing refresh:** the plugin file is now v4 in the repo
  (`.cursor-plugin/plugin.json` 4.0.0 + branded URL; bundled skill rewritten to
  the 9-tool surface + methodology corpus). If cursor.directory / Open Plugins
  does NOT auto-pull from the repo, re-submit / refresh the listing to v4.
- **Record the morning video** (now a POLISH item, not a launch blocker — hero ships
  static 07-21): send the YouTube link and I swap the placeholder comment in
  `hero.tsx` for the iframe.
- **Launch push (MCP + harness = "Agentic Options Trading"):** refresh the 07-07
  directory listings to the v4 branded endpoint (`mcp.gammarips.com`, 9 tools) — they
  point at the old `...run.app/mcp` + "23 tools"; then Show HN / X thread / launch
  blog on the agentic-trading hook (`docs/GTM-MCP-DIRECTORY-PLAN.md`).
- 🔴 **Rotate `POLYGON_API_KEY`** (07-06 leak; `printf %s` no trailing newline;
  redeploy every mounting service: gammarips-mcp, forward-paper-trader,
  enrichment-trigger, signal-notifier, win-tracker). Still pending.
- One real Stripe checkout test. Counsel deferred to ~100 subs (owner call, risk
  accepted — memory `scalping-frontrun-legal-constraint`).
- X: unpin 03-14, pin distribution-stat draft, bio refresh (memory `project_x_revamp_2026_07_09`).

## Watch / dated checkpoints
- **07-29 first live run of BOTH 07-28 builds:** (a) enrichment 05:30 — `liq
  demotion ON ... flagged/admitted` line + clean atomic replace; (b) notifier
  09:52 — "Two-tier slate floor" summary line, email Liquidity line,
  `signal_ranker_runs.*_prompt_version=8`; (c) `agg_pool_tradeability` — ghost
  rate should trend 22%→~12%. Rollbacks: `LIQ_DEMOTION=false` /
  `PRINT_FLOOR_ENABLED=false` (cron+judge rollback rules in the DECISIONS note).
- **~08-27: re-fit print/liq thresholds** on ~30 more days of
  `pool_liquidity_snapshot` (review hard requirement — 15-day in-sample fits).
- **mom_60 tilt KEPT by owner call 07-28** (research says retire-grade OOS —
  FINDINGS_LEDGER `2026-07-28`; owner: "don't drop the tilt yet"). Revisit with
  live-cohort N≥30 or if the live book underperforms.
- **08-17**: kill-switch — zero MCP trials → early reevaluation
  (**10-05**: zero paying subs → business reevaluation).
- **~07-23**: `x_post_metrics` two-week read → which post slots live.
- **Mid-Aug**: re-run the post-06-12-era ITM check (needs ≥200 expired era rows).
- Weekly `mcp_analytics`: zero external paying users as of 07-17.

## Open engineering
- ~~Opp labeler stall~~ **RESOLVED 07-28**: backfill executed (850 rows, surface
  current through 07-22) + automated daily filler (`/fill_closed_windows`, 17:30 ET
  cron) + dbt staleness tripwire + project-wide cron-failure email alerting (channel
  + policy were ZERO before). `docs/DECISIONS/2026-07-28-opp-labeler-automation-and-alerting.md`.
- **`iv_rank_entry`/`iv_percentile_entry` post-entry leakage** — computed 17:00 ET vs
  16:30 close cache (`benchmark_context.py:488-513`); tag as telemetry + exclude from
  `enriched_features_v1` before any future feature search.
- Filler edge case (review 07-28, non-blocking): transient NO_BARS on the opp fetch
  + successful 3d fetch = row never re-qualifies; warn on that combo or add it to
  the re-select predicate.
- MCP smoke-test scrub covers only the 26 new methodology pages — extend it to ALL
  `content/playbooks/` (the `V7_1_TILTED_GIGO` changelog leak slipped that gap).
- Webapp `/lab` research prose has pre-existing em dashes — `/ship` catches at merge.
  Webapp internal Gemini tools (`src/ai/**`) + a legacy script still ref old MCP host.
- Service-auth hardening not executed (`docs/DECISIONS/2026-07-02-service-auth-hardening.md`).
- Substrate: 41 `recommended_delta`=0.0 ITM-at-scan rows; 7 pick rows NO_BARS.
- RM-001b BLOCKED: `pool_liquidity_snapshot` quote cols confirmed 100% NULL (07-28) —
  fetcher populates OI/greeks only; needs quote entitlement, owner $ call.

## Live posture
- Policy: V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + `docs/wiki/_index/REGISTRY.md` + `CHEAT-SHEET.md`.
- Owner trades LIVE (Robinhood since 07-09) — memory `capital-constraint` (PDT analysis).
- Daily crons run end-to-end; no urgent engine action.
