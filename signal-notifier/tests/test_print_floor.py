"""Day-bar date validation + early-print floor tests (2026-08-07).

Covers the stale-day-bar defect: Polygon's v3 option snapshot serves the PRIOR
session's `day` bar when a contract has not printed today, and it NEVER serves a
zero-volume bar — so before this fix `_known_prints()` could not return 0 and the
early-print floor never dropped anything. See
docs/DECISIONS/2026-08-07-stale-day-bar-early-volume.md.

Pure-function tests: no live BigQuery, Firestore, Polygon or Vertex.

    .venv/bin/python -m pytest signal-notifier/tests/test_print_floor.py -q
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest
import pytz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402

EST = pytz.timezone("America/New_York")


def _et(y, m, d, hh, mm) -> datetime:
    return EST.localize(datetime(y, m, d, hh, mm))


def _ns(dt: datetime) -> int:
    """ET datetime -> Polygon epoch-nanosecond timestamp."""
    return int(dt.timestamp() * 1_000_000_000)


# The real GCT card from 2026-08-07: a prior-session day bar (2,045 contracts
# traded on 08-06) served at the 09:52 read on 08-07, on a contract whose live
# book showed volume 0 for the session. OI 44 -> 2,077 overnight was REAL.
GCT_READ_ET = _et(2026, 8, 7, 9, 52)
GCT_SNAPSHOT = {
    "results": {
        "open_interest": 2077,
        "implied_volatility": 0.71,
        "greeks": {"delta": 0.42, "gamma": 0.03, "theta": -0.08, "vega": 0.11},
        "day": {
            "volume": 2045,
            "open": 2.55,
            "high": 3.10,
            "low": 2.40,
            "close": 2.80,
            "last_updated": _ns(_et(2026, 8, 6, 16, 15)),
        },
        "last_trade": {"price": 2.80},
        "last_quote": {"bid": 2.65, "ask": 2.95},
    }
}


class _Resp:
    def __init__(self, body, status=200):
        self._body = body
        self.status_code = status
        self.text = str(body)

    def json(self):
        return self._body


def _fetch(body, read_dt=GCT_READ_ET, status=200):
    with patch.object(main, "POLYGON_API_KEY", "test-key"), \
            patch.object(main.requests, "get", return_value=_Resp(body, status)):
        return main._fetch_live_oi("GCT", "O:GCT260918C00055000", read_dt_et=read_dt)


# -- _fetch_live_oi: the four handoff cases + two guards ----------------------


def test_fresh_bar_today_passes_volume_through():
    body = {"results": dict(GCT_SNAPSHOT["results"])}
    body["results"]["day"] = dict(GCT_SNAPSHOT["results"]["day"])
    body["results"]["day"]["last_updated"] = _ns(_et(2026, 8, 7, 9, 37))
    live_oi, today_volume, status = _fetch(body)
    assert status == "ok"
    assert live_oi == 2077
    assert today_volume == 2045  # real prints today -> untouched


def test_stale_bar_becomes_known_zero_not_stale_count():
    """The GCT regression. 2045 is YESTERDAY's total; today's count is 0."""
    live_oi, today_volume, status = _fetch(GCT_SNAPSHOT)
    assert status == "ok"
    assert live_oi == 2077, "oi_build was real and must survive the fix"
    assert today_volume == 0, "stale bar must resolve to a KNOWN zero"
    assert today_volume is not None, "known-zero must not collapse into UNKNOWN"


def test_missing_day_dict_is_unknown():
    body = {"results": {"open_interest": 500}}
    live_oi, today_volume, status = _fetch(body)
    assert status == "ok"
    assert live_oi == 500
    assert today_volume is None


def test_fetch_error_is_unknown():
    with patch.object(main, "POLYGON_API_KEY", "test-key"), \
            patch.object(main.requests, "get", side_effect=RuntimeError("boom")):
        live_oi, today_volume, status = main._fetch_live_oi("GCT", "O:X")
    assert status == "polygon_error"
    assert live_oi is None and today_volume is None


def test_preopen_read_of_stale_bar_is_unknown_not_zero():
    """Before PRINT_VALID_AFTER_ET_MIN every bar is legitimately yesterday's on
    a 15-min-delayed feed. Asserting zero there would empty the whole slate."""
    _, today_volume, status = _fetch(GCT_SNAPSHOT, read_dt=_et(2026, 8, 7, 9, 20))
    assert status == "ok"
    assert today_volume is None


def test_undatable_bar_fails_open_to_unknown():
    """No last_updated -> we cannot assert the volume is today's. Fail open to
    the pre-fix keep rather than mass-dropping the slate."""
    body = {"results": {"open_interest": 900, "day": {"volume": 1234}}}
    _, today_volume, status = _fetch(body)
    assert status == "ok"
    assert today_volume is None


def test_returns_exactly_three_scalars_no_extra_field_escapes():
    """C1: the response carries IV / greeks / OHLC / trade / quote. Only
    (live_oi, today_volume, status) may cross the function boundary."""
    result = _fetch(GCT_SNAPSHOT)
    assert isinstance(result, tuple) and len(result) == 3
    live_oi, today_volume, status = result
    assert isinstance(live_oi, int) and isinstance(today_volume, int)
    assert status == "ok"


@pytest.mark.parametrize(
    "hh,mm,expect_zero",
    [(9, 49, False), (9, 50, True), (9, 52, True)],
)
def test_print_valid_after_et_min_boundary(hh, mm, expect_zero):
    """589 -> UNKNOWN, 590 -> may assert zero. The guard is a cliff, not a ramp."""
    _, today_volume, _ = _fetch(GCT_SNAPSHOT, read_dt=_et(2026, 8, 7, hh, mm))
    assert (today_volume == 0) is expect_zero


def test_future_dated_bar_is_undatable_not_zero():
    """A bar dated AFTER the read date is nonsense; never treat it as evidence."""
    body = {"results": {"open_interest": 900, "day": {
        "volume": 500, "last_updated": _ns(_et(2026, 8, 9, 16, 15))}}}
    _, today_volume, status = _fetch(body)
    assert status == "ok"
    assert today_volume is None


def test_absurdly_old_bar_fails_open_not_drop_everything():
    """The vendor-unit-change guard: if last_updated units changed ns->ms, every
    contract parses to ~1970 and the interlock must degrade to fail-open, NOT
    silently invert into dropping the entire slate."""
    body = {"results": {"open_interest": 900, "day": {
        "volume": 500, "last_updated": _ns(_et(2026, 8, 6, 16, 15)) // 1_000_000}}}
    _, today_volume, status = _fetch(body)
    assert status == "ok"
    assert today_volume is None, "out-of-range bar date must be UNKNOWN, not 0"


def test_restore_order_prefers_prints_over_known_zero():
    """Documented key is (prints desc NULLS LAST, live_oi desc). A name with
    real tape must outrank a known-zero even when the zero has far more OI —
    this is what kept GCT off the 08-07 slate under production OI_FLOOR."""
    rows = [_row("GOOD", 25, 3000)]
    rows += [_row("ZERO", 0, 99000), _row("PRINTED", 4, 1000)]
    rows += [_row(f"PAD{i}", 30, 250, rec_oi=250) for i in range(3)]
    out = _floor(rows)
    restored = out[out["_print_floor_restored"] == True]  # noqa: E712
    if len(restored) and "ZERO" in list(restored["ticker"]):
        assert "PRINTED" in list(out["ticker"]), (
            "a known-zero was restored while a prints-bearing name was not"
        )


def test_zero_volume_bar_dated_today_stays_zero():
    body = {"results": {"open_interest": 900, "day": {
        "volume": 0, "last_updated": _ns(_et(2026, 8, 7, 9, 37))}}}
    _, today_volume, _ = _fetch(body)
    assert today_volume == 0


# -- floor integration -------------------------------------------------------


def _row(ticker, today_volume, live_oi, rec_oi=5000):
    return {
        "ticker": ticker,
        "recommended_contract": f"O:{ticker}260918C00055000",
        "_today_volume": today_volume,
        "live_oi": live_oi,
        "recommended_oi": rec_oi,
    }


def _floor(rows):
    """Run the two-tier floor with the network refresh stubbed out."""
    df = pd.DataFrame(rows)
    with patch.object(main, "_refresh_live_oi_batch", side_effect=lambda d: d.copy()):
        return main._liquidity_refresh_and_rank(df)


def test_known_zero_is_dropped_and_unknown_is_kept():
    """PRINT_FLOOR_MIN=1: known 0 drops, None (fetch failure) fails open."""
    rows = [_row(f"OK{i}", 25, 6000) for i in range(main.TOURNEY_MIN)]
    rows += [_row("ZERO", 0, 9000), _row("UNKNOWN", None, 9000)]
    out = _floor(rows)
    tickers = list(out["ticker"])
    assert "ZERO" not in tickers, "known-zero print count must be dropped"
    assert "UNKNOWN" in tickers, "UNKNOWN must fail open, not drop"


def test_fail_soft_restore_marks_the_row():
    """Below TOURNEY_MIN survivors, dropped names come back flagged — the path
    that makes the judge-prompt second wall load-bearing."""
    rows = [_row("GOOD", 25, 6000)] + [_row(f"Z{i}", 0, 9000 - i) for i in range(4)]
    out = _floor(rows)
    assert len(out) > 1, "fail-soft must not let the slate starve"
    restored = out[out["_print_floor_restored"] == True]  # noqa: E712
    assert len(restored) >= 1
    assert all(main._known_prints(r) == 0 for _, r in restored.iterrows())


def test_all_known_zero_slate_still_returns_candidates():
    """Worst case after the fix: nothing on the slate has printed."""
    out = _floor([_row(f"Z{i}", 0, 9000 - i * 10) for i in range(6)])
    assert len(out) >= 1
    assert bool(out.iloc[0]["_print_floor_restored"]) is True


# -- email honesty -----------------------------------------------------------


@pytest.mark.parametrize(
    "today_volume,restored,expect_in,expect_not_in",
    [
        (2045, False, "2045 prints by ~09:52 (confirmed)", "UNVERIFIED"),
        (3, False, "CAUTION - thin tape", "confirmed"),
        (0, True, "NO TAPE - restored by fail-soft floor", "UNVERIFIED"),
        (None, True, "UNVERIFIED - restored by fail-soft floor", "prints by"),
        (None, False, "UNVERIFIED - live print count unavailable", "confirmed"),
    ],
)
def test_liquidity_email_line(today_volume, restored, expect_in, expect_not_in):
    row = pd.Series({"_today_volume": today_volume, "_print_floor_restored": restored})
    line = main._liquidity_email_line(row)
    assert expect_in in line
    assert expect_not_in not in line


def test_known_zero_never_renders_as_confirmed():
    """The GCT failure mode, asserted directly: a contract with no tape today
    can never produce a '(confirmed)' liquidity line."""
    _, today_volume, _ = _fetch(GCT_SNAPSHOT)
    row = pd.Series({"_today_volume": today_volume, "_print_floor_restored": True})
    line = main._liquidity_email_line(row)
    assert "confirmed" not in line
    assert "2045" not in line
