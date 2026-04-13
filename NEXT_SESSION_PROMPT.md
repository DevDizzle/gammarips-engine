# Next Session Prompt — Pick Up Cold

> **ACTIVE HANDOFF: 2026-04-12. This supersedes the 2026-04-08 handoff entirely (scroll down for infrastructure reference only).**

---

## 2026-04-12 — V4 FRESH START: no gates, collect everything, discover what wins

### TL;DR

V3.1 produced 29 trades in 7 weeks — "trading ghost." The 2026-04-12 research session identified why (upstream enrichment gate starving the pipeline) and then questioned whether the `premium_score` system even identifies winners. Answer: **it barely does.** Score=0 trades win 76.3% of the time vs score≥2 at 84% — a modest lift that costs you 1,547 trades. HEDGING and DIRECTIONAL have near-identical win rates (78.6% vs 77.3%). Individual flags are a mixed bag (`high_rr` helps, `bull_flow` and `high_atr` hurt). The premium scoring system is not reliably separating signal from noise.

**New philosophy: let everything through, trade it all, then use 30 days of execution data to discover what actually predicts winners via tree-based feature importance (XGBoost/SHAP).** The premium flags still get computed and stored — they just don't gate anymore. After 30 days, we run feature importance on the full enriched+outcome dataset to find the real thresholds that matter, which will inform a V5 alerting system.

**V4 deployed 2026-04-12.** Both services live, scheduler jobs active, first enrichment run triggered manually.

### Decisions made this session (locked)

1. **Enrichment filter: `overnight_score >= 1 AND recommended_spread_pct <= 0.10 AND directional UOA > $500K`.** The score floor drop (6 to 1) grows the candidate universe. Spread cap and UOA floor are applied at enrichment time — the "whale following" filter ensures we only enrich signals backed by institutional unusual options activity. ~70 tickers/day, ~9 minute enrichment runtime.

2. **No trader-side filters.** All signals that pass enrichment execute. Spread cap is enforced upstream at enrichment, not at the trader. Vol/oi floors removed — data showed they're anti-correlated with performance.

3. **DROP the `premium_score >= 2` gate.** Data shows score=0 trades win 76.3% vs score≥2 at 84% — the premium scoring system is not reliably separating winners from losers. HEDGING vs DIRECTIONAL win rates are nearly identical (78.6% vs 77.3%). Individual flags: `high_rr` helps (+8.7pp), `bull_flow` hurts (-5.3pp), `high_atr` hurts (-3.1pp), `hedge` is flat (+1.8pp). Premium flags still get computed and stored in the enriched table — they just don't gate trades anymore. They become features for post-hoc discovery.

4. **KEEP full Gemini with news grounding in enrichment.** `flow_intent`, `hedge`, and all premium flags still get computed and written to the enriched table. They're valuable as features for the discovery phase — they just don't gate execution.

5. **Bracket (+40/−25/2d), direction handling (both) stay.** The bracket execution mechanics are unchanged.

6. **No backfill. Fresh start.** New clean ledger table `forward_paper_ledger_v4_hold2`. V3 runs untouched as control.

7. **After 30 days: tree-based feature importance to discover what actually predicts winners.** Run XGBoost/Random Forest on the full V4 enriched+outcome dataset. Target = `is_win` or `bracket_result`. Features = all enriched fields (overnight_score, flow_intent, premium flags, spread, vol, oi, atr, price_change, etc). Use SHAP values for per-feature contribution and decision tree visualization for interpretable thresholds. This informs a V5 alerting system that gates on empirically-validated features instead of hand-picked flags.

### Architecture: separate Cloud Run services (V3 untouched)

V4 runs as **completely independent services** alongside V3. No shared code paths, no env-var branching, no risk of breaking V3 with a bad V4 deploy.

| | V3.1 (untouched) | V4 (new) |
|---|---|---|
| Enrichment service | `enrichment-trigger` | `enrichment-trigger-v4` |
| Enrichment table | `overnight_signals_enriched` | `overnight_signals_enriched_v4` |
| Enrichment gate | `overnight_score >= 6` | `overnight_score >= 1 AND spread <= 10% AND directional UOA > $500K` |
| Trader service | `forward-paper-trader` | `forward-paper-trader-v4` |
| Trader reads from | `overnight_signals_enriched` | `overnight_signals_enriched_v4` |
| Ledger table | `forward_paper_ledger_v3_hold2` | `forward_paper_ledger_v4_hold2` |
| Premium gate | `premium_score >= 2` | **None** (all enriched signals trade) |
| Vol/OI gate | `vol>=100 AND oi>=50 OR oi>=250` | **None** |
| Spread cap | None | `<= 0.10` (only execution filter) |
| Scheduler jobs | Existing (unchanged) | New V4 jobs |

Both pipelines read from the same upstream `overnight_signals` table (the scanner is shared). They diverge at enrichment.

