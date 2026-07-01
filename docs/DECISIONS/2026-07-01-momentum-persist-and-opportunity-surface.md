# 2026-07-01 — Persist mom_60 + opportunity-surface (MFE/MAE) + 3-day research label

Substrate-readiness audit must-fix **#5** (persist `mom_60`) and **#6**
(opportunity surface / exit-freedom) — `.scratch/substrate_readiness_audit_2026-07-01.md`,
Phase 2 ("the finding + exit-freedom"). **Working-tree change only — NOT deployed,
no BQ write / cache-build / backfill run.** The whole bundle must pass
`gammarips-review` before any deploy; the cache/backfill scripts additionally need
review **and** owner OK before running.

## Scope / guardrails
Research substrate ONLY. **No execution-policy change** — the live same-day GIGO
trader is unchanged, so `docs/TRADING-STRATEGY.md` is intentionally NOT modified.
The 3-day arm is a RESEARCH LABEL, never a trade. Untouched: `_write_ledger_records`,
`forward_paper_ledger`, Firestore `todays_pick`, the live pick path, and the
existing same-day `_simulate_contract` MECHANICS (see "byte-identical" below).

Files:
- `enrichment-trigger/main.py` — persist `mom_60` (+ audit dates) at enrichment.
- `forward-paper-trader/main.py` — parametrize `_simulate_contract` (defaults =
  live constants → byte-identical), add `_simulate_opportunity_surface` +
  `_multi_day_window_closed`, wire mom + opportunity-surface + 3-day arm + label
  tags into `_write_enriched_outcomes` (+ schema-aware mom SELECT).
- `scripts/ledger_and_tracking/create_enriched_option_outcomes.py` — schema +
  docstring for the new column groups.
- `scripts/ledger_and_tracking/create_underlying_daily_bars.py` — NEW, gated DDL.
- `scripts/ledger_and_tracking/load_underlying_daily_bars.py` — NEW, gated loader.
- `scripts/ledger_and_tracking/backfill_mom_60.py` — NEW, gated backfill.
- `scripts/ledger_and_tracking/backfill_opportunity_surface.py` — NEW, gated backfill.

## Must-fix #5 — mom_60 as a point-in-time BQ column
mom_60 was computed transiently in enrichment (`_compute_momentum_map`, leakage-
guarded by `_resolve_momentum_dates`: anchor + lookback both ≤ scan_date) but
written NOWHERE; the only recompute path was a gitignored/stale local parquet — a
leak trap, and the flagship finding was not reproducible from BQ.

- **(a) Persist at enrichment.** `write_enriched_signals` now writes `mom_60`,
  `mom_anchor_date`, `mom_lookback_date`, `mom_lookback_days` onto
  `overnight_signals_enriched` via a thin `_get_momentum_context` accessor that
  **reuses** `_compute_momentum_map`/`_resolve_momentum_dates` (no re-implemented
  math). Persistence is **independent of `MOMENTUM_TILT`** (the ranking kill-switch)
  and gated by a new `PERSIST_MOM_60` env flag (default true); it's a cache hit when
  the tilt already ran, otherwise ≤2 grouped-daily calls. Fail-soft → NULL columns.
  Columns are pre-created via the existing V5.2 `ALTER … ADD COLUMN IF NOT EXISTS`
  block (correct DATE/INT64 typing before the atomic staged load).
- **(b) Flow into the label substrate.** The labeler `pool_sql` selects the mom
  columns **schema-aware** (`NULL AS <col>` when absent, so it never 500s on deploy
  ordering / old rows) and `_write_enriched_outcomes` emits them in the FEATURES
  group; `create_enriched_option_outcomes.py` schema adds them.
- **(c) Scheduled bar cache (gated, unexecuted).** `underlying_daily_bars`
  (create + loader) is the canonical ADJUSTED underlying daily series, sourced from
  the SAME Polygon grouped-daily ADJUSTED endpoint the live tilt uses — reproducible
  from infra, replacing the stale local parquet.
- **(d) mom backfill (gated, unexecuted).** `backfill_mom_60.py` derives mom_60 for
  existing rows from the bar cache, leakage-safe (anchor = latest cache session
  ≤ scan_date; lookback = the LB-th session before it; every bar ≤ scan_date).

Deferred (nice-to-have): `mom_20` / `mom_120`. They share the anchor grouped-daily
and need only 2 extra lookback fetches, but adding a second lookback-resolution path
risks the leakage guard; deferred to keep the diff surgical. mom_60 (the headline
lever) ships now.

## Must-fix #6 — opportunity surface + exit-freedom
The substrate carried ONLY the same-day GIGO bracket, but the finding is a 3-day
hold and profitability depends on HOW a contract is traded. Owner's principle
(`project_surface_contracts_discretionary_exit`): the engine SURFACES good
contracts; capture the OPPORTUNITY so exit is a **free variable**, do NOT hard-code
an exit as product truth.

