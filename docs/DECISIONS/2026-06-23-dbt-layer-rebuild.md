# 2026-06-23 — dbt semantic layer: full rebuild as production infra

**Status:** COMPLETE & LIVE (2026-06-23). Built green (`PASS=124 WARN=5 ERROR=0`),
merged to `master` + pushed, gammarips-review PASS, and the `dbt-runner` Cloud Run
service + daily Scheduler are deployed and smoke-tested. Layer = 25 models + 1 seed
+ 3 exposures + 6 metrics in `profitscout_dbt` (us-central1), rebuilt automatically
06:30 ET Mon–Fri. Only optional items remain (CI secret; `LEDGER_SOURCE=dbt` flip).

Build notes: source dataset `profit_scout` is in **us-central1** (not US). Auth here
used a short-lived token minted from the gcloud `eraphaelparra@gmail.com` session
(ADC was bound to the wrong identity, `evan@`).

**Read-side dedup complete (`6e1736a`):** all five dup-prone sources are deduped in
staging to their grain (latest by timestamp), so every mart is clean; mart
uniqueness tests are ERROR (assert the dedup), source uniqueness tests stay WARN
(surface the upstream bug). Removed: overnight_signals 1940, overnight_signals_
enriched 329, enriched_option_outcomes 145, signal_performance 315, **llm_eval_
results 3450 (~57% — eval-writer idempotency bug, BACKLOG root-cause fix).** Final
build: PASS=124 WARN=5 ERROR=0; the 5 WARNs are all source-level dup findings.
**Scope:** Reporting/analytics layer only. Reads production BigQuery tables; does
**not** touch trading execution. New isolated dataset `profitscout_dbt`.

## Why this exists / what happened before

A dbt Core semantic layer was built and validated green (`PASS=18 ERROR=0`) on
2026-04-09 over the (then-V3) paper-trading ledger. On 2026-04-13, commit `6f0686f`
("V4 pipeline + repo cleanup") added the entire `dbt/` directory to `.gitignore`
("incomplete/stale, not in use"), bundling it with virtualenvs. Because it was
ignored it was never committed; the untracked source was later destroyed by a
working-tree clean and is unrecoverable from git (only the plan `.md` survives).

**Root-cause fix (this change):** ignore **only** `dbt/profiles.yml` (the connection
profile) plus regenerable build artifacts (`target/`, `dbt_packages/`, `logs/`).
Never ignore `dbt/` itself. The project source is committed.

## Reconciliation vs. the stale exec-plan

The original plan (`docs/EXEC-PLANS/dbt-semantic-layer.md`) is a usable skeleton but
stale. This rebuild reconciles it to the live system:

- Sources point at **current** tables, not retired V3 (`forward_paper_ledger_v3_hold2`).
- **Agent-arena is dropped** (service retired — no modeling).
- **Adds** `forward_paper_ledger_intraday` (V7 GIGO, the current live ledger),
  `enriched_option_outcomes` (the ~50× counterfactual option-PnL label table),
  and the shadow tables (`paper_shadow_topscore`, `paper_shadow_intraday`).
- Freeze rules in the old doc are historical (V3-era) and do not apply.

## Domains

| Domain | Source tables |
|---|---|
| Trading | `forward_paper_ledger`, `forward_paper_ledger_intraday`, `overnight_signals_enriched`, `overnight_signals` |
| Outcomes / research | `enriched_option_outcomes`, `signal_performance`, `paper_shadow_topscore`, `paper_shadow_intraday` |
| Eval | `llm_traces_v1`, `llm_eval_results_v1` |

## Canonical-metrics decision

All performance metrics (`expectancy_pct`, `win_rate`, average return, etc.) are
defined once in the dbt metrics layer, on **option PnL, not the underlying**. This
encodes the project's most-repeated analysis footgun as a single source of truth so
consumers stop re-deriving it. Rationale: realized backfill shows underlying-up 54%
vs option-up 41% — evaluating on the underlying is misleading.

