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


def _floor(rows, mode="none"):
    """Run the two-tier floor with the network refresh stubbed out.

    `mode` is FAILSOFT_RESTORE_MODE (2026-08-12). Production default is "none":
    a candidate that failed a floor never returns to the slate.
    """
    df = pd.DataFrame(rows)
    with patch.object(main, "_refresh_live_oi_batch", side_effect=lambda d: d.copy()), \
            patch.object(main, "FAILSOFT_RESTORE_MODE", mode):
        return main._liquidity_refresh_and_rank(df)


def test_known_zero_is_dropped_and_unknown_is_kept():
    """PRINT_FLOOR_MIN=1: known 0 drops, None (fetch failure) fails open."""
    rows = [_row(f"OK{i}", 25, 6000) for i in range(main.TOURNEY_MIN)]
    rows += [_row("ZERO", 0, 9000), _row("UNKNOWN", None, 9000)]
    out, stats = _floor(rows)
    tickers = list(out["ticker"])
    assert "ZERO" not in tickers, "known-zero print count must be dropped"
    assert "UNKNOWN" in tickers, "UNKNOWN must fail open, not drop"
    assert stats["measured"] is True
    assert stats["n_print_dropped"] == 1


# -- FAILSOFT_RESTORE_MODE (2026-08-12) --------------------------------------


def test_default_mode_never_restores_a_sub_floor_name():
    """THE regression fix. 08-12 in miniature: 4 genuine survivors, 8 rejects,
    TOURNEY_MIN=8 — the old code restored 4 rejects and the judge picked one of
    them (MDB, 44.6% spread). Under mode="none" the slate is the 4 survivors."""
    rows = [_row(f"GOOD{i}", 25, 6000) for i in range(4)]
    rows += [_row(f"ZERO{i}", 0, 9000) for i in range(4)]
    rows += [_row(f"THIN{i}", 30, 10, rec_oi=10) for i in range(4)]
    out, stats = _floor(rows)
    assert len(out) == 4, "restored rows must not pad the slate back to TOURNEY_MIN"
    assert set(out["ticker"]) == {f"GOOD{i}" for i in range(4)}
    assert not out["_print_floor_restored"].any()
    assert stats["n_restored"] == 0
    assert stats["n_pass"] == 4


def test_default_mode_returns_empty_when_nothing_clears():
    """Zero survivors is a measurement, not a failure: return the empty slate
    and let the caller emit no_liquid_candidates."""
    out, stats = _floor([_row(f"Z{i}", 0, 9000 - i * 10) for i in range(6)])
    assert len(out) == 0
    assert stats["measured"] is True, (
        "the caller keys its no-pick day off `measured` — an unmeasured empty "
        "slate must never become a no-pick day"
    )
    assert stats["n_pass"] == 0
    assert stats["n_total"] == 6


def test_empty_only_mode_restores_only_when_nothing_cleared():
    surv = [_row("GOOD", 25, 6000)] + [_row(f"Z{i}", 0, 9000) for i in range(4)]
    out, stats = _floor(surv, mode="empty_only")
    assert list(out["ticker"]) == ["GOOD"], "a survivor exists -> no restores"
    assert stats["n_restored"] == 0

    out, stats = _floor([_row(f"Z{i}", 0, 9000 - i) for i in range(4)], mode="empty_only")
    assert len(out) >= 1, "nothing cleared -> restore rather than stand down"
    assert stats["n_restored"] >= 1
    assert bool(out.iloc[0]["_print_floor_restored"]) is True


def test_always_mode_reproduces_the_pre_fix_behavior():
    """The rollback lever must still be the old (defective) behavior, exactly."""
    rows = [_row("GOOD", 25, 6000)] + [_row(f"Z{i}", 0, 9000 - i) for i in range(4)]
    out, stats = _floor(rows, mode="always")
    assert len(out) == main.TOURNEY_MIN - 3, "restores pad toward TOURNEY_MIN"
    assert stats["n_restored"] == 4
    restored = out[out["_print_floor_restored"] == True]  # noqa: E712
    assert all(main._known_prints(r) == 0 for _, r in restored.iterrows())


