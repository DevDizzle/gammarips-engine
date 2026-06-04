# MODELS.md — Model → Function Registry

> **Last updated:** 2026-06-04 (tournament). V6 "Tournament" launched — the ranker
> is now a randomized bracket **tournament** (`tournament_v1`, version 7) at the
> `signal-judge` service; V5.4 retired, ledger truncated, `policy_version='V6_TOURNAMENT'`.
> No Scorer/Picker stages, no `judge_v6`, no memory/rubric/composite weights.
> This is the authoritative map of which model powers which function. Keep it in
> sync whenever a model id changes. Model ids are **env-driven** (see "How to swap" below);
> the defaults below are what ships in each service's `deploy.sh` / code.
>
> *History: `judge_v6` (one memory-aware Scorer+Picker call, version 6) was the ranker
> 2026-06-04 only and was superseded same-day by the tournament; the two-stage
> Scorer→Picker pair (version 5) preceded it.*

## At a glance

| Model | Role | Where it runs | Notes |
|---|---|---|---|
| **`gemini-3.5-flash`** | **Text generation** (the workhorse) | enrichment thesis, overnight report, x-poster text agents, blog-generator, eval **judges** | GA 2026-05-19. Global-endpoint only. Migrated from `gemini-3-flash-preview` 2026-05-27. Never touches the daily pick. |
| **`gemini-3.1-pro-preview`** | **Reasoning** — the tournament judge (the one daily pick) | **signal-judge** `tournament_v1` | Deliberate pro tier. Runs the randomized bracket tournament: all enriched signals → 3 brackets × (batches ≤10, top-2 advance, 94→20→4→1) → consensus pick. Dead-simple prompt + daily report + per-contract JSON. **No** memory, rubric, or composite weights. Not migrated (not flash, not on cull list). |
| **`gemini-3-pro-image-preview`** | **Image generation** (Nano Banana Pro) | x-poster editorial/OG/brand images | Separate deprecation track from text models. |
| **`gemini-2.5-pro`** | **Prompt tuning** (offline, not runtime) | `signal-judge/scripts/vapo_zeroshot.py` (VAPO lint) | Tuning/optimization only — never serves a live request. |
| `gemini-3-flash-preview` | *(retired in this engine)* | only `agent-arena` (DEAD service) | On the 2026-06-15 cull list, but agent-arena is deprecated and not run. |

**Nothing live is on the 2026-06-15 Vertex cull list** (`gemini-2.5-flash`, `gemini-2.5-flash-lite`,
`gemini-3-flash-preview`). The only remaining `gemini-3-flash-preview` reference is in the dead
`agent-arena` service. `profitscout-fida8` also retains access to the culled models anyway because
it is an active project.

## By function (detail)

### Text generation → `gemini-3.5-flash`
The general-purpose workhorse for everything that writes prose:
- **enrichment-trigger** — grounded-search thesis / flow-intent per ticker (`MODEL_NAME`). Google Search tool attached; no `response_schema` (incompatible with grounding) — relies on a strict-JSON prompt contract.
- **overnight-report-generator** — daily editorial report (`GEMINI_MODEL`). `response_schema=ReportResponse`.
- **x-poster** — Planner→Writer→Reviewer ADK agents draft tweets (`GEMINI_MODEL`).
- **blog-generator** — weekly blog + newsletter (`GEMINI_MODEL`). **Deployed.**
- **gammarips-eval judges** — LLM-as-judge for `report_factuality` + `quality` (`config.yaml: judge_model`). **`temperature=0.0`** kept for deterministic judging.
- *(Flash never touches the daily pick. The Scorer stage it briefly ran was removed 2026-06-04 when the ranker first collapsed to `judge_v6` and then moved to the tournament — see history below.)*

