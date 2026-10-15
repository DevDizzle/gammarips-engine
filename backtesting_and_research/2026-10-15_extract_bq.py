#!/usr/bin/env python3
"""Extract the stock-move study inputs from BigQuery into parquet. READ-ONLY.

Writes only into backtesting_and_research/cache/stockmove/ (gitignored).
Run with:  env -u PROJECT_ID .venv/bin/python backtesting_and_research/2026-10-15_extract_bq.py
"""
import os

from google.cloud import bigquery

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "backtesting_and_research", "cache", "stockmove")
PROJECT = "profitscout-fida8"
DS = f"`{PROJECT}.profit_scout`"

QUERIES = {
    "overnight_signals": f"""
        SELECT *, DATE(scan_timestamp, "America/New_York") AS scan_day
        FROM {DS}.overnight_signals""",
    "polygon_iv_history": f"""
        SELECT ticker, as_of_date, atm_iv_30d FROM {DS}.polygon_iv_history""",
    "pool_membership": f"""
        SELECT DISTINCT scan_date, ticker FROM {DS}.overnight_signals_enriched""",
}


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    client = bigquery.Client(project=PROJECT)
    for name, sql in QUERIES.items():
        df = client.query(sql).result().to_dataframe()
        path = os.path.join(OUT, f"{name}.parquet")
        df.to_parquet(path, index=False)
        print(f"{name}: {len(df):,} rows x {df.shape[1]} cols -> {os.path.relpath(path, REPO)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
