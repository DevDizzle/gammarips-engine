"""READ-ONLY extraction for retrospective ITM-vs-delta study. SELECT only."""
from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project="profitscout-fida8")

SQL = r"""
WITH pool AS (
  SELECT
    scan_date, ticker, direction, recommended_contract,
    recommended_strike AS strike,
    recommended_expiration AS expiration,
    recommended_dte, recommended_delta AS delta,
    moneyness_pct, underlying_price,
    opp_status, opp_entry_price, opp_entry_timestamp,
    REGEXP_EXTRACT(recommended_contract, r'([CP])[0-9]{8}$') AS cp_flag
  FROM `profitscout-fida8.profit_scout.enriched_option_outcomes`
),
maxbar AS (
  SELECT MAX(date) AS max_bar_date
  FROM `profitscout-fida8.profit_scout.underlying_daily_bars`
),
joined AS (
  SELECT p.*, m.max_bar_date, b.date AS exp_bar_date, b.close AS exp_close
  FROM pool p
  CROSS JOIN maxbar m
  LEFT JOIN `profitscout-fida8.profit_scout.underlying_daily_bars` b
    ON b.ticker = p.ticker AND b.date <= p.expiration
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY p.scan_date, p.ticker, p.recommended_contract
    ORDER BY b.date DESC) = 1
)
SELECT * FROM joined
"""

df = client.query(SQL).to_dataframe()
print("rows:", len(df))
df.to_parquet("/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad/retro_itm_data.parquet")
print(df[["scan_date","ticker","expiration","exp_bar_date","exp_close","delta","opp_entry_price"]].head())
print("max_bar_date:", df["max_bar_date"].iloc[0])
