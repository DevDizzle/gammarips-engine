# ARCHITECTURE.md

## Purpose
High-level map of the active GammaRips Engine system.

## Active components
### `src/` / scanner core
Core scoring and overnight signal generation.

### `overnight-scanner/`
Scanner-facing package / service wrapper for market-wide overnight options flow scanning.

### `enrichment-trigger/`
Enrichment service for news, technicals, and AI-generated context. Reads from `overnight_signals` with `overnight_score >= 4` and directional UOA > $500K (**spread gate RETIRED 2026-06-05** — this Polygon plan serves no quotes, `recommended_spread_pct` is permanently NULL), then **edge-ranks + grounds only the top-50 BULLISH** names (`thinking_budget=0`). Writes to `overnight_signals_enriched` via an atomic schema-drift-safe path (**never `autodetect`** — that broke every load 2026-07-02). Cloud Scheduler `enrichment-trigger-daily` fires at 05:30 ET Mon-Fri. ~50 tickers/day. The `mom_60` soft tilt (the ".1" in V7.1) biases the edge-rank before the top-50 cut. It has a kill-switch env (see `docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`). `LIQ_DEMOTION` sorts likely-thin names below unflagged names but never drops them (see `docs/DECISIONS/2026-07-28-pool-tradeability-build.md`). The 2026-08-19 cap-20 / pool-admission-floor proposal was NOT adopted: `ENRICH_TOP_N=50` stands (see `docs/DECISIONS/2026-08-19-pool-liquidity-floor-and-cap-20.md`).

### `overnight-report-generator/`
Daily report generation for the overnight signal set.

### `agent-arena/`
Multi-model debate / consensus service for ranking or adjudicating signal quality. **Deprecated 2026-05-04 — not run.**

### `signal-judge/`
The V6 ranker (renamed from `signal-ranker` on 2026-06-04). Cloud Run, `POST /rank` (IAM-only). Runs a **randomized bracket tournament** (`tournament_v1` lineage, currently `tournament_v1_3` / `JUDGE_PROMPT_VERSION=10`, `gemini-3.1-pro-preview`; `signal-judge/deploy.sh` pins the live version) over **all** enriched candidates passed by `signal-notifier` — no upstream selection gating. Three independent brackets each seed the candidate field randomly and reduce it in batches of ≤10 (top-2 advance per batch), collapsing ~50 → … → 1, then a consensus pick is taken across the three bracket winners. The prompt is a daily report + per-contract JSON and carries liquidity directives since 2026-07-28 (tightened 2026-08-07 and 2026-08-12). There is **no memory and no flow/regime/narrative weights** (those belonged to the prior `judge_v6` single-judge era, now retired). Fails closed (no V5.3 fallback). Writes trace rows to `signal_ranker_runs` (table name unchanged).

### `signal-notifier/`
Builds the enriched candidate pool from `overnight_signals_enriched`. The V6 selection gates (moneyness / OI / vol / DTE / V-OI / active-days) were **removed 2026-06-04**. What remains: the BULLISH-only hard gate, the edge-rank pool cap (`TOURNEY_POOL_CAP=12`), and the safety rails. The rails are: no earnings during the hold window, the `VIX <= VIX3M` regime check (fail-closed), the live-OI liquidity floor (`OI_FLOOR`), and the known-prints floor (`PRINT_FLOOR_MIN`; the owner adopted raising it 1 → 25 on 2026-08-19, not yet deployed, live env still 1 as of 2026-08-20). Fail-soft restore is locked to `FAILSOFT_RESTORE_MODE=none` since 2026-08-12 (with `LIVE_FETCH_MIN_OK_FRAC=0.5` as the evidence gate): a candidate a floor drops can never return as the pick. Calls `signal-judge /rank` (the tournament) for the pick, writes it to Firestore `todays_pick/{scan_date}` (+ `{entry_day}`), and emails it (email only; the WhatsApp channel was retired 2026-07-03). Also owns the public cohort surfaces (`cohort_stats/current`, `ledger_trades`) and the `POST /refresh_pool_liquidity` interval refresh of `pool_liquidity_snapshot`. Fail-closed (no email, empty-state `todays_pick`) on any ranker error or skip.

