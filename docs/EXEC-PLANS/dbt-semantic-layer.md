# dbt Semantic Layer — Execution Plan

**Owner:** whichever Claude session picks this up
**Status:** Phase 1–3 complete and validated against BigQuery on 2026-04-09. Tiers 1–3 below are the remaining work.
**Entry read order:** this file → `CLAUDE.md` → `dbt_implementation_summary.md` (repo root) → `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md` → `docs/EVAL-SYSTEM.md`.

---

## 0. Pick-this-up-cold brief

A previous session built a dbt Core semantic layer over the GammaRips forward paper-trading ledger. It is **green end-to-end** against BigQuery (`PASS=18 ERROR=0`). All code lives under `dbt/`. A human-readable state report is in `dbt_implementation_summary.md` at the repo root — read it before touching anything.

Your job is to take this from "green v1 over one domain" to "production-grade analytics platform covering all GammaRips pipelines." The work is broken into three tiers. **Tier 1 is infrastructure maturity. Tier 2 is new-domain coverage. Tier 3 is nice-to-haves.** Tier 4 in this doc is a list of things you must *not* do during the current freeze window.

### What's already green (don't rebuild)

```
dbt/
├── dbt_project.yml              # project 'gammarips'
├── profiles.yml                 # BigQuery OAuth, gitignored
└── models/
    ├── metricflow_time_spine.sql + .yml
    ├── staging/
    │   ├── src_profitscout.yml              # sources: forward_paper_ledger_v3_hold2, overnight_signals_enriched
    │   ├── stg_forward_paper_ledger_v3.sql
    │   └── stg_overnight_signals.sql
    └── marts/
        ├── fct_paper_trades.sql + .yml      # 30 rows, 6 KiB materialized
        ├── fct_signals_enriched.sql         # 2,400 rows
        ├── metrics/performance_metrics.yml  # 12 metrics, incl. expectancy_pct
        └── semantic_models/paper_trades_sm.yml
```

- Venv: `.venv_dbt/` with `dbt-core==1.11.8` and `dbt-bigquery==1.11.1`.
- Run command: `cd dbt && /home/user/gammarips-engine/.venv_dbt/bin/dbt build --profiles-dir .`
- BQ target dataset: `profitscout-fida8.profitscout_dbt`.
- Natural key on the ledger and on `overnight_signals_enriched` is **3-column**: `(scan_date, ticker, recommended_contract)`. Do not regress to a 2-column key — the source test will catch you with ~36 duplicates.
- `trade_id` is `CONCAT(CAST(scan_date AS STRING), '_', ticker, '_', recommended_contract)`.
- Win/loss flags are gated on `is_completed_trade` — skipped rows must never land in winner/loser counts.

### The freeze rule (read twice)

Per `CLAUDE.md` and `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`, the V3.1 forward-paper gate is **frozen for a 4–6 week post-war accumulation period** starting 2026-04-08. During the freeze:

- The `fct_paper_trades` table is **reporting-only**. Do not rank gates, search filters, or select winners on it.
- Pre-war (≤ 2026-04-08) and post-war cohorts must be compared epoch-by-epoch at the revisit point. Do not mix them.
- The 30-row pre-war cohort is regime-confounded (Iran shock, record VRP, VIX peak 35.3). Nothing you compute on it is a signal-quality claim.
- Any Python migration that would *enable* filter searching on the pre-war cohort is out of scope until the freeze lifts.

This plan is designed so every Tier 1 and Tier 2 task is freeze-safe. Tier 3 has a note where relevant.

---

## Tier 1 — Infrastructure maturity (do first)

Goal: turn the current directory of YAML into a production-grade platform with docs, CI, stricter tests, and a declared consumer graph. Every task here is pure infra — zero impact on the freeze.

### T1.1 — Add `packages.yml` with `dbt_utils`

**Why:** The current source PK tests use string-concat hacks (`concat(cast(scan_date as string), '_', ticker, ...)`). `dbt_utils.unique_combination_of_columns` takes a list and does it cleanly. You also get `accepted_range`, `expression_is_true`, and `generate_surrogate_key` which you'll use in T1.3.

**Steps:**
1. Create `dbt/packages.yml` with:
   ```yaml
   packages:
     - package: dbt-labs/dbt_utils
       version: [">=1.3.0", "<2.0.0"]
   ```
