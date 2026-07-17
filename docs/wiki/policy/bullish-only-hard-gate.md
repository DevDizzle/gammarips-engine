Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (a selection gate, not a measured edge)
Source: CLAUDE.md "Current policy"; docs/DECISIONS/2026-06-12-enrich-topN-thinking-cap.md
Date: 2026-07-17

# BULLISH-only is a HARD gate

The pool is **hard-gated to BULLISH-only** (`BULLISH_ONLY=true`, owner-directed,
env-toggleable; enforced on both the strict and fallback paths). The stated reason: the
engine's edge levers are call-delta-defined and do not transfer to puts.

This is a deliberate policy override of the research caveat that "bearish is
regime-conditional, not broken" (see [[bullish-direction-asymmetry]]). The asymmetry was
measured in one 2026 Q1/Q2 war-chop window, so the gate is an operating choice "for now,"
not a claim that puts are permanently dead. It is a hard gate today.

The gate lives UPSTREAM of the grounded LLM: enrichment edge-ranks to the top BULLISH
names before grounding (see [[enrichment-cost-fix-topn-thinking-cap]]).
