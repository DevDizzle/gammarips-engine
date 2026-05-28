# ruff: noqa
"""
blog-generator — ADK multi-agent pipeline for GammaRips weekly blog publishing.

Pipeline:
    SequentialAgent
      ├── LoopAgent (max 3 iterations)
      │    ├── Planner   — reads schedule slot, prior posts, optional live context
      │    ├── Writer    — drafts 1,200-1,800 word markdown in brand voice
      │    ├── Reviewer  — structured APPROVE/REVISE (Pydantic + deterministic rubric)
      │    └── EscalationChecker — escalates the loop when APPROVED
      └── Publisher      — Firestore write (blog_posts/{slug}) + schedule row update

State keys across the pipeline:
    slug, voice_rules, post_outline, post_markdown, rubric_check, review,
    publish_result, iterations, dry_run

  `post_outline` (planner output) carries nested `schedule_slot` and
  `live_context` dicts — writer + reviewer read both from there rather
  than from separate top-level state keys.
"""
from __future__ import annotations

import logging
import os
from typing import AsyncGenerator, Literal

import google.auth
from google.adk.agents import Agent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps import App
from google.adk.events import Event, EventActions
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field

from app import tools
from gammarips_content import compliance, voice_rules

logger = logging.getLogger(__name__)

# --- GCP / Vertex configuration --------------------------------------------
_, _project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _project_id or "profitscout-fida8")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


# --- Structured output schema for the reviewer ----------------------------
class ReviewResult(BaseModel):
    status: Literal["APPROVE", "REVISE"] = Field(
        description=(
            "APPROVE only if every rubric check passed AND the draft reads as "
            "a credible, on-brand GammaRips blog post."
        )
    )
    notes: str = Field(
        description="If REVISE, specific fixes the writer must apply. Empty if APPROVE.",
        default="",
    )


# --- Callbacks -------------------------------------------------------------
async def seed_voice_rules(callback_context: CallbackContext) -> None:
    """Load brand voice rules into state before the first agent runs.

    ADK invokes callbacks with keyword arg `callback_context=...`, so the
    parameter name MUST be `callback_context` (not `ctx`). Mismatching the
    name yields TypeError "got an unexpected keyword argument".
    """
    if "voice_rules" not in callback_context.state:
        callback_context.state["voice_rules"] = voice_rules.render_for_prompt()


async def score_rubric_before_reviewer(callback_context: CallbackContext) -> None:
    """Run deterministic rubric check on the current markdown before reviewer LLM reads it.

    Uses blog-mode (is_blog=True) in gammarips_content.compliance, plus the
    blog-specific extras layered in score_blog_rubric (word count, H2 count,
    disclaimer block, internal link, CTA-match-with-schedule).
    """
    markdown = callback_context.state.get("post_markdown", "") or ""
    if not isinstance(markdown, str):
        # Writer may have written structured output; coerce defensively.
        markdown = str(markdown)

    # Belt-and-suspenders: deterministically strip the writer's paraphrased
    # disclaimer trailer and append the canonical blockquote. Gemini drifts
    # on the long literal block; this is the same canonicalize-before-judge
    # pattern x-poster uses for short post disclaimers.
    if markdown.strip():
        canonical = compliance.canonicalize_blog_disclaimer(markdown)
        if canonical != markdown:
            callback_context.state["post_markdown"] = canonical
            markdown = canonical

    # Pull the schedule slot's expected CTA so the rubric can hard-fail
    # writer drift (e.g. `webapp_visit` → `pro_trial`).
    outline = callback_context.state.get("post_outline", {}) or {}
    if isinstance(outline, dict):
        slot = outline.get("schedule_slot") or {}
    else:
        slot = {}
    expected_cta = slot.get("cta") if isinstance(slot, dict) else None

    result = tools.score_blog_rubric(markdown=markdown, expected_cta=expected_cta)
    callback_context.state["rubric_check"] = result


