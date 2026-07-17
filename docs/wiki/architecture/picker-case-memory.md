Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (picker input design)
Source: docs/DECISIONS/2026-06-03-picker-case-memory.md
Date: 2026-07-17

# Picker priors are curated MD injected as instruction blocks, not RAG

The picker's priors are delivered as **curated Markdown injected as fenced instruction
blocks** (deterministic + auditable), deliberately NOT an ADK MemoryService / RAG
(session-recall is the wrong tool). Two files under the judge's `case_memory/`:
- `quant.md` — hand-authored, ledger-independent priors (Q1–Q12 originally: earnings
  exclusion, spent-catalyst, VRP, short-DTE theta cliff, convexity, moneyness, direction-EV
  asymmetry, timeout dominance, hedging flow, oversold-fade, contango, speed; later extended
  Q13–Q19).
- `exemplars.md` — a bounded curated subset of the bull/bear case library.

This is the ancestor of the current tournament's context injection: under V7 the tournament
loads **quant.md ONLY** and injects it at the CHAMPIONSHIP round
([[quant-md-final-round-priors]]) — `exemplars.md` is deliberately excluded and there is no
per-day ledger memory (the tournament prompt is otherwise memory/rubric/weight-free,
[[bracket-tournament-selection]]).
