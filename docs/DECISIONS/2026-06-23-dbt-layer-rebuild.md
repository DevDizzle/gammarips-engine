# 2026-06-23 — dbt semantic layer: full rebuild as production infra

**Status:** In progress. Phases 0–2 complete (`b0817f2`, `bf40fbc`, `a771cea`).
Phases 3–4 pending. Live `dbt build` validation still owed (operator OAuth / CI).
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
- **P3 — Eval:** `fct_llm_traces`, `fct_llm_eval_results`; cost/latency/pass-rate metrics.
- **P4 — Platform:** `dbt docs` site, GitHub Actions CI (`profitscout_dbt_ci`),
  Cloud Run + Cloud Scheduler daily build + source freshness, `exposures.yml` and
  re-point `current_ledger_stats.py` (and researcher workflows) at the marts.

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
