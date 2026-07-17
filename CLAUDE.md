# CLAUDE.md — GammaRips Engine

## Mission
GammaRips is an overnight options-flow **intelligence engine**. It scans the US options market for unusual activity, curates *hard* (anti-firehose) down to a tiny high-signal BULLISH pool, and surfaces each candidate's **opportunity surface** (realized MFE/MAE excursions) — profit *potential*, with the exit left as a free variable. This repo is the backend + research workspace behind that.

**Product & monetization (owner-locked 2026-07-02).** The human web UI is **completely free** — it is the SEO top-of-funnel. The monetized product is **MCP access** for bring-your-own-agent traders (the `gammarips-mcp` server, a **separate repo**). We sell **data + tools** as a data vendor — the curated pool, historical opportunity/outcome surfaces, and selection methodology — **not a return and not single-contract advice** (the whole-pool composite under a fixed exit is negative; the edge lives in *how* contracts are traded). The MCP exposes **primitives each user's agent reasons over to its own contract** (diffusion), never a pick-returning endpoint.

**Trading.** A live **V7.1 "Tilted GIGO"** paper cohort validates selection; the single daily tournament pick is the operator's **private** signal (kept off the public product to avoid liquidity-stampede + scalping optics). The engine surfaces good contracts; profitability depends on discretionary entry/exit (human or agent).

**Non-negotiables.** Leakage-safety is physics, not policy. Data-not-advice framing. `gammarips-review` before any public data-exposure change.

## Tech stack
- **Language:** Python 3.12
- **Runtime:** GCP Cloud Run (source deploy via `gcloud run deploy --source=.`)
- **Data:** BigQuery (canonical storage), Firestore (eval reports), GCS (ticker universe)
- **APIs:** Polygon (options/equity data), FRED (VIX daily). FMP is legacy — still used by enrichment/win-tracker but **removed from forward-paper-trader**.
- **Framework:** Flask + Gunicorn per service
- **Research:** pandas, pandas-ta, matplotlib, mplfinance
- **AI/LLM:** google-genai (Gemini)
- **Orchestration:** Cloud Scheduler (cron triggers), Pub/Sub
- **Do NOT use:** FMP in forward-paper-trader (retired 2026-04-08), sklearn/XGBoost on N<500 datasets, any new data vendor without user approval

## Commands
```bash
# Deploy a service (run from the service directory)
cd forward-paper-trader && bash deploy.sh
cd enrichment-trigger && bash deploy.sh
cd signal-notifier && bash deploy.sh

# Ledger health check (read-only, safe to run anytime)
python scripts/ledger_and_tracking/current_ledger_stats.py

# Cloud Scheduler status
gcloud scheduler jobs list --project=profitscout-fida8 --location=us-central1

# Cloud Run logs
gcloud run services logs read forward-paper-trader --project=profitscout-fida8 --region=us-central1 --limit=50

# Manual V4 paper-trader trigger (dry run for a specific date)
curl -X POST https://forward-paper-trader-406581297632.us-central1.run.app/ \
  -H "Content-Type: application/json" -d '{"target_date": "2026-04-15"}'

# Manual IVR cache refresh
curl -X POST https://forward-paper-trader-406581297632.us-central1.run.app/cache_iv
```

## Read-first order
Before making meaningful changes, read:
1. `NEXT_SESSION_PROMPT.md` — live session handoff with current state, pre-committed hypotheses, and constraints
2. `docs/TRADING-STRATEGY.md` — canonical execution policy
3. `docs/ARCHITECTURE.md` — system map and data flow
4. `docs/DATA-CONTRACTS.md` — BQ schemas

Deeper context (read when relevant): `docs/DECISIONS/` (decision trail), `docs/EVAL-SYSTEM.md`, `docs/TESTING.md`, `docs/research_reports/INTELLIGENCE_BRIEF.md`, `docs/research_reports/FINDINGS_LEDGER.md`.

## Current policy (summary)
**V7.1 "Tilted GIGO" is the live policy** (`policy_version='V7_1_TILTED_GIGO'`, `LIVE_COHORT_START_DATE='2026-06-26'`) = V6 bracket-tournament SELECTION + V7 same-day EXIT + the ".1" 60-day-momentum enrichment tilt. **The full policy is distilled into one-claim notes in [`docs/wiki/`](docs/wiki/)** — start at [`docs/wiki/_index/REGISTRY.md`](docs/wiki/_index/REGISTRY.md); each claim below is its own note so a fresh session can answer "what runs and why" from the wiki alone:
- Selection: [[bracket-tournament-selection]] · [[bullish-only-hard-gate]] · [[tourney-pool-cap-edge-rank]] · [[live-oi-floor]] · [[selection-gates-removed]]
- Exit: [[v7-gigo-same-day-exit]] (entry 10:00 ET / +40% TP / −30% stop / flat 15:45 ET, no trail, no overnight; V6 −60/+80/3-day is DEAD)
- Upstream funnel + rails: [[enrichment-definition]] · [[spread-gate-retired]] · [[earnings-exclusion-rail]] · [[regime-rail-vix-term]] · [[assert-no-leakage-gate]] · [[enrichment-cost-fix-topn-thinking-cap]]
- Data-contract / history: [[oi-volume-session-frozen-walled-off]] · [[pipeline-bug-hunt-2026-06-04]] · [[ledger-cohort-version-labels]]

The one-page operator view is [`CHEAT-SHEET.md`](CHEAT-SHEET.md). **Source of truth for execution policy** (over any wiki note or research doc): `docs/TRADING-STRATEGY.md` + `forward-paper-trader/main.py` + `signal-judge/app/agent.py` + `docs/DECISIONS/2026-06-04-bracket-tournament.md`.