### The daily pick (the tournament) → `gemini-3.1-pro-preview`
- **signal-judge `tournament_v1`** (`JUDGE_MODEL`) — a randomized bracket tournament over all enriched signals: 3 brackets × (batches of ≤`TOURNEY_BATCH` ≤10 contracts, top-2 advance per batch, 94→20→4→1) → consensus pick. Dead-simple prompt, plus a daily report and a per-contract JSON verdict. **No** case-memory, **no** scoring rubric, **no** composite weights — pure head-to-head bracket. The judge call uses **google-genai direct** (`response_mime_type="application/json"`) with **bounded retry**. Stale liquidity fields (`recommended_volume`, `recommended_oi`, `volume_oi_ratio`, `call_vol_oi_ratio`, `put_vol_oi_ratio`) are **stripped** from the prompt; `recommended_spread_pct` **is** shown (now real after the 2026-06-04 #1 fix). Pro tier earns its keep on the single high-stakes decision; deliberately *not* downgraded to flash.

### Images → `gemini-3-pro-image-preview`
- **x-poster** image generation (`IMAGE_MODEL`) + the `scripts/generate_*` brand/OG helpers.

### Prompt tuning (offline) → `gemini-2.5-pro`
- **`signal-judge/scripts/vapo_zeroshot.py`** (`VAPO_TUNING_MODEL`) — zero-shot prompt-optimization lint pass. Not a runtime dependency; the runtime judge is the model above.

## Operational notes (read before changing any model)

1. **`gemini-3.5-flash` is served ONLY on the Vertex `global` endpoint** — a regional call
   (`us-central1`, etc.) returns `404 Publisher Model not found`. Every generative client in this
   repo already uses `global` (explicit `location="global"` or the google-genai default when
   `GOOGLE_CLOUD_LOCATION` is unset). Keep new clients on `global`. Embeddings/storage are unaffected
   (there are no embedding calls in this repo).
2. **Deployed services pin `google-genai==1.22.0`, which REJECTS `thinking_level`**
   (`ThinkingConfig: extra_forbidden`). Do NOT add `thinking_config=ThinkingConfig(thinking_level=...)`
   without first bumping `google-genai >= 1.74` in that service's `requirements.txt` and re-testing.
   Thinking is ON by default server-side for 3.x regardless. (This bit us during the migration —
   a green build hid it until a live smoke test.)
3. **Eval judge model lives in `gammarips-eval/config.yaml` (`judge_model`)**, which **overrides** the
   `JUDGE_MODEL` env var and the code default. Change the YAML, not just the env, or the swap is a no-op.
4. **Cohort attribution:** the legacy `v5_4_scorer_model` / `v5_4_picker_model` Firestore keys and the
   `signal_ranker_runs` table name were intentionally NOT renamed across the 2026-06-04 collapse +
   tournament (migration/webapp landmines). On the tournament path both `*_model` fields hold the single
   `JUDGE_MODEL` and both `*_prompt_version` columns hold `7`. Segment EV by the `signal_ranker_runs`
   cohort label and **do not pool across boundaries**: **5 = two-stage Scorer/Picker, 6 = single
   `judge_v6` (2026-06-04 only), 7 = `tournament_v1`** (live). Ledger rows carry
   `policy_version='V6_TOURNAMENT'`; pre-V6 rows were truncated at launch.

## How to swap a model (one line, no code edit)

Model ids are env vars pinned in each service's `deploy.sh`; flip the value and redeploy.

| Service | Env var(s) | Endpoint |
|---|---|---|
| enrichment-trigger | `MODEL_NAME` (+ `VERTEX_LOCATION=global`) | thesis |
| overnight-report-generator | `GEMINI_MODEL` | report |
| signal-judge | `JUDGE_MODEL` (+ `GOOGLE_CLOUD_LOCATION=global`, `TOURNEY_BATCH`) | tournament_v1 (the daily pick) |
| x-poster | `GEMINI_MODEL` (text), `IMAGE_MODEL` (image) | tweets / images |
| blog-generator | `GEMINI_MODEL` | blog/newsletter |
| gammarips-eval | **`config.yaml: judge_model`** (authoritative; `JUDGE_MODEL` env is inert) | judges |
| overnight-scanner (`src/enrichment`) | `MODEL_NAME`, `TECHNICALS_ANALYZER_MODEL_NAME`, `NEWS_ANALYZER_MODEL_NAME`, `MACRO_THESIS_MODEL_NAME` | scanner-era analyzers |
| VAPO script | `VAPO_TUNING_MODEL` | offline tuning |

Always smoke-test against the **deployed** service after a swap (local vs container SDK can diverge),
and check logs / `llm_traces_v1` for `NOT_FOUND` / fallback. See
`docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md` for the verification recipe.
