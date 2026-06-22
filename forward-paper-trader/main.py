import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
import pandas_market_calendars as mcal
from google.cloud import bigquery, firestore
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

# Trader execution config — V7 "INTRADAY" get-in-get-out bracket (2026-06-17).
# V7 keeps the V6 tournament SELECTION unchanged and changes ONLY the exit:
# a same-day OCO bracket. Constants here MUST mirror what signal-notifier
# displays in operator email + WhatsApp.
# See docs/DECISIONS/2026-06-17-v7-intraday-bracket.md (+ the velocity backtest
# backtesting_and_research/exit_velocity_sweep.py). Prior 3-day bracket:
# docs/DECISIONS/2026-04-17-v5-3-target-80.md (RETIRED — V6 3-day hold is dead).
#
# V7 philosophy: get in, grab the gain or cut, OUT the same day — velocity of
# capital + a halved disaster tail (-34% vs -61%) beat the 3-day hold on
# return-per-capital-day (~3x) at ~tied per-trade EV.
#   Entry   : 10:00 ET on entry_day (first trading day after scan_date)
#   Target  : +40% on option premium (take-profit limit)
#   Stop    : -30% on option premium (hard stop)
#   Time    : 15:45 ET SAME day — flat no matter what, NO overnight hold
#   Trail   : OFF (USE_TRAIL=False) — a clean 3-leg OCO, no peak-ratchet
#   Hold    : 1 trading day (entry_day == exit_day)
#
# Exit precedence when stop and target hit in the same bar: STOP wins
# (conservative — we can't know intrabar sequencing, so assume worst case).
#
# The trader has NO filters beyond what enrichment + signal-notifier
# applied upstream. Signal quality gates (V/OI, moneyness, VIX <= VIX3M,
# earnings, DTE, OI/vol floors) live in signal-notifier and enrichment-
# trigger, not here. One-pick ledger contract: this service simulates ONLY
# the ticker named in todays_pick/{scan_date} and writes at most one ledger
# row per scan_date.
MAX_SPREAD_PCT = 0.10
HOLD_DAYS = 1      # V7: same-day — entry_day == exit_day
STOP_PCT = 0.30    # -30% on option premium (hard stop)
TARGET_PCT = 0.40  # +40% on option premium (take-profit)
# Trail is RETIRED in V7 (USE_TRAIL=False): a same-day get-in-get-out bracket
# is a flat 3-leg OCO (target / stop / 15:45 time-exit), not a multi-day
# peak-ratchet. TRAIL_* constants are kept (referenced by the bar walk) but
# are INERT while USE_TRAIL is False. To re-enable a trail, flip USE_TRAIL.
USE_TRAIL = False
TRAIL_TRIGGER_PCT = 0.30   # (inert under V7) activate trail when peak gain >= +30%
TRAIL_DRAWDOWN_PCT = 0.25  # (inert under V7) 25% drawdown from peak triggers trail exit
# Symmetric adverse slippage (2026-06-04). Entry pays UP this fraction; bracket
# exits (TARGET/STOP) fill DOWN this same fraction. One constant, both sides.
# See docs/DECISIONS/2026-06-04-pnl-sim-realism-fixes.md.
SLIPPAGE_PCT = 0.02
# Max minutes after 10:00 ET we still treat a fill as an on-time day-1 entry.
# A first print beyond this is a late/illiquid fill, not a clean 10:00 entry.
LATE_FILL_TOLERANCE_MIN = 30
ENTRY_HHMM = "10:00"  # 10:00 ET on entry_day
EXIT_HHMM = "15:45"   # 15:45 ET SAME day (V7 time-exit)
POLICY_VERSION = "V7_1_TILTED_GIGO"
POLICY_GATE = "ENRICHMENT_ONLY_NO_TRADER_GATE"
LEDGER_TABLE = f"{PROJECT_ID}.profit_scout.forward_paper_ledger"
INTRADAY_TABLE = f"{PROJECT_ID}.profit_scout.forward_paper_ledger_intraday"
# Isolated RESEARCH-ONLY shadow table — deterministic top-score baseline vs the
# live Tournament, under identical mechanics. COMPLETELY walled off from the
# live Scorecard (forward_paper_ledger / current_ledger_stats) and the website
# (Firestore todays_pick / signal_performance / webapp / blog). Internal only.
# Written ONLY by _write_topscore_shadow, best-effort, never blocks the live
# return. See docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md.
SHADOW_TABLE = f"{PROJECT_ID}.profit_scout.paper_shadow_topscore"

# Hold-period research shadow: the SAME live Tournament pick, but day-traded —
# entered 10:00 ET on entry_day and exited FLAT at 15:45 ET the SAME day (no
# stop/target, no 3-day hold). Tests whether the edge is front-loaded intraday
# vs the 3-day bracket. Reuses the live trade's entry_price (identical 10:00
# fill) so it never re-touches _simulate_contract. COMPLETELY walled off from
# the live Scorecard and the website — written ONLY by _write_intraday_shadow,
# best-effort. NOTE: distinct from INTRADAY_TABLE (the live MTM table) above.
# See docs/DECISIONS/2026-06-08-intraday-hold-shadow.md.
SHADOW_INTRADAY_TABLE = f"{PROJECT_ID}.profit_scout.paper_shadow_intraday"
INTRADAY_EXIT_HHMM = "15:45"  # same-day flat exit for the intraday shadow

# Isolated RESEARCH-ONLY counterfactual-label table. Records the realized
# +80/-60/trail option outcome for EVERY enriched BULLISH candidate in the daily
# pool (the full ~50 we *could* have traded), not just the single tournament
# pick the live ledger records. This is the leakage-safe option-PnL substrate the
# autonomous edge-finder needs — it grows ~50x faster than forward_paper_ledger
# and supplies the counterfactual ("what would the names we skipped have done?").
# Written ONLY by _write_enriched_outcomes via the /label_enriched_pool endpoint,
# reusing _simulate_contract so labels match production mechanics exactly.
# COMPLETELY walled off from the live Scorecard and the website. Never read or
# written by any production surface. See
# docs/DECISIONS/2026-06-17-enriched-option-outcomes.md.
ENRICHED_OUTCOMES_TABLE = f"{PROJECT_ID}.profit_scout.enriched_option_outcomes"
# Honor the locked scope decision (2026-06-17): label the enriched BULLISH pool
# only (the live strategy's universe), not the raw all-direction scan pool.
ENRICHED_OUTCOMES_BULLISH_ONLY = True

def get_next_trading_day(base_date: date) -> date:
    end_date = base_date + timedelta(days=7)
    schedule = nyse.schedule(start_date=base_date, end_date=end_date)
    future_dates = [d.date() for d in schedule.index if d.date() > base_date]
    return future_dates[0] if future_dates else None

def is_trading_day(d: date) -> bool:
    """True if `d` is an NYSE trading session (handles weekends + holidays)."""
    schedule = nyse.schedule(start_date=d, end_date=d)
    return len(schedule.index) > 0

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


def _fetch_vix_daily_fred(target_date: date) -> pd.DataFrame:
    """Return a DataFrame of VIX daily closes indexed by date.

    Source: FRED VIXCLS series (free CSV endpoint, no auth). Cached in-process
    so we hit FRED at most once per trader invocation.

    Bounded with cosd (start date) = target_date − 60d. Without it FRED
    serializes VIXCLS back to 1990, and that full dump now exceeds the read
    timeout every morning (the "FRED outage" of 2026-06-02..04 was this, not a
    real outage). A 60-day window still yields ~40 trading days — ample for the
    on-or-before lookup and the 6-day delta in get_regime_context.
    """
    if _VIX_CACHE["df"] is not None:
        return _VIX_CACHE["df"]
    import io
    cosd = (target_date - timedelta(days=60)).isoformat()
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd={cosd}"
    resp = requests.get(url, timeout=30)
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
        vix_df = _fetch_vix_daily_fred(target_date)
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

