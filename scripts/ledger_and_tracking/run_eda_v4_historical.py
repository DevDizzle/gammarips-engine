import os
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "profitscout-fida8")
DATASET = "profit_scout"

def run_v4_eda():
    client = bigquery.Client(project=PROJECT_ID)
    
    # We query the enriched table but simulate the V4 Execution rules
    query = f"""
    SELECT 
        ticker, scan_date, direction, is_win, peak_return_3d,
        premium_score, recommended_volume, recommended_oi,
        close_loc, dist_from_low, dist_from_high, stochd_14_3_3
    FROM `{PROJECT_ID}.{DATASET}.overnight_signals_enriched`
    WHERE close_loc IS NOT NULL 
      AND is_win IS NOT NULL
    """
    
    df = client.query(query).to_dataframe()
    
    print(f"Total Enriched Backfilled Records w/ Performance: {len(df)}")
    
    # Apply V4 Base Gates
    v4_base = df[
        (df['premium_score'] >= 1) & 
        (df['recommended_volume'] >= 1000) & 
        (df['recommended_oi'] >= 2000)
    ]
    
    print(f"Records passing V4 Liquidity & Premium=1 Gate: {len(v4_base)}")
    
    # Apply V4 Structural Edge Gates
    def passes_structural_gate(row):
        if row['direction'] == 'BEARISH':
            # Price extended from low, weak close
            return row['dist_from_low'] > 0.20 and row['close_loc'] < 0.30
        elif row['direction'] == 'BULLISH':
            # Price early momentum off bottom, strong close
            return row['dist_from_low'] < 0.10 and row['close_loc'] > 0.70
        return False
        
    v4_base['v4_execute'] = v4_base.apply(passes_structural_gate, axis=1)
    
    v4_executed = v4_base[v4_base['v4_execute'] == True]
    
    print(f"Records passing V4 Structural Gate (Actual Executions): {len(v4_executed)}")
    
    if len(v4_executed) > 0:
        win_rate = v4_executed['is_win'].mean()
        avg_peak = v4_executed['peak_return_3d'].mean()
        
        print("\n--- V4 EXECUTION LAYER PERFORMANCE ---")
        print(f"Overall Win Rate: {win_rate:.2%}")
        print(f"Average Peak Return (3D): {avg_peak:.2%}")
        
        bearish = v4_executed[v4_executed['direction'] == 'BEARISH']
        if len(bearish) > 0:
            print(f"  Bearish Win Rate (n={len(bearish)}): {bearish['is_win'].mean():.2%}")
            
        bullish = v4_executed[v4_executed['direction'] == 'BULLISH']
        if len(bullish) > 0:
            print(f"  Bullish Win Rate (n={len(bullish)}): {bullish['is_win'].mean():.2%}")
    else:
        print("Not enough executed trades to measure performance yet.")

if __name__ == "__main__":
    run_v4_eda()