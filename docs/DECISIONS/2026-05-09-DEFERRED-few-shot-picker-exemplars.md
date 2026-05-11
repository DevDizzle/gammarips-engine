# DEFERRED — Few-shot exemplars for the V5.4 Picker

**Status:** DEFERRED. Not implemented. Trigger: V5.4 ledger has ≥15 closed
trades (≥5 winners AND ≥5 losers, ideally with ≥3 time-exits).

**Original idea (Evan, 2026-05-09):** show the Picker "what ripped yesterday"
so it can pattern-match against contracts with similar features and bias
today's pick toward similar structure.

## Why this is on hold, not killed

The mechanism is sound — few-shot exemplar prompting is well-established for
LLM grounding (Brown et al. 2020 GPT-3 paper and successors). Concrete
examples ground abstract goals like "print +80% on premium in 3 days" better
than the rule-based language in the v4/v3 trading-context preamble alone.

**Three reasons we don't ship it now (2026-05-09):**

1. **N=0 problem.** Ledger was truncated 2026-05-08. First V5.4 close lands
   ~2026-05-15 (Mon-entry hold runs Wed-Fri). At 1-2 picks/week we hit N=15
   around mid-July at the earliest. Below ~15 closed trades, the exemplar
   set is noise — the LLM will pattern-match on irrelevant features
   (ticker letter, sector, weekday).
2. **Survivorship + regime-bias risk if framed wrong.** "Here are recent
   rippers" alone biases the LLM toward winners. Must be symmetric (winners
   + losers + time-exits) and explicitly framed as "pattern context, not
   instruction." Otherwise we're extrapolating from a 2-week sample in a
   non-stationary market — exactly the failure mode the V5.3 lit audit
   2026-05-06 warned against.
3. **Picker already has a coarser version.** `ledger_summary` (14d aggregate
   by direction × policy_version) is the same idea at low resolution.
   Row-level exemplars would be a richer dose of the same medicine —
   marginal value is real but bounded.

## When to revisit

When `forward_paper_ledger` (filtered to `policy_version='V5_4_AGENT_RANKER'`
and `realized_return_pct IS NOT NULL`) has:
- ≥15 closed trades total, AND
- ≥5 with `realized_return_pct > 0` (winners), AND
- ≥5 with `realized_return_pct < 0` (losers).

Time-exits (mid-bracket exits at 15:50 ET day-3) are bonus — they're the
hardest exemplar class to learn from rules alone, so even N=3 of those is
informative.

## Two design paths to choose between (don't decide now, decide at trigger)

### Path A — Few-shot Picker exemplars (the original idea, surgical)

Add a new field to the Picker prompt: a compact JSON list of 5 winners +
5 losers + 5 time-exits from the last 14 trading days. Each exemplar has:
ticker, direction, signed_moneyness_pct, DTE, mid_price, V/OI ratio,
outcome (`+80`/`-60`/`time-exit`), time-to-exit (in trading-day fractions
or hours).

Scorer does NOT get exemplars — it scores one candidate in isolation, no
comparison context to ground exemplars against.

**Upside:** richest signal, lets the LLM pattern-match contract structure
against actual outcomes.

**Downside:** real overfitting risk on small N. The LLM may notice a
spurious correlation (e.g., 4 of 5 winners were puts → bias toward bearish
today). Mitigation: explicit "use as pattern context, not as a rule" framing
in the prompt; rotate exemplars to avoid stable bias.

### Path B — Deterministic feature aggregates (the safer alternative)

Pre-compute bucket statistics in Python and inject as text:
> "In the last 14 trading days under V5_4_AGENT_RANKER:
>  - OTM 5-8% / 7-15 DTE / V/OI > 5: 7-of-10 winners, avg +52%.
>  - OTM 10-15% / 28+ DTE: 1-of-4 winners, avg -22%.
>  - HEDGING flow: 0-of-2 winners (bracket cap fired both)."

**Upside:** deterministic, transparent, audit-friendly, won't overfit to
irrelevant features.

**Downside:** you only learn what you bucket. Dimensions you didn't think to
slice are invisible. Requires ≥15 closes per cell to be meaningful, so
buckets must be coarse.

### Recommended hybrid (when triggered)

**B with breadcrumbs from A.** Lead with deterministic bucket stats; follow
with 2-3 vivid winner exemplars + 2-3 losers as anchors. The bucket stats
do the conditioning; the exemplars give the LLM grounded examples without
letting it overfit. Total prompt overhead ~600-800 tokens — bounded.

## What NOT to do

- **Do NOT show the LLM only winners.** Survivorship bias produces overconfident picks.
- **Do NOT use exemplars from before V5.4 promotion** (`scan_date < 2026-05-08`).
  Different policy version, different bracket, different cohort — apples to oranges.
- **Do NOT compute aggregates over a window > 30 trading days.** Regime drifts
  faster than that; older data dilutes recent signal.
- **Do NOT add exemplars to the Scorer.** The Scorer evaluates one candidate
  in isolation; comparison context doesn't help it score that candidate.

## Trigger checklist (run when N≥15)

When ready to revisit:
1. Confirm trigger thresholds via `SELECT COUNTIF(realized_return_pct > 0)
   AS winners, COUNTIF(realized_return_pct < 0) AS losers, COUNT(*) AS total
   FROM forward_paper_ledger WHERE policy_version='V5_4_AGENT_RANKER' AND
   realized_return_pct IS NOT NULL`.
2. Decide Path A vs B vs hybrid based on what the data actually shows
   (e.g., if a single bucket dominates, B is enough; if winners look
   structurally diverse, A or hybrid).
3. Bump prompts to scorer_v5 / picker_v4 with the new exemplar field. Keep
   the trading-context preamble unchanged — it's separate concern.
4. gammarips-review for cohort drift / lookahead before deploy.
5. New decision note in `docs/DECISIONS/` superseding this one.

## Related work

- 2026-05-09-moneyness-fix-and-trading-context-prompts.md — the v4/v3
  preamble that this design extends.
- 2026-05-09-report-v2-literature-grounded.md — report v2 already gives
  the Picker richer cross-sectional context (sentiment shift, divergences,
  per-candidate calls). Few-shot exemplars are temporal context, complementary
  to the report's cross-sectional context.
- Brown et al. 2020 ("Language Models are Few-Shot Learners") — original
  empirical case for in-context exemplar prompting.

## File / memory cross-references

- This file: `docs/DECISIONS/2026-05-09-DEFERRED-few-shot-picker-exemplars.md`
- Memory pointer:
  `~/.claude/projects/-home-user-gammarips-engine/memory/project_deferred_few_shot_picker_exemplars.md`
