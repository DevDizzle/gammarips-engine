# TRADING-STRATEGY.md

## Status
**V5.4 "Agent Ranker"** is the only active strategy (promoted 2026-05-08; V5.3 retired same day; `forward_paper_ledger` TRUNCATED — 246 rows wiped). V5.4 replaces V5.3's deterministic SQL ranker with a Scorer→Picker LLM pair (`gemini-3-flash-preview` + `gemini-3.1-pro-preview`) hosted at the `signal-ranker` Cloud Run service. Trader execution mechanics are unchanged from V5.3 — V5.4 is a *picker* change, not a *trader* change. **Fail-closed on V5.4 error: no V5.3 fallback exists.** For the one-page operator view, see [`CHEAT-SHEET.md`](../CHEAT-SHEET.md). For the retirement decision, see [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md). For the V5.4 agent-ranker design, see [`docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md`](EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md). For the V5.4 promotion, see [`docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md`](EXEC-PLANS/2026-05-08-v5-4-promotion.md). Earlier V1-V5.3 history lives in `docs/archive/`.

## Objective
Generate at most one high-conviction options alert per trading day, execute it mechanically by phone with pre-defined stop and target orders at entry, and hold for up to 3 trading days. Minimize decisions; maximize routine adherence.

## Regime posture (named explicitly per 2026-05-09 methodology audit)
**V5.4 is a momentum-continuation bet conditioned on calm regimes.** Not a vol-arbitrage strategy, not a contrarian strategy. The composed gate stack (VIX≤VIX3M + no-earnings-during-hold + 5-10% OTM + spread≤8% + V/OI>2 + UOA>$500K + sector cluster boost) implicitly selects calm-market large-cap sector-rotation plays during non-earnings weeks. A regime shift to mean-reversion would directionally invert EV. The Picker's `regime_alignment` rubric is the only line of defense against regime-flip surprise; it operates on a single daily report.

**Operator rule (2026-05-09 audit):** at 5 consecutive V5.4 losses with no skipped days (gates kept emitting picks but they kept losing), pause picks and rerun the regime question manually before the next pick. That's the regime-shift signal. Decision: `docs/research_reports/V5_4_METHODOLOGY_AUDIT_2026_05_09.md`.

## Execution policy (`forward-paper-trader`)
| Parameter | Value |
|---|---|
| Entry | 10:00 ET on day-1 (first trading day after `scan_date`) |
| Stop (initial hard) | −60% on option premium (active until trail activates) |
| Trail trigger | +30% gain on premium (peak premium ≥ entry × 1.30) |
| Trail level | Peak × 0.75 (25% drawdown from peak); ratchets up with each new peak |
| Target | +80% on option premium |
| Hold | 3 trading days |
| Exit | 15:50 ET on day-3 at market (or earlier if stop/trail/target fires) |
| Exit precedence | On ambiguous bars: TIMEOUT > TRAIL/STOP > TARGET (conservative) |
| Direction | Calls on `BULLISH`, puts on `BEARISH` |
| Ledger | `profitscout-fida8.profit_scout.forward_paper_ledger` |
| Policy labels | `policy_version = V5_4_AGENT_RANKER`, `policy_gate = ENRICHMENT_ONLY_NO_TRADER_GATE` |

**Trailing stop semantics:** The trail is the original V5.3 Deep Research recommendation, deferred 2026-04-17 for Robinhood-mobile-OCO reasons and re-introduced 2026-05-09 because the paper trader (programmatic) and the future Alpaca-agent path both bypass that constraint. Once peak premium reaches `entry × 1.30`, the active stop tightens to `peak × 0.75` and ratchets up with every new peak. The original −60% hard stop is dominated by the trail once active. New ledger fields: `trail_trigger_price`, `peak_premium`, `trail_activated`, `trail_stop_at_exit`. New `exit_reason` value: `TRAIL`. Decision: `docs/DECISIONS/2026-05-09-trailing-stop-25-at-30-pct.md`.

The trader applies **no additional gates**. Every enriched signal for the day is simulated and ledgered, which preserves the research dataset for IC analysis. Human alerting is handled by `signal-notifier`, which applies the gate stack, calls the V5.4 agent ranker, and emails the single picked ticker. The "official V5.4 pick" is identified externally via ticker JOIN to Firestore `todays_pick/{scan_date}` — there is no special policy_version tag distinguishing the picked row from the broad-research rows in the ledger.

## Signal filter stack
Enrichment (`enrichment-trigger`) enforces:
- `overnight_score >= 1`
- `recommended_spread_pct <= 0.08` (tightened from 0.10 on 2026-05-06 per H11 lit-audit; Muravyev & Pearson 2020 RFS, Cremers & Weinbaum 2010)
- Directional UOA > $500k (`call_uoa_depth` if bullish, `put_uoa_depth` if bearish)

