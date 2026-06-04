# TRADING-STRATEGY.md

## Status
**V6 "Tournament"** is the only active strategy (launched 2026-06-04; V5.4 retired the same day; `forward_paper_ledger` TRUNCATED — 13 closes wiped, averaging 0.0% realized return; `policy_version='V6_TOURNAMENT'`, cohort_start 2026-06-04). V6 replaces V5.4's memory-aware single judge with a **randomized bracket TOURNAMENT** hosted at the `signal-judge` Cloud Run service (`tournament_v1`, version 7, `gemini-3.1-pro-preview`). **All** enriched signals enter the tournament — there are **NO per-candidate selection gates** any more. The tournament runs **3 independent brackets**, each seeding the full pool in randomized order and reducing it in batches of ≤10 (top-2 advance per batch) until a single bracket winner remains (e.g. 94→20→4→1); a **consensus winner** is chosen across the 3 bracket winners (3/3 agreement → `confidence=high`, 2/3 → `med`, 1/3 → `low`). The judge uses a **simple prompt + the daily report + a per-contract JSON** with NO case-memory, NO rubric, and NO composite weights. **Fail-closed on any tournament error: no fallback path exists.** Stale `volume`/`OI`/`V-OI` are stripped from the judge's view (they are a one-day-stale scan-time snapshot — see DEFERRED note in `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`); the judge sees the **real** spread. Every candidate is `assert_no_leakage`-checked before it can enter a bracket.

V6 retains V5.4's trader execution mechanics unchanged (entry/stop/target/hold/trail/exit) — V6 is a *ranker + gate-removal* change, not a *trader* change. For the one-page operator view, see [`CHEAT-SHEET.md`](../CHEAT-SHEET.md). Decision locks: [`docs/DECISIONS/2026-06-04-bracket-tournament.md`](DECISIONS/2026-06-04-bracket-tournament.md), [`docs/DECISIONS/2026-06-04-contract-selection-liquidity.md`](DECISIONS/2026-06-04-contract-selection-liquidity.md), [`docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`](DECISIONS/2026-06-04-pipeline-bug-fixes.md).

> **HISTORY / SUPERSEDED 2026-06-04.** **V5.4 "Agent Ranker"** was the active strategy from 2026-05-08 (promoted, V5.3 retired same day, `forward_paper_ledger` TRUNCATED — 246 rows wiped) until 2026-06-04. V5.4 replaced V5.3's deterministic SQL ranker with an LLM ranker hosted at `signal-judge` (renamed from `signal-ranker` on 2026-06-04; the BQ table `signal_ranker_runs` + Firestore `v5_4_*` keys kept their names — **still kept under V6**). As of 2026-06-04 (the same day V6 launched) the V5.4 ranker had been collapsed into a single memory-aware judge (`judge_v6`, `gemini-3.1-pro-preview`) that scored every gated candidate AND selected the pick in one structured call (see `docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md`); V6 then superseded that judge entirely with the tournament. (Earlier V5.4 history: launched as a `gemini-3.5-flash` Scorer fanout + `gemini-3.1-pro-preview` Picker; the Scorer migrated `gemini-3-flash-preview` → `gemini-3.5-flash` on 2026-05-27 — see `docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md`.) For the V5.4 retirement/V5.3 decision, see [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md); for the V5.4 agent-ranker design, see [`docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md`](EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md) and [`docs/EXEC-PLANS/2026-05-08-v5-4-promotion.md`](EXEC-PLANS/2026-05-08-v5-4-promotion.md). Earlier V1-V5.3 history lives in `docs/archive/`.

## Objective
Generate at most one high-conviction options alert per trading day, execute it mechanically by phone with pre-defined stop and target orders at entry, and hold for up to 3 trading days. Minimize decisions; maximize routine adherence.

## Regime posture (named explicitly per 2026-05-09 methodology audit)
**V6 is a momentum-continuation bet conditioned on calm regimes.** Not a vol-arbitrage strategy, not a contrarian strategy. With the V5.4 selection-gate stack removed (see Signal filter stack below), the regime conditioning now rests on the **two SAFETY rails** kept at `signal-notifier` — the `VIX ≤ VIX3M` regime gate (fail-closed) and the no-earnings-in-the-3-day-hold exclusion — plus the upstream `enrichment-trigger` definition of "enriched" (`overnight_score ≥ 1`, `spread ≤ 0.30`, directional UOA > $500K). Those still bias the pool toward calm-market large-cap flow plays during non-earnings weeks. A regime shift to mean-reversion would directionally invert EV. The V6 tournament has **no `regime_alignment` rubric** — the `VIX ≤ VIX3M` rail is the only structural line of defense against regime-flip surprise.

