Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md
Date: 2026-07-17

# The trader simulates ONLY todays_pick — one ledger row per day

`forward-paper-trader` simulates ONLY the ticker named in `todays_pick/{scan_date}`, writing
**at most one row per scan_date** (one trade row OR one skip row). This replaced an implicit
"trader writes a research fanout over every enriched row" pattern that had survived from V5.3
and was mislabeling ~70 enriched rows/day with the pick's `policy_version`.

This is the load-bearing invariant behind clean cohort stats and the whole selection→one-pick
model ([[bracket-tournament-selection]]). (The same 2026-05-12 decision also relaxed OI/vol/DTE
gates to un-starve the V5.4 picker — those gates were later removed entirely,
[[selection-gates-removed]]; the one-row-per-day rule is the durable part.) The full-pool
counterfactual now lives in the research substrate ([[opportunity-surface-substrate]]), not
the ledger.
