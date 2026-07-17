Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: hold-to-expiration (ITM at expiry); N=2,146 per-signal / 1,896 unique expired
Source: INTELLIGENCE_BRIEF 2026-07-06 (ITM-vs-delta retro); FINDINGS_LEDGER §2026-07-06
Date: 2026-07-17

# The pool is DELTA-CALIBRATED — no directional edge at expiration

Pre-committed H1 ("the scanner finds direction the market underprices") was **REJECTED**.
On every expired `enriched_option_outcomes` contract (N=2,146; all BULLISH calls; scans
04-10→06-30), realized **ITM 41.3% vs mean scan-time δ 42.1%** (Wilson [39.2,43.4]); cleaned
of a 41-row δ≈0 data bug it is 40.9% vs 42.9%. Per-bucket calibration is near-perfect
(0.2–0.46 band: ITM 35.2% vs δ .365). Since δ=N(d1) overstates P(ITM)=N(d2) by ~3–5pp, the
honest read is **exactly zero directional edge, not negative** — and this in a violently
bullish Apr–Jun tape that should have flattered a long-call pool.

Implication: the scanner surfaces **fairly-priced** contracts. ALL realized ROI lives in
selection-within-pool + entry/exit craft ([[fixed-exit-composites-negative]],
[[path-calibrated-giveback]]). Follow-up: re-run the post-06-12 top-50 era ~mid-Aug when
≥200 era rows have expired (currently only structurally-biased short-DTE rows).