### `forward-paper-trader/`
Cloud Run service for forward paper-trading, IV cache maintenance, and the research-only labeling/backfill crons. Single container; the two live-path endpoints are below, plus the research endpoints `/persist_minute_paths`, `/label_life_surface`, `/label_enriched_pool`, `/fill_closed_windows`, `/load_underlying_bars` and `/mark_to_market` (all token-gated via `X-Refresh-Token`, none of which touch `forward_paper_ledger`):

- **`POST /`** — daily paper trading trigger (Cloud Scheduler `forward-paper-trader-trigger`, 16:30 ET Mon-Fri). Reads the pick from Firestore `todays_pick/{scan_date}`, joins that ONE ticker against `overnight_signals_enriched`, and simulates the **V7.1 Tilted GIGO** policy (`10:00 ET entry, +40% target / −30% stop, same-day, flat 15:45 ET`, no trail; TIMEOUT>STOP>TARGET on ambiguous bars) against Polygon minute bars. Writes at most one row per day (a trade row or a skip row) to `forward_paper_ledger` tagged `policy_version = V7_1_TILTED_GIGO` (cohort start: the live value is `LIVE_COHORT_START_DATE` in `signal-notifier/main.py`, 2026-08-13 as of the 2026-08-12 reset). The same run writes the isolated research shadow `paper_shadow_topscore` (deterministic top-`overnight_score` arm vs the tournament arm, identical mechanics, best-effort, walled off from every public surface; see `docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md`). The full enriched pool is replayed separately by the `/label_enriched_pool` research cron into `enriched_option_outcomes`. No trader-side filters — signal-quality lives upstream in `signal-judge` / `signal-notifier`.
- **`POST /cache_iv`** — daily IV cache refresh (Cloud Scheduler `polygon-iv-cache-daily`, 16:30 ET Mon-Fri). Pulls trailing-30-day watchlist, fetches each underlying's options chain via Polygon, computes ATM ~30-DTE IV, appends to `polygon_iv_history`.
- **`benchmark_context.py`** — non-blocking helper module. Hosts: FRED VIX CSV fetcher, Polygon options-chain fetcher, ATM IV extractor, HV-20d compute, SPY minute-bar cache, price-at-timestamp locators, and BigQuery IV rank query. Every function returns `None` on failure — benchmarking cannot block a trade.

### `win-tracker/`
Tracks realized performance after the trade window and closes the loop on execution outcomes.

### `backtesting_and_research/`
Research scripts and generated artifacts for studying filters, execution assumptions, and cohort behavior.

### `gammarips-eval/`
Cloud Run service that evaluates every LLM/agent call made by the instrumented production services. Reads `profit_scout.llm_traces_v1` (written by `libs/trace_logger` from each service), joins ground truth from `signal_performance` / `signals_labeled_v1`, runs a pluggable evaluator chain (GammaRips-specific + a vendored Gemini-as-judge `quality` evaluator), and writes scored rows to `profit_scout.llm_eval_results_v1`. A weekly `/eval/report` endpoint aggregates the week's results into a Firestore markdown digest at `eval_reports/{iso_week}`. **Monitoring-only, non-gating.** See `docs/EVAL-SYSTEM.md` and `docs/DECISIONS/2026-04-09-eval-system-v1.md`.

### `x-poster/`
ADK multi-agent X publisher for `@gammarips`. Five Cloud Scheduler jobs invoke `POST /post {post_type}` weekday/Friday: `report` (08:30 ET), `signal`/`standby` (09:05 ET), `teaser` (12:30 ET), `callback` for win/loss (16:45 ET), `scorecard` (Fri 17:00 ET). Pipeline: `Planner → Writer → Reviewer (LoopAgent max 3) → Publisher`. Posts are **text-only** as of 2026-04-28 (editorial images retired). The `⚠️ Paper-trade. Not advice.` disclaimer is appended deterministically only on win/loss/callback/scorecard. `signal`/`standby`/`teaser`/`report` ship without a disclaimer. Publisher has no-content guards: `callback` skips when no closes today, `report` skips when `overnight_reports/{date}` is empty. Voice rules + compliance rubric live in shared `libs/gammarips_content/`. Vendored at deploy time.

