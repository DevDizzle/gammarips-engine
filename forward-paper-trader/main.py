import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
import pandas_market_calendars as mcal
from google.cloud import bigquery
import yfinance as yf
import time
from flask import Flask, jsonify, request

import benchmark_context as bctx

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "").strip()

nyse = mcal.get_calendar("NYSE")
est = pytz.timezone("America/New_York")

# Config block for V5.3 — Target 80
# See docs/DECISIONS/2026-04-17-v5-3-target-80.md and CHEAT-SHEET.md
#
# V5.3 philosophy: one rule set, one position, pre-defined exits.
#   Entry   : 10:00 ET on day-1 (first trading day after scan_date)
#   Stop    : -60% on option premium (wide stop absorbs IV crush)
#   Target  : +80% on option premium (Deep Research 2026-04-17 recommended
#             asymmetric profit-taking to beat theta/IV crush on stagnant trades)
#   Hold    : 3 trading days
#   Exit    : 15:50 ET on day-3 at market (or earlier if stop/target fires)
#
# Exit precedence when stop and target hit in the same bar: STOP wins
# (conservative — we can't know intrabar sequencing, so assume worst case).
#
# The trader has NO filters beyond what enrichment applies. Signal quality
# gates (V/OI, moneyness, VIX <= VIX3M) live in signal-notifier and
# enrichment-trigger, not here. This service simulates and ledgers every
# enriched signal so we retain the full-coverage research dataset.
MAX_SPREAD_PCT = 0.10
HOLD_DAYS = 3
STOP_PCT = 0.60    # -60% on option premium
TARGET_PCT = 0.80  # +80% on option premium
ENTRY_HHMM = "10:00"  # 10:00 ET on day-1
EXIT_HHMM = "15:50"   # 15:50 ET on day-3
POLICY_VERSION = "V5_3_TARGET_80"
POLICY_GATE = "ENRICHMENT_ONLY_NO_TRADER_GATE"
LEDGER_TABLE = f"{PROJECT_ID}.profit_scout.forward_paper_ledger"

def get_next_trading_day(base_date: date) -> date:
    end_date = base_date + timedelta(days=7)
    schedule = nyse.schedule(start_date=base_date, end_date=end_date)
    future_dates = [d.date() for d in schedule.index if d.date() > base_date]
    return future_dates[0] if future_dates else None

def get_nth_next_trading_day(base_date: date, n: int) -> date:
    d = base_date
    for _ in range(n):
        d = get_next_trading_day(d)
    return d

def build_polygon_ticker(underlying: str, expiration: date, direction: str, strike: float) -> str:
    sym = underlying.upper().ljust(6, " ")[:6].strip()
    exp_str = expiration.strftime("%y%m%d")
    opt_type = "C" if direction.upper() == "BULLISH" else "P"
    strike_str = f"{int(round(strike * 1000)):08d}"
    return f"O:{sym}{exp_str}{opt_type}{strike_str}"

def fetch_minute_bars(ticker: str, start_date: date, end_date: date) -> list:
    if not POLYGON_API_KEY:
        logger.error("POLYGON_API_KEY is not set.")
        return []

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute/{start_date.isoformat()}/{end_date.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": POLYGON_API_KEY}
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"Polygon API Error: {e}")
            time.sleep(1)
    return []

_VIX_CACHE: dict = {"df": None}


def _fetch_vix_daily_fred() -> pd.DataFrame:
    """Return a DataFrame of VIX daily closes indexed by date.

    Source: FRED VIXCLS series (free CSV endpoint, no auth). Cached in-process
    so we hit FRED at most once per trader invocation. The full history is
    ~160 KB and downloads in under a second.
    """
    if _VIX_CACHE["df"] is not None:
        return _VIX_CACHE["df"]
    import io
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))
    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df = df.set_index("observation_date")
    df = df.rename(columns={"VIXCLS": "close"})
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna()
    _VIX_CACHE["df"] = df
    return df


