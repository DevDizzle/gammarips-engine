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

import logging
import os
import re
from datetime import datetime
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
from app.agent import MODEL, root_agent
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback
from gammarips_content import compliance, voice_rules

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


@app.post("/generate", response_model=RunResponse)
async def trigger_run(request: RunRequest) -> RunResponse:
    """Trigger the blog-generator pipeline for one scheduled post.

    Cloud Scheduler hits this with empty body weekly. Manual retries pass
    {"slug": "..."}. Dry-run previews pass {"dry_run": true}.

    Path is `/generate` (not `/run`) because ADK's `get_fast_api_app` reserves
    `/run` for its built-in session-based interactive endpoint — registering
    a competing handler there returns 422 "missing appName/userId/sessionId".
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


# --- Newsletter endpoints (/draft_email, /blast_email) --------------------
# These are intentionally separate from the blog pipeline. The newsletter is
# a single-shot Gemini render + deterministic compliance check + GCS write +
# Mailgun send. NO LoopAgent, NO Firestore blog write — read-only against
# the blog pipeline state.
#
# Hard rules (do not relax without an Evan-approved decision note):
# 1. compliance.score_against_rubric() must hard-fail before any Mailgun
#    call. Failures => 422, no email leaves the system.
# 2. /draft_email NEVER fans out to users. It always sends to OPERATOR_EMAIL.
# 3. /blast_email requires explicit dry_run=False AND a valid `audience`
#    selector. Per-recipient send only — never BCC, never `to: [a, b, c]`.
# 4. Mailgun POSTs use timeout=10 (already enforced in tools.send_email_via_mailgun).

_py_logger = logging.getLogger(__name__)

# Drafts go to gs://EMAIL_DRAFTS_BUCKET/email/{date}_newsletter.{html,txt}.
# Bucket must be pre-created — service account does not have project-level
# storage.buckets.create. If the bucket is missing, /draft_email returns a
# 500 with an actionable hint rather than auto-creating.
EMAIL_DRAFTS_BUCKET = os.environ.get("EMAIL_DRAFTS_BUCKET", "gammarips-content-drafts").strip()

# Subject-extraction regex for /blast_email — pulls <title>...</title> from
# the rendered HTML. Falls back to a sidecar .subject.txt if present.
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class DraftEmailRequest(BaseModel):
    theme: Optional[str] = Field(
        default=None,
        description=(
            "Optional theme tag for the newsletter (e.g. 'weekly', "
            "'30-trade-callback'). Influences the Gemini prompt. "
            "Defaults to a generic weekly recap."
        ),
    )
    dry_run: bool = Field(
        default=True,
        description=(
            "Operator-preview-only by design — both True and False send to "
            "OPERATOR_EMAIL only. /draft_email NEVER fans out to users; the "
            "/blast_email endpoint is the only path to the user list."
        ),
    )


class DraftEmailResponse(BaseModel):
    status: str
    gcs_uri: Optional[str] = None
    gcs_uri_text: Optional[str] = None
    subject: Optional[str] = None
    preview_text: Optional[str] = None
    compliance_passed: Optional[bool] = None
    compliance_failures: Optional[list[str]] = None
    operator_send_status: Optional[str] = None
    error: Optional[str] = None


class BlastEmailRequest(BaseModel):
    gcs_uri: str = Field(
        description=(
            "gs://gammarips-content-drafts/email/<...>.html — the rendered "
            "newsletter to blast. Must live under the email/ prefix in the "
            "EMAIL_DRAFTS_BUCKET; other paths are rejected."
        ),
    )
    audience: Literal["all", "free", "paid"] = Field(
        default="all",
        description=(
            "Audience selector — 'all' = all non-anonymous users with email "
            "(currently 211); 'free' = 'all' minus active paid; 'paid' = "
            "active pro subscribers only."
        ),
    )
    dry_run: bool = Field(
        default=True,
        description=(
            "If True (default), send only to OPERATOR_EMAIL and return the "
            "would-be recipient count + first-3 sample for sanity check. "
            "If False, fan out per-recipient (capped at MAX_RECIPIENTS)."
        ),
    )


class BlastEmailResponse(BaseModel):
    status: str
    audience: str
    audience_count: int
    sent: int
    failed: int
    dry_run: bool
    recipient_sample: Optional[list[str]] = None
    subject: Optional[str] = None
    error: Optional[str] = None


def _render_newsletter_html(
    theme: str | None,
    voice_block: str,
    closed_trade_count: int,
    latest_blog: dict | None,
    recent_reports: list[dict] | None = None,
    recent_closes: list[dict] | None = None,
    featured_trade: dict | None = None,
) -> tuple[str, str, str, str]:
    """Single-shot Gemini render of the weekly newsletter.

    Returns (html, plain_text, subject, preheader). MODEL is the same
    `gemini-3-flash-preview` the blog pipeline uses — do NOT change it.

    The writer is fed REAL data — daily_reports headlines from the past
    week and V5.3 ledger closes — so it summarizes what actually happened
    rather than inventing tickers.
    """
    from google import genai

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("PROJECT_ID", "profitscout-fida8"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )

    blog_block = "(no published blog post yet — skip the 'What we wrote' section)"
    if latest_blog:
        intro_excerpt = (latest_blog.get("markdown", "") or "")[:1200]
        blog_block = (
            f"slug: {latest_blog.get('slug', '')}\n"
            f"title: {latest_blog.get('title', '')}\n"
            f"description: {latest_blog.get('description', '')}\n"
            f"first_1200_chars_of_markdown:\n{intro_excerpt}"
        )

    # Build report-summary block from real Firestore daily_reports docs.
    reports = recent_reports or []
    if reports:
        report_lines = []
        for r in reports[:5]:
            line = f"- {r.get('scan_date','')}: {r.get('title','').strip()}"
            if r.get("headline"):
                line += f" — {(r['headline'] or '').strip()[:200]}"
            counts = (
                f" ({r.get('total_signals','?')} signals: "
                f"{r.get('bullish_count','?')} bull / {r.get('bearish_count','?')} bear)"
                if r.get("total_signals") is not None else ""
            )
            report_lines.append(line + counts)
        reports_block = "\n".join(report_lines)
    else:
        reports_block = "(no daily reports available for the past week)"

    # Featured trade — the single highest-return positive close of the week.
    # Drives FOMO copy ("Did you catch this trade?"). Skipped entirely if
    # no winners closed this week (losses don't drive sub conversion).
    if featured_trade:
        ft_block = (
            f"ticker: ${featured_trade.get('ticker','')}\n"
            f"direction: {featured_trade.get('direction','')}\n"
            f"entry_date: {featured_trade.get('entry_date','')}\n"
            f"exit_date: {featured_trade.get('exit_date','')}\n"
            f"return: {featured_trade.get('pct_signed','')}\n"
            f"exit_reason: {featured_trade.get('exit_reason','')}"
        )
    else:
        ft_block = "(no winning V5.3 trade closed this week — SKIP the Featured trade section entirely)"

    theme_hint = (theme or "weekly").strip() or "weekly"

    prompt = f"""You are the @gammarips weekly newsletter writer. Output a single
