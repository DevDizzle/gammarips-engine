"""TraceRecord dataclass — mirrors the profit_scout.llm_traces_v1 schema."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Optional


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


@dataclass
class TraceRecord:
    # Required identity
    service: str
    call_site: str
    run_id: str
    scan_date: date
    model_provider: str
    model_id: str
    status: str  # "ok", "parse_error", "api_error", "timeout"

    # Payload
    prompt: Optional[str] = None
    response_text: Optional[str] = None
    response_parsed: Optional[Any] = None  # dict/list — will be JSON-serialized

    # Optional metadata
    ticker: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    error: Optional[str] = None

    # For dedup / drift detection. Pass a stable string of the structured
    # inputs (e.g. f"{ticker}|{direction}|{price_change_pct}") and we hash it.
    inputs_raw: Optional[str] = None

    # Auto-filled if caller doesn't supply
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_bq_row(self) -> dict:
        """Serialize to the dict shape BigQuery insert_rows_json expects."""
        prompt_hash = _sha256(self.prompt) if self.prompt else _sha256("")
        inputs_hash = _sha256(self.inputs_raw) if self.inputs_raw else None

        parsed_json: Optional[str] = None
        if self.response_parsed is not None:
            try:
                parsed_json = json.dumps(self.response_parsed, default=str)
            except (TypeError, ValueError):
                parsed_json = None

        return {
            "trace_id": self.trace_id,
            "run_id": self.run_id,
            "service": self.service,
            "call_site": self.call_site,
            "scan_date": self.scan_date.isoformat() if isinstance(self.scan_date, date) else self.scan_date,
            "ticker": self.ticker,
            "model_provider": self.model_provider,
            "model_id": self.model_id,
            "prompt": self.prompt,
            "prompt_hash": prompt_hash,
            "response_text": self.response_text,
            "response_parsed": parsed_json,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "status": self.status,
            "error": self.error,
            "inputs_hash": inputs_hash,
            "created_at": self.created_at.isoformat(),
        }