2. Run `dbt deps --profiles-dir .` from `dbt/`.
3. In `dbt/models/staging/src_profitscout.yml`, replace both `unique:` concat-string tests with:
   ```yaml
   tests:
     - dbt_utils.unique_combination_of_columns:
         combination_of_columns:
           - scan_date
           - ticker
           - recommended_contract
   ```
4. In `dbt/models/staging/stg_forward_paper_ledger_v3.sql`, consider replacing the `CONCAT(...)` trade_id with `{{ dbt_utils.generate_surrogate_key(['scan_date', 'ticker', 'recommended_contract']) }}`. This is a judgment call — `generate_surrogate_key` produces an MD5 that is stable but no longer human-readable. Keep the concat if you want inspectable IDs, switch to surrogate if you want canonical keys. Document the choice in `fct_paper_trades.yml`.

**Acceptance:** `dbt build --profiles-dir .` still PASS=18 ERROR=0.

### T1.2 — `dbt docs` site + GitHub Actions CI

**Why:** This is the single highest-leverage task in the entire plan. `dbt docs generate` produces a browsable data dictionary and a column-level lineage graph. Paired with a CI workflow that runs `dbt build` on every PR against a dedicated CI dataset, it turns "works on my laptop" into a real platform. This is also the artifact you'd show in an interview.

**Steps:**

**Docs site:**
1. From `dbt/`, run `dbt docs generate --profiles-dir .`. Output lands in `dbt/target/catalog.json` and `manifest.json`.
2. Verify with `dbt docs serve --profiles-dir . --port 8081` (open in browser, click through the lineage graph, confirm column docs show up on `fct_paper_trades`).
3. Add a script: `scripts/dbt_docs.sh` that wraps `generate` + `serve` for local use.
4. Decide on hosting. Two options:
   - **GitHub Pages:** add a workflow step that copies `target/` to `gh-pages` branch after each main-branch build.
   - **Cloud Storage static site:** `gsutil rsync -r dbt/target gs://gammarips-dbt-docs` behind an auth-gated load balancer. Heavier, but keeps it off public GitHub.
   - Default to Pages unless the user says otherwise.

**CI:**
5. Create `.github/workflows/dbt-ci.yml`:
   - Trigger: `pull_request` on any path under `dbt/**` or `requirements.txt`.
   - Set up Python 3.12, install `dbt-core` + `dbt-bigquery` via `uv`.
   - Auth to BigQuery via a GCP service account key stored as a GitHub secret (`GCP_SA_KEY`). The SA needs `BigQuery Data Editor` + `BigQuery User` on a dedicated CI dataset like `profitscout-fida8.profitscout_dbt_ci`.
   - Run `dbt deps` → `dbt build --target ci`.
   - Upload `target/` as a workflow artifact on failure for debugging.
6. Add a `ci` target to `dbt/profiles.yml`:
   ```yaml
   gammarips:
     target: dev
     outputs:
       dev: { ... existing ... }
       ci:
         type: bigquery
         method: service-account-json
         keyfile_json: "{{ env_var('GCP_SA_KEY') | as_native }}"
         project: profitscout-fida8
         dataset: profitscout_dbt_ci
         threads: 4
         location: US
   ```
7. Before the first CI run, manually create the CI dataset: `bq mk --location=US profitscout-fida8:profitscout_dbt_ci`.

**Acceptance:**
- `dbt docs serve` renders locally and shows lineage for `fct_paper_trades` with column-level docs.
- A throwaway PR touching `dbt/models/metricflow_time_spine.sql` triggers the workflow, the workflow runs `dbt build` against `profitscout_dbt_ci`, and it goes green.
- CI dataset `profitscout_dbt_ci` exists in BigQuery.

### T1.3 — Stricter column tests

**Why:** Schema drift detection. The scanner emits enumerated values for `direction`, `exit_reason`, and `policy_gate`. If someone adds a new value, you want to know on the PR that introduced it, not three weeks later in a report.

**Steps:**
1. First, query the live ledger to see what values actually exist:
   ```bash
   bq query --use_legacy_sql=false "SELECT direction, COUNT(*) FROM profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2 GROUP BY 1"
   bq query --use_legacy_sql=false "SELECT exit_reason, COUNT(*) FROM profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2 GROUP BY 1"
   bq query --use_legacy_sql=false "SELECT policy_gate, COUNT(*) FROM profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2 GROUP BY 1"
   bq query --use_legacy_sql=false "SELECT premium_score, COUNT(*) FROM profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2 GROUP BY 1"
   ```
