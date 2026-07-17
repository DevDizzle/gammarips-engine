# 2026-07-17 — Simplification Replan (MASTER, 4 plans)

**Status: RATIFIED by owner 2026-07-17. This is the plan of record.** Slice files with
per-repo checklists: `gammarips-mcp/REPLAN-2026-07-17.md`, `gammarips-trader/REPLAN-2026-07-17.md`,
`gammarips-webapp/REPLAN-2026-07-17.md`. Memory digest: `project_simplification_replan_2026_07_17`
(engine-project auto-memory).

## Vision (owner, 2026-07-17)
Promo = a video of Evan running the morning routine, his agent selecting a contract at
run time, and him buying it on Robinhood. Process, not profits. No claims. $39/mo = data
access, unchanged. **We are NOT selling the pick** — diffusion must be *mechanical*:
selection conditioned on run-time liquidity so two runs at different times genuinely
differ. The trading harness goes open source so anyone can clone the exact workflow;
the harness is free, the data (MCP key) is paid.

## Decisions locked 2026-07-17
- **9-tool MCP v4 map ratified** (below).
- **Trader wiki/findings: ALL can go public** — owner explicitly waived the hold-back
  ("it can all go public"). Personal journals/dollar amounts still excluded (privacy, not IP).
- **Video hosting: YouTube.**
- Open-source approach: **curated public twin repo**, NOT scrub-in-place (private repo
  keeps being the operator's live instance; git history there is secrets-clean but
  contains personal trading data).
- OPEN owner item: one securities-counsel consult before the video ships while charging
  subs (real money + on-camera + paid product = the full fact pattern; posture is good —
  run-time personal selection, not a published signal — but confirm).

## Context snapshot (2026-07-17, verify before acting)
- Zero external MCP users: all 3 API keys are Evan's; 64 anon calls = crawlers + one
  07-11 paywall-bouncer. Breaking the MCP surface is free right now.
- Owner trades LIVE (Robinhood, started 07-09, $1,004 → ~$825 at 07-17). See memory
  `capital-constraint` (retired constraint + PDT analysis).
- Kill-switch clock: zero trials by 2026-08-17 → early reevaluation.

## Sequence
1. **Plan 2A** — trader skill upgrade (run-time data). ~0.5 day. Start immediately.
2. **Plan 1** — MCP v4 consolidation (freezes tool names). ~2 days.
3. **Plan 4 (steps 1-3)** + **Plan 2B rename pass** — webapp skeleton + trader/public
   repo written against v4 names. ~1.5 days.
4. **Plan 3** — engine wiki distill. ~2 days, parallelizable with all of the above.
5. **Ship moment**: owner delivers video → Plan 4 ships (landing + video), Plan 2B repo
   goes public same day. Then LET IT SIT; demand levers (ads probe, directories) run.

---

## Plan 1 — MCP v4: 29 tools → 9 (repo: gammarips-mcp)

Ratified tool map:

| v4 tool | tier | absorbs |
|---|---|---|
| `get_pool` | free preview / pro full | get_overnight_signals, get_enriched_signals, get_pool_features, get_freemium_preview |
| `get_signal` | pro | get_signal_detail, get_earnings_window |
| `get_liquidity` | pro | get_pool_liquidity, get_contract_snapshot |
| `query_outcomes` | pro | query_outcomes, get_outcome_summary, get_opportunity_surface, get_harvest_curve, estimate_exit_rule, get_signal_performance, get_win_rate_summary, get_position_history, get_historical_performance (as `view=` modes) |
| `replay_contract` | pro | get_contract_marks (`granularity="day"\|"minute"`) |
| `get_regime_context` | free | unchanged |
| `get_market_calendar_status` | free | get_available_dates |
| `get_playbook` | free | list_playbooks (no-arg lists), get_signal_explainer field dict + get_enriched_signal_schema become playbook pages |
| `get_daily_report` | free | get_report_list (no date arg lists recent) |

KILLED: `web_search`. Auth/metering/rate-limits UNTOUCHED (paywall verified working).

Steps (file-level detail in the repo slice file): hoist shared BQ/Firestore clients +
table constants → build 9 merged handlers → rewrite `_ALL_TOOLS` + anon set + 3 prompts →
sync mcp.json/README/SECURITY.md + `SERVER_VERSION` 4.0.0 → fix tests → gammarips-review →
deploy → republish registry listing → live keyed verification.

## Plan 2 — Trader: upgrade + open-source twin (repo: gammarips-trader)

**2A (first, private repo):** `/morning-pool` + `/select-contract` gain run-time data:
`get_pool_liquidity` shortlist refresh, live delta/moneyness band checks at decision
time, `get_earnings_window` (drop web_search interim except `not_covered_by_plan`),
run timestamp in journal, afternoon runs default to no-trade. This is what makes
"not selling the pick" mechanically true. Written against v3 names; rename pass after Plan 1.

