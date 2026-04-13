import os
import time
from datetime import datetime, timedelta, date
import pytz
import requests
import pandas as pd
import pandas_market_calendars as mcal
from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "").strip()

nyse = mcal.get_calendar("NYSE")
est = pytz.timezone("America/New_York")

def get_trading_day_offset(base_date: date, n_days: int) -> date:
    end_date = base_date + timedelta(days=max(n_days * 2, 14))
    schedule = nyse.schedule(start_date=base_date, end_date=end_date)
    valid_dates = [d.date() for d in schedule.index if d.date() >= base_date]
    return valid_dates[n_days - 1]

def build_polygon_ticker(underlying: str, expiration: date, direction: str, strike: float) -> str:
    sym = underlying.upper().ljust(6, " ")[:6].strip()
    exp_str = expiration.strftime("%y%m%d")
    opt_type = "C" if direction.upper() == "BULLISH" else "P"
    strike_str = f"{int(round(strike * 1000)):08d}"
    return f"O:{sym}{exp_str}{opt_type}{strike_str}"

def fetch_minute_bars(ticker: str, start_date: date, end_date: date) -> list:
    if not POLYGON_API_KEY:
        return []
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start_date.isoformat()}/{end_date.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLYGON_API_KEY}
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception:
            time.sleep(1)
    return []

def main():
    client = bigquery.Client(project=PROJECT_ID)
    
    # 1. Get the V4 executed trades from the backfilled ledger
    query = f"""
    SELECT 
        scan_date, ticker, recommended_contract, direction, 
        entry_timestamp, entry_price
    FROM `{PROJECT_ID}.profit_scout.forward_paper_ledger_v4`
    WHERE is_skipped = FALSE
    """
    
    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df)} executed trades from V4 ledger.")
    
    targets = [0.40, 0.50, 0.60]
    stops = [-0.25, -0.30, -0.40, -0.50]
    
    results = { (t, s): {'wins': 0, 'losses': 0, 'timeouts': 0, 'total_return': 0, 'executed': 0} for t in targets for s in stops }
    
    for i, row in df.iterrows():
        if pd.isna(row['entry_price']) or not row['entry_timestamp']: 
            print(f"Skipping {row['ticker']} due to missing entry")
            continue
        
        scan_date = row['scan_date']
        if isinstance(scan_date, str):
            scan_date = datetime.strptime(scan_date, "%Y-%m-%d").date()
        elif isinstance(scan_date, datetime):
            scan_date = scan_date.date()

        entry_day = get_trading_day_offset(scan_date, 1)
        timeout_day = get_trading_day_offset(entry_day, 3)
        
        opt_ticker = row["recommended_contract"]
        
        bars = fetch_minute_bars(opt_ticker, entry_day, timeout_day)
        time.sleep(0.2)
        
        if not bars:
            print(f"No bars fetched for {opt_ticker} between {entry_day} and {timeout_day}")
            continue
            
        entry_ts_ms = int(row['entry_timestamp'].timestamp() * 1000)
        
        # Find entry index
        entry_idx = -1
        for j, b in enumerate(bars):
            if b['t'] >= entry_ts_ms:
                entry_idx = j
                break
                
        if entry_idx == -1:
            print(f"DEBUG: {opt_ticker} Could not find entry_ts_ms {entry_ts_ms} ({row['entry_timestamp']}) in bars. First bar: {bars[0]['t'] if bars else 'None'}, Last bar: {bars[-1]['t'] if bars else 'None'}")
            continue
            
        base_entry = row['entry_price']
        timeout_dt = datetime.combine(timeout_day, datetime.strptime("15:59", "%H:%M").time())
        timeout_ts_ms = int(est.localize(timeout_dt).timestamp() * 1000)
        
        for tgt_pct in targets:
            for stop_pct in stops:
                target = base_entry * (1 + tgt_pct)
                stop = base_entry * (1 + stop_pct)
                
                exit_price = None
                exit_reason = "TIMEOUT"
                
                for j in range(entry_idx + 1, len(bars)):
                    b = bars[j]
                    if b['t'] >= timeout_ts_ms:
                        exit_price = b['c']
                        break
                        
                    if b['l'] <= stop and b['h'] >= target:
                        exit_price = stop
                        exit_reason = "STOP"
                        break
                    elif b['l'] <= stop:
                        exit_price = stop
                        exit_reason = "STOP"
                        break
                    elif b['h'] >= target:
                        exit_price = target
                        exit_reason = "TARGET"
                        break
                        
                if exit_price is None:
                    exit_price = bars[-1]['c']
                    exit_reason = "TIMEOUT"
                    
                ret = (exit_price - base_entry) / base_entry
                
                res = results[(tgt_pct, stop_pct)]
                res['executed'] += 1
                res['total_return'] += ret
                if ret > 0: res['wins'] += 1
                if exit_reason == "STOP": res['losses'] += 1
                if exit_reason == "TIMEOUT": res['timeouts'] += 1
                
    print("\n--- V4 EXECUTION BRACKET SWEEP ---")
    print(f"{'Target':<10} | {'Stop':<10} | {'Win Rate':<10} | {'Avg Return':<12} | {'Targets':<8} | {'Stops':<8} | {'Timeouts':<8}")
    print("-" * 80)
    for (t, s), data in results.items():
        if data['executed'] == 0: continue
        wr = data['wins'] / data['executed']
        avg_ret = data['total_return'] / data['executed']
        targets_hit = data['wins'] if data['wins'] else 0
        stops_hit = data['losses']
        timeouts = data['timeouts']
        print(f"+{t*100:<8.0f}% | {s*100:<9.0f}% | {wr:<10.2%} | {avg_ret:<12.2%} | {targets_hit:<8} | {stops_hit:<8} | {timeouts:<8}")

if __name__ == "__main__":
    main()
