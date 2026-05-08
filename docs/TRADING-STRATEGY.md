# TRADING-STRATEGY.md

## Status
**V5.3 "Target 80"** is the only active strategy (adopted 2026-04-17). V4 retired same day. V3 retired 2026-04-16. For the one-page operator view, see [`CHEAT-SHEET.md`](../CHEAT-SHEET.md). For the rationale, see [`docs/DECISIONS/2026-04-17-v5-3-target-80.md`](DECISIONS/2026-04-17-v5-3-target-80.md). Earlier V1-V4 history lives in `docs/archive/`.

**V5.4 "Agent Ranker" is in active development** (spec locked 2026-05-08, no code yet). V5.4 replaces V5.3's deterministic SQL ranker with a Scorer→Picker LLM pair while inheriting V5.3's hard gates (V/OI floor, moneyness, OI/vol floors, VIX ≤ VIX3M, earnings overlap exclusion) upstream unchanged. V5.3 keeps running in production in parallel via a second `forward_paper_ledger` row tagged `policy_version=V5_4_AGENT_RANKER`. No ledger truncation. V5.3 retires only when V5.4 wins on N≥30 head-to-head closes. Spec: [`docs/DECISIONS/2026-05-08-v5-4-locked-spec.md`](DECISIONS/2026-05-08-v5-4-locked-spec.md). Plan: [`docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md`](EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md).

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
- `recommended_spread_pct <= 0.08` (tightened from 0.10 on 2026-05-06 per H11 lit-audit; Muravyev & Pearson 2020 RFS, Cremers & Weinbaum 2010)
- Directional UOA > $500k (`call_uoa_depth` if bullish, `put_uoa_depth` if bearish)

Notifier (`signal-notifier`) layers on top of that:
- `volume_oi_ratio > 2.0` at focal strike
- `moneyness_pct BETWEEN 0.05 AND 0.10` (5-10% OTM; tightened from 0.15 on 2026-05-06 per H12 lit-audit; Aretz et al. 2023 RoF, Augustin et al. 2022 J. Fin. Mkts)
- `VIX <= VIX3M` regime gate (fail-closed if either is NULL)
- **Earnings-overlap exclusion** (added 2026-05-06): exclude any ticker whose scheduled earnings date falls in `[scan_date, entry_day + 2 trading days]`. Window includes `scan_date` to catch AMC-scan_date contamination (V/OI signal generated under known-imminent earnings positioning, then prints before our 10:00 entry_day open). Literature-anchored hard rule (De Silva, Smith & So 2026 *Review of Finance*; Cao & Han 2013 JFE) — retail loses 5–9% on average per earnings event holding long single-leg through the print, 10–14% on high-vol names. Fail-closed if FMP earnings calendar is unreachable OR returns a non-list payload (quota-exhausted: HTTP 200 + error dict). See `docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md`.
- Deterministic 4-key `ORDER BY` then `LIMIT 10` (post-2026-05-01 `voi-first` ranker): `(1) COALESCE(directional V/OI, 0) DESC, (2) recommended_spread_pct ASC, (3) overnight_score DESC, (4) ticker ASC`. Lead key is direction-aware (`call_vol_oi_ratio` for BULLISH, `put_vol_oi_ratio` for BEARISH) per `docs/DECISIONS/2026-05-01-ranker-v2-voi-first.md`. Every tiebreaker is necessary for determinism. Selection: walk the ranked list and take the first ticker NOT reporting earnings in the window. If all 10 have earnings overlap → skip the day with `skip_reason=earnings_overlap_all_candidates`.

If nothing clears the stack, nothing is emailed.

## Publication timing (canonical surface contract)
Today's pick is revealed publicly on the webapp, to paid WhatsApp subscribers, and to any MCP consumer **simultaneously at ~07:30 ET day-0** (moved from 09:00 ET on 2026-05-06 — see `docs/DECISIONS/2026-05-06-signal-notifier-0730-cron.md`) — the same moment `signal-notifier` fires the operator email. There is no earlier access tier. Paying WhatsApp subscribers pay for **convenience** (a push notification to their phone so they don't have to check the webapp), not for timing advantage over free users.

The single source of truth is Firestore `todays_pick/{scan_date}`, written exactly once per run by `signal-notifier` atomically **before** the operator email is sent (fail-closed: if the Firestore write raises, the email is not sent — we never emit inconsistent surfaces). All downstream surfaces (webapp banner, MCP `get_todays_pick`, agent-arena verdict debate, GTM content drafter, WhatsApp push) MUST read this doc without re-applying gate filters. Re-filtering on the read side is the drift vector this contract exists to eliminate.

Schema of `todays_pick/{scan_date}`:
- `has_pick: bool` — false on empty-state days, with `skip_reason` ∈ {`no_candidates_passed_gates`, `regime_fail_closed`, `vix_backwardation`, `earnings_overlap_all_candidates`, `earnings_calendar_unavailable`}
- `ticker, direction, recommended_contract, recommended_strike, recommended_expiration, recommended_mid_price, recommended_dte` — the pick
- `overnight_score, vol_oi_ratio, moneyness_pct, call_dollar_volume, put_dollar_volume, vix3m_at_enrich, vix_now_at_decision` — the gate-evidence fields (for the "why today's pick" panel)
- `decided_at: TIMESTAMP, effective_at: ISO8601 string` — decision time and the 10:00 ET day-1 simulated entry time
- `policy_version: "V5_3_TARGET_80"` — pinned. Never gets mutated; a new version string means a different policy.

**Simulated entry at 10:00 ET day-1 in `forward-paper-trader` models realistic operator slippage; real-money execution is the operator's responsibility and discretionary.** The paper ledger is the control — it takes every V5.3 pick regardless of arena verdict or operator skip. When we start publishing real-money track record as a marketing claim (Phase 5+), every claim must be labeled with the filter used (e.g., "paper: full-coverage +X%" vs "arena-filtered: took only TAKE-votes, +Y%").

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

## Live cohort + public stats surface (added 2026-05-06)
- **Cohort start date:** `LIVE_COHORT_START_DATE = "2026-05-07"`. Constant lives in `signal-notifier/main.py`. Pre-cohort `forward_paper_ledger` rows were truncated 2026-05-06 — they were generated under pre-audit filter set (looser spread, looser moneyness, no earnings exclusion) and are not a clean baseline.
- **Stats Firestore doc:** `cohort_stats/current`, single source of truth for the public webapp social-proof panel. Schema and refresh cadence in `docs/DECISIONS/2026-05-06-paper-trader-reset-and-stats-surface.md`.
- **Refresh trigger:** `signal-notifier/run_notifier()` calls `compute_and_write_cohort_stats()` once per daily cron run. Ad-hoc refresh via `POST /refresh_stats` (no email side-effects).
- **Webapp deep-link:** operator email + WhatsApp messages include `https://gammarips.com/signals/{TICKER}` so subscribers click through to the per-ticker rationale page.

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
