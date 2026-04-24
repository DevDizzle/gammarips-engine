"""
One-shot script — generate the canonical brand_ref_card.png via Nano Banana
(gemini-3-pro-image-preview) and upload to GCS gs://gammarips-x-media/.

Evan runs this once, inspects the output image, iterates on the prompt if needed,
then uploads the chosen image as the locked-in brand reference. Every subsequent
x-poster signal image will pass this card as an input reference so the model
preserves brand layout and only varies data/colors.

Usage:
    uv run python scripts/generate_brand_ref_card.py [--out out/card.png] [--no-upload]

Requires:
    - gcloud auth login (uses application default credentials)
    - gsutil / Storage API enabled
    - GCS bucket gammarips-x-media exists
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from google import genai
from google.cloud import storage

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
GCS_BUCKET = os.getenv("GCS_BUCKET", "gammarips-x-media")
GCS_BLOB = "brand_ref_card.png"
MODEL = "gemini-3-pro-image-preview"

BRAND_PROMPT = """Create a 1200x675 brand reference card for the @gammarips options-flow signal service on X/Twitter.

Design requirements:
- Background: dark navy (#0F1419) with a subtle lighter navy (#15202B) radial gradient from upper-left
- Typography: crisp sans-serif, bold for tickers, regular for body
- Colors: off-white (#E7E9EA) text, accent green (#00BA7C) for bullish markers, accent red (#F4212E) for bearish markers

Layout (3 zones):
1. TOP-LEFT ZONE (upper 20%): Wordmark "🔥 GammaRips" — flame emoji at 36px, brand name in bold 42px off-white. Below it, subtle 16px off-white label "V5.3 SIGNAL ENGINE"
2. CENTER ZONE (middle 60%): A 2x2 grid of placeholder data cells with subtle divider lines. The grid should have clear negative space where specific data (ticker, direction, contract, flow stats) will be composited per-post. Add soft rounded borders (#253341) around each cell, 24px padding.
3. BOTTOM-RIGHT ZONE (lower 20%): Watermark "V5_3_TARGET_80" in 18px off-white, 35% opacity. To the left of it, space for a disclaimer bar.

Composition rules:
- Clean, institutional trading-terminal aesthetic (think Bloomberg meets modern SaaS)
- No hype graphics, no stock charts, no generic "to the moon" imagery
- Heavy negative space — data will be added later, so leave room
- Single focal point: the Center Zone grid should feel like "this is where today's trade lives"
- Avoid: gradients in the center zone, glossy effects, emoji beyond the one flame in the wordmark

The card will be used as a reference style for AI-generated variants. Keep the layout rigid and predictable; per-post variance will be ticker, direction, strike, and flow stats only."""


def generate(prompt: str) -> bytes:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    logger.info(f"Calling {MODEL} with brand prompt ({len(prompt)} chars)…")
    response = client.models.generate_content(model=MODEL, contents=prompt)

    for part in (response.candidates[0].content.parts if response.candidates else []):
        if getattr(part, "inline_data", None) and part.inline_data.data:
            return part.inline_data.data

    logger.error("No image data returned. Full response:")
    logger.error(response)
    sys.exit(1)


def upload_to_gcs(image_bytes: bytes) -> str:
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_BLOB)
    blob.upload_from_string(image_bytes, content_type="image/png")
    gs_uri = f"gs://{GCS_BUCKET}/{GCS_BLOB}"
    logger.info(f"Uploaded to {gs_uri}")
    return gs_uri


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="out/brand_ref_card.png", help="Local output path")
    parser.add_argument("--no-upload", action="store_true", help="Skip GCS upload (preview only)")
    parser.add_argument("--prompt-file", help="Override the default brand prompt with a file path")
    args = parser.parse_args()

    prompt = BRAND_PROMPT
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text()

    image_bytes = generate(prompt)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(image_bytes)
    logger.info(f"Saved local preview: {out_path}")

    if not args.no_upload:
        upload_to_gcs(image_bytes)
    else:
        logger.info("Skipped GCS upload (--no-upload). Review the local file first.")


if __name__ == "__main__":
    main()