**Operator rule (2026-05-09 audit, still in force under V6):** at 5 consecutive losses with no skipped days (the safety rails kept emitting picks but they kept losing), pause picks and rerun the regime question manually before the next pick. That's the regime-shift signal. Decision: `docs/research_reports/V5_4_METHODOLOGY_AUDIT_2026_05_09.md`.

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
| Policy labels | `policy_version = V6_TOURNAMENT`, `policy_gate = ENRICHMENT_ONLY_NO_TRADER_GATE` |

**Trailing stop semantics:** The trail is the original V5.3 Deep Research recommendation, deferred 2026-04-17 for Robinhood-mobile-OCO reasons and re-introduced 2026-05-09 because the paper trader (programmatic) and the future Alpaca-agent path both bypass that constraint. Once peak premium reaches `entry × 1.30`, the active stop tightens to `peak × 0.75` and ratchets up with every new peak. The original −60% hard stop is dominated by the trail once active. New ledger fields: `trail_trigger_price`, `peak_premium`, `trail_activated`, `trail_stop_at_exit`. New `exit_reason` value: `TRAIL`. Decision: `docs/DECISIONS/2026-05-09-trailing-stop-25-at-30-pct.md`.

**Fill realism (added 2026-06-04, `docs/DECISIONS/2026-06-04-pnl-sim-realism-fixes.md`).** Three P&L-simulation fixes removed an upward bias in `realized_return_pct`:
- **Symmetric slippage.** Entry pays `+SLIPPAGE_PCT` (2%) and bracket exits now pay the SAME adverse slippage in the opposite direction: `TARGET` fills at `target × (1 − slip)`; `STOP`/`TRAIL` fill at `min(threshold, bar_low, bar_open) × (1 − slip)` (the `min` models a gap-through bar that opens/trades below the stop). Previously exits filled at the exact bracket threshold with no slippage. `TIMEOUT` marks-to-market at the last in-window close with no slippage (it models an exit-at-market, not a liquidity-taking bracket order). New nullable ledger field: `exit_slippage` (the fraction applied; 0.0 on TIMEOUT).
- **Stale-TIMEOUT guard.** A 3-day-hold exit can no longer be labeled a clean `TIMEOUT` when the last available print is on an EARLIER trading day than `exit_day`. Such marks get the distinct `exit_reason='STALE_NO_TIMEOUT_PRINT'` and `illiquid_exit=True` so they are excludable from EV.
- **Late/pre-market fill guard.** The 10:00 ET entry accepts the first print at/after 10:00 only within `LATE_FILL_TOLERANCE_MIN` (30) minutes; a later first print, or a pre-10:00 proxy fill, sets `illiquid_exit=True` and stamps the signed `late_fill_minutes`. The bracket walk now anchors on `entry_ts_ms` so pre-entry bars can never trigger an exit. The bracket `exit_reason` is preserved (the late/illiquid flag rides in `illiquid_exit` + `late_fill_minutes`).

New nullable ledger fields: `exit_slippage`, `illiquid_exit`, `late_fill_minutes`. New `exit_reason` value: `STALE_NO_TIMEOUT_PRINT`. Existing columns and the `INVALID_LIQUIDITY` (zero-volume / no-bar) path are unchanged.

The trader applies **no additional gates**. Every enriched signal for the day is simulated and ledgered, which preserves the research dataset for IC analysis. Human alerting is handled by `signal-notifier`, which applies the two safety rails, runs the V6 bracket tournament, and emails the single tournament-winner ticker. The "official V6 pick" is identified externally via ticker JOIN to Firestore `todays_pick/{scan_date}` — there is no special policy_version tag distinguishing the picked row from the broad-research rows in the ledger.

## Signal filter stack
**V6 removed the per-candidate selection gates entirely (2026-06-04).** The stack is now just the upstream "enriched" definition plus two safety rails — everything else is decided inside the tournament.