Notifier (`signal-notifier`) layers on top of that:
- `volume_oi_ratio > 2.0` at focal strike
- `moneyness_pct BETWEEN 0.05 AND 0.10` (5-10% OTM; tightened from 0.15 on 2026-05-06 per H12 lit-audit; Aretz et al. 2023 RoF, Augustin et al. 2022 J. Fin. Mkts)
- `recommended_dte BETWEEN 7 AND 45` (added 2026-05-11 at 7-30, widened to 7-45 on 2026-05-12 per pipeline-alignment decision; anchored to `scorer_v5.md:18` / `picker_v4.md:24` — short enough for gamma to dominate theta over the 3-day hold, long enough to survive a flat session AND to keep candidate inventory above the picker-starvation floor. >45 DTE contracts can't print +80% on a 3-day move at the bracket's gamma profile and are penalized by the scorer/picker rubrics. See `docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md` for the widening rationale and Scenario C funnel projection.).
- `active_days_20d >= 5` (added 2026-05-19): the recommended option contract must have printed on ≥5 of the 20 trading days preceding scan_date. Computed per finalist via one Polygon daily-aggs call on `recommended_contract`; zero-fill missing trading days. **Fail-closed:** any Polygon error or empty body → treat as 0 → reject with skip reason `liquidity_check_unavailable`; reject-by-threshold uses skip reason `thin_contract_liquidity`. Motivated by the 2026-05-14 KBR INVALID_LIQUIDITY no-fill (323 scan-day vol but only 4/21 active days, zero prints on entry day). Backtest on N=1,940 enriched rows: fillability lifts 50% → 71% at this threshold with no edge change. See `docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md`.
- `VIX <= VIX3M` regime gate (fail-closed if either is NULL)
- **Earnings-overlap exclusion** (added 2026-05-06): exclude any ticker whose scheduled earnings date falls in `[scan_date, entry_day + 2 trading days]`. Window includes `scan_date` to catch AMC-scan_date contamination (V/OI signal generated under known-imminent earnings positioning, then prints before our 10:00 entry_day open). Literature-anchored hard rule (De Silva, Smith & So 2026 *Review of Finance*; Cao & Han 2013 JFE) — retail loses 5–9% on average per earnings event holding long single-leg through the print, 10–14% on high-vol names. Fail-closed if FMP earnings calendar is unreachable OR returns a non-list payload (quota-exhausted: HTTP 200 + error dict). See `docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md`.
- Deterministic 4-key `ORDER BY` then `LIMIT 10` (the candidate pool): `(1) COALESCE(directional V/OI, 0) DESC, (2) recommended_spread_pct ASC, (3) overnight_score DESC, (4) ticker ASC`. Lead key is direction-aware. Earnings-overlap exclusion removes any ticker reporting in the hold window from the pool. Surviving candidates (≤10) are passed to the V5.4 agent ranker.
- **V5.4 agent ranker** (`signal-ranker` Cloud Run service): Scorer fanout (`gemini-3-flash-preview`, scorer_v3 — HEDGING `flow_conviction` ≤4 hard cap) grades each candidate on three rubrics 1-10. Composite weights 60/25/15 flow / regime / narrative (weighted sum). Top-5 by composite go to the Picker (`gemini-3.1-pro-preview`, picker_v2 — enum confidence). Picker reads top-5 candidate enriched data + Scorer reasoning prose (no raw rubric scores) + the daily report markdown + 14d ledger summary. Returns one ticker + runner-up + justification + confidence. **No abstain.** **No V5.3 fallback** — signal-ranker uptime is the SLO; on any error (timeout, 5xx, picker out-of-set), `signal-notifier` fails CLOSED (no email, empty-state `todays_pick`). Decision lock: `docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`.

If nothing clears the stack, nothing is emailed.

## Publication timing (canonical surface contract)
Today's pick is revealed publicly on the webapp, to paid WhatsApp subscribers, and to any MCP consumer **simultaneously at ~07:30 ET day-0** (moved from 09:00 ET on 2026-05-06 — see `docs/DECISIONS/2026-05-06-signal-notifier-0730-cron.md`) — the same moment `signal-notifier` fires the operator email. There is no earlier access tier. Paying WhatsApp subscribers pay for **convenience** (a push notification to their phone so they don't have to check the webapp), not for timing advantage over free users.

The single source of truth is Firestore `todays_pick/{scan_date}`, written exactly once per run by `signal-notifier` atomically **before** the operator email is sent (fail-closed: if the Firestore write raises, the email is not sent — we never emit inconsistent surfaces). All downstream surfaces (webapp banner, MCP `get_todays_pick`, agent-arena verdict debate, GTM content drafter, WhatsApp push) MUST read this doc without re-applying gate filters. Re-filtering on the read side is the drift vector this contract exists to eliminate.