def _build_skip_record(
    scan_date: date,
    skip_reason: str,
    vix_level: float | None,
    spy_trend: str | None,
    vix_5d_delta: float | None,
    ticker: str | None = None,
) -> dict:
    """Construct a no-trade ledger row.

    Preserves every column the active-trade record carries so downstream
    consumers can SELECT * without NULL-handling per-row. Used for V5.4
    no-pick days (`todays_pick.has_pick=False`), V5.4 missing-doc days, and
    Firestore-unreachable fail-closed days.
    """
    return {
        "scan_date": scan_date,
        "ticker": ticker,
        "recommended_contract": None,
        "direction": None,
        "is_premium_signal": False,
        "premium_score": 0,
        "policy_version": POLICY_VERSION,
        "policy_gate": POLICY_GATE,
        "is_skipped": True,
        "skip_reason": skip_reason,
        "VIX_at_entry": float(vix_level) if vix_level is not None else None,
        "SPY_trend_state": spy_trend,
        "vix_5d_delta_entry": float(vix_5d_delta) if vix_5d_delta is not None else None,
        "recommended_dte": None,
        "recommended_volume": None,
        "recommended_oi": None,
        "recommended_spread_pct": None,
        "entry_timestamp": None,
        "entry_price": None,
        "target_price": None,
        "stop_price": None,
        "trail_trigger_price": None,
        "peak_premium": None,
        "trail_activated": None,
        "trail_stop_at_exit": None,
        "exit_timestamp": None,
        "exit_reason": "SKIPPED",
        "realized_return_pct": None,
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


def _fetch_todays_pick(scan_date: date) -> tuple[str | None, dict | None, str | None]:
    """Read the canonical V5.4 pick doc for ``scan_date``.

    Returns ``(state, doc_dict, picked_ticker)`` where ``state`` is one of:
      - ``"HAS_PICK"`` — doc exists, ``has_pick=True``, ticker present.
      - ``"NO_PICK"`` — doc exists, ``has_pick=False`` (skip_reason carries why).
      - ``"MISSING"`` — doc does not exist at all (signal-notifier never ran).
      - ``"FETCH_FAILED"`` — Firestore call raised; caller must fail-closed.

    The doc is written by signal-notifier under both ``scan_date`` and
    ``entry_day`` keys (dual-write contract, see signal-notifier
    ``write_todays_pick_doc``). The trader reads under ``scan_date`` which is
    the authoritative key for that day's decision.
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        doc_ref = db.collection("todays_pick").document(scan_date.isoformat())
        snap = doc_ref.get()
        if not snap.exists:
            return "MISSING", None, None
        doc = snap.to_dict() or {}
        if not doc.get("has_pick"):
            return "NO_PICK", doc, None
        ticker = doc.get("ticker")
        if not ticker:
            # Malformed doc: has_pick=True but no ticker field. Treat as NO_PICK
            # with an explicit reason so the ledger row says what happened.
            return "NO_PICK", doc, None
        return "HAS_PICK", doc, str(ticker).upper()
    except Exception as e:
        logger.error(f"todays_pick fetch failed for {scan_date}: {e}")
        return "FETCH_FAILED", None, None


def run_forward_paper_trading(target_date: date = None):
    """Forward paper trading — V7 INTRADAY, one row per scan_date.

    Execution policy (V7, 2026-06-17; change only with a new decision doc —
    docs/DECISIONS/2026-06-17-v7-intraday-bracket.md):
      - Entry:  10:00 ET on entry_day (first trading day after scan_date)
      - Stop:   -30% on option premium (hard)
      - Target: +40% on option premium
      - Trail:  OFF (USE_TRAIL=False)
      - Hold:   SAME day; flat at 15:45 ET on entry_day if neither fires
      - Ambiguous bar: STOP wins over TARGET (conservative)
      - Writes to forward_paper_ledger with policy_version=V7_1_TILTED_GIGO

    V5.4-only ledger contract (2026-05-12, see docs/DECISIONS/
    2026-05-12-v5-4-pipeline-alignment.md): the trader simulates ONLY the
    ticker named in Firestore todays_pick/{scan_date}. The previous behavior
    (simulate every enriched signal as a "research fanout dataset") wrote ~70
    rows/day labeled policy_version=V6_TOURNAMENT even though only one
    was actually the V5.4 pick. That mislabeling broke cohort_stats integrity.
    Now: one trade row per day (or one skip row), all genuinely V5.4.

    Fail-closed behavior:
      - todays_pick missing entirely  -> single skip row, skip_reason=NO_TODAYS_PICK_DOC
      - todays_pick has_pick=False    -> single skip row, skip_reason=<doc skip_reason>
      - todays_pick fetch raised      -> single skip row, skip_reason=TODAYS_PICK_FETCH_FAILED
      - todays_pick ticker not in enriched table -> single skip row,
        skip_reason=PICK_NOT_IN_ENRICHED

    The trader applies NO additional gates. Signal quality filters live
    upstream in enrichment-trigger (spread <= 8%, UOA > $500K, score >= 1)
    and in signal-notifier (V/OI > 2, moneyness 5-10%, VIX <= VIX3M,
    earnings overlap, DTE 7-45, OI>=10, vol>=50, V5.4 picker).

    No knobs are exposed at the HTTP layer. To change any of this, edit the
    constants at the top of this file and write a decision note.
    """
    if not target_date:
        # Default to today if not provided
        target_date = datetime.now(est).date()

    # Market-holiday stand-down. The cron fires on the RUN day; if the NYSE is
    # closed that day (holiday/weekend) there is no session to trade — write a
    # single MARKET_HOLIDAY skip row (reusing the existing skip_reason column —
    # NOT a schema change) and return before any Polygon/FRED fetch or
    # simulation. Keyed on the run day, not target_date (the prior scan date).
    # See 2026-06-19 Juneteenth: a trade fired on a closed market.
    run_day = datetime.now(est).date()
    if not is_trading_day(run_day):
        logger.info(f"Market closed on {run_day} (NYSE holiday/weekend) — standing down: writing MARKET_HOLIDAY skip row, no fetches/simulation.")
        skip_record = _build_skip_record(
            target_date, "MARKET_HOLIDAY", None, None, None,
        )
        return _write_ledger_records(bigquery.Client(project=PROJECT_ID), target_date, [skip_record])

    logger.info(f"Running V7 INTRADAY Forward Paper Trading for signals generated on {target_date} "
                f"(entry={ENTRY_HHMM} ET, stop=-{STOP_PCT*100:.0f}%, target=+{TARGET_PCT*100:.0f}%, "
                f"trail={'ON' if USE_TRAIL else 'OFF'}, "
                f"hold_days={HOLD_DAYS} (same-day), flat={EXIT_HHMM} ET, ledger={LEDGER_TABLE})")

    client = bigquery.Client(project=PROJECT_ID)

    # 1. Resolve today's V5.4 pick from Firestore.
    # The trader is now V5.4-only: the ledger row count is at most 1 per
    # scan_date (one trade row OR one skip row, never both, never multiple).
    # The previous fanout path (simulate every enriched row) is gone — it
    # mislabeled non-picks as V6_TOURNAMENT. See docs/DECISIONS/
    # 2026-05-12-v5-4-pipeline-alignment.md.
    pick_state, pick_doc, picked_ticker = _fetch_todays_pick(target_date)

    # 2. Determine entry/exit day timing — needed for both happy-path simulation
    # AND for the timeout-day guard (we don't write skip rows for future hold
    # windows either; the daily cron retries the same target_date next day).
    entry_day = get_next_trading_day(target_date)
    if entry_day > datetime.now(est).date():
        logger.warning(f"Entry day {entry_day} is in the future. Cannot simulate execution yet.")
        return False, f"Entry day {entry_day} is in the future."

    # Refuse to simulate any trade whose hold window hasn't fully closed yet.
    # Without this guard, the exit-fallback path at the bottom of the simulation
    # loop will use a partial intraday bar from "today" as a phantom TIMEOUT exit,
    # producing data that looks like a closed trade but represents an open position.
    # V7: exit_day = entry_day + (HOLD_DAYS - 1) trading days = entry_day (same-day).
    # The cron fires at 16:30 ET after market close, so the 15:45 ET TIMEOUT bar on
    # exit_day=today is already final and safe to simulate — hence `>` (strict future), not `>=`.
    timeout_day_check = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)
    today_et = datetime.now(est).date()
    if timeout_day_check > today_et:
        msg = (f"Exit day {timeout_day_check} for hold_days={HOLD_DAYS} is in the "
               f"future. Hold window has not fully closed; refusing to simulate.")
        logger.warning(msg)
        return False, msg

    vix_level, spy_trend, vix_5d_delta = get_regime_context(entry_day)

    if vix_level is None:
        logger.info(f"Proceeding without VIX telemetry for {entry_day}.")
    else:
        delta_str = f"{vix_5d_delta:+.2f}" if vix_5d_delta is not None else "n/a"
        logger.info(f"Regime telemetry on {entry_day}: VIX = {vix_level:.2f} (5d Δ {delta_str}), SPY Trend = {spy_trend}")

    # 3. Branch on pick state. All non-HAS_PICK branches write a single skip row.
    if pick_state == "FETCH_FAILED":
        logger.error(f"todays_pick Firestore fetch failed for {target_date}; writing fail-closed skip row.")
        skip_record = _build_skip_record(
            target_date, "TODAYS_PICK_FETCH_FAILED", vix_level, spy_trend, vix_5d_delta,
        )
        return _write_ledger_records(client, target_date, [skip_record])

    if pick_state == "MISSING":
        logger.info(f"No todays_pick/{target_date} doc exists; writing NO_TODAYS_PICK_DOC skip row.")
        skip_record = _build_skip_record(
            target_date, "NO_TODAYS_PICK_DOC", vix_level, spy_trend, vix_5d_delta,
        )
        return _write_ledger_records(client, target_date, [skip_record])

    if pick_state == "NO_PICK":
        doc_skip_reason = (pick_doc or {}).get("skip_reason") or "no_candidates_passed_gates"
        logger.info(f"todays_pick/{target_date} has_pick=False; writing skip row skip_reason={doc_skip_reason}.")
        skip_record = _build_skip_record(
            target_date, str(doc_skip_reason), vix_level, spy_trend, vix_5d_delta,
        )
        return _write_ledger_records(client, target_date, [skip_record])

    # HAS_PICK: fetch the single enriched row for the picked ticker on this scan_date.
    assert picked_ticker is not None
    query = f"""
    SELECT
        ticker, scan_date, direction, recommended_contract, recommended_strike,
        recommended_expiration, recommended_dte, recommended_volume, recommended_oi,
        recommended_spread_pct, is_premium_signal, premium_score
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      AND UPPER(ticker) = "{picked_ticker}"
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
    ORDER BY premium_score DESC, recommended_volume DESC
    LIMIT 1
    """

    df = client.query(query).to_dataframe()
    logger.info(f"V5.4 pick={picked_ticker} on {target_date}: matched {len(df)} enriched row(s).")

    if len(df) == 0:
        # The pick ticker is named in todays_pick but no enriched row exists
        # for it on this scan_date. Shouldn't happen in normal operation —
        # signal-notifier selects the pick FROM the enriched table. Treat as
        # fail-closed skip so the ledger row count stays at exactly 1.
        logger.error(
            f"V5.4 pick={picked_ticker} not found in overnight_signals_enriched "
            f"for {target_date}. Writing PICK_NOT_IN_ENRICHED skip row."
        )
        skip_record = _build_skip_record(
            target_date, "PICK_NOT_IN_ENRICHED", vix_level, spy_trend, vix_5d_delta,
            ticker=picked_ticker,
        )
        return _write_ledger_records(client, target_date, [skip_record])

    # Happy path: simulate the single V5.4-picked row. The trader runs at most
    # one simulation per scan_date (one trade row → one ledger row). All bar-
    # walking / benchmarking logic below is unchanged from the V5.3 era; only
    # the input is now a single-row selection instead of a fanout loop.
    row = df.iloc[0]
    records_to_insert: list[dict] = []

    # exit_day = entry_day + (HOLD_DAYS-1) trading days. Needed here to pass into
    # both the sim and the shadow writer; _simulate_contract recomputes the same
    # value internally (identical by construction).
    exit_day = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)

    record = _simulate_contract(
        client, row, entry_day, exit_day, vix_level, spy_trend, vix_5d_delta, pick_doc
    )

    records_to_insert.append(record)

    # Live ledger write FIRST — capture its result and return it UNCHANGED.
    ledger_result = _write_ledger_records(client, target_date, records_to_insert)

    # Best-effort isolated research shadow (deterministic top-score vs Tournament).
    # Walled off from the live Scorecard + website; writes ONLY to SHADOW_TABLE.
    # The inner function already swallows all exceptions; this outer try is
    # belt-and-suspenders so the shadow can NEVER alter the live return.
    # See docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md.
    # Capture the simulated top-score record so the intraday shadow can day-trade
    # the SAME top-score pick (the 4th experiment). None if the top-score shadow
    # skipped/failed → the intraday shadow then runs the TOURNAMENT arm only.
    topscore_record = None
    try:
        topscore_record = _write_topscore_shadow(
            client, target_date, entry_day, exit_day,
            vix_level, spy_trend, vix_5d_delta,
            tournament_record=record, pick_doc=pick_doc,
        )
    except Exception as e:
        logger.error(f"topscore shadow failed (non-fatal): {e}")

    # Best-effort isolated hold-period shadow — day-trade BOTH picks (Tournament
    # + top-score): 10:00 ET entry, flat 15:45 ET same-day exit. Writes ONLY to
    # SHADOW_INTRADAY_TABLE; can NEVER alter the live return.
    # See docs/DECISIONS/2026-06-08-intraday-hold-shadow.md.
    try:
        _write_intraday_shadow(
            client, target_date, entry_day,
            tournament_record=record, topscore_record=topscore_record,
            pick_doc=pick_doc,
        )
    except Exception as e:
        logger.error(f"intraday shadow failed (non-fatal): {e}")

    return ledger_result


def _simulate_contract(
    client: bigquery.Client,
    row,
    entry_day: date,
    exit_day: date,
    vix_level: float | None,
    spy_trend: str | None,
    vix_5d_delta: float | None,
    pick_doc: dict | None,
) -> dict:
    """Simulate one option contract over the V7 same-day intraday bracket.

    Pure mechanical extraction of the per-ticker simulation body that used to
    live inline in run_forward_paper_trading's HAS_PICK happy path. Builds and
    returns a completed ledger ``record`` dict from a single enriched ``row``
    plus entry/exit timing and regime context.

    Inputs (the ``row`` must carry these columns): ticker, scan_date, direction,
    recommended_contract, recommended_strike, recommended_expiration,
    recommended_dte, recommended_volume, recommended_oi, recommended_spread_pct,
    is_premium_signal, premium_score.

    ``pick_doc`` is only read for the policy_gate tag (STRICT vs FALLBACK); pass
    ``None`` for research/shadow callers that have no Firestore pick doc — the
    record then falls back to the service POLICY_GATE constant.

    Mechanics (slippage, bracket precedence STOP/TRAIL > TARGET, illiquid/stale
    tags, benchmarking) are byte-identical to the pre-extraction inline path.
    """
    record = {
        "scan_date": row["scan_date"].date() if isinstance(row["scan_date"], datetime) else row["scan_date"],
        "ticker": row["ticker"],
        "recommended_contract": row["recommended_contract"],
        "direction": row["direction"],
        "is_premium_signal": bool(row["is_premium_signal"]) if pd.notna(row["is_premium_signal"]) else False,
        "premium_score": int(row["premium_score"]) if pd.notna(row["premium_score"]) else 0,
        "policy_version": POLICY_VERSION,
        # Propagate the signal-notifier gate tag (STRICT vs FALLBACK) so
        # daily-cadence fallback trades are measurable separately in the ledger.
        # Falls back to the service constant for pre-fallback docs that omit it.
        # See docs/DECISIONS/2026-06-01-daily-cadence-fallback.md.
        "policy_gate": (pick_doc.get("policy_gate") if pick_doc else None) or POLICY_GATE,
        "is_skipped": False,
        "skip_reason": None,
        "VIX_at_entry": float(vix_level) if vix_level is not None else None,
        "SPY_trend_state": spy_trend,
        "vix_5d_delta_entry": float(vix_5d_delta) if vix_5d_delta is not None else None,
        "recommended_dte": int(row["recommended_dte"]),
        "recommended_volume": int(row["recommended_volume"]),
        "recommended_oi": int(row["recommended_oi"]),
        "recommended_spread_pct": float(row["recommended_spread_pct"]) if pd.notna(row["recommended_spread_pct"]) else None,
        # Execution defaults (overwritten during simulation below).
        "entry_timestamp": None,
        "entry_price": None,
        "target_price": None,
        "stop_price": None,
        "trail_trigger_price": None,
        "peak_premium": None,
        "trail_activated": None,
        "trail_stop_at_exit": None,
        "exit_timestamp": None,
        "exit_reason": None,
        "realized_return_pct": None,
        # P&L-realism audit fields (added 2026-06-04 to remove upward bias in
        # realized_return_pct). All nullable; populated inline during simulation.
        # See docs/DECISIONS/2026-06-04-pnl-sim-realism-fixes.md.
        "exit_slippage": None,       # adverse slippage applied on bracket exits (frac)
        "illiquid_exit": None,       # True when TIMEOUT priced off a stale (earlier-day) print
        "late_fill_minutes": None,   # minutes between 10:00 ET target and the actual entry print
        # Benchmarking & regime context — populated inline during simulation.
        # All remain None on fetch failure (non-blocking, see benchmark_context.py).
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

    # 4. Simulate Execution (single ticker, single contract).
    exp_date = row["recommended_expiration"].date() if isinstance(row["recommended_expiration"], pd.Timestamp) or isinstance(row["recommended_expiration"], datetime) else row["recommended_expiration"]
    opt_ticker = build_polygon_ticker(row["ticker"], exp_date, row["direction"], float(row["recommended_strike"]))

    # V7 mechanics: entry 10:00 ET, same-day hold, flat 15:45 ET on entry_day.
    # HOLD_DAYS is the number of trading days held inclusive of entry_day.
    # V7 HOLD_DAYS=1: exit_day = get_nth_next_trading_day(entry_day, 0) == entry_day.
    exit_day = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)

    bars = fetch_minute_bars(opt_ticker, entry_day, exit_day)
    time.sleep(0.2)

    entry_dt = datetime.combine(entry_day, datetime.strptime(ENTRY_HHMM, "%H:%M").time())
    entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
    timeout_dt = datetime.combine(exit_day, datetime.strptime(EXIT_HHMM, "%H:%M").time())
    timeout_ts_ms = int(est.localize(timeout_dt).timestamp() * 1000)

    # Find the entry bar (Bug #13 fix, 2026-06-04). The 10:00 ET fill must
    # land on a print close to 10:00, not silently hours late or pre-market.
    #   * Prefer the first print at-or-after 10:00 ET, but ONLY if it lands
    #     within LATE_FILL_TOLERANCE_MIN minutes. A later first print is a
    #     late/illiquid fill — keep it but set illiquid_exit=True and stamp
    #     late_fill_minutes so it's excludable from EV (the bracket exit_reason
    #     is preserved as the more informative tag).
    #   * If there is NO at-or-after print at all on entry_day, fall back to
    #     the most recent pre-10:00 print as a price proxy (rather than
    #     discarding the trade), again flagged illiquid with its offset.
    #   * INVALID_LIQUIDITY only when entry_day has zero printed bars.
    # late_fill_minutes is signed: positive = filled after 10:00, negative =
    # pre-10:00 proxy fill.
    entry_day_bars = [b for b in bars
                      if datetime.fromtimestamp(b["t"]/1000, tz=est).date() == entry_day]
    entry_bar = None
    is_late_fill = False
    late_fill_minutes = None
    if entry_day_bars:
        after_or_at = [b for b in entry_day_bars if b["t"] >= entry_ts_ms]
        if after_or_at:
            entry_bar = after_or_at[0]
            late_fill_minutes = (entry_bar["t"] - entry_ts_ms) / 60000.0
            if late_fill_minutes > LATE_FILL_TOLERANCE_MIN:
                is_late_fill = True
        else:
            before = [b for b in entry_day_bars if b["t"] < entry_ts_ms]
            entry_bar = before[-1] if before else None
            if entry_bar is not None:
                late_fill_minutes = (entry_bar["t"] - entry_ts_ms) / 60000.0
                is_late_fill = True  # pre-10:00 proxy fill is never "on time"

    if late_fill_minutes is not None:
        record["late_fill_minutes"] = float(late_fill_minutes)

    if not entry_bar or entry_bar.get("v", 0) == 0:
        record["exit_reason"] = "INVALID_LIQUIDITY"
    else:
        base_entry = entry_bar["c"] * (1.0 + SLIPPAGE_PCT)  # adverse entry slippage
        # V7 base: -30% option stop AND +40% option target (trail inert, USE_TRAIL=False).
        stop = base_entry * (1.0 - STOP_PCT)
        target = base_entry * (1.0 + TARGET_PCT)
        trail_trigger = base_entry * (1.0 + TRAIL_TRIGGER_PCT)

        record["entry_timestamp"] = datetime.fromtimestamp(entry_bar["t"]/1000, tz=est).isoformat()
        record["entry_price"] = base_entry
        record["target_price"] = target
        record["stop_price"] = stop
        record["trail_trigger_price"] = trail_trigger

        # ---- Benchmarking fetches (non-blocking; null on any failure) ----
        # Fetched at entry time. The stock bars are reused for the exit-side
        # lookup after the bar-walk.
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

        # Start the bracket walk at the first bar strictly AFTER 10:00 ET
        # (Bug #13 fix). When entry_bar is a pre-10:00 proxy print, walking
        # from bars.index(entry_bar)+1 would let pre-entry bars trigger
        # bracket exits before the position even exists. Anchor the walk on
        # entry_ts_ms instead so we never evaluate exits on pre-entry bars.
        # When entry_bar is itself at/after 10:00, this matches the original
        # entry_idx (the proxy and the real entry coincide).
        entry_idx = bars.index(entry_bar)
        walk_start = entry_idx + 1
        for k in range(len(bars)):
            if bars[k]["t"] >= entry_ts_ms and bars[k]["t"] > entry_bar["t"]:
                walk_start = k
                break
        exit_reason = "TIMEOUT"
        exit_price = None
        exit_ts = None

        # Track peak premium across the bar walk so the trail can
        # activate / ratchet. base_entry is the seed (always less than
        # any future peak by construction since peaks come from bar highs).
        peak_premium = base_entry
        trail_active = False
        trail_stop_level = None

        # V7 bar walk (same-day): three exits in precedence order.
        #   TIMEOUT — first bar at-or-after 15:45 ET on entry_day (== exit_day), flat
        #   STOP    — option low pierces -30% threshold
        #   TARGET  — option high pierces +40% threshold
        # If stop and target hit on the same bar, STOP wins (intrabar conservative —
        # assume drawdown happened first). TRAIL is inert under V7 (USE_TRAIL=False).
        # Trail can both activate AND trigger on the same bar: peak update
        # uses bar high, then trail level is checked against bar low. This
        # mirrors the conservative "high-then-low" intrabar assumption.
        # Track the most recent bar at-or-before timeout_ts_ms so on
        # TIMEOUT we price off the last in-window print.
        # exit_slip records the adverse slippage actually applied to a bracket
        # fill (TARGET/STOP/TRAIL). TIMEOUT marks-to-market at the last print
        # with no slippage (we model an exit-at-market over a 1-min bar, not a
        # liquidity-taking bracket order). illiquid_exit flags a stale TIMEOUT
        # print (Bug #9).
        exit_slip = 0.0
        illiquid_exit = False
        last_in_window_bar = None
        for j in range(walk_start, len(bars)):
            b = bars[j]
            b_ts = b["t"]

            if b_ts >= timeout_ts_ms:
                # TIMEOUT (Bug #9 fix): price off the last in-window print, but
                # only treat it as a clean TIMEOUT if that print is ON exit_day.
                # A last print from an EARLIER day is a stale mark for a 3-day
                # hold — keep the mid but flag illiquid_exit so it's excludable
                # from EV rather than masquerading as a clean timeout fill.
                timeout_bar = last_in_window_bar if last_in_window_bar is not None else b
                tb_day = datetime.fromtimestamp(timeout_bar["t"]/1000, tz=est).date()
                if tb_day != exit_day:
                    exit_reason = "STALE_NO_TIMEOUT_PRINT"
                    illiquid_exit = True
                else:
                    exit_reason = "TIMEOUT"
                exit_price = timeout_bar["c"]
                exit_ts = timeout_bar["t"]
                break

            # Update peak from this bar's high BEFORE evaluating exits,
            # so an up-and-down bar that crosses the trigger can both
            # activate the trail and stop out on it within the same bar.
            if b["h"] > peak_premium:
                peak_premium = b["h"]
                # V7: USE_TRAIL=False -> trail never activates; effective_stop
                # stays the -30% hard stop and the bracket is a flat 3-leg OCO.
                if USE_TRAIL and peak_premium >= trail_trigger:
                    trail_active = True
                if trail_active:
                    trail_stop_level = peak_premium * (1.0 - TRAIL_DRAWDOWN_PCT)

            # Effective stop: the -30% hard stop (trail inert under V7, USE_TRAIL=False).
            effective_stop = trail_stop_level if trail_active else stop
            effective_stop_reason = "TRAIL" if trail_active else "STOP"

            hit_stop = b["l"] <= effective_stop
            hit_target = b["h"] >= target
            if hit_stop:
                # Stop (trail or hard) takes precedence over TARGET on ambiguous bars.
                # Bug #12 fix: model gap-through — fill at the worse of the
                # threshold and the bar's open/low (a bar that gaps below the
                # stop fills at the gap, not the stop) — then apply adverse
                # slippage symmetric to the entry.
                exit_reason = effective_stop_reason
                fill_level = min(effective_stop, b["l"], b["o"])
                exit_price = fill_level * (1.0 - SLIPPAGE_PCT)
                exit_slip = SLIPPAGE_PCT
                exit_ts = b_ts
                break
            if hit_target:
                # Bug #12 fix: TARGET fills at the threshold minus adverse
                # slippage (we don't get a better-than-target fill).
                exit_reason = "TARGET"
                exit_price = target * (1.0 - SLIPPAGE_PCT)
                exit_slip = SLIPPAGE_PCT
                exit_ts = b_ts
                break

            # No exit triggered on this bar; remember it as the latest in-window print.
            last_in_window_bar = b

        if exit_price is None:
            # The bar walk completed without ever crossing timeout_ts_ms. With
            # the future-timeout guard above, this should only happen when the
            # contract simply stopped printing before the timeout boundary; use
            # the last available in-window bar as the timeout exit price.
            # Bug #9: a last print from an earlier day is stale for a 3-day
            # hold — flag illiquid_exit and use the distinct STALE reason so it
            # is excludable from EV instead of looking like a clean TIMEOUT.
            last = last_in_window_bar if last_in_window_bar is not None else entry_bar
            last_day = datetime.fromtimestamp(last["t"]/1000, tz=est).date()
            if last_day != exit_day:
                exit_reason = "STALE_NO_TIMEOUT_PRINT"
                illiquid_exit = True
            else:
                exit_reason = "TIMEOUT"
            exit_price = last["c"]
            exit_ts = last["t"]

        ret = (exit_price - base_entry) / base_entry

        # Bug #13: a late/illiquid entry fill is recorded but tagged so it's
        # excludable from EV. INVALID_LIQUIDITY (zero-volume) already short-
        # circuits above; LATE_FILL overlays the computed bracket exit_reason
        # only when the realized exit was otherwise clean, preserving the more
        # informative STALE/TIMEOUT/STOP/TARGET tag in exit_reason via the
        # dedicated late_fill_minutes column (already stamped above).
        if is_late_fill:
            illiquid_exit = True

        record["exit_reason"] = exit_reason
        record["exit_timestamp"] = datetime.fromtimestamp(exit_ts/1000, tz=est).isoformat()
        record["realized_return_pct"] = float(ret)
        record["exit_slippage"] = float(exit_slip)
        record["illiquid_exit"] = bool(illiquid_exit)
        record["peak_premium"] = float(peak_premium)
        record["trail_activated"] = bool(trail_active)
        record["trail_stop_at_exit"] = float(trail_stop_level) if trail_stop_level is not None else None

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

    return record


def _write_ledger_records(
    client: bigquery.Client, target_date: date, records_to_insert: list[dict]
) -> tuple[bool, str]:
    """Idempotent write of ledger rows for ``target_date``.

    Delete-then-load via a load job (NOT streaming) so the new rows never
    land in BigQuery's streaming buffer — that buffer blocks DELETE for
    ~90 minutes and would prevent same-day re-triggers from succeeding.

    Used by every exit path in ``run_forward_paper_trading``: happy-path
    trade write AND every fail-closed skip write. Always writes exactly
    what the caller passed (no dedup / dedup is the caller's job).
    """
    if not records_to_insert:
        return True, "No records to insert."

    # Convert date to string for BQ load.
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
        # Allow new nullable columns (exit_slippage, illiquid_exit,
        # late_fill_minutes — added 2026-06-04 for P&L-realism auditing) to
        # auto-create on the existing ledger table without a separate
        # migration. Additive only; never drops or retypes columns.
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
    )
    load_job = client.load_table_from_file(
        io.BytesIO(jsonl.encode("utf-8")),
        LEDGER_TABLE,
        job_config=load_job_config,
    )
    load_job.result()
    logger.info(f"Loaded {len(records_to_insert)} records into {LEDGER_TABLE}")
    return True, f"Successfully inserted {len(records_to_insert)} records."


# ---------------------------------------------------------------------------
# Deterministic top-score vs Tournament SHADOW tracker (RESEARCH-ONLY).
#
# Completely isolated from the live Scorecard and the website. Every HAS_PICK
# day, in the SAME exit-cron invocation that writes the live ledger row, we also
# simulate "just trade the highest overnight_score signal in the pool" under
# IDENTICAL mechanics (_simulate_contract) and record BOTH arms (TOURNAMENT +
# TOP_SCORE) in profit_scout.paper_shadow_topscore.
#
# Hard isolation guarantees:
#   * Writes ONLY to SHADOW_TABLE. Never forward_paper_ledger, todays_pick,
#     signal_performance, or any webapp/blog surface.
#   * Best-effort: the whole body is wrapped in try/except and returns on any
#     error. It must NEVER raise into, block, or alter the live ledger return.
#   * v1 is PAIRED-ONLY: runs only on HAS_PICK days (called from the happy path
#     after the live write), not on skip/regime/no-candidate days.
# See docs/DECISIONS/2026-06-08-topscore-shadow-tracker.md.
# ---------------------------------------------------------------------------

def _write_topscore_shadow(
    client: bigquery.Client,
    target_date: date,
    entry_day: date,
    exit_day: date,
    vix_level: float | None,
    spy_trend: str | None,
    vix_5d_delta: float | None,
    tournament_record: dict,
    pick_doc: dict | None,
) -> dict | None:
    """Simulate the deterministic top-score arm and write both shadow rows.

    Best-effort only — the entire body is wrapped in try/except and returns on
    any failure so it can NEVER raise into the live trade path. Writes ONLY to
    SHADOW_TABLE. Returns the simulated top-score record (record_s) on success
    so the caller can reuse the SAME top-score pick for the intraday shadow;
    returns None on any skip/failure.
    """
    try:
        # Pull the FULL enriched pool for this scan_date with a tradeable
        # contract. Selects every column _simulate_contract reads PLUS the
        # ranking fields (overnight_score + UOA dollar volumes for tie-break).
        pool_sql = f"""
        SELECT
            ticker, scan_date, direction, recommended_contract, recommended_strike,
            recommended_expiration, recommended_dte, recommended_volume, recommended_oi,
            recommended_spread_pct, is_premium_signal, premium_score,
            overnight_score, call_dollar_volume, put_dollar_volume
        FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
        WHERE DATE(scan_date) = "{target_date}"
          AND recommended_strike IS NOT NULL
          AND recommended_expiration IS NOT NULL
          AND recommended_dte IS NOT NULL
          AND recommended_volume IS NOT NULL
          AND recommended_oi IS NOT NULL
        """
        pool_df = client.query(pool_sql).to_dataframe()
        pool_size = int(len(pool_df))
        if pool_size == 0:
            logger.info(f"topscore shadow: empty enriched pool for {target_date}; skip")
            return

        # Deterministic top-score pick: maximize overnight_score, tie-break by
        # GREATEST(call_dollar_volume, put_dollar_volume) desc. Done explicitly
        # in pandas with stable, fully-specified ordering.
        pool_df["_score"] = pd.to_numeric(pool_df["overnight_score"], errors="coerce").fillna(-1.0)
        pool_df["_uoa"] = pool_df[["call_dollar_volume", "put_dollar_volume"]].apply(
            lambda c: max(
                float(c["call_dollar_volume"]) if pd.notna(c["call_dollar_volume"]) else 0.0,
                float(c["put_dollar_volume"]) if pd.notna(c["put_dollar_volume"]) else 0.0,
            ),
            axis=1,
        )
        ranked = pool_df.sort_values(
            by=["_score", "_uoa"], ascending=[False, False], kind="mergesort"
        ).reset_index(drop=True)
        topscore_row = ranked.iloc[0]

        # Simulate the top-score arm under identical mechanics (pick_doc=None →
        # policy_gate falls back to the service constant; confidence is NULL).
        record_s = _simulate_contract(
            client, topscore_row, entry_day, exit_day,
            vix_level, spy_trend, vix_5d_delta, pick_doc=None,
        )

        # Look up the tournament ticker's overnight_score from the same pool.
        tour_ticker = str(tournament_record.get("ticker") or "").upper()
        tour_score = None
        tour_match = pool_df[pool_df["ticker"].astype(str).str.upper() == tour_ticker]
        if len(tour_match) > 0:
            v = tour_match.iloc[0]["overnight_score"]
            tour_score = int(v) if pd.notna(v) else None

        ts_score_v = topscore_row["overnight_score"]
        ts_score = int(ts_score_v) if pd.notna(ts_score_v) else None

        topscore_ticker = str(topscore_row["ticker"]).upper()
        same_pick = (topscore_ticker == tour_ticker)
        confidence = (pick_doc.get("v5_4_confidence") if pick_doc else None)

        # regime_ok = VIX <= VIX3M. vix3m isn't in the trader's cheap scope; only
        # populate from the fields the todays_pick doc already carries
        # (vix_now_at_decision / vix3m_at_enrich — see signal-notifier
        # write_todays_pick_doc), else leave NULL. No new fetch.
        regime_ok = None
        if pick_doc:
            v_lvl = pick_doc.get("vix_now_at_decision")
            v_3m = pick_doc.get("vix3m_at_enrich")
            if v_lvl is not None and v_3m is not None:
                try:
                    regime_ok = bool(float(v_lvl) <= float(v_3m))
                except (TypeError, ValueError):
                    regime_ok = None

        created_at = datetime.now(est).isoformat()

        def _shadow_row(arm: str, src: dict, score, conf) -> dict:
            return {
                "scan_date": target_date.isoformat(),
                "entry_day": entry_day.isoformat(),
                "exit_day": exit_day.isoformat(),
                "arm": arm,
                "ticker": src.get("ticker"),
                "direction": src.get("direction"),
                "recommended_contract": src.get("recommended_contract"),
                "overnight_score": score,
                "confidence": conf,
                "regime_ok": regime_ok,
                "pool_size": pool_size,
                "same_pick": bool(same_pick),
                "entry_price": src.get("entry_price"),
                "exit_price": None,  # not persisted on the ledger record; see below
                "exit_reason": src.get("exit_reason"),
                "realized_return_pct": src.get("realized_return_pct"),
                "illiquid_exit": src.get("illiquid_exit"),
                "late_fill_minutes": src.get("late_fill_minutes"),
                "exit_slippage": src.get("exit_slippage"),
                "policy_version": POLICY_VERSION,
                "created_at": created_at,
            }

        # The ledger record dict does not carry a raw exit_price field (only
        # entry_price + realized_return_pct + exit_reason). Derive exit_price
        # from entry_price * (1 + realized_return_pct) when both are present so
        # the shadow table is self-describing; NULL otherwise.
        def _with_exit_price(d: dict) -> dict:
            ep = d.get("entry_price")
            ret = d.get("realized_return_pct")
            if ep is not None and ret is not None:
                d["exit_price"] = float(ep) * (1.0 + float(ret))
            return d

        rows = [
            _with_exit_price(_shadow_row("TOURNAMENT", tournament_record, tour_score, confidence)),
            _with_exit_price(_shadow_row("TOP_SCORE", record_s, ts_score, None)),
        ]

        _write_shadow_records(client, SHADOW_TABLE, target_date, rows)
        logger.info(
            f"topscore shadow: wrote 2 rows for {target_date} "
            f"(tournament={tour_ticker} score={tour_score}, "
            f"top_score={topscore_ticker} score={ts_score}, "
            f"same_pick={same_pick}, pool_size={pool_size})"
        )
        # Return the simulated top-score record so the intraday shadow can
        # day-trade the SAME top-score pick (its 10:00 entry, reused). None on
        # any skip/failure → the intraday shadow then runs the tournament arm only.
        return record_s
    except Exception as e:
        logger.error(f"topscore shadow write failed for {target_date} (non-fatal): {e}")
        return None


def _write_intraday_shadow(
    client: bigquery.Client,
    target_date: date,
    entry_day: date,
    tournament_record: dict,
    topscore_record: dict | None,
    pick_doc: dict | None,
) -> None:
    """Day-trade BOTH the live Tournament pick AND the deterministic top-score
    pick: enter 10:00 ET, exit FLAT at 15:45 ET the SAME day (no stop/target,
    no 3-day hold). Two arms per day (TOURNAMENT + TOP_SCORE) so the intraday
    "get-in-get-out" theory is measured on both selection methods.

    Reuses each pick's already-simulated 10:00 entry_price (``tournament_record``
    from the live trade; ``topscore_record`` returned by _write_topscore_shadow),
    so it NEVER re-simulates entry and never touches the live path. Best-effort —
    the whole body is wrapped and returns on any failure. Writes ONLY to
    SHADOW_INTRADAY_TABLE.
    """
    try:
        regime_ok = None
        if pick_doc:
            v_lvl = pick_doc.get("vix_now_at_decision")
            v_3m = pick_doc.get("vix3m_at_enrich")
            if v_lvl is not None and v_3m is not None:
                try:
                    regime_ok = bool(float(v_lvl) <= float(v_3m))
                except (TypeError, ValueError):
                    regime_ok = None
        created_at = datetime.now(est).isoformat()

        exit_dt = datetime.combine(
            entry_day, datetime.strptime(INTRADAY_EXIT_HHMM, "%H:%M").time()
        )
        exit_ts_ms = int(est.localize(exit_dt).timestamp() * 1000)

        same_pick = None
        if topscore_record:
            same_pick = (
                str(tournament_record.get("ticker") or "").upper()
                == str(topscore_record.get("ticker") or "").upper()
            )

        def _intraday_row(arm: str, src: dict | None, conf) -> dict | None:
            """Day-trade one pick's contract (10:00 entry reused, 15:45 flat
            exit). Returns the row, or None if this arm isn't simulable."""
            if not src:
                return None
            base_entry = src.get("entry_price")
            opt_contract = src.get("recommended_contract")
            if base_entry is None or not opt_contract:
                logger.info(
                    f"intraday shadow [{arm}]: no entry_price/contract for "
                    f"{target_date} (exit_reason={src.get('exit_reason')}); skip arm"
                )
                return None
            # Same-day minute bars for THIS pick's contract.
            bars = fetch_minute_bars(opt_contract, entry_day, entry_day)
            time.sleep(0.1)
            day_bars = [
                b for b in bars
                if datetime.fromtimestamp(b["t"] / 1000, tz=est).date() == entry_day
            ]
            if not day_bars:
                logger.info(f"intraday shadow [{arm}]: no entry_day bars for {opt_contract} on {entry_day}; skip arm")
                return None
            # Exit = first print at-or-after 15:45 ET; else last earlier same-day
            # print flagged illiquid. Mark at the bar close, no slippage (mirrors
            # the live TIMEOUT convention).
            at_or_after = [b for b in day_bars if b["t"] >= exit_ts_ms]
            illiquid = False
            if at_or_after:
                exit_bar = at_or_after[0]
            else:
                exit_bar = day_bars[-1]
                illiquid = True
            exit_price = exit_bar.get("c")
            if exit_price is None or exit_price <= 0:
                logger.info(f"intraday shadow [{arm}]: non-positive exit price for {opt_contract} on {entry_day}; skip arm")
                return None
            intraday_ret = (exit_price - base_entry) / base_entry
            return {
                "scan_date": target_date.isoformat(),
                "entry_day": entry_day.isoformat(),
                "arm": arm,
                "ticker": src.get("ticker"),
                "direction": src.get("direction"),
                "recommended_contract": opt_contract,
                "confidence": conf,
                "regime_ok": regime_ok,
                "same_pick": same_pick,
                "entry_price": float(base_entry),
                "intraday_exit_price": float(exit_price),
                "intraday_exit_timestamp": datetime.fromtimestamp(exit_bar["t"] / 1000, tz=est).isoformat(),
                "intraday_return_pct": float(intraday_ret),
                "intraday_illiquid": bool(illiquid),
                # Reference: the SAME pick's live 3-day bracket result, side-by-side.
                "hold_3day_return_pct": (
                    float(src["realized_return_pct"])
                    if src.get("realized_return_pct") is not None else None
                ),
                "hold_3day_exit_reason": src.get("exit_reason"),
                "policy_version": POLICY_VERSION,
                "created_at": created_at,
            }

        tour_conf = (pick_doc.get("v5_4_confidence") if pick_doc else None)
        rows = [
            _intraday_row("TOURNAMENT", tournament_record, tour_conf),
            _intraday_row("TOP_SCORE", topscore_record, None),
        ]
        rows = [r for r in rows if r is not None]
        if not rows:
            logger.info(f"intraday shadow: no simulable arms for {target_date}; skip")
            return
        _write_shadow_records(client, SHADOW_INTRADAY_TABLE, target_date, rows)
        logger.info(
            f"intraday shadow: wrote {len(rows)} row(s) for {target_date}: "
            + ", ".join(f"{r['arm']}={r['ticker']}:{r['intraday_return_pct']:+.4f}" for r in rows)
        )
    except Exception as e:
        logger.error(f"intraday shadow write failed for {target_date} (non-fatal): {e}")
        return