### Deployed infrastructure (2026-04-12)

| Component | Service / Table | URL / Schedule |
|---|---|---|
| Enrichment service | `enrichment-trigger-v4` | `https://enrichment-trigger-v4-406581297632.us-central1.run.app` |
| Trader service | `forward-paper-trader-v4` | `https://forward-paper-trader-v4-406581297632.us-central1.run.app` |
| Enriched table | `overnight_signals_enriched_v4` | — |
| Ledger table | `forward_paper_ledger_v4_hold2` | — |
| Enrichment cron | `enrichment-trigger-v4-daily` | 05:30 ET Mon-Fri |
| Trader cron | `forward-paper-trader-v4-trigger` | 16:30 ET Mon-Fri |
| IV cache cron | `polygon-iv-cache-v4-daily` | 16:30 ET Mon-Fri |

### Next session checklist

1. **Verify first full automated run** (Monday 2026-04-14). Check `overnight_signals_enriched_v4` has rows from 05:30 ET enrichment. Check `forward_paper_ledger_v4_hold2` has rows from 16:30 ET trader. Confirm V3 tables unaffected.
2. **Monitor trade volume.** Expect 20-50+ trades/day with the loose gates. If significantly lower, investigate.
3. **After 30 days (2026-05-12):** If N >= 500, run tree-based feature importance (XGBoost/SHAP). If N < 500, extend to 60-90 days.
4. **If anything breaks:** V3 is untouched. Kill V4 scheduler jobs and investigate.

### Success criteria (30-day forward window)

- **Trade count:** V4 should produce significantly more trades than V3 (~4/week). With no premium/vol/oi gates and only spread ≤ 10%, expect 20-50+/week
- **Mean realized return:** track but don't panic on short-term. The whole point is collecting data, not optimizing return yet
- **Feature collection:** every enriched field (overnight_score, flow_intent, premium flags, spread, vol, oi, atr, price_change, etc) must be preserved in the ledger or joinable from the enriched table
- **Spread distribution:** all ≤ 10% by construction
- **V3 comparison:** V3 keeps running in parallel as a live control
- **N ≥ 500 target:** this is the minimum for meaningful tree-based feature importance (per existing rule: no ML on N<500). At 30+ trades/week, expect 120-200+ trades in 30 days. May need 60-90 days to reach N=500

### Phase 2 — Feature importance discovery (after N ≥ 500)

After collecting enough V4 execution data, run tree-based analysis to discover what actually predicts winners:

1. **Dataset:** Join `forward_paper_ledger_v4_hold2` with `overnight_signals_enriched_v4` on `recommended_contract` + `scan_date`. Target variable: `exit_reason` (TARGET vs STOP vs TIMEOUT) or binary win/loss
2. **Features:** overnight_score, flow_intent, premium_hedge, premium_high_rr, premium_bull_flow, premium_bear_flow, premium_high_atr, premium_score, recommended_spread_pct, recommended_volume, recommended_oi, direction, VIX_at_entry, SPY_trend_state, iv_rank_entry, underlying_return, price_change_pct, atr_normalized_move, mean_reversion_risk, catalyst_score, enrichment_quality_score
3. **Methods:**
   - XGBoost classifier → feature importance ranking (gain-based)
   - SHAP values → per-feature contribution with interaction effects
   - Single decision tree (depth 3-4) → interpretable threshold rules ("if spread < 5% AND overnight_score > 3 → 85% win")
   - Bootstrap validation (1000 resamples) → confidence intervals on feature importance rankings
4. **Output:** A ranked list of features that actually predict winners, with specific thresholds. This becomes the V5 gate — empirically validated, not hand-picked
5. **Alerting system:** The discovered thresholds inform real-time alerts: "this contract matches the winning pattern" vs "this one doesn't." Not a gate (V4 still trades everything) but a signal-quality score grounded in data

### What V4 inherits from V3 (unchanged)

| Thing | Status |
|---|---|
| Bracket (+40% TP / −25% SL) | Same |
| Hold days (2) | Same |
| Direction handling (both directions) | Same |
| Gemini with full news grounding | Same — flags still computed and stored for discovery |
| Entry time (15:00 ET on D+1) | Same |
| Upstream scanner (`overnight_signals`) | Shared — both pipelines read the same raw signals |

### What V4 changes vs V3

| Thing | V3.1 | V4 |
|---|---|---|
| Enrichment floor | `overnight_score >= 6` | `overnight_score >= 1` |
| Premium gate | `premium_score >= 2` | **None** — all enriched signals trade |
| Vol/OI gate | `vol>=100 AND oi>=50 OR oi>=250` | **None** |
| Spread cap | None | `<= 0.10` (enforced at enrichment) |
| UOA floor | None | Directional UOA > $500K (enforced at enrichment) |
| Philosophy | Pre-filter, then trade | Trade everything enrichment passes, discover patterns after |
| Enrichment service | `enrichment-trigger` | `enrichment-trigger-v4` (independent) |
| Trader service | `forward-paper-trader` | `forward-paper-trader-v4` (independent) |
| Enriched table | `overnight_signals_enriched` | `overnight_signals_enriched_v4` |
| Ledger table | `forward_paper_ledger_v3_hold2` | `forward_paper_ledger_v4_hold2` |

