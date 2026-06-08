"""Create the paper_shadow_topscore RESEARCH-ONLY shadow table.

Records, for every HAS_PICK day, what "just trade the highest overnight_score
signal in the enriched pool" would have done (TOP_SCORE arm) alongside what the
live Tournament actually picked (TOURNAMENT arm) — both simulated under the
IDENTICAL trader mechanics in forward-paper-trader/main.py:_simulate_contract.

HARD ISOLATION: this table is completely walled off from the live Scorecard
(forward_paper_ledger / current_ledger_stats) and the website (Firestore
todays_pick / signal_performance / webapp / blog). It is an internal research
baseline only — never read or written by any production surface. See
docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md.

Long format: one row PER ARM PER DAY (2 rows/day, arm in {TOURNAMENT,TOP_SCORE}).
Partitioned by entry_day (cheap daily append + age-out).

Idempotent: CREATE TABLE IF NOT EXISTS via exists_ok=True.

Run once (safe isolated infra, NOT a deploy):
    python scripts/ledger_and_tracking/create_paper_shadow_topscore.py
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "paper_shadow_topscore"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("entry_day", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("exit_day", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("arm", "STRING", mode="REQUIRED"),  # TOURNAMENT | TOP_SCORE
    bigquery.SchemaField("ticker", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("direction", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommended_contract", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("overnight_score", "INTEGER", mode="NULLABLE"),
    # confidence: tournament only (from pick_doc v5_4_confidence); NULL for top_score.
    bigquery.SchemaField("confidence", "STRING", mode="NULLABLE"),
    # regime_ok: VIX <= VIX3M; only populated when pick_doc carries the fields.
    bigquery.SchemaField("regime_ok", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("pool_size", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("same_pick", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("entry_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("exit_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("exit_reason", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("realized_return_pct", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("illiquid_exit", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("late_fill_minutes", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("exit_slippage", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("policy_version", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="entry_day",
)

# exists_ok=True == CREATE TABLE IF NOT EXISTS (idempotent, safe to re-run).
table = client.create_table(table, exists_ok=True)
print(f"Ready: {table.project}.{table.dataset_id}.{table.table_id}")
print(f"  partition: entry_day (DAY)")
print(f"  rows: 2 per HAS_PICK day (arm in TOURNAMENT, TOP_SCORE)")
