# Next Session Prompt

> **Contract (owner call 2026-07-17):** this file is the CURRENT STATE for the next
> session, not a log. REFRESH in place — replace stale content, never append dated
> blocks. Hard cap ~100 lines. Durable facts graduate to auto-memory; policy changes
> to `docs/DECISIONS/`; research to the findings ledger. Rules in `CLAUDE.md`.
> Keep the section shape below: Active workstream · Owner queue · Watch/dated
> checkpoints · Open engineering · Live posture. Pointers over prose.

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
1. Liquid-universe funnel: Phase 0 DONE 08-20. Chain rebuild was RUNNING in the
   background (`cache/lu_chain_run.log`, manifest-resumable: rerun
   `2026-08-20_liquid_universe_screen_phase.py chain`). Then
   `2026-08-20_liquid_universe_compute.py all`. Stops at the outcome-pull budget.
2. Pool-vs-benchmark: sampler built, 3-date dry run = the §9 balance gate
   (`cache/s2_dryrun.log`), then the 87-date run + `control_minute_paths`.
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
  2026-08-21 cohort pin.
- Compliance substring misfires (`'for you'` hit the relaunch email on "for your
  agent"; `libs/gammarips_content/.../compliance.py`).
- Organic Social halved (67→35 sessions/28d); x-poster lane needs its own look.
- Small: restore `blog_posts/building-options-flow-pipeline-ai-agents` to
  `published`; lx6bb stray docs call; Cursor listing v4; X pins/bio; Stripe MCP.

## Watch / dated checkpoints
- 🔴 Attribution test checkout (run-sheet item 1) gates Show HN.
- First picks under `PRINT_FLOOR_MIN=25`: thinner slate expected, a
  `no_liquid_candidates` no-pick day is correct.
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
- V7.1 Tilted GIGO — `docs/TRADING-STRATEGY.md` + wiki `REGISTRY.md` + `CHEAT-SHEET.md`.
  Cohort start: `LIVE_COHORT_START_DATE` in `signal-notifier/main.py` (never hardcode).
- Owner trades LIVE (Robinhood since 07-09). Daily crons run; MCP paywall ENFORCE.
- Health: operator digest 07:15 ET weekdays; SEO auth via the `seo-auth` skill.
