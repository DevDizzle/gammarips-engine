"""
Deterministic compliance rubric for GammaRips published content.

Every published post (X or blog) is scored here by a tool call from the
reviewer agent. The LLM reviewer does a holistic read; this module does
the hard-line checks that should never pass a regression.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from .voice_rules import (
    BANNED_RECOMMENDATION_PHRASES,
    DISCLAIMER_REQUIRED_TOKENS,
    RETIRED_ALIASES,
)


# Char budgets by post_type. @gammarips has blue check → 400-char single-tweet budget.
CHAR_BUDGETS: dict[str, int] = {
    "signal": 400,
    "standby": 280,
    "watchlist": 380, # 3 ticker lines + header + footer
    "report": 360,    # Trailing report URL eats ~50 chars
    "teaser": 300,
    "win": 240,       # QRT quote is short — original tweet provides context
    "loss": 240,      # Neutral single, per X research — no QRT
    "scorecard": 400, # Per tweet in the 3-tweet thread
    "blog": 2_000_000,  # Effectively unbounded for blog markdown
}


# Posts that REQUIRE an image to ship. Editorial images were retired
# 2026-04-28 (Evan) — every post now ships text-only.
IMAGE_REQUIRED: frozenset[str] = frozenset()


# Posts where cashtag-at-pos-0 is exempt (e.g. loss singles that lead with "Stopped").
CASHTAG_RULE_EXEMPT: frozenset[str] = frozenset({"loss", "report", "scorecard"})


# Posts that require the Paper-trade disclaimer. Only trade-performance recaps
# carry the disclaimer (Evan 2026-04-28). signal/standby/teaser/report ship
# without — they describe upcoming setups, not realized results.
DISCLAIMER_REQUIRED: frozenset[str] = frozenset(
    {"win", "loss", "callback", "scorecard"}
)


URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)
# Whitelisted URLs allowed in tweet bodies:
#   1. Per-day report click-through: https://gammarips.com/reports/<YYYY-MM-DD>
#   2. Site root for sub-conversion on signal posts (Path B anchor model).
ALLOWED_URL_PATTERN = re.compile(
    r"https://gammarips\.com(?:/reports/\d{4}-\d{2}-\d{2}|/?)\b"
)
CASHTAG_PATTERN = re.compile(r"\$[A-Z]{1,5}\b")


@dataclass
class RubricResult:
    """Structured rubric output. `passed=True` only if every check passed."""

    passed: bool
    char_count: int
    char_budget: int
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def score_against_rubric(
    text: str,
    post_type: str,
    image_url: str | None = None,
    is_blog: bool = False,
) -> RubricResult:
    """Apply all 6 hard-line rubric checks. Return structured result.

    Args:
        text: The post body (or single tweet in a thread; score each tweet separately).
        post_type: One of the keys in CHAR_BUDGETS.
        image_url: URL of the attached image, if any. None if text-only.
        is_blog: If True, skip char budget + cashtag + URL checks (blog posts link + long).

    Returns:
        RubricResult with passed=True only if every check passes.
    """
    failures: list[str] = []
    warnings: list[str] = []
    char_count = len(text)
    char_budget = CHAR_BUDGETS.get(post_type, 280)

    # 1. Char budget
    if not is_blog and char_count > char_budget:
        failures.append(
            f"char_budget: {char_count} > {char_budget} ({post_type})"
        )

    # 2. Retired-alias scan (case-insensitive)
    text_lower = text.lower()
    for alias in RETIRED_ALIASES:
        if alias.lower() in text_lower:
            failures.append(f"retired_alias: '{alias}'")

    # 3. Disclaimer present (case-sensitive — canonical form).
    # Only required on trade-performance posts (Evan 2026-04-28).
    if not is_blog and post_type in DISCLAIMER_REQUIRED:
        missing = [t for t in DISCLAIMER_REQUIRED_TOKENS if t not in text]
        if missing:
            failures.append(f"disclaimer_missing: {missing}")
    # Blog posts have their own longer disclaimer block — checked separately

    # 4. Publisher framing (case-insensitive)
    for phrase in BANNED_RECOMMENDATION_PHRASES:
        if phrase.lower() in text_lower:
            failures.append(f"banned_phrase: '{phrase}'")

    # 5. Cashtag position (≤ char 80)
    if not is_blog and post_type not in CASHTAG_RULE_EXEMPT:
        match = CASHTAG_PATTERN.search(text)
        if match is None:
            failures.append("cashtag_absent")
        elif match.start() > 80:
            failures.append(
                f"cashtag_below_fold: position {match.start()} > 80"
            )

    # 6. URL absence (body-of-tweet — blog allows URLs).
    # The canonical gammarips.com/reports/<date> link is whitelisted on
    # report/signal posts as a click-through to the full brief. Strip it
    # before checking so accidental other URLs still fail.
    if not is_blog:
        text_for_url_check = ALLOWED_URL_PATTERN.sub("", text)
        if URL_PATTERN.search(text_for_url_check):
            failures.append("url_in_body")

    # Image requirement (non-failing warning if missing when required)
    if post_type in IMAGE_REQUIRED and not image_url:
        warnings.append(f"image_required_for_{post_type}_but_absent")

    return RubricResult(
        passed=not failures,
        char_count=char_count,
        char_budget=char_budget,
        failures=failures,
        warnings=warnings,
    )


def rubric_to_reviewer_notes(result: RubricResult) -> str:
    """Format rubric result for the reviewer agent's prompt context."""
    if result.passed and not result.warnings:
        return f"RUBRIC: all 6 checks passed ({result.char_count}/{result.char_budget} chars)."
    lines = [f"RUBRIC: {result.char_count}/{result.char_budget} chars."]
    if result.failures:
        lines.append("FAILURES:")
        lines += [f"  - {f}" for f in result.failures]
    if result.warnings:
        lines.append("WARNINGS:")
        lines += [f"  - {w}" for w in result.warnings]
    return "\n".join(lines)