def test_unknown_mode_falls_back_to_never_restore():
    """A typo'd env var must fail to the SAFE mode, not the defective one."""
    out, _ = _floor([_row("GOOD", 25, 6000)] + [_row(f"Z{i}", 0, 9000) for i in range(4)],
                    mode="restore_everything_please")
    assert list(out["ticker"]) == ["GOOD"]


def test_restore_order_prefers_prints_over_known_zero():
    """Documented key is (prints desc NULLS LAST, live_oi desc). A name with
    real tape must outrank a known-zero even when the zero has far more OI —
    this is what kept GCT off the 08-07 slate under production OI_FLOOR. Only
    reachable in the restoring modes now.

    2026-08-12: rewritten. The old version wrapped its assertion in an `if` and
    asserted a row that never entered the restore pool, so it could not fail for
    the reason it named (review BLOCK finding 5).
    """
    # Both names are dropped and compete for ONE restore slot. ZERO fails the
    # print floor but carries 99,000 OI. PRINTED has real tape and fails the OI
    # floor. Prints must win. (Tests run at the in-code OI_FLOOR default, 200.)
    rows = [_row(f"GOOD{i}", 25, 6000) for i in range(main.TOURNEY_MIN - 1)]
    rows += [_row("ZERO", 0, 99000, rec_oi=99000),
             _row("PRINTED", 4, main.OI_FLOOR - 100, rec_oi=10)]
    out, stats = _floor(rows, mode="always")
    assert stats["n_restored"] == 1, "exactly one slot, so the key decides"
    restored = list(out[out["_print_floor_restored"] == True]["ticker"])  # noqa: E712
    assert restored == ["PRINTED"], (
        f"prints must outrank OI in the restore key, got {restored}"
    )


def test_restored_rows_carry_the_floor_they_failed():
    """The email names the floor; it can only do that if the drop records it."""
    rows = [_row("ZERO", 0, 9000), _row("THIN", 30, 10, rec_oi=10)]
    out, _ = _floor(rows, mode="empty_only")
    by_ticker = {r["ticker"]: r["_floor_failed"] for _, r in out.iterrows()}
    assert by_ticker["ZERO"] == "print"
    assert by_ticker["THIN"] == "oi"


def test_exception_fails_open_and_never_reports_measured():
    """A broken measurement must return the pool untouched — a vendor outage
    cannot be allowed to manufacture a no-pick day."""
    df = pd.DataFrame([_row("A", 25, 6000), _row("B", 25, 6000)])
    with patch.object(main, "_refresh_live_oi_batch", side_effect=RuntimeError("polygon down")):
        out, stats = main._liquidity_refresh_and_rank(df)
    assert len(out) == 2
    assert stats["measured"] is False
    assert "error" in stats


def test_kill_switch_paths_never_report_measured():
    df = pd.DataFrame([_row("A", 25, 6000)])
    with patch.object(main, "LIQUIDITY_TILT", False):
        out, stats = main._liquidity_refresh_and_rank(df)
    assert len(out) == 1 and stats["measured"] is False

    out, stats = main._liquidity_refresh_and_rank(pd.DataFrame())
    assert len(out) == 0 and stats["measured"] is False, (
        "an empty INPUT pool is the upstream gates' no-candidates case, not a "
        "liquidity no-pick day"
    )


def test_legacy_single_tier_path_is_still_bit_identical():
    """PRINT_FLOOR_ENABLED=false is the pre-2026-07-28 off-ramp: OI floor only,
    its own always-on fail-soft, and it can never return an empty slate."""
    rows = [_row(f"THIN{i}", 0, 10, rec_oi=10) for i in range(5)]
    with patch.object(main, "_refresh_live_oi_batch", side_effect=lambda d: d.copy()), \
            patch.object(main, "PRINT_FLOOR_ENABLED", False):
        out, stats = main._liquidity_refresh_and_rank(pd.DataFrame(rows))
    assert len(out) == 5, "legacy fail-soft restores the whole pool"
    assert stats["legacy_path"] is True