Enrichment (`enrichment-trigger`) defines what "enriched" means:
- `overnight_score >= 1`
- `recommended_spread_pct <= 0.30` — **loosened from 0.08 → 0.30 on 2026-06-04.** The old 0.08 threshold was filtering on FAKE spreads: `polygon_client` had been substituting the day low/high for a missing bid/ask, manufacturing 0% spreads on ~43% of picks (one of the 13 bugs fixed 2026-06-04). Once spreads became REAL, 0.08 was rejecting genuinely tradeable contracts; 0.30 admits real spreads while still excluding the untradeable tail. See `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`.
- Directional UOA > $500k (`call_uoa_depth` if bullish, `put_uoa_depth` if bearish)

Notifier (`signal-notifier`) applies **only two SAFETY rails** on top of the enriched pool (no selection gates):
- `VIX <= VIX3M` regime gate (fail-closed if either is NULL). **FRED-resilience (added 2026-06-03):** both FRED CSV fetches retry 3× with linear backoff at a 30s timeout before failing. If the `VXVCLS` (VIX3M) fetch still fails, enrichment **carries forward** the most recent non-null `vix3m_at_enrich` strictly before `scan_date` from BigQuery — but only if it is ≤7 calendar days old; past that bound it stores NULL and the day fail-closes as before. The live VIX leg is never carried forward (a same-day vol spike still trips the gate). **Live-VIX source fallback (simplified 2026-06-04):** if FRED VIXCLS is down, the live VIX falls back to public sources (Stooq, Yahoo) and uses the best one that answers; when both answer it takes the **MAX** (the conservative read for a one-sided `vix_now > vix3m → skip` gate — a low-biased source cannot mask backwardation). A single source is sufficient; only a *total* source blackout fail-closes. **Root cause (2026-06-04): there was never a FRED outage.** All FRED `fredgraph.csv` requests lacked a start date, so FRED serialized each series' full history back to 1990 — a payload that exceeded the read timeout every morning. Every FRED fetch (VIX3M + VIX in enrichment, live VIX in signal-notifier, telemetry VIX in forward-paper-trader) is now bounded with `cosd` = scan_date − 45–60d, dropping the payload to ~30 rows (sub-second); the retry/carry-forward/source-fallback layers remain as defense-in-depth. See `docs/DECISIONS/2026-06-03-vix3m-fred-retry-and-carry-forward.md`.
- **Earnings-overlap exclusion** (added 2026-05-06): exclude any ticker whose scheduled earnings date falls in the 3-day hold window `[scan_date, entry_day + 2 trading days]`. Window includes `scan_date` to catch AMC-scan_date contamination. Literature-anchored hard rule (De Silva, Smith & So 2026 *Review of Finance*; Cao & Han 2013 JFE) — retail loses 5–9% on average per earnings event holding long single-leg through the print, 10–14% on high-vol names. Fail-closed if FMP earnings calendar is unreachable OR returns a non-list payload (quota-exhausted: HTTP 200 + error dict). See `docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md`.

Every enriched candidate that clears the two rails is `assert_no_leakage`-checked, then enters the tournament. **There is no `LIMIT`, no `ORDER BY` selection, and no candidate cap** — the full pool seeds each bracket.

- **V6 bracket tournament** (`signal-judge` Cloud Run service, `tournament_v1`, version 7, `gemini-3.1-pro-preview`): runs **3 independent brackets**, each seeding the full safety-rail-cleared pool in randomized order. Within a bracket the pool is reduced in **batches of ≤10** — each batch returns its top-2, which advance to the next round — until a single bracket winner remains (e.g. 94→20→4→1). A **consensus winner** is chosen across the 3 bracket winners: 3/3 agreement → `confidence=high`, 2/3 → `med`, 1/3 → `low`. The judge sees a **simple prompt + the daily report markdown + a per-contract JSON** with the **real** spread but with stale `volume`/`OI`/`V-OI` stripped out (one-day-stale scan-time snapshots — DEFERRED for re-introduction as frozen point-in-time fields, walled off from the judge; see `docs/DECISIONS/2026-06-04-pipeline-bug-fixes.md`). There is **NO case-memory, NO rubric, NO composite weights** (the V5.4 60/25/15 flow/regime/narrative weighting is gone). **Fail-closed on any tournament error** (timeout, 5xx, off-list/poisoned pick) — `signal-notifier` emits no email and writes an empty-state `todays_pick`; there is **no fallback path** (the V5.4 daily-cadence fallback was removed with the selection gates — see below). The run is mirrored into the kept `signal_ranker_runs` BQ table and Firestore `v5_4_*` keys (table/key names retained for cohort continuity); provenance is stamped `*_prompt_version=7`, `*_model=gemini-3.1-pro-preview`. Decision locks: `docs/DECISIONS/2026-06-04-bracket-tournament.md` + `docs/DECISIONS/2026-06-04-contract-selection-liquidity.md`.