# --- Deterministic canonicalization -----------------------------------------
# The LLM writer paraphrases disclaimers and injects index tickers as filler
# despite prompt rules. We enforce the canonical form deterministically after
# the writer returns, before compliance re-check and publish. This is the
# "belt and suspenders" layer — LLM flexibility with hard guarantees.

DISCLAIMER_CANONICAL_LONG = "⚠️ Paper-trade. Not financial advice."
DISCLAIMER_CANONICAL_SHORT = "⚠️ Paper-trade. Not advice."

# Which disclaimer each post_type uses (Evan 2026-04-28 decision):
# Only trade-performance recaps carry a disclaimer. Forward-looking posts
# (signal / standby / teaser / report) ship without one.
_DISCLAIMER_BY_POST_TYPE: dict[str, str] = {
    "win":       DISCLAIMER_CANONICAL_SHORT,
    "loss":      DISCLAIMER_CANONICAL_SHORT,
    "callback":  DISCLAIMER_CANONICAL_SHORT,   # win/loss routed via callback
    "scorecard": DISCLAIMER_CANONICAL_SHORT,
}

_DISCLAIMER_LINE = re.compile(
    r"^\s*(?:⚠️\s*)?(?:paper[-\s]?trade|not\s+(?:financial\s+)?advice|not\s+a\s+recommendation)"
    r"[^\n]*$",
    re.IGNORECASE,
)
_INDEX_FILLER_IN_HEADER = re.compile(
    r"\s*\(?\s*\$(?:SPY|QQQ|IWM|DIA)\b\s*\)?",
    re.IGNORECASE,
)
_NULL_VOI_SEGMENT = re.compile(
    r"\s*[—\-–|•]\s*V/OI:?\s*(?:None|null|N/A)\s*(?=\s*[—\-–|•]|\s*$)",
    re.IGNORECASE,
)
_STRAY_DIVIDERS = re.compile(r"(?:\s*[—\-–]\s*\|)|(?:\|\s*[—\-–])")


def _enforce_one_cashtag(text: str) -> str:
    """Keep the first cashtag, strip the leading `$` from any subsequent ones.

    X Free tier rejects posts with >1 cashtag (`Posts are limited to a maximum
    of one cashtag ($SYMBOL)`). Watchlist/teaser/scorecard/callback templates
    legitimately reference multiple tickers, so we keep the first as a real
    cashtag (preserves discoverability + rubric `cashtag_absent` check) and
    render the rest as plain text.
    """
    seen = False

    def _sub(m: re.Match[str]) -> str:
        nonlocal seen
        if not seen:
            seen = True
            return m.group(0)
        return m.group(0)[1:]  # drop the `$`

    return CASHTAG_PATTERN.sub(_sub, text)


_BLOG_DISCLAIMER_CANONICAL = (
    "> Paper-trading performance, educational content only. Not investment "
    "advice. Past performance is not a guarantee of future results."
)

# Match a trailing disclaimer-ish block (one or more lines that look like a
# disclaimer / publisher carve-out / risk warning), regardless of blockquote.
# Greedy backwards from end of doc until we hit content that is clearly not
# a disclaimer line.
_BLOG_DISCLAIMER_LINE_RE = re.compile(
    r"^\s*(?:>\s*)?(?:"
    r"paper[-\s]?trad(?:e|ing)|"
    r"not\s+(?:investment\s+|financial\s+)?advice|"
    r"not\s+a\s+recommendation|"
    r"past\s+performance|"
    r"(?:gammarips|the\s+publisher).+(?:not\s+an?\s+(?:investment\s+)?advisor|publisher)|"
    r"options\s+involve\s+risk|"
    r"educational\s+content|"
    r"trades?\s+are\s+based\s+on\s+(?:historical|backtesting|paper)|"
    r"results?\s+do\s+not\s+guarantee"
    r")[^\n]*$",
    re.IGNORECASE,
)


