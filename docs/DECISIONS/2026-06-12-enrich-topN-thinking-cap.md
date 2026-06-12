# 2026-06-12 — Enrichment cost fix: edge-rank to top-N + cap thinking

## Problem
Daily Vertex/Gemini spend hit **~$38/day** — unaffordable; target ~$5/day.

The premise (carried from 2026-06-11) was that the **tournament** (`signal-judge`,
`gemini-3.1-pro-preview`) was the cost driver. **It was not.** Cloud Monitoring
token counts for 2026-06-12 (one tournament run, no retries):

| Model | Input tok | Output tok |
|---|---|---|
| `gemini-3.5-flash` (enrichment) | 615K | **2,074,585** |
| `gemini-3.1-pro-preview` (tournament) | 84K | 19K |

The tournament used ~103K tokens (~$1). The burn was **`enrichment-trigger`**:
`fetch_and_analyze_news` made **513 grounded `gemini-3.5-flash` calls over 344
tickers**, each with **Google Search grounding** and **uncapped thinking**
(`thinking_budget` left at server default → ~3,600 hidden thinking tokens/call →
~2M/day, billed as output).

**Why it was invisible:** the trace logger recorded `output_tokens =
candidates_token_count` only (~397/call), dropping `thoughts_token_count`. So
`llm_traces_v1` showed enrichment at ~$0.10/day while it actually dominated the
bill. (Lesson: eval the data, not just the LLM text — see
`feedback_eval_the_data_not_just_llm_text`.)

The structural waste: the funnel grounded the **wide** end (344 names) then
discarded all but ~12 at the tournament. Token budget was spent backwards.

## Decision (owner-directed)
Concentrate the grounded-LLM budget on the names that can actually win. New funnel:

```
overnight scan (~5000, all dirs)
  └─ cheap gates (no tokens): UOA floor (call/put_uoa_depth > $500K), score >= MIN
  └─ flow_context computed on the FULL scan (market-wide regime/sector/breadth)
  └─ EDGE-RANK → top ENRICH_TOP_N (default 50) BULLISH names
        rank = BULLISH(+2) + |delta| 0.20–0.46 in-band(+1.5), tie-break overnight_score
        (delta is the only CONFIRMED lever — Q19 trap-escape; RR/ATR are computed
         DURING enrichment so they can't rank pre-enrichment, and weren't confirmed)
  └─ GROUND only those ~50 (gemini-3.5-flash, thinking_budget=0)
  └─ tournament over all ~50 → 1 pick
```

### Changes (`enrichment-trigger/main.py` only — code-clean file)
1. **`_edge_select_top_n(signals, k)`** — BULLISH gate + delta-band edge rank,
   keep top `ENRICH_TOP_N` (env, default **50**). Applied AFTER `compute_flow_context`
   (so market-wide context still reflects the full scan), BEFORE grounding +
   technicals. Leakage-safe: only point-in-time scan fields.
2. **`thinking_config=ThinkingConfig(thinking_budget=ENRICH_THINKING_BUDGET)`**
   (env, default **0**) on the grounding call. Verified live on `gemini-3.5-flash`
   WITH grounding: `thoughts_token_count → 0`, news still returned. Raise via env
   if catalyst quality degrades.
3. **Trace-logger truthfulness:** fold `thoughts_token_count` into the logged
   `output_tokens` so `cost_usd` reflects billed reality going forward.

### Config (no code ship for signal-notifier)
- `TOURNEY_POOL_CAP=50` set as a **runtime env var** on `signal-notifier` (via
  `gcloud run services update`, config-only) so all ~50 enriched names reach the
  tournament instead of being re-capped to 12. The code default stays 12 (the
  service's working tree has unrelated uncommitted `gate-changes` WIP, so it was
  NOT redeployed). **When that WIP ships, bump the code default to 50** and pin it
  in `signal-notifier/deploy.sh`.

## Env knobs
| Var | Default | Effect |
|---|---|---|
| `ENRICH_TOP_N` | 50 | how many names get grounded (20↔50↔80 without a code change) |
| `ENRICH_THINKING_BUDGET` | 0 | thinking tokens/call on enrichment (raise if quality drops) |
| `BULLISH_ONLY` | true | shared with notifier; enrich BULLISH only |
| `TOURNEY_POOL_CAP` | 50 (env) | pool into the tournament |

## Expected impact
Grounded calls 344 → 50 (~7×) + thinking → 0 (~2M output tokens/day removed).
Projected **< $5/day** (enrichment grounding ~$1–2 + tournament ~$1–2).

## Sizing rationale (top-50 not top-20)
Supply over 5 scans: ~150–305 BULLISH names/day clear UOA + the delta band. Both
20 and 50 are real caps (50 = top ~quartile, still selective). Cost delta 20→50 is
~$1/day once thinking is capped — negligible vs the $38 cut. Chose **50 for
robustness** (the delta-band rank is a heuristic; 50 gives the tournament real
choice). Env-tunable.

## Tradeoffs / follow-ups
- **Website haystack depth:** `overnight_signals_enriched` shrinks from ~344 to
  ~50 rich (news/thesis) rows. The broad per-ticker SEO pages read the raw
  `overnight_signals` scan, so they are unaffected; only news/thesis depth on
  low-score names drops. Accepted (owner: "invest the budget in the top names,
  not noise"). Verify the webapp haystack still renders the broad scan.
- **Research shadow trackers' universe also shrinks** (gammarips-review NIT-1):
  the top-score shadow and the intraday/MTM watchlist paths in
  `forward-paper-trader` read `overnight_signals_enriched` for the scan_date.
  Their pool was ~344 names across BOTH directions; it is now ~50 BULLISH-only,
  edge-pre-ranked. So the top-score shadow is no longer a pure "top-overnight_score
  over the full pool" control — it's "top-score within BULLISH-top-50." No live
  ledger / capital impact (the live pick is already BULLISH-only; shadows are
  walled off from Scorecard/website), but interpret the N≥15 shadow read with this
  universe shift in mind. See [[project_topscore_shadow_tracker]] /
  [[project_intraday_hold_shadow]].
- **Earnings/regime gates** remain post-enrichment in `signal-notifier`. With only
  ~50 enriched, the waste of enriching a name later killed for earnings is ~1–2/day
  — acceptable; moving them upstream is a deferred refinement.
- **No leakage introduced:** edge rank uses only point-in-time scan fields; the
  grounded news is already point-in-time (24h lookback at scan).

## Validation
First cron after deploy: confirm enrichment grounds ~50 (not ~344) via the
`Edge-rank enrichment cap:` log line, `thoughts_token_count → 0`, and the
`gemini-3.5-flash` output-token total drops ~10× in Cloud Monitoring. Decide on
`ENRICH_TOP_N` / `ENRICH_THINKING_BUDGET` tuning after observing pick quality.
