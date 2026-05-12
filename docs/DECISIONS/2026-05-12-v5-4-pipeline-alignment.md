# 2026-05-12 — V5.4 pipeline alignment: V5.4-only ledger + Scenario C gate relaxation

## Decision

Two surgical changes to resolve the picker-starvation + ledger-mislabeling pair exposed by the first week of post-promotion V5.4 operation:

1. **V5.4-only ledger.** `forward-paper-trader` simulates ONLY the ticker named in `todays_pick/{scan_date}` instead of fanning out across every row in `overnight_signals_enriched`. The ledger writes at most one row per scan_date (one trade row OR one skip row).
2. **Scenario C gate relaxation in `signal-notifier`.** Three knobs are widened to un-starve the V5.4 picker: `OI_MIN` 20→10, `VOL_MIN` 100→50, `DTE_MAX` 30→45. Moneyness, V/OI ratio, and the earnings filter are unchanged (literature-locked).

These supersede the implicit "trader writes research fanout" pattern that has been in place since V5.3 launch — it predated V5.4's promotion-to-canonical and quietly survived the 2026-05-08 retirement, mislabeling ~70 enriched rows/day as `policy_version=V5_4_AGENT_RANKER` even though only one was the actual V5.4 pick.

Full pipeline-alignment plan: `~/.claude/projects/-home-user-gammarips-engine/memory/project_v5_4_pipeline_alignment_2026_05_12.md`.

## Why now

Two problems both surfaced in the first 3 V5.4 scan dates (5/8 Fri, 5/9 Sat-zero, 5/11 Mon):

**Problem A — ledger mislabeling.** `forward_paper_ledger` was filling with ~70 rows/day under `policy_version=V5_4_AGENT_RANKER`. Only one was the V5.4 pick. The "official pick" had to be identified by ticker JOIN against `todays_pick/{scan_date}`, and `cohort_stats/current` was scoped to `policy_version` alone — so the public live-stats panel and the 30-trade DoD gate were both anchored to research fanout, not to actual V5.4 decisions. Process integrity violation: the ledger was no longer a record of V5.4 performance, it was V5.3-shaped research data with V5.4 metadata.

**Problem B — picker starvation.** Researcher funnel analysis of the 22 scan dates with V5.4-era gates (DTE 7-30 + OI/vol floors + V/OI + moneyness + earnings + VIX≤VIX3M) showed:

- Median candidates surviving the gate stack: **1**
- Distribution: **68% of days had ≤1 candidate**; only 22.7% had ≥3
- Zero-pick days (dark): **31.8%**

The V5.4 Picker's value-add (ranking among options) only operates when the candidate set has at least ~3 entries; a 1-candidate day is mechanically a deterministic forward-pick of whatever cleared the gates. The picker is currently doing little more than gate-pass acknowledgement.

Net effect: V5.4 has been the canonical strategy for 4 calendar days and the ledger contains zero V5.4-only rows that are actually V5.4 decisions, and the picker has had ~1 day in 5 where it actually ranked.

## Five-scenario funnel projection

Researcher swept the relaxable knobs across 22-day sample (one row per scan date, post earnings+VIX filters):

| Scenario | OI_MIN | VOL_MIN | V/OI | Money | DTE_MAX | Median candidates | % days >=3 | % zero-pick |
|---|---|---|---|---|---|---|---|---|
| A (current) | 20 | 100 | 2.0 | 5-10% | 30 | 1 | 22.7% | 31.8% |
| B (DTE only) | 20 | 100 | 2.0 | 5-10% | 45 | 1 | 27.3% | 27.3% |
| **C (chosen)** | **10** | **50** | **2.0** | **5-10%** | **45** | **2** | **50.0%** | **22.7%** |
| D (drop V/OI) | 10 | 50 | 1.5 | 5-10% | 45 | 3 | 63.6% | 18.2% |
| E (widen money) | 10 | 50 | 2.0 | 5-15% | 45 | 3 | 68.2% | 13.6% |

## Three locked decisions

| Question | Resolution |
|---|---|
| Which scenario? | **C.** Achieves the "median >=3" goal (just) while preserving every literature-locked invariant. |
| Why not D (drop V/OI to 1.5)? | **Preserve flow-conviction signal.** V/OI > 2 is the strongest single feature in the [V5.3 lit audit](2026-05-06-paper-trader-reset-and-stats-surface.md) and the [V/OI-first ranker pivot](2026-05-01-ranker-v2-voi-first.md). Top-1 win-rate flipped from 17% (dollar-volume primary) to 80% (V/OI primary) on the V5.3 cohort. Relaxing it for picker yield is a direct trade against the strongest live alpha signal we have. Revisit only at N>=15 V5.4 closes if dark-day rate is still >20%. |
| Why not E (widen moneyness)? | **Moneyness is literature-locked.** Aretz et al. 2023 RoF documents the deep-OTM EV cliff above ~10% on 9-DTE contracts; Augustin et al. 2022 JFM shows informed traders prefer slightly OTM, not deep-OTM, because B/A spreads scale inversely with price. The 5-10% band is the explicit output of the H12 lit audit ([2026-05-06](2026-05-06-lit-audit-h11-h12-spread-moneyness.md)). Widening to 5-15% would re-open the lottery zone. |