# -- email honesty -----------------------------------------------------------


@pytest.mark.parametrize(
    "today_volume,restored,floor_failed,expect_in,expect_not_in",
    [
        (2045, False, "", "2045 prints by ~09:52 (confirmed)", "UNVERIFIED"),
        (3, False, "", "CAUTION - thin tape", "confirmed"),
        (0, True, "print", "NO TAPE - restored by fail-soft floor", "UNVERIFIED"),
        (None, True, "oi", "UNVERIFIED - restored by fail-soft floor", "prints by"),
        (None, False, "", "UNVERIFIED - live print count unavailable", "confirmed"),
        # GAP-021: the 08-11 ALC / 08-12 MDB line. Real prints, failed the OI
        # floor, restored — it used to render "(confirmed) (restored by
        # fail-soft floor)".
        (102, True, "oi", "SUB-FLOOR - 102 prints by ~09:52 but FAILED the live-OI floor",
         "(confirmed)"),
    ],
)
def test_liquidity_email_line(today_volume, restored, floor_failed, expect_in, expect_not_in):
    row = pd.Series({
        "_today_volume": today_volume,
        "_print_floor_restored": restored,
        "_floor_failed": floor_failed,
    })
    line = main._liquidity_email_line(row)
    assert expect_in in line
    assert expect_not_in not in line


@pytest.mark.parametrize("prints", [None, 0, 1, 12, 102, 4668])
def test_a_restored_row_can_never_say_confirmed(prints):
    """GAP-021 as an invariant, not a case list: "(confirmed)" and "restored by
    fail-soft floor" in one sentence is an attestation next to its own
    refutation, and the operator traded two of them."""
    for floor_failed in ("print", "oi", ""):
        row = pd.Series({
            "_today_volume": prints,
            "_print_floor_restored": True,
            "_floor_failed": floor_failed,
        })
        assert "confirmed" not in main._liquidity_email_line(row).replace(
            "NOT confirmed", ""
        )


def test_known_zero_never_renders_as_confirmed():
    """The GCT failure mode, asserted directly: a contract with no tape today
    can never produce a '(confirmed)' liquidity line."""
    _, today_volume, _ = _fetch(GCT_SNAPSHOT)
    row = pd.Series({"_today_volume": today_volume, "_print_floor_restored": True})
    line = main._liquidity_email_line(row)
    assert "confirmed" not in line
    assert "2045" not in line


# -- the evidence gate + the no-pick interlock (review BLOCK, 2026-08-12) -----


def test_total_live_fetch_failure_does_not_manufacture_a_no_pick_day():
    """THE blocking defect. A Polygon outage does NOT raise: every future is
    individually try/excepted, so the batch completes with live_oi=None on every
    row. The print floor then drops nothing (None is UNKNOWN) and the OI floor
    would judge the whole slate on STALE frozen recommended_oi. With
    OI_FLOOR=1000 and scan-time OI far below live OI, that sweeps the slate to
    zero and reports "nothing was tradeable" when nothing was measured.
    """
    rows = [_row(f"T{i}", None, None, rec_oi=50) for i in range(12)]
    out, stats = _floor(rows)
    assert stats["measured"] is False, "a blind read must never claim it measured"
    assert stats["degraded"] == "live_fetch_unavailable"
    assert stats["n_live_ok"] == 0
    assert len(out) == 12, "degraded read must fail OPEN to the input pool"
    assert main._is_no_liquid_candidates(out, stats) is False


def test_degraded_read_does_not_judge_on_stale_frozen_oi():
    """Even when the frozen OI would leave survivors, a blind read must not be
    the thing that picks them. Fail open to the edge-rank pool untouched."""
    rows = [_row(f"T{i}", None, None, rec_oi=9000) for i in range(6)]
    rows += [_row(f"U{i}", None, None, rec_oi=5) for i in range(6)]
    out, stats = _floor(rows)
    assert len(out) == 12, "no row may be dropped on frozen OI alone"
    assert stats["measured"] is False


