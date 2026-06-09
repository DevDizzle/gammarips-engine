"""Deterministic, point-in-time macro + sector context for the daily report.

Everything here is NON-BLOCKING and fail-open: every fetch returns a neutral /
UNKNOWN value on any error so a context blip can NEVER 404 the report. (An empty
report_md strips ALL market context from the tournament — far worse than a
missing block.) Every value is as-of scan_date — FRED bounded with cosd, Polygon
bounded with bar_date <= scan_date — so the whole block is reproducible
point-in-time and backtest-safe. NO web sources here (that lives elsewhere,
forward-only). Mirrors the benchmark_context.py "return None on failure" rule.
"""

import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import requests

logger = logging.getLogger(__name__)

POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "").strip()
FRED_LOOKBACK_DAYS = 45  # ~30 trailing trading days — enough for 1d/5d deltas


# ---------------------------------------------------------------------------
# FRED (keyless public CSV) — VIX, VIX term structure, rates
# ---------------------------------------------------------------------------

def _fred_series(series_id: str, scan_date: str) -> list[tuple[date, float]]:
    """Sorted [(date, value)] on/before scan_date, bounded by cosd. [] on failure.

    Bounding with cosd is mandatory: an unbounded fredgraph.csv serializes the
    series back to inception and times out (see the 2026-06-04 FRED outage fix).
    """
    try:
        target = datetime.strptime(scan_date, "%Y-%m-%d").date()
    except ValueError:
        return []
    cosd = (target - timedelta(days=FRED_LOOKBACK_DAYS)).isoformat()
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={cosd}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        text = resp.text
    except Exception as e:  # transport / timeout — degrade, never raise
        logger.warning(f"market_context: FRED {series_id} fetch failed: {e}")
        return []
    out: list[tuple[date, float]] = []
    for ln in text.strip().splitlines()[1:]:  # skip header
        parts = ln.split(",")
        if len(parts) < 2:
            continue
        dstr, vstr = parts[0].strip(), parts[1].strip()
        if not dstr or vstr in ("", "."):
            continue
        try:
            d = datetime.strptime(dstr, "%Y-%m-%d").date()
            v = float(vstr)
        except ValueError:
            continue
        if d <= target:  # point-in-time guard
            out.append((d, v))
    out.sort()
    return out


def _level_and_trend(series: list[tuple[date, float]], n_long: int = 5) -> dict | None:
    """Latest value + 1-step and n_long-step change off PRIOR available (trading-day)
    points — holiday/weekend-safe because we count available rows, not calendar days."""
    if not series:
        return None
    latest = series[-1][1]
    chg_1d = latest - series[-2][1] if len(series) > 1 else None
    chg_long = latest - series[-1 - n_long][1] if len(series) > n_long else None
    return {"value": latest, "chg_1d": chg_1d, "chg_long": chg_long}


