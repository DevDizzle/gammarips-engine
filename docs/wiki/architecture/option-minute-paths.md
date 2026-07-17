Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (per-minute premium tape enabling ANY exit-rule scoring)
Source: docs/DECISIONS/2026-07-07-option-minute-paths.md
Date: 2026-07-17

# option_minute_paths — the per-minute premium tape (recover first-crossing order)

`profit_scout.option_minute_paths` persists one row per (contract, entry_day, minute):
per-minute OHLCV premium bars over each enriched-pool candidate's 3-trading-day excursion
window (144,448 bars backfilled, 2,675 contract-days; ~419 legitimately empty — the no-print
illiquid tail). Partitioned by `entry_day`, clustered by `contract`; topped up daily
(`POST /persist_minute_paths` + `option-minute-paths-refresh` scheduler).

Why: the opportunity-surface substrate ([[opportunity-surface-substrate]]) stored only the
MFE/MAE EXTREMES, so when a bracket's target AND stop both crossed inside the window, the
first-crossing order was unrecoverable (`estimate_exit_rule` fell back to a
minutes-to-extreme heuristic on ~10.5% of rows, and trailing rules could not be scored at
all). The minute tape makes any exit rule — including trailing — exactly scoreable off the
same bars the labeler replays. This is engine must-fix #6g / trader-harness GAP-002 / MCP
RM-002.
