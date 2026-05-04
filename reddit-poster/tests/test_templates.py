"""Unit tests for templates + compliance."""
from __future__ import annotations

from app import compliance, templates


def test_render_trade_idea_fills_all_slots():
    brief = {
        "ticker": "NVDA",
        "direction": "BULLISH",
        "catalyst": "Heavy weekly call sweep into earnings.",
        "vol_oi_ratio": 3.4,
        "recommended_spread_pct": 0.062,
    }
    body = templates.render_trade_idea(brief)
    assert "$NVDA" in body
    assert "BULLISH" in body
    assert "Heavy weekly call sweep" in body
    assert "3.4x" in body
    assert "6.2%" in body
    assert "10:00 ET entry" in body
    assert "gammarips.com/track-record" in body


def test_render_pnl_receipt_includes_disclaimer():
    perf = {
        "ticker": "AAPL",
        "direction": "BEARISH",
        "entry_date": "2026-04-29",
        "exit_date": "2026-05-02",
        "realized_return_pct": 0.80,
        "exit_reason": "TARGET",
    }
    body = templates.render_pnl_receipt(perf)
    assert "Paper-trade" in body
    assert "Not advice" in body
    assert "$AAPL" in body
    assert "+80%" in body
    assert "target hit" in body


def test_compliance_rejects_ai_slop():
    body = (
        "**$XYZ — BULLISH**\n\nThis trade is a real game-changer for the "
        "options ecosystem. Catalyst: heavy call flow.\n\n"
        "10:00 ET entry day-1, -60% stop, +80% target, 3-day hold.\n\n"
        "Tracking V5.3 / Target-80 paper bracket. "
        "Full ledger at gammarips.com/track-record"
    )
    result = compliance.score(body, "trade_idea")
    assert not result.passed
    assert any("game-changer" in f for f in result.failures)
    assert any("ecosystem" in f for f in result.failures)
