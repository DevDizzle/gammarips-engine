# TRADING-STRATEGY.md

This document is the canonical execution policy. It states current state only.
History lives in `docs/DECISIONS/` (one dated note per change) and `docs/wiki/`.
For the one-page operator view, see [`CHEAT-SHEET.md`](../CHEAT-SHEET.md).

## Status
**V7.1 "TILTED GIGO" is the live policy.** `policy_version='V7_1_TILTED_GIGO'`.
V7.1 = V6 bracket-tournament SELECTION + V7 same-day intraday EXIT + the ".1"
60-day-momentum enrichment tilt (`docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`).

**Cohort:** the live value is `LIVE_COHORT_START_DATE` in `signal-notifier/main.py`
(2026-08-13 as of the 2026-08-12 reset). Do not cache the date in docs. Reset
history in one line: 06-25 (live-OI floor), 07-28 (tournament-liquidity upgrade,
entry 07-29), 08-07 (stale-day-bar fix, entry 08-10), 08-12 (fail-soft restore
lockdown, entry 08-13). The 06-04 V6 launch and the 06-22 V7.1 relabel truncated
the ledger. The four later resets kept all rows and moved the date filter only.
See `docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md`.

## Objective
Generate at most one high-conviction options alert per trading day, execute it
mechanically by phone with a pre-defined same-day OCO bracket at entry
(take-profit + stop + a 15:45 ET time-exit), and be flat by the close.
Minimize decisions. Maximize routine adherence.

## Execution policy (`forward-paper-trader`)
| Parameter | Value |
|---|---|
| Entry | 10:00 ET on `entry_day` (first trading day after `scan_date`) |
| Stop (hard) | −30% on option premium |
| Target | +40% on option premium (take-profit limit) |
| Trail | **OFF** (V7: `USE_TRAIL=False` — flat 3-leg OCO, no peak-ratchet) |
| Hold | **1 trading day (same-day; `entry_day == exit_day`)** |
| Exit | **15:45 ET SAME day — flat no matter what** (or earlier if stop/target fires) |
| Exit precedence | On ambiguous bars: TIMEOUT(15:45) > STOP > TARGET (conservative) |
| Direction | Calls on `BULLISH`, puts on `BEARISH` |
| Ledger | `profitscout-fida8.profit_scout.forward_paper_ledger` |
| Policy labels | `policy_version = V7_1_TILTED_GIGO` (cohort start: see Status), `policy_gate = ENRICHMENT_ONLY_NO_TRADER_GATE` |

**Fill realism** (2026-06-04, `docs/DECISIONS/2026-06-04-pnl-sim-realism-fixes.md`):
- Symmetric slippage: entry pays `+SLIPPAGE_PCT` (2%) and TARGET/STOP exits pay
  the same adverse slippage. TIMEOUT marks-to-market with no slippage.
- Stale-TIMEOUT guard: a mark from an earlier trading day gets
  `exit_reason='STALE_NO_TIMEOUT_PRINT'` and `illiquid_exit=True`.
- Late/pre-market fill guard: the entry accepts the first print at/after 10:00
  within 30 minutes. Later or proxy fills set `illiquid_exit=True` and stamp
  `late_fill_minutes`.

The trader applies **no gates**. It simulates the ticker named in Firestore
`todays_pick/{scan_date}` and ledgers the result. Signal-quality decisions live
upstream in `enrichment-trigger` and `signal-notifier`.

**Entry mark on the pick card** (2026-08-14,
`docs/DECISIONS/2026-08-14-entry-mark-date-validation.md`): `last_trade` is not
entitled on the current Polygon plan, so the card's entry mark is a delayed
`day.close` read, labeled with the measured read time. Prior-session prices are
REFUSED: a bar dated before entry day renders a refusal note and no bracket
levels on the card. The refusal note stays visible to the operator by design.
Display path only, no selection input changes.

## Signal filter stack (current state)
Order: scan → enrichment → notifier rails → BULLISH gate + cap → liquidity
floors → tournament. Each item cites its decision note.

**Enrichment (`enrichment-trigger`) defines "enriched":**
- `overnight_score >= 4` floor, a floor not a ceiling
  (2026-06-05, `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`).
