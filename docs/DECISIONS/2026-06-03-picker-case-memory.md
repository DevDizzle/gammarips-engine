# 2026-06-03 — Picker case-memory harness (picker_v5)

**Status:** SHIPPED (signal-ranker only; non-gating, advisory)
**Owner:** Evan
**Decision type:** selection-stage policy change (Picker inputs)

## What

The V5.4 Picker now receives a curated **case-memory** block, `closed_trades_case_memory`,
injected as a fenced instruction block exactly like `top_5_block` / `ledger_block`
(no ADK MemoryService — that is session-recall RAG and the wrong tool; direct
instruction injection is deterministic and auditable).

The block = two files under `signal-ranker/case_memory/`:
- `quant.md` — 12 hand-authored, ledger-independent priors (Q1–Q12: earnings exclusion,
  spent-catalyst, VRP, short-DTE theta cliff, convexity, moneyness, direction EV
  asymmetry, timeout dominance, HEDGING flow, oversold-fade, contango, speed).
- `exemplars.md` — a bounded (~50-case, ~12K-token) curated subset of the full
  `bull.md` (846) / `bear.md` (529) library, grouped by the lesson each teaches.

The full library + provenance are built by `scripts/ledger_and_tracking/build_case_memory.py`
(read-only): it joins `realized_label.pkl` (FILLED rows — option outcome + underlying
path) with `overnight_signals_enriched` (ex-ante greeks/IV/catalyst/flow) on
`(recommended_contract, scan_date)`, overlays the matched live `forward_paper_ledger`
closes, and emits `bull.md`, `bear.md`, `exemplars.md`, `case_index.parquet`,
`build_manifest.json`.

Each case = ex-ante features + a **deterministic** "WHY" (first-order option-physics
decomposition: theta drag / delta capture / inferred IV residual) + a takeaway. No LLM
authors a cause. **Outcome is keyed on `realized_ret>0` (option PnL), NOT `is_win`
(stock direction) — the two disagree 44.2% corpus-wide.** That gap (stock moved your
way, option still lost — the "two-label trap") is the central lesson the harness teaches.

## Why

V5.4 was down ~24% in a bull tape with consecutive losses — the picker doesn't
understand *why* its picks lose at the option level. Curated, causally-labeled
exemplars give it analogical grounding (in-context few-shot, Brown 2020) — better
calibration on contract structure, not "emergent" magic. Honest expected benefit:
small, possibly-zero selection-quality lift, to be observed, not assumed.

## Leakage adjudication (audited by gammarips-review)

**Structural verdict: NOT lookahead bias.** Every case is a strictly-closed past trade
(`scan_date_max` 2026-05-28), the block is static-per-deploy, nothing is dated relative
to the live `scan_date`, and the live candidate path is still gated by `assert_no_leakage`.
The block is advisory and never gates the pick (still constrained to the top-5 set).

**ACCEPTED, BOUNDED VECTOR — same-ticker outcome import.** Because cases carry the
ticker, a live candidate on a frequently-traded name (ADI, ACN, BSX, HTZ, INTU…) may
appear with prior resolved outcomes in the block. This is **not strict leakage** — the
*specific contract* being decided (different strike/expiry/date) has an unknown outcome,
and "we lost on ADI calls twice" is legitimate experience, not future data. But the
mechanism is real: ticker identity collision surfaces a past outcome into the live
decision. We accept it as a *prior on the ticker's behavior*, bounded by: outcome is for
a different contract; block is direction-and-structure framed, not "ticker X always
loses"; exemplars explicitly tagged anecdote-not-edge. Revisit if picks show ticker-recency
bias (e.g. systematic avoidance of any recently-lost ticker regardless of setup).

**Exemplar selection** uses hindsight (most-extreme `|realized_ret|` per pattern) — this
selects *teaching examples*, not candidates, so it does not leak into the decision; the
residual risk is pedagogical over-anchoring on tails, mitigated by the anecdote framing.

## Correctness safeguards (review findings, all fixed)

1. **Fail CLOSED, not open, under v5.** If `case_memory/` doesn't ship, an empty block
   under `PICKER_PROMPT_VERSION>=5` would silently degrade to v4 behavior while persisting
   `picker_prompt_version=5` — corrupting cohort attribution. `run_picker` now raises
   `case_memory_empty_under_v5` (signal-notifier fails closed; no mislabeled trade).
   `RankResponse.case_memory_bytes` surfaces the injected size per run.
2. **Pre-deploy guard.** `deploy.sh` asserts `quant.md` + `exemplars.md` are non-empty and
   `build_manifest.json` parses before building.
3. **This note** records the same-ticker vector as accepted+bounded.

## Single-regime caveat

The corpus is one 2026-Q2 war-chop regime (vix3m ~20-21). Distilled *patterns* are
signal; individual case outcomes are anecdote. Live cases are authoritative but few (6).

## Governance

The owner explicitly **waived** the N≥15 lock / 30-day-OOS / Definition-of-Done ceremony
for this change (case-memory is advisory and non-gating; V5.4 is expected to freeze on the
5-consecutive-loss rule, voiding the N≥15 lock by its own logic). Leakage correctness was
NOT waived and was audited (above).

## Maintenance

- `quant.md` is hand-authored and NOT regenerated — review it on every rebuild (it can
  drift from policy, e.g. the moneyness band).
- Regenerate after new live trades close: `python scripts/ledger_and_tracking/build_case_memory.py`.

## Rollback

Set `PICKER_PROMPT_VERSION=4` in `deploy.sh` and load `picker_v4.md` in
`_build_picker_instruction`, redeploy. The case_memory/ files and builder are inert
without the wiring.

## Deferred (next, if it earns it)

- Flash narrative prose pass over the deterministic physics blocks (readability A/B).
- Phase-2: lift `case_index.parquet` into a feature→outcome graph.
- Direction-aware / structure-similarity retrieval instead of the static bounded block.