## Structural ceiling — moneyness alone

Even under Scenario C, **~23% of scan dates are structurally dark before any relaxable gate fires** — i.e., zero tickers in the universe have any contract in the 5-10% OTM band on a given day. The Apr 10-16 stretch was 5 consecutive dark days under every scenario. If the operator later targets <20% dark-day rate, the only remaining lever is moneyness, which is literature-locked. The honest answer at that point is "the strategy's natural cadence is 3-4 trades/week, not 5."

## N=30 timeline shift

The 30-closed-trade DoD gate ([finished-definition](../../CLAUDE.md), [deferred-alpaca-agent](2026-05-09-DEFERRED-alpaca-agent-execution.md)) was previously trivially satisfiable: under fanout, ~70 rows/day with `policy_version=V5_4_AGENT_RANKER` meant N=30 lands in ~3 calendar days (already hit by 2026-05-11). Under the V5.4-only ledger contract, N=30 is one actual V5.4 trade per non-dark day, projected ~6 weeks at the Scenario C cadence.

All references to "ledger N>=30 trigger" in `project_deferred_alpaca_agent.md` and `project_finished_definition.md` now mean V5.4-only picks (one row per scan_date max), not research fanout rows. The timeline reset is intentional — it forces 30 days of actual V5.4 decisions before any park-mode → active-mode transition.

## What V5.4-only ledger means in practice