- Directional UOA > $500K (`call_uoa_depth` if bullish, `put_uoa_depth` if bearish).
- Spread gate RETIRED: this Polygon plan serves no options NBBO, so
  `recommended_spread_pct` is permanently NULL
  (2026-06-05, `docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md`).
- Edge-rank to the top `ENRICH_TOP_N` (50) BULLISH names before the grounded-LLM
  news step, with `thinking_budget=0`
  (2026-06-12, `docs/DECISIONS/2026-06-12-enrich-topN-thinking-cap.md`).
- `mom_60` soft tilt: names with 60-day momentum ≥ 0.35 get a +1.25 rank bump,
  and `mom_60` descending is the tie-break. Soft, never drops a candidate.
  Kill switch `MOMENTUM_TILT`
  (2026-06-19, `docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`).
- `LIQ_DEMOTION`: scan-time ghost-flagged names sort below every unflagged name,
  never dropped. Publishes `expected_liquidity` (CLEAN/THIN) on every row
  (2026-07-28, `docs/DECISIONS/2026-07-28-pool-tradeability-build.md`).

**Notifier safety rails (`signal-notifier`):**
- `VIX <= VIX3M` regime gate, fail-closed if either leg is NULL. The strategy is
  a momentum-continuation bet conditioned on calm regimes, and this rail is the
  structural defense
  (2026-06-03, `docs/DECISIONS/2026-06-03-vix3m-fred-retry-and-carry-forward.md`).
- Earnings-overlap exclusion over `[scan_date, entry_day + 2 trading days]`,
  fail-closed if the FMP calendar is unreachable. Conservatively broad for a
  same-day hold, and over-exclusion is safe
  (2026-05-06, `docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md`).
- Market-holiday stand-down on the NYSE calendar: no tournament, no email, a
  `market_holiday` skip doc only
  (2026-06-19, `docs/DECISIONS/2026-06-19-market-holiday-standdown.md`).

**Pool shaping:** every rail-cleared candidate is `assert_no_leakage`-checked,
hard-gated to **BULLISH only** (`BULLISH_ONLY=true`, owner-directed), then
soft edge-ranked and capped to the top `TOURNEY_POOL_CAP` = **12** (code
default, no env override)¹
(2026-06-11, `docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md`).
The per-candidate selection gates and the daily-cadence fallback were removed
2026-06-04 (`docs/DECISIONS/2026-06-04-bracket-tournament.md`).

¹ A 2026-06-12 note claimed the cap was raised to 50 via env. That was never
true of the live service. The live value is the code default 12.

**Two-tier liquidity floor** (`_liquidity_refresh_and_rank`, at the ~09:52 ET run):
- **Tier 1, early-print floor.** The `day` bar is date-validated in ET. A bar
  dated before today counts as a KNOWN 0 prints
  (2026-08-07, `docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md`).
  `PRINT_FLOOR_MIN`: code default 1. The owner adopted raising it to 25 on
  2026-08-19, not yet deployed (live env still 1 as of 2026-08-20). The adoption
  is recorded in the header of
  `docs/DECISIONS/2026-08-19-pool-liquidity-floor-and-cap-20.md`. That note's
  enrichment admission-floor design was NOT adopted.
- **Tier 2, live-OI floor.** Fresh open interest is re-fetched per candidate
  from Polygon at pick time. Candidates below `OI_FLOOR` are dropped
  (live env 1000, code default 200)
  (2026-06-25, `docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md`).
- **`FAILSOFT_RESTORE_MODE=none` (confirmed live):** a candidate that fails
  either floor never returns to the slate
  (2026-08-12, `docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md`).
- **`LIVE_FETCH_MIN_OK_FRAC=0.5` (confirmed live):** a run whose live read
  answers for under half the slate is DEGRADED, returns the input pool
  untouched, and cannot empty the slate.
- **No-pick path (fail-closed):** when both floors run to completion, the read
  is measured, and nothing clears, the slate is EMPTY. The notifier writes
  `skip_reason="no_liquid_candidates"` with its counts and emails the operator
  the stand-down. Replay says roughly one no-pick day per month.