2. In `dbt/models/marts/fct_paper_trades.yml`, add:
   - `accepted_values` on `direction` with the enumerated list from step 1.
   - `accepted_values` on `exit_reason`.
   - `accepted_values` on `policy_gate` (if finite; if not, leave with just a description).
   - `dbt_utils.accepted_range` on `premium_score` with `min_value: 0, max_value: 3` (or whatever the actual range is).
3. Also add `not_null` on `is_completed_trade`, `is_winner`, `is_loser` — they're CASE expressions and should never be null.

**Acceptance:** `dbt test --profiles-dir .` shows all new tests passing. If any `accepted_values` test fails, that's a real finding — update the list to match the true vocabulary and flag it in the commit.

### T1.4 — `exposures.yml`

**Why:** Declares who consumes the semantic layer. Turns the dbt graph into a bidirectional impact analysis — `dbt ls --select +exposure:current_ledger_stats` tells you everything upstream of a given consumer. Prevents "I refactored a column and broke a downstream report I didn't know existed."

**Steps:**
1. Create `dbt/models/exposures.yml`:
   ```yaml
   version: 2
   exposures:
     - name: current_ledger_stats
       type: analysis
       maturity: high
       owner:
         name: GammaRips Engineer
       description: "Weekly read-only snapshot of the V3.1 forward paper ledger."
       depends_on:
         - ref('fct_paper_trades')
       url: https://github.com/[owner]/gammarips-engine/blob/main/scripts/ledger_and_tracking/current_ledger_stats.py
   ```
2. Leave hooks for future consumers (eval reports, agent arena dashboards) as placeholders — add them as you wire the actual consumers in T1.5 and Tier 2.

**Acceptance:** `dbt ls --select +exposure:current_ledger_stats --profiles-dir .` lists `fct_paper_trades`, both staging models, and both sources.

### T1.5 — Migrate `current_ledger_stats.py` to read from `fct_paper_trades`

**Why:** This is explicitly marked in `CLAUDE.md` as a "read-only weekly snapshot (no filter ranking, no winner search)," which makes it the ideal first Python consumer — it is **freeze-safe**. It also validates the whole point of the semantic layer: one definition of `win_rate`, one definition of `expectancy_pct`, consumed by anyone who needs it.

**Steps:**
1. Read `scripts/ledger_and_tracking/current_ledger_stats.py` first to understand its current query shape and output format.
2. Replace raw `FROM profit_scout.forward_paper_ledger_v3_hold2` queries with `FROM profitscout_dbt.fct_paper_trades`.
3. Replace any hand-rolled win-rate math with the semantic layer's numbers. Two options for how:
   - **Simple (recommended for v1):** just query the `fct_paper_trades` columns (`is_completed_trade`, `is_winner`, `realized_return_pct`) and compute the stats in Python. This is the minimal migration and proves the table works.
   - **Full MetricFlow (do later):** use the MetricFlow CLI (`dbt sl query --metrics win_rate,expectancy_pct`) to pull metrics directly. Requires `dbt-metricflow` package. More skill-demo value but also more surface area.
   - Default to Simple. Document the Full path in a TODO comment.
4. Run the script, compare output against the pre-migration version (should be identical — both are reading the same underlying rows).
5. Update `exposures.yml` with the real path to the script.

**Acceptance:** `python scripts/ledger_and_tracking/current_ledger_stats.py` produces byte-identical output before and after the migration. No filter-search logic has been added.

---

## Tier 2 — Expand domain coverage (the real Phase 4)

Goal: extend the semantic layer beyond the trading ledger to cover the other production pipelines. Every task here is freeze-independent because it targets the eval and agent-arena tables, not the trading cohort.

### T2.1 — Eval system semantic layer (biggest single item in this plan)

**Why:** `gammarips-eval` writes to `llm_traces_v1` and `llm_eval_results_v1`. Those are real production tables with no semantic layer. Building one matures the entire eval stack in parallel with the trading stack, and it is *completely* freeze-independent — the freeze is about trading gates, not about LLM observability.