def _write_shadow_records(
    client: bigquery.Client, table: str, target_date: date, rows: list[dict]
) -> None:
    """Idempotent delete-then-load append into an ISOLATED shadow table only.

    Mirrors _write_ledger_records' streaming-avoiding load-job pattern but takes
    an explicit ``table`` — deliberately NOT reusing _write_ledger_records (which
    targets LEDGER_TABLE) so the live ledger can never be touched here. Callers
    must pass a research shadow table (SHADOW_TABLE / SHADOW_INTRADAY_TABLE),
    NEVER LEDGER_TABLE.
    """
    if not rows:
        return
    delete_query = (
        f'DELETE FROM `{table}` WHERE scan_date = "{target_date.isoformat()}"'
    )
    client.query(delete_query).result()
    logger.info(f"shadow: deleted prior rows for scan_date={target_date} in {table}")

    import io
    jsonl = "\n".join(json.dumps(r, default=str) for r in rows)
    load_job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
    )
    load_job = client.load_table_from_file(
        io.BytesIO(jsonl.encode("utf-8")),
        table,
        job_config=load_job_config,
    )
    load_job.result()
    logger.info(f"shadow: loaded {len(rows)} rows into {table}")


def get_previous_trading_day(base_date: date) -> date:
    start_date = base_date - timedelta(days=10)
    schedule = nyse.schedule(start_date=start_date, end_date=base_date)
    valid_dates = [d.date() for d in schedule.index if d.date() < base_date]
    return valid_dates[-1] if valid_dates else None

