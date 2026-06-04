# 2026-06-04 — P&L-simulation realism fixes (slippage / stale-timeout / late-fill)

**Status:** IMPLEMENTED in `forward-paper-trader/main.py`. NOT deployed — pending `gammarips-review` per `.claude/rules/forward-paper-trader.md`. Additive ledger columns; trader mechanics (entry/stop/target/hold/trail/exit-precedence) unchanged.

## The bugs (all bias `realized_return_pct` upward)

**Bug #12 — asymmetric slippage.** Entry was slipped `+2%` (`entry_bar["c"] * 1.02`) but bracket exits filled at the EXACT threshold with NO slippage (`exit_price = target` / `exit_price = effective_stop`). Every TARGET/STOP/TRAIL fill was optimistic by ~2%, and stop fills ignored gap-through (a bar that opens below the stop fills at the stop, not the gap).

**Bug #9 — stale TIMEOUT bar.** The TIMEOUT fallback (`last_in_window_bar`, and the post-loop `exit_price is None` branch) could price a 3-day-hold exit off a print from an EARLIER trading day yet still label it a clean `TIMEOUT`. A contract that stops printing on day-1 would record a day-1 mark as a day-3 timeout — uncuttable from EV because nothing flagged it.

**Bug #13 — late / pre-market fill.** The 10:00 ET entry took the first print at/after 10:00 with no upper bound (could be hours late), and on the pre-10:00 fallback it walked the bracket from `bars.index(entry_bar)+1`, letting pre-entry bars trigger STOP/TARGET before the position existed.

## The fixes

- **Symmetric slippage.** Hardcoded `1.02` replaced with `SLIPPAGE_PCT = 0.02`, applied both sides. `TARGET` → `target * (1 - SLIPPAGE_PCT)`. `STOP`/`TRAIL` → `min(effective_stop, bar_low, bar_open) * (1 - SLIPPAGE_PCT)` (the `min` models gap-through). `TIMEOUT` marks-to-market at the last close with no slippage (exit-at-market over a 1-min bar, not a liquidity-taking bracket order). New nullable column `exit_slippage` records the fraction actually applied (0.0 on TIMEOUT).

- **Stale-TIMEOUT guard.** Both timeout paths check the chosen bar's calendar date against `exit_day`. An earlier-day print gets `exit_reason='STALE_NO_TIMEOUT_PRINT'` and `illiquid_exit=True` instead of a clean `TIMEOUT`.

- **Late/pre-market fill guard.** First at/after-10:00 print accepted only within `LATE_FILL_TOLERANCE_MIN = 30` min; later first print → `illiquid_exit=True`. Pre-10:00 proxy fill → `illiquid_exit=True`. Both stamp signed `late_fill_minutes`. The bracket walk now starts at the first bar with `t >= entry_ts_ms AND t > entry_bar["t"]` so pre-entry bars never trigger exits. The bracket `exit_reason` is preserved; the late/illiquid signal rides in the dedicated columns. `INVALID_LIQUIDITY` (zero-volume / no entry bar) is unchanged.

## Ledger contract

- New nullable columns: `exit_slippage` (FLOAT), `illiquid_exit` (BOOL), `late_fill_minutes` (FLOAT). Auto-created on first write via `schema_update_options=[ALLOW_FIELD_ADDITION]` on the existing ledger load job. No existing column renamed/dropped/retyped.
- New `exit_reason` value `STALE_NO_TIMEOUT_PRINT`. Downstream EV/analysis should exclude rows where `illiquid_exit IS TRUE` or `exit_reason = 'STALE_NO_TIMEOUT_PRINT'`.
- Cohort impact: these change `realized_return_pct` magnitudes for the V5.4 cohort going forward (no backfill of prior rows). Pre-fix rows lack the new columns (NULL).

## Why this is safe

Mechanics constants (`STOP_PCT`, `TARGET_PCT`, `HOLD_DAYS`, trail params, entry/exit times, exit precedence) are untouched. No new trader-side selection gate — these are fill-accounting corrections, not signal gates. Benchmarking layer (`benchmark_context.py`) untouched. Reversible: revert the diff and the columns simply stop populating.

## Follow-ups

- `gammarips-review` audit before deploy (mandatory for this service).
- Confirm any ledger EV/IC queries add the `illiquid_exit` / `STALE_NO_TIMEOUT_PRINT` exclusion.
