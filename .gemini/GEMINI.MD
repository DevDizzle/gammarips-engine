# GEMINI.MD — GammaRips Engine

> **Sibling file:** `CLAUDE.md` (repo root). Keep these two in lockstep.

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
```

## Read-first order
Before making meaningful changes, read:
1. `NEXT_SESSION_PROMPT.md` — live session handoff with current state, pre-committed hypotheses, and constraints
2. `docs/TRADING-STRATEGY.md` — canonical execution policy
3. `docs/ARCHITECTURE.md` — system map and data flow
4. `docs/DATA-CONTRACTS.md` — BQ schemas

Deeper context (read when relevant): `docs/DECISIONS/` (decision trail), `docs/EVAL-SYSTEM.md`, `docs/TESTING.md`, `docs/research_reports/INTELLIGENCE_BRIEF.md`, `docs/research_reports/FINDINGS_LEDGER.md`.

## Current policy (summary)
**V6 "Tournament" is the only active strategy** (launched 2026-06-04; V5.4 retired same day, `forward_paper_ledger` TRUNCATED — 13 flat closes wiped, avg 0.0%; `policy_version='V6_TOURNAMENT'`). One signal per day or none, picked by a **randomized bracket tournament over ALL enriched signals (no selection gates)** at the `signal-judge` Cloud Run service: 3 independent brackets, each shuffles the pool into batches of ≤10 → top-2 advance → 94→20→4→1; the **consensus** winner across the 3 brackets is the pick (3/3=high, 2/3=medium, 1/3=low). Dead-simple prompt ("make money buying a single option, sell for profit in 3 days") + the daily report for context + per-contract JSON; **no memory, no rubric, no weights** (`tournament_v1`, version 7, `gemini-3.1-pro-preview`; see `docs/DECISIONS/2026-06-04-bracket-tournament.md`). **Fail-closed on error — no fallback.** Trader mechanics unchanged: entry 10:00 ET day-1, −60% option stop, +80% option target, 3-day hold, exit 15:50 ET day-3. Stop wins over target on ambiguous bars (conservative). **Selection gates REMOVED 2026-06-04** — all enriched signals reach the tournament (the old `signal-notifier` moneyness/OI/vol/DTE/V-OI + active-days gates + the daily-cadence fallback are GONE; they choked real winners on stale scan-time data). UPSTREAM only: `enrichment-trigger` defines "enriched" (`overnight_score >= 4` [floor; EV inverts at >=7], `directional UOA > $500K`, all directions; SPREAD GATE RETIRED 2026-06-05 — this Polygon plan serves no options quotes, spread is permanently NULL, `_best_contract` now prices off last-trade/day-close; see `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`); `signal-notifier` keeps exactly two SAFETY rails — no earnings during the 3-day hold (IV crush) + regime fail-closed (`VIX <= VIX3M`). Every candidate is `assert_no_leakage`-checked before the LLM. **2026-06-04 pipeline bug-hunt (`docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`): 13 silent data bugs fixed — root cause was `polygon_client` substituting day low/high for missing bid/ask → fake/0% spreads on ~43% of picks (now NULL when unquoted); divergence-flip scoring reordered before conviction signals (was suppressing ~87% of the best setups); technicals lookahead bounded to `scan_date`; stale volume/OI stripped from the judge prompt; liquidity-aware contract selection; trader fill-realism. DEFERRED (need point-in-time data): OI + volume are still session-frozen snapshots, walled off from the judge.** The one-page operator view is `CHEAT-SHEET.md`. Service/table context: `docs/GLOSSARY.md`. Model→function registry: `docs/MODELS.md`. Source of truth for execution policy: `docs/TRADING-STRATEGY.md` + `forward-paper-trader/main.py` + `signal-judge/app/agent.py` + `docs/DECISIONS/2026-06-04-bracket-tournament.md`.

## Ground rules
- NEVER hardcode API keys or secrets in source.
- NEVER create separate V-numbered tables or services. There is one pipeline with canonical names.
- NEVER add execution gates to the trader. Signal-quality gates live in `enrichment-trigger` and `signal-notifier`, not in `forward-paper-trader`. Phase 2 feature discovery is the only path to new gates.
- ALWAYS update `docs/TRADING-STRATEGY.md` and add a `docs/DECISIONS/` note when changing execution policy.
- Treat `_archive/`, `docs/archive/`, and `docs/research_reports/_archive/` as historical, not authoritative.
- Prefer archival over deletion when cleaning old artifacts.
- Do not trust historical `PROMPT-*` docs or old research summaries as current spec.
- When touching ledger logic, keep cohort/version metadata explicit.
- Update `NEXT_SESSION_PROMPT.md` in place when work pauses.

## Repo map
| Directory | Purpose |
|---|---|
| `forward-paper-trader/` | Production paper-trading (no trader-side filters, writes to `forward_paper_ledger`). Cloud Run, two endpoints. Also writes an **isolated research shadow** (`paper_shadow_topscore`: top-`overnight_score` deterministic pick vs the tournament pick, identical mechanics, best-effort) — NEVER surfaced to the Scorecard or website; see `docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md`. |
| `enrichment-trigger/` | Enrichment pipeline (score>=1, spread<=10%, UOA>$500K, writes to `overnight_signals_enriched`). Instrumented via `libs/trace_logger`. |
| `agent-arena/` | Multi-model debate / signal ranking (instrumented) |
| `overnight-report-generator/` | Gemini editorial synthesis (instrumented) |
| `gammarips-eval/` | LLM eval service — monitoring-only, non-gating. See `docs/EVAL-SYSTEM.md`. |
| `libs/trace_logger/` | Shared BQ trace logger, vendored into each service by `deploy.sh` |
| `win-tracker/` | Post-trade outcome tracking |
| `src/`, `overnight-scanner/` | Scanner logic |
| `scripts/research/` | Frozen research scripts (do not modify) |
| `scripts/ledger_and_tracking/` | Ledger maintenance and EDA |
| `backtesting_and_research/` | Exploratory research code |
| `docs/` | Authoritative project docs |

## G-Stack governance

This project enforces a strict role-based, gated workflow to prevent algorithmic trading errors.

1. **Active Personas**: Assume one of the following personas when instructed, loading their specific mandates from `.gemini/roles/`:
   - `gammarips-engineer`: Lead execution engineer.
   - `gammarips-researcher`: Quantitative researcher.
   - `gammarips-review`: Paranoid Risk Manager.

2. **Definition of Done**: NEVER deploy a new trading strategy to live execution UNLESS it has passed mandatory 30-day out-of-sample testing on `forward-paper-trader` AND has been audited by `gammarips-review` for lookahead bias and data leakage. Workflow defined in `docs/ARCHITECTURE.md`.