def get_nth_previous_trading_day(base_date: date, n: int) -> date:
    d = base_date
    for _ in range(n):
        d = get_previous_trading_day(d)
        if d is None:
            return None
    return d

def get_canonical_scan_date(today: date = None) -> date:
    """Return the scan_date whose hold window EXITS on `today`.

    A signal scanned on date X enters at next_trading_day(X) and, under V7
    (HOLD_DAYS=1, same-day), times out at nth_next_trading_day(entry, 0) = entry
    itself, flat at 15:45 ET. The cron fires at 16:30 ET after market close, so
    today's bars — including the 15:45 ET TIMEOUT bar — are already final and
    safe to simulate. We walk back HOLD_DAYS trading days from today: the
    entry-day lag (scan → entry) plus HOLD_DAYS-1 for the entry → exit span
    (which is 0 under V7, so scan_date = the prior trading day).

    This is the function the daily cron uses when no explicit target_date is
    provided.
    """
    if today is None:
        today = datetime.now(est).date()
    d = today
    # V7 HOLD_DAYS=1: walk back 1 trading day (entry-day lag; same-day exit).
    for _ in range(HOLD_DAYS):
        d = get_previous_trading_day(d)
    return d


def _coerce_float(v):
    """pandas/numpy scalar -> native float, or None for NaN/NaT/None."""
    try:
        return float(v) if v is not None and pd.notna(v) else None
    except (TypeError, ValueError):
        return None


