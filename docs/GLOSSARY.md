# GammaRips Glossary — Services & Tables

Plain-English reference. Not schemas. Use this to remember what each thing is for.

## Services (Cloud Run)

| Service | What it does | Why it exists |
|---|---|---|
| `overnight-scanner` | Pulls raw options activity data from Polygon each evening. Detects unusual options activity (UOA) — large directional call/put volume, spread quality, technicals. | Ingests the raw universe. You'd see ~500 tickers mentioned per night. |
| `enrichment-trigger` | Filters scanner output to signals with `overnight_score >= 1 AND spread <= 10% AND directional UOA > $500k`. Adds features: premium flags, technicals, V/OI ratio, moneyness %, VIX3M. | Turns raw noise into tradeable candidates. ~80 survive per day. |
| `signal-notifier` | Applies V5.3 quality filters (V/OI > 2, moneyness 5–15% OTM, VIX ≤ VIX3M), ranks by directional UOA $vol, emails you the **top 1** at 9 AM ET. | Your inbox is the signal. One pick per day or nothing. |
| `forward-paper-trader` | Simulates V5.3 execution (10 AM entry, −60% stop, +80% target, 3-day hold, 15:50 exit) on every enriched signal. Writes to `forward_paper_ledger`. | Paper P&L baseline. Runs in parallel with your real trades so we can compare mechanical execution vs your discretion. |
| `win-tracker` | For every enriched signal, tracks the underlying STOCK's 3-day peak price movement. Writes to `signal_performance`. Posts "strong" wins to X/Twitter. | Answers "did the direction call work?" independent of whether the option trade worked. |
| `agent-arena` | Multi-LLM debate service. Different AI models argue for/against signals. Writes to `agent_arena_*` tables. | Research tool. Not currently gating your trades — monitoring only. |
| `overnight-report-generator` | Uses Gemini to write an editorial summary of each night's scan for the webapp. | User-facing narrative layer. Not part of the trading loop. |
| `gammarips-eval` | Evaluates LLM quality against labeled outcomes. Writes to `llm_eval_results_v1`. | Monitoring only. Non-gating. |
| `gammarips-mcp`, `gammarips-webapp` | The public-facing web surface. | Consumer-facing UI for the research. |

## BigQuery tables (`profitscout-fida8.profit_scout.*`)

| Table | What's in it | Who writes it | Why you care |
|---|---|---|---|
| `overnight_signals` | Raw scanner output — every ticker the scanner flagged, before filtering. | `overnight-scanner` | Full universe. You probably never query this directly. |
| `overnight_signals_enriched` | Filtered + feature-added signals. 80-ish rows/day passing the enrichment gate. Has all the features the notifier and trader use (premium flags, technicals, V/OI, moneyness, VIX3M). | `enrichment-trigger` | This is the table the notifier reads to decide what to email you. |
| `signal_performance` | Stock-level 3-day outcomes: peak move %, tier bucket (strong/solid/directional/no_decision/loss), `is_final` flag. 2,664 rows since Feb 18. | `win-tracker` | Answers "did the signal pick the right direction?" Use for directional accuracy analysis. |
| `signals_labeled_v1` | **FROZEN research dataset.** 2,162 option-level simulated trades (Feb 18 – Apr 6) with entry, target, stop, exit, realized return. Built by `scripts/research/` (frozen). | One-shot research script (do not rebuild) | Historical validation backbone. Do not modify. Read-only use only. |
| `forward_paper_ledger` | Paper P&L for every enriched signal. Tagged by `policy_version` — V4 rows from pre-2026-04-17, V5.3 rows going forward. | `forward-paper-trader` | Your live paper scoreboard. Compare V5.3 EV here to your real P&L to see if discretion adds value. |
| `polygon_iv_history` | Daily ATM-30D implied volatility snapshot per ticker in the scan universe. | `forward-paper-trader` `/cache_iv` endpoint (daily 16:30 ET) | Backfills `iv_rank_entry`/`iv_percentile_entry` on ledger rows. |
| `agent_arena_consensus`, `agent_arena_picks`, `agent_arena_rounds` | Multi-LLM debate artifacts. | `agent-arena` | Research/monitoring only. Not in the trading loop. |
| `llm_eval_results_v1`, `llm_traces_v1` | LLM evaluation output and prompt/response traces. | `gammarips-eval`, shared `libs/trace_logger` | Observability into LLM quality. Not in the trading loop. |
| `temp_perf_updates` | Staging table for win-tracker perf updates. | `win-tracker` internal | Ignore. |

## Governance

| Term | What it means |
|---|---|
| `policy_version` | Tag on every ledger row identifying which strategy produced it. V5.3 rows get `V5_3_TARGET_80`; older V4 rows retain `V4_NO_GATE_SPREAD_ONLY`. **Never reuse a label across strategies** — keeps the cohorts clean. |
| `policy_gate` | Describes the filter applied. V5.3 uses `ENRICHMENT_ONLY_NO_TRADER_GATE` — meaning the trader applies no filters, all gates live upstream. |
| `scan_date` | The date the scanner ran (overnight). Signals for `scan_date = X` are traded on `X+1 trading day`. |
| `enriched_at` | Timestamp the enrichment step completed. For a `scan_date` of Monday, `enriched_at` is typically Tuesday 05:30 ET. |
| Frozen files | `scripts/research/*` and `signals_labeled_v1` are immutable for reproducibility. Everything else can evolve. |
| Phase 2 backlog | Sweep/block detection, aggressor side, GEX, trailing stops — all deferred until V5.3 accumulates 4+ weeks of live evidence. |

## Subagents (Claude Code)

| Agent | Role |
|---|---|
| `gammarips-engineer` | Implementation. Code changes, deploys, BQ schema. |
| `gammarips-researcher` | Read-only research. Cohort analysis, hypothesis testing. Does not edit code. |
| `gammarips-review` | Read-only auditor. **Must run before any deploy.** Checks lookahead, leakage, unsafe execution. |

## Read-first docs

| File | Read when |
|---|---|
| `CHEAT-SHEET.md` (root) | You want to know what to do today. |
| `docs/TRADING-STRATEGY.md` | You want the canonical policy spec. |
| `docs/DECISIONS/2026-04-17-v5-3-target-80.md` | You want the rationale behind V5.3. |
| `docs/GLOSSARY.md` (this file) | You forgot what a service or table is for. |
| `docs/ARCHITECTURE.md` | You're touching code and need the data-flow map. |
| `docs/DATA-CONTRACTS.md` | You need the actual BQ schemas. |
| `docs/archive/*` | Historical only. Not authoritative. |
