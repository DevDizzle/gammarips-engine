-- 1) Create a clean V4 ledger table
CREATE OR REPLACE TABLE `profitscout-fida8.profit_scout.forward_paper_ledger_v4` (
  scan_date DATE NOT NULL,
  ticker STRING NOT NULL,
  recommended_contract STRING NOT NULL,
  direction STRING NOT NULL,
  is_premium_signal BOOL,
  premium_score INT64,

  policy_version STRING,
  policy_gate STRING,
  is_skipped BOOL NOT NULL,
  skip_reason STRING,

  VIX_at_entry FLOAT64,
  SPY_trend_state STRING,
  recommended_dte INT64,
  recommended_volume INT64,
  recommended_oi INT64,
  recommended_spread_pct FLOAT64,
  
  close_loc FLOAT64,
  dist_from_low FLOAT64,
  dist_from_high FLOAT64,
  stochd_14_3_3 FLOAT64,

  entry_timestamp TIMESTAMP,
  entry_price FLOAT64,
  target_price FLOAT64,
  stop_price FLOAT64,
  exit_timestamp TIMESTAMP,
  exit_reason STRING,
  realized_return_pct FLOAT64
);