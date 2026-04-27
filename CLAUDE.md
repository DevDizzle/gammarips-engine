# CLAUDE.md — GammaRips Engine

> **Sibling file:** `.gemini/GEMINI.MD`. Keep these two in lockstep — when you change one, update the other.

## Mission
GammaRips Engine is the active backend and research workspace for overnight options-flow scanning, enrichment, reporting, paper execution, and performance tracking. The current operating goal is to validate and improve the forward paper-trading policy so it can become a reliable income-supporting engine.

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
cd agent-arena && bash deploy.sh

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
**V5.3 "Target 80" is the only active strategy** (adopted 2026-04-17, V4 retired same day, V3 retired 2026-04-16). One signal per day or none. Entry 10:00 ET day-1, −60% option stop, +80% option target, 3-day hold, exit 15:50 ET day-3. Stop wins over target on ambiguous bars (conservative). The trader has no filters; signal-quality gates live in `enrichment-trigger` (`overnight_score >= 1 AND spread <= 10% AND directional UOA > $500K`) and `signal-notifier` (`V/OI > 2`, `moneyness 5-15% OTM`, `VIX <= VIX3M`, `LIMIT 1`). The one-page operator view is [`CHEAT-SHEET.md`](CHEAT-SHEET.md). Service/table context: [`docs/GLOSSARY.md`](docs/GLOSSARY.md). Source of truth for execution policy: `docs/TRADING-STRATEGY.md` + `forward-paper-trader/main.py` + `docs/DECISIONS/2026-04-17-v5-3-target-80.md`.

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
- Update `NEXT_SESSION_PROMPT.md` in place when work pauses.

## Subagents
Three project-specific subagents in `.claude/agents/`:
- **`gammarips-engineer`** — code cleanup, deployment fixes, BQ integration. Use for implementation.
- **`gammarips-researcher`** — backtests, cohort analysis, hypothesis testing. Read-only by default.
- **`gammarips-review`** — audits for lookahead bias, data leakage, unsafe execution. Read-only. **ALWAYS invoke before any deploy/ship action.**

## Repo map
| Directory | Purpose |
|---|---|
| `forward-paper-trader/` | Production paper-trading (no trader-side filters, writes to `forward_paper_ledger`). Cloud Run, two endpoints. |
| `enrichment-trigger/` | Enrichment pipeline (score>=1, spread<=10%, UOA>$500K, writes to `overnight_signals_enriched`). Instrumented via `libs/trace_logger`. |
| `agent-arena/` | Multi-model debate / signal ranking (instrumented) |
| `overnight-report-generator/` | Gemini editorial synthesis (instrumented) |
| `gammarips-eval/` | LLM eval service — monitoring-only, non-gating. See `docs/EVAL-SYSTEM.md`. |
| `x-poster/` | **ADK multi-agent X publisher for @gammarips** (since 2026-04-24). Planner→Writer→Reviewer→EscalationChecker LoopAgent + Publisher. 7 post types behind `POST /post`. Nano Banana editorial image gen + PIL logo composite. Cloud Run, DRY_RUN=true default. See `x-poster/DESIGN_SPEC.md`. |
| `blog-generator/` | **ADK multi-agent blog writer** (since 2026-04-24). Same shape as x-poster, writes Firestore `blog_posts/{slug}` for webapp `/blog` rendering. Weekly Mon 05:00 ET cron. Not yet deployed; blocked on dangling-state-ref fix. See `blog-generator/DESIGN_SPEC.md`. |
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
