# CLAUDE.md — GammaRips Engine

## Mission
GammaRips is an overnight options-flow **intelligence engine**. It scans the US options market for unusual activity, curates *hard* (anti-firehose) down to a tiny high-signal BULLISH pool, and surfaces each candidate's **opportunity surface** (realized MFE/MAE excursions) — profit *potential*, with the exit left as a free variable. This repo is the backend + research workspace behind that.

**Product & monetization (owner-locked 2026-07-02).** The human web UI is **completely free** — it is the SEO top-of-funnel. The monetized product is **MCP access** for bring-your-own-agent traders (the `gammarips-mcp` server, a **separate repo**). We sell **data + tools** as a data vendor — the curated pool, historical opportunity/outcome surfaces, and selection methodology — **not a return and not single-contract advice** (the whole-pool composite under a fixed exit is negative; the edge lives in *how* contracts are traded). The MCP exposes **primitives each user's agent reasons over to its own contract** (diffusion), never a pick-returning endpoint.

**Trading.** A live **V7.1 "Tilted GIGO"** paper cohort validates selection; the single daily tournament pick is the operator's **private** signal (kept off the public product to avoid liquidity-stampede + scalping optics). The engine surfaces good contracts; profitability depends on discretionary entry/exit (human or agent).

**Non-negotiables.** Leakage-safety is physics, not policy. Data-not-advice framing.

## Tech stack
Python 3.12 on Cloud Run, BigQuery + Firestore + GCS, Cloud Scheduler / Pub/Sub.
Read any service's `requirements.txt` + `deploy.sh` for the rest.
- **Data vendors:** Polygon (options/equity), FRED (VIX daily). FMP is legacy: its one remaining use is signal-notifier's earnings-calendar rail. Removed from forward-paper-trader (2026-04-08). Never used in enrichment-trigger or win-tracker.
- **Do NOT use:** FMP in forward-paper-trader (retired 2026-04-08), sklearn/XGBoost on N<500 datasets, any new data vendor without user approval

## Writing style — ASD-STE100 (Simplified Technical English)

All prose obeys ASD-STE100 Issue 9. Read the `ste100` skill
(user-level, `~/.claude/skills/ste100/`) before you write a document.
Two project nuances: code, SQL, identifiers, and quoted output are
verbatim (STE applies to prose only), and project domain terms are
technical nouns and stay as they are.

## Commands
Deploying anything: run the `/deploy-service` skill (checklist, secret-mount
and route facts live there, not here).

```bash
# Ledger health check (read-only, safe to run anytime)
python scripts/ledger_and_tracking/current_ledger_stats.py

# Cloud Scheduler status
gcloud scheduler jobs list --project=profitscout-fida8 --location=us-central1

# Cloud Run logs
gcloud run services logs read forward-paper-trader --project=profitscout-fida8 --region=us-central1 --limit=50

# Manual paper-trader trigger (dry run for a specific date)
curl -X POST https://forward-paper-trader-406581297632.us-central1.run.app/ \
  -H "Content-Type: application/json" -d '{"target_date": "2026-08-19"}'

# Manual IVR cache refresh
curl -X POST https://forward-paper-trader-406581297632.us-central1.run.app/cache_iv
```

## Read-first order
Before making meaningful changes, read:
1. `NEXT_SESSION_PROMPT.md` — live session handoff with current state, pre-committed hypotheses, and constraints
2. `docs/TRADING-STRATEGY.md` — canonical execution policy
3. `docs/ARCHITECTURE.md` — system map and data flow
4. `docs/DATA-CONTRACTS.md` — BQ schemas

Deeper context (read when relevant): `docs/DECISIONS/` (decision trail), `docs/EVAL-SYSTEM.md`, `docs/TESTING.md`, `docs/EXECUTION-RISK-GUIDELINES.md` (exit-certainty rules for live execution), `docs/research_reports/INTELLIGENCE_BRIEF.md`, `docs/research_reports/FINDINGS_LEDGER.md`.

## Cross-repo edits (MCP + webapp) — READ THIS FIRST
Much of the MCP and webapp work is driven from an engine session. **A sibling repo's
`CLAUDE.md` does NOT auto-load here** — context loads for the current directory and its
ancestors only. Editing those repos from this one means their rules are invisible unless
you go get them. Failure is silent: the edit looks fine and violates a locked rule.

**Before touching either, read its context file:**
- `../gammarips-mcp/CLAUDE.md` + its `SECURITY.md` (auth/tiering model)
- `../gammarips-webapp/CLAUDE.md` (positioning, forbidden claims, repo landmines)

