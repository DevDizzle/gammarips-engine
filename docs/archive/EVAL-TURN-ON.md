# Eval system — turn-on runbook

> This is the short, follow-along checklist for flipping the eval system
> from "deployed but silent" to "actively logging and scoring." For the
> full architecture, schemas, and rationale, see `docs/EVAL-SYSTEM.md`
> and `docs/DECISIONS/2026-04-09-eval-system-v1.md`.

## Current state (as of 2026-04-09)

Everything is **built, deployed, and safely OFF**. The code that writes
LLM traces to BigQuery exists in every instrumented service, but it's
gated by an env var `TRACE_LOGGING_ENABLED=false` on each Cloud Run
service. Until you flip that flag, nothing is logged and nothing is
scored.

What's live:

- **BigQuery tables** (already created, empty):
  - `profitscout-fida8.profit_scout.llm_traces_v1` — raw LLM calls, 180d partition
  - `profitscout-fida8.profit_scout.llm_eval_results_v1` — scored rows, 365d partition
- **Instrumented Cloud Run services** (deployed, flag OFF):
  - `enrichment-trigger`
  - `agent-arena`
  - `overnight-report-generator`
- **New Cloud Run service** (deployed, healthy):
  - `gammarips-eval` at `https://gammarips-eval-hrhjaecvhq-uc.a.run.app`
- **Cloud Scheduler jobs** (ENABLED, but currently scoring nothing
  because no traces exist yet):
  - `gammarips-eval-daily` — weekday 07:00 ET → `POST /eval/batch`
  - `gammarips-eval-weekly` — Monday 08:00 ET → `POST /eval/report`

## Why daily instead of hourly

All GammaRips LLM calls happen in a 90-minute window, 05:00–06:30 ET
(overnight scan → enrichment → agent arena → report generator). One
daily run at 07:00 ET catches the whole batch in a single pass. The
first scheduled run is set up that way.

**Subtlety — ground-truth lag:** two of the GammaRips evaluators
(`flow_intent_accuracy`, `consensus_return_agreement`) join to
`signal_performance`, which win-tracker populates ~3 days after the
scan. So on the morning after a scan:

- `quality`, `safety`, `calibration`, `report_factuality` → score
  immediately
- `flow_intent_accuracy`, `consensus_return_agreement` → return `None`
  (no GT yet)

That's fine. The weekly report's GT-dependent numbers will describe
trades from 3+ days back, which is exactly what "ground truth" means.
If you later want to re-score old traces once their GT arrives, add a
second scheduler job with an explicit 7-day lookback; v1 doesn't.

## Turn-on procedure

### Step 1 — flip enrichment-trigger first

This is the safest service to start with: single LLM call per ticker,
simple schema, easy to verify.

```bash
gcloud run services update enrichment-trigger \
  --project=profitscout-fida8 --region=us-central1 \
  --update-env-vars=TRACE_LOGGING_ENABLED=true
```

Gcloud will print a revision number. That's it — the flag is live on
the new revision. Trading behavior is unchanged; the only new behavior
is a fire-and-forget BigQuery insert after each Gemini call.

### Step 2 — wait for the next overnight scan

Your existing `overnight-enrichment` Cloud Scheduler job runs weekdays
at 05:00 ET. You do nothing. Just wait one business day.

### Step 3 — verify rows landed in BigQuery

Next morning, run:

```bash
bq query --use_legacy_sql=false '
SELECT
  service,
  COUNT(*) AS n,
  MIN(created_at) AS first_seen,
  MAX(created_at) AS last_seen,
  ROUND(SUM(cost_usd), 4) AS total_cost_usd,
  ROUND(AVG(latency_ms), 0) AS mean_latency_ms
FROM `profitscout-fida8.profit_scout.llm_traces_v1`
WHERE scan_date = CURRENT_DATE()
GROUP BY service'
```

**Expected:** one row, `service = enrichment`, `n` ≈ number of tickers
the scan enriched (typically 10–30).

**If you see no rows:** something is wrong. Check:

```bash
# Confirm the flag is actually set on the current revision
gcloud run services describe enrichment-trigger \
  --project=profitscout-fida8 --region=us-central1 \
  --format='value(spec.template.spec.containers[0].env)'

# Look for trace_logger errors in the service logs
gcloud run services logs read enrichment-trigger \
  --project=profitscout-fida8 --region=us-central1 --limit=50 \
  | grep -i 'trace'
```

Do NOT flip the other two services until enrichment-trigger is
confirmed writing rows.

### Step 4 — flip agent-arena and overnight-report-generator

Once enrichment-trigger is confirmed working, turn on the other two:

