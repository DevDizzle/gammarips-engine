"""Evaluator registry for gammarips-eval.

Each evaluator is a callable with the signature:

    def evaluate(trace, gt_context, config) -> EvalResult | None

Evaluators MUST be pure — no BQ writes, no mutation of the trace. Return
None to signal "not applicable to this trace" (e.g., a quality judge that
can't run because the response is JSON not prose).

To add an evaluator:
    1. Create a module under evaluators/gammarips/ or evaluators/vendored/
    2. Define an `evaluate(trace, gt_context, config)` function
    3. Import it here and add it to REGISTRY
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class EvalResult:
    score: Optional[float]  # 0.0 - 1.0, None if N/A
    details: dict = field(default_factory=dict)
    ground_truth_source: Optional[str] = None
    judge_model: Optional[str] = None


# ---- Imports ----
from .gammarips import (
    flow_intent_accuracy,
    consensus_return_agreement,
    calibration,
    report_factuality,
)
from .vendored import quality, safety, hallucination, factual


REGISTRY: dict[str, Callable[..., Optional[EvalResult]]] = {
    # GammaRips-specific
    "flow_intent_accuracy": flow_intent_accuracy.evaluate,
    "consensus_return_agreement": consensus_return_agreement.evaluate,
    "calibration": calibration.evaluate,
    "report_factuality": report_factuality.evaluate,
    # Vendored from genai-eval-framework
    "quality": quality.evaluate,
    "safety": safety.evaluate,
    "hallucination": hallucination.evaluate,
    "factual": factual.evaluate,
}


def list_evaluators() -> list[str]:
    return sorted(REGISTRY.keys())


def run_evaluator(name: str, *, trace, gt_context, config) -> Optional[EvalResult]:
    fn = REGISTRY.get(name)
    if fn is None:
        raise KeyError(f"Unknown evaluator: {name}")
    return fn(trace=trace, gt_context=gt_context, config=config)
