"""TraceLogger — fire-and-forget BigQuery writer.

Design goals
------------
1. Never raise to the caller. Trading must not break because eval broke.
2. Cheap to construct (lazy BQ client init).
3. Honors a kill-switch env var TRACE_LOGGING_ENABLED. Default: "false".
   Services flip this to "true" once they've been instrumented and validated.
4. Supports deterministic sampling via TRACE_LOGGING_SAMPLE_RATE (0.0-1.0).
   Default: 1.0 (log everything).
"""

from __future__ import annotations

import logging
import os
import random
import threading
from typing import Optional

from .pricing import estimate_cost_usd
from .records import TraceRecord

logger = logging.getLogger(__name__)

DEFAULT_PROJECT = "profitscout-fida8"
DEFAULT_DATASET = "profit_scout"
DEFAULT_TABLE = "llm_traces_v1"


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str, default: float) -> float:
    val = os.environ.get(name)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


class TraceLogger:
    """Fire-and-forget BigQuery trace writer.

    Construct once per process. Calling .log() is non-blocking from the
    caller's perspective (synchronous BQ insert, but errors are swallowed).
    """

    _lock = threading.Lock()

    def __init__(
        self,
        project: Optional[str] = None,
        dataset: Optional[str] = None,
        table: Optional[str] = None,
    ):
        self.project = project or os.environ.get("TRACE_BQ_PROJECT", DEFAULT_PROJECT)
        self.dataset = dataset or os.environ.get("TRACE_BQ_DATASET", DEFAULT_DATASET)
        self.table = table or os.environ.get("TRACE_BQ_TABLE", DEFAULT_TABLE)
        self.table_ref = f"{self.project}.{self.dataset}.{self.table}"
        self.enabled = _env_bool("TRACE_LOGGING_ENABLED", default=False)
        self.sample_rate = max(0.0, min(1.0, _env_float("TRACE_LOGGING_SAMPLE_RATE", 1.0)))
        self._client = None  # lazy
        self._disabled_reason: Optional[str] = None

    # ----- internal -----

    def _get_client(self):
        if self._client is not None:
            return self._client
        with self._lock:
            if self._client is not None:
                return self._client
            try:
                from google.cloud import bigquery
                self._client = bigquery.Client(project=self.project)
            except Exception as e:  # noqa: BLE001 — defensive
                self._disabled_reason = f"bq client init failed: {e}"
                logger.warning("TraceLogger disabled: %s", self._disabled_reason)
                self.enabled = False
            return self._client

    # ----- public -----

    def log(self, record: TraceRecord) -> None:
        """Insert one trace row. Never raises."""
        try:
            if not self.enabled:
                return
            if self.sample_rate < 1.0 and random.random() > self.sample_rate:
                return

            # Back-fill cost if caller didn't supply it.
            if record.cost_usd is None:
                record.cost_usd = estimate_cost_usd(
                    record.model_id, record.input_tokens, record.output_tokens
                )

            client = self._get_client()
            if client is None:
                return

            row = record.to_bq_row()
            errors = client.insert_rows_json(self.table_ref, [row])
            if errors:
                logger.warning("TraceLogger BQ insert errors: %s", errors)
        except Exception as e:  # noqa: BLE001 — swallow everything
            logger.warning("TraceLogger.log swallowed exception: %s", e)