HTML email body suitable for Mailgun. NO Markdown, NO code fences — pure
inline-styled HTML. Email-client-safe (table-friendly, inline styles only,
no external CSS). Width 600px. Dark text on white background.

# Voice rules (must follow)
{voice_block}

# Newsletter theme
{theme_hint}

# Engine state (internal context — DO NOT print this number verbatim in the email body)
- closed_trade_count_internal = {closed_trade_count}
  - This counts every V5.3-bracket trade in the live ledger (the trader runs
    a bracket on every enrichment signal). It is NOT the public track record.
  - The PUBLIC track record is the list of "This week's V5.3 closes" below
    — the only trades the audience has actually seen. Cite ONLY those.
- DO NOT write phrases like "the engine has N closed trades" in the email
  body. That number is internal-only and would mislead readers.

# This week's daily reports (REAL data — summarize these, do NOT invent)
{reports_block}

# Featured trade this week (REAL — the top positive V5.3 close. Render this
# as a prominent callout with FOMO framing. SKIP if 'no winning V5.3 trade'.)
{ft_block}

# Latest blog post (for "What we wrote" section)
{blog_block}

# CRITICAL ANTI-HALLUCINATION RULES
- ONLY mention tickers that appear verbatim in the data blocks above.
  No inventing tickers.
- ONLY cite numbers (signal counts, return percentages) that appear
  verbatim in the data above.
- If 'no winning V5.3 trade' is shown for the featured trade, SKIP the
  Featured Trade section entirely — do NOT invent a winner.
- NEVER reference $SPY, $QQQ, $IWM, $DIA, or any ticker not in the lists.

# Required structure
1. Subject line (≤50 chars). Output as: <!--SUBJECT: ...-->
   If a featured trade exists, lead with it: e.g.
   "$<ticker> closed +<pct>% — did you catch it?"
2. Preheader (≤90 chars). Output as: <!--PREHEADER: ...-->
3. <h1> headline.
4. ## This week — 2-3 sentences synthesizing the daily-report theme(s)
   above. Reference 1-2 specific reports by their headline.
5. ## Featured trade this week — IF a featured trade is provided above,
   render a prominent callout block:
   - Big stat line: "$<ticker> <direction> closed <pct_signed>"
   - The return-percentage value (the "+80%" portion) MUST be wrapped in
     `<span style="color: #16a34a; font-weight: 700;">...</span>` — green
     for ALL winning trades regardless of direction (BULLISH or BEARISH
     wins both render green; we celebrate the outcome, not the side).
   - Entry → Exit dates and the exit_reason ("target hit" / "3-day exit"
     / "stop hit") — translate exit_reason verbatim from the data block.
   - **FOMO copy line, exact intent**: "Did you catch this trade? Paid
     subscribers get our curated daily V5.3 pick at 09:00 AM ET — straight
     to inbox, no chart-watching required."
   - Then immediately the paper-trade disclosure as a small italic line:
     "Paper-trade. Past performance is not a guarantee of future results."
   IF no featured trade, OMIT this entire section.
6. ## What we wrote — only if a latest_blog exists; ~120 word excerpt + a
   link to https://gammarips.com/blog/<slug>. Skip if no post.
7. ## Disclaimer — EXACT verbatim substring at the bottom:

   "Paper-trading performance, educational content only. Not investment
   advice. Past performance is not a guarantee of future results."

8. CTA: founder pricing $29/mo with code FOUNDER29 (or $39/mo without).
   NO seat cap, NO scarcity copy. Link to https://gammarips.com/pricing.
   The CTA appears in EVERY newsletter.

# Hard prohibitions (auto-fail)
- Retired aliases: Ripper, Rippers, Daily Playbook, Overnight Edge (as
  product name), "@mention", "score >= 6", "8:30 AM", "$49/$149",
  "premium signal", "interactive dashboard".
- Recommendation language: "buy this", "act now", second-person timing
  imperatives.
- Scarcity: "only N seats", "500-seat cap", "while supplies last".
- Inventing tickers, signal counts, win rates, or P&L numbers not in the
  data blocks above.

# Output format — STRICT
Emit a single response in this exact shape (no commentary outside the tags):

<!--SUBJECT: GammaRips weekly — ...-->
<!--PREHEADER: ...-->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>...</title>
  </head>
  <body style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1a1f2e; max-width: 600px; margin: 0 auto; padding: 24px;">
    ... full email ...
  </body>
