"""Pin the trace cost table to the rates that actually bill the project.

The 2026-08-17 defect this guards: `gemini-3.5-flash` sat at 0.000075/0.0003 per
1K against a real 0.0015/0.009, so `llm_traces_v1` logged $0.216 for 30 days of
enrichment that billed ~$5.59. A cost column that reads 26x low is worse than an
empty one, because it reconciles with itself.

Rates come from the Cloud Billing Catalog API (service C7E2-9256-1C43), not from
a docs page. The re-verify command is in pricing.py's docstring.

    .venv/bin/python -m pytest libs/trace_logger/tests/test_pricing.py -q
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from trace_logger.pricing import (  # noqa: E402
    LONG_CONTEXT_TOKENS,
    PRICING,
    estimate_cost_usd,
)


def test_flash_carries_the_billed_rate_not_the_stale_one():
    price = PRICING["gemini-3.5-flash"]
    assert (price.input_per_1k, price.output_per_1k) == (0.0015, 0.009)
    # The exact 30-day enrichment volume that exposed the drift.
    cost = estimate_cost_usd("gemini-3.5-flash", 1_177_423, 424_016)
    assert 5.0 < cost < 6.0, cost


def test_judge_day_reconciles_with_the_measured_bill():
    # ~44k in / ~11k out is one trading day of the bracket tournament, measured
    # from Cloud Monitoring token counts on 2026-08-17.
    cost = estimate_cost_usd("gemini-3.1-pro-preview", 44_000, 11_000)
    assert 0.20 <= cost <= 0.24, cost


def test_longest_prefix_wins():
    # "gemini-3.5-flash-lite-001" must not fall onto the 5x-dearer flash entry.
    assert estimate_cost_usd("gemini-3.5-flash-lite-001", 1_000_000, 0) == 0.3
    assert estimate_cost_usd("gemini-3.5-flash-002", 1_000_000, 0) == 1.5


def test_long_context_switches_the_rate_card():
    below = estimate_cost_usd("gemini-3.1-pro-preview", LONG_CONTEXT_TOKENS, 0)
    above = estimate_cost_usd("gemini-3.1-pro-preview", LONG_CONTEXT_TOKENS + 1, 0)
    assert above > below * 1.9


def test_unknown_model_returns_none_rather_than_a_guess():
    assert estimate_cost_usd("gpt-5.2", 1000, 1000) is None
    assert estimate_cost_usd("gemini-3.5-flash", None, None) is None


def test_no_entry_prices_output_below_input():
    for name, price in PRICING.items():
        assert price.input_per_1k > 0, name
        assert price.output_per_1k >= price.input_per_1k, name
