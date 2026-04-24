# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""FastAPI app — adds a /run endpoint for Cloud Scheduler to trigger the
blog-generator pipeline. Optional slug for manual retry; optional dry_run for
preview."""

from __future__ import annotations

import os
from typing import Any, Optional

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
app.title = "blog-generator"
app.description = (
    "ADK multi-agent blog publisher for gammarips.com. "
    "POST /run with {slug?, dry_run?} to trigger the pipeline."
)


# --- Scheduler-triggered pipeline endpoint --------------------------------
class RunRequest(BaseModel):
    slug: Optional[str] = Field(
        default=None,
        description=(
            "Target a specific slug in blog_schedule/current (manual retry). "
            "If omitted, planner picks the next row with status=='pending'."
        ),
    )
    dry_run: bool = Field(
        default=False,
        description=(
            "If True, run the full pipeline but skip Firestore write. "
            "Returns the generated markdown in the response."
        ),
    )


class RunResponse(BaseModel):
    status: str
    slug: Optional[str] = None
    iterations: Optional[int] = None
    reviewer_score: Optional[float] = None
    reviewer_notes: Optional[str] = None
    markdown: Optional[str] = None
    error: Optional[str] = None


@app.post("/run", response_model=RunResponse)
async def trigger_run(request: RunRequest) -> RunResponse:
    """Trigger the blog-generator pipeline for one scheduled post.

    Cloud Scheduler hits this with empty body weekly. Manual retries pass
    {"slug": "..."}. Dry-run previews pass {"dry_run": true}.
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="blog_generator",
        user_id="scheduler",
        state={
            "slug": request.slug or "",
            "dry_run": request.dry_run,
        },
    )
    runner = Runner(
        agent=root_agent,
        app_name="blog_generator",
        session_service=session_service,
    )

    try:
        trigger_text = (
            f"Draft the blog post for slug {request.slug!r}."
            if request.slug
            else "Draft the next pending blog post from the schedule."
        )
        async for _event in runner.run_async(
            user_id="scheduler",
            session_id=session.id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=trigger_text)],
            ),
        ):
            pass  # drain events — state is the source of truth
    except Exception as exc:  # noqa: BLE001
        logger.log_struct(
            {"event": "pipeline_error", "slug": request.slug, "error": str(exc)},
            severity="ERROR",
        )
        raise HTTPException(status_code=500, detail=f"pipeline_error: {exc}") from exc

    final = await session_service.get_session(
        app_name="blog_generator", user_id="scheduler", session_id=session.id
    )
    publish_result: dict[str, Any] = final.state.get("publish_result", {}) if final else {}
    status = publish_result.get("status", "unknown")

    resp = RunResponse(
        status=status,
        slug=publish_result.get("slug"),
        iterations=publish_result.get("iterations"),
        reviewer_score=publish_result.get("reviewer_score"),
        reviewer_notes=publish_result.get("reviewer_notes"),
        # On dry_run or reject we surface the markdown; on published we do not.
        markdown=publish_result.get("markdown") if status in ("dry_run", "rejected") else None,
        error=publish_result.get("error"),
    )
    logger.log_struct(
        {"event": "pipeline_complete", "status": status, "slug": resp.slug,
         "iterations": resp.iterations},
        severity="INFO" if status in ("published", "dry_run") else "WARNING",
    )
    # Fail loud on reject per DESIGN_SPEC §Example Use Cases 4.
    if status == "rejected":
        raise HTTPException(status_code=500, detail=resp.model_dump())
    return resp


# --- Health + feedback -----------------------------------------------------
@app.get("/health")
def health() -> dict[str, Any]:
    # Light-touch probe — no Firestore reads to keep latency low.
    return {
        "service": "blog-generator",
        "project": project_id,
        "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
        "today_et": tools.today_et_iso(),
    }


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
