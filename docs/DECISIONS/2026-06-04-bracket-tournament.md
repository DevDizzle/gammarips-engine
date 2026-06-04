# 2026-06-04 — Bracket tournament replaces the single judge; selection gates removed

**Status:** IMPLEMENTED, pending `gammarips-review` (leakage) + deploy. Owner-directed. The G-Stack ceremony is waived by the owner; only the leakage audit is non-negotiable.

## Decision
Replace the single `judge_v6` call with a **randomized bracket tournament** over **all** enriched signals, and **remove the per-candidate selection gates** so every signal gets a chance.

- **signal-judge** (`tournament_v1`, version 7): 3 independent brackets. Each bracket: shuffle the pool, split into batches of **≤10**, each call ranks its batch and **top-2 advance** (top-1 in the single final batch), repeat until one remains (94→20→4→1). The **consensus** winner across the 3 brackets is the pick (3/3=high, 2/3=medium, 1/3=low confidence). Dead-simple prompt ("make money buying a single option, sell for profit within 3 days") + the daily **report** for context + the structured per-contract JSON. **No memory, no rubric, no weights.**
- **signal-notifier**: the candidate query is **ungated** — the moneyness, OI, volume, DTE, and V/OI selection gates are removed, `LIMIT 10` → `LIMIT 200`, and the rich feature columns (technicals, narrative, greeks) are added so the judge gets the full JSON. The **active-days liquidity gate is bypassed** (and its ~N per-candidate Polygon calls dropped).

## Why
1. **The rigid scorer over-fit junk.** On 2026-06-03 the gated `judge_v6` picked BBWI (engine score **2**, a beaten-down retailer) because the option was cheap, while FTNT/ADI/QCOM-class names with $100M+ institutional flow were either down-ranked or gated out. Removing the gates + a simple prompt over the full pool surfaces the real flow names.
2. **The selection gates were choching winners on stale data.** Scan-time OI is a one-day-stale snapshot — the sweep that earns the score only becomes OI the *next morning* (proven in-data: CAR OI 3→103 overnight; 36%+ of OI-rejected contracts recover). We enter at 10:00 ET and the OI builds behind us — that early entry is the thesis, not a liquidity risk. So we stopped filtering on it.
3. **Features barely separate winners from losers** (bull EV ~+4%, flat across flow/momentum/score/catalyst). A rigid scorer can't extract an edge that isn't there; a simple judge over the full pool at least picks *sensible, report-aligned* trades. Robustness (top-2 + 3-run consensus) removes the single-elimination seeding luck.

## What is KEPT (safety, not selection)
- **No earnings during the hold** (IV crush; literature-settled) — still excluded in `run_notifier`.
- **Regime fail-closed** (VIX ≤ VIX3M) — still checked before the judge is called.
- **A tradeable contract must exist** (strike/expiration NOT NULL) and regime data present (vix3m NOT NULL).
- **Leakage**: every candidate is `assert_no_leakage`-checked before the LLM; the query deliberately does NOT select outcome columns (`next_day*`, `day2/3_*`, `peak_return_3d`, `is_win`, `outcome_tier`, `performance_updated`).

## Cost
~408K input + ~3.5K output tokens/pick (39 calls). ≈ $0.85/pick (~$18/mo) at assumed pro pricing — dominated (83%) by the per-contract JSON, not the report. Not optimized; the cheap lever later is trimming the round-1 contract JSON.

## Persistence / cohort
`signal_ranker_runs` DDL unchanged. The tournament has no rubric scores, so the REQUIRED rubric columns carry an **advancement proxy** (round reached → 1-10). Only finalists + winner + runner_up get rows. Mirrored into both scorer/picker columns at **version 7** so the cohort is cleanly separable (5=two-stage, 6=judge_v6, 7=tournament).

## Reversibility
`git revert` the commit → restores the gated query + judge_v6 single call; redeploy signal-judge + signal-notifier.

## Open / next
- The trader still uses `recommended_contract` at 10:00 ET entry — if a contract is genuinely untradeable at entry, the paper fill will reflect that (a data point, not a crash).
- Watch realized PnL of the tournament cohort (version 7) vs the gated cohort. Selection is a weak lever (EV ~flat); the real test is whether the report-aligned full-pool picks beat the gated ones.
- Cost trim (round-1 JSON), 2-vs-3 runs, and the OI-build/early-entry timing study remain open.
