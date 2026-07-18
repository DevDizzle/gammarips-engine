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
- **Webapp** `landing/video-led` branch READY (v4 surface + branded URL + video
  hero poster + TOOL_COUNT/PRICE constants) — **HELD**; merges via `/ship` AFTER
  the video exists.

## Owner queue
- **Cursor plugin listing refresh:** the plugin file is now v4 in the repo
  (`.cursor-plugin/plugin.json` 4.0.0 + branded URL; bundled skill rewritten to
  the 9-tool surface + methodology corpus). If cursor.directory / Open Plugins
  does NOT auto-pull from the repo, re-submit / refresh the listing to v4.
- **Registry republish** v4.0.0 + branded URL:
  `cd gammarips-mcp && mcp-publisher login github && mcp-publisher publish` (token
  expired; `login github` is interactive — you run it).
- **Record the morning video** → send YouTube link + harness repo link → I merge the
  landing PR via `/ship`.
- 🔴 **Rotate `POLYGON_API_KEY`** (07-06 leak; `printf %s` no trailing newline;
  redeploy every mounting service: gammarips-mcp, forward-paper-trader,
  enrichment-trigger, signal-notifier, win-tracker). Still pending.
- One real Stripe checkout test. Counsel deferred to ~100 subs (owner call, risk
  accepted — memory `scalping-frontrun-legal-constraint`).
- X: unpin 03-14, pin distribution-stat draft, bio refresh (memory `project_x_revamp_2026_07_09`).

## Watch / dated checkpoints
- **08-17**: kill-switch — zero MCP trials → early reevaluation
  (**10-05**: zero paying subs → business reevaluation).
- **~07-23**: `x_post_metrics` two-week read → which post slots live.
- **Mid-Aug**: re-run the post-06-12-era ITM check (needs ≥200 expired era rows).
- Weekly `mcp_analytics`: zero external paying users as of 07-17.

## Open engineering (non-blocking)
- MCP smoke-test scrub covers only the 26 new methodology pages — extend it to ALL
  `content/playbooks/` (the `V7_1_TILTED_GIGO` changelog leak slipped that gap).
- Webapp `/lab` research prose has pre-existing em dashes — `/ship` catches at merge.
  Webapp internal Gemini tools (`src/ai/**`) + a legacy script still ref old MCP host.
- Service-auth hardening not executed (`docs/DECISIONS/2026-07-02-service-auth-hardening.md`).
- Substrate: 41 `recommended_delta`=0.0 ITM-at-scan rows; 7 pick rows NO_BARS.
- RM-001b (bid/ask spread) BLOCKED on the quote-feed purchase — owner $ call.

## Live posture
- Policy: V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + `docs/wiki/_index/REGISTRY.md` + `CHEAT-SHEET.md`.
- Owner trades LIVE (Robinhood since 07-09) — memory `capital-constraint` (PDT analysis).
- Daily crons run end-to-end; no urgent engine action.
