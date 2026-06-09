# 2026-06-09 — Narrative vs. options-physics ROI study → one delta prior (Q19)

**Status:** RESEARCH FINDING → acted on (quant.md Q19 added + deployed). Read-only study on the realized backfill; owner-directed to ship the one confirmed prior. Re-confirm cross-regime before leaning hard.

## Question
For realized 3-day **OPTION** PnL (not underlying direction), which feature family is the more reliable ROI lever — **narrative** (catalyst / flow / conviction) or **options physics** (DTE / moneyness / theta / convexity / delta / spread)? Decides whether to tilt quant.md / the picker prompt.

## Data / method
N=1,375 FILLED closed trades, 33 scan-dates, 2026-04-10..05-28 (single calm 2026-Q2 war-chop regime). `realized_label.pkl` + `analysis_option_pnl.parquet` joined to `overnight_signals_enriched` features. Evaluated on `realized_ret > 0` (option PnL), NOT `is_win` (they disagree ~27% overall, ~36% on right-direction trades). EV splits per family with **day-clustered bootstrap CIs** (resample scan-dates, not trades — trade-level CIs over ~33 days overstate confidence). Direction confound (bullish +4.1% vs bearish −7.7%) controlled by reporting within-direction. No sklearn/XGBoost (N-per-cell too small).

## Findings
1. **Neither family is a reliable lever on this regime.** After day-clustered CIs, almost every split in BOTH families straddles zero. Narrative EV spreads 0.4–4.9pp, none significant. Physics slightly larger, mostly non-significant.
2. **The two-label-trap is a physics/magnitude problem, not narrative.** Among 738 right-direction trades, 36% still lost the option. Separators of won-vs-lost:
   - **Move magnitude dominates** — winners' underlyings moved 6.63% vs losers' 4.08% over 3 days (diff +2.55pp, CI [+1.62, +3.53]). The trap is mostly "right way, not far enough to clear theta + spread." *Not a tradeable input (it's an outcome).*
   - **Delta is the only contract feature that cleanly separates won from lost** (0.191 vs 0.122, diff +0.069, CI [+0.003, +0.141]) and is the **single most OOS-stable finding** (H1 +0.067 ≈ H2 +0.069). [CONFIRMED_ON_OURS, single regime]
   - **No narrative feature** (overnight_score, catalyst_score) separates won from lost in the trap pool. [NO_SUPPORT]
3. **Caveats / what was REJECTED:** the "mid-delta band" win did NOT survive cross-conditioning on moneyness (delta/moneyness corr 0.21; positive cells were far-OTM, N=39–53) — so the prior is "**enough** delta," NOT a target band. Broad theta-burn, convexity (Γ·S), IV-rank, and spread priors showed **NO_SUPPORT** (none separated won from lost or cleared zero). Multiple-comparisons haircut: only the trap-delta gap and move-magnitude survive. Narrative showed *no* edge — weaker than "narrative is harmful"; do NOT gut the story layer.
4. **Side-finding (NOT acted on):** `is_premium_signal=True` was significantly worse (−11.3pp). Owner: `is_premium` is a **zombie flag — not filtered on** anywhere in V6, so this is a dead-flag artifact, not a live problem. No action.

## Decision
- **ADD quant.md Q19 — delta as trap-escape** (CONFIRMED_ON_OURS, single-regime): among same-name/direction contracts, prefer enough delta to monetize a *modest* (~5%) move; don't reach for cheap far-OTM lottery tickets. Framed as "enough delta," not a target band. Refines Q5/Q6 (low-delta convexity is the *exception* needing a fast-move thesis; deep-OTM lottery tickets are the named failure mode).
- **Validated** the 2026-06-09 two-label-trap line already added to the base picker goal — the data confirms that exact mechanism.
- **NOT done:** no broad physics tilt (unsupported), no narrative down-weight (no evidence of harm).

## Files
`signal-judge/case_memory/quant.md` (Q19). Deployed with signal-judge (`load_quant_md` ships quant.md in the image). Analysis was read-only; scripts were `/tmp` scratch, not committed.