The three that bite hardest if you skip the read:
1. **Webapp: pushing to `main` auto-deploys production** (Firebase App Hosting). Branch, then treat every merge as a ship. Gate public surfaces with `/ship` from `~/workspace`.
2. **No pick, anywhere.** The MCP exposes primitives and has no pick-returning endpoint; the site shows the POOL and must never regain a "today's pick" card, push, or endpoint.
3. **The webapp has a numbered forbidden-claims compliance list** (no expected return / win rate / "signals to follow" / selected-positive blended ROI). It is non-negotiable and it lives only in that repo. Any copy change goes through its `gammarips-copywriter` agent.

Separate repos means separate commits and separate pushes. Never `git add` across them.

## Current policy (summary)
**V7.1 "Tilted GIGO" is the live policy** ([[v7-1-tilted-gigo-live-policy]]: `policy_version='V7_1_TILTED_GIGO'`, cohort start = `LIVE_COHORT_START_DATE` in `signal-notifier/main.py` (2026-08-13 as of the 2026-08-12 reset, do not cache the value in docs)) = V6 bracket-tournament SELECTION + V7 same-day EXIT + the ".1" 60-day-momentum enrichment tilt. **The full policy is distilled into one-claim notes in [`docs/wiki/`](docs/wiki/)** — start at [`docs/wiki/_index/REGISTRY.md`](docs/wiki/_index/REGISTRY.md); each claim below is its own note so a fresh session can answer "what runs and why" from the wiki alone:
- Selection: [[bracket-tournament-selection]] · [[bullish-only-hard-gate]] · [[tourney-pool-cap-edge-rank]] · [[live-oi-floor]] · [[selection-gates-removed]]
- Exit: [[v7-gigo-same-day-exit]] (entry 10:00 ET / +40% TP / −30% stop / flat 15:45 ET, no trail, no overnight; V6 −60/+80/3-day is DEAD)
- Upstream funnel + rails: [[enrichment-definition]] · [[spread-gate-retired]] · [[earnings-exclusion-rail]] · [[regime-rail-vix-term]] · [[assert-no-leakage-gate]] · [[enrichment-cost-fix-topn-thinking-cap]]
- Data-contract / history: [[oi-volume-session-frozen-walled-off]] · [[pipeline-bug-hunt-2026-06-04]] · [[ledger-cohort-version-labels]]

The one-page operator view is [`CHEAT-SHEET.md`](CHEAT-SHEET.md). **Source of truth for execution policy** (over any wiki note or research doc): `docs/TRADING-STRATEGY.md` + `forward-paper-trader/main.py` + `signal-judge/app/agent.py` + `docs/DECISIONS/2026-06-04-bracket-tournament.md`.

## Ground rules
- NEVER hardcode API keys or secrets in source.
- NEVER create separate V-numbered tables or services. There is one pipeline with canonical names.
- NEVER add execution gates to the trader. Signal-quality gates live in `enrichment-trigger` and `signal-notifier`, not in `forward-paper-trader`. New gates need owner approval and evidence.
- ALWAYS update `docs/TRADING-STRATEGY.md` and add a `docs/DECISIONS/` note when changing execution policy.
- Treat `_archive/` (repo root) and `docs/archive/` as historical, not authoritative.
- Historical `docs/DECISIONS/` notes cite `.claude/rules/*.md` paths. Those files were retired 2026-07-31 and their content folded into this file (see Code invariants) and the `/deploy-service` skill. The citations are accurate for their dates; do not rewrite them.
- Prefer archival over deletion when cleaning old artifacts.
- Prefer Edit over Write. Do not create new docs unless a plan calls for it.
- Do not trust historical `PROMPT-*` docs or old research summaries as current spec.
- When touching ledger logic, keep cohort/version metadata explicit.
- Update `docs/research_reports/INTELLIGENCE_BRIEF.md` when a hypothesis is tested or resolved.
- Update `NEXT_SESSION_PROMPT.md` in place when work pauses — REFRESH, never append dated blocks; hard cap ~100 lines. Content that leaves it graduates: execution policy → `docs/DECISIONS/`, research → `FINDINGS_LEDGER.md`/`INTELLIGENCE_BRIEF.md`, durable facts + gotchas → auto-memory, everything else → `docs/archive/`.

## Code invariants (the non-obvious ones)
- `forward-paper-trader/benchmark_context.py` is deliberately non-blocking: every fetch returns `None` on failure. Do not add error-raising behavior.
- NEVER remove or rename benchmarking columns in ledger writes — downstream analysis depends on column stability.
- `enrichment-trigger` write path is atomic and schema-drift-safe: **never `autodetect`** (that broke the pick pipeline 2026-07-02).
- `scripts/research/` is FROZEN — it produced `signals_labeled_v1` and the bracket sweeps, and exists for reproducibility only. Do not modify it and do not rebuild or re-label `signals_labeled_v1`. New research writes against the live ledger (`forward_paper_ledger`).
- `scripts/ledger_and_tracking/`: `current_ledger_stats.py` is read-only monitoring — no filter ranking, winner searches, or gate tuning in it. `create_*`/`backfill_*` are already-executed one-shots; do not re-run without explicit owner approval. Any new EDA script must be read-only against BigQuery.

