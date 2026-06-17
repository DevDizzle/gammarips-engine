# 2026-06-17 — enriched_option_outcomes: daily counterfactual option-PnL label

**Status:** IMPLEMENTED, `gammarips-review` PASS (2026-06-17), pending deploy + cron + backfill. Research-only infra — does NOT change execution policy, so the full Definition-of-Done gate (30-day OOS) does not apply. The leakage audit is the non-negotiable part and it passed.

## Problem
The live ledger (`forward_paper_ledger`) records realized **option** PnL for only the **single tournament pick per day** — the labeled dataset grows ~1 row/day. The autonomous edge-finder / regime-detection vision (see the agent-data-readiness work) needs far more, and specifically the **counterfactual**: what would the ~50 enriched names we *didn't* trade have returned, at the option level? Today that doesn't exist:
- `win-tracker`/`signal_performance` tracks the full pool but only **underlying** stock returns — actively misleading for option edge (underlying-up 54% vs option-up 41% on the realized backfill).
- The only real option-PnL label, the 1,375-trade study (`backtesting_and_research/realized_label.pkl`), is a **frozen one-shot ending 2026-05-29, pre-V6**. Nothing replaces it.

So the strategy's edge-rank levers rest on stale, pre-V6 data, and there is no ongoing substrate for an edge agent to learn from.

## Decision
A new RESEARCH-ONLY table `profit_scout.enriched_option_outcomes` + a daily job that replays the live +80/-60/trail bracket over the **full enriched BULLISH pool** (~50/day) and persists one outcome row per candidate. This is the leakage-safe option-PnL substrate, growing ~50x faster than the ledger and supplying the counterfactual.

**Reuse, not re-implement.** The labeler loops the EXISTING production `_simulate_contract(..., pick_doc=None)` over the SAME enriched-pool query already in `_write_topscore_shadow`, and writes via the EXISTING `_write_shadow_records` (idempotent delete-then-load, research table only). So counterfactual labels are byte-identical to how the live trader fills, by construction.

### Scope decisions (owner, 2026-06-17)
- **Pool:** enriched ~50 BULLISH only (the live strategy's universe), `ENRICHED_OUTCOMES_BULLISH_ONLY=True`. Not the raw all-direction scan pool.
- **Backfill:** full enriched history from ~2026-04-10 → present. Regenerates the frozen 1,375-trade study on current data AND extends it through the V6 era, de-staling the lever basis.

### Components
- `scripts/ledger_and_tracking/create_enriched_option_outcomes.py` — table DDL (63 cols, partition `entry_day`, cluster `ticker`; three groups: IDENTITY / FEATURES point-in-time / OUTCOME labels + linkage flags `was_tournament_pick`/`was_topscore_pick`). Created 2026-06-17.
- `forward-paper-trader/main.py` — `_write_enriched_outcomes()`, `run_label_enriched_pool()`, `POST /label_enriched_pool`. Same future-window guard as the live trader (no partial-bar phantom outcomes).
- `scripts/ledger_and_tracking/backfill_enriched_option_outcomes.py` — one-shot HTTP driver over the deployed endpoint (labeling runs in-container where the Polygon secret + deps live); idempotent per scan_date.

## Isolation & safety (review-verified)
- Writes ONLY to `enriched_option_outcomes`. Never `forward_paper_ledger`, `cohort_stats`, `todays_pick`, `ledger_trades`, or any website/Scorecard surface. `run_forward_paper_trading` is unaltered.
- **Leakage-safe:** the pool SELECT explicitly enumerates point-in-time feature columns and pulls NONE of win-tracker's underlying-outcome columns (`next_day_pct`/`day2_pct`/`day3_pct`/`peak_return_3d`/`is_win`/`outcome_tier`) that are written back onto the enriched table. Outcome columns come solely from the forward-looking bracket replay and live in their own column group as labels.
- **No schema-drift landmine:** all 63 written keys match real columns exactly (`_write_shadow_records` uses ALLOW_FIELD_ADDITION without autodetect; verified no stray keys).
- Per-contract sim failure is counted and skipped; empty pool / un-closed window return clean — never abort or corrupt.

## Rollout
1. `create_*` (done). 2. Deploy `forward-paper-trader`. 3. Cloud Scheduler cron on `/label_enriched_pool`, AFTER the trade-exit cron. 4. Run `backfill_*` (report fill-rate). 5. Verify: tournament pick's labeled row in this table matches its `forward_paper_ledger` row (same ticker/date → same `realized_return_pct`) — proof the counterfactual labels use identical mechanics.
