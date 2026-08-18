# 2026-08-17 — LLM cost accounting: real rates, and the tournament gets traced

**Status:** implemented, NOT yet deployed (review gate pending)
**Services:** `libs/trace_logger` (every consumer), `signal-judge` (newly instrumented)
**Redeploy also required to take effect:** `enrichment-trigger`, `overnight-report-generator`

## What happened

The owner asked what the daily bracket tournament costs. BigQuery could not
answer, for two independent reasons.

**1. The tournament wrote no traces.** `signal-judge` was the last LLM caller in
the pipeline with no `trace_logger` wiring. Its cost had to be rebuilt from Cloud
Monitoring token counts (`aiplatform.../token_count`, filtered to
`model_user_id="gemini-3.1-pro-preview"`, which only this service calls).

**2. The rows that did exist understated the bill by ~26x.**
`libs/trace_logger/pricing.py` priced `gemini-3.5-flash` at 0.000075/0.0003 per
1K tokens. The rate that bills the project is 0.0015/0.009. So 30 days of
enrichment logged `$0.216` against a real `~$5.59`. Across the table's life,
5,305 flash rows log `$1.54` against roughly `$40`.

This is the worst failure mode in the doctrine: a cost column that reconciles
perfectly with itself and is wrong by an order of magnitude.

## Measured cost of the tournament (the answer)

Cloud Monitoring, 41 run-days, priced at the catalog rate ($2.00/M in,
$12.00/M out for the Gemini 3.0 / 3.1 Pro text SKU family):

| | per run-day |
|---|---|
| LLM calls | 3 (one per bracket seed) |
| Input tokens | ~44,000 = $0.09 |
| Output tokens, thinking included | ~11,000 = $0.13 |
| `signal-judge` Cloud Run compute | ~$0.002 |
| **Total** | **~$0.25 median** (mean $0.27, range $0.16 to $0.49) |

That is ~$5.75/month over 21 trading days, ~$69/year, and ~24% of all Vertex
spend on the project (~$21.60 per 30 days, the rest being Flash work).

Three calls, not the nine the pool cap implies: the two-tier liquidity floor
usually cuts the 12-name edge-ranked pool below `TOURNEY_BATCH=10` (08-14:
12 to 6), so each bracket collapses to a single round. Output is ~60% of the
bill and is almost all thinking, because the JSON answer is ~90 tokens.

## Decision

**Price from the rate card that bills, not from a docs page.** `pricing.py` is
now verified against the Cloud Billing Catalog API (service `C7E2-9256-1C43`),
with the re-verify command in its docstring. Rates are the global endpoint,
standard `Predictions` SKUs. Long-context rates (above 200k input tokens) are
carried per model and applied automatically.

**An unknown model logs NULL, never a guess.** The unsourced `gpt-5.2`,
`grok-4` and `deepseek-v3` entries are removed. No live service calls them
(agent-arena is dead). Prefix matching now takes the LONGEST match, so
`gemini-3.5-flash-lite-001` can no longer fall onto the 5x-dearer
`gemini-3.5-flash` entry.

**The tournament writes one row per LLM attempt.** `service="signal_judge"`,
`call_site="tournament_batch"`, with seed, round, attempt, batch size and
tickers in `inputs_raw`. Retries get their own rows, because a retry bills like
any other call. Thinking tokens are folded into `output_tokens` (the same trap
enrichment hit on 2026-06-12); logging only `candidates_token_count` would
understate this call ~40x.

**Cost accounting never breaks a pick.** The import is guarded, the context
object is optional, the write runs in a worker thread through the existing
fire-and-forget logger, and every call site swallows. `TRACE_LOGGING_ENABLED=true`
is set in `signal-judge/deploy.sh`; unset, the service behaves exactly as before.
Selection logic is untouched: `run_id` and `scan_date` are carried for the trace
row only, and the prompt is byte-identical (`tournament_v1_3`, version 10).

## What this does NOT do

Historical `cost_usd` values are left as written. Rewriting them is a BigQuery
mutation and an owner call. Read any `llm_traces_v1` row before 2026-08-17 as
~26x low on Flash and ~10x low on `gemini-3-flash-preview`, or recompute from
`input_tokens`/`output_tokens`, which were always correct.

Cached input is still mispriced upward: `TraceRecord` has no cached-token field.
Nothing in the pipeline uses context caching today.

## Rollback

Revert the two files. For the service, drop `TRACE_LOGGING_ENABLED` from
`signal-judge/deploy.sh` and redeploy: the code path then no-ops at the logger,
with no prompt or selection change to unwind.
