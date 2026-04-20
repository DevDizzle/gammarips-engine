# ARCHITECTURE.md

## Purpose
High-level map of the active GammaRips Engine system.

## Active components
### `src/` / scanner core
Core scoring and overnight signal generation.

### `overnight-scanner/`
Scanner-facing package / service wrapper for market-wide overnight options flow scanning.

### `enrichment-trigger/`
Enrichment service for news, technicals, and AI-generated context. Reads from `overnight_signals` with `overnight_score >= 1`, `recommended_spread_pct <= 0.10`, directional UOA > $500K. Writes to `overnight_signals_enriched`. Cloud Scheduler `enrichment-trigger-daily` fires at 05:30 ET Mon-Fri. ~70 tickers/day, ~9 minute runtime.

### `overnight-report-generator/`
Daily report generation for the overnight signal set.

### `agent-arena/`
Multi-model debate / consensus service for ranking or adjudicating signal quality.

### `forward-paper-trader/`
Cloud Run service for forward paper-trading and IV cache maintenance. Single container, two endpoints:

- **`POST /`** — daily paper trading trigger (Cloud Scheduler `forward-paper-trader-trigger`, 16:30 ET Mon-Fri). Reads all enriched signals from `overnight_signals_enriched`, simulates the **V5.3 Target 80** policy (`10:00 ET entry, −60% stop, +80% target, 3-day hold, 15:50 ET exit`; STOP wins on ambiguous bars) against Polygon minute bars, writes to `forward_paper_ledger` tagged `policy_version = V5_3_TARGET_80`. No trader-side filters — signal-quality gates live in `enrichment-trigger` and `signal-notifier`.
- **`POST /cache_iv`** — daily IV cache refresh (Cloud Scheduler `polygon-iv-cache-daily`, 16:30 ET Mon-Fri). Pulls trailing-30-day watchlist, fetches each underlying's options chain via Polygon, computes ATM ~30-DTE IV, appends to `polygon_iv_history`.
- **`benchmark_context.py`** — non-blocking helper module. Hosts: FRED VIX CSV fetcher, Polygon options-chain fetcher, ATM IV extractor, HV-20d compute, SPY minute-bar cache, price-at-timestamp locators, and BigQuery IV rank query. Every function returns `None` on failure — benchmarking cannot block a trade.

### `win-tracker/`
Tracks realized performance after the trade window and closes the loop on execution outcomes.

### `backtesting_and_research/`
Research scripts and generated artifacts for studying filters, execution assumptions, and cohort behavior.

### `gammarips-eval/`
Cloud Run service that evaluates every LLM/agent call made by the instrumented production services. Reads `profit_scout.llm_traces_v1` (written by `libs/trace_logger` from each service), joins ground truth from `signal_performance` / `signals_labeled_v1`, runs a pluggable evaluator chain (GammaRips-specific + a vendored Gemini-as-judge `quality` evaluator), and writes scored rows to `profit_scout.llm_eval_results_v1`. A weekly `/eval/report` endpoint aggregates the week's results into a Firestore markdown digest at `eval_reports/{iso_week}`. **Monitoring-only, non-gating.** See `docs/EVAL-SYSTEM.md` and `docs/DECISIONS/2026-04-09-eval-system-v1.md`.

### `libs/trace_logger/`
Shared Python package (local path install, vendored into each service's build context by its `deploy.sh`) providing `TraceLogger.log(TraceRecord)` — a fire-and-forget BigQuery writer that never raises to the caller. Gated by the `TRACE_LOGGING_ENABLED` env var (default `false`).

## Data flow

1. Overnight scanner produces signal candidates in `overnight_signals`.
2. `enrichment-trigger` enriches signals with `overnight_score >= 1`, `recommended_spread_pct <= 0.10`, and directional UOA > $500K. Writes to `overnight_signals_enriched`. ~70 tickers/day.
3. Optional report/arena layers add synthesis.
4. `signal-notifier` layers V5.3 quality gates (`volume_oi_ratio > 2`, `moneyness_pct` 5–15%, `VIX <= VIX3M`), ranks by directional UOA $vol, and emails **at most one** signal per day.
5. `forward-paper-trader` simulates the **V5.3 Target 80** policy on all enriched signals (no trader-side filters), writes to `forward_paper_ledger`.
6. Win tracker measures post-entry stock-level outcomes (3-day peak) into `signal_performance`.
7. Phase 2 backlog — sweep/block detection, aggressor side, GEX, trailing stops — deferred until V5.3 has 4+ weeks of paper + real P&L evidence.

**IV cache:** `polygon-iv-cache-daily` hits `POST /cache_iv` at 16:30 ET Mon-Fri, snapshotting ATM 30-DTE IV into `polygon_iv_history`. Read by `benchmark_context.fetch_iv_rank_from_bq` at trade time.

## External data dependencies

| Dependency | Used by | Purpose |
|---|---|---|
| **Polygon** | `forward-paper-trader`, `forward-paper-trader` (both endpoints), `src/enrichment/core/clients/polygon_client.py` | Option minute bars, option chain snapshots, stock minute + daily bars, stock snapshots. Secret: `POLYGON_API_KEY`. |
| **FRED** (`fredgraph.csv?id=VIXCLS`) | `forward-paper-trader` (`get_regime_context`) | Daily VIX close for `VIX_at_entry` + `vix_5d_delta_entry`. No API key required. Switched from FMP on 2026-04-08. |
| **FMP** | `enrichment-trigger`, `win-tracker`, `overnight-report-generator` (still) | News, fundamentals, historical quotes. **No longer used by `forward-paper-trader`** — mount removed from `forward-paper-trader/deploy.sh` on 2026-04-08 after FMP's legacy historical-price endpoint was retired. |
| **BigQuery** | All services | Canonical storage for `overnight_signals_enriched`, `forward_paper_ledger`, `polygon_iv_history`, `signals_labeled_v1`, etc. |
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
