"""hallucination — v1 stub.

The genai-eval-framework version uses an NLI cross-encoder
(transformers + torch) which is too heavy for a Cloud Run cold start.
For v1 we ship this stub so the registry entry exists and the config wiring
works; it always returns None (not applicable), which the runner treats as
"skip, don't write a row".

To enable: add torch + transformers + sentence-transformers to
requirements.txt and port the NLI logic from
genai-eval-framework/src/evaluators/hallucination.py.
"""

from __future__ import annotations

from typing import Optional


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    return None
