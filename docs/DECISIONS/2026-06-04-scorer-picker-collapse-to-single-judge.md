# 2026-06-04 — Collapse the V5.4 Scorer→Picker pair into one memory-aware judge (`judge_v6`)

**Status:** IMPLEMENTED in `signal-ranker` (code + prompt + tests + live smoke). Pending `gammarips-review` leakage audit before production deploy. Owner-directed simplification; G-Stack 30-day-OOS ceremony waived (owner's to waive — only the leakage audit is non-negotiable).

## Decision
Replace the two-stage `Scorer` (per-candidate, `gemini-3.5-flash`, memory-blind) + `Picker` (`gemini-3.1-pro-preview`, memory-aware) pipeline with a **single memory-aware judge** (`judge_v6`, `gemini-3.1-pro-preview`) that receives **all** gate-cleared candidates at once and emits, in one structured call:
- a **per-candidate verdict array** (the same three rubric components — flow/regime/narrative 1–10 — so `signal_ranker_runs` stays one-row-per-candidate and the planned N=30 IC re-weighting still has separable dimensions), and
- the **final selection** (`pick`, `runner_up`, `justification`, `confidence`) or a **mass-leakage skip**.

The N+1 LLM calls per day collapse to **1**.

## Why
1. **The Scorer's top-5 cut was a no-op on ~80% of days.** Across 13 V5.4-era slates (2026-05-12 → 06-03), post-gate slates were mostly 1–5 candidates (only 3 days > 5). `take_top_n(5)` kept everything — the Scorer was *annotating*, not *filtering*.
2. **Structural rules were triple-encoded.** ITM / DTE / moneyness / spread / HEDGING / earnings are enforced UPSTREAM in `enrichment-trigger` + `signal-notifier`, yet both prompts re-litigated them. `judge_v6` §0a explicitly trusts the gates and does not re-score hard exclusions.
3. **The score-hiding "firewall" was reproducible by instruction.** `picker_v5.md` hid raw scores to prevent anchoring on a flashy number. The replay showed the judge — which *sees* the numbers — still anti-anchored (passed over the biggest-dollar-volume names on structural grounds) when instructed to "score each candidate as if it were the only one on the slate." `judge_v6` §4 Step 1 encodes this.

## Evidence (workflow replay, 2026-06-04)
13 V5.4-era slates reconstructed by joining `signal_ranker_runs` → `overnight_signals_enriched` (71/71 rows matched), replayed through `judge_v6` and compared to the logged 2-stage pick:
- **9/13 agreed** with the live baseline.
- On the **4 divergences, the judge was structurally sounder 4-to-1** — every divergence was the judge *rejecting* a structurally unfit baseline pick (OKTA balanced-flow two-label-trap → BX; KBR oversold-RSI-25 short → MCO; EQIX self-described deep-OTM LEAP unfit for a 3-day bracket → RDDT; CIEN 7-DTE theta-cliff taken "as sole candidate by default" → GE). The one baseline-favorable cell was a runner-up ordering nuance (both picked DINO).
- **No case** where the judge picked a trap or skipped a good trade.

**Caveats (documented, not waved away):** the replay was a Claude-as-judge *design proxy* on N=13; `report_md` regime context was not fetched into the replay; realized PnL is too thin to score (structural soundness ≠ money). A **live `gemini-3.1-pro` smoke on the 2026-06-03 slate** (post-implementation) confirmed the production path: clean structured-output parse into `JudgeOutput`, anti-anchoring held (down-weighted FTNT's larger flow for near-cap moneyness), and the judge reproduced the baseline BBWI pick.

## The one real regression — bought back
Collapsing the `asyncio.gather` fanout removes its `MIN_SCORER_SUCCESS_FRAC=0.5` partial-failure tolerance: one malformed fused output would now forfeit the whole slate (worsening funnel starvation). **Re-acquired** via `JUDGE_MAX_ATTEMPTS=3` bounded retry on the single structured call in `agent.run_judge` (retries on parse/validation/transport error before failing closed).

## What changed in code
- **New:** `signal-ranker/prompts/judge_v6.md` (single-call rubric; trusts gates; anti-anchoring; absolute leakage discipline; mass-leakage skip; per-candidate array; deterministic composite/tiebreak).
- **`app/schemas.py`:** added `PerCandidateVerdict` + `JudgeOutput`. `ScorerOutput`/`PickerOutput` **kept** (typecheck + pre-collapse replay). `RankResponse.scorer_outputs` re-typed to `list[PerCandidateVerdict]` (signal-notifier does not iterate it; `fast_api_app` only reads `len()`).
- **`app/agent.py`:** removed the Scorer fanout + ADK Picker machinery; added `run_judge` (leakage-assert all candidates → one structured call → bounded retry) and rewired `run_pipeline` (deterministic mass-leakage decision; off-list/poisoned-pick fail-closed). `root_agent` is now a degenerate judge for ADK discovery only.
- **`app/tools.py`:** `persist_run` rewritten to write one row per verdict. **BQ DDL UNCHANGED** — the single judge is mirrored into both `scorer_*` and `picker_*` REQUIRED columns (`*_prompt_version=6`, `*_model=gemini-3.1-pro-preview`), so the post-collapse cohort is cleanly separable from the v5 two-stage cohort. Added `JUDGE_MODEL`/`JUDGE_PROMPT_VERSION`/`JUDGE_PROMPT_LABEL`/`JUDGE_MAX_ATTEMPTS`.
- **`deploy.sh`:** env vars switched to `JUDGE_*` (legacy `SCORER_*`/`PICKER_*` retained-but-inert). Case-memory pre-deploy guard unchanged (memory is now load-bearing — `run_pipeline` fails CLOSED if it didn't ship).
- **Wire contract preserved → zero `signal-notifier` changes:** `pick`/`confidence`/`runner_up`/`justification`/`skip`/`skip_reason`/`run_id` + the 4 provenance fields all present; `call_signal_ranker` only guards on `pick`+`confidence` presence.
- **Tests:** `tests/unit/test_smoke.py` extended (verdict bounds, composite parity with legacy Scorer, `take_top_n` over verdicts, happy-path + mass-leakage `JudgeOutput` shapes). 32 passing.

## Next steps / open items
- **`gammarips-review` leakage audit** before production deploy (non-negotiable).
- **BQ migration (optional, deferred):** could `ALTER` `signal_ranker_runs` to add nullable `judge_prompt_version` / `judge_latency_ms` first-class columns instead of overloading version=6. Needs owner approval per `.claude/rules/scripts-ledger.md`. The mirror-into-existing-columns approach ships without a migration.
- **Shadow option (if desired):** run `judge_v6` logged beside the live 2-stage before cutover. Implemented path is a direct cutover; shadow is available if the owner prefers belt-and-suspenders.
- **Untested in replay:** fat-day (N>5) cross-candidate anchoring, a deliberate poisoned-slate fixture for the mass-leakage trip, confidence calibration drift. Worth a follow-up offline A/B.
