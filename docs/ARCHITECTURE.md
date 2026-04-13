# ARCHITECTURE.md

## Purpose
High-level map of the active GammaRips Engine system.

## Active components
### `src/` / scanner core
Core scoring and overnight signal generation.

### `overnight-scanner/`
Scanner-facing package / service wrapper for market-wide overnight options flow scanning.

### `enrichment-trigger/`
Enrichment service for news, technicals, and AI-generated context. V3 pipeline — reads from `overnight_signals` with `overnight_score >= 6`, writes to `overnight_signals_enriched`.

### `enrichment-trigger-v4/`
V4 parallel enrichment service. Independent Cloud Run deployment. Reads from `overnight_signals` with relaxed filters (`overnight_score >= 1`, `recommended_spread_pct <= 0.10`, directional UOA > $500K), writes to `overnight_signals_enriched_v4`. Cloud Scheduler `enrichment-trigger-v4-daily` fires at 05:30 ET Mon-Fri. ~70 tickers/day, ~9 minute runtime. See `docs/DECISIONS/2026-04-12-v4-fresh-start.md`.

### `overnight-report-generator/`
Daily report generation for the overnight signal set.

### `agent-arena/`
Multi-model debate / consensus service for ranking or adjudicating signal quality.

### `forward-paper-trader/`
Cloud Run service responsible for executing the V3.1 forward paper-trading policy and maintaining the IV-history cache. Single container, two endpoints:

- **`POST /`** — daily trigger (Cloud Scheduler `forward-paper-trader-trigger`, 16:30 ET Mon-Fri). Pulls eligible signals from `overnight_signals_enriched`, applies the V3.1 gate, simulates the `+40% / −25% / 2-day` bracket against Polygon minute bars for each option, and writes one row per signal (executed or skipped) to `forward_paper_ledger_v3_hold2`.
- **`POST /cache_iv`** — daily IV cache refresh (Cloud Scheduler `polygon-iv-cache-daily`, 16:30 ET Mon-Fri). Pulls the trailing-30-day watchlist from `overnight_signals_enriched`, fetches each underlying's options chain via Polygon, computes the ATM ~30-DTE implied volatility, and appends one row per ticker to `polygon_iv_history`.
- **`benchmark_context.py`** — non-blocking helper module imported by `main.py`. Hosts: the FRED VIX CSV fetcher (cached in-process), the Polygon options-chain fetcher, the ATM IV extractor, the HV-20d compute from Polygon daily bars, the SPY minute-bar cache, price-at-timestamp locators, and the BigQuery query that computes `iv_rank_entry` / `iv_percentile_entry` at trade time from `polygon_iv_history`. Every function returns `None` on any failure — the benchmarking layer cannot block a trade from being written.

### `forward-paper-trader-v4/`
V4 parallel paper-trading service. Independent Cloud Run deployment. Reads from `overnight_signals_enriched_v4` with **no trader-side filters** (all enriched signals execute), simulates the same `+40% / −25% / 2-day` bracket, writes to `forward_paper_ledger_v4_hold2`. Cloud Scheduler `forward-paper-trader-v4-trigger` fires at 16:30 ET Mon-Fri. A companion scheduler job `polygon-iv-cache-v4-daily` hits `POST /cache_iv` on this service at 16:30 ET Mon-Fri, writing to the shared `polygon_iv_history` table. See `docs/DECISIONS/2026-04-12-v4-fresh-start.md`.

### `win-tracker/`
Tracks realized performance after the trade window and closes the loop on execution outcomes.

### `backtesting_and_research/`
Research scripts and generated artifacts for studying filters, execution assumptions, and cohort behavior.

### `gammarips-eval/`
Cloud Run service that evaluates every LLM/agent call made by the instrumented production services. Reads `profit_scout.llm_traces_v1` (written by `libs/trace_logger` from each service), joins ground truth from `signal_performance` / `signals_labeled_v1`, runs a pluggable evaluator chain (GammaRips-specific + a vendored Gemini-as-judge `quality` evaluator), and writes scored rows to `profit_scout.llm_eval_results_v1`. A weekly `/eval/report` endpoint aggregates the week's results into a Firestore markdown digest at `eval_reports/{iso_week}`. **Monitoring-only, non-gating.** See `docs/EVAL-SYSTEM.md` and `docs/DECISIONS/2026-04-09-eval-system-v1.md`.