# --- Agent factories --------------------------------------------------------
def create_planner() -> Agent:
    return Agent(
        name="planner",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        description="Gathers context data for the scheduled blog post.",
        instruction="""You are the blog planner for @gammarips.

Slug target: {slug?}

Responsibilities:
1. Call `fetch_next_schedule_slot` (no args) if no specific slug was provided.
   If a slug was provided in session state, call `fetch_schedule_slot_by_slug(slug)`.
   Hold the returned dict — you'll embed it in your `post_outline` output below.
2. Call `fetch_prior_posts(limit=5)` to get titles + slugs + keywords of
   recent published posts for internal-link targets + style continuity.
3. If the schedule_slot's `type` is one of:
     weekly_engine_recap, performance_post, post_mortem, video_demo
   then call `fetch_live_context(post_type=<that type>, scan_date=<today ET>)`.
   If the returned `live_context.status == "blocked"` (closed_trade_count < 30),
   the outline must EXPLICITLY remove any win-rate/P&L claim and label the post
   as structural-only. Do NOT fabricate numbers.
4. Produce the final `post_outline` dict. CRITICAL: embed the raw
   `schedule_slot` and `live_context` tool results as nested keys —
   downstream agents (writer, reviewer) read them from here, not from
   separate state keys.
     {
       "h1": "...",
       "intro_hook": "one-sentence hook (facts, not hype)",
       "sections": [{"h2": "...", "bullets": ["...", "..."]}],   // 3-5 H2s
       "internal_links": [{"anchor": "...", "href": "/blog/<slug>"}],  // 2+
       "methodology_link": {"anchor": "...", "href": "/how-it-works"},
       "closing_cta": "webapp_visit" | "pro_trial" | "starter_trial",
       "target_word_count": 1500,
       "primary_keyword": "...",
       "secondary_keywords": ["...", "..."],
       "schedule_slot": <verbatim dict from fetch_next_schedule_slot or fetch_schedule_slot_by_slug>,
       "live_context": <verbatim dict from fetch_live_context, or null if not called>
     }

Constraints:
- 3-5 H2 sections. Total target 1,200-1,800 words.
- Primary keyword must appear in h1 and intro_hook.
- internal_links must reference real prior-post slugs from fetch_prior_posts
  (or be empty list if no prior posts yet). Planner: prefer 2 internal-link
  slots + 1 methodology-page anchor.
- Do NOT draft markdown — that's the writer's job.
""",
        tools=[
            tools.fetch_next_schedule_slot,
            tools.fetch_schedule_slot_by_slug,
            tools.fetch_prior_posts,
            tools.fetch_live_context,
        ],
        output_key="post_outline",
    )


def create_writer() -> Agent:
    return Agent(
        name="writer",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        description="Drafts the full blog markdown in @gammarips voice.",
        instruction="""You write the full blog post markdown for @gammarips.

Outline: {post_outline}

The outline includes nested `schedule_slot` (the slot the planner picked
from blog_schedule) and `live_context` (live engine numbers, may be null
or status='blocked' when closed_trade_count < 30). Read both from
`post_outline.schedule_slot` and `post_outline.live_context`.

Voice rules:
{voice_rules}

Prior reviewer notes (if this is a revision pass): {review?}

Requirements:
- Emit a YAML front matter block at the very top:
    ---
    title: "..."
    slug: "..."
    description: "< 160 chars, SEO meta"
    keywords: ["primary", "secondary1", "secondary2"]
    cta: "webapp_visit" | "pro_trial" | "starter_trial"
    reading_time_min: 6
    ---
- Single H1 (# ...). 3-5 H2 sections. Use H3 only where it sharpens the outline.
- Target 1,200-1,800 words. Writer: count carefully. Under 1,200 = REVISE.
  Over 1,800 = REVISE.
- Include at LEAST 2 internal links in the form [anchor](/blog/<slug>) using
  the slugs from post_outline.internal_links. Also include at least one
  methodology-page link (`/how-it-works`, `/signals`, or `/about`).
- End with the EXACT literal disclaimer block (inside a blockquote):
    > Paper-trading performance, educational content only. Not investment
    > advice. Past performance is not a guarantee of future results.
- CTA contract — NON-NEGOTIABLE: the front-matter `cta` field MUST equal
  `post_outline.schedule_slot.cta` verbatim. Do NOT substitute. The closing
  paragraph must invite the action implied by THAT exact CTA value:
    * `webapp_visit` → "See today's pick at gammarips.com" tone. NEVER mention
      "Pro Trial", "Starter Trial", "Founder pricing", or any paid tier.
    * `starter_trial` → invite the $19/mo Starter tier specifically. Do NOT
      upsell to Pro.
    * `pro_trial` → invite the Pro tier specifically.
  If the schedule slot says `webapp_visit`, this is a top-of-funnel post —
  drive to the site, NOT to a paid tier.
- Specific dollar amounts and specific times. "$500 per trade", "10:00 AM ET",
  "3 trading days", "-60% / +80%" — not "a lot" or "about $500".
- Publisher framing only. NO "buy this", "act now", "for you", second-person
  imperatives tied to trade timing. Describe the routine, not the reader.

Forbidden (retired aliases — hard-fail if present):
- Ripper / Rippers
- Daily Playbook
- The Overnight Edge (as a product name)
- "@mention" (the literal string — we use "tag the agent" instead)
- "score >= 6"  (old policy — current is V5.4)
- "8:30 AM"    (old time — current is 9:00 AM)
- "$49 / $149" (old pricing)
- "premium signal"
- "interactive dashboard"

If `post_outline.live_context.status == "blocked"`, DO NOT include any
win-rate, closed trades, or P&L numbers. Pivot to structural claims only
(e.g. "max per-trade loss is $300 on a $500 position").

Revision behavior: if `review.notes` is present, treat those notes as hard
constraints and regenerate the full markdown, fixing each specific item.

Output: assign your full markdown string (including front matter) to state
key `post_markdown`.
""",
        output_key="post_markdown",
    )


