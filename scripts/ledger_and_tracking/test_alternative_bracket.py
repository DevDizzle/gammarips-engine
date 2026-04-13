import os
import datetime
import pytz
import requests
import pandas as pd
from google.cloud import bigquery
import time

api_key = os.environ.get("POLYGON_API_KEY", "").strip()
if not api_key:
    print("POLYGON_API_KEY not found!")
    exit(1)

client = bigquery.Client(project='profitscout-fida8')

query = """
SELECT 
    ticker, scan_date, recommended_contract, direction,
    entry_price as old_entry_price,
    realized_return_pct as old_return,
    exit_reason as old_exit_reason
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3`
WHERE exit_reason IN ('TARGET', 'STOP', 'TIMEOUT')
"""
df = client.query(query).to_dataframe()
print(f"Loaded {len(df)} trades for re-evaluation.")

est = pytz.timezone("America/New_York")

def fetch_minute_bars(ticker: str, start_date_str: str, end_date_str: str) -> list:
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start_date_str}/{end_date_str}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            time.sleep(1)
    return []

# We need calendar to get day1 and day3 reliably without fetching SPY per trade
import pandas_market_calendars as mcal
nyse = mcal.get_calendar("NYSE")

def get_trading_days(base_date, num_days):
    end_date = base_date + datetime.timedelta(days=max(num_days * 2, 14))
    schedule = nyse.schedule(start_date=base_date, end_date=end_date)
    valid_dates = [d.date() for d in schedule.index if d.date() > base_date]
    return valid_dates[:num_days]

results_list = []

for idx, row in df.iterrows():
    scan_date = row['scan_date']
    if isinstance(scan_date, datetime.datetime):
        scan_date = scan_date.date()
        
    t_days = get_trading_days(scan_date, 3)
    if len(t_days) < 3:
        continue
        
    entry_day = t_days[0]
    timeout_day = t_days[2]
    
    bars = fetch_minute_bars(row['recommended_contract'], entry_day.isoformat(), timeout_day.isoformat())
    time.sleep(0.2)
    
    entry_dt = datetime.datetime.combine(entry_day, datetime.datetime.strptime("15:00", "%H:%M").time())
    entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
    
    timeout_dt = datetime.datetime.combine(timeout_day, datetime.datetime.strptime("15:59", "%H:%M").time())
    timeout_ts_ms = int(est.localize(timeout_dt).timestamp() * 1000)
    
    entry_bar = next((b for b in bars if b["t"] == entry_ts_ms), None)
    if not entry_bar:
        entry_bar = next((b for b in bars if b["t"] > entry_ts_ms and datetime.datetime.fromtimestamp(b["t"]/1000, tz=est).date() == entry_day), None)
        
    if not entry_bar or entry_bar.get("v", 0) == 0:
        continue
        
    base_entry = entry_bar["c"] * 1.02
    target_price = base_entry * 1.50 # +50% target
    stop_price = base_entry * 0.60   # -40% stop
    
    entry_idx = bars.index(entry_bar)
    exit_reason = "TIMEOUT"
    exit_price = None
    
    for j in range(entry_idx + 1, len(bars)):
        b = bars[j]
        b_ts = b["t"]
        
        if b_ts >= timeout_ts_ms:
            exit_reason = "TIMEOUT"
            exit_price = b["c"]
            break
            
        if b["l"] <= stop_price and b["h"] >= target_price:
            exit_reason = "STOP"
            exit_price = stop_price
            break
        elif b["l"] <= stop_price:
            exit_reason = "STOP"
            exit_price = stop_price
            break
        elif b["h"] >= target_price:
            exit_reason = "TARGET"
            exit_price = target_price
            break
            
    if exit_price is None:
        last = bars[-1] if len(bars) > entry_idx else entry_bar
        exit_reason = "TIMEOUT"
        exit_price = last["c"]
        
    new_ret = (exit_price - base_entry) / base_entry
    
    results_list.append({
        'ticker': row['ticker'],
        'old_reason': row['old_exit_reason'],
        'new_reason': exit_reason,
        'old_ret': row['old_return'],
        'new_ret': new_ret
    })

df_res = pd.DataFrame(results_list)

old_profit = df_res['old_ret'].sum() * 750
new_profit = df_res['new_ret'].sum() * 750

new_wins = len(df_res[df_res['new_reason'] == 'TARGET'])
new_losses = len(df_res[df_res['new_reason'] == 'STOP'])
new_timeouts = len(df_res[df_res['new_reason'] == 'TIMEOUT'])

new_win_rate = new_wins / len(df_res)
profitable_timeouts = len(df_res[(df_res['new_reason'] == 'TIMEOUT') & (df_res['new_ret'] > 0)])

print("\n=== BACKTEST RESULTS (+50% TARGET / -40% STOP) ===")
print(f"Total Trades Analyzed: {len(df_res)}")
print(f"\n--- Old Brackets (+40% / -25%) ---")
print(f"Old Win Rate: {len(df_res[df_res.old_reason == 'TARGET']) / len(df_res):.2%}")
print(f"Old Total Profit: ${old_profit:.2f}")

print(f"\n--- New Brackets (+50% / -40%) ---")
print(f"Wins (+50% Hit): {new_wins}")
print(f"Losses (-40% Hit): {new_losses}")
print(f"Timeouts (Expired): {new_timeouts} (of which {profitable_timeouts} were profitable)")
print(f"New Win Rate (Strict +50% hits): {new_win_rate:.2%}")
print(f"Overall Profitable Trades (>0%): {new_wins + profitable_timeouts} ({(new_wins + profitable_timeouts)/len(df_res):.2%})")
print(f"New Total Profit: ${new_profit:.2f}")

