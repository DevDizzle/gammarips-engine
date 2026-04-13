"""report_factuality — LLM-as-judge for the overnight report.

Sends the daily report's headline + content plus the day's actual ticker
outcomes (from signal_performance) to Gemini 3 Flash with a short rubric:
does the report's stated stance align with what the market actually did?

v1 simplification: we judge only the stated stance direction (bullish-lean
vs bearish-lean vs mixed) against the breadth of positive vs negative
peak_return_pct outcomes. This is deliberately coarse — the evaluator
exists to detect obvious factual misalignment, not to grade prose quality
(that's what `quality` does).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_JUDGE_PROMPT_TEMPLATE = """You are a trading report factuality judge. Given a
daily overnight report and the actual market outcomes that followed, score
whether the report's stated stance aligned with reality.

REPORT:
Title: {title}
Headline: {headline}
Content (first 2000 chars): {content_snippet}

ACTUAL OUTCOMES (peak_return_pct over 3-day window per ticker):
{outcomes_json}

Score the report on a 0.0-1.0 scale:
  1.0 — stated stance clearly matched the breadth of outcomes
  0.5 — mixed or neutral
  0.0 — stated stance clearly contradicted the outcomes

Respond with ONLY valid JSON of the form:
{{"score": <float 0-1>, "reason": "<one sentence>"}}"""


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    from evaluators import EvalResult

    if trace.service != "report_generator":
        return None
    parsed = trace.response_parsed
    if not isinstance(parsed, dict):
        return None

    title = parsed.get("title", "")
    headline = parsed.get("headline", "")
    content = parsed.get("content", "")
    if not (title or headline or content):
        return None

    sp_map = gt_context.get("signal_performance", {})
    if not sp_map:
        return None

    outcomes = {
        t: round(float(r.get("peak_return_pct", 0.0) or 0.0), 3)
        for t, r in sp_map.items()
        if r.get("peak_return_pct") is not None
    }
    if not outcomes:
        return None

    # Cost-budget guard: skip if the per-run judge-call cap is exhausted.
    budget = gt_context.get("budget")
    if budget is not None:
        if budget.get("used", 0) >= budget.get("max", 0):
            budget["exhausted"] = True
            return None

    judge_model = config.get("judge_model", "gemini-3-flash-preview")
    project_id = os.environ.get("PROJECT_ID", "profitscout-fida8")

    try:
        from google import genai
        from google.genai import types as gtypes

        client = genai.Client(vertexai=True, project=project_id, location="global")
        prompt = _JUDGE_PROMPT_TEMPLATE.format(
            title=title,
            headline=headline,
            content_snippet=(content or "")[:2000],
            outcomes_json=json.dumps(outcomes, indent=2),
        )
        resp = client.models.generate_content(
            model=judge_model,
            contents=prompt,
            config=gtypes.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
            ),
        )
        text = resp.text or "{}"
        data = json.loads(text)
        if budget is not None:
            budget["used"] = budget.get("used", 0) + 1
        score = float(data.get("score", 0.5))
        reason = data.get("reason", "")
    except Exception as e:  # noqa: BLE001
        logger.warning("report_factuality judge failed: %s", e)
        return None

    return EvalResult(
        score=max(0.0, min(1.0, score)),
        details={"reason": reason, "n_outcomes": len(outcomes)},
        ground_truth_source="signal_performance",
        judge_model=judge_model,
    )