### What happens to V3 after 30 days

If V4 is working: sunset V3 (stop scheduler jobs, leave tables for reference).
If V4 is not working: kill V4, V3 continues unchanged. Zero risk to current pipeline.

### Key artifacts produced this session (still on disk, can be re-read)

- `/tmp/v4_backtest.parquet` — 7,480 bullish+liquid signals with D+1/D+2/D+3 daily bars fetched from Polygon. Entry model = D+1 open (faithful to real trader).
- `/tmp/v4_bracket_sim.parquet` — same dataset, per-day OHLC stored for day-by-day bracket walking. Used by the liquidity correlation analysis.
- `/tmp/score_vs_option_return_pilot.parquet` — the original pilot. **Contains the overnight-gap artifact — treat this parquet as suspect and do not cite.**
- `backtesting_and_research/score_vs_option_return_pilot.py` — original pilot. **Has the entry-model bug; useful only as reference.**
- `backtesting_and_research/score_vs_option_return_pilot_part2.py` — friction analysis on the bugged pilot.
- `backtesting_and_research/v4_backtest.py` — corrected backtest with D+1-open entry, 1d and 2d holds, friction applied.
- `backtesting_and_research/v4_bracket_sim.py` — the bracket simulator that matches the real V3 ledger mechanics. Useful template for building the trader backfill.
- `backtesting_and_research/liquidity_correlation.py` — the analysis that flipped my recommendation from "tighten vol/oi" to "cap spread." Read this before doubting the spread-cap decision.

### What the research showed — condensed

1. **The original pilot's "gate is useless" finding was a measurement artifact.** It used `recommended_mid_price` (scan-time after-hours mid) as entry, which secretly captured the overnight gap to D+1 open. The real trader enters at D+1 open and can't capture that gap. When re-run with realistic entry, the "edge" vanished and every bucket lost money on close-to-close. See `memory/project_pilot_entry_model_artifact.md`.
2. **The simulator is faithful.** The v4 bracket simulator reproduces the real V3 ledger's STOP = −25% and TARGET = +40% exactly. What differs between the sim and the real ledger is the universe selection (premium_score filter + Gemini's premium flags), not the execution mechanics.
3. **Volume and OI are anti-correlated with bracket outcome.** Counter-intuitive but consistent across every slice: higher liquidity = worse returns. Likely explanation: crowded high-vol names have their directional edge priced in before we see them. See `backtesting_and_research/liquidity_correlation.py` output.
4. **Spread is the only monotonic liquidity feature.** 0–5% spread bucket is positive (+1.1% mean, 28% win); 30–40% bucket is the graveyard (−14.5% mean, 15% win, 73% stop rate). 10% cap is defensible; 5% cap would be better but might shrink universe too much.
5. **Real V3 ledger cross-check:** 29 trades, weighted mean −0.6%, 24/29 bearish, exit distribution 13 STOP / 9 TIMEOUT / 7 TARGET / 1 INVALID_LIQUIDITY. Break-even, regime-appropriate bearish dominance.
6. **Premium scoring doesn't reliably separate winners.** On 2,273 resolved enriched trades: score=0 wins 76.3% (N=1,547), score=1 wins 78.2% (N=638), score≥2 wins 84.0% (N=81). The gate filters out the vast majority of trades for a modest lift. Individual flags: `high_rr` is the only strong predictor (+8.7pp, N=239); `hedge` is flat (+1.8pp); `bull_flow` (-5.3pp) and `high_atr` (-3.1pp) actually hurt. HEDGING vs DIRECTIONAL flow_intent: 78.6% vs 77.3% — essentially identical. Conclusion: stop pre-filtering with hand-picked flags, collect execution data, discover empirical thresholds.

### Hard constraints for next session (DO NOT violate)

- **Do NOT touch V3 code, config, tables, or scheduler jobs.** V3 runs untouched as a live control. All V4 work happens in the copied `-v4` service directories.
- **Do not propose backfilling historical data.** Explored exhaustively and abandoned — hedge flag can't be replicated without real-time news. Forward-only.
- **Do not propose ripping Gemini out of enrichment.** Premium flags still get computed and stored — they're features for the discovery phase. See `memory/project_hedge_flag_is_the_alpha.md`.
- **Do not add any execution gates besides spread ≤ 10%.** The entire point of V4 is to collect unfiltered execution data. No premium_score gate, no vol/oi gate. If you're tempted to add a filter, stop — that's what the Phase 2 discovery is for.
- **Do not run feature importance / ML until N ≥ 500.** Per existing rule. Track trade count weekly.
- **Do not treat bearish dominance as a flaw.** It reflects regime. See `memory/feedback_regime_and_direction.md`.
- **Do not skip the gammarips-review audit before deploy.** Mandatory per `.claude/rules/forward-paper-trader.md`.
- **Keep it simple.** See `memory/feedback_simplicity.md`. Copy dirs, edit configs, deploy, create scheduler jobs. That's it.

