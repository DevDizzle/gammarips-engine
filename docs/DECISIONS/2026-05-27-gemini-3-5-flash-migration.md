# 2026-05-27 — Gemini model migration: `gemini-3-flash-preview` → `gemini-3.5-flash`

## Decision

Migrate every **text-generation** Gemini call in the engine from `gemini-3-flash-preview`
to **`gemini-3.5-flash`** (GA 2026-05-19). Ship the whole pipeline now; **segment the V5.4
paper cohort by `v5_4_scorer_model`** (equivalently `scan_date >= 2026-05-27`) so the 3
existing `gemini-3-flash-preview` closed trades are **not pooled** with new-model trades for
the 15-/30-trade EV gates. Operator-approved 2026-05-27.

**Out of scope (deliberately untouched):** the Picker (`gemini-3.1-pro-preview` — not on the
cull list, deliberate pro-tier decider), x-poster image gen (`gemini-3-pro-image-preview`),
VAPO tuning script (`gemini-2.5-pro`), and `agent-arena` (dead service).

## Why now (and why it is NOT urgent)

Google's "Gemini Enterprise Agent Platform" deprecation notice names project
`profitscout-fida8` and removes access to `gemini-2.5-flash`, `2.5-flash-lite`, and
`gemini-3-flash-preview` for **inactive** projects on **2026-06-15**. **fida8 is active** — it
calls `gemini-3-flash-preview` every day — so it **keeps access past June 15 regardless**.
This is therefore a **voluntary quality upgrade**, not a forced migration: `gemini-3.5-flash`
is the current stable Flash, is a quality bump, and moves us off a *preview* model that carries
its own separate retirement clock.

## The one gotcha (already handled in this codebase)

`gemini-3.5-flash` is served **only on the Vertex `global` endpoint**, not regional. Verified
live on 2026-05-27:

| model | us-central1 | global |
|---|---|---|
| `gemini-3.5-flash` | **404** | **200** |
| `gemini-3-flash-preview` | 404 | 200 |
| `gemini-3.1-pro-preview` (Picker) | 404 | 200 |

The engine already runs every generative client on `global` — either explicit
`location="global"` or the google-genai (1.74.0) default, which is `global` when
`GOOGLE_CLOUD_LOCATION` is unset (proven by the global-only Picker working in production today).
So no location surgery was needed; we added one explicit `location="global"` pin on the
signal-ranker Scorer client as belt-and-suspenders.

## Behavioral changes beyond the model id (per Gemini 3.x guidance)

- **signal-ranker Scorer** (`signal-ranker/app/agent.py`): removed `temperature=0.2`
  (3.x degrades/loops under pinned low temp; `response_schema=ScorerOutput` enforces structure).
  Selection mechanics (`take_top_n` deterministic weighted-sum sort) unchanged; the Scorer never
  had a `seed`, so no new nondeterminism in the *selection* — only in the integer rubric scores
  feeding the sort.
- **enrichment-trigger** (`enrichment-trigger/main.py`): removed `temperature/top_p/top_k/seed`
  from the grounded-search config. **Tradeoff (accepted):** dropping `seed=42` reduces run-to-run
  reproducibility of the thesis/flow-intent that feed the Scorer. Mitigated by the 12h GCS news
  cache (a successful first write is reused on retry).
- **overnight-report-generator** (`main.py`): removed `temperature=0.7`.
  `response_schema=ReportResponse` unchanged.
- **gammarips-eval judges**: **kept `temperature=0.0`** (determinism for LLM-as-judge;
  monitoring-only, non-gating).

### `thinking_level` NOT set (SDK constraint — caught by smoke test)

The initial diff set `thinking_level` (LOW on the Scorer, MEDIUM elsewhere). The **deployed**
services pin `google-genai==1.22.0`, which predates the `thinking_level` field and **rejects it**
(`ThinkingConfig: extra_forbidden`). This surfaced as a runtime 500 on the first live smoke test —
a green build hid it (the field was only validated when a real request was made). Reverted: no
explicit `thinking_config`. **Thinking remains ON at the SDK/server default** for 3.x, so we still
get reasoning; we just don't pin a budget level. Explicit `thinking_level` control is deferred
until a deliberate `google-genai >= 1.74` bump across services (its own compatibility test).

## Cohort handling (the operator decision)

The pick pipeline (enrichment → report → Scorer) is part of the V5.4 *policy* definition, and we
are changing it mid-cohort (3/15 closed trades). `policy_version` stays `V5_4_AGENT_RANKER` (not
bumped) because per-pick provenance already records the Scorer model: `v5_4_scorer_model` is
written on every `has_pick=True` doc (`signal-notifier/main.py:441` ← `signal-ranker`
`/rank` response). **The 15-/30-trade EV evaluation MUST segment on `v5_4_scorer_model`**
(`gemini-3-flash-preview` for the 3 pre-2026-05-27 trades vs `gemini-3.5-flash` after); do not
pool them into a single headline EV. `scan_date >= 2026-05-27` is the equivalent date boundary.

## Config bug fixed in the same change

`gammarips-eval/config.yaml:6` still pinned `judge_model: gemini-3-flash-preview`, which
overrides the code default — so flipping the code/deploy default alone was a **no-op** for the
eval judges. Fixed the YAML to `gemini-3.5-flash`.

## What changed (env-driven, pinned in deploy config)

Model id is env-driven everywhere (`GEMINI_MODEL` / existing `MODEL_NAME` / `SCORER_MODEL` /
`JUDGE_MODEL`), default `gemini-3.5-flash`, and pinned in each service's `deploy.sh` so future
swaps are one-line with no code edit. Touched: `enrichment-trigger`, `signal-ranker`,
`overnight-report-generator`, `gammarips-eval`, `x-poster`, `blog-generator` (code-only — not
deployed), `src/enrichment/core/config.py`, `libs/trace_logger` (added `gemini-3.5-flash`
pricing row; old keys kept for historical cost rows), and the relevant stale docstrings.

## Review

`gammarips-review` audited the diff: **no lookahead, no leakage, no trade-execution path touched**
(`forward-paper-trader` has zero Gemini calls and is not in the diff). Two blockers it raised —
the `config.yaml` judge no-op and the missing `TRADING-STRATEGY.md`/DECISIONS doc update — are
resolved by this change.

## Verification (Definition of Done)

Per service: deploy via `bash deploy.sh`, then exercise a real generative call and
`gcloud run services logs read <svc> ... | grep -iE 'NOT_FOUND|404|Publisher Model|fallback'`
to confirm the call hit `gemini-3.5-flash` and did not silently degrade. Do not declare done on a
green build alone. Re-probe: `gemini-3.5-flash` @ global → 200.