## Ground rules
- NEVER hardcode API keys or secrets in source.
- NEVER create separate V-numbered tables or services. There is one pipeline with canonical names.
- NEVER add execution gates to the trader. Signal-quality gates live in `enrichment-trigger` and `signal-notifier`, not in `forward-paper-trader`. Phase 2 feature discovery is the only path to new gates.
- ALWAYS update `docs/TRADING-STRATEGY.md` and add a `docs/DECISIONS/` note when changing execution policy.
- Treat `_archive/`, `docs/archive/`, and `docs/research_reports/_archive/` as historical, not authoritative.
- Prefer archival over deletion when cleaning old artifacts.
- Prefer Edit over Write. Do not create new docs unless a plan calls for it.
- Do not trust historical `PROMPT-*` docs or old research summaries as current spec.
- When touching ledger logic, keep cohort/version metadata explicit.
- Update `NEXT_SESSION_PROMPT.md` in place when work pauses — REFRESH, never append dated blocks; hard cap ~100 lines; see `.claude/rules/next-session-prompt.md` for graduation paths.

## Subagents
Three project-specific subagents in `.claude/agents/`:
- **`gammarips-engineer`** — code cleanup, deployment fixes, BQ integration. Use for implementation.
- **`gammarips-researcher`** — backtests, cohort analysis, hypothesis testing. Read-only by default.
- **`gammarips-review`** — audits for lookahead bias, data leakage, unsafe execution. Read-only. **ALWAYS invoke before any deploy/ship action.**

## Repo map
| Directory | Purpose |
|---|---|
| `forward-paper-trader/` | Production paper-trading (no trader-side filters, writes to `forward_paper_ledger`). Cloud Run, two endpoints. Also writes an **isolated research shadow** (`paper_shadow_topscore`: top-`overnight_score` deterministic pick vs the tournament pick, identical mechanics, best-effort) — NEVER surfaced to the Scorecard or website; see `docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md`. |
| `enrichment-trigger/` | Enrichment pipeline (score≥4, UOA>$500K, edge-ranked to top-50 BULLISH; spread gate retired; writes `overnight_signals_enriched`). Atomic schema-drift-safe write path — **never `autodetect`** (that broke the pick pipeline 2026-07-02). Instrumented via `libs/trace_logger`. |
| `signal-judge/` | The bracket-tournament picker (`tournament_v1`, `gemini-3.1-pro-preview`). IAM-locked; invoked by `signal-notifier` (the tournament is the SELECTION layer, unchanged under V7.1). |
| `signal-notifier/` | Applies the two safety rails + live-OI floor, runs the tournament, writes `todays_pick`, emails operator/subscribers. Owns the cohort/stats (`LIVE_COHORT_START_DATE`, `cohort_stats/current`). |
| `agent-arena/` | **DEAD (deprecated 2026-05-04)** — no eval/fixes/new work; if touched, propose deletion, not enhancement. |
| `overnight-report-generator/` | Gemini editorial synthesis (instrumented) |
| `gammarips-eval/` | LLM eval service — monitoring-only, non-gating. See `docs/EVAL-SYSTEM.md`. |
| `x-poster/` | **ADK multi-agent X publisher for @gammarips** (since 2026-04-24). Planner→Writer→Reviewer→EscalationChecker LoopAgent + Publisher. 7 post types behind `POST /post`. Nano Banana editorial image gen + PIL logo composite. Cloud Run, DRY_RUN=true default. See `x-poster/DESIGN_SPEC.md`. |
| `blog-generator/` | **ADK multi-agent blog writer** (since 2026-04-24). Same shape as x-poster, writes Firestore `blog_posts/{slug}` for webapp `/blog` rendering. Weekly Mon 05:00 ET cron. **DEPLOYED** (live since 2026-06-01; rev `blog-generator-00023+`). See `blog-generator/DESIGN_SPEC.md`. |
| `gammarips-mcp` (**SEPARATE REPO**) | **The monetized product** — MCP server for bring-your-own-agent access. Exposes data + tool primitives (curated pool, opportunity/outcome surfaces, methodology) each agent reasons over to its OWN contract; **never a pick-returning endpoint**. Hardened but single-tenant today (built for the sandboxed bot); multi-tenant productization is the current build. Fix the unauth `get_todays_pick` leak first. |
| `libs/trace_logger/` | Shared BQ trace logger, vendored into each service by `deploy.sh` |
| `libs/gammarips_content/` | **Shared content lib** (since 2026-04-24). brand constants (real hex codes + fonts + voice markers), compliance rubric + canonicalizer, tweepy + firestore + MCP helpers. Vendored into x-poster + blog-generator at deploy time. |
| `win-tracker/` | Post-trade outcome tracking. **X posting moved to x-poster 2026-04-24** — win-tracker now writes signal_performance only. |
| `src/`, `overnight-scanner/` | Scanner logic |
| `scripts/research/` | Frozen research scripts (do not modify) |
| `scripts/ledger_and_tracking/` | Ledger maintenance and EDA |
| `backtesting_and_research/` | Exploratory research code |
| `docs/` | Authoritative project docs |

## G-Stack governance
This project enforces a strict gated workflow to prevent algorithmic trading errors:

1. **Personas** — load the relevant subagent from `.claude/agents/` when the work matches its mandate.
2. **Definition of Done** — NEVER deploy a new trading strategy to live execution UNLESS it has passed mandatory 30-day out-of-sample testing on `forward-paper-trader` AND has been audited by `gammarips-review` for lookahead bias and data leakage. Workflow defined in `docs/ARCHITECTURE.md`.
