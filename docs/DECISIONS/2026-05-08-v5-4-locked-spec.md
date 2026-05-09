# 2026-05-08 — V5.4 agent-ranker spec locked

## Decision
Replace V5.3's deterministic SQL ranker (`directional V/OI DESC → spread ASC → overnight_score DESC → ticker ASC`) with a Scorer→Picker LLM pair. V5.3's hard gates (V/OI floor, moneyness, OI/vol floors, VIX ≤ VIX3M, earnings overlap exclusion) stay deterministic and run upstream. V5.3 keeps running in production unchanged; V5.4 runs in parallel via a second `forward_paper_ledger` row tagged `policy_version=V5_4_AGENT_RANKER`. **No ledger truncation.**

Full implementation plan: [`docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md`](../EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md).

## Why now
The 2026-05-08 pick was UHS BEAR $160P with a generic litigation-risk thesis that the operator judged could plausibly have lost to another candidate. V5.3's static ranker has no notion of regime fit, narrative coherence with the daily macro report, or contradictions between flow direction and ticker news. With no live customers and no real capital deployed, there is room to iterate the picker layer without GTM risk. Per memory `project_finished_definition.md` the system is in park-mode while the V5.3 cohort accrues — V5.4 builds in parallel during park.

## Locked decisions

| | Value | Anchor |
|---|---|---|
| Composite weights v0 | **60% flow_conviction / 25% regime_alignment / 15% narrative_coherence** | Pan-Poteshman 2006 RFS (flow alpha peaks day 1-2 at our 1-3 day hold horizon); Hu 2014 + Cheng 2019 (regime is multiplier, not edge); Tetlock 2007 + Engelberg et al. 2012 (news priced in by entry, coherence-check role only). In-house: `enrichment_quality_score` was anti-predictive in `FINDINGS_LEDGER.md`. Equal-weighting (33/33/33) is **not** defensible at this horizon — overweights narrative, underweights flow. |
| Re-weight trigger | After N=30 V5.4 closed trades — IC decomposition per dimension on the live ledger | Literature gives the ordering, not a peer-reviewed weight vector. Treat 60/25/15 as a v0 prior and update from in-house data once we have it. |
| Scorer model | `gemini-3-flash-preview` | Repeated 5-10× per day, structured 1-10 output. Flash is plenty. Matches production fleet. |
| Picker model | `gemini-3.1-pro-preview` | Single high-stakes reasoning call/day with full context. Pro tier earns its keep. x-poster CLAUDE.md recommends for new agents. |
| Picker contract | **No abstain.** Given ≥1 candidate from V5.3 gates → return exactly one ticker. | V5.4 inherits V5.3's existing skip_reasons by being downstream. The product is a pick. Operator: "We want picks. Let the thing cook." |
| Top-N cut | Top 5 by Scorer composite | Caps Picker context for cleaner reasoning. ≤5 candidates → all go through. |
| Prompt versioning | Light-touch semantic integer (`scorer_v1`, `picker_v1`), per-row in `signal_ranker_runs`, bump on material changes | Modern models capture intent reliably (no SHA-hash-every-tweak), but eval-cohort attribution + rollback DO require versioning. See memory `feedback_modern_model_intent.md`. |
| Ledger handling | V5.3 + V5.4 cohabit `forward_paper_ledger` via `policy_version`. **No truncation.** | Head-to-head on the same calendar days. V5.3 retires only when V5.4 wins on N≥30 closes. |
| Pre-launch tuning | Vertex AI Prompt Optimizer zero-shot lint pass on both prompts | Free, no labels, single SDK call per agent. Cherry-pick wording wins. |
| Post-launch tuning | Data-driven VAPO on Scorer post-launch with judge endpoint; Picker VAPO deferred to N=50 closes | VAPO targets `gemini-2.5-pro` (preview models excluded as targets); transfer to flash/3.1-pro validated on held-out set. DSPy fallback if transfer fails. |

## What changes

### `forward_paper_ledger` (BigQuery, additions only)
- New `policy_version` value: `V5_4_AGENT_RANKER`. V5.3's `V5_3_TARGET_80` unchanged.

### `signal_ranker_runs` (BigQuery, NEW)
One row per (run_id, candidate). Captures all candidates' Scorer outputs, top-5 cut, Picker choice + justification + confidence, prompt versions, model strings, latency, composite weights JSON. Schema in the EXEC-PLAN.

### `signal-ranker/` (Cloud Run, NEW)
Sibling shape to `x-poster/` and `blog-generator/`. ADK ParallelAgent (Scorer fanout) → deterministic top-5 cutter → LlmAgent (Picker). Endpoint `POST /rank`. Default compute SA.

### `enrichment-trigger/main.py` (independent of V5.4)
Per-ticker thesis prompt at line 276 gains a same-day flow-context struct (sector mix, dominant direction, candidate count, VIX vs VIX3M state). News grounding intact. Free win independent of the V5.4 ranker work.

### `signal-notifier/main.py`
After V5.3 rank-1 selection, HTTP-call `signal-ranker /rank` and write second ledger row with `policy_version=V5_4_AGENT_RANKER`. On signal-ranker failure: log + continue (V5.3-only fallback). Email shows both picks side-by-side.

### `gammarips-eval`
Daily prompt-fidelity scoring on Scorer rubric outputs (LLM-as-judge). Nightly hindsight join to `forward_paper_ledger` after closes — IC per Scorer dimension. Outputs to `eval_runs/v5_4_rubric_ic_{date}`.

## What does NOT change
- `forward-paper-trader/` — V5.4 is a picker change, not a trader change. Same -60/+80/3-day mechanics.
- V5.3 hard gates in `signal-notifier` and `enrichment-trigger` — V5.4 inherits them upstream.
- V5.3 production schedule — same 07:30 ET signal-notifier cron fires both pickers.
- Email/WhatsApp recipients — only operator while in park-mode (no paid subs yet).
- Webapp `todays_pick/{scan_date}` — V5.3's pick still goes there. V5.4 lives in `signal_ranker_runs` + `forward_paper_ledger` only until it earns the surface.

## Pre-launch checklist
See `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md#pre-launch-checklist`. Must-haves before deploy:
- `gammarips-review` pass for lookahead/leakage/fallback
- Leakage assertion in signal-ranker (no field dated > scan_date)
- Fallback path tested (deliberate 500 → V5.3 still ledgers)
- DRY_RUN flag honored on first deploy

## Open

All three pre-Phase-2 questions resolved 2026-05-08 (same day as spec-lock, post-Phase-0 schema approval):

| Question | Resolution | Rationale |
|---|---|---|
| Composite formula | **Weighted sum:** `composite = 0.6*flow + 0.25*regime + 0.15*narrative` | Linear, matches literature anchors directly, easy to debug. Geometric mean deferred — revisit only if eval shows interaction effects. At v0, "10/3/3 beats 7/7/7" is intended — flow dominates by design. |
| Picker confidence | **Enum** `"high" \| "medium" \| "low"` (stored STRING) | Cleaner prompt instruction, no false-precision float hallucinations. Map to {0.8, 0.5, 0.2} for IC analysis if needed. |
| Picker input | **Scorer reasoning prose only** — no raw rubric scores / composite | Prevents Picker from rubber-stamping the loudest single-rubric scorer. Picker integrates evidence itself rather than min-maxing the composite. |

Remaining open call (deferred to Phase 3): operator email format — side-by-side cards vs separate V5.3 / V5.4 sections.
