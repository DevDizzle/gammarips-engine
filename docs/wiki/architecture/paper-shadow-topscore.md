Status: active
Type: architecture
Tag: architecture-fact
Exit-context: identical mechanics to the live pick of its era (was V6 3-day; now GIGO same-day)
Source: docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md
Date: 2026-07-17

# paper_shadow_topscore — walled-off research baseline (tournament vs dumbest selector)

`paper_shadow_topscore` is a passive, completely-isolated research baseline that answers one
question: does the no-gate tournament actually beat the dumbest selector — "just trade the
single highest `overnight_score` in the enriched pool"? Each day with a pick, the trader also
simulates the deterministic top-score row through the IDENTICAL `_simulate_contract`
mechanics and writes two arms (`TOURNAMENT`, `TOP_SCORE`).

Motivation: blindly trading the top `overnight_score` returned **−6.09% mean / 33% win**
across 33 labeled scan-dates — WORSE than random (full-pool ≈ −1.36%). This is the
**score-inversion effect** (overnight_score EV inverts at the high end — exactly why the
enrichment floor is a floor at ≥4, not a ceiling, [[enrichment-definition]]).

HARD isolation: writes ONLY to `paper_shadow_topscore`, never `forward_paper_ledger` /
Firestore / any webapp surface; the live write happens first and its result is returned
unchanged; the shadow is best-effort try/except-wrapped twice. **NEVER surface it to the
Scorecard or website.** (The sibling `paper_shadow_intraday` 3-day-vs-intraday experiment was
retired by V7, [[v7-gigo-same-day-exit]].)
