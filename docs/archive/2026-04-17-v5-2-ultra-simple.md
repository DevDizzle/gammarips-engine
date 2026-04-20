# Decision: V5.2 Ultra Simple — One Strategy, One Position, One Rule Set

**Date:** 2026-04-17
**Author:** eparra
**Status:** Implemented (not yet deployed; awaiting `gammarips-review` audit)
**Supersedes:** `2026-04-12-v4-fresh-start.md` (V4 retired), any in-flight V5/V5.1 complex-exit drafts

## Context

Two inputs converged:

1. **Cohort backtest of the V4 bracket** (`+40% / -25%` on enriched signals) showed an expected value of **-4.26% per trade** on the historical slice. The -25% stop fires on IV-crush noise; the +40% target caps winners that would otherwise run through day 3. The mechanical shape of the bracket was the primary drag, not the signal quality.

2. **Deep Research pass** delivered five actionable findings, all pointing the same direction:
   - Widen the stop to let the thesis play out; IV crush eats -20% alone.
   - Drop the target; time-based exits outperform targets on 3-5 day holds for unusual options flow.
   - Layer a **V/OI at focal strike > 2** quality filter — fresh flow vs stale OI.
   - Constrain **moneyness to 5-15% OTM** — the delta sweet spot for whale-following.
   - Add a **VIX <= VIX3M regime gate** at the notifier layer; long premium in backwardated vol term structures is a coin flip at best.

Modeled EV post-upgrade: **+1.8% to +3.2% per trade**.

The prior V4 "no trader gate" posture has preserved the forward research dataset for 5 days and 70 rows — enough to validate the mechanics, not enough to justify keeping a bracket that models at -4% EV. We cut.

## Decision

Collapse to a single live strategy — **V5.2 Ultra Simple** — with the fewest possible moving parts:

### Execution (`forward-paper-trader`)
- **Entry:** 10:00 ET on day-1 (first trading day after `scan_date`)
- **Stop:** -60% on option premium
- **Target:** none
- **Hold:** 3 trading days
- **Exit:** 15:50 ET on day-3 at market, or earlier if stop fires
- **Policy labels:** `policy_version = V5_2_ULTRA_SIMPLE`, `policy_gate = ENRICHMENT_ONLY_NO_TRADER_GATE`
- **Ledger:** continues writing to `forward_paper_ledger`. The 70 existing V4 rows (`V4_NO_GATE_SPREAD_ONLY`) remain as historical reference and will be excluded from V5.2 analysis by filtering on `policy_version`.

### Signal filtering (`signal-notifier`)
Layered on top of enrichment's existing `overnight_score >= 1 AND spread <= 10% AND directional UOA > $500k`:
- `volume_oi_ratio > 2.0`
- `moneyness_pct BETWEEN 0.05 AND 0.15`
- `VIX <= VIX3M` (fail-closed: skip the day when either value is NULL or when VIX3M is absent from the enriched row)
- `ORDER BY` directional UOA dollar volume
- `LIMIT 1`

The notifier sends **at most one email per day** or nothing at all. The inbox is the signal.

### Feature enrichment (`enrichment-trigger`)
Three new NULLABLE columns on `overnight_signals_enriched`:
- `volume_oi_ratio FLOAT64` — `recommended_volume / NULLIF(recommended_oi, 0)`
- `moneyness_pct FLOAT64` — `abs(recommended_strike - underlying_price) / underlying_price`. If `underlying_price` is missing, fall back to Polygon's scan_date daily close.
- `vix3m_at_enrich FLOAT64` — FRED `VXVCLS` close at or before `scan_date`, cached once per invocation.

Schema is ensured idempotently via `ALTER TABLE ADD COLUMN IF NOT EXISTS`; old rows receive NULL and are skipped by the notifier's fail-closed filter.

## What we are NOT doing in V5.2 (Phase 2 backlog)

These remain research hypotheses, not live policy:
- **Sweep / block detection** — requires tick-level trade classification we don't yet buy.
- **Aggressor side (bid vs ask lift)** — needs millisecond-level Polygon trade data.
- **GEX / dealer positioning** — would need an options-chain snapshot pipeline we don't own.
- **Regime-conditional sizing** — ship flat sizing first; prove EV before adding knobs.

Each will be spec'd as a standalone decision note only after V5.2 accumulates paper EV evidence.

## Rollback plan

If V5.2 underperforms in paper:
1. `git revert` the V5.2 implementation commit. No table drops, no schema downgrades — the three new columns stay NULL on pre-V5.2 rows and are harmless on the enriched table.
2. V4 rows in `forward_paper_ledger` are tagged `V4_NO_GATE_SPREAD_ONLY` and remain queryable as historical baseline.
3. `scripts/research/` and `signals_labeled_v1` are untouched per frozen-research policy.

## Validation posture

- **30-day paper window** is mandatory before any real-money execution. `gammarips-review` must audit this change before the first deploy.
- **No further gate tuning during paper window.** If EV is negative after 4 weeks, revisit Deep Research; don't knob-twiddle.
- **Direction mix is not a flaw.** Bearish dominance still reflects regime.