```bash
gcloud run services update agent-arena \
  --project=profitscout-fida8 --region=us-central1 \
  --update-env-vars=TRACE_LOGGING_ENABLED=true

gcloud run services update overnight-report-generator \
  --project=profitscout-fida8 --region=us-central1 \
  --update-env-vars=TRACE_LOGGING_ENABLED=true
```

### Step 5 — verify all three after the next overnight window

```bash
bq query --use_legacy_sql=false '
SELECT service, call_site, COUNT(*) AS n, ROUND(SUM(cost_usd),4) AS cost_usd
FROM `profitscout-fida8.profit_scout.llm_traces_v1`
WHERE scan_date = CURRENT_DATE()
GROUP BY service, call_site
ORDER BY service, call_site'
```

**Expected:**

| service | call_site | rough n |
|---|---|---|
| enrichment | fetch_and_analyze_news | one per enriched ticker |
| agent_arena | round1_pick_{claude,gemini,...} | ~5 per agent per debate |
| agent_arena | round2_attack_* | ~5 |
| agent_arena | round3_defend_* | ~5 |
| agent_arena | round4_final_* | ~5 |
| report_generator | generate_report_content | 1 |

## What runs automatically after turn-on

- **Every weekday 07:00 ET** — `gammarips-eval-daily` hits
  `/eval/batch`. It pulls any new traces since the watermark, joins
  ground truth, runs the evaluator chain, and writes scored rows. On
  the first run after turn-on, it will find and score the previous
  night's traces.
- **Every Monday 08:00 ET** — `gammarips-eval-weekly` hits
  `/eval/report`. It aggregates the week's scored rows into a markdown
  digest and writes it to Firestore `eval_reports/{iso_week}`.

Neither job touches trading code. Neither job is a promotion gate.
Both are safe to fail — worst case you get no eval row for that
trace, which is a diagnostic nuisance, not a trading problem.

## Reading the weekly report

After the first Monday following turn-on, the digest will appear at:

```
Firestore → eval_reports/2026-W{ISO week number}
```

Fields:

- `markdown` — the rendered report body (this is the human-readable part)
- `aggregates.pass_rates` — per (service, evaluator) N, mean_score, pass_rate
- `aggregates.cost_by_model` — token/cost totals per model
- `aggregates.worst_traces` — the 5 lowest-scored traces of the week,
  with their `trace_id`s so you can pull them from `llm_traces_v1` for
  root cause analysis

Quick look via gcloud:

```bash
gcloud firestore documents describe \
  "projects/profitscout-fida8/databases/(default)/documents/eval_reports/2026-W15"
```

Or open the Firestore console and browse to the `eval_reports`
collection.

## Emergency kill switch

If something goes wrong and you need to stop trace logging immediately:

```bash
# Flip any single service off
gcloud run services update enrichment-trigger \
  --project=profitscout-fida8 --region=us-central1 \
  --update-env-vars=TRACE_LOGGING_ENABLED=false

# Or pause the daily eval job
gcloud scheduler jobs pause gammarips-eval-daily \
  --project=profitscout-fida8 --location=us-central1
```

Trading is unaffected in every scenario — the trace logger is
fire-and-forget and the eval service is read-only against the trading
tables.

## Rollback (if you want to tear the whole thing down)

```bash
# 1. Flip the flags off
for svc in enrichment-trigger agent-arena overnight-report-generator; do
  gcloud run services update $svc \
    --project=profitscout-fida8 --region=us-central1 \
    --update-env-vars=TRACE_LOGGING_ENABLED=false
done

# 2. Pause the scheduler jobs
gcloud scheduler jobs pause gammarips-eval-daily \
  --project=profitscout-fida8 --location=us-central1
gcloud scheduler jobs pause gammarips-eval-weekly \
  --project=profitscout-fida8 --location=us-central1

# 3. (optional) Delete the gammarips-eval service entirely
gcloud run services delete gammarips-eval \
  --project=profitscout-fida8 --region=us-central1 --quiet

# 4. (optional) Drop the BQ tables
bq rm -f -t profitscout-fida8:profit_scout.llm_traces_v1
bq rm -f -t profitscout-fida8:profit_scout.llm_eval_results_v1
```

None of this touches trading.

## Known minor issues

1. **`GET /healthz` returns 404** from Google's frontend on the
   `gammarips-eval` service. The route IS registered in FastAPI
   (`/openapi.json` lists it), but the Google Front End appears to
   reserve that path. `POST /eval/batch` works correctly. Rename to
   `/ping` in a future deploy if needed. Not blocking — schedulers
   don't use the healthz endpoint.

2. **Vendored `hallucination` and `factual` evaluators are stubs.**
   Both return `None` unconditionally in v1. The full ports (NLI
   cross-encoder + embedding-based claim verification) were deferred
   because they pull in torch/transformers and bloat cold starts.