def _coerce_int(v):
    """pandas/numpy scalar -> native int, or None for NaN/NaT/None."""
    try:
        return int(v) if v is not None and pd.notna(v) else None
    except (TypeError, ValueError):
        return None


def _write_enriched_outcomes(
    client: bigquery.Client,
    target_date: date,
    entry_day: date,
    exit_day: date,
    vix_level: float | None,
    spy_trend: str | None,
    vix_5d_delta: float | None,
    tournament_ticker: str | None,
) -> dict:
    """Replay the bracket over the FULL enriched BULLISH pool for one scan_date.

    Reuses the EXACT pool query shape from _write_topscore_shadow and the EXACT
    production simulator (_simulate_contract, pick_doc=None), then writes one row
    per candidate to ENRICHED_OUTCOMES_TABLE. Idempotent delete-then-load via
    _write_shadow_records (research table only — NEVER LEDGER_TABLE).

    Leakage-safe by construction: only point-in-time enriched feature columns are
    SELECTed (the win-tracker underlying-outcome columns next_day_pct/day2_pct/
    day3_pct/peak_return_3d/is_win/outcome_tier are DELIBERATELY NOT selected).
    Outcome columns are produced by the same forward-looking bracket replay the
    live trader uses, and stored in their own column group as labels.

    Returns a summary dict {pool_size, labeled, wins, losses}. Does not raise on
    a per-row simulation error — that row is skipped and counted in `errors`.
    """
    bull_filter = 'AND UPPER(direction) = "BULLISH"' if ENRICHED_OUTCOMES_BULLISH_ONLY else ""
    pool_sql = f"""
    SELECT
        ticker, scan_date, direction, recommended_contract, recommended_strike,
        recommended_expiration, recommended_dte, recommended_volume, recommended_oi,
        recommended_spread_pct, is_premium_signal, premium_score,
        overnight_score, catalyst_score, contract_score,
        recommended_delta, recommended_gamma, recommended_theta, recommended_vega,
        recommended_iv, risk_reward_ratio, atr_normalized_move, moneyness_pct,
        volume_oi_ratio, call_dollar_volume, put_dollar_volume,
        underlying_price, atr_14, rsi_14, vix3m_at_enrich
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      {bull_filter}
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND recommended_dte IS NOT NULL
      AND recommended_volume IS NOT NULL
      AND recommended_oi IS NOT NULL
    """
    pool_df = client.query(pool_sql).to_dataframe()
    pool_size = int(len(pool_df))
    if pool_size == 0:
        logger.info(f"enriched outcomes: empty pool for {target_date}; nothing to label")
        return {"pool_size": 0, "labeled": 0, "wins": 0, "losses": 0, "errors": 0}

    # Deterministic top-score arm flag — identical ranking to _write_topscore_shadow:
    # max overnight_score, tie-break GREATEST(call_dv, put_dv) desc.
    pool_df["_score"] = pd.to_numeric(pool_df["overnight_score"], errors="coerce").fillna(-1.0)
    pool_df["_uoa"] = pool_df[["call_dollar_volume", "put_dollar_volume"]].apply(
        lambda c: max(_coerce_float(c["call_dollar_volume"]) or 0.0,
                      _coerce_float(c["put_dollar_volume"]) or 0.0),
        axis=1,
    )
    ranked = pool_df.sort_values(by=["_score", "_uoa"], ascending=[False, False],
                                 kind="mergesort").reset_index(drop=True)
    topscore_ticker = str(ranked.iloc[0]["ticker"]).upper()
    tour_ticker = (tournament_ticker or "").upper()

    labeled_at = datetime.now(est)
    rows: list[dict] = []
    wins = losses = errors = 0
    for _, prow in pool_df.iterrows():
        try:
            # Identical mechanics to the live trade (pick_doc=None → policy_gate
            # falls back to the service constant; no Firestore doc needed).
            rec = _simulate_contract(
                client, prow, entry_day, exit_day,
                vix_level, spy_trend, vix_5d_delta, pick_doc=None,
            )
        except Exception as e:  # noqa: BLE001 — one bad contract must not abort the pool
            errors += 1
            logger.warning(f"enriched outcomes: sim failed for {prow.get('ticker')} on {target_date}: {e}")
            continue

        ret = rec.get("realized_return_pct")
        if ret is not None:
            if ret > 0:
                wins += 1
            else:
                losses += 1

        row_ticker = str(prow["ticker"]).upper()
        exp = prow["recommended_expiration"]
        out = {
            # ---- IDENTITY ----
            "scan_date": rec["scan_date"],
            "entry_day": entry_day,
            "exit_day": exit_day,
            "ticker": rec["ticker"],
            "direction": rec["direction"],
            "recommended_contract": rec["recommended_contract"],
            "recommended_strike": _coerce_float(prow["recommended_strike"]),
            "recommended_expiration": exp.date() if isinstance(exp, (datetime, pd.Timestamp)) else exp,
            "recommended_dte": rec["recommended_dte"],
            # ---- FEATURES (point-in-time, leakage-safe) ----
            "recommended_delta": _coerce_float(prow["recommended_delta"]),
            "risk_reward_ratio": _coerce_float(prow["risk_reward_ratio"]),
            "atr_normalized_move": _coerce_float(prow["atr_normalized_move"]),
            "moneyness_pct": _coerce_float(prow["moneyness_pct"]),
            "recommended_gamma": _coerce_float(prow["recommended_gamma"]),
            "recommended_theta": _coerce_float(prow["recommended_theta"]),
            "recommended_vega": _coerce_float(prow["recommended_vega"]),
            "recommended_iv": _coerce_float(prow["recommended_iv"]),
            "recommended_spread_pct": rec["recommended_spread_pct"],
            "recommended_volume": rec["recommended_volume"],
            "recommended_oi": rec["recommended_oi"],
            "volume_oi_ratio": _coerce_float(prow["volume_oi_ratio"]),
            "contract_score": _coerce_float(prow["contract_score"]),
            "call_dollar_volume": _coerce_float(prow["call_dollar_volume"]),
            "put_dollar_volume": _coerce_float(prow["put_dollar_volume"]),
            "overnight_score": _coerce_int(prow["overnight_score"]),
            "premium_score": rec["premium_score"],
            "is_premium_signal": rec["is_premium_signal"],
            "catalyst_score": _coerce_float(prow["catalyst_score"]),
            "underlying_price": _coerce_float(prow["underlying_price"]),
            "atr_14": _coerce_float(prow["atr_14"]),
            "rsi_14": _coerce_float(prow["rsi_14"]),
            # ---- REGIME (point-in-time) ----
            "VIX_at_entry": rec["VIX_at_entry"],
            "SPY_trend_state": rec["SPY_trend_state"],
            "vix_5d_delta_entry": rec["vix_5d_delta_entry"],
            "vix3m_at_enrich": _coerce_float(prow["vix3m_at_enrich"]),
            # ---- OUTCOME (realized labels) ----
            "entry_timestamp": rec["entry_timestamp"],
            "entry_price": rec["entry_price"],
            "target_price": rec["target_price"],
            "stop_price": rec["stop_price"],
            "trail_trigger_price": rec["trail_trigger_price"],
            "peak_premium": rec["peak_premium"],
            "trail_activated": rec["trail_activated"],
            "trail_stop_at_exit": rec["trail_stop_at_exit"],
            "exit_timestamp": rec["exit_timestamp"],
            "exit_reason": rec["exit_reason"],
            "realized_return_pct": rec["realized_return_pct"],
            "exit_slippage": rec["exit_slippage"],
            "illiquid_exit": rec["illiquid_exit"],
            "late_fill_minutes": rec["late_fill_minutes"],
            "iv_rank_entry": rec["iv_rank_entry"],
            "iv_percentile_entry": rec["iv_percentile_entry"],
            "hv_20d_entry": rec["hv_20d_entry"],
            "underlying_entry_price": rec["underlying_entry_price"],
            "underlying_exit_price": rec["underlying_exit_price"],
            "underlying_return": rec["underlying_return"],
            "spy_entry_price": rec["spy_entry_price"],
            "spy_exit_price": rec["spy_exit_price"],
            "spy_return_over_window": rec["spy_return_over_window"],
            # ---- LINKAGE / META ----
            "was_tournament_pick": (row_ticker == tour_ticker) if tour_ticker else False,
            "was_topscore_pick": (row_ticker == topscore_ticker),
            "pool_size": pool_size,
            "policy_version": rec["policy_version"],
            "labeled_at": labeled_at,
        }
        rows.append(out)

    # Idempotent delete-then-load into the research table ONLY (never LEDGER_TABLE).
    _write_shadow_records(client, ENRICHED_OUTCOMES_TABLE, target_date, rows)
    logger.info(
        f"enriched outcomes {target_date}: labeled {len(rows)}/{pool_size} "
        f"(wins={wins} losses={losses} errors={errors}); tournament={tour_ticker or 'n/a'} "
        f"topscore={topscore_ticker}"
    )
    return {"pool_size": pool_size, "labeled": len(rows), "wins": wins,
            "losses": losses, "errors": errors}