def macro_regime(scan_date: str) -> dict:
    """VIX (level + 1d/5d trend), term structure, rates (10y/30y level + trend), and
    a composite risk-on/off label. Every field degrades to UNKNOWN, never raises."""
    vix = _level_and_trend(_fred_series("VIXCLS", scan_date))
    vix3m_series = _fred_series("VXVCLS", scan_date)
    ust10 = _level_and_trend(_fred_series("DGS10", scan_date))
    ust30 = _level_and_trend(_fred_series("DGS30", scan_date))

    m: dict = {"as_of": scan_date}

    # --- VIX level + trend ---
    if vix:
        v = vix["value"]
        m["vix"] = round(v, 2)
        m["vix_level_state"] = (
            "CALM" if v < 15 else "NORMAL" if v < 20 else "ELEVATED" if v < 28 else "STRESS"
        )
        c1, c5 = vix["chg_1d"], vix["chg_long"]
        m["vix_chg_1d"] = round(c1, 2) if c1 is not None else None
        m["vix_chg_5d"] = round(c5, 2) if c5 is not None else None
        if c1 is not None and c1 >= 2:
            m["vix_trend"] = "SPIKING"
        elif c5 is not None and c5 > 0:
            m["vix_trend"] = "RISING"
        elif c5 is not None and c5 < 0:
            m["vix_trend"] = "FALLING"
        elif c5 is not None:
            m["vix_trend"] = "QUIET"
        else:
            m["vix_trend"] = "UNKNOWN"
    else:
        m["vix_level_state"] = "UNKNOWN"
        m["vix_trend"] = "UNKNOWN"

    # --- VIX term structure (slack = how much contango) ---
    if vix and vix3m_series:
        vix3m = vix3m_series[-1][1]
        m["vix3m"] = round(vix3m, 2)
        slack = (vix3m - vix["value"]) / vix3m if vix3m else None
        if slack is not None:
            m["term_slack_pct"] = round(slack, 3)
            m["term_state"] = (
                "DEEP_CONTANGO" if slack >= 0.10
                else "THIN_CONTANGO" if slack > 0.01
                else "FLAT" if abs(slack) <= 0.01
                else "BACKWARDATION"
            )
        else:
            m["term_state"] = "UNKNOWN"
    else:
        m["term_state"] = "UNKNOWN"

    # --- Rates ---
    if ust10:
        r = ust10["value"]
        m["ust10y"] = round(r, 2)
        m["ust30y"] = round(ust30["value"], 2) if ust30 else None
        m["rate_state"] = (
            "BENIGN" if r < 4.0 else "ELEVATED" if r <= 4.5 else "RESTRICTIVE"
        )
        c5 = ust10["chg_long"]
        if c5 is not None and c5 > 0.10:
            m["rate_trend"] = "RISING"
        elif c5 is not None and c5 < -0.10:
            m["rate_trend"] = "FALLING"
        elif c5 is not None:
            m["rate_trend"] = "STABLE"
        else:
            m["rate_trend"] = "UNKNOWN"
    else:
        m["rate_state"] = "UNKNOWN"
        m["rate_trend"] = "UNKNOWN"

    # --- Composite risk-on/off (deterministic function of the above) ---
    m["risk_state"], m["risk_state_reasons"] = _risk_state(m)
    return m


def _risk_state(m: dict) -> tuple[str, list[str]]:
    """Bundle the regime fields into one label. Inherits UNKNOWN when core inputs
    are missing — NEVER defaults missing macro to RISK_ON (that would silently bias
    bullish exactly when data is unavailable)."""
    vix_state, vix_trend = m.get("vix_level_state"), m.get("vix_trend")
    if vix_state == "UNKNOWN" or vix_trend == "UNKNOWN":
        return "UNKNOWN", ["macro inputs unavailable"]
    on = off = 0
    reasons: list[str] = []
    if vix_trend in ("SPIKING", "RISING"):
        off += 1
        reasons.append(f"VIX {vix_trend.lower()}")
    elif vix_trend in ("FALLING", "QUIET"):
        on += 1
        reasons.append(f"VIX {vix_trend.lower()}")
    if vix_state in ("ELEVATED", "STRESS"):
        off += 1
        reasons.append(f"VIX {vix_state.lower()}")
    elif vix_state in ("CALM", "NORMAL"):
        on += 1
    if m.get("term_state") == "THIN_CONTANGO":
        off += 1
        reasons.append("thin contango")
    elif m.get("term_state") == "DEEP_CONTANGO":
        on += 1
    if m.get("rate_trend") == "RISING":
        off += 1
        reasons.append("rates rising")
    if off > on:
        return "RISK_OFF", reasons
    if on > off:
        return "RISK_ON", reasons or ["calm vol, contango"]
    return "MIXED", reasons or ["mixed signals"]


# ---------------------------------------------------------------------------
# Polygon sector-ETF momentum panel
# ---------------------------------------------------------------------------

SECTOR_ETFS = [
    "XLK", "SMH", "XLE", "XLF", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC",
]
SECTOR_LABELS = {
    "XLK": "Technology", "SMH": "Semiconductors", "XLE": "Energy", "XLF": "Financials",
    "XLV": "Healthcare", "XLY": "Consumer Cyclical", "XLP": "Consumer Defensive",
    "XLI": "Industrials", "XLU": "Utilities", "XLB": "Materials", "XLRE": "Real Estate",
    "XLC": "Communication",
}


