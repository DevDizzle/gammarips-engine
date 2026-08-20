Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (public-stats display convention)
Source: docs/DECISIONS/2026-05-19-cohort-start-and-position-sizing.md
Date: 2026-07-17

# Public ROI uses fixed-dollar position sizing at the display layer

Public `cohort_stats` ROI is computed with **fixed-dollar position sizing**
(`POSITION_SIZE_USD = 500.0`/trade), applied in-SQL at the DISPLAY layer inside
`compute_and_write_cohort_stats` — the ledger keeps recording per-contract premium and
percent return; sizing is not baked into the ledger and there is no schema change. This
replaced an implicit "1 contract per trade" assumption that let a single expensive contract
dominate invested-capital math.

Both this and `LIVE_COHORT_START_DATE` live as constants in `signal-notifier/main.py` (the
cohort-start value is era-specific and has been reset several times — the live value
lives in `signal-notifier/main.py` (2026-08-21 as of the 2026-08-20 reset), see
[[v7-1-tilted-gigo-live-policy]]). The durable convention is the
display-layer fixed-dollar sizing, not the specific 2026-05 dates in the source decision.
