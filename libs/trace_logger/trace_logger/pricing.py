"""Per-model token pricing. Prices in USD per 1K tokens.

Kept deliberately coarse. Used only to populate cost_usd on trace rows; not
a billing source of truth. Update alongside model additions.
"""

from typing import Optional

# (input_per_1k, output_per_1k) in USD.
PRICING: dict[str, tuple[float, float]] = {
    # Google Gemini (Vertex)
    "gemini-3-flash": (0.000075, 0.0003),
    "gemini-3-flash-preview": (0.000075, 0.0003),
    "gemini-2.5-flash": (0.000075, 0.0003),
    "gemini-2.5-pro": (0.00125, 0.005),
    # Anthropic
    "claude-sonnet-4-20250514": (0.003, 0.015),
    "claude-sonnet-4": (0.003, 0.015),
    "claude-opus-4": (0.015, 0.075),
    # OpenAI / compat
    "gpt-5.2": (0.005, 0.015),
    "grok-4": (0.005, 0.015),
    "deepseek-v3": (0.00014, 0.00028),
}


def estimate_cost_usd(
    model_id: str,
    input_tokens: Optional[int],
    output_tokens: Optional[int],
) -> Optional[float]:
    """Return USD cost or None if model is unknown or token counts missing."""
    if input_tokens is None and output_tokens is None:
        return None
    # Best-effort prefix match for versioned model IDs.
    key = model_id
    if key not in PRICING:
        for k in PRICING:
            if model_id.startswith(k):
                key = k
                break
    if key not in PRICING:
        return None
    in_rate, out_rate = PRICING[key]
    in_toks = input_tokens or 0
    out_toks = output_tokens or 0
    return round((in_toks / 1000.0) * in_rate + (out_toks / 1000.0) * out_rate, 6)