_BLOG_DISCLAIMER_TRIGGER_RE = re.compile(
    r"\b(?:"
    r"paper[-\s]?trad(?:e|ing)|"
    r"not\s+(?:investment|financial)?\s*advice|"
    r"not\s+a\s+recommendation|"
    r"past\s+performance|"
    r"options\s+involve\s+risk|"
    r"educational\s+content|"
    r"gammarips\s+is\s+a\s+publisher|"
    r"results?\s+do\s+not\s+guarantee|"
    r"guarantee\s+of\s+future\s+results|"
    r"backtesting|"
    r"trades?\s+are\s+based\s+on\s+(?:historical|paper)"
    r")\b",
    re.IGNORECASE,
)


def canonicalize_blog_disclaimer(markdown: str) -> str:
    """Strip any writer-paraphrased disclaimer trailer and append the canonical block.

    Gemini drifts on long literal blocks: the writer is told to emit the EXACT
    blockquote disclaimer, but it paraphrases or splits the quote across lines
    in ways that defeat substring matching. We deterministically locate the
    trailing disclaimer block (contiguous blockquote lines OR contiguous lines
    matching disclaimer triggers, with intervening blanks allowed), strip it,
    and append the canonical blockquote.

    Strategy:
      1. Trim trailing blanks.
      2. Walk back collecting a candidate "trailer block": consume any line
         that is (a) a blockquote `>` line, (b) matches a disclaimer trigger
         anywhere in it, or (c) is blank between two collected lines. Stop at
         the first prose line that is neither blockquote nor trigger.
      3. If the candidate trailer contained any disclaimer-trigger line,
         drop the trailer entirely.
      4. Append the canonical blockquote.

    The closing CTA paragraph (regular prose) is preserved — only the trailing
    disclaimer block is removed.
    """
    if not markdown:
        return markdown
    lines = markdown.splitlines()
    end = len(lines)
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    if end == 0:
        return f"{markdown.rstrip()}\n\n{_BLOG_DISCLAIMER_CANONICAL}\n"

    block_start = end
    saw_trigger = False
    while block_start > 0:
        line = lines[block_start - 1]
        stripped = line.strip()
        if not stripped:
            # Blank line: include only if there's already a collected line
            # below it (otherwise it's the gap between body and trailer).
            if block_start < end:
                block_start -= 1
                continue
            block_start -= 1
            continue
        is_blockquote = stripped.startswith(">")
        has_trigger = bool(_BLOG_DISCLAIMER_TRIGGER_RE.search(line))
        if is_blockquote or has_trigger:
            if has_trigger:
                saw_trigger = True
            block_start -= 1
            continue
        break

    # Trim any leading blanks of the candidate trailer block (between body
    # and the first collected line).
    while block_start < end and not lines[block_start].strip():
        block_start += 1

    if saw_trigger:
        body_lines = lines[:block_start]
    else:
        body_lines = lines[:end]
    body = "\n".join(body_lines).rstrip()
    return f"{body}\n\n{_BLOG_DISCLAIMER_CANONICAL}\n"


def canonicalize_draft_text(text: str, post_type: str) -> str:
    """Strip LLM drift and enforce canonical output before publish.

    Does three things the prompt cannot reliably enforce:
    1. Replace any trailing disclaimer-ish line(s) with the canonical disclaimer
       for this post_type. Catches paraphrasing like "Paper-trade only. Not advice."
    2. Strip `$SPY`/`$QQQ`/`$IWM`/`$DIA` filler from standby headers — writer
       keeps adding generic-index tickers when brief has no pick.
    3. Drop `V/OI None` segments from teaser runner-up lines when the upstream
       enrichment row has a null value.
    """
    lines = text.splitlines()

    # 1. Strip trailing disclaimer line(s) + blanks
    while lines and (not lines[-1].strip() or _DISCLAIMER_LINE.match(lines[-1])):
        lines.pop()

    # 2. Strip index-ticker filler on standby headers
    if post_type == "standby":
        cleaned: list[str] = []
        for line in lines:
            if "Standby" in line or "standby" in line.lower():
                line = _INDEX_FILLER_IN_HEADER.sub("", line)
                line = re.sub(r"\s+—", " —", line).rstrip()
            cleaned.append(line)
        lines = cleaned

    # 3. Drop `V/OI None` segments (common in teaser runner-ups with null voi)
    lines = [_NULL_VOI_SEGMENT.sub("", line) for line in lines]
    lines = [_STRAY_DIVIDERS.sub(" | ", line).strip() for line in lines]

    # 4. Enforce X-Free-tier 1-cashtag limit: keep the first $TICKER, strip $
    #    from any subsequent cashtags. Watchlist/teaser/scorecard/callback all
    #    legitimately reference multiple tickers; the others (signal/standby/
    #    report) have ≤1 cashtag by template so this is a no-op for them.
    body = "\n".join(lines).rstrip()
    body = _enforce_one_cashtag(body)
    lines = body.splitlines()

    body = "\n".join(lines).rstrip()
    disclaimer = _DISCLAIMER_BY_POST_TYPE.get(post_type)
    if disclaimer is None:
        # Forward-looking posts (signal/standby/teaser/report) ship without
        # a disclaimer per Evan 2026-04-28. Trailing disclaimer-ish lines
        # already stripped above.
        return body
    return f"{body}\n\n{disclaimer}"