def _polygon_daily_closes(ticker: str, start: date, end: date) -> list[tuple[date, float]]:
    """Sorted [(date, close)] for `ticker`, bar_date <= end. [] on no key/failure."""
    if not POLYGON_API_KEY:
        return []
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start.isoformat()}/{end.isoformat()}"
    params = {"adjusted": "true", "sort": "asc", "limit": 500, "apiKey": POLYGON_API_KEY}
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            resp.raise_for_status()
            rows = resp.json().get("results", []) or []
            out = []
            for b in rows:
                t, c = b.get("t"), b.get("c")
                if t is None or c is None:
                    continue
                d = datetime.utcfromtimestamp(t / 1000).date()
                if d <= end:  # point-in-time guard (redundant with `to`, kept explicit)
                    out.append((d, float(c)))
            out.sort()
            return out
        except Exception as e:
            logger.warning(f"market_context: Polygon {ticker} daily-bar error: {e}")
            time.sleep(1)
    return []


def _etf_metrics(etf: str, scan_date: str) -> dict | None:
    """ret_ytd / ret_1mo / ret_5d + 5-day drawdown in trailing-sigma units, as-of
    scan_date. Both the return windows AND the sigma window filter bar_date<=scan_date."""
    try:
        target = datetime.strptime(scan_date, "%Y-%m-%d").date()
    except ValueError:
        return None
    ytd_anchor = date(target.year, 1, 1)
    closes = _polygon_daily_closes(etf, ytd_anchor - timedelta(days=10), target)
    if len(closes) < 6:
        return None
    last = closes[-1][1]

    def _ret(ref_close: float | None) -> float | None:
        return round((last / ref_close - 1) * 100, 2) if ref_close else None

    ret_5d = _ret(closes[-6][1]) if len(closes) > 5 else None
    ret_1mo = _ret(closes[-22][1]) if len(closes) > 21 else _ret(closes[0][1])
    # YTD: earliest close on/after Jan 1
    ytd_ref = next((c for d, c in closes if d >= ytd_anchor), closes[0][1])
    ret_ytd = _ret(ytd_ref)

    # 5d drawdown in sigma: 5d % move / (daily-return sigma over trailing ~60 closes * sqrt(5))
    drawdown_5d_sigma = None
    tail = closes[-61:] if len(closes) > 61 else closes
    rets = [tail[i][1] / tail[i - 1][1] - 1 for i in range(1, len(tail)) if tail[i - 1][1]]
    if len(rets) >= 20 and ret_5d is not None:
        mean = sum(rets) / len(rets)
        var = sum((x - mean) ** 2 for x in rets) / (len(rets) - 1)
        sigma = var ** 0.5
        sigma_5d_pct = sigma * (5 ** 0.5) * 100
        if sigma_5d_pct > 1e-6:
            drawdown_5d_sigma = round((ret_5d) / sigma_5d_pct, 2)

    return {
        "etf": etf,
        "sector": SECTOR_LABELS.get(etf, etf),
        "ret_ytd": ret_ytd,
        "ret_1mo": ret_1mo,
        "ret_5d": ret_5d,
        "drawdown_5d_sigma": drawdown_5d_sigma,
    }


def sector_panel(scan_date: str) -> dict | None:
    """Per-ETF momentum panel + rotation flags, as-of scan_date. None on no key /
    total failure (report still renders without a Sector Tape)."""
    if not POLYGON_API_KEY:
        logger.info("market_context: no POLYGON_API_KEY — skipping sector panel")
        return None
    with ThreadPoolExecutor(max_workers=6) as ex:
        rows = list(ex.map(lambda e: _etf_metrics(e, scan_date), SECTOR_ETFS))
    panel = {r["etf"]: r for r in rows if r}
    if not panel:
        return None

    # Rotation flags over the ETFs PRESENT this scan_date (no cross-day contamination)
    ytds = sorted(r["ret_ytd"] for r in panel.values() if r["ret_ytd"] is not None)
    flags: dict[str, list[str]] = {}
    if len(ytds) >= 4:
        q_hi = ytds[int(len(ytds) * 0.75)]
        q_lo = ytds[int(len(ytds) * 0.25)]
        for etf, r in panel.items():
            tags = []
            y, dd, r5 = r["ret_ytd"], r["drawdown_5d_sigma"], r["ret_5d"]
            if y is not None and dd is not None and y >= q_hi and dd <= -2:
                tags.append("crowded_rotating")
            if y is not None and r5 is not None and y <= q_lo and r5 > 0:
                tags.append("oversold_lagging")
            if tags:
                flags[etf] = tags
    return {"as_of": scan_date, "etfs": panel, "rotation_flags": flags}
