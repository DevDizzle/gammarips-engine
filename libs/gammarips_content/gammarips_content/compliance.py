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
    "report": 280,
    "teaser": 300,
    "win": 200,       # QRT quote is short — original tweet provides context
    "loss": 200,      # Neutral single, per X research — no QRT
    "scorecard": 400, # Per tweet in the 3-tweet thread
    "blog": 2_000_000,  # Effectively unbounded for blog markdown
}


# Posts that REQUIRE an image to ship. Others: optional.
IMAGE_REQUIRED: frozenset[str] = frozenset({"signal", "standby", "scorecard"})


# Posts where cashtag-at-pos-0 is exempt (e.g. loss singles that lead with "Stopped").
CASHTAG_RULE_EXEMPT: frozenset[str] = frozenset({"loss", "report", "scorecard"})


URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)
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

    # 3. Disclaimer present (case-sensitive — canonical form)
    if not is_blog:
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

    # 6. URL absence (body-of-tweet — blog allows URLs)
    if not is_blog and URL_PATTERN.search(text):
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

# Which disclaimer each post_type uses (Evan 2026-04-24 decision):
# signal/standby/teaser/report get the LONG form ("Not financial advice")
# win/loss/scorecard get the SHORT form ("Not advice")
_DISCLAIMER_BY_POST_TYPE: dict[str, str] = {
    "signal":    DISCLAIMER_CANONICAL_LONG,
    "standby":   DISCLAIMER_CANONICAL_LONG,
    "teaser":    DISCLAIMER_CANONICAL_LONG,
    "report":    DISCLAIMER_CANONICAL_LONG,
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

    body = "\n".join(lines).rstrip()
    disclaimer = _DISCLAIMER_BY_POST_TYPE.get(post_type, DISCLAIMER_CANONICAL_LONG)
    return f"{body}\n\n{disclaimer}"
