import pandas as pd
from google.cloud import bigquery

client = bigquery.Client(project='profitscout-fida8')

# Check schemas
print("--- overnight_signals_enriched ---")
q1 = """
SELECT column_name, data_type 
FROM `profitscout-fida8.profit_scout.INFORMATION_SCHEMA.COLUMNS` 
WHERE table_name = 'overnight_signals_enriched'
"""
print(client.query(q1).to_dataframe())

print("\n--- forward_paper_ledger_v3 ---")
q2 = """
SELECT column_name, data_type 
FROM `profitscout-fida8.profit_scout.INFORMATION_SCHEMA.COLUMNS` 
WHERE table_name = 'forward_paper_ledger_v3'
"""
print(client.query(q2).to_dataframe())

print("\n--- Example Data Join ---")
q3 = """
SELECT s.ticker, s.date, s.close_loc, s.rsi_14, s.atr_pct, s.recommended_spread_pct, s.recommended_iv, l.is_winner, l.pnl_pct
FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` s
LEFT JOIN `profitscout-fida8.profit_scout.forward_paper_ledger_v3` l
ON s.ticker = l.ticker AND s.date = l.signal_date
LIMIT 5
"""
try:
    print(client.query(q3).to_dataframe())
except Exception as e:
    print("Error joining: ", e)