### Exact prompt to paste at session pickup

> Deploying V4 as a parallel pipeline alongside V3. V4 philosophy: no gates except spread ≤ 10%, collect everything, discover what wins after 30 days via tree-based feature importance. Read `NEXT_SESSION_PROMPT.md` top to bottom, then `MEMORY.md` and referenced files. The plan is 12 steps — copy service dirs, edit V4 configs (enrichment floor 6→1, DROP premium_score gate, DROP vol/oi gate, spread cap ≤10% as only filter, new tables), create BQ tables, decision doc, gammarips-review, deploy V4 services, create V4 scheduler jobs. V3 is untouched. No backfill. Execute the plan.

---

## 2026-04-08 handoff (historical — infrastructure facts still valid; gate posture SUPERSEDED)

## Read-first order

Paste this whole file into a fresh Claude Code conversation to resume where we left off. Read these in order before touching anything:

1. **`CLAUDE.md`** (repo root) — project bootstrap, subagents, current policy posture
2. **This file** — you're reading it
3. **`docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md`** — full rationale for the instrumentation pivot, data-source changes, and frozen-gate posture
4. **`docs/research_reports/BENCHMARKING_VALIDATION_V1.md`** — the 29-trade pre-war baseline against which all post-war numbers will be compared
5. **`docs/research_reports/INTELLIGENCE_BRIEF.md`** — the 2026-04-08 update section at the top, plus the H1–H9 open hypothesis list
6. **`docs/DECISIONS/2026-04-07-v3-1-liquidity-quality-gate.md`** — the frozen gate's rationale
7. **`docs/TRADING-STRATEGY.md`** — current canonical strategy doc, including the pre-committed hypotheses list

If you find yourself disagreeing with anything in these files, stop and ask before acting. These are the anchors.

---

## State as of 2026-04-08 (the day this file was written)

### What's deployed

- **Cloud Run service:** `forward-paper-trader`, revision `forward-paper-trader-00025-kvs`. Single container, two endpoints:
  - `POST /` — daily V3.1 paper trading. Cloud Scheduler job `forward-paper-trader-trigger` at 16:30 ET Mon-Fri.
  - `POST /cache_iv` — daily Polygon IVR cache refresh. Cloud Scheduler job `polygon-iv-cache-daily` at 16:30 ET Mon-Fri.
- **V3.1 gate (frozen):** `premium_score >= 2 AND ((recommended_volume >= 100 AND recommended_oi >= 50) OR recommended_oi >= 250)`.
- **Bracket (frozen):** `+40% target / −25% stop / 2-day hold`, 15:00 ET entry.
- **Data sources:** Polygon (minute bars, option chains, daily stock bars, stock snapshots), FRED (VIXCLS for VIX daily). **FMP is no longer used by `forward-paper-trader`** — the `FMP_API_KEY` secret mount was removed from `deploy.sh` on 2026-04-08.
- **Benchmarking helper:** `forward-paper-trader/benchmark_context.py`. Non-blocking — every fetch returns None on failure, trader writes NULL, never blocks a trade.

### BigQuery tables (persistent)

- `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2` — canonical ledger. All 10 benchmarking columns added + 29 pre-existing rows backfilled on 2026-04-08.
- `profitscout-fida8.profit_scout.polygon_iv_history` — new IVR cache, clustered by ticker, partitioned by as_of_date. First row written 2026-04-08 via smoke test (497 tickers, 496 with IV).
- `profitscout-fida8.profit_scout.overnight_signals_enriched` — unchanged, upstream signal source. Still 2026-02-18 → (present). This is the watchlist source for both the trader and the IVR cache.
- `profitscout-fida8.profit_scout.signals_labeled_v1` — frozen research table (V3 mechanics over 1563 historical signals). Not modified. Do not modify.

### Numbers at handoff (pre-war cohort, N=29)

From `current_ledger_stats.py` on 2026-04-08:

```
Option return (bracketed)          29   +2.91%   win 48.3%
Underlying return 1x (signed)      29   +0.36%   win 44.8%
SPY return over window             29   +0.01%   win 55.2%
Alpha: underlying - SPY            29   +0.35%   win 51.7%
```

**First three-way-positive (option, stock, alpha) in the entire research series.** SPY floor at zero means this is not beta capture. N=29 so CI still includes zero. See `BENCHMARKING_VALIDATION_V1.md` for the full writeup and non-conclusions.

### The single most important fact

