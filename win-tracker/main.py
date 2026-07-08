"""
Win Tracker — Signal Performance Tracking
Cloud Run service: win-tracker
Project: profitscout-fida8

Checks enriched overnight signals against actual price movement
over a 3-TRADING-DAY window. Tracks peak return, classifies by tier,
and posts strong wins to X.
"""

import json
import logging
import os
import time
import concurrent.futures
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import yfinance as yf
from flask import Flask, jsonify
from google.cloud import bigquery, firestore
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
DATASET = "profit_scout"
ENRICHED_TABLE = f"{PROJECT_ID}.{DATASET}.overnight_signals_enriched"
PERFORMANCE_TABLE = f"{PROJECT_ID}.{DATASET}.signal_performance"
LEDGER_TABLE = f"{PROJECT_ID}.{DATASET}.forward_paper_ledger"
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "").strip()

# Park watchdog — one-shot Mailgun alerts on engine lifecycle gates.
# Currently watches the 30-trade gate (Evan's documented return trigger).
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "").strip()
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "").strip()
PARK_RECIPIENT = os.getenv("PARK_RECIPIENT", "evan@gammarips.com").strip()
PARK_GATE_30_TRADES = 30

# X posting moved to `x-poster/` service (2026-04-24). This service now
# only tracks signal performance to BQ/Firestore. No X credentials needed.

# Win tier thresholds (based on peak return in right direction)
TIER_NO_DECISION = 1.0    # < 1% = too small to call
TIER_DIRECTIONAL = 1.0    # >= 1% = directional win
TIER_SOLID = 3.0           # >= 3% = solid win
TIER_STRONG = 5.0          # >= 5% = strong win

POST_MIN_SCORE = 7         # Only post wins for signals scored 7+
POST_MIN_TIER = "strong"   # Only post strong wins to X
MAX_TRADING_DAYS = 3       # Track over 3 trading day window

# US Market holidays 2026 (add as needed)
HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
    "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25",
}


def is_trading_day(d: date) -> bool:
    """Check if a date is a trading day (not weekend, not holiday)."""
    if d.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    if d.isoformat() in HOLIDAYS_2026:
        return False
    return True


def count_trading_days(from_date: date, to_date: date) -> int:
    """Count trading days between two dates (exclusive of from_date)."""
    count = 0
    current = from_date + timedelta(days=1)
    while current <= to_date:
        if is_trading_day(current):
            count += 1
        current += timedelta(days=1)
    return count


def get_trading_days_after(from_date: date, n_days: int) -> list[date]:
    """Get the next N trading days after from_date."""
    days = []
    current = from_date + timedelta(days=1)
    while len(days) < n_days:
        if is_trading_day(current):
            days.append(current)
        current += timedelta(days=1)
        if current > from_date + timedelta(days=30):  # safety limit
            break
    return days


def classify_win(peak_return_pct: float, direction: str) -> str:
    """
    Classify signal result based on peak favorable return within window.
    Returns: 'strong', 'solid', 'directional', 'no_decision', 'loss'
    """
    # Peak return should be in the right direction
    if direction == "BULLISH":
        favorable = peak_return_pct  # positive is good
    else:
        favorable = -peak_return_pct  # negative price move is good for bears

    if favorable >= TIER_STRONG:
        return "strong"
    elif favorable >= TIER_SOLID:
        return "solid"
    elif favorable >= TIER_DIRECTIONAL:
        return "directional"
    elif favorable >= 0:
        return "no_decision"
    else:
        return "loss"


