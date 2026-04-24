"""
GammaRips brand constants — single source of truth for colors, fonts, voice
markers, and image-gen anchoring.

Extracted 2026-04-24 from `/home/user/gammarips-webapp/src/app/globals.css`
(HSL → hex), `tailwind.config.ts`, and copy across About / How-It-Works /
Hero. If the webapp palette changes, update here first — x-poster and
blog-generator both import from this module.
"""
from __future__ import annotations

from dataclasses import dataclass, field


# --- Color palette --------------------------------------------------------
# Source: /home/user/gammarips-webapp/src/app/globals.css lines 6-44.
# Single dark theme — webapp forces `.dark` class on <html>.
COLORS: dict[str, str] = {
    "background":       "#1a1f2e",   # Deep charcoal, primary surface
    "foreground":       "#e8ecf7",   # Off-white, high contrast text
    "card":             "#242a3d",   # Slightly lighter charcoal for depth
    "primary_bull":     "#a4e600",   # Brand lime-green — bullish / accent
    "primary_fg":       "#1a3300",   # Dark text on green
    "accent_gold":      "#ffcc00",   # Secondary brand — rings, highlights
    "accent_fg":        "#331a00",   # Dark text on gold
    "destructive_bear": "#cc3333",   # Red — bearish / danger
    "destructive_fg":   "#f2f5fc",   # Light text on red
    "muted_text":       "#9098b3",   # Dimmed / secondary text
    "border":           "#404656",   # Card + element borders
    "chart_blue":       "#3385ff",
    "chart_teal":       "#33cc99",
    "chart_orange":     "#ffaa33",
    "chart_purple":     "#b366ff",
    "chart_pink":       "#ff3366",
}


# --- Typography -----------------------------------------------------------
# Source: tailwind.config.ts:17-20 + layout.tsx next/font imports.
FONTS: dict[str, str] = {
    "headline": "Space Grotesk",  # Next.js --font-space-grotesk (bold for h1-h3)
    "body":     "Inter",           # Next.js --font-inter (default)
    "code":     "monospace",       # fallback only
}


# --- Brand marks / image anchors ------------------------------------------
LOGO_URL = "https://gammarips.com/icon.png"
OG_IMAGE_URL = "https://gammarips.com/og-image.png"
OG_IMAGE_LOCAL = "/home/user/gammarips-webapp/public/og-image.png"

# Brand logo — used as a deterministic PIL-composited watermark on every
# generated image. Source of truth for the brand mark. JPG with dark-teal
# backdrop (functions as a small badge in the bottom-right of editorial cards).
LOGO_GCS = "gs://gammarips-x-media/brand_logo.jpg"

# Deprecated 2026-04-24 — the og-image highlights the multi-agent /arena
# debate which we deprecated. Use LOGO_GCS for watermarking; let Nano Banana
# generate the editorial image freely from a theme-driven prompt.
BRAND_REF_GCS_DEFAULT = "gs://gammarips-x-media/brand_ref_card.png"


# --- Voice markers --------------------------------------------------------
# Distinctive phrases pulled from live webapp copy (hero, about, how-it-works,
# OG image, pricing). Use these in writer prompts and image-gen prompts so the
# brand aesthetic is grounded in actual voice, not generic fintech copy.
VOICE_MARKERS: tuple[str, ...] = (
    "One options trade a day.",
    "Scored before you wake up. Pushed to your phone at 9 AM.",
    "Wake up knowing what smart money did last night.",
    "Stop trading blind.",
    "See the positions at 8:30 AM — hours before the move.",
    "No cherry-picking, no hindsight.",
    "The engine is deterministic — same inputs, same output.",
    "One pick or none. No firehose, no FOMO.",
)


# --- Personality ----------------------------------------------------------
# Prompt-ready voice summary. Pair with VOICE_MARKERS when priming LLMs.
PERSONALITY: str = (
    "Disciplined technical confidence. Institutional-grade pattern recognition. "
    "Solo engineer who built a tool they believe in — not a marketing operation. "
    "Tone: direct, data-driven, anti-hype. Quantified and deterministic. "
    "Subtle swagger rooted in process, not bravado."
)


# --- Visual language ------------------------------------------------------
# For image-gen prompts — describes the card aesthetic.
VISUAL_LANGUAGE: str = (
    "Dark terminal aesthetic. Bloomberg meets modern SaaS. "
    "Heavy negative space. Single focal point per frame. "
    "Green (#a4e600) for bullish, red (#cc3333) for bearish, gold (#ffcc00) for highlight. "
    "Space Grotesk bold for tickers and headlines. Inter for body/numerics. "
    "No hype graphics. No generic 'to the moon' imagery. No stock-chart cliches."
)


@dataclass(frozen=True)
class BrandKit:
    colors: dict[str, str] = field(default_factory=lambda: dict(COLORS))
    fonts: dict[str, str] = field(default_factory=lambda: dict(FONTS))
    voice_markers: tuple[str, ...] = field(default_factory=lambda: VOICE_MARKERS)
    personality: str = PERSONALITY
    visual_language: str = VISUAL_LANGUAGE
    logo_url: str = LOGO_URL
    og_image_url: str = OG_IMAGE_URL
    brand_ref_gcs: str = BRAND_REF_GCS_DEFAULT


BRAND = BrandKit()


def render_for_image_prompt() -> str:
    """Prompt-ready block for injection into Nano Banana / Gemini image calls.

    Use at the START of any image_prompt so the model sees brand colors + fonts +
    aesthetic BEFORE per-post specifics. Combine with a brand-ref image input
    (Part bytes from GCS brand_ref_card.png) for best fidelity.
    """
    color_lines = "\n".join(f"  - {role}: {hx}" for role, hx in COLORS.items())
    return (
        "# GammaRips Brand\n"
        f"Personality: {PERSONALITY}\n"
        f"\nVisual language:\n{VISUAL_LANGUAGE}\n"
        f"\nColors (use exactly these hex codes):\n{color_lines}\n"
        f"\nTypography: headlines in {FONTS['headline']} bold. "
        f"Body / numerics in {FONTS['body']}. Code labels in {FONTS['code']}."
    )


def render_voice_markers() -> str:
    """Prompt-ready bullet list of brand voice markers for writer agents."""
    return "\n".join(f"- {m}" for m in VOICE_MARKERS)
