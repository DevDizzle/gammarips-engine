# 2026-05-09 — Moneyness sign bug fixed + Scorer/Picker prompts get trading-context preamble

## Decision

Two coupled changes landed on 2026-05-09 (Saturday) before Monday 2026-05-11
07:30 ET first live V5.4 cron:

1. **Moneyness sign bug fix** in `enrichment-trigger/main.py:214`. Was
   `moneyness = abs(strike_f - px_f) / px_f`. Now direction-aware:
   - BULLISH (call): `(strike - spot) / spot` — positive = OTM, negative = ITM.
   - BEARISH (put): `(spot - strike) / spot` — positive = OTM, negative = ITM.
   The signal-notifier gate `moneyness_pct BETWEEN 0.05 AND 0.10` now correctly
   filters 5-10% OTM only; ITM contracts (negative moneyness_pct) fail the gate.

2. **Scorer prompt promoted v3 → v4; Picker prompt promoted v2 → v3.** Both
   now include a "Trading Context" preamble that tells the LLMs the actual
   mechanics (3-day hold, +80% take-profit / −60% stop on premium, entry
   10:00 ET, exit 15:50 ET day-3) and the goal (select contracts most likely
   to print +80% in 3 days). Scorer gains an explicit ITM hard cap
   (`flow_conviction ≤ 4` if `moneyness_pct < 0`) and tighter contract-structure
   calibration anchors. Picker gets a structure tiebreaker rule.

## Why

**Concrete trigger:** the 5/8 V5.4 backfill earlier today picked URI
($880 strike vs $944.12 spot = 6.79% ITM) as a "BULLISH 6.79% OTM" trade.
The +80% bracket on URI's $98.52 mid-price requires the underlying to rip
~10%+ in 3 days — structurally near-impossible. The Picker chose URI because
the prompts grade narrative quality and flow conviction, but never told it
the trade had to print +80% in 3 days.

**Two independent failures stacked:**
1. The moneyness gate was filtering 5-10% in absolute distance, not 5-10%
   OTM, because `moneyness_pct` was stored as `abs()`. ITM contracts passed
   through silently for at least the V5.3 era and into V5.4.
2. The Scorer/Picker prompts treated "interesting flow with strong
   narrative" as the goal, not "contract that prints +80% in 3 days." This
   meant even with sign-aware moneyness, the LLM had no reason to penalize
   ITM picks.

**Literature support for the prompt change:**
- **Pan & Poteshman 2006** ("The Information in Option Volume", RFS) —
  informed-trader directional signal is strongest in OTM contracts because
  of leverage. The Scorer should reward OTM, not ITM, when the trade is
  directional.
- **Coval & Shumway 2001** ("Expected Option Returns") — ITM calls have
  lower expected returns and lower volatility; the wrong shape for an
  asymmetric +80%/−60% bracket designed for OTM gamma exposure.
- **Easley, O'Hara & Srinivas 1998** ("Option Volume and Stock Prices") —
  informed traders pick moneyness to maximize leverage given conviction;
  for short-dated directional bets, that's OTM.

## Schema transition (forward-only)

Existing rows in `overnight_signals_enriched` (scan_date ≤ 2026-05-08)
have `moneyness_pct` stored as `abs()` — both ITM and OTM contracts have
positive values, indistinguishable. Rows from the next scanner cron forward
(Mon 2026-05-11 23:00 ET → scan_date 2026-05-12) have signed values.

- **Reads:** signal-notifier gate `BETWEEN 0.05 AND 0.10` works for BOTH
  schemas. Old rows let ITM through (broken state we lived with). New rows
  correctly filter ITM out. No code change needed at the gate.
- **Display:** signal-notifier formats `f"{money * 100:.1f}% OTM"` at lines
  470 and equivalent. With ITM filtered out upstream, display only shows
  OTM percentages.
- **Backfills:** for any backfill against pre-fix data, use direct
  strike-vs-underlying check (see `signal-ranker/scripts/backfill_5_8.py`).
- **Cohort attribution:** rows pre-2026-05-12 have schema v1 moneyness_pct;
  post = schema v2. Pivots that depend on the sign should filter on
  scan_date.

## Out of scope (deliberately)

- **No retroactive BQ UPDATE on existing rows.** Mutating production data
  is risky and not necessary — the gate already works on both schemas.
- **No prompt re-tune via VAPO yet.** v4/v3 are the literature-grounded
  shape; VAPO is deferred until ≥30 closed V5.4 trades give a real fitness
  signal.
- **No new BQ schema column for "moneyness_signed".** Reusing the existing
  column with new semantics + a one-line comment in the compute site is the
  surgical fix.

## Files

- `enrichment-trigger/main.py` — moneyness compute now direction-aware.
- `signal-ranker/prompts/scorer_v4.md` — new prompt with trading-context
  preamble + ITM hard cap.
- `signal-ranker/prompts/picker_v3.md` — new prompt with trading-context
  preamble + structure tiebreaker.
- `signal-ranker/app/agent.py` — load_prompt calls bumped to v4/v3.
- `signal-ranker/app/tools.py` — `SCORER_PROMPT_VERSION=4`,
  `PICKER_PROMPT_VERSION=3`.
- `signal-ranker/scripts/backfill_5_8.py` — one-off backfill with explicit
  ITM exclusion against pre-fix BQ data.
- `docs/DECISIONS/2026-05-09-moneyness-fix-and-trading-context-prompts.md`
  — this note.

## Rollback path

If Monday's first live V5.4 cron produces a clearly-broken pick attributable
to the new prompts, rollback is two `gcloud run services update --update-env-vars`
calls plus restoring the old `load_prompt` filenames in agent.py:
- `SCORER_PROMPT_VERSION=3 PICKER_PROMPT_VERSION=2`
- agent.py:90 → `scorer_v3.md`, agent.py:191 → `picker_v2.md`

The moneyness fix in enrichment-trigger has no rollback need — it's a strict
correctness improvement.

## Backfill of 5/8

Re-ran V5.4 ranker against scan_date 2026-05-07 with v4/v3 prompts and
ITM-excluded candidates via `backfill_5_8.py`. Replaces the prior URI
backfill (which itself replaced V5.3's UHS).