def send_park_email(subject: str, body_text: str) -> bool:
    """Mailgun send to operator for park-mode lifecycle alerts. Returns True on success."""
    if not (MAILGUN_API_KEY and MAILGUN_DOMAIN):
        logger.info("Mailgun not configured; skipping park alert send.")
        return False
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": f"GammaRips Park Watchdog <mailgun@{MAILGUN_DOMAIN}>",
        "to": [PARK_RECIPIENT],
        "subject": subject,
        "text": body_text,
    }
    try:
        resp = requests.post(url, auth=auth, data=data, timeout=10)
        resp.raise_for_status()
        logger.info(f"Park alert sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"Park alert email failed: {e}")
        return False


def check_park_gates(bq_client, fs_client):
    """One-shot park alerts. Idempotent via Firestore flags.

    Currently watches the 30-trade gate — the user's documented return trigger.
    Reset by deleting the Firestore flag at park_watchdog/gate_30_alerted.
    """
    flag_ref = fs_client.collection("park_watchdog").document("gate_30_alerted")
    flag_snap = flag_ref.get()
    if flag_snap.exists and flag_snap.to_dict().get("alerted"):
        return  # one-shot — already fired

    try:
        # 30-pick gate (V5.4 cohort, post-2026-05-08 retirement of V5.3).
        # The trader simulates EVERY enriched signal as V7_1_TILTED_GIGO for
        # research; counting raw closed rows would fire spuriously (~80/day).
        # Approximation: COUNT(DISTINCT scan_date) where the ledger has at
        # least one closed V5.4 row. One scan_date == one V5.4 pick day.
        # Better fix is on the EXEC-PLAN backlog: signal-notifier writes a
        # todays_pick_history BQ table that this query JOINs against.
        query = f"""
            SELECT COUNT(DISTINCT scan_date) AS n
            FROM `{LEDGER_TABLE}`
            WHERE realized_return_pct IS NOT NULL
              AND policy_version = 'V7_1_TILTED_GIGO'
        """
        row = next(iter(bq_client.query(query).result()))
        count = int(row["n"])
    except Exception as e:
        logger.warning(f"30-trade gate count query failed (non-fatal): {e}")
        return

    logger.info(f"V5.4 closed-trade count: {count}/{PARK_GATE_30_TRADES}")
    if count < PARK_GATE_30_TRADES:
        return

    subject = "[GammaRips] 30-trade gate reached — return trigger active"
    body_text = (
        f"V5.4 ledger has crossed the {PARK_GATE_30_TRADES} closed paper trades threshold.\n\n"
        f"Closed count: {count}\n"
        f"Policy: V5.4 Agent Ranker\n\n"
        f"You parked GammaRips with this as your return trigger. The track-record\n"
        f"narrative is ready to ship. Time to come back and:\n\n"
        f"1. Pull aggregate stats from forward_paper_ledger.\n"
        f"2. Publish the 30-trade-in-the-books blog post (Wk 9 of the 90-day plan).\n"
        f"3. Open the paid funnel hard via the newsletter to 211+ users.\n"
        f"4. Move the @gammarips X cadence into recap-led mode.\n\n"
        f"This email fires exactly once. Reset the flag in Firestore at\n"
        f"park_watchdog/gate_30_alerted to re-arm.\n"
    )

    if send_park_email(subject, body_text):
        flag_ref.set({
            "alerted": True,
            "count_at_alert": count,
            "alerted_at": firestore.SERVER_TIMESTAMP,
        })


@app.route("/", methods=["GET", "POST"])
def track_signal_performance():
    """Main entry point."""
    bq_client = bigquery.Client(project=PROJECT_ID)
    fs_client = firestore.Client(project=PROJECT_ID)

    # Get enriched signals from past 7 calendar days (covers weekends + holidays)
    signals = get_recent_signals(bq_client, lookback_days=7)
    logger.info(f"Tracking {len(signals)} signals")

    def process_signal(signal):
        ticker = signal["ticker"]
        signal_date = date.fromisoformat(str(signal["scan_date"]))
        direction = signal["direction"]
        signal_score = signal.get("overnight_score", 0)
        signal_price = float(signal.get("underlying_price", 0) or 0)

        if not signal_price or signal_price <= 0:
            return None

        # How many trading days have passed since signal?
        today = date.today()
        trading_days_elapsed = count_trading_days(signal_date, today)

        if trading_days_elapsed < 1:
            return None  # No trading days yet, skip

        # Get daily prices for the trading window
        prices = get_price_history(ticker, signal_date, days_after=MAX_TRADING_DAYS)
        if not prices:
            return None

        # Calculate returns for each trading day
        returns = []
        for p in prices:
            pct = ((p["close"] - signal_price) / signal_price) * 100
            high_pct = ((p["high"] - signal_price) / signal_price) * 100
            low_pct = ((p["low"] - signal_price) / signal_price) * 100
            returns.append({
                "date": p["date"],
                "close": p["close"],
                "pct_change": round(pct, 2),
                "high_pct": round(high_pct, 2),
                "low_pct": round(low_pct, 2),
            })

        # Peak favorable return within window
        if direction == "BULLISH":
            peak_return = max(r["high_pct"] for r in returns)
        else:
            peak_return = min(r["low_pct"] for r in returns)

        # Current (latest) return
        current_return = returns[-1]["pct_change"]
        current_price = returns[-1]["close"]

        # Classify
        tier = classify_win(peak_return, direction)
        is_win = tier in ("strong", "solid", "directional")

        # Is the signal window complete? (3 trading days have passed)
        is_final = trading_days_elapsed >= MAX_TRADING_DAYS

        return {
            "ticker": ticker,
            "scan_date": signal_date.isoformat(),
            "check_date": today.isoformat(),
            "direction": direction,
            "signal_score": signal_score,
            "signal_price": signal_price,
            "current_price": current_price,
            "pct_change": current_return,
            "peak_return": round(peak_return, 2),
            "trading_days_elapsed": trading_days_elapsed,
            "trading_days_tracked": len(returns),
            "is_win": is_win,
            "tier": tier,
            "is_final": is_final,
            "daily_returns": returns,
        }

    results = []
    strong_wins = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_signal, s) for s in signals]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                # Only collect strong wins for X posting
                if (res["tier"] == "strong" and
                    res["signal_score"] >= POST_MIN_SCORE and
                    res["is_final"]):  # Only post after window completes
                    strong_wins.append(res)
            time.sleep(0.01)

    # Write all results to BigQuery + Firestore
    if results:
        write_performance_to_bq(bq_client, results)
        write_performance_to_firestore(fs_client, results)

    # (X posting removed 2026-04-24 — owned by x-poster service now.)

    # Tally by tier
    tier_counts = {}
    for r in results:
        t = r["tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    summary = {
        "signals_tracked": len(results),
        "tiers": tier_counts,
        "win_rate": f"{(sum(1 for r in results if r['is_win']) / len(results) * 100):.1f}%" if results else "N/A",
    }

    logger.info(f"Performance tracking complete: {json.dumps(summary)}")

    # Park watchdog — non-blocking. One-shot lifecycle alerts (30-trade gate etc.).
    # Lives here because win-tracker already runs daily and reads the same ledger.
    try:
        check_park_gates(bq_client, fs_client)
    except Exception as e:
        logger.warning(f"Park gate check failed (non-fatal): {e}")

    return jsonify(summary), 200