</html>
""".strip()

    response = client.models.generate_content(model=MODEL, contents=prompt)

    # Extract raw text from the candidate.
    raw = ""
    for cand in response.candidates or []:
        for part in (cand.content.parts if cand.content else []) or []:
            if getattr(part, "text", None):
                raw += part.text

    # Pull subject + preheader sentinels.
    subj_match = re.search(r"<!--\s*SUBJECT:\s*(.*?)-->", raw, re.IGNORECASE | re.DOTALL)
    pre_match = re.search(r"<!--\s*PREHEADER:\s*(.*?)-->", raw, re.IGNORECASE | re.DOTALL)
    subject = (subj_match.group(1).strip() if subj_match else f"GammaRips weekly — {theme_hint}")[:120]
    preheader = (pre_match.group(1).strip() if pre_match else "")[:160]

    # Strip the sentinel comments from the HTML body.
    html = re.sub(r"<!--\s*SUBJECT:.*?-->", "", raw, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<!--\s*PREHEADER:.*?-->", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = html.strip()

    # Plain-text alternative — naive HTML strip for Mailgun text/plain.
    text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|h[1-6]|li|tr|div)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return html, text, subject, preheader


@app.post("/draft_email", response_model=DraftEmailResponse)
def draft_email(req: DraftEmailRequest) -> DraftEmailResponse:
    """Render the weekly newsletter, save to GCS, and email the operator.

    Operator-preview-only: even with dry_run=False, the email goes ONLY to
    OPERATOR_EMAIL. /blast_email is the only path to the user list.

    Compliance is deterministic — `compliance.score_against_rubric()` must
    pass or the endpoint returns 422 with the failures listed and no
    Mailgun call is made.
    """
    try:
        # 1. Voice rules for prompt context.
        voice_block = voice_rules.render_for_prompt()

        # 2. Latest published blog post (skipped section if none).
        latest_blog = tools.get_latest_blog_post()

        # 3. Engine state — V5.3 closed-trade count.
        closed_count = tools.get_closed_trade_count()

        # 4. Real content for the "this week" section — past 7 days of
        # daily_reports headlines + V5.3 ledger closes. Without this the
        # writer hallucinates tickers (Evan 2026-04-30 incident).
        recent_reports = tools.get_recent_daily_reports(days=7)
        recent_closes = tools.get_recent_v53_closes(days=7)

        # 4b. Featured trade — top single positive V5.3 close. Drives FOMO
        # ("Did you catch this trade?"). Only winners qualify; if no
        # winning V5.3 trade closed this week, the section is skipped.
        winners = [
            c for c in recent_closes
            if (c.get("return_pct") is not None) and c["return_pct"] > 0
        ]
        featured_trade = (
            max(winners, key=lambda c: c["return_pct"]) if winners else None
        )

        # 5. Single-shot Gemini render.
        try:
            html, text, subject, preheader = _render_newsletter_html(
                theme=req.theme,
                voice_block=voice_block,
                closed_trade_count=closed_count,
                latest_blog=latest_blog,
                recent_reports=recent_reports,
                recent_closes=recent_closes,
                featured_trade=featured_trade,
            )
        except Exception as exc:  # noqa: BLE001
            _py_logger.exception("newsletter Gemini render failed")
            raise HTTPException(status_code=500, detail=f"render_failed: {exc}") from exc

        if not html or len(html) < 200:
            raise HTTPException(
                status_code=500,
                detail=f"render_too_short: len={len(html)} — Gemini returned an empty body",
            )

        # 5. Compliance gate — hard-fail before any Mailgun call. Use blog
        # mode (is_blog=True) so URL/cashtag/char-budget rules don't apply
        # — newsletters are HTML emails with links, not 280-char tweets.
        # The retired-alias + banned-recommendation scans still run and
        # are the load-bearing checks here. We score the plain-text form
        # so HTML tags don't accidentally trip alias/cashtag patterns.
        rubric = compliance.score_against_rubric(
            text=text,
            post_type="newsletter",
            is_blog=True,
        )
        if not rubric.passed:
            return DraftEmailResponse(
                status="compliance_failed",
                subject=subject,
                preview_text=preheader,
                compliance_passed=False,
                compliance_failures=list(rubric.failures),
                error="newsletter rejected by compliance rubric — fix and retry",
            )

        # 6. Write to GCS.
        date_iso = tools.today_et_iso()
        base = f"email/{date_iso}_newsletter"
        html_uri = f"gs://{EMAIL_DRAFTS_BUCKET}/{base}.html"
        text_uri = f"gs://{EMAIL_DRAFTS_BUCKET}/{base}.txt"
        subject_uri = f"gs://{EMAIL_DRAFTS_BUCKET}/{base}.subject.txt"
        preheader_uri = f"gs://{EMAIL_DRAFTS_BUCKET}/{base}.preheader.txt"
        try:
            tools.write_to_gcs(html_uri, html, content_type="text/html")
            tools.write_to_gcs(text_uri, text, content_type="text/plain")
            tools.write_to_gcs(subject_uri, subject, content_type="text/plain")
            tools.write_to_gcs(preheader_uri, preheader, content_type="text/plain")
        except Exception as exc:  # noqa: BLE001
            _py_logger.exception("GCS write failed")
            return DraftEmailResponse(
                status="gcs_error",
                subject=subject,
                preview_text=preheader,
                compliance_passed=True,
                error=(
                    f"GCS write failed: {exc}. "
                    f"If the bucket is missing, run: "
                    f"gsutil mb -p profitscout-fida8 -l us-central1 "
                    f"gs://{EMAIL_DRAFTS_BUCKET}"
                ),
            )

        # 7+8. Operator-only Mailgun send (always — both dry_run=True and False).
        operator_email = os.environ.get("OPERATOR_EMAIL", "evan@gammarips.com").strip()
        send_subject = f"[DRAFT preview] {subject}"
        send_result = tools.send_email_via_mailgun(
            to=operator_email,
            subject=send_subject,
            html=html,
            text=text,
        )

        logger.log_struct(
            {
                "event": "draft_email_complete",
                "gcs_uri": html_uri,
                "subject": subject,
                "operator_send_status": send_result.get("status"),
                "compliance_passed": True,
            },
            severity="INFO",
        )

        return DraftEmailResponse(
            status="ok",
            gcs_uri=html_uri,
            gcs_uri_text=text_uri,
            subject=subject,
            preview_text=preheader,
            compliance_passed=True,
            compliance_failures=[],
            operator_send_status=send_result.get("status"),
            error=send_result.get("message"),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        _py_logger.exception("/draft_email unexpected failure")
        raise HTTPException(status_code=500, detail=f"draft_email_failed: {exc}") from exc


@app.post("/blast_email", response_model=BlastEmailResponse)
def blast_email(req: BlastEmailRequest) -> BlastEmailResponse:
    """Fan-out a previously-drafted newsletter to a user audience.

    Per-recipient Mailgun send (NEVER BCC). dry_run=True is the default
    safety; in dry-run we send only to OPERATOR_EMAIL and report the
    would-be audience count + first-3 sample.
    """
    # 1. Validate URI is under the drafts bucket + email/ prefix.
    expected_prefix = f"gs://{EMAIL_DRAFTS_BUCKET}/email/"
    if not req.gcs_uri.startswith(expected_prefix):
        raise HTTPException(
            status_code=400,
            detail=(
                f"gcs_uri must start with {expected_prefix!r} — "
                f"got {req.gcs_uri!r}"
            ),
        )

    # 2. Load HTML + text + subject + preheader from GCS.
    try:
        html = tools.read_from_gcs(req.gcs_uri)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=f"gcs_read_failed: {exc}") from exc

    text_uri = req.gcs_uri.rsplit(".html", 1)[0] + ".txt"
    try:
        text = tools.read_from_gcs(text_uri)
    except Exception:  # noqa: BLE001
        text = None  # text alternative is optional

    subject_uri = req.gcs_uri.rsplit(".html", 1)[0] + ".subject.txt"
    subject: str | None = None
    if tools.gcs_object_exists(subject_uri):
        try:
            subject = tools.read_from_gcs(subject_uri).strip()
        except Exception:  # noqa: BLE001
            subject = None
    if not subject:
        m = _TITLE_RE.search(html)
        subject = m.group(1).strip() if m else "GammaRips weekly"
    subject = subject[:200]

    # 3. Load audience.
    audience_list = tools.read_email_audience(req.audience)
    audience_count = len(audience_list)
    sample = [u["email"] for u in audience_list[:3]]

    # 4. Dry run → operator-only.
    if req.dry_run:
        operator_email = os.environ.get("OPERATOR_EMAIL", "evan@gammarips.com").strip()
        op_subject = f"[BLAST dry-run | audience={req.audience} count={audience_count}] {subject}"
        result = tools.send_email_via_mailgun(
            to=operator_email,
            subject=op_subject,
            html=html,
            text=text,
        )
        logger.log_struct(
            {
                "event": "blast_email_dry_run",
                "audience": req.audience,
                "audience_count": audience_count,
                "sample": sample,
                "operator_send_status": result.get("status"),
            },
            severity="INFO",
        )
        return BlastEmailResponse(
            status="dry_run",
            audience=req.audience,
            audience_count=audience_count,
            sent=1 if result.get("status") == "success" else 0,
            failed=0 if result.get("status") == "success" else 1,
            dry_run=True,
            recipient_sample=sample,
            subject=subject,
            error=result.get("message"),
        )

    # 5. Real fan-out — per-recipient send, capped for safety.
    max_recipients = int(os.environ.get("MAX_RECIPIENTS", "1000"))
    if audience_count > max_recipients:
        raise HTTPException(
            status_code=400,
            detail=(
                f"audience_count={audience_count} exceeds MAX_RECIPIENTS={max_recipients}. "
                f"Raise MAX_RECIPIENTS env var explicitly to proceed."
            ),
        )

    sent = 0
    failed = 0
    for u in audience_list:
        try:
            r = tools.send_email_via_mailgun(
                to=u["email"],
                subject=subject,
                html=html,
                text=text,
            )
            if r.get("status") == "success":
                sent += 1
            else:
                failed += 1
                _py_logger.warning(f"blast_email send failed for {u['email']!r}: {r}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            _py_logger.exception(f"blast_email send raised for {u.get('email')!r}: {exc}")

    logger.log_struct(
        {
            "event": "blast_email_complete",
            "audience": req.audience,
            "audience_count": audience_count,
            "sent": sent,
            "failed": failed,
            "subject": subject,
            "gcs_uri": req.gcs_uri,
            "completed_at": datetime.utcnow().isoformat() + "Z",
        },
        severity="INFO" if failed == 0 else "WARNING",
    )
    return BlastEmailResponse(
        status="sent",
        audience=req.audience,
        audience_count=audience_count,
        sent=sent,
        failed=failed,
        dry_run=False,
        recipient_sample=sample,
        subject=subject,
    )


# --- /blast_latest -- auto-discover most recent draft + safety gates -----
#
# Designed for the Mon 05:30 ET cron. Sequence:
#   1. Find latest gs://{EMAIL_DRAFTS_BUCKET}/email/<date>_newsletter.html
#   2. Honor blast_killswitch/{date} if Evan set aborted=true after the
#      Sun preview.
#   3. Idempotent via blast_history/{date} — atomic-create lock prevents
#      double-blasts under Cloud Scheduler retry storms.
#   4. Delegate the actual fan-out to the existing /blast_email handler.
#
# Operator kill workflow (run between Sun 17:00 ET preview and Mon 05:30 ET):
#   gcloud firestore documents set blast_killswitch/<DATE> \
#     --data='{"aborted": true, "reason": "..."}' \
#     --project=profitscout-fida8


class BlastLatestRequest(BaseModel):
    audience: Literal["all", "free", "paid"] = Field(
        default="all",
        description="Audience selector — same semantics as /blast_email.",
    )
    dry_run: bool = Field(
        default=False,
        description=(
            "Default False (this endpoint is the auto-blast path). Setting "
            "True routes through the same operator-only preview behavior as "
            "/blast_email dry_run=True."
        ),
    )
    date_iso: Optional[str] = Field(
        default=None,
        description=(
            "YYYY-MM-DD draft date override (manual backfill). If omitted, "
            "the latest draft in GCS is used."
        ),
    )


class BlastLatestResponse(BaseModel):
    status: str  # blasted | killed | already_blasted | no_draft | dry_run
    date_iso: Optional[str] = None
    gcs_uri: Optional[str] = None
    audience: Optional[str] = None
    audience_count: int = 0
    sent: int = 0
    failed: int = 0
    dry_run: bool = False
    reason: Optional[str] = None
    error: Optional[str] = None


@app.post("/blast_latest", response_model=BlastLatestResponse)
def blast_latest(req: BlastLatestRequest) -> BlastLatestResponse:
    """Auto-discover the latest newsletter draft, honor kill switch, blast.

    The auto-blast cron path. Safe to call repeatedly — idempotent on the
    draft date, honors `blast_killswitch/<date>`, and falls through to
    `/blast_email` for the fan-out itself.
    """
    # 1. Discover the draft.
    if req.date_iso:
        gcs_uri = f"gs://{EMAIL_DRAFTS_BUCKET}/email/{req.date_iso}_newsletter.html"
        if not tools.gcs_object_exists(gcs_uri):
            return BlastLatestResponse(
                status="no_draft", date_iso=req.date_iso, audience=req.audience,
                dry_run=req.dry_run, reason=f"draft missing at {gcs_uri}",
            )
        date_iso = req.date_iso
    else:
        latest = tools.find_latest_email_draft()
        if not latest:
            return BlastLatestResponse(
                status="no_draft", audience=req.audience, dry_run=req.dry_run,
                reason="no draft objects under email/ prefix",
            )
        gcs_uri, date_iso = latest

    # 2. Kill switch — operator can abort between Sun preview and Mon blast.
    if tools.is_blast_killswitch_set(date_iso):
        operator_email = os.environ.get("OPERATOR_EMAIL", "evan@gammarips.com").strip()
        try:
            tools.send_email_via_mailgun(
                to=operator_email,
                subject=f"[KILL HONORED] blast {date_iso} aborted",
                html=(
                    f"<p>Kill switch <code>blast_killswitch/{date_iso}</code> "
                    f"is set. No emails were sent for draft {gcs_uri}.</p>"
                ),
                text=f"Kill switch honored for {date_iso}. No emails sent.",
            )
        except Exception as exc:  # noqa: BLE001
            _py_logger.warning(f"kill-switch operator notification failed: {exc}")
        logger.log_struct(
            {"event": "blast_latest_killed", "date_iso": date_iso, "gcs_uri": gcs_uri},
            severity="WARNING",
        )
        return BlastLatestResponse(
            status="killed", date_iso=date_iso, gcs_uri=gcs_uri,
            audience=req.audience, dry_run=req.dry_run, reason="killswitch_set",
        )

    # 3. Idempotency — atomic-create a history doc so two cron retries can't
    #    both fan out. Skipped on dry_run since dry runs don't fan to users.
    if not req.dry_run:
        prior = tools.get_blast_history(date_iso)
        if prior and prior.get("status") in ("completed", "in_progress"):
            return BlastLatestResponse(
                status="already_blasted", date_iso=date_iso, gcs_uri=gcs_uri,
                audience=prior.get("audience", req.audience),
                audience_count=int(prior.get("audience_count", 0) or 0),
                sent=int(prior.get("sent", 0) or 0),
                failed=int(prior.get("failed", 0) or 0),
                dry_run=False, reason=f"prior_status={prior.get('status')}",
            )
        if not tools.mark_blast_started(date_iso, gcs_uri, req.audience):
            return BlastLatestResponse(
                status="already_blasted", date_iso=date_iso, gcs_uri=gcs_uri,
                audience=req.audience, dry_run=False, reason="lock_create_failed",
            )

    # 4. Delegate to /blast_email — single source of truth for fan-out.
    blast_resp = blast_email(BlastEmailRequest(
        gcs_uri=gcs_uri, audience=req.audience, dry_run=req.dry_run,
    ))

    # 5. Record outcome.
    if not req.dry_run:
        tools.mark_blast_completed(
            date_iso=date_iso,
            sent=blast_resp.sent,
            failed=blast_resp.failed,
            audience_count=blast_resp.audience_count,
            status="completed" if blast_resp.failed == 0 else "completed_with_errors",
        )

    logger.log_struct(
        {
            "event": "blast_latest_complete",
            "date_iso": date_iso,
            "gcs_uri": gcs_uri,
            "audience": blast_resp.audience,
            "audience_count": blast_resp.audience_count,
            "sent": blast_resp.sent,
            "failed": blast_resp.failed,
            "dry_run": req.dry_run,
        },
        severity="INFO" if blast_resp.failed == 0 else "WARNING",
    )
    return BlastLatestResponse(
        status="dry_run" if req.dry_run else "blasted",
        date_iso=date_iso,
        gcs_uri=gcs_uri,
        audience=blast_resp.audience,
        audience_count=blast_resp.audience_count,
        sent=blast_resp.sent,
        failed=blast_resp.failed,
        dry_run=req.dry_run,
        error=blast_resp.error,
    )


# --- /weekly_intel -- Mon 07:00 ET intel report ---------------------------
#
# Pulls GA4 + GSC + ledger + blast-history rollups, asks Gemini to surface
# 5 sections of human-readable intel + 5-10 numbered suggestions, sends the
# report via Mailgun to OPERATOR_EMAIL.
#
# Approval workflow is INFORMAL: operator reads the email, comes back to a
# Claude session, and says "implement #2 and #5" — no inbound-email parsing
# required. Suggestions are numbered consistently so referencing them is easy.
#
# GA4 + GSC are stub-able: until the operator finishes service-account setup
# (see deploy.sh trailing comments), those sections degrade to "not yet
# configured" hints rather than failing the whole endpoint.


class WeeklyIntelRequest(BaseModel):
    days: int = Field(
        default=7,
        description="Lookback window for GA4/GSC summaries (days).",
    )
    ledger_days: int = Field(
        default=30,
        description="Lookback window for ledger health rollup.",
    )
    dry_run: bool = Field(
        default=False,
        description=(
            "If True, return the rendered HTML in the response without "
            "emailing the operator."
        ),
    )


class WeeklyIntelResponse(BaseModel):
    status: str  # ok | error
    sections: int
    operator_send_status: Optional[str] = None
    subject: Optional[str] = None
    html_preview: Optional[str] = None
    error: Optional[str] = None
    ga4_status: Optional[str] = None
    gsc_status: Optional[str] = None


def _render_weekly_intel_email(
    ga4: dict,
    gsc: dict,
    ledger: dict,
    blasts: list[dict],
    closes: list[dict],
    voice_block: str,
) -> tuple[str, str]:
    """Single-shot Gemini render of the weekly intel email.

    Returns (subject, html). The prompt is anti-hallucination: model is told
    explicitly to never invent metrics not in the data blocks.
    """
    from google import genai
    client = genai.Client(
        vertexai=True,
        project=os.environ.get("PROJECT_ID", "profitscout-fida8"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )

    import json as _json

    def _block(label: str, data: Any) -> str:
        return f"## {label}\n```json\n{_json.dumps(data, default=str, indent=2)}\n```"

    prompt = f"""You are the GammaRips weekly operations intel writer. Output a
