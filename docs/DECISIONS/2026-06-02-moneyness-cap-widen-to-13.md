# 2026-06-02 — Widen the moneyness cap 0.10 → 0.13 (STRICT path)

**Status:** IMPLEMENTED in code 2026-06-02 (owner-directed), pending `gammarips-review` on the diff + `bash deploy.sh`. STRICT path only; FALLBACK cap decoupled and pinned at 0.10.
**Service:** `signal-notifier` (`MONEYNESS_MAX`, `_build_candidate_query` STRICT branch).
**Decision owner:** Evan — directed for pick-slate width; overrides the N≥15-closes lock for this gate.
**Evidence:** realized-option-PnL backtest, N=1,375 fills (`backtesting_and_research/moneyness_band_study.py`).
**Related:** [[2026-06-02-voi-gate-relaxation-proposal]], [[2026-05-06-lit-audit-h11-h12-spread-moneyness]] (the H12 tightening this revisits), [[2026-06-01-daily-cadence-fallback]].

## Problem

The picker is starved (median ~2 candidates/day). The funnel collapses ~123 enriched → ~5 before the LLM ranker. The `moneyness 0.05-0.10` gate is the single harshest filter. The operator wants more *good* candidates reaching the picker ("if I have 2 POS candidates I get a POS pick").

## Mechanism correction (why this is NOT a literature reversal)

The 2026-05-06 H12 decision tightened the cap 0.15 → 0.10 citing Aretz et al. 2023 / Augustin et al. 2022 — the deep-OTM long-call EV cliff. **That cliff is a HOLD-TO-EXPIRY phenomenon:** you overpay the variance-risk-premium / skew at entry and bleed it via theta over the option's *life*, and the lottery overpricing only burns you if you ride to (or near) expiry. Our trade is the opposite shape:
- **3-day max hold** on a 7-45 DTE option → theta over 3 days is a rounding error; we never ride to expiry.
- **+80% target / −60% stop** → we trade the gamma/delta move, not a tail jackpot, and the stop caps the bleed.
- **Conditioned on directional UOA flow** → not the *average* OTM option the papers measure.

So the cited literature is evidence about a *different trade*. It does not bind here. (Earlier review flagged "don't reverse the literature on N=123" — but that principle applies to claims the literature actually covers; this one it does not.)

## Evidence (realized option bracket PnL, N=1,375)

`moneyness_band_study.py` re-replayed the +80/-60 bracket on cached option minute bars with realistic spread-based cost, stratified by moneyness. The slice the cap admits beyond 0.10 (flat-1.02 cost; ~1-1.5pt optimistic):

| increment | n_fill | mean ret | 90% CI |
|---|---|---|---|
| 10-12% | 60 | +11.5% | [+0.017, +0.211] |
| **10-13%** | **87** | **+8.9%** | **[+0.014, +0.163]** |
| 10-15% | 123 | +7.4% | [+0.012, +0.140] |

Fine bins show the edge is real but noisy, and the **(0.14, 0.15] bin is toxic (−15%, CI all-negative)** — so the cap stops at 0.13 to exclude it. 0.13 vs 0.12 is within noise; 0.13 keeps ~27 more candidates at the same EV (serves the slate-width goal). Per-day: 10-13% candidates appear on ~82% of days (~4.5/day) — reliably widens the daily slate, not clustered.

## Decision

- **`MONEYNESS_MAX = 0.10 → 0.13`** on the STRICT path.
- **`FALLBACK_MONEYNESS_MAX` DECOUPLED and pinned at 0.10** (was `= MONEYNESS_MAX`). Fallback fires only on zero-strict-candidate (lowest-conviction) days — the worst place for deeper-OTM names. The widening applies only where the evidence is (STRICT), not where conviction is weakest.
- Floor unchanged at 0.05 (ATM/ITM buckets are clearly negative, −5.5% / −5.0%; do not admit them).
- Cap stops at 0.13 (excludes the toxic 0.14-0.15 bin).

## Caveats (carry forward)

1. **Thin, single-regime evidence.** 10-13% increment is N=87 / ~one momentum-ish quarter. This is a reasonable forward bet, not a proven edge.
2. **Cost-realism is structurally unmeasurable here.** The trader books flat-1.02 entry with no exit haircut and we have no real-capital fills, so live paper EV of these picks will be *optimistically biased* and won't fully settle deep-OTM friction. Spread is capped ≤8% upstream, which bounds (not eliminates) the concern.
3. **0.13 is a sensible cut, not a data-identified breakpoint** — the bins are noisy; do not over-read the exact decimal.

## Monitoring / revert

- **Kill switch:** set `MONEYNESS_MAX` back to `0.10`. One line.
- **Measurement (no tag field needed):** the newly-admitted cohort is recoverable by JOIN — `forward_paper_ledger` rows with `scan_date >= 2026-06-02` JOIN `overnight_signals_enriched` on (ticker, scan_date) WHERE `moneyness_pct` in (0.10, 0.13]. Compare their realized EV to the 5-10% cohort. Revisit after ~10 such closes; revert if they underperform.

## What this does NOT change

- The floor (0.05), the FALLBACK cap (0.10), and every other gate (V/OI already removed, OI/vol/DTE/regime/earnings/active-days). Unchanged.
- Trader execution mechanics and the one-pick-per-day cap. Unchanged.
