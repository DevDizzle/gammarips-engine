# V5.4 Agent Ranker — Execution Plan

> **Self-contained handoff.** A fresh session reads this and starts Phase 0 without needing prior conversation context. Spec was locked in the 2026-05-08 planning session (literature review on rubric weights + Vertex AI Prompt Optimizer feasibility).

## TL;DR

V5.4 replaces V5.3's deterministic SQL ranker with a Scorer→Picker LLM pair. V5.3's hard gates (V/OI floor, moneyness, OI/vol floors, VIX ≤ VIX3M, earnings overlap exclusion) stay deterministic and run upstream — by the time candidates hit the Scorer, every one is gate-clean. V5.3 keeps running in parallel — both V5.3 and V5.4 picks write to `forward_paper_ledger` with different `policy_version` so head-to-head P&L attribution is built in. **No ledger truncation.**

```
overnight-scanner → enrichment-trigger → overnight_signals_enriched
                                                │
                                                ▼
                                       signal-notifier
                                             │
                            ┌────────────────┴────────────────┐
                            │                                 │
                  V5.3 SQL rank (LIMIT 1)            HTTP → signal-ranker (NEW)
                            │                                 │
                            ▼                                 ▼
            forward_paper_ledger                   ScorerAgent (ParallelAgent fanout)
            policy=V5_3_TARGET_80                  ↓
                                                   top-5 by composite
                                                   ↓
                                                   PickerAgent (LlmAgent)
                                                   ↓
                                                   forward_paper_ledger
                                                   policy=V5_4_AGENT_RANKER
                                                   + signal_ranker_runs (NEW BQ table)
```

## Why V5.4 (problem statement)

V5.3's ranker is a 4-key SQL `ORDER BY` (`directional V/OI DESC → spread ASC → overnight_score DESC → ticker ASC`). Two candidates with similar V/OI/spread are treated as equivalent. Qualitative regime fit, narrative coherence with the daily macro report, and contradictions between flow direction and ticker news are invisible to it. The pick we shipped 2026-05-08 (UHS BEAR $160P) had a generic litigation-risk thesis the operator judged could plausibly have lost to another candidate the LLM would have chosen. V5.4 closes that gap.

## Decisions locked 2026-05-08

| Decision | Value | Rationale |
|---|---|---|
| Composite weights v0 | **60% flow_conviction / 25% regime_alignment / 15% narrative_coherence** | Pan-Poteshman 2006 RFS (flow alpha peaks day 1-2 at our exact horizon); Hu 2014 + Cheng 2019 (regime is a multiplier on flow, not independent edge); Tetlock 2007 + Engelberg et al. 2012 (news mostly priced in by 10:00 ET entry, coherence-check role only). In-house corroboration: `enrichment_quality_score` was anti-predictive in `FINDINGS_LEDGER.md`. Equal-weighting is **not** defensible at this horizon. Re-weight after N=30 V5.4 closed trades via IC decomposition. |
| Scorer model | `gemini-3-flash-preview` | Repeated 5-10× per day, structured 1-10 output. Flash is plenty. Matches production fleet. |
| Picker model | `gemini-3.1-pro-preview` | Single high-stakes reasoning call/day with full context (top-5 + Scorer outputs + report + 14d ledger). Pro tier earns its keep. x-poster CLAUDE.md recommends for new agents. |
| Picker contract | **No abstain.** Given ≥1 candidate from V5.3 gates → return exactly one ticker. | V5.4 inherits V5.3's skip_reasons by being downstream. The product is a pick. |
| Top-N cut to Picker | Top 5 by composite Scorer score | Caps Picker context for cleaner reasoning; ≤5 is no-op (everyone goes through). |
| Prompt versioning | Light-touch semantic integer (`scorer_v1`, `picker_v1`), per-row in `signal_ranker_runs`, bump on material changes only | Modern models capture intent reliably so no SHA-hash-every-tweak; but eval-cohort attribution + rollback DO require versioning. See memory `feedback_modern_model_intent.md`. |
| Ledger handling | V5.3 and V5.4 cohabit `forward_paper_ledger` via `policy_version`. **No truncation.** | Head-to-head on the same calendar days. V5.3 retires only when V5.4 wins on N≥30 closes. |
| Pre-launch tuning | Zero-shot Vertex AI Prompt Optimizer (VAPO) lint pass on both prompts | Free, no labels needed, single SDK call per agent. Cherry-pick wording wins. |
| Post-launch tuning | Data-driven VAPO on Scorer once Cloud Run judge endpoint exists; Picker VAPO deferred to N=50 closes | VAPO targets `gemini-2.5-pro` and we transfer to flash/3.1 (preview models excluded as targets). DSPy/MIPROv2 is fallback if transfer fails. |

