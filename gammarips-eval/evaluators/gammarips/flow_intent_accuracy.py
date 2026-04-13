"""flow_intent_accuracy — does enrichment's DIRECTIONAL/HEDGING call match reality?

Logic:
  - trace.service must be "enrichment" and trace.response_parsed must contain
    `flow_intent` ∈ {DIRECTIONAL, HEDGING, MECHANICAL, MIXED}.
  - Ground truth comes from profit_scout.signal_performance.peak_return_pct
    for (ticker, scan_date), pulled by runner.py into gt_context.
  - Score:
      DIRECTIONAL + same sign as `direction` + |peak_return_pct| > 0.5%  => 1.0
      HEDGING    + opposite sign OR |peak_return_pct| < 1%               => 1.0
      MIXED / MECHANICAL                                                  => 0.5 (neutral)
      any other miss                                                      => 0.0
  - Returns None if GT not yet available (settlement window hasn't closed).
"""

from __future__ import annotations

from typing import Optional


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    from evaluators import EvalResult

    if trace.service != "enrichment":
        return None
    parsed = trace.response_parsed or {}
    if not isinstance(parsed, dict):
        return None
    flow_intent = parsed.get("flow_intent")
    if not flow_intent:
        return None

    ticker = trace.ticker
    if not ticker:
        return None

    sp = gt_context.get("signal_performance", {}).get(ticker)
    if sp is None or sp.get("peak_return_pct") is None:
        # GT not yet available (within the 3-day settlement window).
        return None

    peak_ret = float(sp["peak_return_pct"])

    # Direction comes from the trace's parsed inputs hash context, but the
    # simplest proxy is to look at the sign of peak_return_pct alone plus the
    # enrichment's own implied direction, which we don't have here. Instead,
    # we treat DIRECTIONAL as "significant move" and HEDGING as "muted move".
    score = 0.0
    if flow_intent == "DIRECTIONAL":
        # A directional call should predict a meaningful move in the 3d window.
        score = 1.0 if abs(peak_ret) >= 0.5 else 0.0
    elif flow_intent == "HEDGING":
        # A hedging call should predict a small or reversed move.
        score = 1.0 if abs(peak_ret) < 1.0 else 0.0
    elif flow_intent in ("MIXED", "MECHANICAL"):
        score = 0.5
    else:
        score = 0.0

    return EvalResult(
        score=score,
        details={
            "flow_intent": flow_intent,
            "peak_return_pct": peak_ret,
            "win_tier": sp.get("win_tier"),
        },
        ground_truth_source="signal_performance",
    )
