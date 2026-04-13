"""GammaRips shared LLM trace logger.

Usage (all services):

    from trace_logger import TraceLogger, TraceRecord

    _tl = TraceLogger()  # singleton per process; cheap

    # ... call your LLM ...

    _tl.log(TraceRecord(
        service="enrichment",
        call_site="fetch_and_analyze_news",
        run_id=run_id,
        scan_date=scan_date,
        ticker=ticker,
        model_provider="vertex_gemini",
        model_id="gemini-3-flash",
        prompt=prompt,
        response_text=response.text,
        response_parsed=parsed,
        input_tokens=usage.prompt_token_count,
        output_tokens=usage.candidates_token_count,
        latency_ms=elapsed_ms,
        status="ok",
    ))

The logger is fire-and-forget: exceptions are swallowed and logged at WARNING
but NEVER raised to the caller. Trading must not break because eval broke.
"""

from .records import TraceRecord
from .logger import TraceLogger

__all__ = ["TraceRecord", "TraceLogger"]
