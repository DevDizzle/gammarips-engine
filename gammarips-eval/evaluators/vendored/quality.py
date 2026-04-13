"""quality — LLM-as-judge quality evaluator.

Adapted from genai-eval-framework src/evaluators/quality.py.
Scores response coherence / fluency / relevance on a 1-5 scale via Gemini,
then normalizes to 0.0-1.0. Skips traces whose response is constrained JSON
(those don't benefit from prose quality evaluation).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_PROMPT = """You are a quality evaluator for AI-generated text. Score the
following response on three dimensions, each 1 (worst) to 5 (best):

  - coherence: is it logically consistent and easy to follow?
  - fluency:   is the grammar and phrasing natural?
  - relevance: does it directly address the prompt?

PROMPT:
{prompt_snippet}

RESPONSE:
{response_snippet}

Respond with ONLY valid JSON of the form:
{{"coherence": <int 1-5>, "fluency": <int 1-5>, "relevance": <int 1-5>, "reason": "<one sentence>"}}"""


def _has_prose(text: Optional[str]) -> bool:
    if not text:
        return False
    t = text.strip()
    if not t:
        return False
    # If it starts with { or [, it's JSON — skip.
    if t[0] in "{[":
        return False
    return len(t) >= 80  # arbitrary floor; don't waste judge calls on nothing


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    from evaluators import EvalResult

    # Prose-heavy services only.
    if trace.service not in ("agent_arena", "report_generator"):
        return None

    response_text = trace.response_text
    if not _has_prose(response_text):
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
        prompt = _PROMPT.format(
            prompt_snippet=(trace.prompt or "")[:1500],
            response_snippet=(response_text or "")[:2000],
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
        coh = int(data.get("coherence", 3))
        flu = int(data.get("fluency", 3))
        rel = int(data.get("relevance", 3))
        reason = data.get("reason", "")
    except Exception as e:  # noqa: BLE001
        logger.warning("quality judge failed: %s", e)
        return None

    avg = (coh + flu + rel) / 3.0
    score = (avg - 1.0) / 4.0  # 1..5 -> 0..1

    return EvalResult(
        score=max(0.0, min(1.0, score)),
        details={
            "coherence": coh,
            "fluency": flu,
            "relevance": rel,
            "reason": reason,
        },
        judge_model=judge_model,
    )