**Read first:** `docs/EVAL-SYSTEM.md`, `docs/DECISIONS/2026-04-09-eval-system-v1.md`, and the live schemas:
```bash
bq show --schema --format=prettyjson profitscout-fida8:profit_scout.llm_traces_v1
bq show --schema --format=prettyjson profitscout-fida8:profit_scout.llm_eval_results_v1
```

**Steps:**
1. Add both tables to `dbt/models/staging/src_profitscout.yml` as new sources. Grain for `llm_traces_v1` is per-trace (probably `trace_id`). For `llm_eval_results_v1`, grain is likely `(trace_id, evaluator)` — confirm from the schema. Add freshness: warn 24h / error 72h on `scan_date`.
2. Create `dbt/models/staging/stg_llm_traces.sql` and `stg_llm_eval_results.sql`. 1:1 projections with type standardization and any obvious column renames. Do not drop columns — staging should be lossless.
3. Create `dbt/models/marts/fct_llm_traces.sql`:
   - One row per trace.
   - Derived columns: `total_input_tokens`, `total_output_tokens`, `total_cost_usd`, `latency_ms`, `is_error` (CASE on status/error fields).
   - Partition by `scan_date`, cluster by `(service, model_id)` to match the source table's clustering.
4. Create `dbt/models/marts/fct_llm_eval_results.sql`:
   - One row per `(trace_id, evaluator)`.
   - Derived columns: `passed` (boolean), `score_normalized` (0-1 if scores are on varied scales).
5. Build a new semantic model `dbt/models/marts/semantic_models/llm_eval_sm.yml` with:
   - Entity: `trace_id` (primary).
   - Dimensions: `scan_date`, `service`, `model_id`, `evaluator`.
   - Measures: `total_traces`, `total_eval_runs`, `total_passed`, `total_cost_usd`, `p50_latency_ms`, `p95_latency_ms` (use percentile aggregations — check if MetricFlow supports `percentile` natively; if not, compute on the fact table as pre-aggregated columns).
6. Extend `dbt/models/marts/metrics/performance_metrics.yml` (or create a new `eval_metrics.yml`) with:
   - `eval_pass_rate = total_passed / total_eval_runs`
   - `avg_cost_per_trace = total_cost_usd / total_traces`
   - `error_rate = total_errors / total_traces`
7. Add column-level docs and tests (`not_null` on grain, `accepted_values` on `service`, `model_id`, `evaluator`).
8. Register `gammarips-eval`'s weekly Firestore report script as an exposure in `exposures.yml`.

**Acceptance:** `dbt build` green. `fct_llm_traces` and `fct_llm_eval_results` both materialized. All new tests passing. `dbt docs serve` shows them in the lineage graph alongside the trading layer.

### T2.2 — Agent Arena semantic layer

**Why:** `agent_arena_picks`, `agent_arena_rounds`, and `agent_arena_consensus` are the debate layer. A semantic layer over them gives you agent-level metrics — consensus rate, flip rate, inter-agent disagreement, pick-vs-outcome correlation. This is how you'd eventually rank agents the same way you'd rank strategies, but for agents, not for gates, so the freeze doesn't apply.

**Read first:** `agent-arena/agents.py`, `agent-arena/main.py`, and the three table schemas:
```bash
bq show --schema --format=prettyjson profitscout-fida8:profit_scout.agent_arena_picks
bq show --schema --format=prettyjson profitscout-fida8:profit_scout.agent_arena_rounds
bq show --schema --format=prettyjson profitscout-fida8:profit_scout.agent_arena_consensus
```

**Steps:**
1. Add all three as sources in `src_profitscout.yml` with freshness thresholds.
2. Create `stg_agent_arena_picks.sql`, `stg_agent_arena_rounds.sql`, `stg_agent_arena_consensus.sql`.
3. Create a mart layer. Likely shape:
   - `fct_agent_picks` — one row per pick, with `agent_name`, `round_id`, `ticker`, `side`, `confidence`, `scan_date`.
   - `fct_agent_rounds` — one row per debate round, with `round_id`, `consensus_ticker`, `participant_count`, `did_consensus` flag.
4. Build a `fct_agent_outcomes` joining `fct_agent_picks` to `fct_paper_trades` on `(scan_date, ticker)` (NOT on `recommended_contract` — agent picks are at ticker level, not contract level — confirm this). This lets you compute per-agent hit rate against actual paper trades.
5. Semantic model with `agent_name` as a dimension enables queries like "win rate by agent" without writing any SQL.
6. Metrics: `agent_consensus_rate`, `agent_hit_rate`, `agent_flip_rate`.