### `libs/trace_logger/`
Shared Python package (local path install, vendored into each service's build context by its `deploy.sh`) providing `TraceLogger.log(TraceRecord)` — a fire-and-forget BigQuery writer that never raises to the caller. Gated by the `TRACE_LOGGING_ENABLED` env var (default `false`).

## Data flow

### V3 pipeline (live control)
1. Overnight scanner produces signal candidates in `overnight_signals`.
2. `enrichment-trigger` enriches signals scoring `overnight_score >= 6`, writes to `overnight_signals_enriched`.
3. Optional report/arena layers add synthesis.
4. `forward-paper-trader` applies the V3.1 gate (`premium_score >= 2`, vol/oi floor), simulates bracket execution, and writes to `forward_paper_ledger_v3_hold2`.
5. Win tracker measures post-entry outcomes.

### V4 pipeline (parallel data collection, deployed 2026-04-12)
1. Same upstream `overnight_signals` table (shared scanner).
2. `enrichment-trigger-v4` enriches signals scoring `overnight_score >= 1` with `recommended_spread_pct <= 0.10` and directional UOA > $500K, writes to `overnight_signals_enriched_v4`. ~70 tickers/day.
3. `forward-paper-trader-v4` trades **all** enriched signals (no trader-side filters), simulates the same `+40% / −25% / 2-day` bracket, writes to `forward_paper_ledger_v4_hold2`.
4. After 30 days (target N >= 500), tree-based feature importance (XGBoost/SHAP) discovers empirical thresholds for a future V5 gate.

V3 and V4 are completely independent Cloud Run services with separate scheduler jobs, enriched tables, and ledger tables. They share only the upstream `overnight_signals` table and the `polygon_iv_history` IV cache.

**Parallel daily jobs:** `polygon-iv-cache-daily` (V3) and `polygon-iv-cache-v4-daily` (V4) both hit their respective service's `POST /cache_iv` at 16:30 ET Mon-Fri, snapshotting ATM 30-DTE IV into the shared `polygon_iv_history` table. This cache is read by `benchmark_context.fetch_iv_rank_from_bq` at trade time to populate `iv_rank_entry` / `iv_percentile_entry` on both ledgers.

## External data dependencies

| Dependency | Used by | Purpose |
|---|---|---|
| **Polygon** | `forward-paper-trader`, `forward-paper-trader-v4` (both endpoints), `src/enrichment/core/clients/polygon_client.py` | Option minute bars, option chain snapshots, stock minute + daily bars, stock snapshots. Secret: `POLYGON_API_KEY`. |
| **FRED** (`fredgraph.csv?id=VIXCLS`) | `forward-paper-trader` (`get_regime_context`) | Daily VIX close for `VIX_at_entry` + `vix_5d_delta_entry`. No API key required. Switched from FMP on 2026-04-08. |
| **FMP** | `enrichment-trigger`, `win-tracker`, `overnight-report-generator` (still) | News, fundamentals, historical quotes. **No longer used by `forward-paper-trader`** — mount removed from `forward-paper-trader/deploy.sh` on 2026-04-08 after FMP's legacy historical-price endpoint was retired. |
| **BigQuery** | All services | Canonical storage for `overnight_signals_enriched`, `overnight_signals_enriched_v4`, `forward_paper_ledger_v3_hold2`, `forward_paper_ledger_v4_hold2`, `polygon_iv_history`, `signals_labeled_v1`, etc. |
| **GCS** | `overnight-scanner` | Ticker universe file (`overnight-universe.txt`). |

## Current architecture truth
The most important architectural boundary right now is between:
- **signal generation research**
- **execution policy selection**
- **outcome measurement**

Those must stay separable so policy changes can be evaluated cleanly.

## Historical areas
- `_archive/` contains older legacy code and should not be treated as active runtime infrastructure.
- `docs/research_reports/` contains historical research and planning context, not necessarily the current execution spec.

## Current technical debt
- execution logic and docs have drifted
- no prior root agent harness
- generated artifacts and historical prompts were cluttering the repo
- policy versioning in the forward ledger needs to be explicit

## Near-term objective
Make the repo legible enough that a coding agent or Gemini can safely operate without guessing which documents are authoritative.

## The GammaRips Gated Workflow (G-Stack)

To prevent regressions and protect live capital, all strategy changes must adhere to the following strict "Definition of Done" pipeline inspired by the G-Stack methodology:

1. **Phase 1: Idea & Planning (`gammarips-researcher`)**: Hypothesis generation, backtest planning, and explicit target metrics. No code is written for live execution yet.
2. **Phase 2: Code & Review (`gammarips-engineer` + `gammarips-review`)**: Engineering implementation followed by a mandatory audit for lookahead bias, data leakage, and unhandled edge cases.
3. **Phase 3: Forward Paper Validation**: Mandatory 30-day out-of-sample testing on the `forward-paper-trader` system, logging to the BigQuery `forward_paper_ledger`.
4. **Phase 4: Ship**: Production deployment is ONLY permitted if Phase 3 yields a verified positive expectancy.