def get_recent_signals(bq_client, lookback_days=7):
    """Get enriched signals from past N days."""
    cutoff = (date.today() - timedelta(days=lookback_days)).isoformat()

    query = f"""
    SELECT ticker, scan_date, direction, overnight_score, underlying_price,
           catalyst_type, news_summary, recommended_contract
    FROM `{ENRICHED_TABLE}`
    WHERE scan_date >= '{cutoff}'
      AND overnight_score >= 6
    """
    rows = list(bq_client.query(query).result())
    return [dict(r) for r in rows]


def get_price_history(ticker: str, signal_date: date, days_after: int = 3) -> list[dict]:
    """
    Get daily closing prices for trading days after signal_date.
    Returns up to `days_after` trading days of price data.
    """
    # Calculate end date (signal_date + enough calendar days to cover trading days)
    end_date = signal_date + timedelta(days=days_after * 2 + 5)  # generous buffer
    if end_date > date.today():
        end_date = date.today()

    start_date = signal_date + timedelta(days=1)  # day after signal

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date.isoformat()}/{end_date.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "apiKey": POLYGON_API_KEY}

    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)

            if resp.status_code == 429:
                time.sleep(1 * (attempt + 1))
                continue

            resp.raise_for_status()
            bars = resp.json().get("results", [])

            if not bars:
                return []

            # Convert to clean list, limit to MAX_TRADING_DAYS trading days
            prices = []
            for bar in bars:
                bar_date = datetime.fromtimestamp(bar["t"] / 1000).strftime("%Y-%m-%d")
                if is_trading_day(date.fromisoformat(bar_date)):
                    prices.append({
                        "date": bar_date,
                        "close": bar["c"],
                        "high": bar.get("h", bar["c"]),
                        "low": bar.get("l", bar["c"]),
                    })
                    if len(prices) >= days_after:
                        break

            return prices

        except Exception as e:
            logger.warning(f"Price history attempt {attempt+1} failed for {ticker}: {e}")
            time.sleep(0.5 * (attempt + 1))

    logger.error(f"Price history failed for {ticker} after 3 attempts")
    return []


