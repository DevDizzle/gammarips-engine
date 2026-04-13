"""Build the frozen `signals_labeled_v1` feature-discovery dataset.

For every (ticker, scan_date) row in `overnight_signals_enriched` whose
recommended_strike and recommended_expiration are non-null, simulate the V3
mechanics (T+1-from-scan_date entry at 15:00 ET, +40% target / -25% stop, force
exit at 15:59 ET on entry_day + 2 trading days) and write a labeled row to
`signals_labeled_v1`.

Imports the trading-calendar helpers, the Polygon ticker builder, and the
minute-bar fetcher directly from `forward-paper-trader/main.py` so the labeling
mechanics are provably identical to the production trader. The simulator block
itself (the bar walk + exit logic) is a verbatim port of `main.py:283-384`.

The script is idempotent: a single DELETE on `simulator_version` clears the
prior labeled rows, and a load job (not streaming insert) writes the new ones.
Re-running it produces the exact same table.

Usage:
    POLYGON_API_KEY=$(gcloud secrets versions access latest --secret=POLYGON_API_KEY \
        --project=profitscout-fida8) \
    python scripts/research/build_labeled_signals_v1.py

Optional flags:
    --limit N        only process the first N rows (smoke test)
    --resume         skip rows whose (ticker, scan_date) already exist in the
                     table for the current simulator_version
"""

import argparse
import io
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, date
from pathlib import Path

import numpy as np
import pandas as pd
import pytz
from google.cloud import bigquery

# Import the helpers and the simulator's primitives directly from the production
# trader so we can prove parity. The trader file is at the repo's
# `forward-paper-trader/main.py`; this script lives at
# `scripts/research/build_labeled_signals_v1.py`.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "forward-paper-trader"))
import main as trader  # noqa: E402  (path manipulation above is intentional)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
SOURCE_TABLE = f"{PROJECT_ID}.profit_scout.overnight_signals_enriched"
LABELED_TABLE = f"{PROJECT_ID}.profit_scout.signals_labeled_v1"
SIMULATOR_VERSION = "V3_MECHANICS_2026_04_07"
HOLD_DAYS = 2  # Frozen, matches trader.HOLD_DAYS
SLIPPAGE = 1.02
TARGET_MULT = 1.40
STOP_MULT = 0.75

est = pytz.timezone("America/New_York")