def create_reviewer() -> Agent:
    return Agent(
        name="reviewer",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        description="Final compliance reviewer — structured APPROVE or REVISE.",
        instruction="""You are the final compliance reviewer for a GammaRips blog post.

Deterministic rubric check (run before you): {rubric_check}
Post outline: {post_outline}
(`post_outline.schedule_slot` carries the slot/cta/type, and
`post_outline.live_context` carries any live engine numbers or block status.)

The rubric_check dict has: passed (bool), word_count, h2_count,
disclaimer_present, internal_link_count, failures[], warnings[].

Decision rules — walk them in order:

1. If rubric_check.passed is False:
     status = REVISE
     notes = bullet list of EACH failure string + the exact fix required.
     Stop here. Do not approve.

2. If rubric_check.passed is True, do a holistic read of the markdown:
     - Does the post ladder to the One Promise: "one options trade a day,
       scored before you wake up, pushed to your phone at 9 AM"?
     - Publisher framing (SEC v. Lowe): no individualized recommendation
       language, no "buy this / act now / for you".
     - Keyword density: primary keyword appears in H1 + first paragraph
       + at least 2 H2s. Not stuffed (< 1.5% density).
     - Retired-alias scan: zero matches for Ripper, Daily Playbook,
       Overnight Edge (as product name), "@mention", "score >= 6",
       "8:30 AM", "$49/$149", "premium signal", "interactive dashboard".
     - Tone: disciplined, numbers-first, short declarative sentences.
     - Disclaimer block present AND unmodified (exact wording from voice_rules).
     - If schedule_slot.type requires live data and live_context is blocked,
       post must NOT claim win rates or P&L.

3. If all holistic checks pass → status = APPROVE, notes = "".
   Otherwise → status = REVISE, notes = specific fixes.

Be strict on rubric failures and retired aliases. Be generous on aesthetic
judgment — it's a 1,500 word post, not a manifesto.
""",
        output_schema=ReviewResult,
        output_key="review",
        before_agent_callback=score_rubric_before_reviewer,
    )


