"""Deterministic Reddit body templates — no LLM in the hot path.

Distraction-frame voice: trades on entry, receipts on close. Short. No
literature, no methodology walk-through, no promotional footers. See
`feedback_reddit_short_distraction.md` for the rule and rationale.
"""
from __future__ import annotations

from typing import Any

DISCLAIMER = (
    "Paper-trade. Not advice. "
    "Past performance does not guarantee future results."
)

_DIRECTION_LOWER = {"BULLISH": "bullish", "BEARISH": "bearish"}
_EXIT_REASON_DISPLAY = {
    "TARGET": "+80% target hit",
    "STOP": "-60% stop hit",
    "TIMEOUT": "3-day timeout exit",
}


def _fmt_signed_pct(v: Any) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "n/a"
    if abs(f) < 1.0:
        f *= 100.0
    return f"{'+' if f >= 0 else ''}{int(round(f))}%"


def _ticker(brief: dict) -> str:
    return (brief.get("ticker") or "").upper().lstrip("$")


def _direction_lower(brief: dict) -> str:
    return _DIRECTION_LOWER.get((brief.get("direction") or "").upper(), "")


def render_trade_idea(brief: dict) -> str:
    """Anchor post on entry day. Names the ticker + bracket, promises the
    receipt. No methodology, no citations, no contract details — that's the
    paid-side value. Mirrors the X Path B anchor philosophy."""
    ticker = _ticker(brief)
    direction = _direction_lower(brief)
    return (
        f"Overnight options-flow scan flagged ${ticker} {direction} today.\n"
        f"\n"
        f"Paper-trade entry at 10:00 ET. Bracket: -60% stop / +80% target / "
        f"3-day hold.\n"
        f"\n"
        f"Receipt going up when it closes in 3 trading days, win or lose.\n"
        f"\n"
        f"Full ledger at gammarips.com."
    )


def render_trade_idea_title(brief: dict) -> str:
    ticker = _ticker(brief)
    direction = _direction_lower(brief)
    return f"Paper-trading ${ticker} {direction} today — V5.3 setup, receipt on close"


def render_pnl_receipt(perf: dict) -> str:
    """Receipt post on close. Entry / exit / outcome / cohort tally /
    disclaimer. Cohort tally needs `wins_so_far` + `closed_so_far` populated
    by the orchestrator (see `fetch_recent_close` in tools.py)."""
    entry_date = perf.get("entry_date") or perf.get("scan_date") or "n/a"
    exit_date = perf.get("exit_date") or "n/a"
    reason = _EXIT_REASON_DISPLAY.get(
        (perf.get("exit_reason") or "").upper(),
        perf.get("exit_reason") or "exit",
    )
    wins = perf.get("wins_so_far")
    closed = perf.get("closed_so_far")
    tally_line = ""
    if wins is not None and closed is not None and int(closed) > 0:
        tally_line = f"V5.3 cohort so far: {int(wins)}/{int(closed)}.\n\n"
    return (
        f"In {entry_date} at 10:00 ET on overnight options flow.\n"
        f"Out {exit_date} on {reason}.\n"
        f"\n"
        f"{tally_line}"
        f"{DISCLAIMER}\n"
        f"\n"
        f"gammarips.com"
    )


def render_pnl_receipt_title(perf: dict) -> str:
    ticker = _ticker(perf)
    direction = _direction_lower(perf)
    ret = _fmt_signed_pct(perf.get("realized_return_pct"))
    return f"${ticker} {direction} closed {ret} — paper-trade receipt"
