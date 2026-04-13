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
    
    # We query the enriched signals table for our V6 logic:
    query = f"""
    SELECT 
        scan_date, ticker, recommended_contract, direction, recommended_strike, 
        recommended_expiration, recommended_dte, rsi_14, close_loc
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE recommended_contract IS NOT NULL
      AND recommended_dte BETWEEN 14 AND 28
      AND rsi_14 <= 55.0
      AND close_loc > 0.20
    """
    
    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df)} signals matching V6 Structural Sniper criteria.")
    
    target_pct = 0.40
    stop_pct = -0.25
    
    trade_results = []
    
    for i, row in df.iterrows():
        scan_date = row['scan_date']
        if isinstance(scan_date, str):
            scan_date = datetime.strptime(scan_date, "%Y-%m-%d").date()
        elif isinstance(scan_date, datetime):
            scan_date = scan_date.date()

        entry_day = get_trading_day_offset(scan_date, 1)
        if entry_day >= datetime.now(est).date():
            print(f"Skipping {row['ticker']} from {scan_date} because entry_day {entry_day} is in the future or today.")
            continue

        timeout_day = get_trading_day_offset(entry_day, 3)
        
        opt_ticker = row["recommended_contract"]
        
        bars = fetch_minute_bars(opt_ticker, entry_day, timeout_day)
        time.sleep(0.2)
        
        if not bars:
            print(f"Skipping {row['ticker']} because no bars were fetched for {opt_ticker} between {entry_day} and {timeout_day}.")
            continue
            
        # Entry is 15:00 ET
        entry_dt = datetime.combine(entry_day, datetime.strptime("15:00", "%H:%M").time())
        entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
        
        entry_idx = -1
        for j, b in enumerate(bars):
            if b['t'] >= entry_ts_ms:
                entry_idx = j
                break
                
        if entry_idx == -1:
            print(f"Skipping {row['ticker']} because entry time (15:00) not found in bars on {entry_day}.")
            continue
            
        entry_bar = bars[entry_idx]
        if entry_bar.get("v", 0) == 0:
            print(f"Skipping {row['ticker']} because entry bar had 0 volume.")
            continue
            
        base_entry = entry_bar['c'] * 1.02 # 2% slippage penalty
        target_price = base_entry * (1 + target_pct)
        stop_price = base_entry * (1 + stop_pct)
        
        timeout_dt = datetime.combine(timeout_day, datetime.strptime("15:59", "%H:%M").time())
        timeout_ts_ms = int(est.localize(timeout_dt).timestamp() * 1000)
        
        exit_price = None
        exit_reason = "TIMEOUT"
        
        for j in range(entry_idx + 1, len(bars)):
            b = bars[j]
            if b['t'] >= timeout_ts_ms:
                exit_price = b['c']
                break
                
            if b['l'] <= stop_price and b['h'] >= target_price:
                exit_price = stop_price
                exit_reason = "STOP"
                break
            elif b['l'] <= stop_price:
                exit_price = stop_price
                exit_reason = "STOP"
                break
            elif b['h'] >= target_price:
                exit_price = target_price
                exit_reason = "TARGET"
                break
                
        if exit_price is None:
            exit_price = bars[-1]['c']
            exit_reason = "TIMEOUT"
            
        ret = (exit_price - base_entry) / base_entry
        
        trade_results.append({
            'ticker': row['ticker'],
            'scan_date': scan_date,
            'contract': opt_ticker,
            'ret': ret,
            'win': 1 if ret > 0 else 0,
            'exit_reason': exit_reason
        })
        
    df_results = pd.DataFrame(trade_results)
    if len(df_results) == 0:
        print("No valid executions simulated.")
        return

    print(f"\nSuccessfully simulated {len(df_results)} executions.\n")
    
    print(f"--- V6 STRUCTURAL SNIPER SWEEP (+40% / -25% Bracket) ---")
    trades = len(df_results)
    wins = df_results['win'].sum()
    wr = df_results['win'].mean()
    avg_ret = df_results['ret'].mean()
    print(f"Total Trades: {trades}")
    print(f"Win Rate:     {wr:.2%}")
    print(f"Avg Return:   {avg_ret:.2%}")
    print(f"Wins:         {wins}")
    print(f"Losses/Time:  {trades - wins}")
    
    # breakdown by exit reason
    print("\nBreakdown by Exit Reason:")
    print(df_results['exit_reason'].value_counts())

if __name__ == "__main__":
    main()