# --- Custom workflow agents ------------------------------------------------
class EscalationChecker(BaseAgent):
    """Stops the LoopAgent only when review.APPROVE AND deterministic rubric passes.

    Defense-in-depth: Gemini occasionally returns APPROVE on the final iteration
    even when `rubric_check.passed` is False (e.g. paraphrased disclaimer
    sneaks through). Trusting the LLM here would publish a non-compliant post.
    Re-check the structured rubric as the actual gate.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        review = ctx.session.state.get("review", {}) or {}
        status = review.get("status") if isinstance(review, dict) else None
        rubric = ctx.session.state.get("rubric_check", {}) or {}
        rubric_passed = bool(rubric.get("passed")) if isinstance(rubric, dict) else False
        # Track iterations for observability (each pass through the loop increments).
        ctx.session.state["iterations"] = ctx.session.state.get("iterations", 0) + 1
        if status == "APPROVE" and rubric_passed:
            logger.info("Reviewer APPROVED + rubric passed — escalating loop exit.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            if status == "APPROVE" and not rubric_passed:
                logger.warning(
                    f"Reviewer APPROVED but rubric FAILED ({rubric.get('failures')}) — "
                    "ignoring approval, continuing loop."
                )
            else:
                logger.info(f"Reviewer returned {status!r} — loop continues.")
            yield Event(author=self.name)


class Publisher(BaseAgent):
    """Runs once after the LoopAgent: Firestore write + schedule update + log.

    On reject (loop exhausted without APPROVE): log_rejected() and surface the
    result to session state so fast_api_app can return the markdown + 500.
    On dry_run: skip Firestore write, just stash the markdown into
    publish_result so the endpoint can return it.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        review = state.get("review", {}) or {}
        markdown = state.get("post_markdown", "") or ""
        outline = state.get("post_outline", {}) or {}
        schedule_slot = state.get("schedule_slot", {}) or {}
        rubric = state.get("rubric_check", {}) or {}
        iterations = int(state.get("iterations", 1) or 1)
        dry_run = bool(state.get("dry_run", False))

        # Resolve slug + metadata (outline is the source; schedule_slot is fallback)
        slug = (
            state.get("slug")
            or (outline.get("slug") if isinstance(outline, dict) else None)
            or schedule_slot.get("slug", "")
        )
        title = (
            (outline.get("h1") if isinstance(outline, dict) else None)
            or schedule_slot.get("title_candidate", "")
        )
        description = (
            (outline.get("description") if isinstance(outline, dict) else None)
            or (schedule_slot.get("description") if isinstance(schedule_slot, dict) else "")
            or ""
        )
        keywords = (
            schedule_slot.get("keywords") if isinstance(schedule_slot, dict) else None
        ) or []
        cta = (
            (outline.get("closing_cta") if isinstance(outline, dict) else None)
            or schedule_slot.get("cta", "webapp_visit")
        )
        # Reviewer score — rubric_check passed? Convert to a pseudo-score for observability.
        reviewer_score = 10.0 if rubric.get("passed") else 0.0

        # Publish gate (mirror EscalationChecker): require BOTH reviewer
        # APPROVE AND deterministic rubric pass. Either side missing →
        # reject and log instead of publishing a non-compliant post.
        review_approved = review.get("status") == "APPROVE"
        rubric_passed = bool(rubric.get("passed"))
        # ADK only persists in-session state via EventActions(state_delta=...).
        # Mutating `state["publish_result"]` directly is invisible to the
        # session_service after the run ends — fast_api_app.get_session would
        # see no publish_result. Always yield a state_delta event.
        if not (review_approved and rubric_passed):
            why = (
                f"review={review.get('status')!r}"
                f" rubric_passed={rubric_passed}"
                f" rubric_failures={rubric.get('failures')}"
            )
            logger.warning(f"Loop ended without clean APPROVE — logging rejected. {why}")
            notes = review.get("notes", "") if isinstance(review, dict) else ""
            if rubric.get("failures"):
                rf = "; ".join(rubric.get("failures", []))
                notes = f"{notes}\n[rubric] {rf}".strip()
            if not dry_run and slug:
                tools.log_rejected(slug=slug, notes=notes)
            rejected = {
                "status": "rejected",
                "slug": slug,
                "iterations": iterations,
                "reviewer_notes": notes,
                "markdown": markdown,
            }
            state["publish_result"] = rejected
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={"publish_result": rejected}),
            )
            return

        # Dry run → do not write to Firestore
        if dry_run:
            dry = {
                "status": "dry_run",
                "slug": slug,
                "markdown": markdown,
                "iterations": iterations,
                "reviewer_score": reviewer_score,
            }
            state["publish_result"] = dry
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={"publish_result": dry}),
            )
            return

        # Happy path — Firestore write.
        publish_out = tools.publish_to_firestore(
            slug=slug,
            title=title,
            description=description,
            markdown=markdown,
            keywords=list(keywords) if keywords else [],
            cta=cta,
            reviewer_score=reviewer_score,
            iterations=iterations,
        )
        published = {
            "status": publish_out.get("status", "unknown"),
            "slug": slug,
            "iterations": iterations,
            "reviewer_score": reviewer_score,
            "error": publish_out.get("message"),
        }
        state["publish_result"] = published
        yield Event(
            author=self.name,
            actions=EventActions(state_delta={"publish_result": published}),
        )


# --- Root pipeline ----------------------------------------------------------
def build_root_agent() -> BaseAgent:
    loop = LoopAgent(
        name="draft_review_loop",
        sub_agents=[
            create_planner(),
            create_writer(),
            create_reviewer(),
            EscalationChecker(name="escalation_checker"),
        ],
        max_iterations=3,
    )
    return SequentialAgent(
        name="blog_generator_pipeline",
        sub_agents=[loop, Publisher(name="publisher")],
        before_agent_callback=seed_voice_rules,
    )


root_agent = build_root_agent()

app = App(
    root_agent=root_agent,
    name="blog_generator",
)
