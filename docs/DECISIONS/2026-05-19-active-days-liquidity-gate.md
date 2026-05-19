# 2026-05-19 — `active_days_20d` hard liquidity gate at signal-notifier

## Decision

Add a new hard gate in `signal-notifier`: reject any finalist whose recommended option contract has fewer than **5 trading days with vol > 0 in the 20 sessions preceding scan_date** (`active_days_20d >= 5`).

Computed per finalist via a single Polygon daily-aggregates call on `recommended_contract`. Fail-closed: if Polygon returns no data or errors, the gate treats it as `active_days_20d = 0` and rejects. Skip reason logged as `thin_contract_liquidity`.

## Why now

**Production incident 2026-05-14.** V5.4 picked KBR Jun-18 $27.5P. Scan-day volume 323 cleared every existing gate (vol≥50 ✓, V/OI 2.03 ✓, OI 159 ✓, spread 2.25% ✓, moneyness 9.84% OTM ✓, DTE 35 ✓). Scorer composite 9.4 — highest of any V5.4 pick to date. Trader marked **INVALID_LIQUIDITY** on 5/14: zero minute bars all day. Polygon confirms the contract printed on only 4 of the prior 21 trading days. The "323 contracts on 5/13" was a single block trade, not real ongoing liquidity. The existing point-in-time gates can't distinguish this from a contract trading 50/day consistently.

This is a fail-closed structural execution leak, not an alpha question. INVALID_LIQUIDITY days burn the daily-pick slot, show up publicly in the ledger as no-fill, and have no upside (the trade can't fire — there's no contra to take).

## Backtest

**Source:** `overnight_signals_enriched` filtered to `recommended_contract IS NOT NULL AND is_win IS NOT NULL`. N=1,940 rows across 25 trading days, 2026-04-10 → 2026-05-14. (NOT `signals_labeled_v1` — that ends 2026-04-06 pre-V4 and is stale.)

**Method:** Per row, pull (a) trailing 20 trading days of Polygon daily option bars to compute `active_days_20d`, (b) entry-day minute bars to check fillability. Bucket by `active_days_20d`.

**Fillability gradient — monotone:**

| Bucket | N | % fillable |
|---|---:|---:|
| [0-3] | 1,403 | 50.0 % |
| [4-7] | 308 | 62.7 % |
| [8-13] | 164 | 74.4 % |
| [14-20] | 65 | 87.7 % |

Bootstrap (N=1,000) fillability gap at `≥8`: **+25.9 pp** (95% CI [20.4, 31.2]). Chronological half-split confirms stability: H1 +25.6pp, H2 +25.8pp — not a recency artifact.

**Edge gradient — flat:** Win-rate is 71-79% across all buckets. Gap at `≥8` is −2.1pp, CI crosses zero. The gate **buys fillability with no edge loss and no edge gain.**

**Caveat:** The `is_win` field's 77% baseline reflects permissive labeling (peak-3d / target-touch on stock side, not actual option PnL — see `project_pilot_entry_model_artifact`). "No edge change" is "no selection effect on the permissive label" — the gate may still improve real option PnL.

## Why threshold = 5, not 8

| Threshold | Cohort retained | V5.4-eligible retained | V5.4 dry days (of 25) |
|---|---:|---:|---:|
| ≥3 | 27.7% | 33.0% | 0 |
| **≥5** | **21.9%** | **30.2%** | **0** |
| ≥8 | 11.8% | 26.7% | 2 |

`≥8` is cleaner statistically but burns 2/25 V5.4-eligible days dry. Per `project_v5_4_funnel_starvation`, the picker already runs on 1-candidate days 68% of the time — every dry day matters. `≥5` lifts fillability 50% → 71% (~95% of the gain from ≥8) with **zero dry days** in the V5.4 eligibility cohort. KBR (4 active days) is killed by either threshold.

The threshold is conservative on purpose. If at N≥15 V5.4 closes we still see thin-contract patterns surviving the gate, tighten to ≥7 then ≥8 — don't relax. Direction of travel is one-way.

## Where the gate lives

**signal-notifier, not enrichment-trigger.** Three reasons:

1. **Co-location with sibling gates.** The V/OI, moneyness, DTE, earnings, spread, and OI/vol floors all live in `signal-notifier`. Adding one more gate there keeps the gate stack in one file.
2. **Cheaper API spend.** Computing per-finalist (typically ~10-30/day) is one Polygon call per candidate. Computing in `enrichment-trigger` would be one call per enriched row (~70-100/day) — 3-7× more calls for no extra signal.
3. **No schema migration.** Adding a column to `overnight_signals_enriched` would require a BQ DDL + an enrichment-trigger code change. Keeping the computation transient in signal-notifier avoids both.

Trade-off: the value is computed but not stored. We accept that — if research later wants it for a cohort study, the backtest cache at `backtesting_and_research/cache/poly_daily/` already has 25 days of history and the next backtest can recompute on demand. Not worth a schema change.

## Implementation contract

- **Function:** `compute_active_days_20d(recommended_contract: str, scan_date: date) -> int`
- **Polygon call:** `GET /v2/aggs/ticker/{contract}/range/1/day/{scan_date - 35 cal days}/{scan_date - 1 cal day}` with `adjusted=true&sort=asc&limit=120`
- **Compute:** Filter results to the 20 most recent trading days ending the trading day *before* scan_date (use pandas BDay or pandas_market_calendars XNYS). Zero-fill missing trading days. Count days where `v > 0`.
- **Gate:** If `active_days_20d < 5`, reject. Skip reason `thin_contract_liquidity`. Log `recommended_contract` and `active_days_20d` for postmortem.
- **Fail-closed:** Any Polygon error (timeout, 4xx, 5xx, empty body) → treat as `active_days_20d = 0` → reject. Log distinct skip reason `liquidity_check_unavailable` so we can tell the two apart in postmortem.
- **No new dependencies.** signal-notifier already calls Polygon for other reasons; reuse the existing session.

## Cohort impact projection

Under the V5.4 Scenario C eligibility filter, the gate retains ~30% of pre-gate candidates. Median V5.4-eligible candidates/day was 2 under Scenario C — this drops to median 1, BUT zero days go fully dark (vs 2 days fully dark at `≥8`). The Picker continues to operate at the same starved cadence as before, just on a higher-quality candidate set.

## Definition of done

- DECISIONS doc committed (this file)
- TRADING-STRATEGY.md gate list updated
- signal-notifier deployed via `bash deploy.sh`
- Manual scan invocation verifies the gate fires and `thin_contract_liquidity` appears as a skip reason in logs
- First overnight cron run produces either a pick or a dark-day skip — neither path errors

## References

- Backtest script: `backtesting_and_research/2026-05-19_trailing_liquidity_backtest.py`
- Backtest output: `backtesting_and_research/results/2026-05-19_trailing_liquidity_{summary.md, backtest.csv}`
- KBR incident row: `forward_paper_ledger WHERE ticker='KBR' AND scan_date='2026-05-13'` (exit_reason `INVALID_LIQUIDITY`)
- Sibling gate decisions: [2026-05-12 pipeline alignment](2026-05-12-v5-4-pipeline-alignment.md), [2026-05-11 leakage fail-closed + DTE](2026-05-11-leakage-fail-closed-and-dte-gate.md)
- Memory: `project_v5_4_funnel_starvation`, `project_pilot_entry_model_artifact`, `feedback_use_live_enrichment_not_labeled_v1`
