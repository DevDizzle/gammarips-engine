-- signals_labeled_v1.sql
--
-- Frozen, deterministic feature-discovery dataset.
--
-- One row per (ticker, scan_date) signal in overnight_signals_enriched whose
-- recommended contract is non-null. Every row carries every column from the
-- source enrichment table plus the realized outcome of a fixed simulator that
-- mirrors forward-paper-trader/main.py exactly:
--
--   entry_day      = first trading day after scan_date (the day the signal is
--                    surfaced to the user)
--   entry_bar      = first Polygon minute bar at-or-after 15:00 ET on entry_day
--                    (fall back to last bar before 15:00 if none)
--   base_entry     = entry_bar.close * 1.02   (+2% slippage)
--   target         = base_entry * 1.40
--   stop           = base_entry * 0.75
--   timeout_day    = entry_day + 2 trading days
--   force_exit_at  = 15:59 ET on timeout_day (kept at 15:59 for parity with the
--                    live ledger; user noted 15:50 as the operational target,
--                    deferred to a separate decision)
--
-- This table is the single source of truth for all downstream feature-discovery
-- analyses. It is built once by scripts/research/build_labeled_signals_v1.py
-- and re-built deterministically (idempotent DELETE-then-load) on every rerun.
-- Do NOT join the live ledger into this table. Do NOT mutate this table from
-- ad-hoc queries.

CREATE TABLE IF NOT EXISTS `profitscout-fida8.profit_scout.signals_labeled_v1`
LIKE `profitscout-fida8.profit_scout.overnight_signals_enriched`;

-- Outcome columns added by the simulator. ADD COLUMN IF NOT EXISTS is idempotent
-- so this whole script can be re-run safely.
ALTER TABLE `profitscout-fida8.profit_scout.signals_labeled_v1`
  ADD COLUMN IF NOT EXISTS entry_day           DATE,
  ADD COLUMN IF NOT EXISTS timeout_day         DATE,
  ADD COLUMN IF NOT EXISTS entry_timestamp     TIMESTAMP,
  ADD COLUMN IF NOT EXISTS entry_price         FLOAT64,
  ADD COLUMN IF NOT EXISTS target_price        FLOAT64,
  ADD COLUMN IF NOT EXISTS stop_price          FLOAT64,
  ADD COLUMN IF NOT EXISTS exit_timestamp      TIMESTAMP,
  ADD COLUMN IF NOT EXISTS exit_price          FLOAT64,
  ADD COLUMN IF NOT EXISTS exit_reason         STRING,
  ADD COLUMN IF NOT EXISTS realized_return_pct FLOAT64,
  ADD COLUMN IF NOT EXISTS bars_to_exit        INT64,
  ADD COLUMN IF NOT EXISTS simulator_version   STRING,
  ADD COLUMN IF NOT EXISTS labeled_at          TIMESTAMP;