**Acceptance:** `dbt build` green. Running `dbt sl query --metrics agent_hit_rate --group-by agent_name` (or the SQL equivalent) returns a sensible per-agent table.

### T2.3 — `seeds/regimes.csv` + `dim_regime`

**Why:** Regime boundaries are human judgment, not data — they belong in a seed file, not a computed table. Setting this up now means the machinery is ready the moment the post-war cohort accumulates enough data to compare. This is **freeze-safe** because you're building infra, not running comparisons.

**Steps:**
1. Create `dbt/seeds/regimes.csv`:
   ```csv
   regime_name,start_date,end_date,description
   pre_war,2020-01-01,2026-04-07,"Pre-ceasefire baseline including Iran shock"
   post_war,2026-04-08,9999-12-31,"Post-ceasefire regime; start of freeze accumulation"
   ```
2. Run `dbt seed --profiles-dir .` to materialize it as a BQ table.
3. Add `dbt/seeds/schema.yml` with column docs and a `unique` test on `regime_name`.
4. In `fct_paper_trades.sql`, add a LEFT JOIN onto `ref('regimes')` via date-range:
   ```sql
   LEFT JOIN {{ ref('regimes') }} r
     ON scan_date BETWEEN r.start_date AND r.end_date
   ```
5. Add `regime` as a categorical dimension in `paper_trades_sm.yml`.
6. **Explicitly document in `fct_paper_trades.yml`**: "The `regime` dimension exists for post-freeze epoch-by-epoch comparison. Do NOT use it to compare pre-war vs. post-war performance until the freeze lifts and the post-war cohort has ≥ 30 rows."

**Acceptance:** `dbt build` green. `SELECT regime, COUNT(*) FROM profitscout_dbt.fct_paper_trades GROUP BY 1` returns all 30 rows under `pre_war` and 0 under `post_war` (until new trades accumulate).

### T2.4 — `fct_signal_performance`

**Why:** `signal_performance` is the production post-trade tracking table (written by `win-tracker/`). Putting it behind staging + marts lets you join it to `fct_paper_trades` via `(scan_date, ticker, recommended_contract)` and compute reporting metrics like "paper entry vs. realized best exit in the 5 days after signal." Reporting-safe, not filter-search.

**Steps:**
1. Inspect schema: `bq show --schema --format=prettyjson profitscout-fida8:profit_scout.signal_performance`.
2. Add as a source, build staging, build `fct_signal_performance` with any standardized outcome flags.
3. Expose as a dimension on `fct_paper_trades` via a join, or keep as a separate fact table with `trade_id` as a foreign key — depends on the grain. If `signal_performance` is 1:1 with paper trades, inline-join. If it's 1:N (multiple lookback windows per trade), keep separate.

**Acceptance:** `dbt build` green. Any existing consumer of `signal_performance` can be re-pointed at `fct_signal_performance` in a follow-up PR.

---

## Tier 3 — Nice to have

### T3.1 — `dbt source freshness` in CI
You already declared the thresholds on `forward_paper_ledger_v3_hold2` in T0. A scheduled `dbt source freshness` in Cloud Scheduler (hitting a tiny Cloud Run service) or GitHub Actions turns that declaration into an actual alert. One YAML workflow, maybe 15 minutes.

### T3.2 — Snapshot `overnight_signals_enriched`
`dbt snapshot` captures SCD-2 history. If the enrichment pipeline ever overwrites an enriched row, you lose the original. A snapshot preserves the "signal as-of T" state. **Caveat:** this creates a new data dependency — think about retention and storage before enabling.