**The Iran ceasefire ended the war regime on 2026-04-08.** Every trade in the ledger at time of writing has `entry_day <= 2026-04-08`. Every trade written after that is post-war. The war-regime environment was Iran shock (Feb 28), Strait of Hormuz closure (Mar 4), Brent $120, VIX peak 35.3, VIX term structure backwardation, record IV-RV spread. The post-war environment is expected to normalize (VIX drifting lower, VRP compressing, term structure contango). These are structurally different regimes. The next 4-6 weeks of data is the first real out-of-regime test the signal generator has ever had.

---

## What to do immediately on pickup (in this order)

### Step 1 — Verify the infrastructure is still running

Before anything else, confirm the trader and the IVR cache have been running daily. Claim: "if the cron jobs stopped, everything below is moot until they're fixed."

```sql
-- How many trades have been written since 2026-04-08?
SELECT COUNT(*) AS n_post_war, MIN(entry_day) AS first, MAX(entry_day) AS last
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
  AND entry_day >= '2026-04-09';
```

Expected: `n_post_war` should be somewhere between 15 and 40 depending on how many weeks elapsed.

```sql
-- How much IVR history do we have?
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT ticker) AS unique_tickers,
  MIN(as_of_date) AS first_day,
  MAX(as_of_date) AS last_day,
  COUNT(DISTINCT as_of_date) AS trading_days_covered,
  COUNTIF(atm_iv_30d IS NOT NULL) AS rows_with_iv
FROM `profitscout-fida8.profit_scout.polygon_iv_history`;
```

Expected: `first_day` around 2026-04-08, `last_day` within a day or two of today, `trading_days_covered` roughly matches the number of Mon-Fri days since 2026-04-08. If there's a gap of more than 2 days anywhere in the middle, the cache job is broken and that needs to be fixed before anything else.

```sql
-- Has iv_rank_entry started populating on new trades?
SELECT
  COUNT(*) AS n_trades,
  COUNTIF(iv_rank_entry IS NOT NULL) AS n_with_ivr,
  MIN(entry_day) FILTER(WHERE iv_rank_entry IS NOT NULL) AS first_ivr_day
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY');
```

Expected at ~4 weeks post-2026-04-08: `iv_rank_entry` is starting to populate around 2026-05-06 (20 trading days after cache go-live). At ~6 weeks it should be populating routinely. **Important:** IVR is still *diagnostic only*, not decision-grade, until the cache has 252 days. Do not test IVR hypotheses yet.

### Step 2 — Run the stats snapshot and the epoch split

```bash
python scripts/ledger_and_tracking/current_ledger_stats.py
```

Report the full output. Then run the epoch split:

```sql
SELECT
  CASE WHEN entry_day < '2026-04-09' THEN 'pre_war' ELSE 'post_war' END AS epoch,
  COUNT(*) AS n,
  ROUND(AVG(realized_return_pct) * 100, 2) AS option_mean_pct,
  ROUND(AVG(underlying_return) * 100, 2) AS stock_mean_pct,
  ROUND(AVG(spy_return_over_window) * 100, 2) AS spy_mean_pct,
  ROUND(AVG(underlying_return - spy_return_over_window) * 100, 2) AS alpha_pct,
  ROUND(COUNTIF(realized_return_pct > 0) / COUNT(*) * 100, 1) AS option_win_pct
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
GROUP BY epoch
ORDER BY epoch;
```

**Report the numbers. Do not yet interpret them.** Go to Step 3.

### Step 3 — Count trades against the N≥100 threshold

```sql
SELECT
  COUNT(*) AS total_trades,
  100 - COUNT(*) AS trades_remaining_to_threshold
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY');
```

If `total_trades < 100`, we are still in the accumulation period. You may run the diagnostic queries below, but **you may not modify the gate, run filter searches, or make any strategy changes**. The only permitted actions are: monitoring, reporting, fixing infrastructure breakages, and updating documentation.

If `total_trades >= 100`, you are permitted to run the pre-committed hypothesis tests in Step 4.

---

## Step 4 — Pre-committed hypothesis tests (ONLY if N ≥ 100)

These are the **only** questions permitted. Running any other candidate filter constitutes a new search and is not allowed until these four are settled. If none of these produce an actionable result, the answer is "accumulate more data," not "try a new hypothesis."

### Hypothesis 1 — Epoch split (pre-war vs post-war)

Already run in Step 2 above. The question is: **is the post-war epoch's mean option return, mean underlying return, and directional alpha meaningfully different from the pre-war epoch's?**