- `forward_paper_ledger` row count drops ~70/day → 1/day max.
- Skip rows (`is_skipped=True`) replace zero-row days. Every scan_date that completes its hold window produces exactly one row, classified as one of:
  - Trade row (`is_skipped=False`, `exit_reason` in {STOP, TRAIL, TARGET, TIMEOUT, INVALID_LIQUIDITY}).
  - Skip row with `exit_reason=SKIPPED` and `skip_reason` in:
    - `no_candidates_passed_gates` / `regime_fail_closed` / `vix_backwardation` / `earnings_overlap_all_candidates` / `earnings_calendar_unavailable` / `v5_4_unavailable` / `v5_4_out_of_set` / `v5_4_mass_leakage` (mirrored from `todays_pick.skip_reason`)
    - `NO_TODAYS_PICK_DOC` (signal-notifier never ran for this scan_date)
    - `TODAYS_PICK_FETCH_FAILED` (Firestore unreachable — trader fails closed, doesn't fall back to fanout)
    - `PICK_NOT_IN_ENRICHED` (todays_pick names a ticker but no enriched row exists — shouldn't happen in normal operation)
- `cohort_stats/current` query (in `signal-notifier/compute_and_write_cohort_stats`) already filters `COALESCE(is_skipped, FALSE) = FALSE` and `realized_return_pct IS NOT NULL`, so skip rows are excluded from win-rate / ROI math without any signal-notifier change. The denominator becomes meaningful (V5.4 trades only) instead of misleading (fanout).
- Research fanout data is **DROPPED** from the ledger. Anyone needing the full enriched-signal universe must re-derive from `overnight_signals_enriched` directly.
- Backfill via `POST / {"target_date": "YYYY-MM-DD"}` still works: the trader looks up `todays_pick/{historical_scan_date}` for past dates the dual-write covers (signal-notifier writes under both `scan_date` and `entry_day` keys per the [dual-write contract](../../CLAUDE.md)). Historical scan dates without a `todays_pick` doc write a `NO_TODAYS_PICK_DOC` skip row.

## What Scenario C does NOT change

- `VOL_OI_MIN = 2.0` — strongest flow-conviction signal. Revisit only at N>=15 V5.4 closes.
- `MONEYNESS_MIN/MAX = 0.05/0.10` — literature-locked (Aretz 2023 RoF / Augustin 2022 JFM / H12 audit).
- Earnings overlap exclusion — literature-locked (De Silva 2026 / Cao-Han 2013).
- VIX <= VIX3M regime gate.
- Spread <= 8% (enrichment-trigger).
- Directional UOA > $500K (enrichment-trigger).
- Trader mechanics: entry 10:00 ET day-1, stop -60%, target +80%, trail -25% off peak @ +30% trigger, hold 3 trading days, exit 15:50 ET day-3, STOP wins on ambiguous bars.
- Composite weights 60/25/15 (flow/regime/narrative).
- Picker prompts are bumped to **scorer_v5 / picker_v4** in this same change (the prior `scorer_v4` / `picker_v3` files are retained for audit). The new files widen every internal DTE reference from 7-30 to 7-45 so guidance matches the relaxed `signal-notifier` hard gate, and `SCORER_PROMPT_VERSION` / `PICKER_PROMPT_VERSION` are bumped to `5` / `4` respectively for cohort attribution on `signal_ranker_runs`. Composite weights and ITM hard cap unchanged.

## Deferred (with revisit triggers)

| Item | Trigger to revisit |
|---|---|
| V/OI relaxation (2.0 → 1.5) | If dark-day rate >20% on N>=15 V5.4 closes despite Scenario C. |
| Moneyness widening (5-10% → 5-15%) | Requires literature re-audit (Aretz / Augustin reread) — NOT a data-driven knob. |
| Few-shot Picker exemplars | At N>=15 closed V5.4 trades (~mid-July). See [2026-05-09-DEFERRED-few-shot-picker-exemplars.md](2026-05-09-DEFERRED-few-shot-picker-exemplars.md). |
| 5-consecutive-losses pause | Active. See [methodology audit](../../CLAUDE.md). |

## Edits

| File | Change |
|---|---|
| `forward-paper-trader/main.py` | New `_fetch_todays_pick` + `_build_skip_record` + `_write_ledger_records` helpers. `run_forward_paper_trading` rewritten: read `todays_pick/{scan_date}` first, single-row simulation if `has_pick=True`, single skip row otherwise. Old fanout SELECT + dedup loop + per-row iteration removed. Mechanics block (bar walk, trail, benchmarking) unchanged. |
| `signal-notifier/main.py` | `OI_MIN = 20 → 10`. `VOL_MIN = 100 → 50`. `DTE_MAX = 30 → 45`. Comments above each constant updated to cite this decision doc. |
| `signal-ranker/prompts/scorer_v5.md` (NEW) | Copy of `scorer_v4.md` with all 4 internal `7-30` DTE references widened to `7-45`. Calibration anchor at line 58 now reads `DTE in [7, 45]` (with `[7, 30]` called out as the still-ideal lower half). Line 18 keeps the historical context that the band was widened 2026-05-12 from 7-30. The `>45 DTE` soft-gamma penalty is unchanged. |
| `signal-ranker/prompts/picker_v4.md` (NEW) | Copy of `picker_v3.md` with all 3 internal `7-30` DTE references widened to `7-45` (preamble, `high`-confidence definition, structure tiebreaker). Lower half [7, 30] still flagged as ideal within the band. |
| `signal-ranker/app/agent.py` | `tools.load_prompt("scorer_v4.md")` → `"scorer_v5.md"`. `tools.load_prompt("picker_v3.md")` → `"picker_v4.md"`. Mass-leakage comment reference bumped to `scorer_v5.md:29`. Picker docstring file reference bumped to `picker_v4.md`. |
| `signal-ranker/app/tools.py` | Default `SCORER_PROMPT_VERSION` `4 → 5`, `PICKER_PROMPT_VERSION` `3 → 4`. These are emitted to `signal_ranker_runs` per row for cohort attribution. |
| `signal-ranker/deploy.sh` | Env vars `SCORER_PROMPT_VERSION=4 → 5`, `PICKER_PROMPT_VERSION=3 → 4`. New change-log comment added above the env-vars line. |
| `CLAUDE.md` | Current-policy paragraph updated to mention V5.4-only ledger and Scenario C gate values; new decision doc added to the source-of-truth list. |
| `docs/TRADING-STRATEGY.md` | DTE band line updated 7-30 → 7-45 with widening rationale + new prompt-line anchors (`scorer_v5.md:18` / `picker_v4.md:24`). |
| `CHEAT-SHEET.md` | Filter list items 7-8 (OI 20→10, vol 100→50) and new item 9 (DTE 7-45) reflect Scenario C. |

## Replaces / supersedes

- The implicit "trader writes research fanout" pattern carried over from V5.3.
- The `DTE_MAX = 30` from [2026-05-11 leakage-fail-closed-and-dte-gate](2026-05-11-leakage-fail-closed-and-dte-gate.md) — both the hard `signal-notifier` gate AND the scorer/picker prompt guidance widen from 7-30 to 7-45 in this same change (new `scorer_v5.md` / `picker_v4.md`; `SCORER_PROMPT_VERSION=5`, `PICKER_PROMPT_VERSION=4`).
- The `scorer_v4` / `picker_v3` prompt versions promoted on [2026-05-09](2026-05-09-moneyness-fix-and-trading-context-prompts.md) — superseded by `scorer_v5` / `picker_v4` here. Old prompt files retained on disk for audit trail (matches the v1/v2/v3 retention pattern).

## Status — NOT DEPLOYED (audit pending)

Diffs produced 2026-05-12. `gammarips-review` audit MUST pass before any service is deployed.

## Deploy procedure

Execute strictly in the order below. Steps 1 and 5 are operator-run (not part of `deploy.sh`); they must not be skipped.

1. **Pre-deploy: purge the fanout-era V5.4-mislabeled rows.** ~350 rows written between scan_date 2026-05-08 and 2026-05-12 carry `policy_version=V5_4_AGENT_RANKER` because the trader was still fanning out under the V5.4 label (Problem A above). They poison `cohort_stats/current` and inflate the N=30 DoD gate. Run against BigQuery (operator console, NOT a script in `scripts/ledger_and_tracking/` — that directory is read-only per `.claude/rules/scripts-ledger.md`):

   ```sql
   DELETE FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
   WHERE scan_date BETWEEN '2026-05-08' AND '2026-05-12'
     AND policy_version = 'V5_4_AGENT_RANKER';
   ```

   Capture and record the deleted row count. Expected: ~350. If the count diverges materially from that estimate, STOP and re-audit before proceeding.

   **Sanity check before the DELETE:** the ledger was truncated 2026-05-08 when V5.3 was retired (see `project_v5_4_live.md` memory), so no V5.4-labeled rows should exist before that date. Confirm with:

   ```sql
   SELECT scan_date, COUNT(*) AS n
   FROM `profitscout-fida8.profit_scout.forward_paper_ledger`
   GROUP BY scan_date
   HAVING n > 1
   ORDER BY scan_date;
   ```

   This returns one row per scan_date that has more than one ledger row. Under the V5.4-only ledger contract every scan_date should have exactly one row (one trade OR one skip). If a scan_date earlier than 2026-05-08 shows `n > 1`, that is unexpected — investigate before extending the DELETE.

2. **Deploy `signal-notifier`.** The relaxed `OI_MIN=10`, `VOL_MIN=50`, `DTE_MAX=45` gates must be live before the next 07:30 ET cron writes a `todays_pick/{scan_date}` doc — otherwise the trader will block on a stale doc.

   ```bash
   cd /home/user/gammarips-engine/signal-notifier && bash deploy.sh
   ```

3. **Deploy `signal-ranker`.** The new `scorer_v5.md` / `picker_v4.md` prompt files ship in the Cloud Run build context (they live under `signal-ranker/prompts/` and are loaded via `tools.load_prompt`). Env vars `SCORER_PROMPT_VERSION=5` and `PICKER_PROMPT_VERSION=4` are baked into the deploy by `deploy.sh`. After deploy, hit the service and confirm both prompts loaded and version labels match.

   ```bash
   cd /home/user/gammarips-engine/signal-ranker && bash deploy.sh
   ```

4. **Deploy `forward-paper-trader`.** The V5.4-only ledger contract must go live after `signal-notifier` so the trader's first new run reads a fresh doc written under the relaxed gate stack.

   ```bash
   cd /home/user/gammarips-engine/forward-paper-trader && bash deploy.sh
   ```

5. **Post-deploy backfill (2026-05-08 only).** The 2026-05-08 scan_date's 3-day hold window has fully closed (entry 2026-05-09, exit 2026-05-13 by ledger calendar), so the trader can simulate it now under the V5.4-only contract and produce exactly one ledger row. The 5/11 and 5/12 scan_dates have hold windows that have NOT fully closed (entries 5/12 and 5/13, exits 5/14 and 5/15) — the daily 16:30 ET cron will pick them up naturally on those exit dates, so do NOT manually backfill them.

   ```bash
   TRADER_URL="$(gcloud run services describe forward-paper-trader \
     --project=profitscout-fida8 --region=us-central1 --format='value(status.url)')"
   curl -X POST "${TRADER_URL}/" \
     -H "Content-Type: application/json" \
     -d '{"target_date": "2026-05-08"}'
   ```

6. **Validate the ledger contract.** After backfill, confirm one-row-per-scan_date and that `policy_version` is consistent. Operator console (BQ), not a script:

   ```bash
   bq query --nouse_legacy_sql \
     "SELECT scan_date, ticker, policy_version, exit_reason, realized_return_pct \
      FROM \`profitscout-fida8.profit_scout.forward_paper_ledger\` \
      WHERE scan_date >= '2026-05-08' \
      ORDER BY scan_date"
   ```

   Expected: at most one row per scan_date. 2026-05-08 will be a trade or skip row; 2026-05-11 and 2026-05-12 will still be empty until their respective hold-window exit dates (5/14 and 5/15). After 5/15, every scan_date from 5/8 onward must show exactly one row.