def run_label_enriched_pool(target_date: date = None) -> tuple[bool, dict | str]:
    """Driver for the daily counterfactual labeling of the enriched pool.

    Same date/timing contract as run_forward_paper_trading: simulate ONLY when
    the same-day hold window has fully closed (refuse future windows so no partial
    intraday bar masquerades as a TIMEOUT exit). Writes ONLY to
    ENRICHED_OUTCOMES_TABLE; never touches forward_paper_ledger or any live
    surface. Backfill-safe (idempotent per scan_date).
    """
    if not target_date:
        target_date = get_canonical_scan_date()

    entry_day = get_next_trading_day(target_date)
    today_et = datetime.now(est).date()
    if entry_day > today_et:
        return False, f"Entry day {entry_day} is in the future; nothing to label."
    exit_day = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)
    if exit_day > today_et:
        return False, (f"Exit day {exit_day} is in the future; hold window not closed, "
                       f"refusing to label.")

    vix_level, spy_trend, vix_5d_delta = get_regime_context(entry_day)

    # Best-effort lookup of the live tournament pick for linkage (None on any
    # failure — backfill of old dates still has todays_pick docs dual-written).
    tournament_ticker = None
    try:
        _, _, tournament_ticker = _fetch_todays_pick(target_date)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"enriched outcomes: todays_pick lookup failed for {target_date}: {e}")

    client = bigquery.Client(project=PROJECT_ID)
    summary = _write_enriched_outcomes(
        client, target_date, entry_day, exit_day,
        vix_level, spy_trend, vix_5d_delta, tournament_ticker,
    )
    return True, {"scan_date": target_date.isoformat(), "entry_day": entry_day.isoformat(),
                  "exit_day": exit_day.isoformat(), **summary}


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