- If post-war is **three-way-positive** (option > 0, stock > 0, alpha > 0) at roughly the same scale as pre-war: the V3.1 gate expectancy is regime-general. Do not change the gate. Continue accumulation. Reassess at N=200.
- If post-war is **three-way-positive at a materially different scale** (e.g. 2× better, 2× worse): there is a real regime-conditional effect. Investigate what specifically changed (VIX bucket distribution, direction mix, HV bucket distribution) but **do not act on it** — a regime-conditional edge detected on one regime transition is still N=1 regime transition. Reassess at N=200.
- If post-war is **flat on option but negative on stock**: the options instrument is saving you but the signal has no directional edge. The positive option return is coming from bracket structure, not signal, which is fragile. Flag for deeper investigation but do not deploy.
- If post-war is **negative on everything**: the pre-war three-way-positive was regime-dependent. The V3.1 gate does not generalize. This is the scenario that justifies a gate narrowing or a pause — but both require a new decision note and a `gammarips-review` audit before any deploy.

### Hypothesis 2 — VIX < 25 vs ≥ 25 (only if `N_post_war >= 30`)

Both the labeled cohort and the 29-trade pre-war cohort flagged a VIX-25 breakpoint. Does it hold in the post-war epoch?

```sql
SELECT
  CASE WHEN VIX_at_entry < 25 THEN 'lt_25' ELSE 'gte_25' END AS vix_bucket,
  COUNT(*) AS n,
  ROUND(AVG(realized_return_pct) * 100, 2) AS option_mean_pct,
  ROUND(AVG(underlying_return) * 100, 2) AS stock_mean_pct,
  ROUND(AVG(underlying_return - spy_return_over_window) * 100, 2) AS alpha_pct
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
  AND entry_day >= '2026-04-09'
  AND VIX_at_entry IS NOT NULL
GROUP BY vix_bucket
ORDER BY vix_bucket;
```

- If the VIX-25 split persists: the breakpoint is regime-general. Adding `VIX_at_entry < 25` to the gate becomes a candidate — **but only after a new decision note, a `gammarips-review` audit, and verification that the post-war VIX distribution is not too narrow to support the split in the first place** (e.g. if the post-war regime has VIX 15-22 throughout, the split is untestable regardless of outcome).
- If the split does not persist: the earlier pattern was regime-dependent. Drop the VIX-25 candidate and do not re-test it.

### Hypothesis 3 — Underlying-vs-option return gap

The labeled cohort showed an instrument bleed of −2.93 pp/trade (option mean minus stock mean). The V3.1 pre-war cohort flipped this to +2.55 pp/trade (option helping). Which side is the post-war cohort on?

```sql
SELECT
  ROUND(AVG(realized_return_pct) * 100, 2) AS option_mean_pct,
  ROUND(AVG(underlying_return) * 100, 2) AS stock_mean_pct,
  ROUND((AVG(realized_return_pct) - AVG(underlying_return)) * 100, 2) AS instrument_gap_pct
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ('SKIPPED', 'INVALID_LIQUIDITY')
  AND entry_day >= '2026-04-09';
```

- If `instrument_gap_pct > 0`: options are continuing to help. Consistent with the pre-war cohort. Continue accumulation.
- If `instrument_gap_pct < 0`: the instrument bleed is back. The pre-war option-helping result was regime-specific. This justifies revisiting the debit-vertical / deep-ITM alternative experiments from the 2026-04-07 Deep Research brief (H5, H6 in `INTELLIGENCE_BRIEF.md`).

### Hypothesis 4 — IVR is DEFERRED

The IVR cache will have ~20-40 trading days of history at pickup, **not** the 252 days needed for decision-grade IV Rank. Any `iv_rank_entry` values at pickup are diagnostic only. Do not test IVR hypotheses until the 12-month mark (~2027-04-08). Document this in every report but do not act on it.

---

## What NOT to do on pickup

These are not suggestions; they are hard constraints.

- **No filter searches.** Do not rank candidate filters against the ledger. Do not run combinatorial sweeps. If you find yourself thinking "let me try X threshold on feature Y," stop and re-read this file. The previous session spent two weeks in that loop and produced nothing.
- **No bracket sweeps.** 840 variants have been exhausted on the labeled cohort. Post-war data is not a new domain for bracket search — it's a test of the existing bracket.
- **No ML models on N < 500.** Feature-importance rankings from XGBoost on 50-100 trades are pure noise. The label columns to never include are listed in `.claude/agents/gammarips-researcher.md`.
- **No premature gate narrowing.** Even if VIX < 25 looks decisive on post-war data, a single-regime-transition test is N=1 regime transition. Narrowing the gate off of one data point is exactly the mistake the previous session made repeatedly.
- **No retroactive IVR backfill.** The cache has no pre-2026-04-08 history. Trying to synthesize IVR for pre-war trades would poison the epoch comparison.
- **No new data sources** without user approval. The FMP→FRED+Polygon switch was a deliberate architectural decision; introducing a new vendor without a plan creates drift.
- **No changes to `signals_labeled_v1`.** Frozen research table. Do not rebuild, do not add columns, do not re-label. Any new research is against the live ledger.
- **No pressure to produce a conclusion.** If the numbers are ambiguous, the right answer is "accumulate more data, report the numbers, recommend another revisit at N=200." A non-conclusion is a valid outcome and often the correct one.

