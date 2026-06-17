"""Create the paper_shadow_intraday RESEARCH-ONLY shadow table.

Records, for every HAS_PICK day, what the LIVE Tournament pick AND the
deterministic top-score pick would have done if DAY-TRADED instead of held 3
days: entered 10:00 ET on entry_day and exited FLAT at 15:45 ET the SAME day (no
stop/target). Two arms per day (TOURNAMENT + TOP_SCORE) so the intraday
"get-in-get-out" theory is measured on both selection methods. The entry is the
identical 10:00 fill each pick used (entry_price reused), so this never
re-simulates entry. Each row also carries that SAME pick's live 3-day bracket
result (hold_3day_return_pct) for a self-contained side-by-side.

HARD ISOLATION: completely walled off from the live Scorecard
(forward_paper_ledger / current_ledger_stats) and the website (Firestore
todays_pick / signal_performance / webapp / blog). Internal research only —
never read or written by any production surface. Distinct from
forward_paper_ledger_intraday (the live MTM table). See
docs/DECISIONS/2026-06-08-intraday-hold-shadow.md.

Up to 2 rows per HAS_PICK day (arm in {TOURNAMENT, TOP_SCORE}). Partitioned by entry_day.

Idempotent: CREATE TABLE IF NOT EXISTS via exists_ok=True.

Run once (safe isolated infra, NOT a deploy):
    python scripts/ledger_and_tracking/create_paper_shadow_intraday.py
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "paper_shadow_intraday"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("entry_day", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("arm", "STRING", mode="REQUIRED"),  # TOURNAMENT | TOP_SCORE
    bigquery.SchemaField("ticker", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("direction", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("recommended_contract", "STRING", mode="NULLABLE"),
    # confidence: tournament consensus (TOURNAMENT arm only); NULL for top_score.
    bigquery.SchemaField("confidence", "STRING", mode="NULLABLE"),
    # regime_ok: VIX <= VIX3M; only populated when pick_doc carries the fields.
    bigquery.SchemaField("regime_ok", "BOOLEAN", mode="NULLABLE"),
    # same_pick: top_score ticker == tournament ticker that day.
    bigquery.SchemaField("same_pick", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("entry_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("intraday_exit_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("intraday_exit_timestamp", "STRING", mode="NULLABLE"),
    # The intraday-flat result: (15:45 close - entry) / entry, no stop/target.
    bigquery.SchemaField("intraday_return_pct", "FLOAT", mode="NULLABLE"),
    # True when no 15:45+ print existed (priced off a stale earlier same-day bar).
    bigquery.SchemaField("intraday_illiquid", "BOOLEAN", mode="NULLABLE"),
    # Reference: the SAME pick's live 3-day bracket outcome, for side-by-side.
    bigquery.SchemaField("hold_3day_return_pct", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("hold_3day_exit_reason", "STRING", mode="NULLABLE"),
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
print(f"  rows: up to 2 per HAS_PICK day (arm TOURNAMENT/TOP_SCORE)")