## Architecture

### `signal-ranker` (NEW Cloud Run service)

ADK service, sibling shape to `x-poster/` and `blog-generator/`. Vendors `gammarips_content` at deploy time. Default compute SA per memory `feedback_default_compute_sa.md`.

**Endpoints:**
- `POST /rank` — request body `{ scan_date: "YYYY-MM-DD", candidates: [...], report_md: "...", ledger_summary: {...} }`. Returns `{ pick: ticker, runner_up: ticker, justification: str, confidence: "high"|"medium"|"low", scorer_outputs: [...], scorer_prompt_version: int, picker_prompt_version: int }`.

**Agent shape:**
```
ScorerRunner (ParallelAgent, ADK fanout)
  ├─ ScorerAgent for candidate_1 → ScorerOutput
  ├─ ScorerAgent for candidate_2 → ScorerOutput
  └─ ...                          → ScorerOutput
       │
       ▼
TopNCutter (deterministic Python, not an agent) — composite = 0.6*flow + 0.25*regime + 0.15*narrative; sort desc; take top 5
       │
       ▼
PickerAgent (LlmAgent, structured output)
       │
       ▼
PersistRun (deterministic) — writes signal_ranker_runs row + returns to caller
```

**Scorer prompt** lives at `signal-ranker/prompts/scorer_v1.md`. Rubric:
- `flow_conviction` (1-10): strength of directional unusual flow on this name. References V/OI ratio, dollar volume, OI persistence, spread, depth.
- `regime_alignment` (1-10): fit with today's report and macro context. Must cite specific report passages or VIX-regime state. Score ≤4 if directly contradicted by report; ≤6 if neutral; ≥7 only if explicitly aligned.
- `narrative_coherence` (1-10): does the per-signal news/thesis support the directional bet? Score ≤4 on contradictions (bearish put on ticker with fresh analyst upgrade etc.); ≥7 only on direct narrative confirmation.

Output (Pydantic schema, structured output):
```python
class ScorerOutput(BaseModel):
    ticker: str
    flow_conviction: int  # 1-10
    regime_alignment: int  # 1-10
    narrative_coherence: int  # 1-10
    composite: float  # auto-computed: 0.6*flow + 0.25*regime + 0.15*narrative
    reasoning: str  # 2-3 sentences
```

**Picker prompt** lives at `signal-ranker/prompts/picker_v1.md`. Inputs:
- Top 5 candidates' enriched data (full BQ row each)
- Top 5 candidates' Scorer outputs (`reasoning` strings; **not** raw rubric scores — prevents Picker from rubber-stamping the highest single-rubric scorer)
- Today's `overnight_report` markdown from `daily_reports/{scan_date}` Firestore doc
- Last 14d ledger summary, split by direction AND policy_version (so the Picker sees "V5.3 is 0/4 on bullish picks this week" if applicable)

Output:
```python
class PickerOutput(BaseModel):
    pick: str  # ticker
    runner_up: str  # ticker
    justification: str  # 2-3 sentences explaining why this beat the runner-up
    confidence: Literal["high", "medium", "low"]
```

**Hard constraints in prompts:**
- All inputs are dated ≤ scan_date close. Anything dated entry_day or later is a leakage bug.
- Picker MUST pick from the top-5 set. If it returns a ticker not in the set → fallback to V5.3 rank-1 (this is a Picker bug; alert).
- No abstain branch.