def simulate_signal(row: dict, today_et: date) -> dict:
    """Pure port of forward-paper-trader/main.py:283-384.

    Returns a dict of outcome columns to merge onto the source row. The
    structure mirrors the trader exactly so a bytewise comparison against the
    live ledger is meaningful (verification step #1 in the plan).
    """
    out = {
        "entry_day": None,
        "timeout_day": None,
        "entry_timestamp": None,
        "entry_price": None,
        "target_price": None,
        "stop_price": None,
        "exit_timestamp": None,
        "exit_price": None,
        "exit_reason": None,
        "realized_return_pct": None,
        "bars_to_exit": None,
    }

    scan_d = row["scan_date"]
    if isinstance(scan_d, datetime):
        scan_d = scan_d.date()

    entry_day = trader.get_next_trading_day(scan_d)
    if entry_day is None:
        out["exit_reason"] = "NO_BARS"
        return out

    timeout_day = trader.get_nth_next_trading_day(entry_day, HOLD_DAYS)
    out["entry_day"] = entry_day
    out["timeout_day"] = timeout_day

    # Future-window guard: do not label trades whose hold window has not closed.
    if timeout_day is None or timeout_day >= today_et:
        out["exit_reason"] = "FUTURE_TIMEOUT"
        return out

    exp_date = row["recommended_expiration"]
    if isinstance(exp_date, (pd.Timestamp, datetime)):
        exp_date = exp_date.date()

    opt_ticker = trader.build_polygon_ticker(
        row["ticker"], exp_date, row["direction"], float(row["recommended_strike"])
    )

    bars = trader.fetch_minute_bars(opt_ticker, entry_day, timeout_day)
    time.sleep(0.2)  # match trader cadence

    if not bars:
        out["exit_reason"] = "NO_BARS"
        return out

    entry_dt = datetime.combine(entry_day, datetime.strptime("15:00", "%H:%M").time())
    entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
    timeout_dt = datetime.combine(timeout_day, datetime.strptime("15:59", "%H:%M").time())
    timeout_ts_ms = int(est.localize(timeout_dt).timestamp() * 1000)

    # Find the entry bar — same logic as main.py:298-312.
    entry_day_bars = [
        b for b in bars
        if datetime.fromtimestamp(b["t"] / 1000, tz=est).date() == entry_day
    ]
    entry_bar = None
    if entry_day_bars:
        after_or_at = [b for b in entry_day_bars if b["t"] >= entry_ts_ms]
        if after_or_at:
            entry_bar = after_or_at[0]
        else:
            before = [b for b in entry_day_bars if b["t"] < entry_ts_ms]
            entry_bar = before[-1] if before else None

    if not entry_bar or entry_bar.get("v", 0) == 0:
        out["exit_reason"] = "INVALID_LIQUIDITY"
        return out

    base_entry = entry_bar["c"] * SLIPPAGE
    target = base_entry * TARGET_MULT
    stop = base_entry * STOP_MULT

    out["entry_timestamp"] = datetime.fromtimestamp(entry_bar["t"] / 1000, tz=est).isoformat()
    out["entry_price"] = base_entry
    out["target_price"] = target
    out["stop_price"] = stop

    entry_idx = bars.index(entry_bar)
    exit_reason = "TIMEOUT"
    exit_price = None
    exit_ts = None
    last_in_window_bar = None

    for j in range(entry_idx + 1, len(bars)):
        b = bars[j]
        b_ts = b["t"]

        if b_ts >= timeout_ts_ms:
            exit_reason = "TIMEOUT"
            timeout_bar = last_in_window_bar if last_in_window_bar is not None else b
            exit_price = timeout_bar["c"]
            exit_ts = timeout_bar["t"]
            break

        if b["l"] <= stop and b["h"] >= target:
            exit_reason = "STOP"
            exit_price = stop
            exit_ts = b_ts
            break
        elif b["l"] <= stop:
            exit_reason = "STOP"
            exit_price = stop
            exit_ts = b_ts
            break
        elif b["h"] >= target:
            exit_reason = "TARGET"
            exit_price = target
            exit_ts = b_ts
            break

        last_in_window_bar = b

    if exit_price is None:
        last = last_in_window_bar if last_in_window_bar is not None else entry_bar
        exit_reason = "TIMEOUT"
        exit_price = last["c"]
        exit_ts = last["t"]

    out["exit_reason"] = exit_reason
    out["exit_timestamp"] = datetime.fromtimestamp(exit_ts / 1000, tz=est).isoformat()
    out["exit_price"] = float(exit_price)
    out["realized_return_pct"] = float((exit_price - base_entry) / base_entry)
    out["bars_to_exit"] = int((exit_ts - entry_bar["t"]) / 60000)
    return out


def fetch_population(client: bigquery.Client) -> pd.DataFrame:
    """Pull every signal with a tradeable contract, deduped one per (ticker, scan_date).

    Dedup priority matches forward-paper-trader/main.py:194-212:
        1. highest premium_score
        2. highest recommended_volume
    """
    query = f"""
    WITH ranked AS (
      SELECT
        *,
        ROW_NUMBER() OVER (
          PARTITION BY ticker, scan_date
          ORDER BY premium_score DESC, recommended_volume DESC
        ) AS rn
      FROM `{SOURCE_TABLE}`
      WHERE recommended_strike IS NOT NULL
        AND recommended_expiration IS NOT NULL
    )
    SELECT * EXCEPT(rn)
    FROM ranked
    WHERE rn = 1
    ORDER BY scan_date, ticker
    """
    return client.query(query).to_dataframe()


def _normalize(v):
    """Coerce a pandas/numpy value into a JSON-safe Python primitive.

    Critical: pandas NaT must serialize as null, not the string 'NaT'.
    Otherwise BigQuery rejects the load with 'Could not parse NaT as timestamp'.
    """
    if v is None:
        return None
    # pd.NaT and pd.NA — handle BEFORE the isinstance(Timestamp) branch because
    # NaT IS a Timestamp.
    if v is pd.NaT or (isinstance(v, float) and math.isnan(v)):
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, pd.Timestamp):
        if pd.isna(v):
            return None
        return v.isoformat()
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        f = float(v)
        return None if math.isnan(f) else f
    if isinstance(v, np.bool_):
        return bool(v)
    return v


