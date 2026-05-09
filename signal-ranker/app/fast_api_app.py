"""FastAPI app — POST /rank endpoint for the V5.4 signal-ranker.

ADK reserves /run; we use /rank (per memory feedback_adk_route_reserved.md).
signal-notifier calls this inline from its 07:30 ET cron (Phase 3 wires it).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import google.auth
from fastapi import FastAPI, HTTPException
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

from app import agent
from app.app_utils.telemetry import setup_telemetry
from app.schemas import RankRequest, RankResponse

setup_telemetry()
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
gcp_logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=None,
    otel_to_cloud=True,
)
app.title = "signal-ranker"
app.description = (
    "V5.4 agent-ranker. POST /rank with candidates + report_md + ledger_summary "
    "to get one pick + runner_up + justification + confidence."
)


@app.post("/rank", response_model=RankResponse)
async def rank(request: RankRequest) -> RankResponse:
    """V5.4 ranker entrypoint.

    Caller (signal-notifier) is responsible for fetching enriched candidates,
    today's daily report, and the 14-day ledger summary, then passing them in.
    On any error: 500 with structured detail; caller fails closed (no pick today).
    """
    try:
        result = await agent.run_pipeline(request)
    except Exception as exc:  # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
        gcp_logger.log_struct(
            {
                "event": "rank_pipeline_error",
                "scan_date": request.scan_date,
                "n_candidates": len(request.candidates),
                "error": str(exc),
                "traceback": tb,
            },
            severity="ERROR",
        )
        raise HTTPException(status_code=500, detail=f"rank_failed: {exc}") from exc

    gcp_logger.log_struct(
        {
            "event": "rank_complete",
            "run_id": result.run_id,
            "scan_date": request.scan_date,
            "pick": result.pick,
            "runner_up": result.runner_up,
            "confidence": result.confidence,
            "n_candidates": len(request.candidates),
            "n_scored": len(result.scorer_outputs),
            "scorer_latency_ms": result.scorer_latency_ms,
            "picker_latency_ms": result.picker_latency_ms,
            "dry_run": result.dry_run,
        },
        severity="INFO",
    )
    return result


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "service": "signal-ranker",
        "project": project_id,
        "scorer_model": agent.SCORER_MODEL,
        "picker_model": agent.PICKER_MODEL,
        "scorer_prompt_version": agent.tools.SCORER_PROMPT_VERSION,
        "picker_prompt_version": agent.tools.PICKER_PROMPT_VERSION,
        "dry_run": agent.tools.DRY_RUN,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
