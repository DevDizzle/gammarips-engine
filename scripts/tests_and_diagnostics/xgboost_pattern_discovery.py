import pandas as pd
from google.cloud import bigquery
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def main():
    client = bigquery.Client(project="profitscout-fida8")
    
    query = """
    SELECT
      e.close_loc, e.rsi_14, e.atr_14, e.recommended_spread_pct, e.recommended_iv,
      e.recommended_volume, e.premium_score, e.recommended_dte, e.underlying_price,
      e.macd, e.stochd_14_3_3, e.dist_from_low, e.dist_from_high,
      l.realized_return_pct, l.exit_reason, l.is_skipped
    FROM `profitscout-fida8.profit_scout.overnight_signals_enriched` e
    JOIN `profitscout-fida8.profit_scout.forward_paper_ledger_v3` l
      ON e.ticker = l.ticker AND e.scan_date = l.scan_date
    WHERE l.is_skipped = FALSE AND l.realized_return_pct IS NOT NULL
    """
    
    print("Fetching data from BigQuery...")
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    print(f"Dataset size before cleaning: {len(df)} rows.")

    if len(df) == 0:
        print("No data found! Check the join conditions.")
        return

    # Target variable: +40% target hit
    # Since prices can slip, we use >= 35% as a proxy for the 40% target
    df['is_win'] = (df['realized_return_pct'] >= 0.35).astype(int)
    win_rate = df['is_win'].mean()
    print(f"Overall Win Rate (Target >= 35% return): {win_rate:.2%}")

    features = [
        'close_loc', 'rsi_14', 'atr_14', 'recommended_spread_pct', 'recommended_iv',
        'recommended_volume', 'premium_score', 'recommended_dte', 'underlying_price',
        'macd', 'dist_from_low', 'dist_from_high'
    ]
    
    df[features] = df[features].fillna(df[features].median())
    print(f"Dataset size after missing value imputation: {len(df)}")

    X = df[features]
    y = df['is_win']

    if len(X) < 10:
        print("Not enough data to train a model.")
        return

    # 1. Random Forest for Feature Importance
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
    rf.fit(X, y)
    importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)
    
    print("\n" + "="*50)
    print("FEATURE IMPORTANCES (Random Forest)")
    print("="*50)
    for feat, imp in importances.head(10).items():
        print(f"{feat:25s} {imp:.4f}")

    # 2. Decision Tree for Rules Extraction
    dt = DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=42, class_weight='balanced')
    dt.fit(X, y)

    print("\n" + "="*50)
    print("DECISION TREE RULES (Paths)")
    print("="*50)
    tree_rules = export_text(dt, feature_names=features)
    print(tree_rules)

    # 3. Analyze Leaves for Expectancy
    df['leaf_id'] = dt.apply(X)
    leaf_stats = df.groupby('leaf_id').agg(
        count=('is_win', 'count'),
        win_rate=('is_win', 'mean'),
        avg_return=('realized_return_pct', 'mean')
    ).sort_values(by='win_rate', ascending=False)
    
    print("\n" + "="*50)
    print("TOP PERFORMING PATTERNS (Leaves)")
    print("="*50)
    print(leaf_stats[leaf_stats['count'] >= 5].head(5))

if __name__ == "__main__":
    main()