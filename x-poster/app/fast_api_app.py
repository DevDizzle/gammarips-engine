# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""FastAPI app — adds a /post endpoint for Cloud Scheduler to trigger the
x-poster pipeline with a specific post_type + scan_date, bypassing the default
ADK chat surface."""

from __future__ import annotations

import os
from typing import Any, Literal, Optional

import google.auth
from fastapi import FastAPI, HTTPException
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import logging as google_cloud_logging
from google.genai import types as genai_types
from pydantic import BaseModel, Field

from app import tools
from app.agent import root_agent
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

setup_telemetry()
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=True,
)
app.title = "x-poster"
app.description = (
    "ADK multi-agent X publisher for @gammarips. "
    "POST /post with {post_type, scan_date?} to trigger the pipeline."
)


# --- Scheduler-triggered pipeline endpoint --------------------------------
class PostRequest(BaseModel):
    post_type: Literal[
        "signal", "watchlist", "standby", "report", "teaser", "callback",
        "scorecard", "pool_outcomes", "life_stats", "agent_angle"
    ] = Field(description="Which post-type handler to invoke.")
    scan_date: Optional[str] = Field(
        default=None,
        description="YYYY-MM-DD (Eastern time). Defaults to today ET if omitted.",
    )
    dry_run: bool = Field(
        default=False,
        description="Run the full pipeline but skip the actual X publish. "
        "For validating post types end-to-end on the live service.",
    )


class PostResponse(BaseModel):
    status: str
    post_type: str
    scan_date: str
    tweet_id: Optional[str] = None
    review_status: Optional[str] = None
    error: Optional[str] = None


# Post types that can reveal the PRIVATE daily tournament pick (or recap it
# per-ticker). Paused at the scheduler 2026-07-03, and hard-blocked here since
# the 2026-07-09 revamp: the service is deployed --allow-unauthenticated with
# DRY_RUN=false, so "paused" must be enforced in code, not just cron config
# (scalping-optics constraint — see docs/DECISIONS/2026-07-09-x-poster-revamp.md).
_PICK_REVEALING_POST_TYPES: frozenset[str] = frozenset({"signal", "callback", "scorecard"})
_PAUSED_TYPES_ENABLED = os.getenv("ENABLE_PAUSED_POST_TYPES", "false").lower() == "true"


@app.post("/post", response_model=PostResponse)
async def trigger_post(request: PostRequest) -> PostResponse:
    """Trigger the x-poster pipeline for one scheduled post.

    Cloud Scheduler hits this with {"post_type": "signal"} (or other types).
    Seed a fresh session with post_type + scan_date, drain the agent loop,
    return the final publish_result from session state.
    """
    if request.post_type in _PICK_REVEALING_POST_TYPES and not _PAUSED_TYPES_ENABLED:
        raise HTTPException(
            status_code=403,
            detail=(
                f"post_type '{request.post_type}' is paused: the daily pick is "
                "private (free-UI/paid-MCP model). Set ENABLE_PAUSED_POST_TYPES=true "
                "to re-enable deliberately."
            ),
        )

    scan_date = request.scan_date or tools.today_et_iso()

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="x-poster",
        user_id="scheduler",
        state={
            "post_type": request.post_type,
            "scan_date": scan_date,
            "dry_run": request.dry_run,
        },
    )
    runner = Runner(
        agent=root_agent,
        app_name="x-poster",
        session_service=session_service,
    )

    try:
        async for _event in runner.run_async(
            user_id="scheduler",
            session_id=session.id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=f"Execute {request.post_type} pipeline.")],
            ),
        ):
            pass  # drain events — state is the source of truth
    except Exception as exc:  # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
        logger.log_struct(
            {
                "event": "pipeline_error",
                "post_type": request.post_type,
                "error": str(exc),
                "traceback": tb,
            },
            severity="ERROR",
        )
        raise HTTPException(status_code=500, detail=f"pipeline_error: {exc}") from exc

    final = await session_service.get_session(
        app_name="x-poster", user_id="scheduler", session_id=session.id
    )
    publish_result_raw = final.state.get("publish_result", {}) if final else {}
    review_raw = final.state.get("review", {}) if final else {}
    publish_result: dict[str, Any] = publish_result_raw if isinstance(publish_result_raw, dict) else {}
    review: dict[str, Any] = review_raw if isinstance(review_raw, dict) else {}

    resp = PostResponse(
        status=publish_result.get("status", "unknown"),
        post_type=request.post_type,
        scan_date=scan_date,
        tweet_id=publish_result.get("tweet_id"),
        review_status=review.get("status"),
        error=publish_result.get("error"),
    )
    logger.log_struct({"event": "pipeline_complete", **resp.model_dump()}, severity="INFO")
    return resp


# --- Post-metrics collection (nightly cron; no LLM involved) ---------------
class MetricsRequest(BaseModel):
    lookback_days: int = Field(default=10, ge=1, le=30)


@app.post("/collect_metrics")
def collect_metrics(request: MetricsRequest) -> dict[str, Any]:
    """Snapshot public metrics for recent tweets into BQ `x_post_metrics`.

    Deterministic tool call — deliberately bypasses the agent pipeline.
    Fail-soft: returns the tool's status dict; never 500s on X quota errors
    so Cloud Scheduler doesn't retry-storm a rate-limited API.
    """
    result = tools.collect_x_metrics(lookback_days=request.lookback_days)
    logger.log_struct({"event": "collect_metrics", **result}, severity="INFO")
    return result


# --- Health + feedback -----------------------------------------------------
@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "service": "x-poster",
        "project": project_id,
        "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
        "handle": os.getenv("BRAND_HANDLE", "@gammarips"),
    }


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
