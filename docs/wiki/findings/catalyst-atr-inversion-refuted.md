Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: 3-day opp_peak_return ≥ +20% label off the 10:00 ET anchor (research label, not the live exit)
Source: FINDINGS_LEDGER §2026-08-05 (trader-handoff adjudication)
Date: 2026-08-05

# The catalyst/ATR "inversions" are a between-day tape artifact

A trader handoff on 5 entry days claimed `catalyst_score` (AUC 0.346) and
`atr_normalized_move` (0.362) INVERT, meaning high values predict failure. Replicated at
full history (N=3,040, 74 days) the inversion dissolves: catalyst_score day-demeaned AUC
is **0.499**, and both features whose pooled CIs excluded 0.50 go NULL once each day's
pool mean is removed. The trader's measurements were accurate; the window was
unrepresentative (three simultaneous "inversions" were correlated day effects on 5
shared-tape days).

What is real is day-level composition: high-catalyst-heavy pool days are lower-base-rate
days (Spearman −0.381, p=0.001, 74 days). That is regime correlation, telemetry to
accrue, not per-contract information. The IV-crush mechanism was tested and NOT
supported.

**Do not down-rank high-catalyst or high-ATR contracts within a day's pool, and do not
re-fit the ranker from this evidence.** Same lesson class as
[[contract-score-lead-dead]]: era and window slices on this pool die out of sample.