@pytest.mark.parametrize("n_ok,expect_measured", [(5, False), (6, True), (12, True)])
def test_live_fetch_threshold_is_a_cliff(n_ok, expect_measured):
    """LIVE_FETCH_MIN_OK_FRAC=0.5 of 12 -> at least 6 rows must answer."""
    rows = [_row(f"OK{i}", 25, 6000) for i in range(n_ok)]
    rows += [_row(f"BLIND{i}", None, None, rec_oi=9000) for i in range(12 - n_ok)]
    _, stats = _floor(rows)
    assert stats["measured"] is expect_measured
    assert stats["n_live_ok"] == n_ok


def test_no_liquid_candidates_predicate_requires_measurement():
    """Every non-measured path answers False. An empty slate from an unmeasured
    run means "we could not see", not "nothing was tradeable"."""
    empty = pd.DataFrame()
    full = pd.DataFrame([_row("A", 25, 6000)])
    assert main._is_no_liquid_candidates(empty, {"measured": True}) is True
    assert main._is_no_liquid_candidates(full, {"measured": True}) is False
    for stats in (
        {},                                                   # caller default
        {"measured": False, "error": "boom"},                 # exception path
        {"measured": False, "skipped": "LIQUIDITY_TILT=false"},
        {"measured": False, "skipped": "empty input pool"},
        {"measured": False, "degraded": "live_fetch_unavailable"},
    ):
        assert main._is_no_liquid_candidates(empty, stats) is False, stats


def test_rank_payload_carries_the_alias_and_never_the_raw_keys():
    """The incident in one assertion: the flag was computed correctly and lost
    at the /rank boundary. The alias must be ON the wire and the internal
    columns must be OFF it."""
    row = pd.Series({
        "ticker": "MDB", "direction": "BULLISH", "overnight_score": 6,
        "recommended_contract": "O:MDB260821C00470000", "recommended_oi": 197,
        "live_oi": 399, "_today_volume": 102,
        "_print_floor_restored": True, "_floor_failed": "oi",
    })
    cand = main._candidate_for_ranker(row, 1)
    assert cand["liquidity_floor_restored"] is True
    assert cand["early_volume"] == 102
    for raw in ("_today_volume", "_print_floor_restored", "_floor_failed"):
        cand.pop(raw, None)          # mirrors call_signal_ranker
    assert not (main._FORBIDDEN_LIVE_KEYS & set(cand))
    assert not [k for k in cand if k.startswith("_")], "no internal key on the wire"


def test_legacy_path_can_never_stand_the_engine_down():
    """PRINT_FLOOR_ENABLED=false sets measured=True but is safe only because its
    OWN fail-soft cannot return empty — a different invariant, and one that
    breaks at TOURNEY_MIN=0. Exclude it so "no non-measured path stands the
    engine down" holds by construction, not by a second argument."""
    assert main._is_no_liquid_candidates(
        pd.DataFrame(), {"measured": True, "legacy_path": True}
    ) is False
    with patch.object(main, "PRINT_FLOOR_ENABLED", False), \
            patch.object(main, "TOURNEY_MIN", 0), \
            patch.object(main, "_refresh_live_oi_batch", side_effect=lambda d: d.copy()):
        out, stats = main._liquidity_refresh_and_rank(
            pd.DataFrame([_row("THIN", 0, 5, rec_oi=5)])
        )
    assert main._is_no_liquid_candidates(out, stats) is False, (
        "the legacy off-ramp must never reach the no-pick branch"
    )


def test_degraded_read_is_declared_on_the_card():
    """A pick chosen with NO liquidity screen must not render a normal card.
    Without this the degraded card is byte-identical to a measured one."""
    row = pd.Series({"ticker": "AAA"})
    line = main._liquidity_email_line(
        row, {"degraded": "live_fetch_unavailable", "n_live_ok": 2, "n_total": 12}
    )
    assert "NOT MEASURED" in line
    assert "2/12" in line
    assert "SKIPPED" in line
    assert "confirmed" not in line
