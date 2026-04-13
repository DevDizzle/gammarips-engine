import os
import json
import requests
import math
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "profitscout-fida8")
DATASET = "profit_scout"
POLYGON_KEY = os.getenv("POLYGON_API_KEY")

bq_client = bigquery.Client(project=PROJECT_ID)

def fetch_historical_bars(ticker: str, end_date: str) -> pd.DataFrame | None:
    # fetch 250 bars to be safe (needed for 200 SMA and 52-week lookback which is roughly 250 trading days)
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/2024-01-01/{end_date}?adjusted=true&sort=asc&limit=300&apiKey={POLYGON_KEY}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "results" not in data or not data["results"]:
            return None
        bars = data["results"]
        
        df = pd.DataFrame(bars)
        df["date"] = pd.to_datetime(df["t"], unit="ms").dt.strftime("%Y-%m-%d")
        df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
        return df
    except Exception as e:
        print(f"Error fetching Polygon for {ticker}: {e}")
        return None

def compute_v4_metrics(df: pd.DataFrame) -> dict | None:
    if df is None or len(df) < 20:
        return None
    try:
        import pandas_ta as ta
        df.ta.stoch(length=14, k=3, d=3, append=True)
    except Exception as e:
        print(f"Error in pandas_ta: {e}")
        return None
        
    latest = df.iloc[-1]
    
    def safe_float(x):
        try:
            v = float(x)
            return None if (math.isnan(v) or math.isinf(v)) else round(v, 4)
        except:
            return None

    close_price = safe_float(latest.get("close", 0))
    latest_low = safe_float(latest.get("low"))
    latest_high = safe_float(latest.get("high"))
    
    # Approx 52-week low/high using up to 250 bars
    high_52w = safe_float(df["high"].max())
    low_52w = safe_float(df["low"].min())
    
    if latest_high is not None and latest_low is not None and latest_high > latest_low:
        close_loc = (close_price - latest_low) / (latest_high - latest_low)
    else:
        close_loc = 0.5
        
    dist_from_low = (close_price - low_52w) / low_52w if low_52w and low_52w > 0 else None
    dist_from_high = (high_52w - close_price) / close_price if close_price and close_price > 0 and high_52w else None
    
    stochd_14_3_3 = safe_float(latest.get("STOCHd_14_3_3"))
    
    return {
        "close_loc": safe_float(close_loc),
        "dist_from_low": safe_float(dist_from_low),
        "dist_from_high": safe_float(dist_from_high),
        "stochd_14_3_3": safe_float(stochd_14_3_3)
    }

def main():
    if not POLYGON_KEY:
        print("Missing POLYGON_API_KEY environment variable.")
        return

    q = f"SELECT ticker, scan_date FROM `{PROJECT_ID}.{DATASET}.overnight_signals_enriched` WHERE close_loc IS NULL ORDER BY scan_date ASC"
    rows = list(bq_client.query(q).result())
    
    print(f"Found {len(rows)} records to backfill...")
    
    updates = []
    
    for i, row in enumerate(rows):
        ticker = row["ticker"]
        scan_date = str(row["scan_date"])
        print(f"[{i+1}/{len(rows)}] Backfilling {ticker} for {scan_date}...")
        
        df = fetch_historical_bars(ticker, scan_date)
        metrics = compute_v4_metrics(df)
        
        if metrics:
            close_loc = metrics["close_loc"]
            dist_from_low = metrics["dist_from_low"]
            dist_from_high = metrics["dist_from_high"]
            stochd = metrics["stochd_14_3_3"]
            
            update_sql = f"""
                UPDATE `{PROJECT_ID}.{DATASET}.overnight_signals_enriched`
                SET close_loc = {close_loc if close_loc is not None else 'NULL'},
                    dist_from_low = {dist_from_low if dist_from_low is not None else 'NULL'},
                    dist_from_high = {dist_from_high if dist_from_high is not None else 'NULL'},
                    stochd_14_3_3 = {stochd if stochd is not None else 'NULL'}
                WHERE ticker = '{ticker}' AND scan_date = '{scan_date}'
            """
            updates.append(update_sql)
            
            # Batch update every 50 to prevent huge memory or timeout
            if len(updates) >= 50:
                print("Running batch update...")
                batch_job = bq_client.query("; ".join(updates))
                batch_job.result()
                updates = []
        else:
            print(f"Skipping {ticker} on {scan_date}, insufficient data.")

    if updates:
        print("Running final batch update...")
        batch_job = bq_client.query("; ".join(updates))
        batch_job.result()
        
    print("Backfill complete.")

if __name__ == "__main__":
    main()