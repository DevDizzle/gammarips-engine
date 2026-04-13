import os
import time
from datetime import datetime, timedelta, date
import pytz
import requests
import pandas as pd
import numpy as np
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
    
    query = f"""
    SELECT 
        scan_date, ticker, recommended_contract, direction, recommended_strike, 
        recommended_expiration, recommended_volume, recommended_oi,
        close_loc, dist_from_low, dist_from_high, rsi_14, stochd_14_3_3,
        underlying_price, atr_14, recommended_iv, recommended_dte, recommended_spread_pct,
        macd_hist
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE premium_score = 1
      AND recommended_volume >= 250
      AND recommended_contract IS NOT NULL
      AND scan_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
    """
    
    print("Executing BigQuery...")
    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df)} signals with premium_score=1 and Vol>=250.")
    
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
            continue

        timeout_day = get_trading_day_offset(entry_day, 3)
        opt_ticker = row["recommended_contract"]
        
        bars = fetch_minute_bars(opt_ticker, entry_day, timeout_day)
        time.sleep(0.2)
        
        if not bars:
            continue
            
        entry_dt = datetime.combine(entry_day, datetime.strptime("15:00", "%H:%M").time())
        entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
        
        entry_idx = -1
        for j, b in enumerate(bars):
            if b['t'] >= entry_ts_ms:
                entry_idx = j
                break
                
        if entry_idx == -1:
            continue
            
        entry_bar = bars[entry_idx]
        if entry_bar.get("v", 0) == 0:
            continue
            
        base_entry = entry_bar['c'] * 1.02 # slippage
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
        win = 1 if ret > 0 else 0
        
        # Compute normalized ATR (ATR %)
        atr_pct = (row['atr_14'] / row['underlying_price']) if row['underlying_price'] and row['atr_14'] else np.nan
        
        trade_results.append({
            'win': win,
            'direction': row['direction'],
            'close_loc': row['close_loc'],
            'dist_from_low': row['dist_from_low'],
            'dist_from_high': row['dist_from_high'],
            'rsi_14': row['rsi_14'],
            'atr_pct': atr_pct,
            'iv': row['recommended_iv'],
            'dte': row['recommended_dte'],
            'spread': row['recommended_spread_pct'],
            'macd_hist': row['macd_hist'],
            'stochd': row['stochd_14_3_3']
        })
        
    df_res = pd.DataFrame(trade_results)
    if len(df_res) == 0:
        print("No valid executions simulated.")
        return

    print(f"\n--- FEATURE ANALYSIS FOR PREMIUM SCORE = 1 ({len(df_res)} Trades) ---")
    
    print("\n[MEDIANS: WINNERS vs LOSERS]")
    medians = df_res.groupby('win').median(numeric_only=True).T
    medians.columns = ['Losers (0)', 'Winners (1)']
    print(medians.to_string(float_format=lambda x: f"{x:.4f}"))
    
    print("\n[MEANS: WINNERS vs LOSERS]")
    means = df_res.groupby('win').mean(numeric_only=True).T
    means.columns = ['Losers (0)', 'Winners (1)']
    print(means.to_string(float_format=lambda x: f"{x:.4f}"))

    # Let's see some basic correlations
    print("\n[FEATURE CORRELATION WITH WINNING]")
    corr = df_res.corr(numeric_only=True)['win'].sort_values(ascending=False)
    print(corr.to_string(float_format=lambda x: f"{x:.4f}"))
    
    # Analyze by Direction
    print("\n[BULLISH vs BEARISH]")
    bulls = df_res[df_res['direction'] == 'BULLISH']
    bears = df_res[df_res['direction'] == 'BEARISH']
    print(f"BULLISH: {len(bulls)} trades, Win Rate: {bulls['win'].mean():.2%}")
    print(f"BEARISH: {len(bears)} trades, Win Rate: {bears['win'].mean():.2%}")

if __name__ == "__main__":
    main()