**Contract selection is now liquidity-aware (2026-06-04).** Rather than emit the raw scan-time focal contract, the pipeline selects the most fillable contract consistent with the directional flow at scan time. See `docs/DECISIONS/2026-06-04-contract-selection-liquidity.md`.

**Removed in V6 (2026-06-04):** the per-candidate selection gates `moneyness_pct BETWEEN 0.05 AND 0.13`, `OI ≥ 10`, `vol ≥ 50`, `recommended_dte BETWEEN 7 AND 45`, `volume_oi_ratio > 2.0` (already removed 2026-06-02), and `active_days_20d ≥ 5`, **and the entire daily-cadence FALLBACK path**. They choked winners on stale scan-time data: scan-time OI/liquidity is a one-day-stale snapshot and the sweep that earns the score only becomes OI after our 10:00 entry, so selection on it was a weak-to-negative EV lever. Realized option-PnL evidence: `V/OI > 2` dropped ~55-63% of real +80%/+25% winners for precision lift statistically ≤ 0 (90% CI [-0.061, -0.001]); the prior gate stack drove median ~2 candidates/day picker-starvation. The tournament now ranges across the full enriched pool. See `docs/DECISIONS/2026-06-04-bracket-tournament.md`; the V5.4 gate rationale lives in `docs/DECISIONS/2026-06-02-voi-gate-relaxation-proposal.md`, `docs/DECISIONS/2026-06-02-moneyness-cap-widen-to-13.md`, `docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md`, `docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md`, and `docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`.

If both safety rails leave the pool empty (every candidate reports in the hold window, or the regime gate fail-closes / trips), nothing is emailed — an honest skip.

## Publication timing (canonical surface contract)
Today's pick is revealed publicly on the webapp, to paid WhatsApp subscribers, and to any MCP consumer **simultaneously at ~07:30 ET day-0** (moved from 09:00 ET on 2026-05-06 — see `docs/DECISIONS/2026-05-06-signal-notifier-0730-cron.md`) — the same moment `signal-notifier` fires the operator email. There is no earlier access tier. Paying WhatsApp subscribers pay for **convenience** (a push notification to their phone so they don't have to check the webapp), not for timing advantage over free users.

The single source of truth is Firestore `todays_pick/{scan_date}`, written exactly once per run by `signal-notifier` atomically **before** the operator email is sent (fail-closed: if the Firestore write raises, the email is not sent — we never emit inconsistent surfaces). All downstream surfaces (webapp banner, MCP `get_todays_pick`, agent-arena verdict debate, GTM content drafter, WhatsApp push) MUST read this doc without re-applying gate filters. Re-filtering on the read side is the drift vector this contract exists to eliminate.

Schema of `todays_pick/{scan_date}`:
- `has_pick: bool` — false on empty-state days, with `skip_reason` ∈ {`no_candidates_passed_gates`, `regime_fail_closed`, `vix_backwardation`, `earnings_overlap_all_candidates`, `earnings_calendar_unavailable`, `v5_4_unavailable`, `v5_4_out_of_set`, `v5_4_mass_leakage` (every candidate `assert_no_leakage`-flagged; deterministic all-leakage check in `tournament_v1` / `run_pipeline`)}. (V6 removed the selection-gate-derived `thin_contract_liquidity` / `liquidity_check_unavailable` skip reasons with the `active_days_20d` gate; the keys are retained for historical docs.)
- `ticker, direction, recommended_contract, recommended_strike, recommended_expiration, recommended_mid_price, recommended_dte` — the pick
- `overnight_score, vol_oi_ratio, moneyness_pct, call_dollar_volume, put_dollar_volume, vix3m_at_enrich, vix_now_at_decision` — the evidence fields (for the "why today's pick" panel). Note: `vol_oi_ratio` is retained as a display field only — it is **not** a gate under V6 and is **not** fed to the tournament judge.
- `policy_gate` — `ENRICHMENT_ONLY_NO_TRADER_GATE` under V6. (The V5.4 `STRICT` / `FALLBACK` split was removed 2026-06-04 when the daily-cadence fallback was retired; the trader still falls back to the `ENRICHMENT_ONLY_NO_TRADER_GATE` constant for any doc that omits the field, so historical FALLBACK rows remain separable in ledger analysis.)
- `decided_at: TIMESTAMP, effective_at: ISO8601 string` — decision time and the 10:00 ET day-1 simulated entry time
- `policy_version: "V6_TOURNAMENT"` — pinned. Never gets mutated; a new version string means a different policy.
- `v5_4_run_id, v5_4_runner_up, v5_4_justification, v5_4_confidence, v5_4_scorer_prompt_version, v5_4_picker_prompt_version, v5_4_scorer_model, v5_4_picker_model` — tournament provenance (key names retained from V5.4 for cohort continuity), present on every `has_pick=True` doc. Under V6, `*_prompt_version=7` and `*_model=gemini-3.1-pro-preview`; `v5_4_confidence` carries the consensus level (`high`/`med`/`low`). Webapp / email / x-poster / blog newsletter render `v5_4_justification` as the "Why we picked it" prose under the contract card.

