"""Benchmarking and regime-context helpers for the forward paper trader.

This module enriches every ledger row with decision-support and diagnostic
context without touching the entry gate or the bracket logic. All functions
are NON-BLOCKING: on any external-fetch failure, they return None and the
trader writes NULL for the affected column. The benchmarking layer must never
be able to prevent a trade from being written.

Responsibilities:
    - fetch_hv_20d            20-day historical realized volatility on the
                               underlying (from Polygon daily bars, free)
    - fetch_iv_rank_stub      placeholder for IV Rank / IV Percentile.
                               Returns (None, None) until a real vendor is
                               wired in. See module docstring below.
    - get_spy_bars_cached     SPY minute bars for a (start, end) window, cached
                               in-process so SPY is fetched at most once per
                               scan_date rather than per signal.
    - find_price_at_or_after  locate the first Polygon bar at-or-after a given
                               ms-epoch timestamp; returns None if no bar.
    - find_price_at_or_before locate the last Polygon bar at-or-before a given
                               ms-epoch timestamp; returns None if no bar.

IV Rank / IV Percentile status
------------------------------
Computing IVR/IVP properly requires 252 trading days of ATM implied-vol
history per underlying ticker. No free single-call API exposes this:
    - Tradier returns per-contract snapshot IV, not trailing underlying IV.
    - Polygon exposes per-contract IV via daily snapshots; a proper IVR would
      require pulling the ATM contract's IV for each of the last 252 days per
      ticker, which is rate-limit-prohibitive at trade time.
    - ORATS (paid) and tastytrade (free with account) expose IVR directly.

Until one of those is provisioned, `fetch_iv_rank_stub` returns (None, None)
and the ledger columns `iv_rank_entry` / `iv_percentile_entry` stay null.
The stub is intentionally a stub — replacing it with a real client should be
a drop-in edit to this one function.

As a functional substitute, HV_20d combined with the already-written
`recommended_iv` column gives us the IV-HV spread directly in SQL:
    recommended_iv - hv_20d_entry  ==  the vega tax per trade
which is the metric the Cao & Han "volatility-idiosyncratic trap" literature
actually cares about.
"""

from __future__ import annotations

import logging
import math
import os
import time
from datetime import date, datetime, timedelta
from typing import Optional

import requests

logger = logging.getLogger(__name__)

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "").strip()
TRADIER_API_KEY = os.environ.get("TRADIER_API_KEY", "").strip()
POLYGON_BASE = "https://api.polygon.io"

# In-process SPY bar cache. Keyed by (start_iso, end_iso) → list of Polygon bars.
# One SPY fetch per (start, end) per trader invocation; all signals in the
# same scan_date share the same window and therefore the same cache entry.
_SPY_BAR_CACHE: dict[tuple[str, str], list] = {}

# Lazy module-level BigQuery client so importing this module doesn't require
# cloud auth at test time.
_BQ_CLIENT = None

def _bq_client():
    global _BQ_CLIENT
    if _BQ_CLIENT is None:
        from google.cloud import bigquery
        _BQ_CLIENT = bigquery.Client(project="profitscout-fida8")
    return _BQ_CLIENT


# ---------------------------------------------------------------------------
# Rate limiter for Polygon batch calls (options chain cache job).
# Simple sliding window; mirrors src/enrichment/core/clients/polygon_client.py.
# ---------------------------------------------------------------------------

class _RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls, self.period = max_calls, period
        self._ts: list[float] = []

    def acquire(self) -> None:
        now = time.time()
        self._ts = [t for t in self._ts if now - t < self.period]
        if len(self._ts) >= self.max_calls:
            sleep_for = (self._ts[0] + self.period) - now
            if sleep_for > 0:
                time.sleep(sleep_for)
        self._ts.append(time.time())


_POLYGON_RL = _RateLimiter(max_calls=15, period=1.0)


# ---------------------------------------------------------------------------
# Polygon helpers (mirror forward-paper-trader/main.py's fetch_minute_bars
# but defined here to keep benchmark_context import-safe with no circular
# dependency on main.py).
# ---------------------------------------------------------------------------

def _polygon_minute_bars(ticker: str, start: date, end: date) -> list:
    """Fetch 1-minute Polygon bars for any ticker (stock OR option)."""
    if not POLYGON_API_KEY:
        return []
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}"
        f"/range/1/minute/{start.isoformat()}/{end.isoformat()}"
    )
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": POLYGON_API_KEY,
    }
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("results", []) or []
        except Exception as e:
            logger.warning(f"benchmark_context: Polygon minute-bar error for {ticker}: {e}")
            time.sleep(1)
    return []


