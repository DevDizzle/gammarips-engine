# 2026-06-09 — Macro/sector report context + quant.md priors at the tournament final round

**Status:** IMPLEMENTED + DEPLOYED (signal-judge rev `signal-judge-00004-8k5`, overnight-report-generator rev `overnight-report-generator-00018-jbd`). `gammarips-review`: **PASS** (leakage-clean, picker-pure, fail-open, no trader gate). Owner-directed; G-Stack ceremony waived by the owner — only the leakage audit was non-negotiable, and it passed. Forward-only; no backfill.

## Decision
Give the V6 tournament the two things it was blind to — the **macro/regime environment** and **sector rotation** — and a **rulebook** for how to weigh them, without touching the trader and without re-introducing a rubric/gate.

Two coordinated changes, shipped as matched pairs (each new report observable has a quant.md rule that says how to act on it):

1. **Report = the market facts.** `overnight-report-generator` now computes and renders two new deterministic, point-in-time sections in every daily report:
   - **Macro & Regime Backdrop** (FRED, keyless): VIX level + 1d/5d trend, VIX term-structure slack (VIX/VIX3M), 10y/30y rate level + trend, and a composite **risk-on/off** label with its driving reasons.
   - **Sector Tape** (Polygon): a 12-ETF momentum panel (XLK, SMH, XLE, XLF, XLV, XLY, XLP, XLI, XLU, XLB, XLRE, XLC) — YTD / 1-month / 5-day return + a 5-day **drawdown-in-sigma**, plus `crowded_rotating` / `oversold_lagging` rotation flags.
   - New module `overnight-report-generator/market_context.py`. Everything is as-of `underlying_scan_date` (the scan night), **non-blocking and fail-open**: every fetch degrades to `UNKNOWN`/`None` and can never 404 the report (an empty `report_md` strips ALL context from the tournament — strictly worse than a missing block).

2. **quant.md = the rulebook, injected at the FINAL round only.** The hand-authored, ledger-independent priors file (`signal-judge/case_memory/quant.md`) is now loaded (quant.md **only** — `exemplars.md` deliberately excluded) and injected into the tournament's **championship round** (`k == 1`, the single ≤10-finalist batch that crowns each bracket winner) — **not** the cheap early cull rounds. That's **3 rulebook injections per pick** (one per bracket final), not ~30. Added rules **Q13–Q18** for the new context:
   - **Q13** — VIX direction conditions the Q7 direction tilt (rising/spiking tape ⇒ don't lean bullish).
   - **Q14** — term-structure slack grades Q11's vol cushion (thin contango ⇒ more theta-skepticism).
   - **Q15** — rising long-end yields are a headwind for high-multiple bullish longs.
   - **Q16** — risk-on/off is the first regime read; conditions the directional/theta priors.
   - **Q17** — discount long premium into a >2σ sector drawdown (falling-knife tape).
   - **Q18** — a `crowded_rotating` sector haircuts the reliability of the flow's directional read (route through Q9/Q2).

## Why
- **The report was the only context lever besides the prompt + per-contract JSON, and it was regime-blind.** During the 06-05/06 semiconductor crash (SOX ~−10% single session, VIX 5-day rising, 10y > 4.5%, rotation out of tech into healthcare/financials), the picker had no idea a semi/AI bullish call was buying into a risk-off, rotating tape. The new context closes exactly that blindness (verified live: the 2026-06-09 report renders `RISK_OFF` + XLK `crowded_rotating` / XLV+XLF `oversold_lagging`).
- **The rulebook existed but was switched off.** `quant.md`, `exemplars.md`, and the `render_case_memory_for_picker` seam were built 2026-06-03 for `judge_v6`, then disconnected when V6 collapsed to "no memory" 24h later (`case_memory_bytes=0`). This re-arms **quant.md only**, and only where deep judgment happens (the final round), so the early rounds stay the lean "is this even plausible" cull V6 intended.
- **Matched pairs.** A report field with no rule is noise the LLM rationalizes around; a rule with no field is unactionable. Each Q13–Q18 cites the report field it reads.

## What is NOT changed
- **The trader.** No new execution gate; `forward-paper-trader` is untouched. Entry/stop/target/hold/trail/exit mechanics unchanged.
- **Tournament purity.** quant.md is injected as advisory **PRIORS** ("weigh them, they never override the goal"), never a hard gate or numeric weight. Q13–Q18 are all explicitly "never a gate / never a disqualifier." The early cull rounds get **no** rulebook.
- **Exemplars.** `exemplars.md` stays excluded (it is generated from a single 2026-Q2 war-chop backfill; regime-overfit risk).
- **Candidate leakage gate.** `assert_no_leakage` still runs on every candidate; the macro/sector context enters via `report_md` (market-wide), not via candidate fields.

## Leakage / honesty
- **Point-in-time, backtest-safe.** FRED is `cosd`-bounded and `d <= scan_date`-filtered; Polygon closes are range-end-bounded and `bar_date <= scan_date`-filtered on BOTH the return windows and the trailing-σ window (a suffix of the same as-of list). No web sources. `gammarips-review` confirmed no future data reaches the picker.
- **Evidence honesty.** Our realized corpus is a single calm 2026-Q2 regime (VIX 15.7–19.5, contango pre-gated, no rate/sector columns), so it **cannot** validate cross-regime macro or any sector rule. Q13–Q18 are therefore labeled `LITERATURE-ONLY` (settled market behavior: leverage effect, term structure, equity duration, sector momentum/rotation), **not** "confirmed on ours." Per owner direction, sensible-on-known-behavior priors are acceptable to start; this is forward-only and never backfilled.

## Files
- `overnight-report-generator/market_context.py` (new), `overnight-report-generator/main.py` (payload + 2 prompt sections), `overnight-report-generator/deploy.sh` (mount `POLYGON_API_KEY`).
- `signal-judge/case_memory/quant.md` (Q13–Q18), `signal-judge/app/tools.py` (`load_quant_md`), `signal-judge/app/agent.py` (final-round injection; `case_memory_bytes` now reports quant.md size).

## Cost / ops
~16 extra HTTP fetches on the once-daily 07:00 ET report path (4 FRED + 12 Polygon ETFs, 6-way threaded, all bounded + fail-open under the 540s Cloud Run timeout). quant.md adds ~10 KB to the 3 final-round prompts only.

## Follow-ups (not blockers)
- Forward shadow / per-rule attribution to see whether Q13–Q18 actually move outcomes (owner waived the N≥15 hard pause; this is observational, not a gate).
- Web-sourced live narrative (Fed posture, rotation headlines) was scoped but **deferred** — it is forward-only/non-reproducible and requires a dual-write leakage scrub at `main.py` before it can ship. Not in this change.