def run_mark_to_market() -> tuple[bool, dict]:
    """Daily EOD mark-to-market snapshot for V5.4 open positions.

    An "open position" is a pick whose entry_day has occurred but whose hold
    window has not yet fully closed (today <= exit_day). We discover them by
    walking the last HOLD_DAYS entry_day candidates (today, today-1td,
    today-2td) and reading each corresponding todays_pick doc.
    For each open position we pull the option's intraday bars from entry_day
    through today, derive entry_price (10:00 ET on entry_day with the same
    2% slippage the trader uses) and the current EOD mid, and write one
    snapshot row to forward_paper_ledger_intraday.

    Read-only against the canonical ledger. The hard exit at HOLD_DAYS day-N
    is still owned by run_forward_paper_trading — this function never closes
    a position, only observes it.
    """
    client = bigquery.Client(project=PROJECT_ID)
    db = firestore.Client(project=PROJECT_ID)
    today_et = datetime.now(est).date()
    snapshot_ts_iso = datetime.now(est).isoformat()

    rows: list[dict] = []
    inspected = 0

    # Open positions can have entry_day in {today, today-1td, today-2td}.
    # We iterate scan_date = entry_day - 1 trading day for each.
    for n in range(HOLD_DAYS):
        entry_day = today_et if n == 0 else get_nth_previous_trading_day(today_et, n)
        if entry_day is None:
            continue
        scan_date = get_previous_trading_day(entry_day)
        if scan_date is None:
            continue
        inspected += 1

        # Read the pick.
        try:
            snap = db.collection("todays_pick").document(scan_date.isoformat()).get()
        except Exception as e:
            logger.warning(f"MTM: todays_pick read failed for {scan_date}: {e}")
            continue
        if not snap.exists:
            continue
        pick = snap.to_dict() or {}
        if not pick.get("has_pick"):
            continue
        ticker = pick.get("ticker")
        if not ticker:
            continue

        # Hydrate full contract details from overnight_signals_enriched. The
        # pick doc carries ticker + direction; the enriched row carries the
        # canonical strike/expiration we need to build the Polygon option ID.
        enriched_sql = f"""
        SELECT ticker, direction, recommended_contract, recommended_strike,
               recommended_expiration
        FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
        WHERE DATE(scan_date) = "{scan_date.isoformat()}"
          AND UPPER(ticker) = "{str(ticker).upper()}"
          AND recommended_strike IS NOT NULL
          AND recommended_expiration IS NOT NULL
        ORDER BY premium_score DESC, recommended_volume DESC
        LIMIT 1
        """
        try:
            edf = client.query(enriched_sql).to_dataframe()
        except Exception as e:
            logger.warning(f"MTM: enriched lookup failed for {ticker}@{scan_date}: {e}")
            continue
        if len(edf) == 0:
            logger.info(f"MTM: no enriched row for {ticker}@{scan_date}; skip")
            continue
        row = edf.iloc[0]

        exp_date = row["recommended_expiration"].date() if isinstance(row["recommended_expiration"], (pd.Timestamp, datetime)) else row["recommended_expiration"]
        opt_ticker = build_polygon_ticker(
            row["ticker"], exp_date, row["direction"], float(row["recommended_strike"])
        )

        exit_day = get_nth_next_trading_day(entry_day, HOLD_DAYS - 1)
        # Past the hold window — let the daily exit cron own this one.
        if today_et > exit_day:
            continue
        # Before entry — pick is published but entry hasn't happened yet.
        if today_et < entry_day:
            continue

        bars = fetch_minute_bars(opt_ticker, entry_day, today_et)
        time.sleep(0.2)
        if not bars:
            logger.info(f"MTM: no bars for {opt_ticker} {entry_day}→{today_et}; skip")
            continue

        # Entry bar (mirrors run_forward_paper_trading): first bar at or after
        # 10:00 ET on entry_day, with the trader's 2% slippage applied.
        entry_dt = datetime.combine(entry_day, datetime.strptime(ENTRY_HHMM, "%H:%M").time())
        entry_ts_ms = int(est.localize(entry_dt).timestamp() * 1000)
        entry_day_bars = [b for b in bars
                          if datetime.fromtimestamp(b["t"]/1000, tz=est).date() == entry_day]
        entry_bar = None
        if entry_day_bars:
            after = [b for b in entry_day_bars if b["t"] >= entry_ts_ms]
            if after:
                entry_bar = after[0]
            else:
                before = [b for b in entry_day_bars if b["t"] < entry_ts_ms]
                entry_bar = before[-1] if before else None
        if not entry_bar or entry_bar.get("v", 0) == 0:
            logger.info(f"MTM: invalid entry bar for {opt_ticker} on {entry_day}; skip")
            continue
        entry_price = entry_bar["c"] * 1.02

        # Post-entry walk: peak high + EOD mid (today's last bar close).
        post_entry = [b for b in bars if b["t"] >= entry_bar["t"]]
        peak = max(b["h"] for b in post_entry) if post_entry else entry_price
        current_mid = post_entry[-1]["c"] if post_entry else entry_bar["c"]

        # trading_day_idx: 1 on entry_day, 2 on entry+1td, 3 on entry+2td.
        trading_day_idx = n + 1  # n=0 → today is entry_day → idx 1

        unrealized = (current_mid - entry_price) / entry_price if entry_price else None
        trail_armed = bool(peak >= entry_price * (1.0 + TRAIL_TRIGGER_PCT))

        rows.append({
            "scan_date": scan_date.isoformat(),
            "ticker": row["ticker"],
            "direction": row["direction"],
            "recommended_contract": row["recommended_contract"],
            "entry_day": entry_day.isoformat(),
            "exit_day": exit_day.isoformat(),
            "snapshot_date": today_et.isoformat(),
            "snapshot_ts": snapshot_ts_iso,
            "trading_day_idx": trading_day_idx,
            "entry_price": entry_price,
            "current_mid": current_mid,
            "peak_mid": peak,
            "unrealized_return_pct": unrealized,
            "trail_armed": trail_armed,
            "underlying_close": None,
            "policy_version": POLICY_VERSION,
        })

    if not rows:
        logger.info(f"MTM: {inspected} scan_date(s) inspected, 0 open positions found")
        return True, {"rows_written": 0, "scan_dates_inspected": inspected}

    # Idempotent write: delete any prior snapshot for today, then load.
    delete_sql = f'DELETE FROM `{INTRADAY_TABLE}` WHERE snapshot_date = "{today_et.isoformat()}"'
    try:
        client.query(delete_sql).result()
    except Exception as e:
        logger.error(f"MTM: pre-write DELETE failed: {e}")
        return False, {"error": f"Pre-write DELETE failed: {e}"}

    import io
    jsonl = "\n".join(json.dumps(r, default=str) for r in rows)
    load_job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    load_job = client.load_table_from_file(
        io.BytesIO(jsonl.encode("utf-8")),
        INTRADAY_TABLE,
        job_config=load_job_config,
    )
    load_job.result()
    logger.info(f"MTM: loaded {len(rows)} snapshot row(s) for {today_et}")
    return True, {"rows_written": len(rows), "scan_dates_inspected": inspected}


