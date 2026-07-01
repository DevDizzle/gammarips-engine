"""Create the underlying_daily_bars SCHEDULED BQ cache (substrate must-fix #5c).

    ################################################################################
    #  NOT YET EXECUTED.  This is a BigQuery DDL WRITE (CREATE TABLE).  It is         #
    #  gammarips-review + OWNER gated.  Do NOT run it until both sign off.            #
    ################################################################################

WHY (docs/DECISIONS/2026-07-01-momentum-persist-and-opportunity-surface.md):
mom_60 is now persisted onto overnight_signals_enriched at enrichment time, but the
ONLY way to RE-derive / backfill / audit it historically today is a gitignored,
stale (2026-06-19) local parquet cache
(backtesting_and_research/cache/poly_daily_underlying/) — a leak trap and not
reproducible from infra. This table is the canonical, point-in-time, split/dividend
ADJUSTED underlying daily-bar series so momentum is reproducible from BQ, not a
local artifact.

WHAT: one row per (ticker, date) with the ADJUSTED OHLCV close. Partitioned by
`date` (DAY), clustered by `ticker`. Source = Polygon grouped-daily ADJUSTED (the
SAME endpoint the live enrichment momentum tilt uses — _fetch_grouped_daily_closes
— so the cache is byte-consistent with the tilt by construction). Loaded by
scripts/ledger_and_tracking/load_underlying_daily_bars.py (also gated).

LEAKAGE NOTE: this table is UNCONDITIONAL market history (a bar dated D is D's
close). It is leakage-SAFE to CONSUME only when every read is bounded to dates
<= the decision point (scan_date). The mom backfill (backfill_mom_60.py) enforces
that bound; do not join it to labels without a date filter.

HARD ISOLATION: research/infra cache. Never read or written by the live trading
path. Additive only.

Idempotent: exists_ok=True == CREATE TABLE IF NOT EXISTS (safe to re-run).

Run once (safe isolated infra, NOT a deploy), only after review + owner OK:
    python scripts/ledger_and_tracking/create_underlying_daily_bars.py

One-shot DDL script (per .claude/rules/scripts-ledger.md): do NOT re-run without
explicit user approval.
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "underlying_daily_bars"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    bigquery.SchemaField("date", "DATE", mode="REQUIRED"),        # partition field
    bigquery.SchemaField("ticker", "STRING", mode="REQUIRED"),    # cluster field
    bigquery.SchemaField("open", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("high", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("low", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("close", "FLOAT", mode="NULLABLE"),      # ADJUSTED close
    bigquery.SchemaField("volume", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("adjusted", "BOOLEAN", mode="NULLABLE"),  # always TRUE from grouped-adj
    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),     # e.g. "polygon_grouped_daily_adj"
    bigquery.SchemaField("loaded_at", "TIMESTAMP", mode="NULLABLE"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="date",
)
table.clustering_fields = ["ticker"]

table = client.create_table(table, exists_ok=True)
print(f"Ready: {table.project}.{table.dataset_id}.{table.table_id}")
print(f"  partition: date (DAY)")
print(f"  cluster:   ticker")
print(f"  columns:   {len(table.schema)}")
print(f"  source:    Polygon grouped-daily ADJUSTED (load_underlying_daily_bars.py)")
