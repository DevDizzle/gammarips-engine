"""gammarips-eval — FastAPI service.

Endpoints
---------
GET  /healthz        — liveness
POST /eval/batch     — pull new traces since watermark, score, write results
POST /eval/report    — aggregate eval_results for the current ISO week into
                       a markdown digest and write to Firestore eval_reports/

Both POST endpoints accept an optional JSON body:
    {"since": "2026-04-01", "limit": 100, "dry_run": false}
"""

import logging
import os
from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel

from runner import EvalRunner
from report import build_weekly_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="gammarips-eval", version="0.1.0")

PROJECT_ID = os.environ.get("PROJECT_ID", "profitscout-fida8")
DATASET = os.environ.get("DATASET", "profit_scout")

_runner = EvalRunner(project_id=PROJECT_ID, dataset=DATASET)


class BatchRequest(BaseModel):
    since: str | None = None  # ISO date; if None, use watermark
    limit: int = 500
    dry_run: bool = False
    service: str | None = None  # optional filter


class ReportRequest(BaseModel):
    iso_week: str | None = None  # e.g. "2026-W15"; if None, current week
    dry_run: bool = False


@app.get("/healthz")
def healthz():
    return {"status": "ok", "project": PROJECT_ID, "dataset": DATASET}


@app.post("/eval/batch")
def eval_batch(req: BatchRequest | None = None):
    req = req or BatchRequest()
    logger.info(
        "eval/batch since=%s limit=%s dry_run=%s service=%s",
        req.since, req.limit, req.dry_run, req.service,
    )
    summary = _runner.run_batch(
        since=req.since,
        limit=req.limit,
        dry_run=req.dry_run,
        service_filter=req.service,
    )
    return summary


@app.post("/eval/report")
def eval_report(req: ReportRequest | None = None):
    req = req or ReportRequest()
    iso_week = req.iso_week or date.today().strftime("%G-W%V")
    logger.info("eval/report iso_week=%s dry_run=%s", iso_week, req.dry_run)
    result = build_weekly_report(
        project_id=PROJECT_ID,
        dataset=DATASET,
        iso_week=iso_week,
        dry_run=req.dry_run,
    )
    return result
