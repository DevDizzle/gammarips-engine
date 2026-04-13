# GammaRips eval system

The eval system measures the quality of every LLM/agent call made by the
GammaRips production services. It is **monitoring-first, non-gating** —
see `docs/DECISIONS/2026-04-09-eval-system-v1.md` for the posture.

## Architecture at a glance

```
4 LLM-producing services (instrumented via libs/trace_logger)
  enrichment-trigger, agent-arena, overnight-report-generator
         │
         ▼
profit_scout.llm_traces_v1   (append-only, one row per LLM call)
         │
         ▼
gammarips-eval  (Cloud Run)
  POST /eval/batch   (hourly, Cloud Scheduler)
      → pulls traces since watermark
      → joins ground truth from signal_performance
      → runs evaluator chain
      → writes profit_scout.llm_eval_results_v1
  POST /eval/report  (weekly, Mon 08:00 ET)
      → aggregates the week's results
      → writes Firestore eval_reports/{iso_week}
```

## Data model

### `profit_scout.llm_traces_v1`

Append-only, partitioned on `scan_date`, clustered on `(service,
model_id)`. Written by `libs/trace_logger.TraceLogger.log()` at every
LLM call site. See `scripts/ledger_and_tracking/create_llm_traces_v1.py`
for the authoritative schema.

Key columns:
- `trace_id` — uuid4, primary key
- `service` — `enrichment`, `agent_arena`, `report_generator`
- `call_site` — e.g. `fetch_and_analyze_news`, `round1_pick_claude`
- `run_id` — correlates all traces in one service invocation
- `prompt`, `response_text`, `response_parsed` — full payload (no redaction)
- `prompt_hash`, `inputs_hash` — sha256 for drift detection
- `input_tokens`, `output_tokens`, `latency_ms`, `cost_usd`
- `status` — `ok` | `parse_error` | `api_error` | `timeout`

### `profit_scout.llm_eval_results_v1`

Append-only, partitioned on `scan_date` (365d expiration), clustered on
`(service, evaluator)`. Written by `gammarips-eval/runner.py`. See
`scripts/ledger_and_tracking/create_llm_eval_results_v1.py`.

**Deduplication:** `eval_id` is deterministic — `sha256(trace_id |
evaluator | eval_version)[:32]` — so re-runs of `/eval/batch` over
overlapping windows are semantically idempotent. **But:** BigQuery
streaming inserts do NOT enforce uniqueness, so physical duplicate rows
can exist. **All consumer queries MUST dedupe on `eval_id`:**

```sql
SELECT *
FROM `profitscout-fida8.profit_scout.llm_eval_results_v1`
WHERE scan_date BETWEEN '2026-04-07' AND '2026-04-13'
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY eval_id ORDER BY created_at DESC
) = 1
```

The weekly report builder in `gammarips-eval/report.py` applies this
dedup pattern in its aggregation queries. A daily MERGE-based dedup
job is tracked as future work but is not required for correct report
numbers.

Key columns:
- `eval_id` — deterministic sha256 of `(trace_id, evaluator, eval_version)`
- `trace_id` — FK to `llm_traces_v1`
- `evaluator`, `eval_version`, `judge_model`
- `score` (0.0-1.0), `passed` (bool)
- `details` (JSON — evaluator-specific breakdown)
- `ground_truth_source` — `signal_performance`, etc.

## Evaluators

Registered in `gammarips-eval/evaluators/__init__.py`. Each evaluator is
a pure `(trace, gt_context, config) -> EvalResult | None` callable.
Return `None` to mean "not applicable, don't write a row".

### GammaRips-specific

| Name | Scope | Signal |
|---|---|---|
| `flow_intent_accuracy` | enrichment | DIRECTIONAL/HEDGING call vs 3d peak_return_pct |
| `consensus_return_agreement` | agent_arena round4_final | final pick direction vs realized return |
| `calibration` | enrichment + arena | per-trace calibration (Brier-like) of catalyst_score/conviction |
| `report_factuality` | report_generator | Gemini LLM judge: report stance vs next-day outcomes |

### Vendored (adapted from genai-eval-framework)

| Name | Scope | Signal |
|---|---|---|
| `quality` | agent_arena + report_generator | Gemini judge: coherence/fluency/relevance (1-5 → 0-1) |
| `safety` | report_generator | regex PII / advice-language / profanity |
| `hallucination` | — | **v1 stub** (always returns None); NLI port deferred |
| `factual` | — | **v1 stub**; embedding port deferred |

Which evaluators run against which service is configured in
`gammarips-eval/config.yaml` under `service_evaluators`.

## Instrumentation pattern

Every instrumented service follows the same pattern:

1. `try: from trace_logger import TraceLogger, TraceRecord` at import
   time. If it fails, the service runs normally — no instrumentation.