---

## Decision tree for gate changes

| Post-war cohort pattern | Action |
|---|---|
| Three-way-positive at similar scale to pre-war | **Gate stays, accumulate more.** Reassess at N=200. |
| Three-way-positive at materially different scale | **Gate stays, accumulate more.** Document the regime-conditional effect. Reassess at N=200. |
| Flat on stock, positive on alpha | **Accumulate more.** Flag as "signal may be beta-dependent." Do not change gate. |
| Flat everywhere | **Accumulate more.** The null hypothesis is alive. |
| Negative on both stock and alpha | **Investigate but do not deploy.** Candidate: narrow the gate. Requires: new decision note + `gammarips-review` audit + user sign-off. |
| Positive on option, negative on stock | **Instrument-bleed thesis is back.** Debit-vertical experiment becomes priority. Still requires new decision note before any gate change. |

No single result in any column of this table permits immediate deployment of a gate change. Every path either stays or routes through a decision note + review cycle. This is intentional.

---

## Handoff dataset commands (copy/paste ready)

```bash
# Quick health check
python scripts/ledger_and_tracking/current_ledger_stats.py

# How many days of IVR history?
bq query --use_legacy_sql=false '
SELECT
  COUNT(DISTINCT as_of_date) AS days_covered,
  MIN(as_of_date) AS first_day,
  MAX(as_of_date) AS last_day,
  COUNT(DISTINCT ticker) AS unique_tickers
FROM `profitscout-fida8.profit_scout.polygon_iv_history`
'

# Epoch split
bq query --use_legacy_sql=false '
SELECT
  CASE WHEN entry_day < "2026-04-09" THEN "pre_war" ELSE "post_war" END AS epoch,
  COUNT(*) AS n,
  ROUND(AVG(realized_return_pct) * 100, 2) AS opt_mean,
  ROUND(AVG(underlying_return) * 100, 2) AS stock_mean,
  ROUND(AVG(spy_return_over_window) * 100, 2) AS spy_mean,
  ROUND(AVG(underlying_return - spy_return_over_window) * 100, 2) AS alpha
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3_hold2`
WHERE exit_reason NOT IN ("SKIPPED", "INVALID_LIQUIDITY")
GROUP BY epoch
ORDER BY epoch
'

# Manual trigger for the paper trader on a specific scan_date
curl -X POST https://forward-paper-trader-406581297632.us-central1.run.app/ \
  -H "Content-Type: application/json" \
  -d '{"target_date": "2026-04-15"}'

# Manual trigger for the IVR cache refresh
curl -X POST https://forward-paper-trader-406581297632.us-central1.run.app/cache_iv

# Check Cloud Scheduler status
gcloud scheduler jobs list --project=profitscout-fida8 --location=us-central1

# Recent logs from the trader
gcloud run services logs read forward-paper-trader \
  --project=profitscout-fida8 --region=us-central1 --limit=50