concise HTML email body for Mailgun (inline-styled, 600px max width, dark
text on white). NO Markdown, NO code fences, no external CSS.

# Voice rules (must follow)
{voice_block}

# Data blocks (read these — DO NOT INVENT METRICS)

{_block("GA4 traffic (last 7d)", ga4)}

{_block("GSC search (last 7d)", gsc)}

{_block("V5.3 ledger health (last 30d)", ledger)}

{_block("Newsletter blast history (last 4 weeks)", blasts)}

{_block("V5.3 closed trades this week", closes)}

# Required structure (use exactly these section headings)
1. <h1>GammaRips weekly intel — <date></h1> where <date> is today's ISO.
2. <h2>What worked</h2> — 3-5 bullets. Cite specific tickers, numbers,
   GA4 sources, or GSC queries from the data blocks. If data is missing
   ("status: unavailable"), skip that bullet rather than inventing.
3. <h2>What didn't</h2> — 3-5 bullets. Bounce rate, lost positions in
   search, failed sends, etc. — surfaced from the same data.
4. <h2>Anomalies + outliers</h2> — 0-3 bullets only when something
   genuinely sticks out (3x traffic spike, single-query CTR collapse,
   >2 stop-outs in a row). Skip the section if nothing qualifies.
5. <h2>Numbered suggestions</h2> — 5 to 10 ordered suggestions, each
   one tagged with one of [CONTENT], [PRODUCT], [INFRA], [DISTRIBUTION].
   Each suggestion is one sentence + a one-line rationale. Number them
   1..N — the operator will reply "implement 2, 5, 7" by number, so
   numbering must be unambiguous.
