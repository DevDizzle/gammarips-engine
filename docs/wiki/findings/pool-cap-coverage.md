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
the pool. The flip to 25 was PENDING behind the momentum-tilt's clean N≥15 read at the time
of writing; the current effective cap is still 50.