- **(e) Opportunity surface (MFE/MAE).** `_simulate_opportunity_surface` records,
  over `[entry_day .. entry_day+(OPP_WINDOW_DAYS-1) td]` (default 3) with **NO exit
  rule**: `opp_peak_return` (max favorable excursion = profit potential),
  `opp_trough_return` (max adverse excursion), `opp_minutes_to_peak/trough`,
  `opp_bar_count`, `opp_status`, `opp_entry_price/timestamp`. Entry cost basis
  mirrors the live 10:00 fill (`close × (1+SLIPPAGE_PCT)`); **no exit slippage** is
  applied — the raw achievable path, so any exit (and its costs) is derivable
  offline. Reuses `build_polygon_ticker` + `fetch_minute_bars`.
- **(e) Interim 3-day bracket label.** A parallel `-60%/+80%/HOLD=3` bracket via
  `_simulate_contract(..., hold_days=3, stop_pct=0.60, target_pct=0.80,
  exit_hhmm="15:50", use_trail=False, fetch_benchmarks=False)` →
  `realized_return_pct_3d` / `exit_reason_3d` / `exit_day_3d` / `exit_timestamp_3d`
  / `entry_price_3d` / `peak_premium_3d`. This is the horizon the mom_60 finding
  lives on.
- **(f) Label-semantics tags.** Per row: `label_sim_version` + `label_hold_days` /
  `label_stop_pct` / `label_target_pct` (same-day) and `label_3d_*` (3-day). Do NOT
  infer horizon from the hardcoded `policy_version`.
- **(g) Full per-bar PATH companion table — DEFERRED (designed, not built).** The
  MFE/MAE summary is the 80/20 shipped now. The eventual heavier target: a companion
  table keyed on `(entry_day, ticker, recommended_contract)` with the full minute
  bar path so ANY exit is re-derivable — either **one row per bar**
  (`ts, o, h, l, c, v`, partitioned by `entry_day`, clustered by ticker; largest,
  most flexible) or **one row per contract with a nested `bars` ARRAY<STRUCT<…>>**
  (fewer rows, atomic per contract). At ~50 contracts/day × ~390 min/day × N days
  the row-per-bar variant is ~10⁵ rows/day — feasible but a separate safe pass, not
  a single collector loop. Build after the MFE/MAE surface proves the demand.

### Byte-identical live path (the key safety property)
`_simulate_contract` gained keyword-only overrides
(`hold_days`/`stop_pct`/`target_pct`/`exit_hhmm`/`use_trail`/`trail_*`/
`fetch_benchmarks`) whose **defaults are the live V7.1 module constants**. Every
existing call site (the live ledger path and the same-day research label) passes
none → identical results. **No new keys are added to the returned `record`**, so the
`forward_paper_ledger` schema is untouched (avoids the schema-drift landmine on
`_write_ledger_records`). Only the research `_write_enriched_outcomes` out-dict grows.

### Timing (window closure)
The opportunity-surface + 3-day arms require a CLOSED multi-day window (no partial
bar as a false peak/timeout). The daily 17:00-ET label cron labels a fresh scan_date
whose window is still OPEN → those columns write NULL (`opp_status='WINDOW_OPEN'`,
3-day NULL); the same-day label is unaffected. They are filled by
`backfill_opportunity_surface.py` (gated) or a future **lagged N-day re-label cron**
(deferred wiring). The daily cron therefore incurs **no extra Polygon calls** (the
guard short-circuits before any fetch).

## Column groups added (agent-safety tagging)
- **FEATURES (point-in-time, safe as model inputs):** `mom_60`, `mom_anchor_date`,
  `mom_lookback_date`, `mom_lookback_days`.
- **OPPORTUNITY SURFACE (NOT a label; profit potential — exit is free):**
  `opp_window_days`, `opp_status`, `opp_entry_timestamp`, `opp_entry_price`,
  `opp_peak_return`, `opp_trough_return`, `opp_minutes_to_peak`,
  `opp_minutes_to_trough`, `opp_bar_count`, `opp_sim_version`.
- **3-DAY LABEL (own horizon; never mix with same-day):**
  `realized_return_pct_3d`, `exit_reason_3d`, `exit_day_3d`, `exit_timestamp_3d`,
  `entry_price_3d`, `peak_premium_3d`.
- **TELEMETRY (label semantics):** `label_sim_version`, `label_hold_days`,
  `label_stop_pct`, `label_target_pct`, `label_3d_sim_version`, `label_3d_hold_days`,
  `label_3d_stop_pct`, `label_3d_target_pct`.

## Kill switches / knobs
`PERSIST_MOM_60` (enrichment), `OPP_SURFACE` / `OPP_WINDOW_DAYS` / `OPP_EXIT_HHMM`
and `LABEL_3D` / `LABEL_3D_HOLD_DAYS` / `LABEL_3D_STOP_PCT` / `LABEL_3D_TARGET_PCT`
/ `LABEL_3D_EXIT_HHMM` (collector). All default to the values above; setting the
enable flags false restores the prior behavior exactly.