6. <h2>Confirm to implement</h2> — A single sentence: "Reply or message
   Claude with the numbers you want me to implement (e.g. 'implement 2, 5')."

# Hard rules (auto-fail)
- ONLY mention numbers, tickers, queries, sources, etc. that appear
  verbatim in the data blocks. No invented metrics.
- Skip sections when their data is missing rather than fabricating.
- No retired aliases (Ripper, Daily Playbook, Overnight Edge, score>=6,
  $49/$149, premium signal).
- No scarcity copy. No FOMO. This is operator intel, not marketing.

# Output format
Emit a single response. First line must be a sentinel:
<!--SUBJECT: weekly intel — YYYY-MM-DD - <one-line tldr ≤ 60 chars>-->
Then the HTML body. No commentary outside.
""".strip()

    response = client.models.generate_content(model=MODEL, contents=prompt)
    raw = ""
    for cand in response.candidates or []:
        for part in (cand.content.parts if cand.content else []) or []:
            if getattr(part, "text", None):
                raw += part.text
    subj_match = re.search(r"<!--\s*SUBJECT:\s*(.*?)-->", raw, re.IGNORECASE | re.DOTALL)
    subject = (subj_match.group(1).strip() if subj_match else f"GammaRips weekly intel — {tools.today_et_iso()}")[:200]
    html = re.sub(r"<!--\s*SUBJECT:.*?-->", "", raw, flags=re.IGNORECASE | re.DOTALL).strip()
    return subject, html


@app.post("/weekly_intel", response_model=WeeklyIntelResponse)
def weekly_intel(req: WeeklyIntelRequest) -> WeeklyIntelResponse:
    """Pull GA4 + GSC + ledger + blast history; Gemini synthesize; email."""
    try:
        voice_block = voice_rules.render_for_prompt()
        ga4 = tools.fetch_ga4_traffic_summary(days=req.days)
        gsc = tools.fetch_gsc_search_summary(days=req.days)
        ledger = tools.fetch_ledger_intel_summary(days=req.ledger_days)
        blasts = tools.fetch_recent_blast_history(weeks=4)
        closes = tools.get_recent_v53_closes(days=req.days)

        subject, html = _render_weekly_intel_email(
            ga4=ga4, gsc=gsc, ledger=ledger,
            blasts=blasts, closes=closes, voice_block=voice_block,
        )

        if not html or len(html) < 200:
            raise HTTPException(
                status_code=500,
                detail=f"intel_render_too_short: len={len(html)}",
            )

        text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</(p|h[1-6]|li|tr|div)>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        if req.dry_run:
            logger.log_struct(
                {"event": "weekly_intel_dry_run", "ga4_status": ga4.get("status"),
                 "gsc_status": gsc.get("status"), "subject": subject},
                severity="INFO",
            )
            return WeeklyIntelResponse(
                status="ok", sections=5, subject=subject, html_preview=html[:2000],
                ga4_status=ga4.get("status"), gsc_status=gsc.get("status"),
            )

        operator_email = os.environ.get("OPERATOR_EMAIL", "evan@gammarips.com").strip()
        send_result = tools.send_email_via_mailgun(
            to=operator_email, subject=subject, html=html, text=text,
        )
        logger.log_struct(
            {"event": "weekly_intel_sent", "ga4_status": ga4.get("status"),
             "gsc_status": gsc.get("status"), "subject": subject,
             "operator_send_status": send_result.get("status")},
            severity="INFO",
        )
        return WeeklyIntelResponse(
            status="ok", sections=5, subject=subject,
            operator_send_status=send_result.get("status"),
            ga4_status=ga4.get("status"), gsc_status=gsc.get("status"),
            error=send_result.get("message"),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        _py_logger.exception("/weekly_intel failure")
        raise HTTPException(status_code=500, detail=f"weekly_intel_failed: {exc}") from exc


# --- /draft_reddit -- Tier-1 subs weekly Markdown drafts ------------------

# Hand-curated voice config per Tier-1 subreddit. Lives in code (not Firestore)
# until voice tuning becomes a regular thing — easier to iterate via PR.
# `lead_style` examples: "lead with a specific number", "lead with a question",
# "lead with a contrarian claim". `taboo_phrases` are auto-rejected. `length_words`
# is target window. `mod_traps` describes common failure modes per sub.
_DEFAULT_SUBREDDIT_VOICE: dict[str, dict[str, Any]] = {
    "options": {
        "lead_style": "lead with a specific bracket or number from the engine (e.g. '76 setups overnight, 1 cleared the gate stack')",
        "taboo_phrases": ["YOLO", "to the moon", "tendies", "boomer puts", "free money"],
        "length_words": (180, 320),
        "mod_traps": "r/options auto-removes posts that look like spam-marketing. Avoid promotional language; describe the methodology instead.",
        "tone": "Methodical, structural. Engineer talking to engineers about systematic options flow.",
    },
    "thetagang": {
        "lead_style": "lead with a paper-trade outcome with realistic numbers, then unpack the entry/exit rules",
        "taboo_phrases": ["YOLO", "to the moon", "no-brainer", "guaranteed", "easy money"],
        "length_words": (200, 380),
        "mod_traps": "r/thetagang values process over outcome. Posts that brag get removed. Lead with the rule, then the result.",
        "tone": "Disciplined, premium-selling-adjacent. Acknowledge the audience knows their greeks.",
    },
    "algotrading": {
        "lead_style": "lead with a falsifiable claim or a backtest-vs-live divergence, NOT a result",
        "taboo_phrases": ["AI predictions", "ML magic", "sharpe > 5", "backtested gold"],
        "length_words": (220, 400),
        "mod_traps": "r/algotrading auto-rejects posts without methodology. Lead with the gate stack or the bracket logic, not the P&L.",
        "tone": "Engineering-first. Describe the system, not the returns.",
    },
}

_NUMBER_LEAD_RE = re.compile(r"^[^\n]{0,80}?\d", re.MULTILINE)


def _read_subreddit_voice(sub: str) -> dict[str, Any]:
    """Look up voice config for a subreddit. Falls back to embedded defaults
    if a Firestore override doesn't exist (`content_config/subreddit_voice/{sub}`)."""
    try:
        override = tools.fetch_subreddit_voice_override(sub)  # type: ignore[attr-defined]
        if override:
            return override
    except AttributeError:
        pass
    except Exception as exc:  # noqa: BLE001
        _py_logger.warning(f"subreddit voice override fetch failed for {sub!r}: {exc}")
    if sub not in _DEFAULT_SUBREDDIT_VOICE:
        raise HTTPException(
            status_code=400,
            detail=f"unknown_sub: {sub!r} not in default voice list {list(_DEFAULT_SUBREDDIT_VOICE)}",
        )
    return _DEFAULT_SUBREDDIT_VOICE[sub]


