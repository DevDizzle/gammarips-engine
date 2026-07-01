"""Create the enriched_option_outcomes RESEARCH-ONLY counterfactual-label table.

Records, for EVERY enriched candidate (the full ~50 BULLISH overnight pool per
scan_date — not just the single tournament pick), the realized +80%/-60%/trail
option outcome under byte-identical production mechanics. This is the daily
counterfactual label the autonomous edge-finding agent needs: the live ledger
grows ~1 row/day (the pick only); this grows ~50 rows/day (the whole pool we
*could* have traded), so a leakage-safe option-PnL dataset accrues ~50x faster
and answers "what would the names we skipped have returned?".

Built by reusing forward-paper-trader's `_simulate_contract()` looped over the
same enriched-pool query already in `_write_topscore_shadow` — so labels match
how we actually trade, by construction (no parallel/divergent re-implementation).

COLUMN GROUPS, deliberately separated:
  1. IDENTITY    — keys + the contract.
  2. FEATURES    — point-in-time, leakage-safe inputs (the study levers + greeks
                   + technicals + regime + mom_60). SAFE to use as model features.
                   The regime features are anchored as-of SCAN_DATE close (the real
                   selection point) — vix_at_scan / spy_trend_at_scan /
                   vix_5d_delta_at_scan / vix3m_at_enrich. mom_60 (+ anchor/lookback
                   dates) is the flagship finding's headline lever, persisted at
                   enrichment with anchor + lookback both <= scan_date (must-fix #5).
  3. OUTCOME     — same-day realized labels + telemetry. NEVER feed these back as
                   features. Includes the ENTRY-day-close regime (oc_vix_at_close /
                   oc_spy_trend_at_close / oc_vix_5d_delta_at_close): realized AFTER
                   the same-day trade closes, so benchmarking/telemetry only.
  4. OPPORTUNITY SURFACE (must-fix #6e) — max favorable / max adverse excursion
                   (opp_peak_return / opp_trough_return) over a multi-day window
                   with NO exit rule: the "profit potential" so exit is a FREE
                   VARIABLE derived offline. NOT a tradeable label.
  5. 3-DAY LABEL (must-fix #6) — a parallel -60%/+80%/HOLD=3 bracket
                   (realized_return_pct_3d / exit_reason_3d / exit_day_3d), the
                   horizon the mom_60 finding lives on. Own horizon; NEVER mix with
                   the same-day label.
  6. LABEL-SEMANTICS TAGS (must-fix #6f) — the exact HOLD/STOP/TARGET + sim_version
                   behind each label group so horizons never silently mix.
Plus LINKAGE flags to join each row to the live tournament/top-score decision.

LEAKAGE-FIX 2026-07-01 (substrate must-fix #2): the regime FEATURE is now as-of
scan_date close, not entry-day close. The legacy entry-day-close columns
(VIX_at_entry / SPY_trend_state / vix_5d_delta_entry) were mislabeled as features
but are realized after the same-day trade — they are superseded by the scan-date
features here and re-homed to the oc_*_at_close telemetry group. Existing rows are
migrated by scripts/ledger_and_tracking/backfill_regime_scan_date.py (NOT yet run;
gammarips-review + owner gated). See
docs/DECISIONS/2026-07-01-regime-scan-date-leakage-fix.md.

HARD ISOLATION: research-only. Walled off from the live Scorecard
(forward_paper_ledger / current_ledger_stats) and the website (Firestore /
webapp / blog). Never read or written by any production surface. Pure mechanical
bracket replay — no LLM. See docs/DECISIONS/2026-06-17-enriched-option-outcomes.md.

Partitioned by entry_day (DAY), clustered by ticker.

Idempotent: CREATE TABLE IF NOT EXISTS via exists_ok=True.

Run once (safe isolated infra, NOT a deploy):
    python scripts/ledger_and_tracking/create_enriched_option_outcomes.py
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "enriched_option_outcomes"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    # ---- 1. IDENTITY -------------------------------------------------------
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("entry_day", "DATE", mode="REQUIRED"),   # partition field
    bigquery.SchemaField("exit_day", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("ticker", "STRING", mode="REQUIRED"),    # cluster field
    bigquery.SchemaField("direction", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommended_contract", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommended_strike", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("recommended_expiration", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("recommended_dte", "INTEGER", mode="NULLABLE"),

    # ---- 2. FEATURES (point-in-time, leakage-safe — SAFE as model inputs) ---
    # The 1,375-trade study's confirmed/candidate levers:
    bigquery.SchemaField("recommended_delta", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("risk_reward_ratio", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("atr_normalized_move", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("moneyness_pct", "FLOAT", mode="NULLABLE"),
    # Greeks + contract liquidity:
    bigquery.SchemaField("recommended_gamma", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("recommended_theta", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("recommended_vega", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("recommended_iv", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("recommended_spread_pct", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("recommended_volume", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("recommended_oi", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("volume_oi_ratio", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("contract_score", "FLOAT", mode="NULLABLE"),
    # Flow:
    bigquery.SchemaField("call_dollar_volume", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("put_dollar_volume", "FLOAT", mode="NULLABLE"),
    # Scoring + grounding:
    bigquery.SchemaField("overnight_score", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("premium_score", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("is_premium_signal", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("catalyst_score", "FLOAT", mode="NULLABLE"),
    # Underlying technicals (scan-time):
    bigquery.SchemaField("underlying_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("atr_14", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("rsi_14", "FLOAT", mode="NULLABLE"),
    # 60-day underlying-momentum FEATURE (substrate must-fix #5) — the flagship
    # finding's headline lever. Point-in-time: anchor + lookback both <= scan_date
    # (leakage-guarded upstream in enrichment _resolve_momentum_dates). The audit
    # dates are persisted for reproducibility. See
    # docs/DECISIONS/2026-07-01-momentum-persist-and-opportunity-surface.md.
    bigquery.SchemaField("mom_60", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("mom_anchor_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("mom_lookback_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("mom_lookback_days", "INTEGER", mode="NULLABLE"),

    # ---- 2b. REGIME FEATURES (as-of SCAN_DATE close = the decision point) ---
    # Leakage-fix 2026-07-01: SAFE as model inputs (anchored <= scan_date).
    bigquery.SchemaField("vix_at_scan", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("spy_trend_at_scan", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("vix_5d_delta_at_scan", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("vix3m_at_enrich", "FLOAT", mode="NULLABLE"),  # scan-time (enrich)

    # ---- 3. OUTCOME (realized LABELS — NEVER feed back as features) --------
    bigquery.SchemaField("entry_timestamp", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("entry_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("target_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("stop_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("trail_trigger_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("peak_premium", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("trail_activated", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("trail_stop_at_exit", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("exit_timestamp", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("exit_reason", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("realized_return_pct", "FLOAT", mode="NULLABLE"),
    # P&L-realism audit (mirrors forward_paper_ledger, 2026-06-04 fixes):
    bigquery.SchemaField("exit_slippage", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("illiquid_exit", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("late_fill_minutes", "FLOAT", mode="NULLABLE"),
    # Benchmarking:
    bigquery.SchemaField("iv_rank_entry", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("iv_percentile_entry", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("hv_20d_entry", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("underlying_entry_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("underlying_exit_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("underlying_return", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("spy_entry_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("spy_exit_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("spy_return_over_window", "FLOAT", mode="NULLABLE"),
    # Regime TELEMETRY — entry-day CLOSE (realized after the same-day trade
    # closes). NOT a feature; benchmarking only. See the scan-date FEATURES above.
    bigquery.SchemaField("oc_vix_at_close", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("oc_spy_trend_at_close", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("oc_vix_5d_delta_at_close", "FLOAT", mode="NULLABLE"),

    # ---- 4. OPPORTUNITY SURFACE (must-fix #6e — exit is a FREE VARIABLE) ----
    # Max favorable (peak) / max adverse (trough) excursion of the option premium
    # over [entry_day .. entry_day+(opp_window_days-1) td] with NO exit rule — the
    # "profit potential" so any exit is derivable offline. NOT a tradeable label.
    # opp_status: OK / WINDOW_OPEN / NO_BARS / INVALID_LIQUIDITY /
    #             NO_POST_ENTRY_BARS / ERROR / DISABLED.
    bigquery.SchemaField("opp_window_days", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("opp_status", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("opp_entry_timestamp", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("opp_entry_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("opp_peak_return", "FLOAT", mode="NULLABLE"),    # MFE
    bigquery.SchemaField("opp_trough_return", "FLOAT", mode="NULLABLE"),  # MAE
    bigquery.SchemaField("opp_minutes_to_peak", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("opp_minutes_to_trough", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("opp_bar_count", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("opp_sim_version", "STRING", mode="NULLABLE"),

    # ---- 5. 3-DAY BRACKET LABEL (own horizon — NEVER mix with same-day) ----
    # Parallel -60%/+80%/HOLD=3 bracket (the horizon the mom_60 finding lives on).
    # NULL until the 3-day window closes; filled by the daily cron for closed
    # windows or the gated opportunity-surface backfill.
    bigquery.SchemaField("realized_return_pct_3d", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("exit_reason_3d", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("exit_day_3d", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("exit_timestamp_3d", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("entry_price_3d", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("peak_premium_3d", "FLOAT", mode="NULLABLE"),

    # ---- 6. LABEL-SEMANTICS TAGS (telemetry; must-fix #6f) -----------------
    # The EXACT mechanics that produced each label group, per row, so horizons
    # never silently mix. Do NOT infer horizon from policy_version.
    bigquery.SchemaField("label_sim_version", "STRING", mode="NULLABLE"),     # same-day
    bigquery.SchemaField("label_hold_days", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("label_stop_pct", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("label_target_pct", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("label_3d_sim_version", "STRING", mode="NULLABLE"),  # 3-day
    bigquery.SchemaField("label_3d_hold_days", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("label_3d_stop_pct", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("label_3d_target_pct", "FLOAT", mode="NULLABLE"),

    # ---- LINKAGE / META ----------------------------------------------------
    # Join each pool row back to the live decision for that scan_date:
    bigquery.SchemaField("was_tournament_pick", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("was_topscore_pick", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("pool_size", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("policy_version", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("labeled_at", "TIMESTAMP", mode="NULLABLE"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="entry_day",
)
table.clustering_fields = ["ticker"]

# exists_ok=True == CREATE TABLE IF NOT EXISTS (idempotent, safe to re-run).
table = client.create_table(table, exists_ok=True)
print(f"Ready: {table.project}.{table.dataset_id}.{table.table_id}")
print(f"  partition: entry_day (DAY)")
print(f"  cluster:   ticker")
print(f"  columns:   {len(table.schema)} ({sum(1 for f in table.schema)} fields)")
print(f"  scope:     full enriched BULLISH pool per scan_date (~50 rows/day)")
