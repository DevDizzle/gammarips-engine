"""One-shot DDL: create profit_scout.llm_traces_v1.

Append-only trace table written by the gammarips trace_logger library.
Every LLM call across enrichment-trigger, agent-arena, overnight-report-generator
(and any future LLM call-site) lands here.

Safe to re-run: google.cloud.bigquery raises Conflict on duplicate create, which
we catch and print. No destructive behavior.
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "llm_traces_v1"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    # Identity
    bigquery.SchemaField("trace_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("service", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("call_site", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("ticker", "STRING", mode="NULLABLE"),

    # Model
    bigquery.SchemaField("model_provider", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("model_id", "STRING", mode="REQUIRED"),

    # Prompt / response payload
    bigquery.SchemaField("prompt", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("prompt_hash", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("response_text", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("response_parsed", "JSON", mode="NULLABLE"),

    # Usage / cost
    bigquery.SchemaField("input_tokens", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("output_tokens", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("latency_ms", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("cost_usd", "FLOAT", mode="NULLABLE"),

    # Status
    bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("error", "STRING", mode="NULLABLE"),

    # Dedup / drift keys
    bigquery.SchemaField("inputs_hash", "STRING", mode="NULLABLE"),

    # Bookkeeping
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="scan_date",
    # 180 days. Traces include full prompts + responses (large columns);
    # bound the table so it cannot grow unboundedly. Adjust up once volume
    # and audit-retention needs are known.
    expiration_ms=180 * 24 * 60 * 60 * 1000,
)
table.clustering_fields = ["service", "model_id"]

try:
    table = client.create_table(table)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
    print(f"  Partitioned on: scan_date (DAY)")
    print(f"  Clustered on:   service, model_id")
except Exception as e:
    print(f"Error creating table (may already exist): {e}")
