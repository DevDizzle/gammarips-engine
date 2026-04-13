"""Create the polygon_iv_history cache table.

One row per (ticker, as_of_date) holding the ATM ~30-DTE implied volatility
on the underlying, as pulled once per trading day from the Polygon options
snapshot. The trader's benchmark_context module queries the trailing 252
trading days of this table to compute `iv_rank_entry` and `iv_percentile_entry`
at trade time.

Clustered by ticker (cheap trailing lookups), partitioned by as_of_date
(cheap daily append + age-out).

Idempotent: if the table already exists, logs and exits cleanly.

Run once:
    python scripts/ledger_and_tracking/create_polygon_iv_history.py
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "polygon_iv_history"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    bigquery.SchemaField("ticker", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("as_of_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("atm_iv_30d", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("dte_used", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("strike_used", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("underlying_px", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("contract_symbol", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("fetched_at", "TIMESTAMP", mode="REQUIRED"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="as_of_date",
)
table.clustering_fields = ["ticker"]

try:
    table = client.create_table(table)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
    print(f"  partition: as_of_date (DAY)")
    print(f"  clustering: {table.clustering_fields}")
except Exception as e:
    print(f"Error creating table (may already exist): {e}")