@app.route("/mark_to_market", methods=["POST", "GET"])
def trigger_mark_to_market():
    """Daily EOD MTM endpoint — hit by Cloud Scheduler ~16:15 ET, before the
    16:30 ET exit cron. Snapshots open V5.4 positions for the webapp live
    panel. Non-blocking with respect to the realized-PnL exit logic.
    """
    try:
        success, result = run_mark_to_market()
        if success:
            return jsonify({"status": "success", **result}), 200
        return jsonify({"status": "error", "message": str(result)}), 500
    except Exception as e:
        logger.error(f"Error in mark-to-market endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


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
            # Default: process the most recent scan_date whose same-day hold window
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


@app.route("/label_enriched_pool", methods=["POST", "GET"])
def trigger_label_enriched_pool():
    """RESEARCH-ONLY counterfactual labeling endpoint.

    Replays the live V7 bracket (+40/-30, same-day flat 15:45) over the FULL
    enriched BULLISH pool for one scan_date and writes one outcome row per
    candidate to enriched_option_outcomes. Hit by a dedicated daily Cloud
    Scheduler cron AFTER the trade-exit cron (the cohort whose hold window just
    closed). Writes ONLY to
    the research table — never forward_paper_ledger or any live surface. Accepts
    an optional {"target_date": "YYYY-MM-DD"} for backfill; defaults to the
    canonical just-closed scan_date.
    """
    try:
        req_data = request.get_json(silent=True) or {}
        target_date_str = req_data.get("target_date")
        target_date = (datetime.strptime(target_date_str, "%Y-%m-%d").date()
                       if target_date_str else get_canonical_scan_date())
        success, result = run_label_enriched_pool(target_date)
        if success:
            return jsonify({"status": "success", **result}), 200
        return jsonify({"status": "error", "message": result}), 500
    except Exception as e:
        logger.error(f"Error in label_enriched_pool endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)