def _polygon_daily_bars(ticker: str, start: date, end: date) -> list:
    """Fetch 1-day Polygon bars for an underlying. Used for HV_20d."""
    if not POLYGON_API_KEY:
        return []
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}"
        f"/range/1/day/{start.isoformat()}/{end.isoformat()}"
    )
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 500,
        "apiKey": POLYGON_API_KEY,
    }
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("results", []) or []
        except Exception as e:
            logger.warning(f"benchmark_context: Polygon daily-bar error for {ticker}: {e}")
            time.sleep(1)
    return []


# ---------------------------------------------------------------------------
# SPY cache
# ---------------------------------------------------------------------------

def get_spy_bars_cached(start: date, end: date) -> list:
    """Return Polygon SPY minute bars for [start, end], fetched once per window.

    The cache key is the (start_iso, end_iso) pair. A single trader invocation
    processes one scan_date, which produces one (entry_day, timeout_day) window,
    so the cache holds exactly one entry per invocation in practice.
    """
    key = (start.isoformat(), end.isoformat())
    if key in _SPY_BAR_CACHE:
        return _SPY_BAR_CACHE[key]
    bars = _polygon_minute_bars("SPY", start, end)
    _SPY_BAR_CACHE[key] = bars
    return bars


# ---------------------------------------------------------------------------
# Price locators
# ---------------------------------------------------------------------------

def find_price_at_or_after(bars: list, ts_ms: int) -> Optional[float]:
    """First bar close at-or-after ts_ms (or None if no such bar)."""
    if not bars:
        return None
    for b in bars:
        if b.get("t", 0) >= ts_ms:
            try:
                return float(b["c"])
            except (KeyError, TypeError, ValueError):
                return None
    return None


