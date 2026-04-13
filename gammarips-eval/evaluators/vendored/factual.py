"""factual — v1 stub.

The genai-eval-framework version extracts claims and verifies them via
embeddings. For v1 we ship the stub so the registry entry exists. Full
port is deferred until the trace volume justifies the judge cost.

To enable: port
genai-eval-framework/src/evaluators/factual.py and add
sentence-transformers to requirements.txt.
"""

from __future__ import annotations

from typing import Optional


def evaluate(*, trace, gt_context, config) -> Optional[object]:
    return None
