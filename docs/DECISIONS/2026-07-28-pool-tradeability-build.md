# 2026-07-28 — Pool-tradeability build: liquidity demotion, log-OI contract scoring, published expected_liquidity, standing metric

## Problem

The published pool of 50 is structurally under-tradeable on entry day: 42.8% of
pool rows trade <50 contracts, 22.3% GHOST (<10), 8.9% trade zero — every one of
15 measured days (entry-day tradeability study, `pool_liquidity_snapshot` scans
2026-07-06..07-24, N=750; FINDINGS_LEDGER "2026-07-28 (evening)"). Trigger: owner
real-money kill on UNP 260821C310 (6 contracts all day, ~30% effective spread) +
`gammarips-trader/docs/POOL-LIQUIDITY-FINDING-2026-07-28.txt`. Root causes the
study quantified: (1) the contract picker's OI term `min(oi/200)*5` saturates for
87% of the delivered pool while 16% of maxed contracts are still ghosts (the
2026-06-04 "OI is PRIMARY... can't be faked" rationale is falsified AT THAT
SATURATION POINT — OI still carries rank signal, ghost rate falls monotonically to
~2-4% only at OI 2000-5000); (2) the two strongest tradeability predictors are
NAME-level and unused by the pipeline: underlying share volume (rho +0.585) and
chain active-strikes breadth (+0.554); (3) sweep volume is non-monotonic at the
top (the sweep is the signal, not liquidity).

## Owner call (2026-07-28 evening, "go")

Build the three-layer tradeability change. Explicitly out of scope: the score>=4
floor (stays), the mom_60 tilt (owner keeps), signal-notifier timing (layer-4
decision pending), and forward-paper-trader (untouched).

## What was built (CODE ONLY — gammarips-review + deploy pending)

1. **Layer 1 — name-level liquidity DEMOTION in the enrichment edge-rank**
   (`enrichment-trigger/main.py`). New `_liquidity_flag(sig)` implements the
   scan-time GHOST rule: `day_volume <= 2.5M AND (call_active_strikes +
   put_active_strikes) <= 15 AND recommended_oi <= 1000` (precision 0.60 / recall
   0.59, flags ~22%). `_edge_select_top_n` prepends `not liq_flagged` to the sort
   key: flagged names sort BELOW every unflagged name but are never dropped — a
   thin day can never starve the pool below ENRICH_TOP_N. `get_signal_tickers`
   now also SELECTs `day_volume` (already in the `overnight_signals` schema, was
   just not read). Missing components fail OPEN (never demote on missing data).
   Logs flagged tickers + demoted-out vs still-admitted counts. Env:
   `LIQ_DEMOTION=true` (kill switch → bit-identical prior ordering),
   `LIQ_UND_VOL_MIN=2500000`, `LIQ_STRIKES_MIN=15`, `LIQ_OI_MIN=1000`.
   **Thresholds are 15-day IN-SAMPLE fits — re-fit as `pool_liquidity_snapshot`
   accrues.**
2. **Layer 2 — contract picker scoring fix**
   (`src/enrichment/core/pipelines/overnight_scanner.py::_best_contract`):
   OI term `min(oi/200,1)*5` → `min(log10(oi+1)/log10(3000),1)*5` (log ramp
   saturating ~3000, where ghost rate reaches ~2-4%); sweep-volume weight 2.0 →
   1.0 (non-monotonic at the top); delta sweet-spot bonus band 0.25–0.50 →
   **0.20–0.46** (aligned with the one VALIDATED rank component — the 0.46
   ceiling, FINDINGS_LEDGER 2026-07-28 morning; note the 0.20 floor itself is
   unvalidated, carried for band symmetry with the edge-rank). The `vol >= 10`
   floor stays but is re-commented as a data-sanity floor (no trustworthy mark
   below it), not a liquidity gate. Everything else unchanged.
3. **Layer 3a — published tradeability field**: every `overnight_signals_enriched`
   row now carries `expected_liquidity` ("CLEAN"/"THIN" = the Layer-1 verdict,
   written for ALL rows including demoted-but-admitted fills, independent of the
   `LIQ_DEMOTION` switch) + components `liq_underlying_volume` (INT64),
   `liq_active_strikes` (INT64). Columns ALTER-added in the existing
   `ADD COLUMN IF NOT EXISTS` block; the staged load stays bound to the cloned
   live schema — NEVER autodetect (the 2026-07-02 outage). This is the trader
   doc's R3 field (deliberately NOT the inoperative `is_tradeable`, TF-15).
4. **Layer 3b — standing metric** (trader doc R5): dbt mart
   `dbt/models/marts/agg_pool_tradeability.sql` off the newly-declared source
   `pool_liquidity_snapshot` — per scan_date: pool size, share of recommended
   contracts with entry-day max non-stale `day_volume` <50 and <10 (stale =
   `day_last_updated` date != `as_of` date; entry day = the pool's snapshot day;
   all-stale contracts count as volume 0). Telemetry rollup only — never a
   feature, never joined to selection.

## Acceptance evidence (read-only replay over the study's labeled N=750)

Replaying the Layer-1 rule on `full_labeled.csv`: flags 163/750 (21.7%),
precision 0.59 / recall 0.57 (matches the ledger's rounded 0.60/0.59); per-day
flagged 4–20 (median 11) of 50. Kept-pool (unflagged) ghost rate 22.3% → 12.1%
pooled; under-50 rate 42.8% → 31.5%. Improvement is direction-consistent on all
15/15 days. `py_compile` PASS on both services; `dbt parse` PASS (model + source
+ tests registered).

## What this does NOT do

- No hard drop anywhere: demotion only reorders; the pool stays at 50.
- No execution gate in forward-paper-trader (untouched).
- No claim about PnL — this is a fillability fix (the study's rule is fit on
  tradeability labels, and sim-PnL on ghosts is untrustworthy — stale marks).
- Layer-2 effects on which CONTRACT is picked per name are unmeasured forward —
  the log-OI ramp changes relative scoring for OI in (200, 3000).

## Revert

`LIQ_DEMOTION=false` restores the exact prior edge-rank ordering. Layer 2 and the
published columns revert by git revert + redeploy (columns are additive/NULLABLE;
consumers must treat `expected_liquidity` as nullable for historical rows).