def build_record(row: pd.Series, outcome: dict, labeled_at_iso: str) -> dict:
    """Merge a source row + simulator outcome into a single record for BQ load."""
    rec = {k: _normalize(v) for k, v in row.to_dict().items()}
    rec.update({k: _normalize(v) for k, v in outcome.items()})
    rec["simulator_version"] = SIMULATOR_VERSION
    rec["labeled_at"] = labeled_at_iso
    return rec


def write_records(client: bigquery.Client, records: list) -> None:
    if not records:
        return
    jsonl = "\n".join(json.dumps(r, default=str) for r in records)
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    job = client.load_table_from_file(
        io.BytesIO(jsonl.encode("utf-8")),
        LABELED_TABLE,
        job_config=job_config,
    )
    job.result()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="process only N rows (smoke test)")
    parser.add_argument("--resume", action="store_true",
                        help="skip rows already labeled for this simulator_version")
    parser.add_argument("--batch-size", type=int, default=100,
                        help="rows per BQ load job")
    args = parser.parse_args()

    if not os.environ.get("POLYGON_API_KEY"):
        logger.error("POLYGON_API_KEY not set in env. Aborting.")
        sys.exit(1)
    # The trader module read POLYGON_API_KEY at import time. Re-bind it in case
    # the env was set after this script started its imports somewhere upstream.
    trader.POLYGON_API_KEY = os.environ["POLYGON_API_KEY"].strip()

    client = bigquery.Client(project=PROJECT_ID)

    # Idempotency: clear prior rows for this simulator_version unless resuming.
    if not args.resume:
        delete_query = (
            f"DELETE FROM `{LABELED_TABLE}` "
            f"WHERE simulator_version = '{SIMULATOR_VERSION}'"
        )
        logger.info("Clearing prior rows: %s", delete_query)
        client.query(delete_query).result()

    population = fetch_population(client)
    logger.info("Loaded %d signals from %s", len(population), SOURCE_TABLE)

    if args.resume:
        existing = client.query(
            f"SELECT ticker, scan_date FROM `{LABELED_TABLE}` "
            f"WHERE simulator_version = '{SIMULATOR_VERSION}'"
        ).to_dataframe()
        existing_keys = set(zip(existing["ticker"], existing["scan_date"].astype(str)))
        before = len(population)
        mask = ~population.apply(
            lambda r: (r["ticker"], str(r["scan_date"])) in existing_keys, axis=1
        )
        population = population[mask].reset_index(drop=True)
        logger.info("Resume mode: %d/%d rows already labeled, %d remaining",
                    before - len(population), before, len(population))

    if args.limit:
        population = population.head(args.limit)
        logger.info("Limit applied: processing %d rows", len(population))

    today_et = datetime.now(est).date()
    labeled_at_iso = datetime.now(est).isoformat()

    batch = []
    total = len(population)
    written = 0
    counts = {"TARGET": 0, "STOP": 0, "TIMEOUT": 0, "INVALID_LIQUIDITY": 0,
              "NO_BARS": 0, "FUTURE_TIMEOUT": 0}

    for idx, row in population.iterrows():
        try:
            outcome = simulate_signal(row.to_dict(), today_et)
        except Exception as e:
            logger.exception("simulate_signal failed for %s %s: %s",
                             row.get("ticker"), row.get("scan_date"), e)
            outcome = {
                "entry_day": None, "timeout_day": None, "entry_timestamp": None,
                "entry_price": None, "target_price": None, "stop_price": None,
                "exit_timestamp": None, "exit_price": None, "exit_reason": "NO_BARS",
                "realized_return_pct": None, "bars_to_exit": None,
            }

        reason = outcome.get("exit_reason") or "NO_BARS"
        counts[reason] = counts.get(reason, 0) + 1

        rec = build_record(row, outcome, labeled_at_iso)
        batch.append(rec)

        if len(batch) >= args.batch_size:
            write_records(client, batch)
            written += len(batch)
            logger.info("Wrote batch: %d / %d  (counts so far: %s)",
                        written, total, counts)
            batch = []

    if batch:
        write_records(client, batch)
        written += len(batch)

    logger.info("Done. Wrote %d rows. Final exit-reason counts: %s", written, counts)


if __name__ == "__main__":
    main()
