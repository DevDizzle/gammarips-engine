# Decision: LLM eval system v1 — monitoring-first, non-gating

- **Date:** 2026-04-09
- **Status:** accepted
- **Supersedes:** none (additive)

## Context

Four GammaRips services ship production LLM output every night —
`enrichment-trigger` (Gemini grounded-search flow-intent classification),
`agent-arena` (5-model debate), `overnight-report-generator` (Gemini
editorial synthesis), and the win-tracker / signal-notifier pair (post-hoc
notifications) — and none of them log raw prompts, raw responses, token
cost, or latency. There is no standing measurement of whether
`flow_intent` calls are correct, whether agent consensus tracks realized
returns, or whether the daily report is factually aligned with what the
market did the next day. Every after-the-fact analysis requires refetching
from Firestore JSON blobs and manually joining to `signal_performance`.
This is not sustainable as the stack grows.

At the time of writing, the V3.1 gate was frozen for accumulation per
`docs/archive/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`. V3 has
since been retired (2026-04-16) and V4 is the sole active pipeline. The
eval system's monitoring-only, non-gating posture remains correct regardless
of which trading pipeline is active.

## Decision

Ship `gammarips-eval`, a separate Cloud Run service that reads from a new
append-only trace table `profit_scout.llm_traces_v1` (written by an
instrumented shared library `libs/trace_logger`) and writes scored rows
to `profit_scout.llm_eval_results_v1`. A weekly scheduled endpoint
aggregates the results into a markdown digest in Firestore
`eval_reports/{iso_week}`. Four GammaRips-specific evaluators —
`flow_intent_accuracy`, `consensus_return_agreement`, `calibration`,
`report_factuality` — join against the ground-truth tables that already
exist (`signal_performance`, `signals_labeled_v1`). A vendored `quality`
LLM-as-judge evaluator (Gemini 3 Flash via Vertex) scores prose coherence
on agent-arena and report-generator traces. A regex-based `safety`
evaluator runs on the daily report.

### What this is NOT

- **Not a promotion gate.** The framework's `decision_engine` is not
  imported. No code path consults eval results to decide whether to
  enrich, debate, publish, or trade.
- **Not a CI block.** No GitHub Action, no pre-merge check. CI/CD gating
  is explicitly out of scope for v1 and deferred until the trace base
  is large enough to establish stable thresholds.
- **Not real-time.** `/eval/batch` runs hourly via Cloud Scheduler on a
  watermark; worst-case lag is ~1 hour. Streaming is a phase-2 concern.
- **Not a trading signal.** Eval scores never feed back into strategy.

### Non-blocking guarantees

1. `trace_logger.TraceLogger.log()` swallows every exception. A BQ
   outage cannot break enrichment or the debate.
2. Each instrumented service imports `trace_logger` inside a `try`
   block; if the import fails the service runs exactly as it did pre-
   instrumentation.
3. The `TRACE_LOGGING_ENABLED` env var starts at `false` on every
   service. It is flipped on per-service only after a dry-run deploy
   and a smoke test confirms rows land in BQ.
4. Eval writes are keyed by a deterministic `eval_id =
   sha256(trace_id|evaluator|eval_version)[:32]` so re-runs are
   idempotent even though BQ streaming inserts don't enforce uniqueness.

### Schemas

- `profit_scout.llm_traces_v1` — append-only trace table, partitioned
  on `scan_date`, clustered on `(service, model_id)`. One row per LLM
  call across all instrumented services. See
  `scripts/ledger_and_tracking/create_llm_traces_v1.py` for the DDL.
- `profit_scout.llm_eval_results_v1` — append-only scoring table,
  partitioned on `scan_date`, clustered on `(service, evaluator)`. See
  `scripts/ledger_and_tracking/create_llm_eval_results_v1.py`.

### Services touched

- **New:** `gammarips-eval/` (Cloud Run, FastAPI + Uvicorn).
- **New lib:** `libs/trace_logger/` (local path install, vendored into
  each service's build context by `deploy.sh`).
- **Modified:** `enrichment-trigger/{main.py,Dockerfile,deploy.sh,
  requirements.txt}`, `agent-arena/{agents.py,main.py,Dockerfile,
  deploy.sh,requirements.txt}`, `overnight-report-generator/{main.py,
  Dockerfile,deploy.sh}`. All edits are guarded by try/except imports
  and by the `TRACE_LOGGING_ENABLED` env flag.

## Consequences

- **Positive:** we finally have a standing measurement of whether
  `flow_intent` and agent consensus track realized returns. When the
  accumulation window closes and the gate is unfrozen, we will have a
  real evidence base to point at.
- **Positive:** raw prompts and responses are archived in BQ. If a
  model vendor changes behavior silently (as happened with FMP), we can
  diff prompt hashes and spot drift.
- **Negative:** one more service to deploy, monitor, and keep cheap.
  The cost budget is `EVAL_MAX_SPEND_USD=2.0` per `/eval/batch` run.
- **Negative:** two new BQ tables live in `profit_scout`. They carry
  the `llm_` prefix to distinguish them from trading ledgers, and their
  partition expirations should be revisited once volume is known.
- **Open:** vendored `hallucination` and `factual` evaluators are v1
  stubs. Full NLI / embedding ports are deferred.

## Rollout

See the plan file
`/home/user/.claude/plans/idempotent-painting-stroustrup.md` (12-step
rollout sequence, starting with the two DDL scripts and ending with
`gammarips-review` audit before merge). Per G-Stack rules in
`CLAUDE.md`, `gammarips-review` must pass before the branch is
considered ready.
