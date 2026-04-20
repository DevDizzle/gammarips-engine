# TRADING-STRATEGY.md

## Status
**V5.3 "Target 80"** is the only active strategy (adopted 2026-04-17). V4 retired same day. V3 retired 2026-04-16. For the one-page operator view, see [`CHEAT-SHEET.md`](../CHEAT-SHEET.md). For the rationale, see [`docs/DECISIONS/2026-04-17-v5-3-target-80.md`](DECISIONS/2026-04-17-v5-3-target-80.md). Earlier V1-V4 history lives in `docs/archive/`.

## Objective
Generate at most one high-conviction options alert per trading day, execute it mechanically by phone with pre-defined stop and target orders at entry, and hold for up to 3 trading days. Minimize decisions; maximize routine adherence.

## Execution policy (`forward-paper-trader`)
| Parameter | Value |
|---|---|
| Entry | 10:00 ET on day-1 (first trading day after `scan_date`) |
| Stop | −60% on option premium (GTC stop-limit in real; bar-walk models option low piercing threshold in paper) |
| Target | +80% on option premium (GTC limit sell in real; bar-walk models option high piercing threshold in paper) |
| Hold | 3 trading days |
| Exit | 15:50 ET on day-3 at market (or earlier if stop/target fires) |
| Exit precedence | On ambiguous bars, STOP wins over TARGET (conservative) |
| Direction | Calls on `BULLISH`, puts on `BEARISH` |
| Ledger | `profitscout-fida8.profit_scout.forward_paper_ledger` |
| Policy labels | `policy_version = V5_3_TARGET_80`, `policy_gate = ENRICHMENT_ONLY_NO_TRADER_GATE` |

The trader applies **no additional gates**. Every enriched signal for the day is simulated and ledgered, which preserves the research dataset. Human alerting is handled by `signal-notifier`, which applies the V5.3 filter stack and emails at most one signal.

## Signal filter stack
Enrichment (`enrichment-trigger`) enforces:
- `overnight_score >= 1`
- `recommended_spread_pct <= 0.10`
- Directional UOA > $500k (`call_uoa_depth` if bullish, `put_uoa_depth` if bearish)

Notifier (`signal-notifier`) layers on top of that:
- `volume_oi_ratio > 2.0` at focal strike
- `moneyness_pct BETWEEN 0.05 AND 0.15` (5-15% OTM)
- `VIX <= VIX3M` regime gate (fail-closed if either is NULL)
- `ORDER BY` directional UOA dollar volume, `LIMIT 1`

If nothing clears the stack, nothing is emailed.

## Feature enrichment (`overnight_signals_enriched`)
Three V5.3 columns added on top of the existing schema (all NULLABLE; old rows get NULL and are excluded by the notifier's fail-closed filter):
- `volume_oi_ratio` — `recommended_volume / NULLIF(recommended_oi, 0)` at the focal strike
- `moneyness_pct` — `abs(recommended_strike - underlying_price) / underlying_price`. Falls back to Polygon scan_date close when `underlying_price` is missing.
- `vix3m_at_enrich` — FRED `VXVCLS` close at or before `scan_date`, cached once per invocation

Schema is ensured via `ALTER TABLE ADD COLUMN IF NOT EXISTS` on every enrichment run (idempotent).

## Benchmarking instrumentation (unchanged)
Every executed ledger row still writes three parallel P&L streams:
1. **Option return** — realized outcome (`realized_return_pct`)
2. **Underlying return** — `(stock_exit_price / stock_entry_price - 1) * direction_sign` at matched entry/exit timestamps
3. **SPY return** — the noise floor. Alpha = `underlying_return - spy_return_over_window`

Plus regime context: `VIX_at_entry` (FRED VIXCLS), `vix_5d_delta_entry`, `hv_20d_entry`, `iv_rank_entry` / `iv_percentile_entry` from `polygon_iv_history`.

## Validation posture
- **Paper + real parallel** from deploy. User elected to begin real-money trading at $500/trade in parallel with paper ledger. `gammarips-review` must audit V5.3 before deploy.
- **No knob-twiddling during paper.** If EV is negative after 4 weeks, revisit Deep Research; don't tune filters.
- **Do not modify `signals_labeled_v1` or `scripts/research/`** — both are frozen for reproducibility.
- **Do not treat bearish dominance as a flaw.** It reflects regime.
- **Do not add execution gates to the trader.** Signal-quality gates live in enrichment and notifier, not in `forward-paper-trader`.

## Phase 2 backlog (NOT in V5.3)
Deferred until V5.3 accumulates paper EV evidence:
- Sweep / block detection (needs tick-level trade classification)
- Aggressor side (bid vs ask lift, needs millisecond trade data)
- GEX / dealer positioning
- Regime-conditional sizing

Each will ship as its own decision note, not a silent parameter change.