```

---

## Open items and risks

- **IVR cache health.** If `polygon-iv-cache-daily` silently fails for several days, the cache will have gaps. The pickup cache-health query (Step 1) is the canary. A gap of more than 2 consecutive days is actionable — check Cloud Run logs for `/cache_iv` failures and re-trigger manually via the curl command above. Gaps of 1-2 days are acceptable (Polygon has occasional outages).
- **Post-war direction imbalance.** The pre-war cohort was 26 bearish / 3 bullish. If the post-war cohort is 3 bearish / 26 bullish (or similarly imbalanced in the opposite direction), cohort-level means will shift for reasons that have nothing to do with gate quality. Always report the direction breakdown alongside the main numbers.
- **INVALID_LIQUIDITY rate.** If the post-war cohort has a higher rate of INVALID_LIQUIDITY exits than the pre-war cohort, that suggests either a Polygon data issue or a regime-specific liquidity change. Flag it but do not act on it.
- **BigQuery storage costs.** `polygon_iv_history` accumulates ~500 rows/day. Over a year, ~120k rows, ~5 MB. Trivial. Over 5 years, 25 MB. Still trivial. No action needed.
- **Cloud Run revision count.** Each redeploy bumps the revision. Past revisions can be listed with `gcloud run revisions list --service=forward-paper-trader --project=profitscout-fida8 --region=us-central1`. Rollback is `gcloud run services update-traffic forward-paper-trader --to-revisions=REVISION_NAME=100 --project=profitscout-fida8 --region=us-central1`.

---

## Things I (the 2026-04-08 me) want the next-session-me to know

1. **The user made a commitment on 2026-04-08 to stop pivoting.** The previous few weeks of work oscillated between filter candidates and the user called it out: "we keep jumping around and I can't get a consistent take." Respect that. Your default action is **no action** unless the data clearly demands one.
2. **The three-way-positive on 29 trades is a hypothesis, not a finding.** The instrumentation was built specifically so that it becomes a finding (or a refutation) with more data. Do not cite it as validation. Do not deploy based on it.
3. **The war ending on 2026-04-08 is the single most important fact in the research history.** Every prior analysis was contaminated by the Iran shock. The post-war data is the first clean domain we have. Treat it with proportional care. The pickup session's job is to use the cleanest possible methodology (pre-committed hypotheses, epoch split, N ≥ 100 threshold) because this dataset is too precious to waste on another filter search.
4. **The instrumentation is deliberately non-blocking.** If you see a null in any benchmarking column, it means an external fetch failed, not that the trader is broken. Check logs, but do not assume the trader itself is damaged.
5. **If you find yourself about to run a new script that ranks candidates on the ledger, stop.** Instead: run the pre-committed hypothesis tests from Step 4 (if N ≥ 100), or run the monitoring query and wait longer (if N < 100). Those are the only two things this session is permitted to do.
6. **The user's income goal is $5k/month consistent, not home runs.** At the current run rate and the pre-war cohort's +2.91% per trade, that requires either position size ~$10k/trade or ~170 trades/month. Both are achievable, neither is urgent. Scaling position size is the correct lever; loosening the gate to get more trades is the exact mistake we just spent a session diagnosing.
7. **If the post-war numbers look like a disaster, do not panic-change anything.** The disaster scenario is: post-war three-way-negative with no positive subset visible. In that case, the right action is (a) document it, (b) write a decision note proposing either gate narrowing or a pause, (c) trigger `gammarips-review`, (d) get user sign-off before any deploy. Never deploy a reaction.
8. **If the post-war numbers look like a triumph, do not scale anything.** The triumph scenario is: post-war three-way-positive at similar scale to pre-war. In that case, the right action is (a) document it, (b) continue accumulation to N=200, (c) only then consider scaling position size with user sign-off. Never scale off of a single regime-transition result.

## Things the user wants you to optimize for

- **Consistency over cleverness.** Don't "improve" things that are working. Don't add features the plan didn't ask for. Don't rank filters.
- **Honest non-conclusions.** If the data doesn't say anything, say "the data doesn't say anything" clearly. Don't round ambiguity into a narrative.
- **Terse, direct reports.** Lead with the numbers, not the context. The user has good instincts and doesn't need hand-holding.
- **Safety first on the production path.** The trader is now writing valuable self-benchmarked data. Any change to `forward-paper-trader/main.py` that could drop a benchmarking column is a regression, not a fix.

---

## Appendix — files to know about

| File | Purpose |
|---|---|
| `forward-paper-trader/main.py` | Main trader, now with `/cache_iv` endpoint and inline benchmarking writes |
| `forward-paper-trader/benchmark_context.py` | Non-blocking helper: FRED VIX, Polygon chain, HV-20d, SPY cache, price locators, IVR BQ query |
| `forward-paper-trader/deploy.sh` | Cloud Run deploy, no more FMP secret |
| `scripts/ledger_and_tracking/current_ledger_stats.py` | **Weekly read-only monitor. Run this, do not modify.** |
| `scripts/ledger_and_tracking/backfill_benchmarks_v1.py` | One-shot backfill of the 29 pre-instrumentation rows. Already executed. Keep for posterity. |
| `scripts/ledger_and_tracking/create_polygon_iv_history.py` | DDL for the IVR cache table. Already executed. |
| `docs/DECISIONS/2026-04-08-ledger-benchmarking-and-fmp-retirement.md` | Full rationale for this session's architectural decisions |
| `docs/research_reports/BENCHMARKING_VALIDATION_V1.md` | The 29-trade pre-war baseline report |
| `docs/research_reports/UNDERLYING_VS_OPTIONS_V1.md` | The original 1563-row labeled-cohort underlying vs options relabel |
| `docs/research_reports/INTELLIGENCE_BRIEF.md` | Top-of-stack research state; includes the 2026-04-08 update |
| `docs/TRADING-STRATEGY.md` | Strategy doc with pre-committed hypotheses section |
| `docs/DATA-CONTRACTS.md` | Schema for `forward_paper_ledger_v3_hold2` and `polygon_iv_history` |

## Appendix — the exact prompt to paste at pickup

> I'm picking up the GammaRips work cold. The previous session (2026-04-08) instrumented the forward paper ledger with inline benchmarking columns, built a Polygon IVR cache job, switched VIX from FMP to FRED, and froze the V3.1 gate for an accumulation period of 4-6 weeks. The war ended 2026-04-08. I want to run the Step 1 health checks from `NEXT_SESSION_PROMPT.md`, then Step 2 (stats snapshot + epoch split), then report what I find before deciding anything. Do **not** run any filter searches, feature rankings, or gate tuning. Follow the decision tree in the same file.

The prompt above is deliberately terse. If the claude instance on pickup tries to do more than Steps 1-3 before reporting back, that is a violation of this handoff and should be corrected immediately.