**Simulated entry at 10:00 ET day-1 in `forward-paper-trader` models realistic operator slippage; real-money execution is the operator's responsibility and discretionary.** The paper ledger is the V6 cohort baseline. The `forward_paper_ledger` was truncated 2026-06-04 when V6 launched (13 closes, avg 0.0%); the V6 cohort starts fresh from 2026-06-04.

## Feature enrichment (`overnight_signals_enriched`)
Three V5.2-era columns added on top of the existing schema (all NULLABLE; old rows get NULL and are excluded by the notifier's fail-closed filter). They remain enrichment outputs; under V6 `volume_oi_ratio` is display-only (no longer a gate or judge input):
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
- **Cohort start date:** `LIVE_COHORT_START_DATE = "2026-06-04"`. Constant lives in `signal-notifier/main.py`. The full `forward_paper_ledger` was TRUNCATED 2026-06-04 when V5.4 was retired (13 closes, avg 0.0% realized return) — V6 cohort starts fresh from 2026-06-04 under `policy_version='V6_TOURNAMENT'`.
- **Stats Firestore doc:** `cohort_stats/current`, single source of truth for the public webapp social-proof panel. Schema and refresh cadence in `docs/DECISIONS/2026-05-06-paper-trader-reset-and-stats-surface.md` (original baseline), updated for V5.4 in `docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`, and for V6 in `docs/DECISIONS/2026-06-04-bracket-tournament.md`.
- **Refresh trigger:** `signal-notifier/run_notifier()` calls `compute_and_write_cohort_stats()` once per daily cron run. Ad-hoc refresh via `POST /refresh_stats` (no email side-effects).
- **Webapp deep-link:** operator email + WhatsApp messages include `https://gammarips.com/signals/{TICKER}` so subscribers click through to the per-ticker rationale page.

## Validation posture
- **Paper-only until proven.** No real-money capital is in market. The V6 cohort begins 2026-06-04 and accumulates closed trades in `forward_paper_ledger`. Real-money go-live (Alpaca agent path documented in `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`) is triggered when: (1) N ≥ 30 closed V6 trades AND (2) cohort EV ≥ 0 AND (3) at least 15 operator-confirmed manual trades match the picker's signal. Until all three fire, the system is paper-only.
- **15-closed-trade interim checkpoint (operator plan, 2026-05-27, carried into V6).** At 15 closed/counted trades (distinct scan_date with a realized exit — excludes SKIPPED and INVALID_LIQUIDITY), run the evals + a diagnostic as a GO/NO-GO health check. This is a milestone, NOT the go-live gate — the full three-part trigger above plus a `gammarips-review` audit still apply before any real-money execution.
- **`gammarips-review` must audit V6 before each new deploy.**
- **No knob-twiddling during paper.** If EV is negative after 4 weeks at N ≥ 15, revisit Deep Research; don't tune filters one at a time.
- **Do not modify `signals_labeled_v1` or `scripts/research/`** — both are frozen for reproducibility.
- **Do not treat bearish dominance as a flaw.** It reflects regime.
- **Do not add execution gates to the trader.** Signal-quality gates live in enrichment and notifier, not in `forward-paper-trader`.
- **Do not add a fallback for V6 tournament errors.** Fail-closed is intentional — signal-judge uptime is the SLO.

## Phase 2 backlog (NOT in V6)
Deferred until V6 accumulates paper EV evidence:
- Sweep / block detection (needs tick-level trade classification)
- Aggressor side (bid vs ask lift, needs millisecond trade data)
- GEX / dealer positioning
- Regime-conditional sizing

Each will ship as its own decision note, not a silent parameter change.