## Data contracts

### `signal_ranker_runs` (NEW BigQuery table)

`profitscout-fida8.profit_scout.signal_ranker_runs`

```sql
CREATE TABLE `profitscout-fida8.profit_scout.signal_ranker_runs` (
  run_id STRING NOT NULL,                    -- UUID, one per /rank call
  scan_date DATE NOT NULL,
  entry_day DATE NOT NULL,                   -- for join to forward_paper_ledger
  candidate_ticker STRING NOT NULL,
  candidate_rank_static INT64,               -- V5.3 SQL ranker position (1-10), null if scoring more than top-10
  composite_score FLOAT64 NOT NULL,
  flow_conviction INT64 NOT NULL,            -- 1-10
  regime_alignment INT64 NOT NULL,           -- 1-10
  narrative_coherence INT64 NOT NULL,        -- 1-10
  scorer_reasoning STRING,
  in_top_5 BOOL NOT NULL,                    -- did this candidate go to Picker
  picker_chose BOOL NOT NULL,                -- final pick
  picker_runner_up BOOL NOT NULL,
  picker_justification STRING,               -- only populated for picked + runner_up rows; null otherwise
  picker_confidence STRING,                  -- "high" | "medium" | "low" | null
  scorer_prompt_version INT64 NOT NULL,
  picker_prompt_version INT64 NOT NULL,
  scorer_model STRING NOT NULL,              -- "gemini-3-flash-preview" at v1
  picker_model STRING NOT NULL,              -- "gemini-3.1-pro-preview" at v1
  scorer_latency_ms INT64,
  picker_latency_ms INT64,
  composite_weights_json STRING NOT NULL,    -- '{"flow":0.6,"regime":0.25,"narrative":0.15}' at v0
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY scan_date;
```

**One row per (run_id, candidate_ticker)** — typically 5-10 rows per scan_date. Joinable to `forward_paper_ledger` on `(candidate_ticker, entry_day)` for outcome.

### `forward_paper_ledger` (existing, additions only)

- New `policy_version` value: `V5_4_AGENT_RANKER`
- V5.3's `V5_3_TARGET_80` unchanged

### `daily_reports/{scan_date}` (Firestore, existing — no change needed)

Picker reads this Firestore doc directly. Already populated by `overnight-report-generator` daily at 08:15 ET. Read-only consumer.

## Phases

### Phase 0 — `signal_ranker_runs` BQ table (1 day)

**Deliverable:** Table exists in BQ, partitioned, with the schema above. One-shot `scripts/ledger_and_tracking/create_signal_ranker_runs.py` (mirrors existing one-shot pattern; per `.claude/rules/scripts-ledger.md`, do not re-run without approval).

**Acceptance:** `bq show profitscout-fida8:profit_scout.signal_ranker_runs` returns the schema. No rows yet. Schema reviewed against this doc.

### Phase 1 — Enrichment thesis flow-context plumb (½ day)

**Deliverable:** `enrichment-trigger/main.py` thesis prompt accepts a same-day flow-context struct (sector mix, dominant direction, candidate count, VIX vs VIX3M state) computed from the day's enriched signals. Per-ticker news grounding (Gemini Grounded Search at line 276) stays intact.

**Why this is independent of V5.4:** Even without the agent ranker, per-ticker theses get sharper because the LLM sees the cross-cutting frame. Free win.

**Acceptance:** Existing thesis output schema unchanged (`thesis: str`). Visual A/B on 2-3 historical scan dates: new theses reference cross-cutting context (sector, regime, candidate count) where the old ones read generic.

### Phase 2 — `signal-ranker` Cloud Run service (3 days)

**Deliverable:** New service at `signal-ranker/` mirroring `x-poster/` shape:
- ADK app under `signal-ranker/app/` with `ScorerRunner` ParallelAgent + `PickerAgent` LlmAgent
- Pydantic schemas for ScorerOutput + PickerOutput
- Prompt files at `signal-ranker/prompts/scorer_v1.md` and `signal-ranker/prompts/picker_v1.md`
- BQ writer for `signal_ranker_runs`
- `signal-ranker/Dockerfile` + `deploy.sh` matching x-poster pattern
- Default compute SA, project profitscout-fida8
- Vendors `gammarips_content` at deploy time

