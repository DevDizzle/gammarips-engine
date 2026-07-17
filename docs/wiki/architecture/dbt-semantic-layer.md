Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-23-dbt-layer-rebuild.md
Date: 2026-07-17

# dbt semantic layer — reporting/analytics only, isolated dataset, read-side dedup

The dbt layer is LIVE production infra (2026-06-23): 25 models + 1 seed + 3 exposures + 6
metrics in the isolated `profitscout_dbt` dataset (us-central1), rebuilt automatically 06:30
ET Mon–Fri by a `dbt-runner` Cloud Run service + Scheduler. Scope is reporting/analytics
ONLY — it READS production BigQuery tables and does NOT touch trading execution.

Key fact for anyone reading marts: all five dup-prone sources are **deduped in staging** to
their grain (latest by timestamp), so marts are clean — mart uniqueness tests are ERROR
(assert the dedup) while source uniqueness tests stay WARN (surface the upstream bug).
Removed dup counts flagged the upstream bugs: overnight_signals 1940,
overnight_signals_enriched 329, enriched_option_outcomes 145, signal_performance 315,
llm_eval_results 3450 (~57%, an eval-writer idempotency bug, still backlog). Gotcha: the
source dataset `profit_scout` is in us-central1, NOT US.