def write_performance_to_bq(bq_client, results):
    """Write performance results to BigQuery."""
    # Flatten for BQ (remove daily_returns nested field)
    bq_rows = []
    for r in results:
        row = {k: v for k, v in r.items() if k != "daily_returns"}
        bq_rows.append(row)

    table_ref = f"{PROJECT_ID}.{DATASET}.signal_performance"

    # Delete existing rows for these signals to avoid duplicates
    scan_dates = list(set(r["scan_date"] for r in results))
    for sd in scan_dates:
        try:
            delete_q = f"DELETE FROM `{table_ref}` WHERE scan_date = '{sd}'"
            bq_client.query(delete_q).result()
        except Exception as e:
            logger.warning(f"BQ delete failed for {sd}: {e}")

    errors = bq_client.insert_rows_json(table_ref, bq_rows)
    if errors:
        logger.error(f"BQ insert errors: {errors}")
    else:
        logger.info(f"Wrote {len(bq_rows)} performance rows to BQ")


def write_performance_to_firestore(fs_client, results):
    """Write performance to Firestore for webapp display."""
    batch = fs_client.batch()
    count = 0
    for r in results:
        doc_id = f"{r['scan_date']}_{r['ticker']}"
        ref = fs_client.collection("signal_performance").document(doc_id)
        # Store clean version (no daily_returns in Firestore to save space)
        doc_data = {k: v for k, v in r.items() if k != "daily_returns"}
        batch.set(ref, doc_data, merge=True)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = fs_client.batch()
    batch.commit()
    logger.info(f"Wrote {count} performance docs to Firestore")


def _calc_premium_fields(row: dict) -> dict:
    """
    Calculate all premium signal fields for a given signal.
    Returns dict with all premium fields ready to merge into the row.
    
    Based on deep analysis of 287 backfilled signals.
    Each pattern independently showed 80%+ win rate.
    """
    flow_intent = (row.get("flow_intent") or "").upper()
    risk_reward = float(row.get("risk_reward_ratio") or 0)
    move_overdone = bool(row.get("move_overdone", True))
    call_vol_oi = float(row.get("call_vol_oi_ratio") or 0)
    put_vol_oi = float(row.get("put_vol_oi_ratio") or 0)
    direction = (row.get("direction") or "").upper()
    atr_move = float(row.get("atr_normalized_move") or 0)
    
    # Individual pattern flags
    hedge = (flow_intent == "HEDGING")
    high_rr = (risk_reward > 2.0 and not move_overdone)
    bull_flow = (call_vol_oi > 1.5 and direction == "BULLISH" and not move_overdone)
    high_atr = (atr_move > 2.0)
    bear_flow = (put_vol_oi > 2.0 and direction == "BEARISH")
    
    score = sum([hedge, high_rr, bull_flow, high_atr, bear_flow])
    is_tradeable = (hedge and high_rr) or (hedge and high_atr)
    
    return {
        "premium_hedge": hedge,
        "premium_high_rr": high_rr,
        "premium_bull_flow": bull_flow,
        "premium_high_atr": high_atr,
        "premium_bear_flow": bear_flow,
        "premium_score": score,
        "is_premium_signal": score >= 1,  # TRUE if ANY pattern matches
        "is_tradeable": is_tradeable,
    }

