"""Entry-mark date validation + honest asof label (2026-08-14).

The same vendor semantics that produced GAP-018 in `_fetch_live_oi`, one
function over. `_fetch_entry_mark` fell back to the snapshot's `day.close`
without reading `day.last_updated`, so a prior session's settle could be
published as an entry-day mark. The 2026-08-07 follow-on audit scoped to
readers of `day.volume` and never looked here.

Measured on the live pick history 2026-08-14:
  * `last_trade` was absent on 32 of 32 picks — the plan does not entitle it,
    so every card has priced off `day.close`.
  * `entry_mark_asof` was therefore None on 32 of 32, and the card's label
    defaulted to the literal string "9:50 ET".
  * `entry_mark_stale` was False on 32 of 32: on the day_close path the
    staleness flag was structurally unreachable.
  * Against the engine's own 10:00 ET entry basis (`opp_entry_price`), the
    published mark missed by a median 16.2% and a mean 28.4% over 27 picks.

Pure-function tests: no live BigQuery, Firestore, Polygon or Vertex.

    .venv/bin/python -m pytest signal-notifier/tests/test_entry_mark.py -q
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import pytz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402

EST = pytz.timezone("America/New_York")


def _et(y, m, d, hh, mm) -> datetime:
    return EST.localize(datetime(y, m, d, hh, mm))


def _ns(dt: datetime) -> int:
    return int(dt.timestamp() * 1_000_000_000)


# The real HPE card from 2026-08-13. The published mark was $4.00 — exactly the
# 09:32 minute-bar close — while the true 10:00 ET anchor was $3.15 and the
# operator filled at $3.49. Prior session (08-12) closed at $2.09.
READ_ET = _et(2026, 8, 13, 9, 52)
TODAY_BAR_NS = _ns(_et(2026, 8, 13, 9, 37))
PRIOR_BAR_NS = _ns(_et(2026, 8, 12, 16, 0))


def _snapshot(day: dict | None, last_trade: dict | None = None) -> dict:
    res: dict = {}
    if day is not None:
        res["day"] = day
    if last_trade is not None:
        res["last_trade"] = last_trade
    return {"results": res}


def _resp(body: dict) -> MagicMock:
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    return m


def _fetch(body: dict, read_dt=READ_ET) -> dict:
    with patch.object(main, "POLYGON_API_KEY", "test-key"), \
            patch.object(main.requests, "get", return_value=_resp(body)):
        return main._fetch_entry_mark("HPE", "O:HPE260821C00060000", read_dt_et=read_dt)


# --------------------------------------------------------------- day bar ---

def test_todays_day_bar_is_served_with_its_real_timestamp():
    """A bar dated today passes through AND stops claiming a time it never had."""
    out = _fetch(_snapshot({"close": 4.00, "last_updated": TODAY_BAR_NS}))
    assert out["price"] == 4.00
    assert out["source"] == "day_close"
    assert out["asof_iso"] is not None
    # The label the card renders must be the bar's own 09:37, not a constant.
    assert datetime.fromisoformat(out["asof_iso"]).astimezone(EST).strftime("%H:%M") == "09:37"


def test_prior_session_close_is_refused_outright():
    """The GAP-018 defect class: yesterday's settle must never become a mark.

    A wrong mark is worse than no mark — limit, do-not-chase, target and stop
    are all derived from it and the operator places orders against them.
    """
    out = _fetch(_snapshot({"close": 2.09, "last_updated": PRIOR_BAR_NS}))
    assert out["price"] is None
    assert out["source"] == "stale_day_bar"
    assert out["status"] == "ok"


def test_undatable_bar_serves_the_price_but_never_claims_freshness():
    """Fail-open on the value (same as the print floor), fail-closed on the claim."""
    out = _fetch(_snapshot({"close": 4.00}))
    assert out["price"] == 4.00
    assert out["asof_iso"] is None
    assert out["stale"] is True, "an unverifiable age must render as (stale), not as fresh"


def test_stale_flag_is_reachable_on_the_day_close_path():
    """Regression: before 2026-08-14 `stale` was False on this path by construction."""
    old = _ns(_et(2026, 8, 13, 8, 0))  # ~2h before the read, past ENTRY_MARK_STALE_SECS
    out = _fetch(_snapshot({"close": 4.00, "last_updated": old}))
    assert out["source"] == "day_close"
    assert out["stale"] is True


def test_missing_day_close_is_unavailable_not_a_fabricated_zero():
    out = _fetch(_snapshot({"last_updated": TODAY_BAR_NS}))
    assert out["price"] is None
    assert out["source"] == "unavailable"


# ------------------------------------------------------------ last trade ---

def test_last_trade_still_wins_when_the_plan_ever_entitles_it():
    """Dead in production today (0 of 32 picks), kept for the entitlement."""
    lt_ns = _ns(_et(2026, 8, 13, 9, 51))
    out = _fetch(_snapshot(
        {"close": 4.00, "last_updated": PRIOR_BAR_NS},
        last_trade={"price": 3.20, "sip_timestamp": lt_ns},
    ))
    assert out["price"] == 3.20
    assert out["source"] == "last_trade"
    # A stale DAY bar must not poison a good last-trade read.
    assert out["stale"] is False


# ----------------------------------------------------------- card label ----

def test_card_label_never_hardcodes_a_time():
    """`_entry_display_strings` used to default asof_label to the literal '9:50 ET'."""
    eds = main._entry_display_strings({
        "entry_mark": 4.00, "entry_mark_asof": None,
        "entry_mark_source": "day_close", "entry_mark_stale": True,
        "limit_entry_price": 4.10, "do_not_chase_above": 4.30,
        "display_target_price": 5.60, "display_stop_price": 2.80,
    })
    assert "9:50" not in eds["asof_label"]
    assert eds["asof_label"] == "time unknown"
    assert eds["stale"] is True


def test_card_label_renders_the_measured_time_when_known():
    eds = main._entry_display_strings({
        "entry_mark": 4.00,
        "entry_mark_asof": datetime.fromtimestamp(TODAY_BAR_NS / 1e9, tz=pytz.UTC).isoformat(),
        "entry_mark_source": "day_close", "entry_mark_stale": False,
        "limit_entry_price": 4.10, "do_not_chase_above": 4.30,
        "display_target_price": 5.60, "display_stop_price": 2.80,
    })
    assert eds["asof_label"] == "09:37 ET"


def test_refused_mark_yields_no_bracket_at_all():
    """No mark => no limit, no chase cap, no target, no stop. Nothing to place."""
    assert main._entry_display_strings({
        "entry_mark": None, "entry_mark_source": "stale_day_bar",
    }) is None


# ------------------------------------------------- refusal must be VISIBLE ---
# gammarips-review 2026-08-14, BLOCKING B1. With no usable mark the card falls
# back to `recommended_mid_price`, the OVERNIGHT scan mark — the exact number
# this feature exists to escape. A silent fallback renders a normal-looking
# card, so the refusal that protects the operator becomes invisible.

@pytest.mark.parametrize("source,fragment", [
    ("stale_day_bar", "PRIOR-SESSION day bar"),
    ("stale_last_trade", "PRIOR SESSION"),
    ("unavailable", "no live price came back"),
])
def test_refusal_note_names_the_reason(source, fragment):
    note = main._entry_mark_refusal_note({"entry_mark": None, "entry_mark_source": source})
    assert "OVERNIGHT scan mark" in note
    assert fragment in note
    assert "REFUSED" in note


def test_refusal_note_is_empty_when_a_mark_exists():
    assert main._entry_mark_refusal_note({"entry_mark": 4.00,
                                          "entry_mark_source": "day_close"}) == ""
    assert main._entry_mark_refusal_note(None) == ""


def test_unknown_source_still_produces_a_caveat():
    """A future enum value must never render as a silent clean fallback."""
    note = main._entry_mark_refusal_note({"entry_mark": None,
                                          "entry_mark_source": "something_new"})
    assert "OVERNIGHT scan mark" in note


# ------------------------------------------------------- max-age bound (B2) ---

def test_undatable_unit_change_does_not_refuse_everything():
    """A ns->ms vendor change parses every bar to 1970.

    Refusing on that would silently drop EVERY card to the overnight mark, so
    an out-of-range date must be UNDATABLE (serve + flag), not "prior session".
    """
    out = _fetch(_snapshot({"close": 4.00, "last_updated": 1}))  # epoch ~1970
    assert out["price"] == 4.00, "a unit change must not refuse 100% of marks"
    assert out["source"] == "day_close"
    assert out["stale"] is True


def test_bar_dated_in_the_future_is_undatable_not_trusted():
    future = _ns(_et(2026, 9, 30, 10, 0))
    out = _fetch(_snapshot({"close": 4.00, "last_updated": future}))
    assert out["price"] == 4.00
    assert out["stale"] is True


def test_yesterdays_bar_is_still_refused_inside_the_age_window():
    """The bound must not weaken the refusal it guards."""
    out = _fetch(_snapshot({"close": 2.09, "last_updated": PRIOR_BAR_NS}))
    assert out["source"] == "stale_day_bar"
    assert out["stale"] is True, "the stalest possible read must never read fresh"


# ------------------------------------------- last_trade parity (non-blocking 3) ---

# ------------------------------------------------- WIRING regression (B1) ---
# gammarips-review, second pass, follow-up 1. The tests above exercise
# `_entry_mark_refusal_note` in isolation, so deleting its CALL SITE leaves them
# all green. B1 was a WIRING defect: the helper existed nowhere near the place
# the wrong conclusion is drawn. These two tests fail if the wiring is removed.

def _row() -> pd.Series:
    return pd.Series({
        "ticker": "HPE", "direction": "BULLISH",
        "recommended_contract": "O:HPE260821C00060000",
        "recommended_strike": 60.0, "recommended_dte": 8,
        "recommended_mid_price": 2.09, "vol_oi_ratio": 0.3823,
        "moneyness_pct": 0.0206, "overnight_score": 7,
    })


REFUSED = {"entry_mark": None, "entry_mark_source": "stale_day_bar",
           "entry_mark_stale": True, "limit_entry_price": None,
           "do_not_chase_above": None, "display_target_price": None,
           "display_stop_price": None}


def test_email_card_declares_a_refused_mark_next_to_the_overnight_number():
    html = main.format_email_html(_row(), date(2026, 8, 12), date(2026, 8, 13),
                                  entry_disp=REFUSED)
    assert "REFUSED" in html, "the card must not present the overnight mid silently"
    assert "OVERNIGHT scan mark" in html
    # The stale number it fell back to is still on the card, which is exactly
    # why the caveat has to sit beside it.
    assert "2.09" in html


def test_plaintext_card_declares_a_refused_mark_too():
    msg = main.format_whatsapp_message(_row(), date(2026, 8, 12), date(2026, 8, 13),
                                       has_pick=True, entry_disp=REFUSED)
    assert "REFUSED" in msg


def test_a_good_mark_prints_no_refusal_note_anywhere():
    good = {"entry_mark": 4.00, "entry_mark_asof": None,
            "entry_mark_source": "day_close", "entry_mark_stale": False,
            "limit_entry_price": 4.10, "do_not_chase_above": 4.30,
            "display_target_price": 5.60, "display_stop_price": 2.80}
    html = main.format_email_html(_row(), date(2026, 8, 12), date(2026, 8, 13),
                                  entry_disp=good)
    assert "REFUSED" not in html
    assert "Limit BUY" in html


def test_prior_session_last_trade_is_refused_too():
    """Otherwise the entitlement landing re-opens the hole we just closed."""
    old_ns = _ns(_et(2026, 8, 12, 15, 59))
    out = _fetch(_snapshot({"close": 4.00, "last_updated": TODAY_BAR_NS},
                           last_trade={"price": 2.11, "sip_timestamp": old_ns}))
    assert out["price"] is None
    assert out["source"] == "stale_last_trade"
    assert out["stale"] is True


# ------------------------------------------------------------ fail-soft ----

@pytest.mark.parametrize("body", [{}, {"results": {}}, {"results": None}])
def test_empty_payloads_never_raise(body):
    out = _fetch(body)
    assert out["price"] is None
    assert out["source"] == "unavailable"