**2B (public twin, e.g. `DevDizzle/gammarips-harness`):** ships CLAUDE.md (firewall +
`~/gammarips-engine` clauses removed), 5 skills + 2 agents (same edits), `scripts/lint.py`
(portable as-is), full wiki (`WIKI-SCHEMA.md` + ALL findings/literature notes — owner
cleared them public; strip `Source:` lines pointing at private engine paths), journal
`_TEMPLATE.md` + one synthetic example, `.mcp.json` with public URL + `${GAMMARIPS_MCP_KEY}`
pattern, README quickstart ("subscribe → create key at gammarips.com/account → export →
run /morning-pool"). EXCLUDE: the 5 real journals (real capital, fills, the 07-15
firewall-breach entry), doctrine personal risk numbers, GAP-LOG.md, MCP-ROADMAP.md,
ENGINE-MCP-PROMPT.txt, KEY-SETUP.txt (rewrite), GCP project ids/`owner-evan`.
DoD: clean machine + fresh key completes one full morning loop. Publish with the video.

## Plan 3 — Engine LLM wiki + docs distill (repo: gammarips-engine)

Adopt the trader `WIKI-SCHEMA.md` note format (Status/Type/Tag/Exit-context/Source/Date +
one-claim body) into `docs/wiki/` + `_index/`. Distill priority: (1) CLAUDE.md "Current
policy" 5.5KB paragraph → ~10-15 atomic notes + 10-line pointer section; (2)
INTELLIGENCE_BRIEF (H1-H21 claims) + FINDINGS_LEDGER → notes, files stay canonical but thin;
(3) DECISIONS corpus (73 files, regular `## Finding`/`## Decision` shape) → fan out to
subagents, notes cite source decision files, DECISIONS/ untouched as provenance;
(4) NEXT_SESSION_PROMPT.md → true handoff — **DONE EARLY 2026-07-17** (append-era file
archived to `docs/archive/NEXT_SESSION_PROMPT-append-era-2026-07-17.md`, fresh ~70-line
handoff written, refresh-not-append contract encoded in
`.claude/rules/next-session-prompt.md` + CLAUDE.md ground rule); (5) archive sweep
to `docs/archive/`: all EXEC-PLANS (incl. this file when executed), EVAL-TURN-ON.md,
LAUNCH-DAY-2026-04-21.md, V1/V5.4-era research reports, research_reports/handoffs/.
Archive, never delete. DoD: fresh session answers "live policy and why" from CLAUDE.md +
wiki alone; every old-paragraph claim resolves to exactly one note.

## Plan 4 — Webapp: video-led landing (repo: gammarips-webapp)

On a `landing/*` branch (main auto-deploys — PR only): (1) hero → YouTube video slot
(poster until asset exists) + one line ("I trade my own tool every morning. $39/mo gets
your agent the same data.") + existing 2 CTAs; keep curation funnel, pool snapshot,
honesty section, FAQ; tighten rest per 07-08 copy rule (8th-grade sentences, no em
dashes). (2) Kill literal-string drift: `TOOL_COUNT` + `PRICE` constants in `src/lib/`,
imported by the ~15 files each that hardcode "23 tools"/"$39" (incl. public/llms.txt,
public/mcp.json, public/skill.md, .well-known/ai-plugin.json, mailgun.ts). (3) /developers
+ agent-discovery files rewritten to the 9-tool v4 surface (AFTER Plan 1 freezes names).
(4) Video: YouTube embed (owner-decided; no CSP in repo, nothing blocks it; avoids the
maxInstances:1 self-hosting problem). Framing: personal process, not a signal to follow,
same disclaimer treatment as agent-demo. (5) /ship gate (content-reviewer + claim-skeptic)
before merge. DoD: PR merged, video live, all counts/prices resolve from constants.

---

## Progress checklist (update in place)
- [ ] 2A trader skills run-time upgrade
- [ ] 1 MCP v4 built + tested locally
- [ ] 1 MCP v4 reviewed (gammarips-review) + deployed + registry republished
- [ ] 4.1-4.2 webapp skeleton branch + constants
- [ ] 2B public twin repo built (private, pre-publish)
- [ ] 2A' + 4.3 rename passes to v4 names
- [ ] 3 engine wiki distill (CLAUDE.md ¶ → notes → NSP rewrite → archive sweep)
- [ ] OWNER: video recorded + uploaded to YouTube
- [ ] OWNER: counsel consult
- [ ] SHIP: landing PR merged + harness repo public (same day)
