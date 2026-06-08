# 2026-06-08 — Deterministic top-score vs Tournament SHADOW tracker (research-only, NOT deployed)

**Status:** CODE + TABLE + SCRIPTS LANDED, **NOT DEPLOYED.** A separate `gammarips-review` pass and the owner's explicit go gate the deploy. Live execution is **unchanged** — this is a passive, completely-isolated research baseline. `docs/TRADING-STRATEGY.md` is intentionally untouched.

## Motivation

We need a free, forward, retrospective baseline answering one question: **does the gutted no-gate V6 Tournament actually beat the dumbest possible selector** — "just trade the single highest `overnight_score` signal in the enriched pool"?

A labeled-scan retrospective made this worth tracking, not assuming: blindly trading the top `overnight_score` returned **-6.09% mean option PnL / 33% win** across 33 labeled scan-dates — *worse* than picking at random (full-pool mean ≈ -1.36%). That is the **score-inversion effect** (`overnight_score` EV inverts at the high end; see `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md` §B, which is exactly why the enrichment floor is a floor at `>=4`, **not** a ceiling). The Tournament is supposed to be the thing that discriminates *within* that broad pool. This shadow measures, forward and on the live V6 pipeline, whether it does.

## What it does

Every day the live Tournament produces a pick (HAS_PICK), in the **same** exit-cron invocation that writes the live ledger row, the trader also:

1. Pulls the FULL enriched pool for that `scan_date` (tradeable contracts only).
2. Picks the deterministic top-score row: max `overnight_score`, tie-break by `GREATEST(call_dollar_volume, put_dollar_volume)` desc (explicit, stable `mergesort` ordering).
3. Simulates it through the **identical** mechanics (`_simulate_contract`) the live pick uses — same 10:00 ET entry, -60% stop / +80% target / 25%-off-peak trail, 3-day hold, symmetric 2% slippage, STOP/TRAIL > TARGET precedence, illiquid/stale tagging, benchmarking.
4. Writes **two rows** (`arm='TOURNAMENT'`, `arm='TOP_SCORE'`) to `profitscout-fida8.profit_scout.paper_shadow_topscore`, with realized PnL already resolved (the trade closes in arrears, so the row is complete on write).

## Hard isolation guarantees

- Writes **ONLY** to `paper_shadow_topscore`. Never `forward_paper_ledger`, never `forward_paper_ledger_intraday`, never Firestore `todays_pick` / `signal_performance`, never any webapp/blog surface.
- The live ledger write happens **first** and its result is returned **unchanged**; the shadow runs after, best-effort.
- The shadow writer body is wrapped in `try/except → log+return` internally, AND the call site wraps it again (belt-and-suspenders). It can **never** raise into, block, or alter the live return.
- `_write_shadow_records` is hardcoded to `SHADOW_TABLE` and deliberately does **not** reuse `_write_ledger_records` (which targets `LEDGER_TABLE`), so there is no code path by which the live ledger can be touched here.
- The live `record` produced by `_simulate_contract` is **byte-identical** to the pre-extraction inline path — the refactor was a pure mechanical extraction (no change to slippage, bracket precedence, tags, or benchmarking). `current_ledger_stats.py` and the Scorecard see no new rows and no changed rows.

## The refactor

The per-ticker simulation body that lived inline in `run_forward_paper_trading`'s HAS_PICK happy path was extracted verbatim into `_simulate_contract(client, row, entry_day, exit_day, vix_level, spy_trend, vix_5d_delta, pick_doc) -> record`. `pick_doc` is read only for the `policy_gate` tag; shadow callers pass `pick_doc=None`, which falls back to the service `POLICY_GATE` constant (and yields `confidence=NULL` for the top-score arm). Both arms therefore run the exact same code.

## v1 limitation — PAIRED-ONLY

v1 runs the shadow **only on HAS_PICK days**, called from the happy path after the live write. On skip / regime-fail / no-candidate / fetch-failed days the shadow does **not** run (there is no tournament arm to pair against, and no live simulation happened). This means the shadow N is a subset of all scan-dates. A future v2 could simulate a top-score arm on non-pick days too (an unpaired "would the naive baseline have traded when we sat out?" view), but that is explicitly out of scope here.

## Table

`profitscout-fida8.profit_scout.paper_shadow_topscore`, partitioned by `entry_day`, long format (2 rows/day). DDL: `scripts/ledger_and_tracking/create_paper_shadow_topscore.py` (CREATE TABLE IF NOT EXISTS; already run once, table created empty). Schema: `scan_date, entry_day, exit_day, arm, ticker, direction, recommended_contract, overnight_score, confidence (tournament only), regime_ok (VIX<=VIX3M when pick_doc carries the fields, else NULL — no new fetch added), pool_size, same_pick, entry_price, exit_price, exit_reason, realized_return_pct, illiquid_exit, late_fill_minutes, exit_slippage, policy_version, created_at`.

## Reading it

`scripts/ledger_and_tracking/shadow_topscore_compare.py` — strictly read-only. Pivots the arms by `entry_day` over CLOSED rows (`realized_return_pct NOT NULL`, `exit_reason NOT IN ('INVALID_LIQUIDITY','SKIPPED')`): paired N, per-arm mean/median/win%, %same_pick, mean T−S spread on paired days, and a clean-EV view excluding any day with `illiquid_exit=True` on either arm.

## Decision threshold

**DO NOT act on this comparison until N >= 15 paired closes.** Below that, the spread is noise. At N>=15 the result feeds a `gammarips-review` discussion, not an automatic change — if the Tournament fails to beat the naive top-score baseline, that is a signal about V6 selection quality, evaluated then, not now.