### `blog-generator/`
ADK multi-agent weekly blog publisher. One Cloud Scheduler job `blog-generator-weekly` (Mon 05:00 ET) invokes `POST /generate` with empty body. Pipeline: same `Planner → Writer → Reviewer (LoopAgent max 3) → Publisher` shape as x-poster. Reads `blog_schedule/current` from Firestore (13-row 90-day plan), drafts ~1,500-word markdown, writes to `blog_posts/{slug}` with `status="published"`. Webapp `/blog/[slug]` renders directly from Firestore. **Endpoint is `/generate`, not `/run`** — ADK's `get_fast_api_app` reserves `/run` for its built-in session handler. Rubric gate is enforced at BOTH `EscalationChecker` (loop exit) and `Publisher` (publish gate); the LLM reviewer cannot bypass deterministic checks. Disclaimer canonicalization in `gammarips_content.compliance.canonicalize_blog_disclaimer` strips writer paraphrase and appends the canonical blockquote. CTA validation hard-fails on schedule-slot mismatch and on paid-tier pitches in `webapp_visit` slots. First production deploy: 2026-04-28 (rev `00008-9qt`, DRY_RUN=false). Also hosts the newsletter endpoints: `POST /draft_email` sends drafts to `OPERATOR_EMAIL` only and never fans out, and `POST /blast_email` is the only path to the user list (requires explicit `dry_run=False` and a valid `audience`).

### `reddit-poster/`
ADK Reddit drafter. Cloud Run shape, `POST /post` for `trade_idea` / `pnl_receipt` only. Carries its own deterministic `compliance.py` rubric that imports the shared voice and banned-recommendation lists from `libs/gammarips_content`. Deploy state is not verifiable from the repo.

### `dbt/`
Semantic layer over the BigQuery tables (target dataset `profitscout_dbt`). Sits downstream of the Cloud Run pipeline and never touches trading execution. Source of the leakage-split model pair (`features_enriched_option_outcomes` agent-facing vs `fct_enriched_option_outcomes` label-carrying). See `dbt/README.md`.

### `dbt-runner/`
Cloud Run wrapper that runs the dbt project on a schedule (`POST /` = `dbt build`, `POST /freshness`). Its own README declares it **DRAFT, NOT DEPLOYED**. See `docs/DECISIONS/2026-06-23-dbt-layer-rebuild.md`.