def _fetch_spy_daily_polygon(target_date: date) -> pd.DataFrame:
    """Return SPY daily closes in a ~45-day window ending on target_date.

    Source: Polygon /v2/aggs daily endpoint. Uses the same POLYGON_API_KEY as
    fetch_minute_bars. Returns an empty DataFrame on failure.
    """
    if not POLYGON_API_KEY:
        return pd.DataFrame()
    start = (target_date - timedelta(days=45)).isoformat()
    end = target_date.isoformat()
    url = f"https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "sort": "asc", "limit": 500, "apiKey": POLYGON_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("results", []) or []
        if not data:
            return pd.DataFrame()
        rows = [
            {"date": pd.Timestamp(b["t"], unit="ms").normalize(), "close": float(b["c"])}
            for b in data
        ]
        df = pd.DataFrame(rows).set_index("date")
        return df
    except Exception as e:
        logger.warning(f"Polygon SPY daily fetch failed for {target_date}: {e}")
        return pd.DataFrame()


def get_regime_context(target_date: date):
    """Fetch VIX level, SPY trend state, and VIX 5-day delta for the given date.

    Returns a 3-tuple: (vix_level, spy_trend, vix_5d_delta). All fields are
    telemetry only; missing context must not block execution, so any failure
    returns (None, None, None).

    Data sources (as of 2026-04-08):
      - VIX: FRED series VIXCLS (free CSV, no auth, cloud-reliable)
      - SPY: Polygon /v2/aggs daily bars (already-paid key)
    Switched from yfinance on 2026-04-08 after Yahoo rate-limited Cloud Run.

    spy_trend is "BULLISH" if target_spy_close > 10-day SMA, else "BEARISH".
    vix_5d_delta is (current_vix - vix_5_trading_days_ago), positive = rising.
    """
    try:
        vix_df = _fetch_vix_daily_fred()
        spy_df = _fetch_spy_daily_polygon(target_date)

        if vix_df is None or vix_df.empty:
            logger.warning(f"FRED VIX empty for {target_date}")
            return None, None, None
        if spy_df is None or spy_df.empty:
            logger.warning(f"Polygon SPY daily empty for {target_date}")
            return None, None, None

        target_ts = pd.Timestamp(target_date)

        vix_on_or_before = vix_df[vix_df.index <= target_ts]["close"]
        if len(vix_on_or_before) == 0:
            return None, None, None
        vix_level = float(vix_on_or_before.iloc[-1])

        vix_5d_delta = None
        if len(vix_on_or_before) >= 6:
            vix_5d_ago = float(vix_on_or_before.iloc[-6])
            vix_5d_delta = vix_level - vix_5d_ago

        spy_on_or_before = spy_df[spy_df.index <= target_ts]["close"]
        if len(spy_on_or_before) < 10:
            logger.warning(f"Not enough SPY history for SMA_10 at {target_date}: {len(spy_on_or_before)} days")
            return None, None, None
        target_spy_close = float(spy_on_or_before.iloc[-1])
        spy_sma = float(spy_on_or_before.iloc[-10:].mean())
        spy_trend = "BULLISH" if target_spy_close > spy_sma else "BEARISH"

        return vix_level, spy_trend, vix_5d_delta
    except Exception as e:
        logger.error(f"Error extracting regime context (FRED/Polygon) for {target_date}: {e}")
        return None, None, None

