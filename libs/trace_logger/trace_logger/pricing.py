"""Per-model token pricing. Prices in USD per 1K tokens.

Used only to populate cost_usd on trace rows. It is NOT a billing source of
truth, but it must stay inside an order of magnitude of the bill, or the traces
lie about what the pipeline costs.

VERIFIED 2026-08-17 against the Cloud Billing Catalog API (the same rate card
that bills the project), not against a docs page:

    TOKEN=$(gcloud auth print-access-token)
    curl -s -H "Authorization: Bearer $TOKEN" \
      "https://cloudbilling.googleapis.com/v1/services/C7E2-9256-1C43/skus?pageSize=5000&currencyCode=USD" \
      | python3 -c "import sys,json;[print(s['description'], s['pricingInfo'][0]['pricingExpression']['tieredRates'][0]['unitPrice']) for s in json.load(sys.stdin)['skus'] if 'Text' in s['description']]"

The prior table was stale by 20x on the input side and 30x on the output side
for gemini-3.5-flash (0.000075/0.0003 against a real 0.0015/0.009), so 30 days
of enrichment logged $0.216 against a real ~$5.59. Re-verify with the command
above whenever you add a model or a price bump lands.

Scope of these numbers:
- Google rates are the GLOBAL endpoint, standard "Predictions" SKUs. Regional
  endpoints cost ~10% more. Batch is ~50% less, Flex less again, Priority more.
- THINKING tokens bill as output. Callers must fold thoughts_token_count into
  output_tokens (see enrichment-trigger's fetch_and_analyze_news), or the row
  understates the bill.
- CACHED input bills at ~10% of the input rate. TraceRecord has no cached-token
  field, so a caller that uses context caching OVERSTATES its input cost here.
- Long-context rates apply above LONG_CONTEXT_TOKENS input tokens.

Unknown models deliberately return None (a NULL cost_usd) instead of a guess.
"""

from typing import NamedTuple, Optional


class TokenPrice(NamedTuple):
    """USD per 1K tokens. The `long_*` rates apply above LONG_CONTEXT_TOKENS."""

    input_per_1k: float
    output_per_1k: float
    long_input_per_1k: Optional[float] = None
    long_output_per_1k: Optional[float] = None


# Input-token count above which the long-context rate card applies.
LONG_CONTEXT_TOKENS = 200_000

PRICING: dict[str, TokenPrice] = {
    # --- Google Gemini (Vertex, global endpoint) ---
    # One SKU family covers 3.0 and 3.1 Pro: "Gemini 3.0 / 3.1 Pro Text ...".
    "gemini-3.1-pro": TokenPrice(0.002, 0.012, 0.004, 0.018),
    "gemini-3.0-pro": TokenPrice(0.002, 0.012, 0.004, 0.018),
    "gemini-3-pro": TokenPrice(0.002, 0.012, 0.004, 0.018),
    # gemini-3-pro-image-preview: text input bills at the Pro text rate, but its
    # OUTPUT is image tokens at 0.12/1K (100x the text rate). This entry prices
    # output as image tokens, which is right for an image call and wrong for a
    # text-only one. x-poster is not instrumented today; fix this entry if it is.
    "gemini-3-pro-image": TokenPrice(0.002, 0.12),
    "gemini-3.5-flash-lite": TokenPrice(0.0003, 0.0025),
    "gemini-3.5-flash": TokenPrice(0.0015, 0.009),
    "gemini-3-flash": TokenPrice(0.0005, 0.003),
    "gemini-2.5-pro": TokenPrice(0.00125, 0.010, 0.0025, 0.015),
    "gemini-2.5-flash-lite": TokenPrice(0.0001, 0.0004),
    "gemini-2.5-flash": TokenPrice(0.0003, 0.0025),
    # --- Anthropic (public list price, NOT catalog-verified) ---
    "claude-sonnet-4": TokenPrice(0.003, 0.015),
    "claude-opus-4": TokenPrice(0.015, 0.075),
}
# Removed 2026-08-17: gpt-5.2, grok-4, deepseek-v3. Those rates were unsourced
# guesses and no live service calls them (agent-arena is dead). A NULL cost is
# better than an invented one.


def estimate_cost_usd(
    model_id: str,
    input_tokens: Optional[int],
    output_tokens: Optional[int],
) -> Optional[float]:
    """Return USD cost or None if model is unknown or token counts missing."""
    if input_tokens is None and output_tokens is None:
        return None

    price = PRICING.get(model_id)
    if price is None:
        # Longest-prefix match for versioned / suffixed model IDs, so
        # "gemini-3.5-flash-lite-001" cannot fall onto the 5x-dearer
        # "gemini-3.5-flash" entry just because it is earlier in the dict.
        matches = [k for k in PRICING if model_id.startswith(k)]
        if not matches:
            return None
        price = PRICING[max(matches, key=len)]

    in_toks = input_tokens or 0
    out_toks = output_tokens or 0

    in_rate, out_rate = price.input_per_1k, price.output_per_1k
    if in_toks > LONG_CONTEXT_TOKENS:
        in_rate = price.long_input_per_1k or in_rate
        out_rate = price.long_output_per_1k or out_rate

    return round((in_toks / 1000.0) * in_rate + (out_toks / 1000.0) * out_rate, 6)
