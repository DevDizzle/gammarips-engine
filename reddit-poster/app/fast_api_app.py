"""FastAPI app — POST /post for trade_idea / pnl_receipt only."""
from __future__ import annotations

import os
import time
from typing import Any, Literal, Optional

from fastapi import FastAPI, HTTPException
from google.cloud import logging as google_cloud_logging
from pydantic import BaseModel, Field

from app import compliance, templates, tools

logging_client = google_cloud_logging.Client()
logger = logging_client.logger("reddit-poster")

app = FastAPI(
    title="reddit-poster",
    description="Minimal Reddit auto-poster for trade ideas + pnl receipts.",
)


class PostRequest(BaseModel):
    post_type: Literal["trade_idea", "pnl_receipt"] = Field(
        description="Only trade_idea or pnl_receipt are accepted."
    )
    scan_date: Optional[str] = Field(default=None, description="YYYY-MM-DD ET.")
    subreddit: Optional[str] = Field(
        default=None, description="Override the round-robin subreddit pick."
    )
    dry_run: Optional[bool] = Field(
        default=None,
        description="Override DRY_RUN env var for this call. None = use env.",
    )


class PostResponse(BaseModel):
    status: str
    post_type: str
    scan_date: str
    subreddit: Optional[str] = None
    reddit_url: Optional[str] = None
    reddit_id: Optional[str] = None
    draft_uri: Optional[str] = None
    reason: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "service": "reddit-poster",
        "project": os.getenv("PROJECT_ID", "profitscout-fida8"),
        "dry_run": os.getenv("DRY_RUN", "true").lower() == "true",
        "default_subreddits": list(tools.DEFAULT_SUBREDDITS),
    }


@app.post("/post", response_model=PostResponse)
def trigger_post(request: PostRequest) -> PostResponse:
    t0 = time.time()
    scan_date = request.scan_date or tools.today_et_iso()
    dry_run = (
        request.dry_run
        if request.dry_run is not None
        else os.getenv("DRY_RUN", "true").lower() == "true"
    )

    # 1. Source data
    if request.post_type == "trade_idea":
        brief = tools.fetch_todays_pick(scan_date)
        if not brief or not brief.get("has_pick"):
            return _skip(scan_date, request.post_type, None, "no_pick_today", t0, dry_run)
        title = templates.render_trade_idea_title(brief)
        body = templates.render_trade_idea(brief)
    else:
        perf = tools.fetch_recent_close()
        if not perf:
            return _skip(scan_date, request.post_type, None, "no_close_today", t0, dry_run)
        title = templates.render_pnl_receipt_title(perf)
        body = templates.render_pnl_receipt(perf)

    # 2. Subreddit selection
    subreddit = tools.pick_subreddit(request.post_type, request.subreddit)

    # 3. Idempotency
    if tools.already_posted(scan_date, request.post_type, subreddit):
        return _skip(scan_date, request.post_type, subreddit, "already_posted", t0, dry_run)

    # 4. Compliance
    rubric = compliance.score(body, request.post_type)
    if not rubric.passed:
        _log("post_attempt", request.post_type, subreddit, "rejected", dry_run, t0,
             extra={"failures": rubric.failures, "char_count": rubric.char_count})
        raise HTTPException(
            status_code=422,
            detail={"status": "rejected", "failures": rubric.failures,
                    "char_count": rubric.char_count, "char_budget": list(rubric.char_budget)},
        )

    tools.mark_pending(scan_date, request.post_type, subreddit, body, title)

    # 5. Publish (or write draft)
    if dry_run:
        draft_uri = tools.write_draft(scan_date, request.post_type, subreddit, title, body)
        tools.mark_skipped(scan_date, request.post_type, subreddit, "dry_run")
        tools.record_subreddit_state(request.post_type, subreddit)
        _log("post_attempt", request.post_type, subreddit, "dry_run", dry_run, t0,
             extra={"draft_uri": draft_uri})
        return PostResponse(
            status="dry_run",
            post_type=request.post_type,
            scan_date=scan_date,
            subreddit=subreddit,
            draft_uri=draft_uri,
        )

    client = tools.reddit_client()
    if client is None:
        _log("post_attempt", request.post_type, subreddit, "error", dry_run, t0,
             extra={"error": "reddit_creds_missing"})
        raise HTTPException(status_code=500, detail="reddit_creds_missing")

    try:
        submission = tools.submit_post(client, subreddit, title, body)
    except Exception as exc:  # noqa: BLE001
        _log("post_attempt", request.post_type, subreddit, "error", dry_run, t0,
             extra={"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"reddit_submit_error: {exc}") from exc

    tools.mark_posted(
        scan_date, request.post_type, subreddit,
        submission["reddit_url"], submission["reddit_id"],
    )
    tools.record_subreddit_state(request.post_type, subreddit)
    _log("post_attempt", request.post_type, subreddit, "posted", dry_run, t0,
         extra={"reddit_url": submission["reddit_url"]})
    return PostResponse(
        status="posted",
        post_type=request.post_type,
        scan_date=scan_date,
        subreddit=subreddit,
        reddit_url=submission["reddit_url"],
        reddit_id=submission["reddit_id"],
    )


# --- helpers --------------------------------------------------------------

def _skip(scan_date: str, post_type: str, subreddit: str | None, reason: str,
          t0: float, dry_run: bool) -> PostResponse:
    _log("post_attempt", post_type, subreddit, "skipped", dry_run, t0,
         extra={"reason": reason})
    return PostResponse(
        status="skipped", post_type=post_type, scan_date=scan_date,
        subreddit=subreddit, reason=reason,
    )


def _log(event: str, post_type: str, subreddit: str | None, status: str,
         dry_run: bool, t0: float, extra: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {
        "event": event,
        "post_type": post_type,
        "subreddit": subreddit,
        "status": status,
        "dry_run": dry_run,
        "latency_ms": int((time.time() - t0) * 1000),
    }
    if extra:
        payload.update(extra)
    severity = "ERROR" if status == "error" else "INFO"
    logger.log_struct(payload, severity=severity)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