## Subagents
Four in `.claude/agents/` (`gammarips-engineer`, `gammarips-researcher`, `gammarips-review`,
`gammarips-seo`). Routing and mandates live in each agent's own description — read those,
not a summary here. Tool scoping enforces the read-only ones.

## Repo map
| Directory | Purpose |
|---|---|
| `forward-paper-trader/` | Production paper-trading (no trader-side filters, writes to `forward_paper_ledger`). Cloud Run, routes in `main.py`. Also writes an **isolated research shadow** (`paper_shadow_topscore`: top-`overnight_score` deterministic pick vs the tournament pick, identical mechanics, best-effort) — NEVER surfaced to the Scorecard or website; see `docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md`. |
| `enrichment-trigger/` | Enrichment pipeline (score≥4, UOA>$500K, edge-ranked to top-50 BULLISH; spread gate retired; writes `overnight_signals_enriched`). Atomic schema-drift-safe write path — **never `autodetect`** (that broke the pick pipeline 2026-07-02). Instrumented via `libs/trace_logger`. |
| `signal-judge/` | The bracket-tournament picker (`tournament_v1` family, current prompt version pinned in `signal-judge/deploy.sh`; `gemini-3.1-pro-preview`). IAM-locked; invoked by `signal-notifier` (the tournament is the SELECTION layer, unchanged under V7.1). |
| `signal-notifier/` | Applies the two safety rails + the two-tier liquidity floor (early prints, then live OI; fail-closed, a dropped candidate never returns — [[live-oi-floor]]), runs the tournament, writes `todays_pick`, emails operator/subscribers. Owns the cohort/stats (`LIVE_COHORT_START_DATE`, `cohort_stats/current`). |
| `agent-arena/` | **DEAD (deprecated 2026-05-04)** — no eval/fixes/new work; if touched, propose deletion, not enhancement. |
| `gammarips-eval/` | LLM eval service — monitoring-only, non-gating. See `docs/EVAL-SYSTEM.md`. |
| `x-poster/` | **ADK multi-agent X publisher for @gammarips** (since 2026-04-24). Planner→Writer→Reviewer→EscalationChecker LoopAgent + Publisher. 7 post types behind `POST /post`. Nano Banana editorial image gen + PIL logo composite. Cloud Run, DRY_RUN=false in prod (LIVE posting since 2026-04-27). Pass per-request `dry_run=true` for a safe test. See `x-poster/DESIGN_SPEC.md`. |
| `blog-generator/` | **ADK multi-agent blog writer** (since 2026-04-24). Same shape as x-poster, writes Firestore `blog_posts/{slug}` for webapp `/blog` rendering. Weekly Mon 05:00 ET cron. **DEPLOYED** (live since 2026-06-01; rev `blog-generator-00023+`). See `blog-generator/DESIGN_SPEC.md`. |
| `gammarips-mcp` (**SEPARATE REPO**) | **The monetized product** — MCP server for bring-your-own-agent access. Exposes data + tool primitives (curated pool, opportunity/outcome surfaces, methodology) each agent reasons over to its OWN contract; **never a pick-returning endpoint**. The same-day pick tools were removed in the V3 surface (2026-07-02). OAuth AS on gammarips.com + the auth-required `/pro` path shipped and went live 2026-08-19. Deploy state is tracked in that repo. |
| `libs/trace_logger/` | Shared BQ trace logger, vendored into each service by `deploy.sh` |
| `libs/gammarips_content/` | **Shared content lib** (since 2026-04-24). brand constants (real hex codes + fonts + voice markers), compliance rubric + canonicalizer, tweepy + firestore + MCP helpers. Vendored into x-poster + blog-generator at deploy time. |
| `win-tracker/` | Post-trade outcome tracking. **X posting moved to x-poster 2026-04-24** — win-tracker now writes signal_performance only. |

Unlisted dirs do what their names say; `scripts/` rules are in **Code invariants**.

## Definition of Done
**The 30-day out-of-sample gate is RETIRED (owner call, 2026-08-19). It is DECIDED. Never
re-raise it in any framing, including as a reminder, a risk note, or a checklist row.**
It blocked shipping and bought nothing.

`gammarips-review` is OPTIONAL and owner-invoked. It is not automatic and it does not gate
a deploy. Ship, watch the logs, roll back with an env var.