def find_price_at_or_before(bars: list, ts_ms: int) -> Optional[float]:
    """Last bar close at-or-before ts_ms (or None if no such bar)."""
    if not bars:
        return None
    last = None
    for b in bars:
        if b.get("t", 0) <= ts_ms:
            last = b
        else:
            break
    if last is None:
        return None
    try:
        return float(last["c"])
    except (KeyError, TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 20-day historical realized volatility
# ---------------------------------------------------------------------------

def fetch_hv_20d(ticker: str, entry_day: date) -> Optional[float]:
    """Annualized 20-day realized volatility from daily log returns.

    Pulls ~35 calendar days of daily bars ending on entry_day (to ensure we
    have at least 20 trading-day closes), computes log returns, returns
    stdev * sqrt(252). Returns None on any failure.
    """
    try:
        start = entry_day - timedelta(days=45)
        bars = _polygon_daily_bars(ticker, start, entry_day)
        if len(bars) < 21:
            return None
        closes = [b["c"] for b in bars[-21:]]  # 21 closes → 20 returns
        log_returns = []
        for i in range(1, len(closes)):
            prev, cur = closes[i - 1], closes[i]
            if prev and prev > 0 and cur > 0:
                log_returns.append(math.log(cur / prev))
        if len(log_returns) < 5:
            return None
        mean = sum(log_returns) / len(log_returns)
        var = sum((r - mean) ** 2 for r in log_returns) / (len(log_returns) - 1)
        return math.sqrt(var) * math.sqrt(252)
    except Exception as e:
        logger.warning(f"benchmark_context: HV_20d compute failed for {ticker}: {e}")
        return None


# ---------------------------------------------------------------------------
# Polygon options-chain helpers (for the daily /cache_iv endpoint)
# ---------------------------------------------------------------------------

def _polygon_get(url: str, params: dict | None = None) -> dict | None:
    """Rate-limited GET against Polygon with minimal retry. Returns parsed JSON
    or None on any failure. Used by the options-chain cache path; the
    per-trade minute-bar fetchers have their own loop and do not share this.
    """
    if not POLYGON_API_KEY:
        return None
    params = dict(params or {})
    params["apiKey"] = POLYGON_API_KEY
    for attempt in range(3):
        try:
            _POLYGON_RL.acquire()
            resp = requests.get(url, params=params, timeout=20)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt == 2:
                logger.warning(f"benchmark_context: Polygon GET failed {url}: {e}")
                return None
            time.sleep(1)
    return None


def _map_contract(r: dict) -> dict:
    """Flatten a Polygon options snapshot result into a simple dict."""
    details = r.get("details") or {}
    und = r.get("underlying_asset") or {}
    day = r.get("day") or {}
    last_trade = r.get("last_trade") or {}

    # Underlying price: try multiple paths (match polygon_client.py heuristics).
    upx = None
    v = und.get("price")
    if isinstance(v, (int, float)):
        upx = float(v)
    if upx is None:
        s = und.get("session") or {}
        for k in ("price", "close", "previous_close", "prev_close"):
            v = s.get(k)
            if isinstance(v, (int, float)):
                upx = float(v)
                break
    if upx is None:
        lt_px = (und.get("last_trade") or {}).get("price")
        if isinstance(lt_px, (int, float)):
            upx = float(lt_px)

    return {
        "contract_symbol": details.get("ticker"),
        "option_type": (details.get("contract_type") or "").lower(),
        "expiration_date": details.get("expiration_date"),
        "strike": details.get("strike_price"),
        "implied_volatility": r.get("implied_volatility"),
        "volume": r.get("volume", day.get("volume")),
        "open_interest": r.get("open_interest"),
        "underlying_price": upx,
    }


def fetch_underlying_price_snapshot(ticker: str) -> Optional[float]:
    """Single-call stock snapshot → last price, used to compute ATM for a chain.

    Polygon's /v3/snapshot/options/{ticker} endpoint returns `underlying_asset`
    as just {"ticker": X}; the price is not included. We need a separate hit
    against the stocks snapshot endpoint.
    """
    if not ticker:
        return None
    url = f"{POLYGON_BASE}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
    j = _polygon_get(url)
    if not j:
        return None
    t = j.get("ticker") or {}
    # Prefer lastTrade.p, then day.c, then prevDay.c.
    for path in (
        ("lastTrade", "p"),
        ("day", "c"),
        ("prevDay", "c"),
        ("min", "c"),
    ):
        obj = t
        for k in path:
            obj = (obj or {}).get(k)
        if isinstance(obj, (int, float)) and obj > 0:
            return float(obj)
    return None


def fetch_options_chain_for_underlying(ticker: str, max_days: int = 60) -> list[dict]:
    """Paginated Polygon options chain snapshot for a single underlying.

    Returns a list of mapped contract dicts, each with `underlying_price`
    backfilled from a separate stock-snapshot call. Restricts to expirations
    strictly AFTER today (skip expiring-today contracts, they have no IV)
    and within `max_days` of today. Returns [] on any failure.
    """
    if not ticker:
        return []
    url = f"{POLYGON_BASE}/v3/snapshot/options/{ticker}"
    params: dict | None = {"limit": 250}
    out: list[dict] = []
    today = date.today()
    min_exp = today + timedelta(days=1)
    max_exp = today + timedelta(days=max_days)

    # Paginate until next_url is absent. Cap pagination to 25 pages defensively;
    # ultra-liquid underlyings like SPY have thousands of contracts across
    # many expirations and need deeper pagination than single-name equities.
    for _ in range(25):
        j = _polygon_get(url, params=params)
        if not j:
            break
        for r in j.get("results") or []:
            mapped = _map_contract(r)
            exp_str = mapped.get("expiration_date")
            if not exp_str:
                continue
            try:
                exp_d = date.fromisoformat(exp_str)
            except Exception:
                continue
            if not (min_exp <= exp_d <= max_exp):
                continue
            out.append(mapped)
        next_url = j.get("next_url")
        if not next_url:
            break
        url, params = next_url, None

    # Backfill underlying price via a single stock-snapshot call.
    if out and all(c.get("underlying_price") is None for c in out):
        upx = fetch_underlying_price_snapshot(ticker)
        if upx is not None:
            for c in out:
                c["underlying_price"] = upx

    return out


def compute_atm_iv_for_dte(chain: list[dict], target_dte: int = 30) -> dict | None:
    """Given a mapped options chain, return the ATM contract whose expiration
    is closest to `target_dte` among contracts that have IV populated.

    Returns dict with atm_iv_30d, dte_used, strike_used, contract_symbol,
    underlying_px — or None if nothing usable.
    """
    if not chain:
        return None

    upx = None
    for c in chain:
        if c.get("underlying_price"):
            upx = float(c["underlying_price"])
            break
    if upx is None or upx <= 0:
        return None

    today = date.today()

    # Strict: only consider contracts that have IV populated AND a strike
    # within ±15% of the underlying. This rules out deep ITM/OTM contracts
    # that may report stale or missing IV from Polygon.
    usable = [
        c for c in chain
        if c.get("implied_volatility") is not None
        and c.get("strike") is not None
        and c.get("expiration_date") is not None
        and abs(float(c["strike"]) - upx) / upx <= 0.15
    ]
    if not usable:
        return None

    # Group by expiration; only keep expirations that actually have usable
    # (IV-populated, near-ATM) contracts.
    by_exp: dict[str, list[dict]] = {}
    for c in usable:
        by_exp.setdefault(c["expiration_date"], []).append(c)

    def dte_of(exp_str: str) -> int:
        try:
            return (date.fromisoformat(exp_str) - today).days
        except Exception:
            return 10**9

    # Rank expirations by DTE distance; this is safe because every key in
    # by_exp is guaranteed to have at least one usable contract.
    exp_ranked = sorted(by_exp.keys(), key=lambda e: abs(dte_of(e) - target_dte))
    if not exp_ranked:
        return None
    best_exp = exp_ranked[0]
    best_dte = dte_of(best_exp)

    # Prefer calls for consistency across tickers. Fall back to any side.
    candidates = by_exp[best_exp]
    calls = [c for c in candidates if c.get("option_type") == "call"]
    picks = calls or candidates
    atm = min(picks, key=lambda c: abs(float(c["strike"]) - upx))

    return {
        "atm_iv_30d": float(atm["implied_volatility"]),
        "dte_used": int(best_dte),
        "strike_used": float(atm["strike"]),
        "contract_symbol": atm.get("contract_symbol"),
        "underlying_px": float(upx),
    }


# ---------------------------------------------------------------------------
# IV Rank / IV Percentile — queried at trade time from polygon_iv_history
# ---------------------------------------------------------------------------

IV_HISTORY_TABLE = "profitscout-fida8.profit_scout.polygon_iv_history"
MIN_HISTORY_DAYS = 20  # return (None, None) below this; cache is too thin to rank


def fetch_iv_rank_from_bq(ticker: str, as_of: date) -> tuple[Optional[float], Optional[float]]:
    """Compute (iv_rank, iv_percentile) from the trailing 252 trading days of
    atm_iv_30d in polygon_iv_history.

    Returns (None, None) if:
      - BigQuery is unreachable or the table does not exist
      - fewer than MIN_HISTORY_DAYS observations exist for this ticker in the window
      - the current day's IV is not in the window

    This is expected to return (None, None) for the first ~20 trading days
    after the cache job goes live. That is correct behavior — IVR is
    undefined on a cold cache.
    """
    try:
        client = _bq_client()
        from google.cloud import bigquery
        sql = f"""
        SELECT atm_iv_30d
        FROM `{IV_HISTORY_TABLE}`
        WHERE ticker = @ticker
          AND as_of_date <= @as_of
          AND as_of_date >  DATE_SUB(@as_of, INTERVAL 252 DAY)
          AND atm_iv_30d IS NOT NULL
        ORDER BY as_of_date
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("ticker", "STRING", ticker),
                bigquery.ScalarQueryParameter("as_of", "DATE", as_of.isoformat()),
            ]
        )
        rows = list(client.query(sql, job_config=job_config).result())
        ivs = [float(r["atm_iv_30d"]) for r in rows if r["atm_iv_30d"] is not None]
        if len(ivs) < MIN_HISTORY_DAYS:
            return (None, None)
        lo, hi = min(ivs), max(ivs)
        current = ivs[-1]  # last row in chronological order
        if hi <= lo:
            return (None, None)
        iv_rank = (current - lo) / (hi - lo) * 100.0
        iv_percentile = sum(1 for x in ivs if x < current) / len(ivs) * 100.0
        return (float(iv_rank), float(iv_percentile))
    except Exception as e:
        logger.warning(f"fetch_iv_rank_from_bq failed for {ticker}: {e}")
        return (None, None)


# ---------------------------------------------------------------------------
# Aggregator — one call per signal from the trader loop
# ---------------------------------------------------------------------------

def fetch_underlying_context(
    ticker: str, entry_day: date
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Return (iv_rank, iv_percentile, hv_20d) for an underlying at entry_day.

    Non-blocking: any failure returns None for the affected field and the
    trader writes NULL. Never raises.
    """
    try:
        ivr, ivp = fetch_iv_rank_from_bq(ticker, entry_day)
    except Exception:
        ivr, ivp = None, None
    try:
        hv = fetch_hv_20d(ticker, entry_day)
    except Exception:
        hv = None
    return (ivr, ivp, hv)
