"""One-shot DDL: create profit_scout.llm_eval_results_v1.

Append-only evaluator output table written by the gammarips-eval Cloud Run
service. Each row is one (trace_id, evaluator) scoring result.

Safe to re-run.
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "llm_eval_results_v1"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    # Identity
    bigquery.SchemaField("eval_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("trace_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("service", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),

    # Evaluator
    bigquery.SchemaField("evaluator", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("eval_version", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("judge_model", "STRING", mode="NULLABLE"),

    # Score
    bigquery.SchemaField("score", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("passed", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("details", "JSON", mode="NULLABLE"),

    # Ground truth
    bigquery.SchemaField("ground_truth_source", "STRING", mode="NULLABLE"),

    # Bookkeeping
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="scan_date",
    # 365 days. Eval results are small rows (score + small details JSON)
    # but we keep them longer than traces to enable year-over-year audits.
    expiration_ms=365 * 24 * 60 * 60 * 1000,
)
table.clustering_fields = ["service", "evaluator"]

try:
    table = client.create_table(table)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
    print(f"  Partitioned on: scan_date (DAY)")
    print(f"  Clustered on:   service, evaluator")
except Exception as e:
    print(f"Error creating table (may already exist): {e}")
