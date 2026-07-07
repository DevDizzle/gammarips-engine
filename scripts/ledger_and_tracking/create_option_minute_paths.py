"""Create the option_minute_paths companion table (MCP Priority-4 / RM-002 /
engine must-fix #6g — the known-deferred minute-path table).

One row per (contract, entry_day, ts): the per-minute option-premium bars
over each enriched-pool candidate's 3-trading-day excursion window
[entry_day .. exit_day_3d]. This is the FIRST-CROSSING substrate the
distributional exit tools were missing — with it, `estimate_exit_rule` can
resolve both-levels-crossed rows by EXACT first touch instead of the
minutes-to-extreme heuristic, and can score TRAILING rules (TF-14); the MCP
`replay_contract` primitive serves the same rows for per-contract replay.

Writers:
  * scripts/ledger_and_tracking/backfill_option_minute_paths.py (one-shot
    history backfill from enriched_option_outcomes; executed 2026-07-07)
  * forward-paper-trader POST /persist_minute_paths (daily top-up cron; each
    run reconciles the last 3 scan_dates so day-2/day-3 bars land as their
    sessions close)
Both write via LOAD JOBS with this EXPLICIT schema — never streaming into
this table (daily reconcile DELETEs by scan_date, which streaming buffers
block), never autodetect (2026-07-02 outage rule).

LEAKAGE CLASSIFICATION — REALIZED TAPE, NEVER A FEATURE
--------------------------------------------------------
Every bar here is realized post-entry market data (the excursion window
starts at the 10:00 ET entry). Same class as the opp_* opportunity surface:
research/label substrate for CLOSED windows. It must never be joined into
enriched_features_v1 or any as-of <= scan_date feature surface, and never
consulted by the selection path. Serving CLOSED-window bars to agents is
fine (it is the historical tape, explicitly timestamped).

Partitioned by entry_day (window-scoped reads + age-out), clustered by
contract (the replay lookup). Idempotent (exists_ok=True).

Run once (safe isolated infra, NOT a deploy):
    PROJECT_ID=profitscout-fida8 python scripts/ledger_and_tracking/create_option_minute_paths.py
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "option_minute_paths"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    # -- identity / join keys ---------------------------------------------
    bigquery.SchemaField("scan_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("entry_day", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("contract", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ticker", "STRING", mode="NULLABLE"),
    # -- the bar ------------------------------------------------------------
    bigquery.SchemaField("ts", "TIMESTAMP", mode="REQUIRED"),  # bar start (UTC)
    bigquery.SchemaField("bar_date", "DATE", mode="NULLABLE"),  # ET session date of the bar
    bigquery.SchemaField("day_index", "INTEGER", mode="NULLABLE"),  # 1..3 within the excursion window
    bigquery.SchemaField("open", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("high", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("low", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("close", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("volume", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("vwap", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("transactions", "INTEGER", mode="NULLABLE"),
    # -- provenance -----------------------------------------------------------
    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="NULLABLE"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY, field="entry_day"
)
table.clustering_fields = ["contract"]
table.description = (
    "Per-minute option-premium bars over each enriched-pool candidate's "
    "3-trading-day excursion window (engine must-fix #6g / MCP RM-002). "
    "REALIZED TAPE — research/label substrate for CLOSED windows only; "
    "NEVER a feature, never joined into enriched_features_v1, never read by "
    "the selection path. Load-jobs only (no streaming, no autodetect). See "
    "docs/DECISIONS/2026-07-07-option-minute-paths.md."
)

created = client.create_table(table, exists_ok=True)
print(f"OK: {created.full_table_id} (partition=entry_day, cluster=contract)")
print(f"Columns: {[f.name for f in created.schema]}")
