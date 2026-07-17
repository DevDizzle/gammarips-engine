"""READ-ONLY extraction #2 (excursion path study). SELECT only.
Pulls (a) recommended_iv per pool row, (b) daily bar paths for the ticker universe.
Reuses the cached retro_itm_data.parquet universe."""
from google.cloud import bigquery
import pandas as pd, pyarrow.parquet as pq

SP = "/tmp/claude-1000/-home-user-gammarips-engine/05559f27-2c1f-4a61-8a0f-b862bbcd2b81/scratchpad"
tbl = pq.read_table(f"{SP}/retro_itm_data.parquet"); tbl = tbl.replace_schema_metadata(None)
df = tbl.to_pandas()
for c in ["scan_date","expiration","max_bar_date"]:
    df[c] = pd.to_datetime(df[c])
MAXBAR = df["max_bar_date"].iloc[0]

client = bigquery.Client(project="profitscout-fida8")

# (a) IV per pool row (feature-tagged, as-of <= scan_date)
iv = client.query("""
SELECT scan_date, ticker, recommended_contract, recommended_iv
FROM `profitscout-fida8.profit_scout.enriched_option_outcomes`
""").to_dataframe()
print("iv rows:", len(iv), "null IV:", iv["recommended_iv"].isna().sum())
print("dupes on key:", iv.duplicated(["scan_date","ticker","recommended_contract"]).sum())
iv.to_parquet(f"{SP}/retro_exc_iv.parquet")
print(iv["recommended_iv"].describe())

# (b) daily bars for the whole ticker universe over the study window
tickers = sorted(df["ticker"].unique().tolist())
print("tickers:", len(tickers))
bars = client.query("""
SELECT ticker, date, open, high, low, close
FROM `profitscout-fida8.profit_scout.underlying_daily_bars`
WHERE ticker IN UNNEST(@tickers) AND date BETWEEN '2026-04-01' AND @maxbar
ORDER BY ticker, date
""", job_config=bigquery.QueryJobConfig(query_parameters=[
    bigquery.ArrayQueryParameter("tickers","STRING",tickers),
    bigquery.ScalarQueryParameter("maxbar","DATE",MAXBAR.date()),
])).to_dataframe()
print("bar rows:", len(bars), "null high:", bars["high"].isna().sum(), "null close:", bars["close"].isna().sum())
bars.to_parquet(f"{SP}/retro_exc_bars.parquet")
print("date range:", bars["date"].min(), bars["date"].max())
