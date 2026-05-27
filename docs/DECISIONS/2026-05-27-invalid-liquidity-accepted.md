# 2026-05-27 — INVALID_LIQUIDITY accepted as a paper-only artifact; trailing-liquidity volume-floor REJECTED

## Decision

**No gate change.** The existing `active_days_20d >= 5` liquidity gate in `signal-notifier` stays exactly as-is. A proposed tightening (add a per-day volume floor — count a day "active" only if `vol >= N`) was backtested and **rejected**. INVALID_LIQUIDITY no-fill days are accepted as an inherent, paper-only cost of the V5.4 strategy. No change to `signal-notifier`, `enrichment-trigger`, or `forward-paper-trader`.

## Why now

EQIX (scan 2026-05-20) hit INVALID_LIQUIDITY and BLK (scan 2026-05-21) was at risk, **despite** the `active_days_20d >= 5` gate (shipped 2026-05-19) being live when both were picked. Investigation confirmed the picked contracts genuinely printed zero entry-day minute bars — not a fetch/symbol bug. Root cause: the contracts V5.4 selects (5–10% OTM, short-DTE, single-name, chosen off a UOA *spike*) are uniformly thin; `recommended_volume` is the scan-day spike itself, which does not persist; entry-day fill is near-random and not predictable from trailing data.

## Backtest — the per-day volume floor fails

Script: `backtesting_and_research/2026-05-27_active_day_volume_floor.py`. Output: `results/2026-05-27_active_day_volume_floor_summary.md`. Redefined an "active day" as `vol >= MIN_DAILY_VOL` and swept the floor.

**Named spot-check (gate = active_days >= 5):**

| contract | outcome | active days @vol>0 | @vol≥5 |
|---|---|---:|---:|
| OKTA | real fill (−1.96%) | 5 ✓ | 2 ✗ rejected |
| HTZ | real fill (**+80%**) | **3 ✗** | 1 ✗ |
| BBY | real fill (+15.28%) | 6 ✓ | 1 ✗ rejected |
| EQIX | dead / no fill | 6 ✓ | 1 ✗ |
| BLK | dead / no fill | **12 ✓** | 0 ✗ |

Three killers:
1. **A floor rejects our real winners.** At floor 5, OKTA and BBY (both real fills) get cut.
2. **Trailing volume does not predict fillability.** BLK had the *most* trailing activity (12 active days) yet printed zero entry bars; HTZ had only 3 and filled to +80%. No separating line exists.
3. **Funnel collapse.** Floor 5 darkens **10 of 24** V5.4-eligible days (42%); floor 10 darkens 17/24 — a direct violation of the zero-dry-day constraint (`project_v5_4_funnel_starvation`).

A quote-based fill model (fill at the bid/ask even with no trade) was also checked and is **not implementable**: Polygon `/v3/quotes` returns 0 quotes even for OKTA (which traded), so there is no NBBO history on our tier.

## Why accept it (operator call)

INVALID_LIQUIDITY affects **paper trades only**. In a real account the operator enters manually and a thin OTM contract fills by crossing the ask (you become the buyer; there is almost always a quoted ask to lift), and on the exit "if it rips there will be buyers." The paper trader's print-based INVALID_LIQUIDITY therefore **overstates** real-world un-fillability — it fires when no one *else* traded, not when there is no market. These no-fill days cost nothing real.

## Caveat for the eventual go-live diagnostic

The live `active_days_20d >= 5` gate may be **net-harmful** on this cohort: it would have rejected HTZ (the +80% winner) and it did **not** catch EQIX/BLK. It is left untouched per this decision, but flag it for review when the go-live evals/diagnostic run. Do **not** pursue another trailing-liquidity gate variant — the approach is tested and dead.

## References

- Backtest: `backtesting_and_research/2026-05-27_active_day_volume_floor.{py, results/...summary.md}`
- Prior gate it supersedes-in-spirit: [`2026-05-19-active-days-liquidity-gate.md`](2026-05-19-active-days-liquidity-gate.md)
- Memory: `project_invalid_liquidity_root_cause`, `project_v5_4_funnel_starvation`
- Incident rows: `forward_paper_ledger WHERE exit_reason='INVALID_LIQUIDITY'` (KBR 05-13, EQIX 05-20)
