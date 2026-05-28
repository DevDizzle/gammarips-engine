# MODELS.md — Model → Function Registry

> **Last updated:** 2026-05-28 (after the `gemini-3.5-flash` migration —
> see `docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md`).
> This is the authoritative map of which model powers which function. Keep it in
> sync whenever a model id changes. Model ids are **env-driven** (see "How to swap" below);
> the defaults below are what ships in each service's `deploy.sh` / code.

## At a glance

| Model | Role | Where it runs | Notes |
|---|---|---|---|
| **`gemini-3.5-flash`** | **Text generation + scoring** (the workhorse) | enrichment thesis, overnight report, signal-ranker **Scorer**, x-poster text agents, blog-generator, eval **judges** | GA 2026-05-19. Global-endpoint only. Migrated from `gemini-3-flash-preview` 2026-05-27. |
| **`gemini-3.1-pro-preview`** | **Reasoning** — the single high-stakes daily decision | signal-ranker **Picker** | Deliberate pro tier; reads top-5 + Scorer prose + report + ledger, returns one pick. Not migrated (not flash, not on cull list). |
| **`gemini-3-pro-image-preview`** | **Image generation** (Nano Banana Pro) | x-poster editorial/OG/brand images | Separate deprecation track from text models. |
| **`gemini-2.5-pro`** | **Prompt tuning** (offline, not runtime) | `signal-ranker/scripts/vapo_zeroshot.py` (VAPO lint) | Tuning/optimization only — never serves a live request. |
| `gemini-3-flash-preview` | *(retired in this engine)* | only `agent-arena` (DEAD service) | On the 2026-06-15 cull list, but agent-arena is deprecated and not run. |

**Nothing live is on the 2026-06-15 Vertex cull list** (`gemini-2.5-flash`, `gemini-2.5-flash-lite`,
`gemini-3-flash-preview`). The only remaining `gemini-3-flash-preview` reference is in the dead
`agent-arena` service. `profitscout-fida8` also retains access to the culled models anyway because
it is an active project.

## By function (detail)

### Text generation & scoring → `gemini-3.5-flash`
The general-purpose workhorse for everything that writes prose or grades structured rubrics:
- **enrichment-trigger** — grounded-search thesis / flow-intent per ticker (`MODEL_NAME`). Google Search tool attached; no `response_schema` (incompatible with grounding) — relies on a strict-JSON prompt contract.
- **overnight-report-generator** — daily editorial report (`GEMINI_MODEL`). `response_schema=ReportResponse`.
- **signal-ranker Scorer** — fans out over candidates, grades flow/regime/narrative 1-10 (`SCORER_MODEL`). `response_schema=ScorerOutput`. Temperature intentionally **unset** (3.x degrades under pinned low temp; schema enforces structure).
- **x-poster** — Planner→Writer→Reviewer ADK agents draft tweets (`GEMINI_MODEL`).
- **blog-generator** — weekly blog + newsletter (`GEMINI_MODEL`). *Code migrated but service not deployed.*
- **gammarips-eval judges** — LLM-as-judge for `report_factuality` + `quality` (`config.yaml: judge_model`). **`temperature=0.0`** kept for deterministic judging.

### Reasoning / final pick → `gemini-3.1-pro-preview`
- **signal-ranker Picker** (`PICKER_MODEL`) — the one model that makes the actual daily call. Pro tier earns its keep on the single high-stakes decision; deliberately *not* downgraded to flash.

### Images → `gemini-3-pro-image-preview`
- **x-poster** image generation (`IMAGE_MODEL`) + the `scripts/generate_*` brand/OG helpers.

### Prompt tuning (offline) → `gemini-2.5-pro`
- **`signal-ranker/scripts/vapo_zeroshot.py`** (`VAPO_TUNING_MODEL`) — zero-shot prompt-optimization lint pass. Not a runtime dependency; runtime Scorer/Picker are the models above.

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
4. **Cohort attribution:** every V5.4 pick records `v5_4_scorer_model` + `v5_4_picker_model`
   (`signal-notifier` writes them to `todays_pick`). When the Scorer/Picker model changes mid-cohort,
   segment EV evaluation by `v5_4_scorer_model` — do not pool across models.

## How to swap a model (one line, no code edit)

Model ids are env vars pinned in each service's `deploy.sh`; flip the value and redeploy.

| Service | Env var(s) | Endpoint |
|---|---|---|
| enrichment-trigger | `MODEL_NAME` (+ `VERTEX_LOCATION=global`) | thesis |
| overnight-report-generator | `GEMINI_MODEL` | report |
| signal-ranker | `SCORER_MODEL`, `PICKER_MODEL` (+ `GOOGLE_CLOUD_LOCATION=global`) | Scorer / Picker |
| x-poster | `GEMINI_MODEL` (text), `IMAGE_MODEL` (image) | tweets / images |
| blog-generator | `GEMINI_MODEL` | blog/newsletter |
| gammarips-eval | **`config.yaml: judge_model`** (authoritative; `JUDGE_MODEL` env is inert) | judges |
| overnight-scanner (`src/enrichment`) | `MODEL_NAME`, `TECHNICALS_ANALYZER_MODEL_NAME`, `NEWS_ANALYZER_MODEL_NAME`, `MACRO_THESIS_MODEL_NAME` | scanner-era analyzers |
| VAPO script | `VAPO_TUNING_MODEL` | offline tuning |

Always smoke-test against the **deployed** service after a swap (local vs container SDK can diverge),
and check logs / `llm_traces_v1` for `NOT_FOUND` / fallback. See
`docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md` for the verification recipe.