### T3.3 — `dim_ticker`
Classic warehouse pattern. If you can source sector/industry/float/avg-volume metadata (FMP is retired per the 2026-04-08 decision; check if Polygon's reference endpoints expose it), a `dim_ticker` gives sector-level slicing on every fact table for free. Low priority unless someone asks for sector breakouts.

### T3.4 — MetricFlow CLI queries in a report
The payoff of the semantic layer is consumer queries like `dbt sl query --metrics win_rate,expectancy_pct --group-by premium_score`. Pick one consumer (eval report? agent-arena dashboard?) and wire it to pull from MetricFlow instead of raw SQL. This is the skill-demo moment.

---

## Tier 4 — Do NOT do during the freeze

These are real future work, but they must **not** run on the pre-war cohort while the freeze is active:

- Migrating `backfill_april.py` or `simulate_live_execution.py` to the semantic layer. These are filter-search tools. Their migration is Phase 5, post-freeze.
- Any metric whose purpose is to rank gates, filters, or strategies on the 30-row cohort.
- Cross-regime comparisons (pre-war vs. post-war) until the post-war cohort has ≥ 30 rows and the freeze has formally lifted via a new `docs/DECISIONS/` entry.
- Incremental models on the ledger. Not needed at 30 rows; premature.
- Snapshots of the ledger itself. It's append-only-ish already; snapshotting it is the wrong tool.

If the user asks you to do any of these, push back. Reference `CLAUDE.md` and `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`.

---

## Command reference

```bash
# From /home/user/gammarips-engine/dbt/
DBT=/home/user/gammarips-engine/.venv_dbt/bin/dbt

# One-time
$DBT deps --profiles-dir .

# The hot loop
$DBT build --profiles-dir . --no-partial-parse

# Docs
$DBT docs generate --profiles-dir .
$DBT docs serve    --profiles-dir . --port 8081

# Source freshness
$DBT source freshness --profiles-dir .

# Targeted runs
$DBT run  --select fct_paper_trades --profiles-dir .
$DBT test --select source:profit_scout_fida8 --profiles-dir .
$DBT ls   --select +exposure:current_ledger_stats --profiles-dir .

# Seeds
$DBT seed --profiles-dir .

# Clean slate (nuke partial-parse + compiled artifacts)
$DBT clean --profiles-dir .
```

Installing or updating the venv:
```bash
VIRTUAL_ENV=/home/user/gammarips-engine/.venv_dbt uv pip install dbt-core dbt-bigquery
```

---

## Suggested session order

If you have two to three hours:
1. Read this doc, `dbt_implementation_summary.md`, and `CLAUDE.md`. Check the venv still works with `dbt --version`.
2. Run `dbt build` to confirm green state.
3. **Tier 1 bundle (T1.1 → T1.4)** — packages, docs, stricter tests, exposures. These are all small and reinforce each other.
4. **T1.5** — migrate `current_ledger_stats.py`. Smallest real Python consumer, validates the system top-to-bottom.
5. Commit Tier 1 as a single PR with a clear title like "dbt: Tier 1 infra (packages, docs, CI, tests, exposures)".

If you have a full day:
6. **T2.1** — eval system semantic layer. This is the biggest domain expansion and the one the user flagged as most valuable.

If you have more:
7. **T2.2 → T2.4** — agent arena, regimes seed, signal performance.

Do not skip Tier 1 to get to Tier 2. T1.2 (docs + CI) and T1.3 (stricter tests) will catch bugs in Tier 2 work that would otherwise hit production silently.

---

## Acceptance criteria for "tier N complete"

**Tier 1 complete when:**
- `dbt build` green with all T1.3 tests added.
- `dbt docs` site renders with full lineage.
- A PR triggers the CI workflow and it goes green against `profitscout_dbt_ci`.
- `current_ledger_stats.py` reads from `fct_paper_trades` and produces identical output.
- `exposures.yml` declares at least one real consumer.

**Tier 2 complete when:**
- `fct_llm_traces`, `fct_llm_eval_results`, `fct_agent_picks`, `fct_agent_rounds`, `fct_signal_performance` all exist and are tested.
- `dim_regime` seeded and joined into `fct_paper_trades` (with the freeze guardrail documented).
- New metrics defined for eval (`eval_pass_rate`, `avg_cost_per_trace`) and agent arena (`agent_hit_rate`).
- All Tier 1 infra (tests, docs, CI) covers the new models too — not just the trading layer.

**Tier 3 complete when:**
- `dbt source freshness` runs on a schedule and alerts on stale ledgers.
- At least one consumer pulls metrics via MetricFlow CLI, not raw SQL.
- Any T3 item not done has a concrete reason in this file's changelog.

---

## Changelog

- 2026-04-09: Initial plan written. Phase 1–3 validated (`PASS=18 ERROR=0`). Tier 1–3 scoped. Tier 4 freeze constraints listed.
