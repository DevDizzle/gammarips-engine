"""consensus_return_agreement — does agent-arena's final pick track realized return?

Logic:
  - Only scores round4_final traces where response_parsed contains at least
    one pick with a ticker + direction.
  - For each picked ticker, pull peak_return_pct from signal_performance.
  - Score = fraction of picks whose direction matched the realized move sign
    (BULLISH + peak > 0) or (BEARISH + peak < 0). If magnitude < 0.5% we
    treat it as no-call (half credit) to avoid punishing noise.
  - Returns None if no picks have ground truth yet.
"""

from __future__ import annotations

from typing import Optional


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    from evaluators import EvalResult

    if trace.service != "agent_arena":
        return None
    if not trace.call_site.startswith("round4_final"):
        return None

    parsed = trace.response_parsed
    if not parsed or not isinstance(parsed, list):
        return None

    sp_map = gt_context.get("signal_performance", {})
    hits = 0
    graded = 0
    per_pick_details = []

    for pick in parsed:
        if not isinstance(pick, dict):
            continue
        ticker = pick.get("ticker")
        direction = (pick.get("direction") or "").upper()
        if not ticker or direction not in ("BULLISH", "BEARISH"):
            continue
        sp = sp_map.get(ticker)
        if sp is None or sp.get("peak_return_pct") is None:
            continue

        peak = float(sp["peak_return_pct"])
        if abs(peak) < 0.5:
            score = 0.5  # noise — half credit
        else:
            correct = (direction == "BULLISH" and peak > 0) or (
                direction == "BEARISH" and peak < 0
            )
            score = 1.0 if correct else 0.0

        hits += score
        graded += 1
        per_pick_details.append({
            "ticker": ticker,
            "direction": direction,
            "peak_return_pct": peak,
            "score": score,
        })

    if graded == 0:
        return None

    return EvalResult(
        score=hits / graded,
        details={"picks": per_pick_details, "graded": graded},
        ground_truth_source="signal_performance",
    )
