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
**V6 "Tournament" is the only active strategy** (launched 2026-06-04; V5.4 retired same day, `forward_paper_ledger` TRUNCATED — 13 flat closes wiped, avg 0.0%; `policy_version='V6_TOURNAMENT'`). One signal per day or none, picked by a **randomized bracket tournament** at the `signal-judge` Cloud Run service over the enriched pool **hard-gated to BULLISH only, then deterministically edge-ranked and capped to the top `TOURNEY_POOL_CAP` (default 12)** candidates (cost-forced, 2026-06-11 — the full ~94-pool tournament was ~39 model calls/pick; cap → ~9 at 12, ~3 at 10). **BULLISH-only is a HARD gate** (`BULLISH_ONLY=true`, owner-directed, env-toggleable; both strict + fallback paths) — the edge levers are call-delta-defined and don't transfer to puts; this explicitly overrides the "bearish is regime-conditional" caveat for now. Among bullish names the cap is a **SOFT pre-rank** by the 1,375-trade study's levers (mid-|delta| 0.20–0.46, RR<1.4, ATR-move), all point-in-time/leakage-safe; FALLBACK inherits the BULLISH gate but skips the edge-cap. See `docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md`: 3 independent brackets, each shuffles the pool into batches of ≤10 → **top-2 advance** → 94→20→4→1; the **consensus** winner across the 3 brackets is the pick (3/3=high, 2/3=medium, 1/3=low confidence). Dead-simple prompt ("make money buying a single option, sell for profit in 3 days") + the daily report for context + per-contract JSON; **no memory, no rubric, no weights** (`tournament_v1`, version 7, `gemini-3.1-pro-preview`; see `docs/DECISIONS/2026-06-04-bracket-tournament.md`). **Fail-closed on error — no fallback.** Trader mechanics unchanged: entry 10:00 ET day-1, −60% option stop, +80% option target, 3-day hold, exit 15:50 ET day-3. Stop wins over target on ambiguous bars. The trader simulates ONLY the ticker in `todays_pick/{scan_date}` (one row per day max). **Selection gates REMOVED 2026-06-04** — all enriched signals reach the tournament; the old `signal-notifier` moneyness/OI/vol/DTE/V-OI gates + the active-days liquidity gate + the daily-cadence fallback are GONE (they choked real winners on stale scan-time OI — the sweep only becomes OI the next morning; we enter at 10:00 and ride the build). UPSTREAM, only two layers remain: `enrichment-trigger` defines "enriched" (`overnight_score >= 4` [floor; EV inverts at >=7], `directional UOA > $500K`, all directions; SPREAD GATE RETIRED 2026-06-05 — this Polygon plan serves no options quotes, spread is permanently NULL, `_best_contract` now prices off last-trade/day-close; see `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`), and `signal-notifier` keeps exactly two SAFETY rails — **no earnings during the 3-day hold** (IV crush; literature-settled) and **regime fail-closed** (`VIX <= VIX3M`). Every candidate is `assert_no_leakage`-checked before the LLM. **2026-06-04 pipeline bug-hunt (`docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`): 13 silent data bugs fixed — the root cause was `polygon_client` substituting day low/high for missing bid/ask → fake/0% spreads on ~43% of picks (now NULL when unquoted; real spread otherwise); divergence-flip scoring reordered before conviction signals (was suppressing ~87% of the best setups); technicals lookahead (window bounded to `scan_date`); stale volume/OI fields stripped from the judge prompt; contract selection now liquidity-aware (OI-primary, real spread, no-quote strikes dropped); trader fill-realism. DEFERRED (need point-in-time data): OI + volume are still session-frozen snapshots — walled off from the judge, used only in the scanner's relative ranking.** The one-page operator view is [`CHEAT-SHEET.md`](CHEAT-SHEET.md). Source of truth for execution policy: `docs/TRADING-STRATEGY.md` + `forward-paper-trader/main.py` + `signal-judge/app/agent.py` + `docs/DECISIONS/2026-06-04-bracket-tournament.md`. (Prior eras for history: V5.4 single-judge `docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md`; ledger cohort labels: 5=two-stage, 6=judge_v6, 7=tournament in `signal_ranker_runs`.) **COST FIX 2026-06-12 — enrichment funnel:** the ~$38/day Gemini bill was NOT the tournament (~$1) but `enrichment-trigger` grounding all ~344 UOA names with uncapped thinking (~2M output tok/day; the trace logger hid it by dropping `thoughts_token_count`). FIXED: enrichment now edge-ranks to the **top `ENRICH_TOP_N` (default 50) BULLISH** names (`_edge_select_top_n`, confirmed |delta| lever, leakage-safe) and grounds only those with **`thinking_budget=0`**; the BULLISH gate + cap thus move UPSTREAM of the grounded LLM (so the "all directions" enrichment above now applies only to the cheap scan/UOA query — grounding is BULLISH-top-50). `TOURNEY_POOL_CAP` raised to 50 (env) so all enriched seed the tournament. `overnight_signals_enriched` shrinks ~344→~50 (raw-scan SEO pages unaffected; haystack/shadow-tracker depth narrows). Check real LLM cost via Cloud Monitoring `token_count`, not the trace table. See `docs/DECISIONS/2026-06-12-enrich-topN-thinking-cap.md`.

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
| `forward-paper-trader/` | Production paper-trading (no trader-side filters, writes to `forward_paper_ledger`). Cloud Run, two endpoints. Also writes an **isolated research shadow** (`paper_shadow_topscore`: top-`overnight_score` deterministic pick vs the tournament pick, identical mechanics, best-effort) — NEVER surfaced to the Scorecard or website; see `docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md`. |
| `enrichment-trigger/` | Enrichment pipeline (score>=1, spread<=10%, UOA>$500K, writes to `overnight_signals_enriched`). Instrumented via `libs/trace_logger`. |
| `agent-arena/` | Multi-model debate / signal ranking (instrumented) |
| `overnight-report-generator/` | Gemini editorial synthesis (instrumented) |
| `gammarips-eval/` | LLM eval service — monitoring-only, non-gating. See `docs/EVAL-SYSTEM.md`. |
| `x-poster/` | **ADK multi-agent X publisher for @gammarips** (since 2026-04-24). Planner→Writer→Reviewer→EscalationChecker LoopAgent + Publisher. 7 post types behind `POST /post`. Nano Banana editorial image gen + PIL logo composite. Cloud Run, DRY_RUN=true default. See `x-poster/DESIGN_SPEC.md`. |
| `blog-generator/` | **ADK multi-agent blog writer** (since 2026-04-24). Same shape as x-poster, writes Firestore `blog_posts/{slug}` for webapp `/blog` rendering. Weekly Mon 05:00 ET cron. **DEPLOYED** (live since 2026-06-01; rev `blog-generator-00023+`). See `blog-generator/DESIGN_SPEC.md`. |
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
