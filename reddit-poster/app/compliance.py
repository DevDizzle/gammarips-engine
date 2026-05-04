"""Reddit-specific compliance rubric — short, deterministic, 5 checks max.

X-poster's rubric is too tweet-shaped (cashtag-pos-80, 280-char budgets).
Reddit allows longer bodies and different anti-spam etiquette, so we keep
a separate, shorter rubric here. We still import the shared retired-alias
and banned-recommendation lists from gammarips_content so voice rules stay
in lockstep.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from gammarips_content.voice_rules import (
    BANNED_RECOMMENDATION_PHRASES,
    DISCLAIMER_REQUIRED_TOKENS,
    RETIRED_ALIASES,
)

# Reddit-specific char budgets. Trade-idea has more room than a tweet but
# still needs to read like a comment, not a blog post.
CHAR_BUDGETS: dict[str, tuple[int, int]] = {
    "trade_idea": (400, 1500),
    "pnl_receipt": (200, 700),
}

# AI-slop tells — common LLM filler words that signal "AI wrote this" to
# r/options moderators and readers. Reject if any appear.
AI_SLOP_PHRASES: tuple[str, ...] = (
    "game-changer",
    "game changer",
    "leverage",
    "ecosystem",
    "AI-powered",
    "AI powered",
    "unlock",
    "unlocks",
    "synergy",
    "paradigm",
    "robust",
    "seamless",
    "harness",
    "delve",
)

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
GAMMARIPS_URL_PATTERN = re.compile(r"https?://(?:www\.)?gammarips\.com\S*", re.IGNORECASE)


@dataclass
class RubricResult:
    passed: bool
    char_count: int
    char_budget: tuple[int, int]
    failures: list[str] = field(default_factory=list)


def score(text: str, post_type: str, allow_gammarips_link: bool = False) -> RubricResult:
    """Apply 5 hard-line checks. `allow_gammarips_link=False` enforces no
    naked gammarips.com URL on first-post-in-a-sub (Reddit anti-spam).
    The footer literal `gammarips.com/track-record` (no scheme) is allowed.
    """
    failures: list[str] = []
    char_count = len(text)
    lo, hi = CHAR_BUDGETS.get(post_type, (0, 1500))
    text_lower = text.lower()

    # 1. Char budget
    if char_count < lo or char_count > hi:
        failures.append(f"char_budget: {char_count} not in [{lo}, {hi}] ({post_type})")

    # 2. Banned recommendation phrasing + retired aliases
    for phrase in BANNED_RECOMMENDATION_PHRASES:
        if phrase.lower() in text_lower:
            failures.append(f"banned_phrase: '{phrase}'")
    for alias in RETIRED_ALIASES:
        if alias.lower() in text_lower:
            failures.append(f"retired_alias: '{alias}'")

    # 3. AI-slop tells
    for phrase in AI_SLOP_PHRASES:
        if phrase.lower() in text_lower:
            failures.append(f"ai_slop: '{phrase}'")

    # 4. Disclaimer required on pnl_receipt only
    if post_type == "pnl_receipt":
        missing = [t for t in DISCLAIMER_REQUIRED_TOKENS if t not in text]
        if missing:
            failures.append(f"disclaimer_missing: {missing}")

    # 5. Naked gammarips.com URL — only allowed when caller has confirmed
    # we have prior karma/posts in the target subreddit.
    if not allow_gammarips_link and GAMMARIPS_URL_PATTERN.search(text):
        failures.append("naked_gammarips_url_first_post")

    return RubricResult(
        passed=not failures,
        char_count=char_count,
        char_budget=(lo, hi),
        failures=failures,
    )
