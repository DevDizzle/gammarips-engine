# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Rule: `.claude/rules/next-session-prompt.md`.
> The append-era file (2026-05 → 07-17, 172KB) is archived at
> `docs/archive/NEXT_SESSION_PROMPT-append-era-2026-07-17.md`.

## Active workstream — 2026-07-17 simplification replan (RATIFIED)
Read `docs/EXEC-PLANS/2026-07-17-simplification-replan.md` FIRST — it has the vision,
locked decisions, and the progress checklist. Summary: MCP v4 = 29→9 tools; trader
skills get run-time liquidity (makes "not selling the pick" mechanical) then an
open-source curated twin repo; engine LLM-wiki docs distill; webapp video-led landing
(YouTube). Per-repo slices: `REPLAN-2026-07-17.md` at the root of gammarips-mcp,
gammarips-trader, gammarips-webapp. Sequence: trader-2A → MCP v4 → webapp + renames →
wiki (parallel) → ship day (video + landing + public repo together). Nothing started
as of 2026-07-17.

## Owner queue
- 🔴 **Rotate `POLYGON_API_KEY`** (07-06 leak incident; new Secret Manager version
  WITHOUT trailing newline via `printf %s`; redeploy every mounting service:
  gammarips-mcp, forward-paper-trader, enrichment-trigger, signal-notifier,
  win-tracker). Still pending as of 07-17.
- Record the morning-routine video (gates the landing ship) + the one-time
  securities-counsel consult (real money + on-camera + paid product).
- One real Stripe checkout test (pending since 07-07).
- X: unpin the 03-14 tweet, pin the distribution-stat draft, bio refresh
  (drafts: memory `project_x_revamp_2026_07_09`).
- Directory follow-ups: cursor.directory browser form; Glama claim (free, GitHub
  sign-in); PulseMCP (email hello@pulsemcp.com if the 07-14 routine reported absent).
- Gated opportunity backfill for scans 06-29/06-30
  (`backfill_opportunity_surface.py` dry-run → `--confirm`).

## Watch / dated checkpoints
- **07-20**: OAuth checkpoint — `mcp_analytics` for claude.ai-shaped demand →
  scope OAuth 2.1 build or keep holding.
- **~07-23**: `x_post_metrics` two-week read → decide which post slots live.
- **Mid-Aug**: re-run the post-06-12-era ITM check (needs ≥200 expired era rows).
- **08-17**: kill-switch — zero MCP trials → early reevaluation
  (**10-05**: zero paying subs → business reevaluation).
- Weekly: `mcp_analytics` metering readout. As of 07-17: zero external users
  (all 3 keys are the owner's; anon traffic = crawlers + one 07-11 paywall-bouncer).

## Open engineering (non-blocking)
- Substrate: 41 rows with `recommended_delta`=0.0 on ITM-at-scan contracts
  (missing-delta-as-zero, May–Jun); 7 pick rows with zero labels (NO_BARS).
- blog-generator: redeploy to pick up the shared-lib RETIRED_ALIASES; remove the
  seeded topic `whatsapp-group-tag-the-agent` from its schedule first.
- Engine repo branch `scorecard/life-distribution` carries UNCOMMITTED work:
  x-poster 07-09 changes + the 07-17 replan docs + this file's rewrite.
- Service-auth hardening not executed
  (`docs/DECISIONS/2026-07-02-service-auth-hardening.md`).
- RM-001b (bid/ask spread) BLOCKED on the quote-feed purchase — owner $ call.

## Live posture (pointers, not prose)
- Policy: V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + `CHEAT-SHEET.md`.
- Owner trades LIVE (Robinhood since 07-09, $1,004 → ~$825 at 07-17) — memory
  `capital-constraint` has the PDT/day-trade-limit analysis.
- Daily crons run end-to-end; no urgent engine action.