**Endpoint:** `POST /rank` (do NOT use `/run` — ADK reserves it per memory `feedback_adk_route_reserved.md`).

**Tests:**
- Unit: ScorerOutput schema enforces 1-10 bounds; composite math is correct
- Unit: TopNCutter sorts deterministically when ties
- Unit: Leakage assertion — agent input contains no field dated > scan_date
- Integration: full `/rank` happy path on a stubbed BQ + Firestore fixture
- Integration: Picker returns a ticker outside the top-5 → service raises a specific error code (caller falls back to V5.3 rank-1)

**Acceptance:** Service deploys to Cloud Run. `curl POST /rank` with a real scan_date returns a structured pick within ~10s. `signal_ranker_runs` table receives the rows.

### Phase 2.5 — Zero-shot VAPO lint pass (½ day)

**Deliverable:** Run Vertex AI Prompt Optimizer in zero-shot mode on `scorer_v1.md` and `picker_v1.md`. Diff the optimized text against the hand-written. Cherry-pick wording wins manually; do not blindly accept the rewrite. If accepted, bump to `scorer_v2.md` / `picker_v2.md`.

**Acceptance:** Two prompt files at version 1 or 2 (depending on what we accepted) committed. Diff log saved at `signal-ranker/scripts/vapo_zeroshot_diff.md` for reference.

### Phase 3 — Wire into `signal-notifier` (1 day)

**Deliverable:** `signal-notifier/main.py` modifications:
- After existing V5.3 rank-1 selection but before Firestore write, HTTP-call `signal-ranker /rank` with the top-10 candidates
- On success: write a second `forward_paper_ledger` row with `policy_version="V5_4_AGENT_RANKER"`. Same entry/stop/target/hold mechanics as V5.3 (this is unchanged — V5.4 is a *picker* change, not a *trader* change).
- On failure (timeout, 5xx, schema mismatch, picker returns out-of-set ticker): log structured error, continue with V5.3 only. Email still goes out.
- Email format: side-by-side V5.3 + V5.4 picks (operator-only — no paid subs yet per memory `project_email_only_delivery.md`, and operator is the only consumer per 2026-05-08 conversation).

**Cron:** No new schedule needed. signal-ranker is called inline from signal-notifier's existing 07:30 ET trigger.

**Acceptance:** End-to-end: 07:30 ET cron fires → V5.3 + V5.4 picks both written to ledger → operator email shows both. If V5.4 errors, only V5.3 lands. If V5.3 has 0 candidates (skip day), V5.4 also skips silently.

### Phase 4 — `gammarips-eval` hookup (2 days)

**Deliverable:** `gammarips-eval` reads `signal_ranker_runs` daily. Two eval modes:

1. **Prompt-fidelity** (runs after each `/rank` call, before email send if possible):
   - LLM-as-judge scores each Scorer rubric output
   - Did `regime_alignment` cite concrete report passages? Score 0-1
   - Did `narrative_coherence` flag contradictions where they exist? Score 0-1
   - Are scores well-distributed across the 1-10 range, or bunched (sign of prompt confusion)?

2. **Hindsight P&L** (runs nightly after trades close):
   - Join `signal_ranker_runs` to `forward_paper_ledger` on `(candidate_ticker, entry_day)`
   - Compute IC per Scorer dimension: does `flow_conviction` rank correlate with realized 3-day option return? Same for `regime_alignment`, `narrative_coherence`.
   - Output `eval_runs/v5_4_rubric_ic_{date}` Firestore docs

**Acceptance:** First eval run produces a Firestore doc with rubric IC scores by dimension. After N=10 V5.4 closes, IC numbers should be inspectable to validate the 60/25/15 priors.

