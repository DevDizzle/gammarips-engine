# Decision: V3 Retirement and Documentation Archival

**Date:** 2026-04-16
**Status:** Executed

## What

V3 is retired as an active strategy. V4 is now the sole active trading pipeline. All V3-era decision docs and exec plans have been moved to `docs/archive/`. Core documentation (`TRADING-STRATEGY.md`, `CLAUDE.md`, `NEXT_SESSION_PROMPT.md`, `ARCHITECTURE.md`) has been rewritten to reflect V4-only operation.

## Why

1. **V3 starved the pipeline.** 29 trades in 7 weeks. The `premium_score >= 2` gate and `overnight_score >= 6` enrichment floor rejected ~95% of candidate signals for a modest lift in win rate.
2. **premium_score is not a reliable gate.** Research showed score=0 wins 76.3% vs score≥2 at 84% — the gate costs 1,547 trades for an 8pp win-rate improvement. Vol/OI floors are anti-correlated with outcome.
3. **V4 is regime-adaptive by design.** Unfiltered data collection + periodic feature importance re-runs naturally adapts to regime shifts. V3's static gate assumed the same flags matter forever.
4. **V3 already served its purpose as a control.** The 29-trade baseline is preserved in `forward_paper_ledger_v3_hold2`. We don't need the service running to compare against it.
5. **Simplification.** One pipeline is easier to monitor, debug, and reason about than two parallel pipelines.

## What was archived

Moved to `docs/archive/`:
- `2026-03-26-drop-vix-gate.md` — V3-era VIX gate decision
- `2026-04-07-v3-1-liquidity-quality-gate.md` — V3.1 gate rationale
- `2026-04-08-ledger-benchmarking-and-fmp-retirement.md` — V3.1 benchmarking infrastructure (still valid technically, but V3.1-framed)
- `v3-reset.md` — V3 exec plan, completed
- `2026-04-03-xgboost-prompt.md` — V6 Structural Sniper proposal, cancelled

## V3 infrastructure teardown (executed same day)

All V3 infrastructure was fully torn down on 2026-04-16:

**Deleted:**
- Cloud Scheduler jobs: `forward-paper-trader-trigger`, `overnight-enrichment`, `polygon-iv-cache-daily` (V3 versions)
- Cloud Run services: `forward-paper-trader` (V3), `enrichment-trigger` (V3) — overwritten by canonical deploys
- Cloud Run services: `forward-paper-trader-v4`, `enrichment-trigger-v4` — replaced by canonical names
- Cloud Scheduler jobs: `forward-paper-trader-v4-trigger`, `enrichment-trigger-v4-daily`, `polygon-iv-cache-v4-daily`
- BigQuery tables: `forward_paper_ledger_v3_hold2`, `overnight_signals_enriched` (V3 data)
- Code directories: `forward-paper-trader/` (V3), `enrichment-trigger/` (V3)

**Renamed to canonical:**
- `forward-paper-trader-v4/` → `forward-paper-trader/`
- `enrichment-trigger-v4/` → `enrichment-trigger/`
- `overnight_signals_enriched_v4` → `overnight_signals_enriched`
- `forward_paper_ledger_v4_hold2` → `forward_paper_ledger`
- Cloud Run services and scheduler jobs all use canonical names (no `-v4` suffix)

**Preserved:**
- `signals_labeled_v1` — frozen research table, untouched
- `polygon_iv_history` — shared IV cache, still active