def run_forward_paper_trading(target_date: date = None):
    """V5.3 forward paper trading — Target 80.

    Execution policy (frozen; change only with a new decision doc):
      - Entry:  10:00 ET on D+1 (first trading day after scan_date)
      - Stop:   -60% on option premium
      - Target: +80% on option premium
      - Hold:   3 trading days; exit at 15:50 ET on day-3 if neither fires
      - Ambiguous bar: STOP wins over TARGET (conservative)
      - Writes to forward_paper_ledger with policy_version=V5_3_TARGET_80

    The trader applies NO additional gates. Signal quality filters live
    upstream in enrichment-trigger (spread <= 10%, UOA > $500K, V/OI > 2,
    moneyness 5-15%) and in signal-notifier (VIX <= VIX3M, LIMIT 1).

    No knobs are exposed at the HTTP layer. To change any of this, edit the
    constants at the top of this file and write a decision note.
    """
    if not target_date:
        # Default to today if not provided
        target_date = datetime.now(est).date()

    logger.info(f"Running V5.3 Forward Paper Trading for signals generated on {target_date} "
                f"(entry={ENTRY_HHMM} ET day-1, stop=-{STOP_PCT*100:.0f}%, target=+{TARGET_PCT*100:.0f}%, "
                f"hold_days={HOLD_DAYS}, exit={EXIT_HHMM} ET day-{HOLD_DAYS}, ledger={LEDGER_TABLE})")
    
    client = bigquery.Client(project=PROJECT_ID)
    
    # 1. Fetch Eligible Signals
    # V5.3: no trader-side gates. All signal quality filtering is upstream
    # (enrichment-trigger + signal-notifier). Everything in the enriched table
    # gets simulated and ledgered. See docs/DECISIONS/2026-04-17-v5-3-target-80.md
    query = f"""
    SELECT
        ticker, scan_date, direction, recommended_contract, recommended_strike,
        recommended_expiration, recommended_dte, recommended_volume, recommended_oi,
        recommended_spread_pct, is_premium_signal, premium_score
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
    """
    
    df = client.query(query).to_dataframe()
    logger.info(f"Found {len(df)} eligible signals for {target_date}")
    
    if len(df) == 0:
        return True, "No eligible signals found."
        
    # Deduplicate signals: one per ticker per scan_date
    # Priority: 1. highest premium_score, 2. highest volume, 3. fallback deterministically on index
    df = df.sort_values(by=["premium_score", "recommended_volume"], ascending=[False, False])
    
    # Track which ticker/date combos have been seen
    seen_combinations = set()
    deduplicated_rows = []
    
    for _, row in df.iterrows():
        combo_key = (row["ticker"], str(row["scan_date"].date() if isinstance(row["scan_date"], datetime) else row["scan_date"]))
        if combo_key in seen_combinations:
            # We'll process this as a skipped duplicate later, but keep it in the dataframe for ledger logging
            row["is_duplicate"] = True
        else:
            row["is_duplicate"] = False
            seen_combinations.add(combo_key)
        deduplicated_rows.append(row)
        
    df = pd.DataFrame(deduplicated_rows)
        
    # The intended execution day is the next trading day after the scan_date
    entry_day = get_next_trading_day(target_date) # target_date + 1 trading day
    if entry_day > datetime.now(est).date():
        logger.warning(f"Entry day {entry_day} is in the future. Cannot simulate execution yet.")
        return False, f"Entry day {entry_day} is in the future."

    # Refuse to simulate any trade whose hold window hasn't fully closed yet.
    # Without this guard, the exit-fallback path at the bottom of the simulation
    # loop will use a partial intraday bar from "today" as a phantom TIMEOUT exit,
    # producing data that looks like a closed trade but represents an open position.
    # V5.3: exit_day = entry_day + (HOLD_DAYS - 1) trading days.
    timeout_day_check = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)
    today_et = datetime.now(est).date()
    if timeout_day_check >= today_et:
        msg = (f"Exit day {timeout_day_check} for hold_days={HOLD_DAYS} is today or "
               f"in the future. Hold window has not fully closed; refusing to simulate.")
        logger.warning(msg)
        return False, msg
        
    vix_level, spy_trend, vix_5d_delta = get_regime_context(entry_day)

    if vix_level is None:
        logger.info(f"Proceeding without VIX telemetry for {entry_day}.")
    else:
        delta_str = f"{vix_5d_delta:+.2f}" if vix_5d_delta is not None else "n/a"
        logger.info(f"Regime telemetry on {entry_day}: VIX = {vix_level:.2f} (5d Δ {delta_str}), SPY Trend = {spy_trend}")
    
    records_to_insert = []
    
    for _, row in df.iterrows():
        is_skipped = False
        skip_reason = None
        
        # 2. Evaluate Skip Conditions

        # Deduplication check
        if row.get("is_duplicate", False):
            is_skipped = True
            skip_reason = "DEDUP_TICKER_DATE_SKIP"
        # V5.3: no trader-side gates — all enriched signals trade

        record = {
            "scan_date": row["scan_date"].date() if isinstance(row["scan_date"], datetime) else row["scan_date"],
            "ticker": row["ticker"],
            "recommended_contract": row["recommended_contract"],
            "direction": row["direction"],
            "is_premium_signal": bool(row["is_premium_signal"]) if pd.notna(row["is_premium_signal"]) else False,
            "premium_score": int(row["premium_score"]) if pd.notna(row["premium_score"]) else 0,
            "policy_version": POLICY_VERSION,
            "policy_gate": POLICY_GATE,
            "is_skipped": is_skipped,
            "skip_reason": skip_reason,
            "VIX_at_entry": float(vix_level) if vix_level is not None else None,
            "SPY_trend_state": spy_trend,
            "vix_5d_delta_entry": float(vix_5d_delta) if vix_5d_delta is not None else None,
            "recommended_dte": int(row["recommended_dte"]),
            "recommended_volume": int(row["recommended_volume"]),
            "recommended_oi": int(row["recommended_oi"]),
            "recommended_spread_pct": float(row["recommended_spread_pct"]),
            # Execution defaults (will be updated if not skipped)
            "entry_timestamp": None,
            "entry_price": None,
            "target_price": None,
            "stop_price": None,
            "exit_timestamp": None,
            "exit_reason": "SKIPPED" if is_skipped else None,
            "realized_return_pct": None,
            # Benchmarking & regime context — populated inline during simulation.
            # All remain None for skipped rows and on fetch failure (non-blocking).
            "iv_rank_entry": None,
            "iv_percentile_entry": None,
            "hv_20d_entry": None,
            "underlying_entry_price": None,
            "underlying_exit_price": None,
            "underlying_return": None,
            "spy_entry_price": None,
            "spy_exit_price": None,
            "spy_return_over_window": None,
        }
        
        # 3. Simulate Execution
        if not is_skipped:
            exp_date = row["recommended_expiration"].date() if isinstance(row["recommended_expiration"], pd.Timestamp) or isinstance(row["recommended_expiration"], datetime) else row["recommended_expiration"]
            opt_ticker = build_polygon_ticker(row["ticker"], exp_date, row["direction"], float(row["recommended_strike"]))
            
            # V5.3: entry 10:00 ET day-1, hold 3 trading days, exit 15:50 ET day-3.
            # HOLD_DAYS is the number of trading days held inclusive of entry_day.
            # day-1 == entry_day, day-3 == get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)
            exit_day = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)

            bars = fetch_minute_bars(opt_ticker, entry_day, exit_day)
            time.sleep(0.2)

            entry_dt = datetime.combine(entry_day, datetime.strptime(ENTRY_HHMM, "%H:%M").time())
            entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
            timeout_dt = datetime.combine(exit_day, datetime.strptime(EXIT_HHMM, "%H:%M").time())
            timeout_ts_ms = int(est.localize(timeout_dt).timestamp() * 1000)

            # Find the entry bar. Prefer a bar at-or-after 10:00 ET, but fall
            # back to the most recent bar before 10:00 as a price proxy rather
            # than throwing the whole trade away. Only mark INVALID_LIQUIDITY
            # when entry_day genuinely has zero printed bars.
            entry_day_bars = [b for b in bars
                              if datetime.fromtimestamp(b["t"]/1000, tz=est).date() == entry_day]
            entry_bar = None
            if entry_day_bars:
                after_or_at = [b for b in entry_day_bars if b["t"] >= entry_ts_ms]
                if after_or_at:
                    entry_bar = after_or_at[0]
                else:
                    before = [b for b in entry_day_bars if b["t"] < entry_ts_ms]
                    entry_bar = before[-1] if before else None

            if not entry_bar or entry_bar.get("v", 0) == 0:
                record["exit_reason"] = "INVALID_LIQUIDITY"
            else:
                base_entry = entry_bar["c"] * 1.02  # 2% Base Slippage
                # V5.3: -60% option stop AND +80% option target.
                stop = base_entry * (1.0 - STOP_PCT)
                target = base_entry * (1.0 + TARGET_PCT)

                record["entry_timestamp"] = datetime.fromtimestamp(entry_bar["t"]/1000, tz=est).isoformat()
                record["entry_price"] = base_entry
                record["target_price"] = target
                record["stop_price"] = stop

                # ---- Benchmarking fetches (non-blocking; null on any failure) ----
                # Fetched per-signal at entry time. The stock bars are reused
                # for the exit-side lookup after the simulation loop.
                stock_bars_for_trade: list = []
                spy_bars_for_trade: list = []
                try:
                    stock_bars_for_trade = fetch_minute_bars(
                        row["ticker"], entry_day, exit_day
                    )
                    time.sleep(0.1)
                    price = bctx.find_price_at_or_after(
                        stock_bars_for_trade, entry_bar["t"]
                    )
                    record["underlying_entry_price"] = price
                except Exception as e:
                    logger.warning(f"underlying_entry_price fetch failed for {row['ticker']}: {e}")

                try:
                    spy_bars_for_trade = bctx.get_spy_bars_cached(entry_day, exit_day)
                    record["spy_entry_price"] = bctx.find_price_at_or_after(
                        spy_bars_for_trade, entry_bar["t"]
                    )
                except Exception as e:
                    logger.warning(f"spy_entry_price fetch failed: {e}")

                try:
                    ivr, ivp, hv = bctx.fetch_underlying_context(row["ticker"], entry_day)
                    record["iv_rank_entry"] = ivr
                    record["iv_percentile_entry"] = ivp
                    record["hv_20d_entry"] = hv
                except Exception as e:
                    logger.warning(f"underlying context fetch failed for {row['ticker']}: {e}")
                # ------------------------------------------------------------------

                entry_idx = bars.index(entry_bar)
                exit_reason = "TIMEOUT"
                exit_price = None
                exit_ts = None

                # V5.3 bar walk: three exits in precedence order.
                #   TIMEOUT — first bar at-or-after 15:50 ET on exit_day
                #   STOP    — option low pierces -60% threshold
                #   TARGET  — option high pierces +80% threshold
                # If stop and target hit on the same bar, STOP wins (we can't
                # know intrabar sequencing; assume worst case). Track the most
                # recent bar at-or-before timeout_ts_ms so that on TIMEOUT we
                # price off the last in-window print.
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

                    hit_stop = b["l"] <= stop
                    hit_target = b["h"] >= target
                    if hit_stop:
                        # STOP takes precedence over TARGET on ambiguous bars.
                        exit_reason = "STOP"
                        exit_price = stop
                        exit_ts = b_ts
                        break
                    if hit_target:
                        exit_reason = "TARGET"
                        exit_price = target
                        exit_ts = b_ts
                        break

                    # No exit triggered on this bar; remember it as the latest in-window print.
                    last_in_window_bar = b

                if exit_price is None:
                    # The bar walk completed without ever crossing timeout_ts_ms. With
                    # the future-timeout guard above, this should only happen when the
                    # contract simply stopped printing before the timeout boundary; use
                    # the last available in-window bar as the timeout exit price.
                    last = last_in_window_bar if last_in_window_bar is not None else entry_bar
                    exit_reason = "TIMEOUT"
                    exit_price = last["c"]
                    exit_ts = last["t"]
                    
                ret = (exit_price - base_entry) / base_entry

                record["exit_reason"] = exit_reason
                record["exit_timestamp"] = datetime.fromtimestamp(exit_ts/1000, tz=est).isoformat()
                record["realized_return_pct"] = float(ret)

                # ---- Benchmarking exit-side fetches (non-blocking) ----
                # Reuse the stock and SPY bar lists fetched at entry time.
                try:
                    stock_exit_px = bctx.find_price_at_or_before(
                        stock_bars_for_trade, exit_ts
                    )
                    record["underlying_exit_price"] = stock_exit_px
                    stock_entry_px = record.get("underlying_entry_price")
                    if (
                        stock_entry_px is not None
                        and stock_exit_px is not None
                        and stock_entry_px > 0
                    ):
                        raw = (stock_exit_px - stock_entry_px) / stock_entry_px
                        sign = 1.0 if str(row["direction"]).upper() == "BULLISH" else -1.0
                        record["underlying_return"] = float(sign * raw)
                except Exception as e:
                    logger.warning(f"underlying_exit fetch failed for {row['ticker']}: {e}")

                try:
                    spy_exit_px = bctx.find_price_at_or_before(
                        spy_bars_for_trade, exit_ts
                    )
                    record["spy_exit_price"] = spy_exit_px
                    spy_entry_px = record.get("spy_entry_price")
                    if (
                        spy_entry_px is not None
                        and spy_exit_px is not None
                        and spy_entry_px > 0
                    ):
                        record["spy_return_over_window"] = float(
                            (spy_exit_px - spy_entry_px) / spy_entry_px
                        )
                except Exception as e:
                    logger.warning(f"spy_exit fetch failed: {e}")
                # --------------------------------------------------------

        records_to_insert.append(record)
        
    # 4. Write to BigQuery — idempotent: delete any existing rows for this
    # scan_date in LEDGER_TABLE, then load the new ones via a load job.
    # We use a load job (not streaming insert_rows_json) so the new rows do not
    # land in BigQuery's streaming buffer, which would block the DELETE on a
    # subsequent re-trigger of the same scan_date for ~90 minutes.
    if records_to_insert:
        # Convert date to string for BQ load
        for r in records_to_insert:
            if isinstance(r["scan_date"], date):
                r["scan_date"] = r["scan_date"].isoformat()

        # Idempotency: delete any prior rows for this scan_date in the canonical ledger.
        delete_query = f'DELETE FROM `{LEDGER_TABLE}` WHERE scan_date = "{target_date.isoformat()}"'
        try:
            client.query(delete_query).result()
            logger.info(f"Deleted any prior rows for scan_date={target_date} in {LEDGER_TABLE}")
        except Exception as e:
            # Most likely cause: prior rows are still in the streaming buffer from a
            # very recent insert. With load jobs (below) this should not happen on
            # repeat triggers, but legacy data inserted via streaming may still trip
            # this on the first run after deploy. Surface the error rather than
            # silently double-writing.
            logger.error(f"Pre-write DELETE failed for {LEDGER_TABLE} scan_date={target_date}: {e}")
            return False, f"Pre-write DELETE failed: {e}"

        # Load via a load job (NOT streaming) so the rows don't sit in streaming buffer.
        import io
        jsonl = "\n".join(json.dumps(r, default=str) for r in records_to_insert)
        load_job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )
        load_job = client.load_table_from_file(
            io.BytesIO(jsonl.encode("utf-8")),
            LEDGER_TABLE,
            job_config=load_job_config,
        )
        load_job.result()
        logger.info(f"Loaded {len(records_to_insert)} records into {LEDGER_TABLE}")
        return True, f"Successfully inserted {len(records_to_insert)} records."
    return True, "No records to insert."

