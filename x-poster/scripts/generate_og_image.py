"""
One-shot script — generate a fresh gammarips.com OG / social-preview image via
Nano Banana Pro (gemini-3-pro-image-preview).

The current /og-image.png still pitches the deprecated agent-arena ("5 AI
Agents. 4 Rounds. 1 Consensus Trade.") and is aesthetically off. This regen
puts the live V5.4 voice on the card: "One options trade a day. Scored before
you wake up."

Usage:
    PROJECT_ID=profitscout-fida8 uv run python scripts/generate_og_image.py
    # writes out/og-image.png; preview, then re-run with --write to overwrite
    # the webapp asset at /home/user/gammarips-webapp/public/og-image.png

Generates several variants in one run so we can pick the strongest.
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path

from google import genai

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
MODEL = "gemini-3-pro-image-preview"
WEBAPP_OG_PATH = Path("/home/user/gammarips-webapp/public/og-image.png")

# Brand colors mirror libs/gammarips_content/brand.py — single source of truth.
# Webapp tokens (HSL → hex):
#   background #1a1f2e, card #242a3d, primary_bull #a4e600, accent_gold #ffcc00,
#   destructive_bear #cc3333, foreground #e8ecf7, muted_text #9098b3, border #404656.

BASE_PROMPT = """Generate a 1200x630 Open Graph / social preview card for gammarips.com.
This image appears whenever the URL is shared on X, LinkedIn, iMessage, Slack,
Discord — it must read instantly at thumbnail size and look institutional, not
hype-y.

# Brand
GammaRips is an overnight options-flow signal engine. One options trade per
day, scored before market open. Tone: disciplined, data-driven, anti-hype.
Bloomberg meets modern SaaS.

# Required text (verbatim, no other words on the card)
- HEADLINE (largest, 2 lines, left-aligned):
    "One options trade a day."
    "Scored before you wake up."
- SUBLINE (smaller, single line, directly below headline):
    "Overnight options-flow signals. Pushed at 9 AM ET."
- WORDMARK (top-left, much smaller than headline):
    "GammaRips"
  Optionally pair with a small lime-green chevron / mountain "▲" glyph to the
  left of the wordmark. No other logos.

# Color system (use these EXACT hex codes)
- Background base:  #1a1f2e (deep charcoal navy)
- Card / panel:     #242a3d (one step lighter for any inset surface)
- Headline text:    #e8ecf7 (off-white)
- Subline text:     #9098b3 (muted slate)
- Accent (primary): #a4e600 (lime green — bullish)
- Accent (secondary): #ffcc00 (gold — sparingly, for a single highlight)
- Borders / hairlines: #404656 at low opacity
DO NOT introduce teal, turquoise, cyan, or pastel greens. The accent green
must be the saturated lime #a4e600, not the seafoam-green of generic fintech
templates.

# Layout
- 1200 wide x 630 tall, full bleed.
- Heavy negative space — at least 40% of the canvas should be empty dark
  background. Resist the urge to fill corners.
- Left half: stacked headline + subline + small wordmark above.
- Right half: ONE simple, abstract focal element — a clean upward candle / bar
  / flow glyph in #a4e600, with a subtle glow. No charts, no axes, no tickers,
  no faces, no people.
- Optional: very subtle vertical hairline grid in #404656 at ~8% opacity
  behind the right-side glyph to evoke a trading terminal. Keep it whisper-
  quiet — must not compete with the headline.

# Hard prohibitions
- NO emojis anywhere.
- NO stock-chart cliches (bull statues, money rain, rockets, "to the moon").
- NO multi-agent / "5 agents" / "consensus" / "round" language — that
  product is deprecated.
- NO blurry text, NO misspellings, NO duplicated words. Headline must read
  exactly as specified.
- NO photographic elements. Pure vector / clean digital illustration.

Typography: bold geometric sans for the headline (Space Grotesk or visually
equivalent), regular weight for the subline. Generous line-height. Tight
letter-spacing on the headline. Subline 35-45% of the headline size.

The card should feel like the cover of a sober quant research note, not a
crypto ad."""

VARIANTS: list[tuple[str, str]] = [
    (
        "candle",
        BASE_PROMPT
        + "\n\nRight-side focal element: a single tall upward-pointing green "
        "candlestick (#a4e600 body, thin wick) with a soft outer glow against "
        "the dark navy. Geometric, flat, no 3D.",
    ),
    (
        "arrow",
        BASE_PROMPT
        + "\n\nRight-side focal element: a clean angular up-and-to-the-right "
        "arrow rendered as a sharp lime-green (#a4e600) chevron with a soft "
        "outer glow. Minimal, almost wayfinding-sign simple.",
    ),
    (
        "ripple",
        BASE_PROMPT
        + "\n\nRight-side focal element: three concentric arcs in #a4e600 "
        "radiating outward from a small bright dot — a 'gamma ripple' pulse. "
        "Clean, geometric, no chart, no labels. Soft outer glow.",
    ),
]


def generate(prompt: str) -> bytes:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    logger.info(f"Calling {MODEL} ({len(prompt)} chars)…")
    response = client.models.generate_content(model=MODEL, contents=prompt)
    for part in (response.candidates[0].content.parts if response.candidates else []):
        if getattr(part, "inline_data", None) and part.inline_data.data:
            return part.inline_data.data
    logger.error("No image data returned. Full response:\n%s", response)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        default="out/og",
        help="Directory to drop variant PNGs into",
    )
    parser.add_argument(
        "--variant",
        choices=[v[0] for v in VARIANTS] + ["all"],
        default="all",
        help="Which variant(s) to generate",
    )
    parser.add_argument(
        "--write",
        metavar="VARIANT_NAME",
        help="After generating, copy this variant to the webapp og-image.png",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = VARIANTS if args.variant == "all" else [v for v in VARIANTS if v[0] == args.variant]
    paths: dict[str, Path] = {}
    for name, prompt in selected:
        logger.info(f"\n--- Generating variant: {name} ---")
        image_bytes = generate(prompt)
        out_path = out_dir / f"og_{name}.png"
        out_path.write_bytes(image_bytes)
        logger.info(f"  wrote {out_path} ({len(image_bytes):,} bytes)")
        paths[name] = out_path

    if args.write:
        if args.write not in paths:
            logger.error(
                "Cannot --write %s; not in generated variants %s",
                args.write,
                list(paths),
            )
            sys.exit(2)
        if not WEBAPP_OG_PATH.parent.exists():
            logger.error("Webapp public dir missing: %s", WEBAPP_OG_PATH.parent)
            sys.exit(2)
        backup = WEBAPP_OG_PATH.with_suffix(".png.bak")
        if WEBAPP_OG_PATH.exists() and not backup.exists():
            shutil.copy2(WEBAPP_OG_PATH, backup)
            logger.info("Backed up old OG → %s", backup)
        shutil.copy2(paths[args.write], WEBAPP_OG_PATH)
        logger.info("Wrote %s → %s", paths[args.write], WEBAPP_OG_PATH)


if __name__ == "__main__":
    main()
