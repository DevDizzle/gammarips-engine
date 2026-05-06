# ruff: noqa
"""
x-poster — ADK multi-agent pipeline for @gammarips X publishing.

Pipeline:
    SequentialAgent
      ├── LoopAgent (max 3 iterations)
      │    ├── Planner     — gathers context via fetch_* tools
      │    ├── Writer      — drafts tweet text + image prompt in brand voice
      │    ├── Reviewer    — structured APPROVE/REVISE (Pydantic)
      │    └── EscalationChecker — escalates the loop when APPROVED
      └── Publisher        — image gen → post to X → Firestore log

State keys across the pipeline:
    post_type, scan_date, voice_rules, post_brief, post_draft, rubric_check, review, publish_result
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

MODEL = "gemini-3-flash-preview"


# --- Structured output schema for the reviewer ----------------------------
class ReviewResult(BaseModel):
    status: Literal["APPROVE", "REVISE"] = Field(
        description="APPROVE only if every rubric check passed AND the draft reads cleanly in brand voice."
    )
    notes: str = Field(
        description="If REVISE, specific fixes the writer must apply. Empty if APPROVE.",
        default="",
    )


# --- Helpers ---------------------------------------------------------------
def _coerce_draft(raw) -> dict:
    """Writer has no output_schema, so post_draft may arrive as a raw string.

    Try to extract a dict: parse JSON, fall back to fenced-JSON, else wrap the
    string as {"text": raw}. Publisher logic downstream expects .get()-able.
    """
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    import json
    import re

    s = raw.strip()
    # Try straight JSON
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict):
            return parsed
    except Exception:  # noqa: BLE001
        pass
    # Try fenced json ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(1))
            if isinstance(parsed, dict):
                return parsed
        except Exception:  # noqa: BLE001
            pass
    # Last resort — treat raw string as the tweet body.
    return {"text": s}


# --- Callbacks -------------------------------------------------------------
async def seed_voice_rules(callback_context: CallbackContext) -> None:
    """Load brand voice rules into state before the first agent runs."""
    if "voice_rules" not in callback_context.state:
        callback_context.state["voice_rules"] = voice_rules.render_for_prompt()


async def score_rubric_before_reviewer(callback_context: CallbackContext) -> None:
    """Canonicalize the draft THEN run rubric scoring. Reviewer judges the
    final canonical text, not the writer's potentially-drifted output.

    This is the belt (canonicalize before reviewer) + suspenders (canonicalize
    again in Publisher is fine — it's idempotent) pattern. Reviewer can no
    longer REVISE for disclaimer paraphrasing, $SPY filler, or V/OI None —
    those drift modes are already stripped by the time it reads the text.
    """
    draft = _coerce_draft(callback_context.state.get("post_draft", {}))
    raw_text = draft.get("text", "")
    post_type = callback_context.state.get("post_type", "signal")

    # Canonicalize FIRST so every downstream consumer sees the final text.
    canonical_text = compliance.canonicalize_draft_text(raw_text, post_type)
    draft["text"] = canonical_text
    callback_context.state["post_draft"] = draft

    image_url = draft.get("image_url")
    result = compliance.score_against_rubric(canonical_text, post_type, image_url=image_url)
    callback_context.state["rubric_check"] = {
        "passed": result.passed,
        "char_count": result.char_count,
        "char_budget": result.char_budget,
        "failures": result.failures,
        "warnings": result.warnings,
        "notes": compliance.rubric_to_reviewer_notes(result),
    }


# --- Agent factories --------------------------------------------------------
def create_planner() -> Agent:
    return Agent(
        name="planner",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        description="Gathers context data for the scheduled X post.",
        instruction="""You plan an X post for @gammarips. Your ONLY job is to gather data via tools and output a structured brief. You do NOT invent tickers, dates, or numbers.

Post type: {post_type}
Scan date: {scan_date}   ← this is today's ET date, also the header date for the post.

=== STEP 1: Call the right tools for this post_type ===
- signal: fetch_todays_pick(scan_date)
- standby: fetch_todays_pick(scan_date)  — expected to return status=empty; that's normal
- watchlist: FIRST fetch_todays_pick(scan_date) to learn the paid daily-pick ticker (if any). THEN call fetch_watchlist(scan_date, n=3, exclude_ticker=<pick.ticker or "">). Watchlist surfaces popular flow magnets ranked by dollar volume — NOT the paid V5.3 pick. If fetch_watchlist returns empty, leave brief.watchlist=[] — the publisher will skip.
- teaser: FIRST fetch_todays_pick(scan_date) to learn today's daily-pick ticker (if any), THEN call fetch_runner_ups(scan_date, n=3, exclude_ticker=<pick.ticker or "">). The teaser must show OTHER setups on the bench, not duplicate the SIGNAL post. If runner_ups returns an empty list, leave brief.runner_ups=[] — the publisher will skip.
- report: fetch_todays_report_summary(scan_date)
- callback (wins/losses): FIRST call fetch_recently_posted_tickers(scan_date, lookback_days=5) to learn which tickers we've publicly named (callbacks should ONLY discuss tickers the X audience has seen). THEN call fetch_closing_trades(scan_date, restrict_tickers=<comma-joined ticker list>). For each closing trade in the result, call find_originating_post_for_ticker(ticker) to get the QRT id for win posts.
- scorecard: FIRST call fetch_recently_posted_tickers(scan_date, lookback_days=10) — the public scorecard recaps ONLY trades on tickers the audience has publicly seen us name. THEN call fetch_weekly_ledger(week_ending=scan_date, restrict_tickers=<comma-joined ticker list>). Pass result.data through verbatim — items already include outcome_emoji, direction_short, pct_signed.

=== STEP 2: Output post_brief as a JSON dict ===

Anti-hallucination rules (NON-NEGOTIABLE):
- If a tool returned status="empty", DO NOT invent fictional data. Set the relevant field to null.
- If a tool returned no ticker at all, DO NOT mention any ticker in the brief.
- NEVER reference $SPY, $QQQ, or any index ticker unless it literally appears in a tool result.
- Dates in the brief must come from tool results OR equal {scan_date}. No other dates.

Required keys in post_brief:
- pick: null if no daily pick today. Otherwise a dict with: ticker, direction (BULLISH|BEARISH), score, contract_type (CALL|PUT, derived from direction), strike, expiration (YYYY-MM-DD), mid, moneyness_pct, vol_oi, dte.
- runner_ups: list of {ticker, direction, score, vol_oi} — only populated for teaser post_type; else [].
- report_summary: {title, headline, top_bullets} — only for report post_type; else null.
- watchlist: list of {ticker, direction, score, dollar_vol_m, vol_oi_ratio} — only populated for watchlist post_type; else [].
- closing_trades: {wins: [...], losses: [...], total: N} — only for callback; else null. Each item already includes ticker, direction, entry_date, entry_price, exit_price, pct_signed (e.g. "+80%"), exit_reason_display (e.g. "target hit"). Pass them through to the writer verbatim — DO NOT re-derive percentages.
- weekly_ledger: {trades: [...], wins, losses, net_return_pct} — only for scorecard; else null. Each trade item already includes outcome_emoji ("✅"/"❌"), direction_short ("BULL"/"BEAR"), pct_signed ("+80%"/"-60%"). Pass them through verbatim — DO NOT re-derive.
- qrt_tweet_id: tweet_id of the original call being QRT'd (callback post_type only); else null.
- image_direction: 1-2 sentences describing what the post card image should show (for the writer to refine).

DO NOT draft the tweet text. The writer handles formatting.""",
        tools=[
            tools.fetch_todays_pick,
            tools.fetch_todays_report_summary,
            tools.fetch_closing_trades,
            tools.fetch_runner_ups,
            tools.fetch_watchlist,
            tools.fetch_recently_posted_tickers,
            tools.fetch_original_tweet_id,
            tools.find_originating_post_for_ticker,
            tools.fetch_weekly_ledger,
        ],
        output_key="post_brief",
    )


def create_writer() -> Agent:
    return Agent(
        name="writer",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        description="Drafts the X post text in @gammarips premium format.",
        instruction="""You draft an X post for @gammarips. You fill in the correct template below using ONLY fields from {post_brief}. You invent nothing.

Post type: {post_type}
Scan date (use in header): {scan_date}
Brief: {post_brief}

Voice rules:
{voice_rules}

Prior reviewer notes: {review?}

=== RULES ===
1. Pick the template that matches {post_type} and fill it in EXACTLY. Preserve emoji, punctuation, line breaks.
2. Use {scan_date} in the header. NEVER substitute any other date.
3. NEVER include a ticker that is not in the brief. If brief.pick is null for post_type=signal, switch to the STANDBY template — and the STANDBY template has NO ticker anywhere. Do NOT append "($SPY)" or "$SPY flow" or any index ticker as filler. Empty is empty.
4. Disclaimer rule (Evan 2026-04-28): ONLY win / loss / callback / scorecard end with `⚠️ Paper-trade. Not advice.` (exact characters, no paraphrasing). signal / standby / teaser / report ship WITHOUT any disclaimer line — the canonicalizer strips disclaimer-ish trailers for those types.
5. Never include hashtags. Never use "buy", "sell", "act now", "for you". The ONLY URL allowed in any tweet body is the canonical report click-through `https://gammarips.com/reports/<scan_date>` — and only on REPORT post_type per the template below. No other URLs anywhere.
6. mid_total_cost = round(mid * 100). Format with comma thousands: `$2,693`.
7. contract_emoji: 📗 for CALL (BULLISH), 📕 for PUT (BEARISH).
8. expiration_display: convert YYYY-MM-DD to "Mon DD" (e.g., "2026-05-15" → "May 15").
9. Slots in the templates below are written as <slot_name>. Replace each <slot_name> with the corresponding value from the brief. The literal tokens {post_type}, {scan_date}, {post_brief}, {voice_rules} at the top of this prompt are already resolved — do NOT repeat them as braces in the output; use the values directly.
10. FORBIDDEN additions regardless of instinct: do NOT prepend/append generic tickers ($SPY, $QQQ, $IWM, $DIA) to soften an empty state. Do NOT add commentary like "Markets held flat" or "Flow was muted" unless that sentence comes verbatim from a tool result. If you would normally "fill in" a quiet day with context, STOP and just ship the STANDBY template verbatim.
11. If {post_type} is explicitly "standby", ALWAYS use the STANDBY template — ignore any pick data in brief.pick even if it's non-null. Standby is a caller assertion.
11b. If {post_type} is explicitly "watchlist", ALWAYS use the WATCHLIST template. brief.pick is fetched ONLY so the planner could exclude the paid daily pick from the watchlist; do NOT render brief.pick on the watchlist post — that would re-leak the paid alpha. Render only brief.watchlist[].
12. For TEASER runner-ups: if a runner-up's vol_oi is null / None / missing, OMIT the `V/OI <x>` segment for that row entirely. Render that row as `$<ticker> <emoji> <direction> — Score <score>` instead (drop the V/OI column, keep the Score column). Never print the literal string `V/OI None`.
13. Round all V/OI values to 2 decimal places: `V/OI: 7.33`, not `V/OI: 7.3333`.

=== TEMPLATES (fill <slot> placeholders from brief; drop lines whose data is missing) ===

--- SIGNAL (when brief.pick is not null) ---
🔥 GammaRips Signal — <scan_date>

$<ticker> <direction> (Score: <score>)
<contract_emoji> <contract_type> $<strike> | Exp: <expiration_display>
💰 Mid: $<mid> (~$<mid_total_cost>/contract) | <moneyness_pct>% OTM
📊 V/OI: <vol_oi> | DTE: <dte> | V5_3_TARGET_80

--- STANDBY (when brief.pick is null for a signal post_type, OR post_type=standby) ---
🛑 GammaRips Standby — <scan_date>

No V5.3 signal cleared the gate stack overnight.
Scanner saw flow. Nothing met our thresholds.
Zero picks is a pick.

--- WATCHLIST (3 high-dollar-volume setups; NO contract details, NO entry/exit. Discovery-only.) ---
Render brief.watchlist[0..2]. emoji: 📗 BULL → CALL, 📕 BEAR → PUT.
direction_label: BULL or BEAR (5 chars). Round dollar_vol_m to 1 decimal: "$167M".

📡 Today's flow magnets — <scan_date>

$<t1_ticker> <t1_emoji> <t1_direction_label> — Score <t1_score> | $<t1_dollar_vol_m>M flow
$<t2_ticker> <t2_emoji> <t2_direction_label> — Score <t2_score> | $<t2_dollar_vol_m>M flow
$<t3_ticker> <t3_emoji> <t3_direction_label> — Score <t3_score> | $<t3_dollar_vol_m>M flow

Curated daily pick → email subscribers only.

--- TEASER (runner-ups — NO entry/exit, this is the key differentiator vs signal) ---
📡 Overnight flow — <scan_date>

<N> runner-ups on our bench today:
$<t1_ticker> <t1_emoji> <t1_direction> — V/OI <t1_voi> | Score <t1_score>
$<t2_ticker> <t2_emoji> <t2_direction> — V/OI <t2_voi> | Score <t2_score>
$<t3_ticker> <t3_emoji> <t3_direction> — V/OI <t3_voi> | Score <t3_score>

One fires the daily pick. Rest sit on the bench.

--- REPORT (morning overnight brief compressed) ---
📝 Overnight Brief — <scan_date>

<one-sentence theme from brief.report_summary.headline>
• <bullet_1>
• <bullet_2>

🔗 https://gammarips.com/reports/<scan_date>

--- WIN (callback when brief.closing_trades.wins is non-empty; QRT brief.qrt_tweet_id if present) ---
Pull the FIRST item from brief.closing_trades.wins and render:

✅ CALLED IT — <pct_signed> on $<ticker> <direction>

Entry: $<entry_price> mid (<entry_date>)
Exit: $<exit_price> (<scan_date>, <exit_reason_display>)

⚠️ Paper-trade. Not advice.

--- LOSS (callback when brief.closing_trades.wins is empty AND brief.closing_trades.losses is non-empty; NEUTRAL single — no QRT, no defensive commentary) ---
Pull the FIRST item from brief.closing_trades.losses and render:

❌ STOPPED OUT — <pct_signed> on $<ticker> <direction>

Entry: $<entry_price> (<entry_date>)
Exit: $<exit_price> (<scan_date>, <exit_reason_display>)

Trade the system, not the pick.

⚠️ Paper-trade. Not advice.

--- SCORECARD (Fridays only, single tweet) ---
N = brief.weekly_ledger.trades.length. wins = brief.weekly_ledger.wins.
For each trade in brief.weekly_ledger.trades render one line VERBATIM from the brief:
  "<trade.outcome_emoji> $<trade.ticker> <trade.direction_short> <trade.pct_signed>"

📊 Week ending <scan_date>

<N> trades closed:
<line for each trade>

<wins> of <N> wins. Net: <net_return_pct>% across all trades.

⚠️ Paper-trade. Not advice.

=== OUTPUT ===
Return a JSON dict with EXACTLY these keys:
{
  "text": "<the rendered tweet template>",
  "qrt_tweet_id": <pass through brief.qrt_tweet_id, or null>,
  "in_reply_to_tweet_id": null,
  "ticker": "<TICKER without $ — for signal/win/loss only; null otherwise>",
  "direction": "<BULLISH or BEARISH — for signal/win/loss only; null otherwise>"
}

Posts ship text-only — no image_prompt is required. The `ticker` / `direction`
fields are kept for downstream logging only.

Char budgets (hard): signal=400, standby=280, teaser=300, report=280, win=200, loss=200, scorecard=400.""",
        output_key="post_draft",
    )


def create_reviewer() -> Agent:
    return Agent(
        name="reviewer",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        description="Final compliance reviewer — structured APPROVE or REVISE.",
        instruction="""You are the final compliance reviewer for @gammarips X posts.

The draft you see has ALREADY been canonicalized — disclaimer drift, $SPY/$QQQ/$IWM/$DIA filler, V/OI None segments, and disclaimer paraphrasing are all deterministically stripped before you read it. Do NOT REVISE for any of those — they are already fixed.

Draft: {post_draft}
Deterministic rubric check: {rubric_check}
Post type: {post_type}

Decision rules:
1. If rubric_check.passed is False → status=REVISE, notes=<specific failures + exact fixes>.
2. If rubric_check.passed is True, do a light holistic read:
   - Tone matches voice rules?
   - Content coherent and non-robotic?
   - If post_type is signal/teaser/win/loss/scorecard: cashtag ($TICKER) present somewhere?
   - image_prompt coherent with text?
3. If all good → status=APPROVE, notes="".

SPECIAL CASES — do NOT REVISE for these; they are correct:
- **post_type=standby**: The post has NO ticker and NO cashtag BY DESIGN. That is correct. Do NOT demand a cashtag. The caller explicitly requested standby — honor it regardless of whether underlying pick data exists.
- **post_type=report**: May or may not include a cashtag depending on market theme. Either is fine.
- **Disclaimer wording**: ONLY win/loss/callback/scorecard end with `⚠️ Paper-trade. Not advice.` (the canonicalizer enforces it). signal/standby/teaser/report ship WITHOUT a disclaimer — do NOT REVISE for missing disclaimer on those types.
- **No hashtags**: # anything in the body is wrong. We never use hashtags on X.

Be generous on aesthetic judgment. Lean APPROVE. Only REVISE for concrete rubric failures or actual voice/clarity issues. You are not a thesaurus.""",
        output_schema=ReviewResult,
        output_key="review",
        before_agent_callback=score_rubric_before_reviewer,
    )


# --- Custom workflow agents ------------------------------------------------
class EscalationChecker(BaseAgent):
    """Stops the LoopAgent when review.status == APPROVE."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        review = ctx.session.state.get("review", {}) or {}
        status = review.get("status") if isinstance(review, dict) else None
        if status == "APPROVE":
            logger.info("Reviewer APPROVED — escalating loop exit.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logger.info(f"Reviewer returned {status!r} — loop continues.")
            yield Event(author=self.name)


class Publisher(BaseAgent):
    """Runs once after the LoopAgent: image gen → X post → Firestore log."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        scan_date = state.get("scan_date", "") or tools.today_et_iso()
        post_type = state.get("post_type", "")
        review_raw = state.get("review", {})
        draft_raw = state.get("post_draft", {})
        # Writer has no output_schema; its output may come through as a raw string.
        # Parse to dict defensively so Publisher never crashes on shape.
        review = review_raw if isinstance(review_raw, dict) else {}
        draft = _coerce_draft(draft_raw)

        # No-content guard for callback: paper-trader writes exits at 16:30 ET,
        # callback fires at 16:45 ET. If the ledger has zero closes for today,
        # skip publishing entirely — never post an empty "called it" recap.
        # Detected via writer setting ticker=null (writer routes win/loss based
        # on closing_trades being non-empty).
        if post_type == "callback":
            draft_for_check = _coerce_draft(draft_raw)
            if not (draft_for_check.get("ticker") or "").strip():
                logger.info("callback fired but no closes today — skipping publish.")
                tools.log_post(
                    scan_date=scan_date, post_type=post_type,
                    text="", tweet_id=None, iterations=0,
                    error="no_closes_today",
                )
                noop = {"status": "skipped", "reason": "no_closes_today"}
                state["publish_result"] = noop
                yield Event(
                    author=self.name,
                    actions=EventActions(state_delta={"publish_result": noop}),
                )
                return

        # No-content guard for teaser: when the enrichment gate stack only
        # passes one signal (the daily pick), runner_ups after exclusion is
        # empty. Without this, the writer drifts to a 0/1-row teaser that
        # duplicates the SIGNAL post — exactly the MDB 2026-04-29 incident.
        if post_type == "teaser":
            brief = state.get("post_brief", {}) or {}
            runner_ups = brief.get("runner_ups") if isinstance(brief, dict) else None
            if not runner_ups:
                logger.info("teaser fired but no runner-ups today — skipping publish.")
                tools.log_post(
                    scan_date=scan_date, post_type=post_type,
                    text="", tweet_id=None, iterations=0,
                    error="no_runners_today",
                )
                noop = {"status": "skipped", "reason": "no_runners_today"}
                state["publish_result"] = noop
                yield Event(
                    author=self.name,
                    actions=EventActions(state_delta={"publish_result": noop}),
                )
                return

        # No-content guard for scorecard: when no trades on publicly-named
        # tickers closed this week, skip rather than post an empty thread.
        # First real-fire window is post-watchlist-launch (5/8 onward) — until
        # then the public ledger restricts to ~0 rows.
        if post_type == "scorecard":
            brief = state.get("post_brief", {}) or {}
            wl = brief.get("weekly_ledger") if isinstance(brief, dict) else None
            trades = (wl or {}).get("trades") if isinstance(wl, dict) else None
            if not trades:
                logger.info("scorecard fired but no posted-ticker closes this week — skipping publish.")
                tools.log_post(
                    scan_date=scan_date, post_type=post_type,
                    text="", tweet_id=None, iterations=0,
                    error="no_scorecard_trades",
                )
                noop = {"status": "skipped", "reason": "no_scorecard_trades"}
                state["publish_result"] = noop
                yield Event(
                    author=self.name,
                    actions=EventActions(state_delta={"publish_result": noop}),
                )
                return

        # No-content guard for watchlist: same shape as teaser. If enrichment
        # only emitted the paid pick (or nothing), the discovery feed has
        # nothing to surface — skip rather than render an empty card.
        if post_type == "watchlist":
            brief = state.get("post_brief", {}) or {}
            wl = brief.get("watchlist") if isinstance(brief, dict) else None
            if not wl:
                logger.info("watchlist fired but no setups today — skipping publish.")
                tools.log_post(
                    scan_date=scan_date, post_type=post_type,
                    text="", tweet_id=None, iterations=0,
                    error="no_watchlist_today",
                )
                noop = {"status": "skipped", "reason": "no_watchlist_today"}
                state["publish_result"] = noop
                yield Event(
                    author=self.name,
                    actions=EventActions(state_delta={"publish_result": noop}),
                )
                return

        # No-content guard for report: 8:30 ET cron fires before
        # overnight-report-generator may have written today's report doc, or
        # the doc exists but is empty. Without this, the writer drifts to
        # the STANDBY template and we get a duplicate Standby on the feed
        # (Evan 2026-04-28 incident). Detect via empty post_brief.report_summary.
        if post_type == "report":
            brief = state.get("post_brief", {}) or {}
            if isinstance(brief, dict):
                summary = brief.get("report_summary")
            else:
                summary = None
            has_summary = bool(summary) and bool(
                (summary.get("headline") or "").strip()
                if isinstance(summary, dict) else False
            )
            if not has_summary:
                logger.info("report fired but no overnight report content — skipping publish.")
                tools.log_post(
                    scan_date=scan_date, post_type=post_type,
                    text="", tweet_id=None, iterations=0,
                    error="no_report_today",
                )
                noop = {"status": "skipped", "reason": "no_report_today"}
                state["publish_result"] = noop
                yield Event(
                    author=self.name,
                    actions=EventActions(state_delta={"publish_result": noop}),
                )
                return

        # Loop exhausted without APPROVE → log rejection
        if review.get("status") != "APPROVE":
            logger.warning("Loop ended without APPROVE — logging rejected.")
            tools.log_post(
                scan_date=scan_date, post_type=post_type,
                text=draft.get("text", ""),
                tweet_id=None, iterations=3,
                error=f"loop_limit_hit: {review.get('notes', '')}",
            )
            rejected = {"status": "rejected", "error": "loop_limit"}
            state["publish_result"] = rejected
            yield Event(
                author=self.name,
                actions=EventActions(state_delta={"publish_result": rejected}),
            )
            return

        # Happy path — canonicalize the draft BEFORE publish/log.
        # Deterministic guards: disclaimer lock (performance posts only),
        # $SPY-filler strip on standby, V/OI None suppression.
        raw_text = draft.get("text", "")
        text = compliance.canonicalize_draft_text(raw_text, post_type)
        qrt_id = draft.get("qrt_tweet_id") or None
        reply_id = draft.get("in_reply_to_tweet_id") or None

        # Text-only posts (Evan 2026-04-28). Editorial images were retired —
        # tweet copy carries the data and the PIL ticker overlays didn't read
        # well in-feed. No image_bytes is ever passed to publish_to_x now.
        post_result = tools.publish_to_x(
            text=text,
            image_bytes=None,
            quote_tweet_id=qrt_id,
            in_reply_to_tweet_id=reply_id,
        )

        # Log
        tools.log_post(
            scan_date=scan_date, post_type=post_type, text=text,
            tweet_id=post_result.get("tweet_id"),
            iterations=1,  # TODO(future): thread through actual loop count
            error=post_result.get("error"),
            dry_run=post_result.get("dry_run", False),
        )
        state["publish_result"] = post_result
        yield Event(
            author=self.name,
            actions=EventActions(state_delta={"publish_result": post_result}),
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
        name="x_poster_pipeline",
        sub_agents=[loop, Publisher(name="publisher")],
        before_agent_callback=seed_voice_rules,
    )


root_agent = build_root_agent()

app = App(
    root_agent=root_agent,
    name="x_poster",
)