## Plan of record (5 phases, each a commit)

- **P0 — Foundation:** un-ignore `dbt/` (secret-only), scaffold project, `dbt_utils`,
  bump dbt-core 1.11.8→1.11.11, commit the skeleton. ✅
- **P1 — Trading core:** sources + `stg_*`; marts `fct_paper_trades` (3-day),
  `fct_paper_trades_intraday` (V7), `fct_signals_enriched`, `agg_paper_performance`
  (canonical option-PnL rollup) + MetricFlow semantic model/metrics; tests. ✅
- **P2 — Outcomes/research:** `fct_enriched_option_outcomes` (+ `agg_pool_outcomes`),
  `fct_signal_performance`, `fct_shadow_topscore`, `fct_shadow_intraday`,
  `regimes.csv` seed → `dim_regime`. ✅
- **P3 — Eval:** `fct_llm_traces`, `fct_llm_eval_results`, `agg_llm_cost`,
  `agg_eval_quality` (cost/latency/error + pass-rate rollups). ✅
- **P4a — Platform scaffolding (no deploy):** `exposures.yml`, `scripts/dbt_docs.sh`,
  `.github/workflows/dbt-ci.yml`. ✅
- **P4b — Platform deploy: LIVE (2026-06-23).** `dbt-runner` Cloud Run service
  deployed (`https://dbt-runner-hrhjaecvhq-uc.a.run.app`, private). Two Cloud
  Scheduler jobs ENABLED: `dbt-daily-build` (POST `/`, 06:30 ET Mon–Fri) +
  `dbt-source-freshness` (POST `/freshness`, 07:00 ET). Compute SA granted
  `run.invoker`. CI dataset `profitscout_dbt_ci` created (us-central1). Smoke-test
  PASS: triggered run rebuilt the marts at 22:31 UTC (Scheduler→OIDC→Run→build→BQ).
  STILL OPTIONAL/operator: `GCP_SA_KEY` GitHub secret for CI (recommend skip or
  keyless WIF — runner already covers refresh); flip `LEDGER_SOURCE=dbt` to cut
  `current_ledger_stats.py` over to the mart.

## Operator runbook to unblock Phase 4b

1. `gcloud auth application-default login` (as a user with BQ on `profitscout-fida8`).
2. `cd dbt && cp profiles.yml.example profiles.yml`
3. `/home/user/gammarips-engine/.venv_dbt/bin/dbt deps --profiles-dir .`
4. `dbt build --profiles-dir .` → materializes everything into `profitscout_dbt`,
   runs all tests. Paste any failures (most likely a `select *` column mismatch).
5. Once green: `bq mk --location=us-central1 profitscout-fida8:profitscout_dbt_ci`
   (us-central1, NOT US — must match the source dataset's location), add the
   `GCP_SA_KEY` GitHub secret, then run `gammarips-review` and proceed to P4b.
   Grant the CI/runner SA least privilege: `BigQuery Data Editor` on the dbt
   dataset(s) + `Data Viewer` on `profit_scout` — never write on `profit_scout`.

## Decisions locked (2026-06-23)

- Refresh: **Cloud Run + Cloud Scheduler** (daily build) **and** GitHub Actions (PR CI).
- Model **both** ledgers (3-day legacy + V7 intraday) as separate facts.
- Dataset: reuse `profitscout_dbt`.

## Governance

- Layer is read-only over production and isolated in its own dataset, so model work
  is low-risk. Before Phase 4 wires a **scheduled live build**, run `gammarips-review`.
- `dbt build` requires BigQuery `bigquery.jobs.create`; the agent sandbox lacks it,
  so green-build validation runs on the operator's OAuth creds or in CI.

## Non-goals

- Does not change picks, gates, or execution. No incremental models (data is tiny).
- Does not snapshot the append-only ledger.
