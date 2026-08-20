Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: ceiling/best-name-capture test on the option-PnL pool; NOT an LLM-pick-quality test
Source: docs/DECISIONS/2026-06-19-pool-cap-coverage.md; INTELLIGENCE_BRIEF 2026-06-19
Date: 2026-07-17

# Tournament pool can shrink 50→25 with no demonstrated loss of the winner

Best-name capture by cap size: N=10 → 56%, N=20 → 89%, N=25 → 93.5%; the ceiling-EV
shortfall CI touches zero only at ≥25. N=10 drops the eventual winner on 43% of days; a cap
of 50 almost never binds (>50 candidates on only 4/46 days). So the [[tourney-pool-cap-edge-rank]]
can safely shrink **50→25**, roughly halving grounded-enrichment + tournament LLM cost.

This is a ceiling test (does the winner survive the cap), NOT a test of pick quality inside
the pool. The effective cap at enrichment remains 50 (`ENRICH_TOP_N=50`). The old gating
condition (the momentum-tilt's clean N≥15 read) is obsolete: the tilt question settled by
owner override on 2026-07-28 ([[momentum-60d-enrichment-tilt]]). The 2026-08-19 cap-20
admission-floor proposal was reviewed and NOT adopted (superseded the same day by the
notifier print-floor raise; see the status header of
docs/DECISIONS/2026-08-19-pool-liquidity-floor-and-cap-20.md). The ceiling evidence in
this note still stands.
