# 2026-09-28: Retire the tournament, the paper cohort and eval

**Status:** DECIDED. Owner call 2026-09-28. Infra change done the same day
(commit `c864458`). Do not re-open unless the owner asks.

## Decision

The engine no longer selects a daily pick, paper-trades it, or evaluates LLM
output. The V7.1 "Tilted GIGO" policy is retired. No engine execution policy
is live after 2026-09-28.

The engine continues as a data pipeline. It feeds the `gammarips-mcp` product
and the live VM trader in `gammarips-trader`. The trader chooses its own
contracts and exits under that repo's `docs/RULES.md`.

## Why

- The owner does not use the tournament pick and does not need eval.
- The VM trader never reads the pick. Its only load-bearing engine input is
  `get_pool(view="enriched")` at 10:00 ET. Its soft inputs are
  `enriched_option_outcomes`, `option_minute_paths` and
  `pool_liquidity_snapshot`. It does not read `todays_pick`, `cohort_stats`,
  `forward_paper_ledger` or an eval table.
- No webapp page and no live MCP tool reads the pick or the cohort stats. The
  webapp readers (`getTodaysPick`, `getCohortStats`, `getLedgerTrades`) are dead
  code.
- The saving is small: about $7 per month (signal-judge Vertex Pro about $4.8,
  gammarips-eval about $2.1). The large cost item was the MCP server, fixed
  separately on the same day (gammarips-mcp `53498d3`, GET /mcp returns 405).

## What changed

Paused Cloud Scheduler jobs. The services stay deployed and scale to zero.

| Job | Target | What it did |
|---|---|---|
| `signal-notifier-job` (09:52 ET) | signal-notifier `/` | Rails, liquidity floor, tournament, `todays_pick`, `cohort_stats`, `ledger_trades`, the operator pick email |
| `forward-paper-trader-trigger` (16:30 ET) | forward-paper-trader `/` | Paper trade of the pick into `forward_paper_ledger`, plus the two research shadows |
| `forward-paper-trader-mtm` (16:15 ET) | forward-paper-trader `/mark_to_market` | `forward_paper_ledger_intraday` |
| `gammarips-eval-daily` (07:00 ET) | gammarips-eval `/eval/batch` | LLM-as-judge over `llm_traces_v1` |
| `gammarips-eval-weekly` (Mon 08:00 ET) | gammarips-eval `/eval/report` | Weekly eval report |

Monitoring, in the same change:
- dbt source freshness removed on `forward_paper_ledger`,
  `forward_paper_ledger_intraday`, `paper_shadow_topscore`,
  `paper_shadow_intraday` and `llm_eval_results_v1`. Without this, `/freshness`
  returns 500 about five days after the last write and pages every morning.
- The `ledger` and `shadow` rows are removed from the digest coverage grid.
- dbt-runner deployed as rev `00012-n7b`. `/freshness` returned green on the
  nine remaining sources.

## What did not change

These jobs stay ENABLED because they produce the trader's and the MCP's data:
`overnight-scanner-trigger`, `enrichment-trigger-daily`,
`overnight-report-generator-trigger`, `pool-liquidity-refresh` (a signal-notifier
route that is independent of the pick path), `forward-paper-trader-label-pool`,
`label-life-surface`, `option-minute-paths-refresh`, `load-underlying-bars`,
`fill-closed-windows`, `polygon-iv-cache-daily`, `pool-outcomes-refresh`,
`track-signal-performance`, `backfill-signal-performance`, and the dbt jobs.

The daily report continues. It is the SEO asset and the source of the MCP
`get_daily_report` tool.

## Effects to know

- No pick email arrives at 09:52 ET.
- `todays_pick`, `cohort_stats/current`, `ledger_trades` and
  `forward_paper_ledger` are static history from 2026-09-28. The MCP
  `positions` and `performance` views read `forward_paper_ledger`, so they now
  serve that history.
- `enriched_option_outcomes.was_tournament_pick` is FALSE for new rows. The
  labeler reads the pick on a best-effort basis.
- `LIVE_COHORT_START_DATE` and the V7.1 cohort labels have no live reader.
- The signal-judge timeout fix (`67ee8d0`) is committed but not deployed. It
  does not need a deploy.

## Rollback

Resume the five jobs, then put the five freshness blocks and the two digest
rows back and redeploy dbt-runner. The services, code and tables are unchanged.
