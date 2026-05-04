"""Deterministic Reddit body templates — no LLM in the hot path."""
from __future__ import annotations

from typing import Any

FOOTER = (
    "Tracking V5.3 / Target-80 paper bracket. "
    "Full ledger at gammarips.com/track-record"
)
DISCLAIMER = (
    "Paper-trade. Not advice. "
    "Past performance is not a guarantee of future results."
)

_DIRECTION_DISPLAY = {"BULLISH": "BULLISH", "BEARISH": "BEARISH"}
_EXIT_REASON_DISPLAY = {
    "TARGET": "+80% target hit",
    "STOP": "-60% stop hit",
    "TIMEOUT": "3-day timeout exit",
}


def _fmt_pct(v: Any, signed: bool = False) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "n/a"
    if abs(f) < 1.0:
        f *= 100.0
    if signed:
        return f"{'+' if f >= 0 else ''}{int(round(f))}%"
    return f"{round(f, 2)}%"


def _fmt_ratio(v: Any) -> str:
    try:
        return f"{float(v):.1f}x"
    except (TypeError, ValueError):
        return "n/a"


def render_trade_idea(brief: dict) -> str:
    """Render a Reddit trade-idea post body from a `todays_pick` doc.

    Required fields: ticker, direction, vol_oi_ratio, recommended_spread_pct.
    Optional: catalyst (1-sentence string from the brief).
    """
    ticker = (brief.get("ticker") or "").upper().lstrip("$")
    direction = _DIRECTION_DISPLAY.get(
        (brief.get("direction") or "").upper(), brief.get("direction") or ""
    )
    catalyst = (brief.get("catalyst") or "").strip()
    voi = _fmt_ratio(brief.get("vol_oi_ratio"))
    spread = _fmt_pct(brief.get("recommended_spread_pct"))

    lines = [
        f"**${ticker} — {direction}** (overnight options-flow signal)",
        "",
    ]
    if catalyst:
        lines.append(f"Catalyst: {catalyst}")
    lines.append(f"Volume/OI: {voi} | Spread: {spread}")
    lines.append("")
    lines.append(
        "This is the watchlist signal we surfaced overnight at 09:00 ET. "
        "Here's the entry/stop/target framework we're paper-trading on it: "
        "10:00 ET entry day-1, -60% option stop, +80% option target, "
        "3-day hold, exit 15:50 ET day-3. One signal per day or none."
    )
    lines.append("")
    lines.append(FOOTER)
    return "\n".join(lines).strip()


def render_pnl_receipt(perf: dict) -> str:
    """Render a Reddit pnl-receipt post body from a `signal_performance` doc."""
    ticker = (perf.get("ticker") or "").upper().lstrip("$")
    direction = _DIRECTION_DISPLAY.get(
        (perf.get("direction") or "").upper(), perf.get("direction") or ""
    )
    entry_date = perf.get("entry_date") or perf.get("scan_date") or "n/a"
    exit_date = perf.get("exit_date") or "n/a"
    ret = _fmt_pct(perf.get("realized_return_pct"), signed=True)
    reason = _EXIT_REASON_DISPLAY.get(
        (perf.get("exit_reason") or "").upper(), perf.get("exit_reason") or "exit"
    )

    lines = [
        f"**${ticker} {direction} — paper close: {ret}**",
        "",
        f"Entry: {entry_date} | Exit: {exit_date}",
        f"Outcome: {reason}",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines).strip()


def render_trade_idea_title(brief: dict) -> str:
    ticker = (brief.get("ticker") or "").upper().lstrip("$")
    direction = (brief.get("direction") or "").upper()
    return f"${ticker} {direction} — overnight options-flow signal (paper)"


def render_pnl_receipt_title(perf: dict) -> str:
    ticker = (perf.get("ticker") or "").upper().lstrip("$")
    direction = (perf.get("direction") or "").upper()
    ret = _fmt_pct(perf.get("realized_return_pct"), signed=True)
    return f"${ticker} {direction} paper close: {ret}"
