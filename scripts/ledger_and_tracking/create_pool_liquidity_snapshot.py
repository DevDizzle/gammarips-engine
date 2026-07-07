"""Create the pool_liquidity_snapshot TELEMETRY table (MCP Priority-1A).

One row per (contract, as_of): the interval liquidity re-read of the current
enriched pool that signal-notifier's /refresh_pool_liquidity endpoint writes
every ~10 minutes during regular trading hours (plus one pre-open pass). The
gammarips-mcp `get_contract_snapshot` / `get_pool_liquidity` tools serve this
table CACHE-FIRST so a whole shortlist refreshes in one metered call at the
busiest minute of the day (~10:00 ET). See
docs/DECISIONS/2026-07-07-pool-liquidity-snapshot.md.

LEAKAGE CLASSIFICATION — TELEMETRY, NEVER A FEATURE
---------------------------------------------------
Every non-identity column here is ENTRY-DAY-LIVE (the 09:15+ tape), keyed by
an explicit `as_of` timestamp. Under the enriched_features_v1 classification
rule this whole table is TELEMETRY:
  * it must NEVER be joined into overnight_signals_enriched,
    enriched_features_v1, or any as-of <= scan_date feature surface;
  * it must never reach the tournament / signal-judge selection path
    (the pick path keeps its own C1-walled OI-only fetch in
    signal-notifier/main.py:_fetch_live_oi);
  * MCP/agents consume it as a LIVE liquidity read with explicit as_of
    provenance — decision-time freshness, not a backtest feature.

Quote columns (bid/ask/mid/spread_pct) are SCHEMA PLACEHOLDERS for the
RM-001b quote-feed purchase — the current Polygon plan serves no options
quotes, so the writer leaves them NULL and the MCP OMITS them from responses
while NULL (a missing field is honest; a NULL reads like a data bug).

Partitioned by DATE(as_of) (cheap day-scoped reads + age-out), clustered by
contract (the MCP's point lookup). Idempotent (exists_ok=True).

Run once (safe isolated infra, NOT a deploy):
    PROJECT_ID=profitscout-fida8 python scripts/ledger_and_tracking/create_pool_liquidity_snapshot.py
"""

from google.cloud import bigquery

PROJECT_ID = "profitscout-fida8"
DATASET_ID = "profit_scout"
TABLE_ID = "pool_liquidity_snapshot"

client = bigquery.Client(project=PROJECT_ID)
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

schema = [
    # -- identity / batch keys -------------------------------------------------
    bigquery.SchemaField("contract", "STRING", mode="REQUIRED"),   # OCC ticker, e.g. O:UNIT260717C00030000
    bigquery.SchemaField("underlying", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("scan_date", "DATE", mode="NULLABLE"),    # the pool this contract came from
    bigquery.SchemaField("as_of", "TIMESTAMP", mode="REQUIRED"),   # batch fetch time (one per refresh pass)
    bigquery.SchemaField("is_preopen", "BOOLEAN", mode="NULLABLE"),  # fetched before 09:30 ET
    bigquery.SchemaField("fetch_status", "STRING", mode="NULLABLE"),  # ok | polygon_empty | polygon_error
    # -- liquidity read (delayed per plan) ------------------------------------
    bigquery.SchemaField("open_interest", "INTEGER", mode="NULLABLE"),  # refreshes once each morning
    bigquery.SchemaField("day_volume", "INTEGER", mode="NULLABLE"),     # live session volume
    bigquery.SchemaField("last_trade_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("last_trade_ts", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("day_open", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("day_high", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("day_low", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("day_close", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("day_last_updated", "TIMESTAMP", mode="NULLABLE"),
    # -- context (TF-18: live moneyness needs the underlying) -----------------
    bigquery.SchemaField("underlying_price", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("underlying_price_source", "STRING", mode="NULLABLE"),  # option_snapshot | day_agg_delayed | prev_close
    bigquery.SchemaField("implied_volatility", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("delta", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("gamma", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("theta", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("vega", "FLOAT", mode="NULLABLE"),
    # -- RM-001b placeholders: NULL until the quote-feed purchase --------------
    bigquery.SchemaField("bid", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("ask", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("mid", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("spread_pct", "FLOAT", mode="NULLABLE"),
    # -- provenance -------------------------------------------------------------
    bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("is_delayed", "BOOLEAN", mode="NULLABLE"),
]

table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY, field="as_of"
)
table.clustering_fields = ["contract"]
table.description = (
    "Interval liquidity telemetry over the current enriched pool "
    "(~10-min cadence during RTH + one pre-open pass), written by "
    "signal-notifier /refresh_pool_liquidity. TELEMETRY ONLY — entry-day-live, "
    "keyed by as_of; NEVER a feature, never joined into enriched_features_v1 "
    "or any as-of<=scan_date surface, never read by the selection path. "
    "bid/ask/mid/spread_pct are NULL placeholders pending the RM-001b quote "
    "feed. See docs/DECISIONS/2026-07-07-pool-liquidity-snapshot.md."
)

created = client.create_table(table, exists_ok=True)
print(f"OK: {created.full_table_id} (partition=DATE(as_of), cluster=contract)")
print(f"Columns: {[f.name for f in created.schema]}")
