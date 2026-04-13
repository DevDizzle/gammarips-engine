import pandas as pd
from google.cloud import bigquery

client = bigquery.Client(project="profitscout-fida8")
query = """
SELECT exit_reason, realized_return_pct
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3`
WHERE exit_reason IN ('TARGET', 'STOP', 'TIMEOUT')
"""
df = client.query(query).to_dataframe()

total_executed = len(df)
won = len(df[df['exit_reason'] == 'TARGET'])
lost = len(df[df['exit_reason'] == 'STOP'])
timeout = len(df[df['exit_reason'] == 'TIMEOUT'])

win_rate = won / total_executed if total_executed > 0 else 0

investment_per_trade = 750.0

df['dollar_return'] = investment_per_trade * df['realized_return_pct']
total_profit = df['dollar_return'].sum()

print(f"Total executed trades: {total_executed}")
print(f"Won (TARGET): {won}")
print(f"Lost (STOP): {lost}")
print(f"Timed Out (TIMEOUT): {timeout}")
print(f"Win Rate: {win_rate:.2%}")
print(f"Total Profit: ${total_profit:.2f}")

