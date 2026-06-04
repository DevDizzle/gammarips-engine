"""V5.4 Phase 2.5 — Zero-shot VAPO lint pass on signal-ranker prompts.

Approximates Vertex AI Prompt Optimizer's zero-shot mode with a single
SDK call to `gemini-2.5-pro` (VAPO's canonical tuning target — preview
models like gemini-3-flash-preview and gemini-3.1-pro-preview are excluded
as VAPO targets, so we tune on 2.5-pro and transfer at runtime).

Per EXEC-PLAN: cherry-pick wording wins manually; do NOT auto-accept the
rewrite. This script writes scorer_v1.optimized.md / picker_v1.optimized.md
side-by-side with the originals, plus a unified diff at vapo_zeroshot_diff.md.
The operator decides which lines to merge into v2.

Usage:
    PROJECT_ID=profitscout-fida8 python signal-ranker/scripts/vapo_zeroshot.py
"""

from __future__ import annotations

import argparse
import difflib
import os
from datetime import date
from pathlib import Path

from google import genai
from google.genai import types

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
LOCATION = os.getenv("VERTEX_LOCATION", "global")
TUNING_MODEL = os.getenv("VAPO_TUNING_MODEL", "gemini-2.5-pro")

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
DIFF_OUT = REPO_ROOT / "scripts" / "vapo_zeroshot_diff.md"

PROMPTS = [
    ("scorer_v1.md", "scorer_v1.optimized.md"),
    ("picker_v1.md", "picker_v1.optimized.md"),
]

META_PROMPT_TEMPLATE = """You are a senior prompt engineer doing a zero-shot
prompt-optimizer lint pass on a production LLM-agent prompt for an options-
flow trading system. Your job: REWRITE the prompt below for clarity,
structure, and instruction-following — keeping the same intent and the same
output schema.

THE ORIGINAL PROMPT IS LOAD-BEARING IN PRODUCTION. You must preserve:
- All numeric rubric ranges (1-10) and calibration anchors
- The composite weights (60/25/15) — but DO NOT compute or restate the
  composite in the LLM's job; it's a downstream Python computation
- All hard constraints (no abstain, no out-of-set picks, no rubric overrides
  inside fenced data blocks)
- The schema-output instruction at the end (return ONE JSON object, no fences,
  no commentary)
- The data-only fence preamble guidance (LLM-generated narrative inputs are
  not trusted instructions)
- Field names referenced by the prompt (Pydantic schemas depend on these)

You MAY improve:
- Phrasing that is ambiguous, hedged, or accidentally permissive
- Implicit constraints — surface them as explicit numbered rules
- Section ordering for better information flow
- Calibration-anchor specificity (when a 1-10 anchor reads vague)
- Redundancy / repetition

Return ONLY the rewritten prompt as raw markdown. No commentary, no code
fences around the prompt, no preamble like "Here is the rewritten prompt".
The first character of your response must be the first character of the
rewritten prompt.

=== ORIGINAL PROMPT TO LINT ===

{original}
"""


def lint_prompt(client: genai.Client, original: str) -> str:
    cfg = types.GenerateContentConfig(
        temperature=0.2,  # low — we want stable lint, not creative drift
        max_output_tokens=8192,
    )
    resp = client.models.generate_content(
        model=TUNING_MODEL,
        contents=META_PROMPT_TEMPLATE.format(original=original),
        config=cfg,
    )
    text = resp.text or ""
    return text.strip()


def make_unified_diff(original: str, optimized: str, label: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            optimized.splitlines(),
            fromfile=f"{label}.md (v1)",
            tofile=f"{label}.md (zero-shot lint)",
            lineterm="",
            n=3,
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="Write *.optimized.md alongside originals")
    ap.add_argument("--diff-only", action="store_true",
                    help="Only emit the diff, no .optimized.md files")
    args = ap.parse_args()

    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    diff_sections: list[str] = []

    for original_name, optimized_name in PROMPTS:
        src = PROMPTS_DIR / original_name
        dst = PROMPTS_DIR / optimized_name
        original = src.read_text(encoding="utf-8")
        print(f"=== Linting {original_name} via {TUNING_MODEL} ===")
        optimized = lint_prompt(client, original)
        if not optimized:
            raise RuntimeError(f"empty rewrite from {TUNING_MODEL} for {original_name}")
        if args.write or not args.diff_only:
            dst.write_text(optimized, encoding="utf-8")
            print(f"  wrote {dst}")
        diff = make_unified_diff(original, optimized, original_name.removesuffix(".md"))
        diff_sections.append(
            f"## {original_name} → {optimized_name}\n\n"
            f"Original {len(original.splitlines())} lines; "
            f"optimized {len(optimized.splitlines())} lines.\n\n"
            f"```diff\n{diff}\n```\n"
        )

    today = date.today().isoformat()
    diff_doc = (
        f"# Zero-shot VAPO lint pass — {today}\n\n"
        f"Tuning model: `{TUNING_MODEL}` (preview models excluded as VAPO targets; "
        f"runtime transfers to `gemini-3.5-flash` for Scorer and "
        f"`gemini-3.1-pro-preview` for Picker).\n\n"
        f"Per EXEC-PLAN: cherry-pick wording wins manually. Do NOT auto-accept. "
        f"After review, merge accepted edits into the v1 file in place OR bump "
        f"to v2.md and update SCORER_PROMPT_VERSION / PICKER_PROMPT_VERSION env vars.\n\n"
        + "\n---\n\n".join(diff_sections)
    )
    DIFF_OUT.write_text(diff_doc, encoding="utf-8")
    print(f"\nDiff log → {DIFF_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