2. A module-level `_trace_logger = TraceLogger()` — lazy BQ client init.
3. At each LLM call site:
   - `_t0 = time.monotonic()` before the call.
   - On success, build a `TraceRecord(service=..., call_site=...,
     run_id=..., scan_date=..., prompt=..., response_text=...,
     response_parsed=..., input_tokens=..., output_tokens=...,
     latency_ms=int((time.monotonic()-_t0)*1000), status="ok")`
     and call `_trace_logger.log(record)`.
   - On error, the same but with `status="api_error"` or
     `"parse_error"` and `error=str(e)[:500]`.
4. All trace calls are wrapped in an inner `try/except Exception: pass`
   so they can never raise to the caller.

The `TRACE_LOGGING_ENABLED` env var is the kill switch (default
`"false"`). Deploy with it off, smoke test, flip on.

## Shared lib: `libs/trace_logger/`

Local path install. Each service's `deploy.sh` stages a copy of
`libs/trace_logger/` into `./_trace_logger_vendor/` before running
`gcloud run deploy --source=.`, and the service's `Dockerfile` runs
`pip install /opt/trace_logger`. The vendor dir is in `.gitignore` and
cleaned up by a shell `trap` in `deploy.sh`.

Package contents:
- `trace_logger/records.py` — `TraceRecord` dataclass, hash helpers
- `trace_logger/pricing.py` — per-model `(in_per_1k, out_per_1k)` table
- `trace_logger/logger.py` — `TraceLogger` with fire-and-forget semantics

## Adding a new evaluator

1. Create a new module under `gammarips-eval/evaluators/gammarips/`
   (or `vendored/`) with an `evaluate(trace, gt_context, config)`
   function returning `EvalResult | None`.
2. Import it in `gammarips-eval/evaluators/__init__.py` and add it to
   the `REGISTRY` dict.
3. Add the evaluator name under the relevant service in
   `gammarips-eval/config.yaml` → `service_evaluators`.
4. Set a pass threshold under `thresholds`.
5. Redeploy `gammarips-eval`; the runner picks it up automatically.

## Adding a new instrumented service

1. Add `try: from trace_logger import TraceLogger, TraceRecord` at the
   top of the service's main module.
2. Instantiate `TraceLogger()` at module scope.
3. Wrap each LLM call per the instrumentation pattern above.
4. Update `deploy.sh` with the vendor-stage + trap snippet:
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   VENDOR_DIR="${SCRIPT_DIR}/_trace_logger_vendor"
   rm -rf "${VENDOR_DIR}"
   cp -r "${SCRIPT_DIR}/../libs/trace_logger/." "${VENDOR_DIR}"
   trap 'rm -rf "${VENDOR_DIR}"' EXIT
   ```
5. Update the `Dockerfile` with the COPY + pip install snippet:
   ```dockerfile
   COPY _trace_logger_vendor/ /opt/trace_logger/
   RUN pip install --no-cache-dir /opt/trace_logger
   ```
6. Add `TRACE_LOGGING_ENABLED=false` to `--set-env-vars`. Flip on only
   after a successful dry-run deploy.
7. Add the service to `gammarips-eval/config.yaml` with the evaluator
   chain you want it scored against.

## Reading the weekly report

Find it at Firestore `eval_reports/{iso_week}` (e.g. `2026-W15`). The
`markdown` field is the rendered digest; `aggregates` is the raw data
behind it. The markdown contains:

1. Pass rates by `(service, evaluator)`.
2. Cost & call volume by `(service, model_id)`.
3. The worst 5 traces of the week (by score), keyed by `trace_id` so
   they can be pulled from `llm_traces_v1` for root-cause.

## Verification commands

```bash
# Count traces written in the last 24h, broken out by service
bq query --use_legacy_sql=false '
  SELECT service, COUNT(*) AS n, AVG(latency_ms) AS mean_latency_ms,
         SUM(cost_usd) AS total_cost
  FROM `profitscout-fida8.profit_scout.llm_traces_v1`
  WHERE scan_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  GROUP BY service'

# Smoke-test /eval/batch in dry-run mode
curl -X POST https://gammarips-eval-XXXX.run.app/eval/batch \
  -H 'Content-Type: application/json' \
  -d '{"limit": 20, "dry_run": true}'

# Build this week's report (dry run)
curl -X POST https://gammarips-eval-XXXX.run.app/eval/report \
  -H 'Content-Type: application/json' \
  -d '{"dry_run": true}'
```

## Out of scope for v1

- Promotion / CI gates
- Real-time / streaming eval
- Human-in-the-loop review inbox
- NLI hallucination evaluator (stubbed)
- Embedding factual evaluator (stubbed)
- Multi-tenancy, Firebase auth, Slack UI
