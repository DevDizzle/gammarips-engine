"""calibration — per-trace calibration proxy.

Trace-level single-point calibration isn't meaningful on its own (ECE needs
a binned population), so for v1 this evaluator emits a "signed miss" score
per trace. The weekly report aggregates these into a reliability diagram.

Logic:
  - For enrichment traces: score field = catalyst_score (0.0-1.0). Outcome =
    normalized abs(peak_return_pct) clipped to [0,1].
  - For agent_arena round4_final traces: score field = pick's conviction /
    10.0 (conviction lives on [1,10]). Outcome = 1.0 if direction correct
    else 0.0.
  - Score = 1 - |predicted - outcome| (higher is better).
  - Returns None when GT not yet available.
"""

from __future__ import annotations

from typing import Optional


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    from evaluators import EvalResult

    parsed = trace.response_parsed
    sp_map = gt_context.get("signal_performance", {})

    if trace.service == "enrichment":
        if not isinstance(parsed, dict):
            return None
        predicted = parsed.get("catalyst_score")
        if predicted is None:
            return None
        predicted = _clip01(float(predicted))
        sp = sp_map.get(trace.ticker or "")
        if sp is None or sp.get("peak_return_pct") is None:
            return None
        outcome = _clip01(abs(float(sp["peak_return_pct"])) / 5.0)  # 5% ~= full confidence
        score = 1.0 - abs(predicted - outcome)
        return EvalResult(
            score=score,
            details={"predicted": predicted, "outcome": outcome, "field": "catalyst_score"},
            ground_truth_source="signal_performance",
        )

    if trace.service == "agent_arena" and trace.call_site.startswith("round4_final"):
        if not isinstance(parsed, list) or not parsed:
            return None
        # Take the top-conviction pick as the trace-level representative.
        top = max(
            (p for p in parsed if isinstance(p, dict) and p.get("ticker")),
            key=lambda p: float(p.get("conviction", 0) or 0),
            default=None,
        )
        if top is None:
            return None
        predicted = _clip01(float(top.get("conviction", 0) or 0) / 10.0)
        ticker = top.get("ticker")
        direction = (top.get("direction") or "").upper()
        sp = sp_map.get(ticker)
        if sp is None or sp.get("peak_return_pct") is None:
            return None
        peak = float(sp["peak_return_pct"])
        if abs(peak) < 0.5:
            outcome = 0.5
        else:
            outcome = 1.0 if (
                (direction == "BULLISH" and peak > 0)
                or (direction == "BEARISH" and peak < 0)
            ) else 0.0
        score = 1.0 - abs(predicted - outcome)
        return EvalResult(
            score=score,
            details={
                "predicted": predicted,
                "outcome": outcome,
                "ticker": ticker,
                "direction": direction,
                "peak_return_pct": peak,
                "field": "conviction",
            },
            ground_truth_source="signal_performance",
        )

    return None
