"""One-shot DDL: create profit_scout.signal_ranker_runs.

Append-only run-trace table written by the V5.4 signal-ranker Cloud Run
service. Each row is one (run_id, candidate_ticker) — typically 5-10 rows
per scan_date capturing the full Scorer fanout, top-5 cut, and Picker choice.

Joinable to forward_paper_ledger on (candidate_ticker, entry_day) for
hindsight P&L attribution per Scorer rubric dimension.

Schema source: docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md
                (Phase 0 deliverable, locked 2026-05-08)

Per .claude/rules/scripts-ledger.md: this is a one-shot DDL. Do not re-run
without explicit user approval after first execution.

Safe to re-run technically: google.cloud.bigquery raises Conflict on
duplicate create, which we catch and print. No destructive behavior.
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "signal_ranker_runs"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    # Identity
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("entry_day", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("candidate_ticker", "STRING", mode="REQUIRED"),

    # Static-ranker context
    bigquery.SchemaField("candidate_rank_static", "INTEGER", mode="NULLABLE"),

    # Scorer rubric
    bigquery.SchemaField("composite_score", "FLOAT", mode="REQUIRED"),
    bigquery.SchemaField("flow_conviction", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("regime_alignment", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("narrative_coherence", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("scorer_reasoning", "STRING", mode="NULLABLE"),

    # Top-5 + Picker
    bigquery.SchemaField("in_top_5", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("picker_chose", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("picker_runner_up", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("picker_justification", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("picker_confidence", "STRING", mode="NULLABLE"),

    # Versioning
    bigquery.SchemaField("scorer_prompt_version", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("picker_prompt_version", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("scorer_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("picker_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("composite_weights_json", "STRING", mode="REQUIRED"),

    # Latency
    bigquery.SchemaField("scorer_latency_ms", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("picker_latency_ms", "INTEGER", mode="NULLABLE"),

    # Bookkeeping
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="scan_date",
)
# Cluster on join keys to forward_paper_ledger for fast hindsight P&L joins.
table.clustering_fields = ["candidate_ticker", "entry_day"]

try:
    table = client.create_table(table)
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
    print(f"  Partitioned on: scan_date (DAY)")
    print(f"  Clustered on:   candidate_ticker, entry_day")
except Exception as e:
    print(f"Error creating table (may already exist): {e}")