## Testing
`py_compile` clean on all edited + new files. Read-only `bq --dry_run` validated the
labeler `pool_sql` (pre-deploy `NULL AS mom_*` form) against the live schema. No BQ
write / cache-build / backfill was run (mandate). The gated scripts' live dry-runs
require their prerequisite tables (bar cache; the new opp/3d columns) and are
deferred to run-time under review + owner OK.

## Deploy ordering (for the reviewer / owner)
1. Deploy `enrichment-trigger` first (adds the mom columns + starts persisting).
2. Deploy `forward-paper-trader` (labeler picks up mom schema-aware either way).
3. The new columns are created EXPLICITLY (typed) by
   `_ensure_enriched_outcomes_columns` on both write paths — see the "Review round 2"
   section below. Re-running `create_enriched_option_outcomes.py` is still optional
   (idempotent) and remains the authoritative schema file, but is NOT the mechanism
   the collector relies on.
4. Cache + backfills (`create_/load_underlying_daily_bars.py`, `backfill_mom_60.py`,
   `backfill_opportunity_surface.py`) — gated, run only after review + owner OK.

## Review round 2 (2026-07-01) — explicit schema creation + realism fixes
`gammarips-review` cleared the leakage + live-path safety but flagged two FIX-FIRST
write-path data-integrity blockers (the schema-drift landmine class) plus four
minors. All fixed working-tree-only; live pick / `forward_paper_ledger` /
`_simulate_contract` mechanics / Firestore `todays_pick` untouched.

- **BLOCKER A — `enriched_option_outcomes` columns never created with EXPLICIT types.**
  The prior plan assumed the atomic staged-write's autodetect would ALTER-add the new
  columns. It cannot: the whole opp/3d group is all-NULL until a window closes, and
  `mom_60` is all-NULL for names without a persisted momentum — an all-NULL JSON
  column gives autodetect no type, so the column is dropped or (on a mixed batch)
  created as STRING that 500s on the next FLOAT/DATE write. **Confirmed live:** all
  28 columns were ABSENT from the 63-column live table at review time. Fix: a single
  shared `ENRICHED_OUTCOMES_RESEARCH_COLUMNS` (col→GoogleSQL-type) list +
  `_ensure_enriched_outcomes_columns()` helper in `forward-paper-trader/main.py` runs
  `ALTER TABLE … ADD COLUMN IF NOT EXISTS <col> <TYPE>` (mirroring the
  `enrichment-trigger` V5.2 pattern) ONCE before every write in
  `_write_enriched_outcomes`, covering the must-fix #5 momentum + #6 opp/3d/
  label-semantics groups. Names/types are reconciled to
  `create_enriched_option_outcomes.py` (the source of truth).
- **BLOCKER B — backfill MERGE referenced columns it never guaranteed exist.**
  `backfill_opportunity_surface.py::_merge` now calls the SAME shared helper
  (`fpt._ensure_enriched_outcomes_columns(client, TABLE)`) before `CREATE TABLE …
  LIKE` + MERGE, so a first `--confirm` run can't 500 with "Unrecognized name".
- **Type reconciliation.** The must-fix spec tentatively typed
  `opp_minutes_to_peak` / `opp_minutes_to_trough` as INT64, but both the schema
  script and the `_simulate_opportunity_surface` output (`float(… / 60000.0)`) are
  FLOAT — kept **FLOAT64** (schema is authoritative).
- **Minor 1 — window-closed guard.** `_multi_day_window_closed` now requires the
  window end STRICTLY `< today_et` (was `<=`), so an INTRADAY backfill on the exact
  last window day can't read a partial final session as a false MFE/MAE peak or
  3-day timeout. One-day-lag by design (the daily cron writes `WINDOW_OPEN`; the
  backfill fills next trading day). The live same-day path uses its own post-close
  guard and is unaffected.
- **Minor 2 — opp walk anchor.** `_simulate_opportunity_surface` now excludes bars
  before the 10:00 ET `entry_ts_ms` (mirroring `_simulate_contract`'s anchor), so a
  pre-10:00 proxy fill can't let pre-entry bars enter MFE/MAE or drive
  `opp_minutes_to_peak/trough` negative. Post-scan realism (not leakage — window
  already closed); no change when the entry bar is at/after 10:00.
- **Minor 3 — backfill ticker casing.** `_compute` writes `row["ticker"]` as stored
  (no `.upper()`) so the case-sensitive `MERGE ON T.ticker=S.ticker` matches the
  collector's un-uppercased value.
- **Minor 4 — soft-skip documented.** Rows with NULL `recommended_dte/volume/oi` get
  no 3-day label (reused `_simulate_contract` int()-casts them; caller swallows the
  TypeError) but STILL get an opportunity surface — expected attrition, not a hole.

**Validated:** `py_compile` clean; `bq --dry_run` on the ALTER (statementType
ALTER_TABLE, DONE) and the MERGE skeleton (statementType MERGE, DONE). The full
MERGE dry-run intentionally errored "Unrecognized name: opp_window_days" pre-ALTER —
the exact Blocker B premise the fix removes. Returns to `gammarips-review`.