Schema of `todays_pick/{scan_date}`:
- `has_pick: bool` — false on empty-state days, with `skip_reason` ∈ {`no_candidates_passed_gates`, `regime_fail_closed`, `vix_backwardation`, `earnings_overlap_all_candidates`, `earnings_calendar_unavailable`, `v5_4_unavailable`, `v5_4_out_of_set`, `v5_4_mass_leakage` (added 2026-05-11 — all top-5 candidates flagged leakage by Scorer per `scorer_v4.md:29`), `thin_contract_liquidity` / `liquidity_check_unavailable` (added 2026-05-19 — see `active_days_20d` gate)}
- `ticker, direction, recommended_contract, recommended_strike, recommended_expiration, recommended_mid_price, recommended_dte` — the pick
- `overnight_score, vol_oi_ratio, moneyness_pct, call_dollar_volume, put_dollar_volume, vix3m_at_enrich, vix_now_at_decision` — the gate-evidence fields (for the "why today's pick" panel)
- `decided_at: TIMESTAMP, effective_at: ISO8601 string` — decision time and the 10:00 ET day-1 simulated entry time
- `policy_version: "V5_4_AGENT_RANKER"` — pinned. Never gets mutated; a new version string means a different policy.
- `v5_4_run_id, v5_4_runner_up, v5_4_justification, v5_4_confidence, v5_4_scorer_prompt_version, v5_4_picker_prompt_version, v5_4_scorer_model, v5_4_picker_model` — agent-ranker provenance, present on every `has_pick=True` doc post-2026-05-08 promotion. Webapp / email / x-poster / blog newsletter render `v5_4_justification` as the "Why we picked it" prose under the contract card.

**Simulated entry at 10:00 ET day-1 in `forward-paper-trader` models realistic operator slippage; real-money execution is the operator's responsibility and discretionary.** The paper ledger is the V5.4 cohort baseline. Pre-2026-05-08 V5.3 ledger rows were truncated; the V5.4 cohort starts fresh from 2026-05-08.

## Feature enrichment (`overnight_signals_enriched`)
Three V5.2-era columns added on top of the existing schema (all NULLABLE; old rows get NULL and are excluded by the notifier's fail-closed filter). These remain V5.4's canonical inputs:
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

## Live cohort + public stats surface
- **Cohort start date:** `LIVE_COHORT_START_DATE = "2026-05-08"`. Constant lives in `signal-notifier/main.py`. The full `forward_paper_ledger` was TRUNCATED 2026-05-08 when V5.3 was retired — V5.4 cohort starts fresh from 2026-05-08.
- **Stats Firestore doc:** `cohort_stats/current`, single source of truth for the public webapp social-proof panel. Schema and refresh cadence in `docs/DECISIONS/2026-05-06-paper-trader-reset-and-stats-surface.md` (pre-promotion baseline) updated for V5.4 in `docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`.
- **Refresh trigger:** `signal-notifier/run_notifier()` calls `compute_and_write_cohort_stats()` once per daily cron run. Ad-hoc refresh via `POST /refresh_stats` (no email side-effects).
- **Webapp deep-link:** operator email + WhatsApp messages include `https://gammarips.com/signals/{TICKER}` so subscribers click through to the per-ticker rationale page.

## Validation posture
- **Paper-only until proven.** No real-money capital is in market. The V5.4 cohort begins 2026-05-08 and accumulates closed trades in `forward_paper_ledger`. Real-money go-live (Alpaca agent path documented in `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`) is triggered when: (1) N ≥ 30 closed V5.4 trades AND (2) cohort EV ≥ 0 AND (3) at least 15 operator-confirmed manual trades match the picker's signal. Until all three fire, the system is paper-only.
- **`gammarips-review` must audit V5.4 before each new deploy.**
- **No knob-twiddling during paper.** If EV is negative after 4 weeks at N ≥ 15, revisit Deep Research; don't tune filters one at a time.
- **Do not modify `signals_labeled_v1` or `scripts/research/`** — both are frozen for reproducibility.
- **Do not treat bearish dominance as a flaw.** It reflects regime.
- **Do not add execution gates to the trader.** Signal-quality gates live in enrichment and notifier, not in `forward-paper-trader`.
- **Do not add a V5.3 fallback for V5.4 errors.** Fail-closed is intentional — signal-ranker uptime is the SLO.

## Phase 2 backlog (NOT in V5.4)
Deferred until V5.4 accumulates paper EV evidence:
- Sweep / block detection (needs tick-level trade classification)
- Aggressor side (bid vs ask lift, needs millisecond trade data)
- GEX / dealer positioning
- Regime-conditional sizing

Each will ship as its own decision note, not a silent parameter change.