def get_previous_trading_day(base_date: date) -> date:
    start_date = base_date - timedelta(days=10)
    schedule = nyse.schedule(start_date=start_date, end_date=base_date)
    valid_dates = [d.date() for d in schedule.index if d.date() < base_date]
    return valid_dates[-1] if valid_dates else None

def get_canonical_scan_date(today: date = None) -> date:
    """Return the most recent scan_date whose V5.3 hold window has fully closed
    before `today`.

    A signal scanned on date X enters at next_trading_day(X) (= day-1) and
    times out at nth_next_trading_day(entry, HOLD_DAYS - 1) (= day-N). For the
    trade to be safely simulated, the timeout day must be strictly before
    `today`. We walk back (HOLD_DAYS + 1) trading days from today: 1 for the
    entry-day lag, and HOLD_DAYS - 1 for the span from day-1 to day-N, plus 1
    for the "strictly before today" guard.

    This is the function the daily cron uses when no explicit target_date is
    provided.
    """
    if today is None:
        today = datetime.now(est).date()
    d = today
    # HOLD_DAYS=3: walk back 4 trading days (entry + 2 more hold days + 1 buffer)
    for _ in range(HOLD_DAYS + 1):
        d = get_previous_trading_day(d)
    return d

def run_iv_cache_update():
    """Daily IV cache refresh — one row per underlying per as_of_date in
    `polygon_iv_history`. Fetches the trailing-30-day signal watchlist from
    `overnight_signals_enriched`, snapshots each underlying's options chain via
    Polygon, extracts the nearest-to-30-DTE ATM call's IV, and appends rows.

    Idempotent per as_of_date: DELETE-then-LOAD, matching the main trader's
    write pattern. Non-blocking per-ticker: any single ticker failing logs a
    warning and the batch continues.
    """
    client = bigquery.Client(project=PROJECT_ID)
    today_et = datetime.now(est).date()

    # Watchlist = any ticker seen in overnight_signals_enriched in the last 30 days.
    # This is the natural "tickers we might trade tomorrow" universe.
    wl_sql = f"""
    SELECT DISTINCT ticker
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE scan_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
      AND ticker IS NOT NULL
    """
    watchlist_df = client.query(wl_sql).to_dataframe()
    tickers = sorted(watchlist_df["ticker"].dropna().unique().tolist())
    logger.info(f"IV cache watchlist: {len(tickers)} tickers")

    if not tickers:
        return True, {"rows_written": 0, "tickers_attempted": 0, "tickers_with_iv": 0}

    rows: list[dict] = []
    fetched_at_iso = datetime.now(est).isoformat()
    n_attempted = 0
    n_with_iv = 0
    for tkr in tickers:
        n_attempted += 1
        try:
            chain = bctx.fetch_options_chain_for_underlying(tkr, max_days=60)
            atm = bctx.compute_atm_iv_for_dte(chain, target_dte=30)
            if atm is None:
                # Still record a row so we know the cache job ran this day,
                # but with NULL iv. Prevents confusing "ticker missing" vs
                # "job failed" downstream.
                rows.append({
                    "ticker": tkr,
                    "as_of_date": today_et.isoformat(),
                    "atm_iv_30d": None,
                    "dte_used": None,
                    "strike_used": None,
                    "underlying_px": None,
                    "contract_symbol": None,
                    "source": "polygon_snapshot",
                    "fetched_at": fetched_at_iso,
                })
                continue
            n_with_iv += 1
            rows.append({
                "ticker": tkr,
                "as_of_date": today_et.isoformat(),
                "atm_iv_30d": atm["atm_iv_30d"],
                "dte_used": atm["dte_used"],
                "strike_used": atm["strike_used"],
                "underlying_px": atm["underlying_px"],
                "contract_symbol": atm["contract_symbol"],
                "source": "polygon_snapshot",
                "fetched_at": fetched_at_iso,
            })
        except Exception as e:
            logger.warning(f"IV cache: {tkr} failed: {e}")
            continue

    if not rows:
        return True, {"rows_written": 0, "tickers_attempted": n_attempted, "tickers_with_iv": 0}

    iv_table = bctx.IV_HISTORY_TABLE
    delete_sql = f'DELETE FROM `{iv_table}` WHERE as_of_date = "{today_et.isoformat()}"'
    try:
        client.query(delete_sql).result()
        logger.info(f"Deleted prior rows for as_of_date={today_et} in {iv_table}")
    except Exception as e:
        logger.error(f"Pre-write DELETE failed for {iv_table}: {e}")
        return False, f"Pre-write DELETE failed: {e}"

    import io
    jsonl = "\n".join(json.dumps(r, default=str) for r in rows)
    load_job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    load_job = client.load_table_from_file(
        io.BytesIO(jsonl.encode("utf-8")),
        iv_table,
        job_config=load_job_config,
    )
    load_job.result()
    logger.info(
        f"IV cache loaded {len(rows)} rows into {iv_table} "
        f"(attempted={n_attempted}, with_iv={n_with_iv})"
    )
    return True, {
        "rows_written": len(rows),
        "tickers_attempted": n_attempted,
        "tickers_with_iv": n_with_iv,
    }


@app.route("/cache_iv", methods=["POST", "GET"])
def trigger_iv_cache():
    """Daily IV cache refresh endpoint — hit by Cloud Scheduler at 16:30 ET."""
    try:
        success, result = run_iv_cache_update()
        if success:
            return jsonify({"status": "success", **result}), 200
        return jsonify({"status": "error", "message": str(result)}), 500
    except Exception as e:
        logger.error(f"Error in IV cache endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/", methods=["GET", "POST"])
def trigger_paper_trading():
    try:
        # Check if a specific target date is passed via JSON payload
        req_data = request.get_json(silent=True) or {}
        target_date_str = req_data.get("target_date")

        if target_date_str:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        else:
            # Default: process the most recent scan_date whose 3-day hold window
            # has fully closed before today.
            target_date = get_canonical_scan_date()

        success, msg = run_forward_paper_trading(target_date)
        if success:
            return jsonify({"status": "success", "message": msg}), 200
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        logger.error(f"Error in paper trading endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)