@app.route("/backfill-performance", methods=["GET", "POST"])
def run_backfill_performance():
    """Daily job to backfill performance columns on overnight_signals_enriched."""
    bq_client = bigquery.Client(project=PROJECT_ID)
    
    query = f"""
    SELECT ticker, scan_date, direction, underlying_price, 
           flow_intent, risk_reward_ratio, move_overdone, call_vol_oi_ratio
    FROM `{ENRICHED_TABLE}`
    WHERE performance_updated IS NULL
      AND scan_date <= DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)
    """
    try:
        job = bq_client.query(query)
        signals = [dict(row) for row in job.result()]
    except Exception as e:
        logger.error(f"Failed to fetch signals for backfill: {e}")
        return jsonify({"error": str(e)}), 500

    if not signals:
        logger.info("No signals to backfill.")
        return jsonify({"status": "success", "message": "No signals to backfill."}), 200

    logger.info(f"Found {len(signals)} signals to backfill.")
    
    tickers = list(set([s['ticker'] for s in signals]))
    min_date = min([s['scan_date'] for s in signals])
    max_date = max([s['scan_date'] for s in signals])
    
    start_date = min_date.strftime("%Y-%m-%d")
    end_date = (max_date + timedelta(days=10)).strftime("%Y-%m-%d")
    
    logger.info(f"Fetching yfinance data for {len(tickers)} tickers from {start_date} to {end_date}")
    
    try:
        data = yf.download(tickers, start=start_date, end=end_date)
    except Exception as e:
        logger.error(f"Failed to fetch data from yfinance: {e}")
        return jsonify({"error": str(e)}), 500

    updates = []
    
    for s in signals:
        ticker = s['ticker']
        scan_date = s['scan_date']
        direction = s['direction']
        underlying_price = s['underlying_price']
        
        if pd.isna(underlying_price) or underlying_price <= 0:
            continue

        try:
            if len(tickers) == 1:
                ticker_data = data
            else:
                if ticker not in data.columns.levels[1]:
                    continue
                ticker_data = data.xs(ticker, axis=1, level=1)
                
            ticker_data = ticker_data.dropna(subset=['Close'])
            future_data = ticker_data[ticker_data.index.date > scan_date]
            
            if len(future_data) < 3:
                continue
                
            t1, t2, t3 = future_data.iloc[0], future_data.iloc[1], future_data.iloc[2]
            
            t1_close = t1['Close']
            t2_close = t2['Close']
            t3_close = t3['Close']
            
            t1_high, t2_high, t3_high = t1['High'], t2['High'], t3['High']
            t1_low, t2_low, t3_low = t1['Low'], t2['Low'], t3['Low']
            
            next_day_pct = ((t1_close - underlying_price) / underlying_price) * 100
            day2_pct = ((t2_close - underlying_price) / underlying_price) * 100
            day3_pct = ((t3_close - underlying_price) / underlying_price) * 100
            
            if direction == "BULLISH":
                peak_return_3d = ((max(t1_high, t2_high, t3_high) - underlying_price) / underlying_price) * 100
            else:
                peak_return_3d = ((underlying_price - min(t1_low, t2_low, t3_low)) / underlying_price) * 100
                
            if peak_return_3d >= 5.0:
                outcome_tier = "home_run"
            elif peak_return_3d >= 3.0:
                outcome_tier = "strong"
            elif peak_return_3d >= 1.0:
                outcome_tier = "directional"
            elif peak_return_3d >= 0.0:
                outcome_tier = "flat"
            else:
                outcome_tier = "wrong"
                
            is_win = bool(peak_return_3d >= 1.0)
            
            premium_fields = _calc_premium_fields(s)
            
            updates.append({
                'ticker': ticker,
                'scan_date': scan_date.strftime("%Y-%m-%d"),
                'next_day_close': float(t1_close),
                'next_day_pct': float(next_day_pct),
                'day2_close': float(t2_close),
                'day2_pct': float(day2_pct),
                'day3_close': float(t3_close),
                'day3_pct': float(day3_pct),
                'peak_return_3d': float(peak_return_3d),
                'outcome_tier': outcome_tier,
                'is_win': is_win,
                'is_premium_signal': premium_fields['is_premium_signal'],
                'premium_score': premium_fields['premium_score'],
                'premium_hedge': premium_fields['premium_hedge'],
                'premium_high_rr': premium_fields['premium_high_rr'],
                'premium_bull_flow': premium_fields['premium_bull_flow'],
                'premium_high_atr': premium_fields['premium_high_atr'],
                'premium_bear_flow': premium_fields['premium_bear_flow'],
                'is_tradeable': premium_fields['is_tradeable'],
                'performance_updated': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            logger.warning(f"Error processing {ticker} on {scan_date}: {e}")
            continue

    if not updates:
        logger.info("No valid updates to process after analyzing data.")
        return jsonify({"status": "success", "message": "No valid updates could be processed."}), 200

    logger.info(f"Writing {len(updates)} updates back to BigQuery...")
    temp_table_id = f"{PROJECT_ID}.{DATASET}.temp_perf_updates"
    
    schema = [
        bigquery.SchemaField("ticker", "STRING"),
        bigquery.SchemaField("scan_date", "DATE"),
        bigquery.SchemaField("next_day_close", "FLOAT"),
        bigquery.SchemaField("next_day_pct", "FLOAT"),
        bigquery.SchemaField("day2_close", "FLOAT"),
        bigquery.SchemaField("day2_pct", "FLOAT"),
        bigquery.SchemaField("day3_close", "FLOAT"),
        bigquery.SchemaField("day3_pct", "FLOAT"),
        bigquery.SchemaField("peak_return_3d", "FLOAT"),
        bigquery.SchemaField("outcome_tier", "STRING"),
        bigquery.SchemaField("is_win", "BOOLEAN"),
        bigquery.SchemaField("is_premium_signal", "BOOLEAN"),
        bigquery.SchemaField("premium_score", "INTEGER"),
        bigquery.SchemaField("premium_hedge", "BOOLEAN"),
        bigquery.SchemaField("premium_high_rr", "BOOLEAN"),
        bigquery.SchemaField("premium_bull_flow", "BOOLEAN"),
        bigquery.SchemaField("premium_high_atr", "BOOLEAN"),
        bigquery.SchemaField("premium_bear_flow", "BOOLEAN"),
        bigquery.SchemaField("is_tradeable", "BOOLEAN"),
        bigquery.SchemaField("performance_updated", "TIMESTAMP"),
    ]
    
    job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_TRUNCATE")
    
    try:
        load_job = bq_client.load_table_from_json(updates, temp_table_id, job_config=job_config)
        load_job.result()
        
        merge_query = f"""
        MERGE `{ENRICHED_TABLE}` T
        USING `{temp_table_id}` S
        ON T.ticker = S.ticker AND T.scan_date = S.scan_date
        WHEN MATCHED THEN
          UPDATE SET 
            next_day_close = S.next_day_close,
            next_day_pct = S.next_day_pct,
            day2_close = S.day2_close,
            day2_pct = S.day2_pct,
            day3_close = S.day3_close,
            day3_pct = S.day3_pct,
            peak_return_3d = S.peak_return_3d,
            outcome_tier = S.outcome_tier,
            is_win = S.is_win,
            is_premium_signal = S.is_premium_signal,
            premium_score = S.premium_score,
            premium_hedge = S.premium_hedge,
            premium_high_rr = S.premium_high_rr,
            premium_bull_flow = S.premium_bull_flow,
            premium_high_atr = S.premium_high_atr,
            premium_bear_flow = S.premium_bear_flow,
            is_tradeable = S.is_tradeable,
            performance_updated = S.performance_updated
        """
        merge_job = bq_client.query(merge_query)
        merge_job.result()
        logger.info(f"Successfully merged {len(updates)} rows.")
        return jsonify({"status": "success", "updated_rows": len(updates)}), 200
        
    except Exception as e:
        logger.error(f"Error updating BigQuery: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/pool_outcomes", methods=["GET", "POST"])
def compute_pool_outcomes():
    """Aggregate the labeled pool substrate into Firestore pool_outcomes/current.

    Feeds the public Track Record page (pool outcomes replaced the pick-cohort
    scorecard, owner call 2026-07-03). Read-only against BigQuery; writes ONE
    idempotent Firestore doc recomputed from BQ truth, so an unauthenticated
    re-trigger can only refresh it, never poison it. Return values are
    FRACTIONS (0.21 = +21%) despite the legacy *_pct column names.
    """
    outcomes_table = f"{PROJECT_ID}.{DATASET}.enriched_option_outcomes"
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)
        fs_client = firestore.Client(project=PROJECT_ID)

        # Per-row sim-version tags are the source of truth for label mechanics
        # (never inferred from policy_version) — aggregate ONLY matching rows so
        # a future mechanics change can't silently blend into the public number.
        # HISTORY CAVEAT: same-day rows written before 07-01 predate tagging and
        # carry NULL label_sim_version. Verified 2026-07-03: the NULL cohort's
        # distribution (avg -4.4%/day, WR 29.8%) matches the documented GIGO
        # same-day composite and is distinct from the tagged V6 3-day arm
        # (avg -3.6%, WR 41%) — so NULL is treated as legacy same-day. New rows
        # are stamped by the fpt label pass; any FUTURE mechanics change gets a
        # new tag and stays excluded here by construction.
        sameday_sim = "SAMEDAY_V7_1_GIGO"
        sameday_match = f"(label_sim_version = '{sameday_sim}' OR label_sim_version IS NULL)"
        threeday_sim = "HOLD3D_V6_LEGACY_8060"
        opp_sim = "OPP_MFE_MAE_V1"
        # Full-life (surfaced -> expiration) surface — the scorecard-redesign
        # centerpiece (owner-approved 2026-07-08). DEPENDS on the life_* columns
        # existing in enriched_option_outcomes (created by forward-paper-trader's
        # schema-ensure / the life backfill) — deploy order: substrate first.
        # Fixed bucket edges are part of the public contract: the webapp renders
        # these bucket labels verbatim from the doc.
        life_sim = "LIFE_TO_EXPIRY_V1"
        life_match = f"life_sim_version = '{life_sim}'"
        peak_edges = [(None, 0.05), (0.05, 0.20), (0.20, 0.40), (0.40, 0.70),
                      (0.70, 1.00), (1.00, 2.00), (2.00, None)]
        expiry_edges = [(None, -0.90), (-0.90, -0.50), (-0.50, 0.0), (0.0, 0.50),
                        (0.50, 1.00), (1.00, 2.00), (2.00, None)]

        def _bucket_countifs(col: str, edges, prefix: str) -> str:
            parts = []
            for i, (lo, hi) in enumerate(edges):
                cond = f"{life_match} AND {col} IS NOT NULL"
                if lo is not None:
                    cond += f" AND {col} >= {lo}"
                if hi is not None:
                    cond += f" AND {col} < {hi}"
                parts.append(f"COUNTIF({cond}) AS {prefix}_{i}")
            return ",\n          ".join(parts)

        query = f"""
        SELECT
          COUNTIF({life_match} AND life_status IS NOT NULL) AS life_processed,
          COUNTIF({life_match} AND life_status = 'NO_ENTRY') AS life_no_entry,
          COUNTIF({life_match} AND life_peak_return IS NOT NULL) AS life_n_peak,
          COUNTIF({life_match} AND life_expiry_return IS NOT NULL) AS life_n_expiry,
          CAST(MIN(IF({life_match} AND life_peak_return IS NOT NULL, scan_date, NULL)) AS STRING) AS life_first_scan_date,
          CAST(MAX(IF({life_match} AND life_peak_return IS NOT NULL, scan_date, NULL)) AS STRING) AS life_last_scan_date,
          ROUND(APPROX_QUANTILES(IF({life_match}, life_peak_return, NULL), 100)[OFFSET(50)], 4) AS life_peak_median,
          ROUND(APPROX_QUANTILES(IF({life_match}, life_peak_return, NULL), 100)[OFFSET(75)], 4) AS life_peak_p75,
          ROUND(APPROX_QUANTILES(IF({life_match}, life_peak_return, NULL), 100)[OFFSET(90)], 4) AS life_peak_p90,
          ROUND(APPROX_QUANTILES(IF({life_match}, life_trough_return, NULL), 100)[OFFSET(50)], 4) AS life_trough_median,
          ROUND(APPROX_QUANTILES(IF({life_match}, life_trough_return, NULL), 100)[OFFSET(10)], 4) AS life_trough_p10,
          ROUND(APPROX_QUANTILES(IF({life_match}, life_expiry_return, NULL), 100)[OFFSET(50)], 4) AS life_expiry_median,
          COUNTIF({life_match} AND life_peak_return >= 0.40) AS life_peak_ge_40,
          COUNTIF({life_match} AND life_peak_return >= 1.00) AS life_peak_ge_100,
          {_bucket_countifs("life_peak_return", peak_edges, "lpb")},
          {_bucket_countifs("life_expiry_return", expiry_edges, "leb")},
          COUNT(*) AS contracts_total,
          COUNT(DISTINCT scan_date) AS scan_days,
          CAST(MIN(scan_date) AS STRING) AS first_scan_date,
          CAST(MAX(scan_date) AS STRING) AS last_scan_date,
          COUNTIF(realized_return_pct IS NOT NULL
            AND {sameday_match}) AS labeled_sameday,
          COUNTIF(realized_return_pct_3d IS NOT NULL
            AND label_3d_sim_version = '{threeday_sim}') AS labeled_3d,
          COUNTIF(opp_peak_return IS NOT NULL
            AND opp_sim_version = '{opp_sim}') AS with_opp_surface,
          ROUND(AVG(IF({sameday_match}, realized_return_pct, NULL)), 4) AS bracket_avg_return,
          ROUND(COUNTIF({sameday_match} AND realized_return_pct > 0)
            / NULLIF(COUNTIF({sameday_match} AND realized_return_pct IS NOT NULL), 0), 4) AS bracket_win_rate,
          ROUND(AVG(IF(label_3d_sim_version = '{threeday_sim}', realized_return_pct_3d, NULL)), 4) AS bracket_3d_avg_return,
          ROUND(COUNTIF(label_3d_sim_version = '{threeday_sim}' AND realized_return_pct_3d > 0)
            / NULLIF(COUNTIF(label_3d_sim_version = '{threeday_sim}' AND realized_return_pct_3d IS NOT NULL), 0), 4) AS bracket_3d_win_rate,
          ROUND(APPROX_QUANTILES(IF(opp_sim_version = '{opp_sim}', opp_peak_return, NULL), 100)[OFFSET(50)], 4) AS opp_peak_median,
          ROUND(APPROX_QUANTILES(IF(opp_sim_version = '{opp_sim}', opp_peak_return, NULL), 100)[OFFSET(75)], 4) AS opp_peak_p75,
          ROUND(APPROX_QUANTILES(IF(opp_sim_version = '{opp_sim}', opp_peak_return, NULL), 100)[OFFSET(90)], 4) AS opp_peak_p90,
          ROUND(APPROX_QUANTILES(IF(opp_sim_version = '{opp_sim}', opp_trough_return, NULL), 100)[OFFSET(50)], 4) AS opp_trough_median,
          ROUND(APPROX_QUANTILES(IF(opp_sim_version = '{opp_sim}', opp_trough_return, NULL), 100)[OFFSET(10)], 4) AS opp_trough_p10
        FROM `{outcomes_table}`
        """
        row = dict(next(iter(bq_client.query(query).result())))

        # Fail loud on an empty/degraded substrate instead of publishing zeros.
        if not row.get("contracts_total") or not row.get("labeled_sameday"):
            logger.error(f"pool_outcomes: degraded substrate, refusing write: {row}")
            # 503 so Cloud Scheduler records a FAILURE (retry + alerting)
            # instead of letting the public doc go silently stale.
            return jsonify({"status": "refused", "reason": "degraded substrate", "row": str(row)}), 503

        # Fold the flat life_*/lpb_*/leb_* query fields into ONE nested map so
        # the webapp reads doc.life.* and the legacy top-level fields stay
        # byte-compatible for any existing reader.
        life_raw = {k: row.pop(k) for k in list(row.keys())
                    if k.startswith(("life_", "lpb_", "leb_"))}
        peak_bucket_labels = ["<+5%", "+5–20%", "+20–40%", "+40–70%",
                              "+70–100%", "+100–200%", "+200%+"]
        expiry_bucket_labels = ["<−90%", "−90–−50%", "−50–0%",
                                "0–+50%", "+50–100%", "+100–200%", "+200%+"]
        life = {
            "sim_version": life_sim,
            "label": ("Full-life surface: what each pool contract's premium did from "
                      "the 10:00 ET surfacing fill to expiration — peak/trough "
                      "excursion with NO exit rule, plus the hold-to-settlement "
                      "intrinsic mark. Pool-level aggregates only."),
            "processed": life_raw.get("life_processed"),
            "no_entry_excluded": life_raw.get("life_no_entry"),
            "n_peak": life_raw.get("life_n_peak"),
            "n_expiry": life_raw.get("life_n_expiry"),
            "first_scan_date": life_raw.get("life_first_scan_date"),
            "last_scan_date": life_raw.get("life_last_scan_date"),
            "peak_median": life_raw.get("life_peak_median"),
            "peak_p75": life_raw.get("life_peak_p75"),
            "peak_p90": life_raw.get("life_peak_p90"),
            "trough_median": life_raw.get("life_trough_median"),
            "trough_p10": life_raw.get("life_trough_p10"),
            "expiry_median": life_raw.get("life_expiry_median"),
            "peak_ge_40": life_raw.get("life_peak_ge_40"),
            "peak_ge_100": life_raw.get("life_peak_ge_100"),
            "peak_buckets": [
                {"label": lbl, "n": life_raw.get(f"lpb_{i}")}
                for i, lbl in enumerate(peak_bucket_labels)
            ],
            "expiry_buckets": [
                {"label": lbl, "n": life_raw.get(f"leb_{i}")}
                for i, lbl in enumerate(expiry_bucket_labels)
            ],
        }

        doc = {
            **row,
            "life": life,
            "units": "fractions (0.21 = +21%)",
            "bracket_label": "Blind buy of EVERY pool contract under the fixed same-day +40%/-30% bracket (10:00 entry, flat 15:45 ET)",
            "bracket_sim_version": f"{sameday_sim} (incl. legacy pre-tagging rows, verified same-day)",
            "bracket_3d_label": "Legacy comparison arm: blind buy under the V6-era -60%/+80% bracket over a 3-trading-day hold — DIFFERENT stop/target than the same-day baseline, not just a longer hold",
            "bracket_3d_sim_version": threeday_sim,
            "opp_label": "Opportunity surface: realized peak/trough excursion per contract over its labeled window",
            "opp_sim_version": opp_sim,
            "source_table": "enriched_option_outcomes",
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        fs_client.collection("pool_outcomes").document("current").set(doc)
        logger.info(
            f"pool_outcomes/current updated: {row['contracts_total']} contracts, "
            f"{row['scan_days']} days, sameday WR {row['bracket_win_rate']}"
        )
        return jsonify({"status": "success", **{k: str(v) for k, v in row.items()}}), 200

    except Exception as e:
        logger.error(f"pool_outcomes failed: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