## Tournament (`signal-judge`)
**`tournament_v1_3` / `JUDGE_PROMPT_VERSION=10`, `gemini-3.1-pro-preview`.**
Three independent brackets, each seeding the capped pool in randomized order and
reducing it in batches of ≤10 (top-2 advance) to a bracket winner. A consensus
winner across the 3 brackets sets `confidence` (3/3 high, 2/3 med, 1/3 low).
The judge sees a simple prompt + the daily report markdown + a per-contract
JSON, with stale scan-time `volume`/`OI` stripped and the live tradeability
fields (`early_volume`, `oi_build`, `live_oi`, `expected_liquidity`) included.
`quant.md` priors inject at the championship round only. **Fail-closed on any
tournament error:** no fallback path, no email, an empty-state `todays_pick`
(2026-06-04, `docs/DECISIONS/2026-06-04-bracket-tournament.md`).

Prompt lineage, one line: v7 `tournament_v1` (2026-06-04) → v8 `v1_1` liquidity
fields (2026-07-28) → v9 `v1_2` zero-prints wall (2026-08-07) → v10 `v1_3`
restored-flag rule (2026-08-12). `signal-judge/deploy.sh` pins the live version.

## Publication timing (canonical surface contract)
The notifier cron fires **~09:52 ET** so the 15-minute-delayed feed shows real
entry-day prints. The pick finalizes **~09:53–09:57 ET** and the operator +
subscriber email lands ~09:53–09:55. All surfaces reveal at the same moment.
There is no earlier access tier: paid subscribers pay for convenience, not
timing advantage.

The single source of truth is Firestore `todays_pick/{scan_date}`, written
exactly once per run, atomically, **before** the email is sent (if the write
raises, no email goes out). Downstream surfaces (webapp banner, subscriber
email fan-out) MUST read this doc without re-applying gate filters. The MCP has
**no pick-returning endpoint** by product rule and does not read this doc.

`skip_reason` values on `has_pick=false` days: `no_candidates_passed_gates`,
`regime_fail_closed`, `vix_backwardation`, `earnings_overlap_all_candidates`,
`earnings_calendar_unavailable`, `no_liquid_candidates` (both floors ran to
completion and nothing tradeable survived), `v5_4_unavailable`,
`v5_4_out_of_set`, `v5_4_mass_leakage`, `market_holiday`.

## Cohort + provenance
- `policy_version` is pinned `V7_1_TILTED_GIGO` and never mutated. A new policy
  gets a new string.
- Cohort start: `LIVE_COHORT_START_DATE` in `signal-notifier/main.py` (see
  Status). `cohort_stats/current` recomputes from the constant on every cron
  run. Ad-hoc refresh via `POST /refresh_stats`.
- Tournament provenance rides the retained `v5_4_*` keys (`v5_4_run_id`,
  `v5_4_justification`, `v5_4_confidence`, prompt-version and model keys) on
  every `has_pick=true` doc. `*_prompt_version` tracks `JUDGE_PROMPT_VERSION`
  (10 live). `*_model=gemini-3.1-pro-preview`.
- `policy_gate = ENRICHMENT_ONLY_NO_TRADER_GATE` on every current row.
  Historical `FALLBACK` rows remain separable in ledger analysis.

## Validation posture
- **No automated execution.** The operator trades live, discretionarily, with
  his own bankroll. The `forward_paper_ledger` cohort validates SELECTION.
- **15-closed-trade checkpoint** (operator plan, 2026-05-27): at 15 closed
  trades in the live cohort, run the evals + a diagnostic. This is a health
  check, not a gate.
- **Operator regime rule** (2026-05-09 audit): at 5 consecutive losses with no
  skipped days, pause picks and re-ask the regime question manually.
- Do not tune filters one at a time on small-N cohort noise.
- Do not modify `signals_labeled_v1` or `scripts/research/` (frozen).
- Do not add execution gates to the trader. Signal-quality gates live in
  enrichment and the notifier.
- Do not add a fallback for tournament errors. Fail-closed is intentional, and
  signal-judge uptime is the SLO.

## Phase 2 backlog
Deferred; each ships as its own decision note, not a silent parameter change:
- Sweep / block detection (needs tick-level trade classification)
- Aggressor side (bid vs ask lift, needs millisecond trade data)
- GEX / dealer positioning
- Regime-conditional sizing
