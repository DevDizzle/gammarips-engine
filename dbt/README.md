# GammaRips dbt semantic layer

Production analytics/reporting layer over the GammaRips BigQuery tables. It sits
**downstream** of the Python Cloud Run pipeline (it reads the tables those services
write) and does **not** touch trading execution. Target dataset: `profitscout_dbt`.

> **History / do-not-repeat:** an earlier version of this layer was built and validated
> green on 2026-04-09, then the whole `dbt/` directory was wrongly added to `.gitignore`
> (commit `6f0686f`) and never committed — the untracked source was later lost to a
> working-tree clean. Only `dbt/profiles.yml` (the connection profile) is ignored now.
> See `docs/DECISIONS/2026-06-23-dbt-layer-rebuild.md`.

## Domains modeled

| Domain | Source tables |
|---|---|
| Trading | `forward_paper_ledger` (3-day), `forward_paper_ledger_intraday` (V7 GIGO), `overnight_signals_enriched`, `overnight_signals` |
| Outcomes / research | `enriched_option_outcomes`, `signal_performance`, `paper_shadow_topscore`, `paper_shadow_intraday` |
| Eval | `llm_traces_v1`, `llm_eval_results_v1` |

Agent-arena is intentionally **not** modeled (service is retired).

## Layout

```
models/
  staging/   # stg_*  — lossless 1:1 projections of sources (views)
  marts/     # fct_*  — analytics-ready facts (tables) + metrics + semantic models
seeds/       # regimes.csv -> dim_regime
```

## Canonical metrics rule

All return/performance metrics are defined **once** here, on **option PnL, not the
underlying** (the project's recurring footgun). Consumers read these definitions
instead of re-deriving win-rate / expectancy in each script.

## Commands

```bash
DBT=/home/user/gammarips-engine/.venv_dbt/bin/dbt
cd dbt

# one-time
cp profiles.yml.example profiles.yml         # then `gcloud auth application-default login`
$DBT deps --profiles-dir .

# the hot loop (run models + tests in DAG order)
$DBT build --profiles-dir .

# connection / config sanity check
$DBT debug --profiles-dir .

# docs site (column-level lineage)
$DBT docs generate --profiles-dir . && $DBT docs serve --profiles-dir . --port 8081
```