def _render_reddit_post(
    theme: str | None,
    sub: str,
    voice: dict[str, Any],
    voice_block: str,
    closed_count: int,
) -> tuple[str, str]:
    """Single-shot Gemini render of a Markdown Reddit post for one sub.

    Returns (title, markdown_body). Title is one line, no markdown.
    """
    from google import genai

    client = genai.Client(
        vertexai=True,
        project=os.environ.get("PROJECT_ID", "profitscout-fida8"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
    lo, hi = voice["length_words"]
    theme_hint = (theme or "weekly").strip() or "weekly"

    prompt = f"""You are drafting a Reddit post for r/{sub}. Output a single
post in this exact format and nothing else:

<!--TITLE: ...-->
<post body in plain Markdown>

# Voice rules (must follow)
{voice_block}

# Subreddit-specific style
- Lead style: {voice["lead_style"]}
- Tone: {voice["tone"]}
- Mod traps to avoid: {voice["mod_traps"]}
- Length target: {lo}-{hi} words.
- TABOO phrases (auto-fail): {", ".join(voice["taboo_phrases"])}.

# Theme this week
{theme_hint}

# Engine state
- closed_trade_count = {closed_count}
  - If < 30: structural language only. NO claimed win rates / aggregate P&L.
  - If >= 30: aggregate numbers OK as structural claim, never as recommendation.

# Hard prohibitions (auto-fail)
- NO URLs anywhere in the body. (Reddit auto-flags spam.)
- NO recommendation language ("buy this", "act now", "you should").
- NO retired aliases: Ripper, Daily Playbook, Overnight Edge (as product),
  premium signal, "score >= 6".
- NO scarcity copy ("only N seats", "while supplies last", "founding cohort").
- NO promo of paid product. This is methodology content for community
  credibility, not lead generation.

# What to write about
Pick ONE specific, concrete angle from the engine's last-week activity:
- A specific gate (overnight_score>=1, spread<=10%, UOA>$500K, V/OI>2)
  and WHY that bracket was picked.
- The -60%/+80% bracket and how it lines up with realistic option premium
  decay over a 3-day hold.
- The "conservative on ambiguous bars" rule (stop wins over target on the
  same bar) and why that rule reduces variance.
- A common misread of unusual options activity that the gate stack rules out.
- The difference between contract count and dollar volume as popularity
  signals (high-contract small-caps vs. high-dollar big names).

Pick ONE. Write it like a methodology post, not a recap. The reader is a
self-directed trader who will be skeptical of any post that smells like
marketing — earn their attention with specifics.

# Output format — STRICT
Emit a single response in this exact shape (no commentary outside the tags):

<!--TITLE: ...-->
<markdown body — paragraphs, NO heading lines other than optional sub-heads>
""".strip()

    response = client.models.generate_content(model=MODEL, contents=prompt)
    raw = ""
    for cand in response.candidates or []:
        for part in (cand.content.parts if cand.content else []) or []:
            if getattr(part, "text", None):
                raw += part.text

    title_match = re.search(r"<!--\s*TITLE:\s*(.*?)-->", raw, re.IGNORECASE | re.DOTALL)
    title = (title_match.group(1).strip() if title_match else f"Methodology — {theme_hint}")[:200]
    body = re.sub(r"<!--\s*TITLE:.*?-->", "", raw, flags=re.IGNORECASE | re.DOTALL).strip()
    return title, body


def _score_reddit_rubric(
    title: str, body: str, sub: str, voice: dict[str, Any]
) -> tuple[bool, list[str], list[str]]:
    """Per-sub Reddit rubric. Hard fails (block GCS+email): URL in body,
    taboo phrases, retired aliases, banned recommendation phrases. Soft
    warnings (notify operator but still ship): word count out of window,
    lead-not-with-number. Returns (passed, failures, warnings)."""
    failures: list[str] = []
    warnings: list[str] = []
    word_count = len(body.split())
    lo, hi = voice["length_words"]
    if word_count < lo or word_count > hi:
        warnings.append(f"word_count_out_of_window: {word_count} not in [{lo},{hi}]")
    if compliance.URL_PATTERN.search(body):
        failures.append("url_in_body: Reddit body must contain no URLs")
    body_lower = body.lower()
    for phrase in voice["taboo_phrases"]:
        if phrase.lower() in body_lower:
            failures.append(f"taboo_phrase: '{phrase}'")
    # Lead-with-number heuristic — within first ~80 chars. Soft only.
    if not _NUMBER_LEAD_RE.match(body):
        warnings.append("lead_does_not_open_with_number")
    # Reuse retired-alias + banned-recommendation scans (is_blog=True skips
    # cashtag/char-budget rules, leaves alias + banned-phrase checks).
    shared = compliance.score_against_rubric(
        text=f"{title}\n\n{body}", post_type="reddit", is_blog=True
    )
    failures.extend(shared.failures)
    return (not failures), failures, warnings


class DraftRedditRequest(BaseModel):
    theme: Optional[str] = Field(
        default=None,
        description="Optional theme tag (e.g. 'gate-stack-explainer'). Defaults to 'weekly'.",
    )
    subs: Optional[list[str]] = Field(
        default=None,
        description="Subreddit list (without 'r/' prefix). Defaults to ['options','thetagang','algotrading'].",
    )
    dry_run: bool = Field(
        default=False,
        description="Operator-preview-only by design — drafts always go to OPERATOR_EMAIL only. The drafter NEVER auto-posts to Reddit.",
    )


class DraftRedditDraftItem(BaseModel):
    sub: str
    title: str
    gcs_uri: Optional[str] = None
    word_count: int
    compliance_passed: bool
    compliance_failures: list[str] = []
    compliance_warnings: list[str] = []
    error: Optional[str] = None


class DraftRedditResponse(BaseModel):
    status: str
    drafts: list[DraftRedditDraftItem] = []
    operator_send_status: Optional[str] = None
    error: Optional[str] = None


@app.post("/draft_reddit", response_model=DraftRedditResponse)
def draft_reddit(req: DraftRedditRequest) -> DraftRedditResponse:
    """Render Markdown post drafts for Tier-1 subs, save to GCS, email operator.

    NEVER auto-posts to Reddit. The operator manually copy-pastes from each
    GCS draft into the target sub at the prescribed Tue 10:00-12:00 ET window
    (per 90-day plan §3). Each per-sub draft is independent — a compliance
    failure on one sub does not block the others.
    """
    try:
        target_subs = req.subs or list(_DEFAULT_SUBREDDIT_VOICE.keys())
        voice_block = voice_rules.render_for_prompt()
        closed_count = tools.get_closed_trade_count()
        date_iso = tools.today_et_iso()

        drafts: list[DraftRedditDraftItem] = []
        operator_lines: list[str] = []

        for sub in target_subs:
            try:
                voice = _read_subreddit_voice(sub)
            except HTTPException as exc:
                drafts.append(DraftRedditDraftItem(
                    sub=sub, title="", word_count=0,
                    compliance_passed=False,
                    error=f"voice_lookup_failed: {exc.detail}",
                ))
                continue

            try:
                title, body = _render_reddit_post(
                    theme=req.theme, sub=sub, voice=voice,
                    voice_block=voice_block, closed_count=closed_count,
                )
            except Exception as exc:  # noqa: BLE001
                _py_logger.exception(f"reddit Gemini render failed for r/{sub}")
                drafts.append(DraftRedditDraftItem(
                    sub=sub, title="", word_count=0,
                    compliance_passed=False, error=f"render_failed: {exc}",
                ))
                continue

            passed, failures, warnings = _score_reddit_rubric(title, body, sub, voice)
            wc = len(body.split())

            gcs_uri: Optional[str] = None
            if passed:
                base = f"reddit/{date_iso}_{sub}"
                gcs_uri = f"gs://{EMAIL_DRAFTS_BUCKET}/{base}.md"
                try:
                    full_md = f"# {title}\n\n{body}\n"
                    tools.write_to_gcs(gcs_uri, full_md, content_type="text/markdown")
                except Exception as exc:  # noqa: BLE001
                    _py_logger.exception(f"GCS write failed for r/{sub}")
                    drafts.append(DraftRedditDraftItem(
                        sub=sub, title=title, word_count=wc,
                        compliance_passed=True, compliance_warnings=warnings,
                        error=f"gcs_write_failed: {exc}",
                    ))
                    continue

            drafts.append(DraftRedditDraftItem(
                sub=sub, title=title, gcs_uri=gcs_uri, word_count=wc,
                compliance_passed=passed, compliance_failures=failures,
                compliance_warnings=warnings,
            ))
            status_label = "ok" if passed else "compliance_failed"
            operator_lines.append(
                f"r/{sub} — {status_label}, {wc} words"
                + (f"\n  Title: {title}" if title else "")
                + (f"\n  GCS: {gcs_uri}" if gcs_uri else "")
                + (f"\n  Failures: {failures}" if failures else "")
                + (f"\n  Warnings: {warnings}" if warnings else "")
            )

        # Operator email — always send, even if some drafts compliance-failed.
        # The operator can rerun individual subs from the failure detail.
        operator_email = os.environ.get("OPERATOR_EMAIL", "evan@gammarips.com").strip()
        body_html = (
            "<h2>Reddit drafts ready</h2>"
            "<p>Target window: <strong>Tue 10:00 AM – 12:00 PM ET</strong>. "
            "Drafter never auto-posts; copy/paste manually.</p>"
            "<pre style=\"font-family: ui-monospace, monospace; white-space: pre-wrap;\">"
            + "\n\n".join(operator_lines)
            + "</pre>"
        )
        body_text = "Reddit drafts ready. Target window: Tue 10:00-12:00 ET.\n\n" + "\n\n".join(operator_lines)
        send_result = tools.send_email_via_mailgun(
            to=operator_email,
            subject=f"[Reddit drafts] {date_iso} — {len(drafts)} subs",
            html=body_html,
            text=body_text,
        )

        any_passed = any(d.compliance_passed for d in drafts)
        return DraftRedditResponse(
            status="ok" if any_passed else "all_compliance_failed",
            drafts=drafts,
            operator_send_status=send_result.get("status"),
            error=send_result.get("message"),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        _py_logger.exception("/draft_reddit unexpected failure")
        raise HTTPException(status_code=500, detail=f"draft_reddit_failed: {exc}") from exc


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