### `libs/trace_logger/`
Shared Python package (local path install, vendored into each service's build context by its `deploy.sh`) providing `TraceLogger.log(TraceRecord)` — a fire-and-forget BigQuery writer that never raises to the caller. Gated by the `TRACE_LOGGING_ENABLED` env var (default `false`).

### `libs/gammarips_content/`
Shared content lib vendored at deploy time into `x-poster` + `blog-generator`, and imported by `reddit-poster`'s compliance rubric. Contains: `voice_rules` (DO/DO NOT, retired aliases, banned phrases, canonical disclaimer strings), `compliance` (`score_against_rubric`, `canonicalize_draft_text` for X posts, `canonicalize_blog_disclaimer` for blog markdown), `brand` (hex codes, fonts), `firestore_helpers` (idempotency keys, x_posts log writer, todays_pick reader), `tweepy_helper` (X posting + DRY_RUN), `mcp_client` (used by the agent). Single source of truth for any voice/compliance change — services pick it up at next `bash deploy.sh`.

## Data flow

1. Overnight scanner produces signal candidates in `overnight_signals`.
2. `enrichment-trigger` enriches signals with `overnight_score >= 4` and directional UOA > $500K (spread gate retired 2026-06-05), edge-ranking + grounding the top-50 BULLISH names. Writes to `overnight_signals_enriched`. ~50 tickers/day.
3. `overnight-report-generator` adds the daily report (regime + narrative context the tournament reads).
4. `signal-notifier` builds the enriched candidate pool (V6 selection gates removed 2026-06-04), applies the BULLISH hard gate + edge-rank cap and the rails: earnings exclusion, `VIX <= VIX3M` regime check (fail-closed), live-OI floor, and known-prints floor (`PRINT_FLOOR_MIN`; raise to 25 adopted 2026-08-19, not yet deployed, live env still 1 as of 2026-08-20). Fail-soft restore is locked to `none` since 2026-08-12, so a floor-dropped candidate never returns. It then calls `signal-judge` (`tournament_v1` lineage, currently `tournament_v1_3`), which runs a randomized bracket tournament (3 brackets × batches of ≤10, top-2 advance, ~50 → … → 1 → consensus) and returns **at most one** pick. `signal-notifier` writes `todays_pick`, refreshes `cohort_stats/current` + `ledger_trades`, and emails the pick (or fails closed).
5. `forward-paper-trader` simulates the **V7.1 Tilted GIGO** policy (same-day 10:00→15:45 bracket) on the single `todays_pick` ticker (no trader-side filters; at most one ledger row per day), and writes to `forward_paper_ledger` tagged `policy_version = V7_1_TILTED_GIGO` (cohort start: the live value is `LIVE_COHORT_START_DATE` in `signal-notifier/main.py`, 2026-08-13 as of the 2026-08-12 reset). The `/label_enriched_pool` cron replays the full pool into `enriched_option_outcomes` separately.
6. Win tracker measures post-entry stock-level outcomes (3-day peak) into `signal_performance`.
7. Phase 2 feature discovery remains the only path to new gates (see the CLAUDE.md ground rules). Backlog items: sweep/block detection, aggressor side, GEX, trailing stops. Each ships as its own decision note.

**IV cache:** `polygon-iv-cache-daily` hits `POST /cache_iv` at 16:30 ET Mon-Fri, snapshotting ATM 30-DTE IV into `polygon_iv_history`. Read by `benchmark_context.fetch_iv_rank_from_bq` at trade time.

## External data dependencies

| Dependency | Used by | Purpose |
|---|---|---|
| **Polygon** | `forward-paper-trader`, `forward-paper-trader` (both endpoints), `src/enrichment/core/clients/polygon_client.py` | Option minute bars, option chain snapshots, stock minute + daily bars, stock snapshots. Secret: `POLYGON_API_KEY`. |
| **FRED** (`fredgraph.csv?id=VIXCLS`) | `forward-paper-trader` (`get_regime_context`) | Daily VIX close for `VIX_at_entry` + `vix_5d_delta_entry`. No API key required. Switched from FMP on 2026-04-08. |
| **FMP** | `signal-notifier` only | Earnings calendar for the no-earnings-during-hold rail. **No longer used by `forward-paper-trader`** (mount removed 2026-04-08). Never used by `enrichment-trigger` or `win-tracker`. |
| **BigQuery** | All services | Canonical storage for `overnight_signals_enriched`, `forward_paper_ledger`, `polygon_iv_history`, `signals_labeled_v1`, etc. |
| **GCS** | `overnight-scanner` | Ticker universe file (`overnight-universe.txt`). |

## Current architecture truth
The most important architectural boundary right now is between:
- **signal generation research**
- **execution policy selection**
- **outcome measurement**

Those must stay separable so policy changes can be evaluated cleanly.

**2026-06-04 pipeline bug-fixes** (see `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`): scanner contract selection is now liquidity-aware (uses real bid/ask spread, drops no-quote strikes, scores divergence-first); the technicals window is bounded to `scan_date` (lookahead fix); and the trader gained fill-realism. These landed alongside the V6 tournament + selection-gate removal in the same pass.

## Historical areas
- `_archive/` contains older legacy code and should not be treated as active runtime infrastructure.
- `docs/research_reports/` contains historical research and planning context, not necessarily the current execution spec.

## The GammaRips workflow (G-Stack)

The G-Stack phases are workflow guidance, not gates. The Definition of Done lives in `CLAUDE.md`: ship, watch the logs, roll back with an env var.

1. **Phase 1: Idea & Planning (`gammarips-researcher`)**: hypothesis generation, backtest planning, and explicit target metrics before live code.
2. **Phase 2: Code (`gammarips-engineer`)**: engineering implementation. Leakage-safety is physics: no lookahead, no post-entry features. `gammarips-review` is optional and owner-invoked.
3. **Phase 3: Telemetry**: `forward-paper-trader` logs to `forward_paper_ledger`. The ledger is telemetry. No deploy waits on it.
4. **Phase 4: Ship**: deploy per the `/deploy-service` skill, then watch the logs. Add a `docs/DECISIONS/` note when execution policy changes.
