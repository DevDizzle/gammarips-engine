"""
Brand voice rules for GammaRips content.

Source of truth: docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md §2.
Update here first, then mirror back into the plan doc if the rules drift.
"""
from __future__ import annotations

from dataclasses import dataclass


# Retired aliases — MUST NOT appear in any published content.
# Case-insensitive match in compliance.score_against_rubric().
RETIRED_ALIASES: tuple[str, ...] = (
    "Ripper",
    "Rippers",
    "Daily Playbook",
    "The Overnight Edge",
    "@mention",
    "score >= 6",
    "score>=6",
    "8:30 AM",
    "8:30 ET",
    "$49/$149",
    "premium signal",
    "interactive dashboard",
    "#TheOvernightEdge",
)


# Publisher-exclusion compliance — banned individualized-recommendation phrasing.
# SEC v. Lowe §202(a)(11)(D) — keep framing impersonal, scheduled, educational.
BANNED_RECOMMENDATION_PHRASES: tuple[str, ...] = (
    "buy this",
    "sell this",
    "act now",
    "for you",
    "your next trade",
    "entry for you",
    "guaranteed",
    "risk-free",
    "can't lose",
)


# Standard disclaimer. Every post must contain both substrings.
# Canonical long form (blog, long posts):
DISCLAIMER_LONG = (
    "Paper-trading performance, educational content only. "
    "Not investment advice. Past performance is not a guarantee of future results."
)

# Canonical short form (X posts — char budget):
DISCLAIMER_SHORT = "Paper-trade. Not advice."

# Required substrings — case-sensitive, both must be present.
DISCLAIMER_REQUIRED_TOKENS = ("Paper-trade", "Not advice")


@dataclass(frozen=True)
class VoiceRules:
    """Structured voice rules for passing into agent prompts."""

    do: tuple[str, ...] = (
        "Write for a working professional with a full-time job and a $2K-$20K options account.",
        "Use specific dollar amounts and specific times. $500/trade, 10:00 AM ET, -60%/+80%, 3 trading days.",
        "Prefer short, declarative sentences. One idea per sentence.",
        "Show the routine, not the dashboard. GammaRips is a morning habit.",
        "Use cashtags ($AAPL) for ticker references — standard FinTwit, drives discovery.",
        "Put the cashtag in the first 80 characters for above-the-fold visibility.",
    )

    do_not: tuple[str, ...] = (
        "Never use retired aliases (Ripper, Daily Playbook, The Overnight Edge, etc.).",
        "Never use individualized recommendation language (buy this, act now, for you).",
        "Never include URLs in post bodies — X downranks link-bearing posts. Link lives in pinned tweet + bio.",
        "Never use hashtags — near-dead on X in 2026 and slightly suppressive.",
        "Never claim real-money P&L before V5.3 has >= 30 closed trades. Paper-trade framing only.",
        "Never cherry-pick wins. Loss callbacks ship. Ledger-backed credibility beats hype.",
    )

    brand_tone: str = (
        "Disciplined. Transparent. Educational. Numbers-first. "
        "Never hype, never prescribe, never hedge with 'might' or 'could.' "
        "State the signal, state the routine, state the disclaimer. Move on."
    )


VOICE_RULES = VoiceRules()


def render_for_prompt() -> str:
    """Render voice rules as a prompt-ready string for injection into LLM instructions."""
    lines = ["# Brand voice rules", "", f"Tone: {VOICE_RULES.brand_tone}", "", "## DO"]
    lines += [f"- {r}" for r in VOICE_RULES.do]
    lines += ["", "## DO NOT"]
    lines += [f"- {r}" for r in VOICE_RULES.do_not]
    lines += ["", "## Retired aliases (never use)"]
    lines += [f"- {a}" for a in RETIRED_ALIASES]
    lines += ["", "## Banned recommendation phrasing"]
    lines += [f"- {p}" for p in BANNED_RECOMMENDATION_PHRASES]
    lines += ["", f"## Disclaimer (required in every post)", f"- Short form: {DISCLAIMER_SHORT}"]
    return "\n".join(lines)
