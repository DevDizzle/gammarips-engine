import os
import datetime
import pytz
import requests
import pandas as pd
from google.cloud import bigquery

def to_et(ts_ms):
    dt = datetime.datetime.fromtimestamp(ts_ms / 1000, tz=pytz.utc)
    return dt.astimezone(pytz.timezone('US/Eastern'))

api_key = os.environ.get("POLYGON_API_KEY")
if not api_key:
    print("POLYGON_API_KEY not found!")
    exit(1)

client = bigquery.Client(project='profitscout-fida8')

# We join with overnight_signals_enriched to get recommended_strike and recommended_expiration
query = """
SELECT 
    l.ticker, l.scan_date, l.direction, 
    l.entry_price as old_entry_price, l.exit_price as old_exit_price, l.exit_reason as old_exit_reason,
    l.recommended_contract,
    s.recommended_strike, s.recommended_expiration
FROM `profitscout-fida8.profit_scout.forward_paper_ledger_v3` l
JOIN `profitscout-fida8.profit_scout.overnight_signals_enriched` s
  ON l.ticker = s.ticker AND l.scan_date = s.scan_date
WHERE l.exit_reason IN ('TARGET', 'STOP', 'TIMEOUT')
"""

df = client.query(query).to_dataframe()
print(f"Loaded {len(df)} trades.")

# Cache SPY days to avoid repeated calls
spy_days_cache = {}
def get_trading_days(scan_dt_str):
    if scan_dt_str in spy_days_cache:
        return spy_days_cache[scan_dt_str]
    resp = requests.get(f"https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/{scan_dt_str}/2026-12-31?adjusted=true&sort=asc&limit=50&apiKey={api_key}").json()
    t_days = []
    for r in resp.get('results', []):
        dt = datetime.datetime.utcfromtimestamp(r['t']/1000).strftime('%Y-%m-%d')
        t_days.append(dt)
    
    t_days = [d for d in t_days if d > scan_dt_str]
    spy_days_cache[scan_dt_str] = t_days
    return t_days

results_list = []

for idx, row in df.iterrows():
    sym = row['ticker']
    exp_date = row['recommended_expiration']
    exp_str = exp_date.strftime("%y%m%d")
    opt_type = 'C' if row['direction'] == 'BULLISH' else 'P'
    strike_val = row['recommended_strike']
    strike_str = f"{int(strike_val * 1000):08d}"
    
    reconstructed_ticker = f"O:{sym}{exp_str}{opt_type}{strike_str}"
    
    # Verify reconstruction
    if reconstructed_ticker != row['recommended_contract']:
        print(f"Mismatch: Reconstructed {reconstructed_ticker} != {row['recommended_contract']}")
        opt_ticker = row['recommended_contract'] # fallback
    else:
        opt_ticker = reconstructed_ticker

    scan_dt_str = row['scan_date'].strftime('%Y-%m-%d')
    t_days = get_trading_days(scan_dt_str)
    
    if len(t_days) < 3:
        print(f"Not enough trading days for {opt_ticker} after {scan_dt_str}")
        continue
        
    day1 = t_days[0]
    day3 = t_days[2]

    # Fetch minute bars
    url = f"https://api.polygon.io/v2/aggs/ticker/{opt_ticker}/range/1/minute/{day1}/{day3}?adjusted=true&sort=asc&limit=50000&apiKey={api_key}"
    opt_resp = requests.get(url).json()
    
    raw_bars = opt_resp.get('results', [])
    bars = []
    for r in raw_bars:
        dt = to_et(r['t'])
        bars.append({'dt': dt, 'open': r['o'], 'high': r['h'], 'low': r['l'], 'close': r['c']})
        
    if not bars:
        print(f"No minute bars for {opt_ticker} from {day1} to {day3}")
        continue

    # Find Entry Bar (>= 15:00 ET on Day 1)
    entry_bar = None
    for b in bars:
        if b['dt'].strftime('%Y-%m-%d') == day1 and b['dt'].hour == 15 and b['dt'].minute >= 0:
            entry_bar = b
            break
            
    if not entry_bar:
        print(f"No 15:00 entry bar found for {opt_ticker} on {day1}")
        continue

    base_entry = entry_bar['close'] * 1.02
    target_price = base_entry * 1.50
    stop_price = base_entry * 0.60
    
    exit_price = None
    exit_reason = None
    exit_dt = None

    for b in bars:
        if b['dt'] <= entry_bar['dt']:
            continue
        
        hit_stop = b['low'] <= stop_price
        hit_target = b['high'] >= target_price
        
        if hit_stop and hit_target:
            exit_price = stop_price
            exit_reason = 'STOP'
            exit_dt = b['dt']
            break
        elif hit_stop:
            exit_price = min(stop_price, b['open'])
            exit_reason = 'STOP'
            exit_dt = b['dt']
            break
        elif hit_target:
            exit_price = max(target_price, b['open'])
            exit_reason = 'TARGET'
            exit_dt = b['dt']
            break
            
        if b['dt'].strftime('%Y-%m-%d') == day3 and b['dt'].hour >= 15 and b['dt'].minute >= 59:
            exit_price = b['close']
            exit_reason = 'TIMEOUT'
            exit_dt = b['dt']
            break

    if exit_price is None:
        exit_price = bars[-1]['close']
        exit_reason = 'TIMEOUT'
        exit_dt = bars[-1]['dt']

    old_ret = (row['old_exit_price'] / row['old_entry_price']) - 1 if row['old_entry_price'] > 0 else 0
    new_ret = (exit_price / base_entry) - 1
    
    old_profit = old_ret * 750
    new_profit = new_ret * 750
    
    results_list.append({
        'ticker': opt_ticker,
        'old_reason': row['old_exit_reason'],
        'new_reason': exit_reason,
        'old_profit': old_profit,
        'new_profit': new_profit,
        'new_ret': new_ret
    })

df_res = pd.DataFrame(results_list)

old_total_profit = df_res['old_profit'].sum()
new_total_profit = df_res['new_profit'].sum()
new_wins = len(df_res[df_res['new_reason'] == 'TARGET'])
new_win_rate = new_wins / len(df_res) * 100
profitable_timeouts = len(df_res[(df_res['new_reason'] == 'TIMEOUT') & (df_res['new_profit'] > 0)])

print("\n--- Summary ---")
print(f"Total Trades processed: {len(df_res)}")
print(f"Old Total Profit: ${old_total_profit:.2f}")
print(f"New Total Profit (+50/-40): ${new_total_profit:.2f}")
print(f"New Win Rate: {new_wins}/{len(df_res)} ({new_win_rate:.2f}%)")
print(f"Profitable Timeouts: {profitable_timeouts}")