### Phase 4.5 — Data-driven VAPO on Scorer (2 days, post-launch)

**Deliverable:**
- Cloud Run "judge" endpoint wrapping `gammarips-eval`'s LLM-as-judge for `(response, reference)` → 0-1 score
- Pull ~100 historical `overnight_signals_enriched` rows as a VAPO dataset
- Run VAPO data-driven mode on Scorer prompt with judge endpoint as custom metric
- Target model: `gemini-2.5-pro` (preview models excluded). Validate transfer to `gemini-3-flash-preview` on a held-out 20 candidates
- Bump `scorer_prompt_version` if accepted

**Acceptance:** New `scorer_v2.md` (or `v3` etc.) committed with measurable improvement on judge metric. Held-out set confirms transfer to flash.

### Phase 5 — Iterate (open-ended)

| Milestone | Action |
|---|---|
| N=10 V5.4 closes | First read on V5.4 vs V5.3 divergence quality. If V5.4 just rubber-stamps V5.3 → fix prompts. If divergent → check whether divergent picks won or lost. |
| N=30 V5.4 closes | gammarips-review pass + decide whether to retire V5.3. Re-weight composite via IC decomposition (kill or shrink any dimension with IC < 0.05). |
| N=50 V5.4 closes | Data-driven VAPO on Picker against `(top-5 set, winning_ticker, realized_pnl)` JSONL. |

## Pre-launch checklist

- [ ] `gammarips-review` pass on full diff: lookahead bias, leakage paths, fallback paths, prompt-injection from candidate news strings
- [ ] Leakage assertion in `signal-ranker`: agent input contains no field dated > `scan_date` close. Fails-closed if violated.
- [ ] Fallback verified: signal-ranker errors → V5.3 still ledgers + emails. Tested via deliberate 500 from signal-ranker in staging.
- [ ] Picker out-of-set return → caller falls back to V5.3 rank-1 with logged error
- [ ] `signal_ranker_runs` BQ table created with partition + version columns
- [ ] Scorer + Picker prompt files at v1, both reviewed against project voice (`libs/gammarips_content/brand.py` PERSONALITY)
- [ ] Zero-shot VAPO lint pass run + diff committed (Phase 2.5)
- [ ] Service deployed with default compute SA (per `feedback_default_compute_sa.md`)
- [ ] DRY_RUN flag honored in signal-ranker for first deploy (writes to BQ only, signal-notifier skips the second ledger row)

## Open questions for next session

- Composite formula: weighted **sum** (current spec) vs weighted **geometric mean** (penalizes low single-dimension scores more aggressively). Recommended default: weighted sum until eval shows actual interaction effects.
- Picker confidence: enum (`high|medium|low`) or float 0-1? Enum is cleaner for prompt; float is friendlier for downstream IC. **Recommended:** enum at v1, revisit if eval needs continuous.
- Whether Picker sees raw rubric scores or only Scorer reasoning prose. **Recommended:** prose only (prevents min-maxing the loudest rubric).
- Email format: side-by-side cards vs separate sections. Operator preference call.

## References

- `docs/TRADING-STRATEGY.md` — V5.3 canonical execution policy (V5.4 is a picker change, not a trader change)
- `docs/DECISIONS/2026-05-08-v5-4-locked-spec.md` — short decision-log entry for this plan
- `docs/research_reports/INTELLIGENCE_BRIEF.md` — literature anchors for the 60/25/15 weights (Pan-Poteshman, Johnson-So, Hu, Cheng, Tetlock, Engelberg)
- `signal-notifier/main.py:660-690` — V5.3 SQL ranker (the thing V5.4 replaces at the picker layer)
- `enrichment-trigger/main.py:276` — current per-ticker thesis prompt (Phase 1 modifies this)
- `x-poster/app/agent.py` — ADK pattern reference for `signal-ranker` shape
- Memory: `project_v5_4_dynamic_criteria.md`, `feedback_modern_model_intent.md`, `feedback_lean_on_literature.md`, `feedback_default_compute_sa.md`, `feedback_adk_route_reserved.md`
