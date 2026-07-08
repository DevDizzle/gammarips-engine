-- Leakage-safe FEATURES-ONLY projection of the counterfactual option-PnL set
-- (substrate must-fix #4). The dbt-native mirror of the BigQuery view
-- `enriched_features_v1`.
--
-- fct_enriched_option_outcomes is a deliberate `select o.*` kitchen sink (it
-- carries the realized labels for human analysis). THIS model is the surface a
-- headless data-science agent / the MCP should point at: it exposes ONLY
-- point-in-time features (as-of <= scan_date), identity/join keys, and cohort
-- metadata. Every outcome / label / opportunity / regime-telemetry column is
-- excluded by an EXPLICIT allowlist (not `except`) — a new base column is
-- dropped by default until someone classifies it and adds it here.
--
-- Join back to fct_enriched_option_outcomes on outcome_id when (and only when) a
-- human needs the labels for supervised training.
{{ config(materialized='view') }}

select
    -- identity / join keys (known at selection)
    outcome_id,
    scan_date,
    entry_day,
    ticker,
    direction,
    recommended_contract,
    recommended_strike,
    recommended_expiration,
    recommended_dte,

    -- features (point-in-time, as-of <= scan_date; safe as model inputs)
    recommended_delta,
    risk_reward_ratio,
    atr_normalized_move,
    moneyness_pct,
    recommended_gamma,
    recommended_theta,
    recommended_vega,
    recommended_iv,
    recommended_spread_pct,
    recommended_volume,
    recommended_oi,
    volume_oi_ratio,
    contract_score,
    call_dollar_volume,
    put_dollar_volume,
    overnight_score,
    premium_score,
    is_premium_signal,
    catalyst_score,
    underlying_price,
    atr_14,
    rsi_14,
    vix3m_at_enrich,

    -- cohort / linkage metadata (describes the SELECTION, not the outcome)
    was_tournament_pick,
    was_topscore_pick,
    pool_size,
    policy_version

    -- PENDING (uncomment once the must-fix #2 regime-scan-date + must-fix #5
    -- mom_60 backfills add these columns to the base table):
    -- , vix_at_scan
    -- , spy_trend_at_scan
    -- , vix_5d_delta_at_scan
    -- , mom_60
    -- , mom_anchor_date
    -- , mom_lookback_date
    -- , mom_lookback_days
from {{ ref('stg_enriched_option_outcomes') }}
