Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: signals_labeled_v1 bracket sweeps (regime-confounded); premium_score as a gate
Source: FINDINGS_LEDGER §Premium-Score Validation; INTELLIGENCE_BRIEF "what we know"
Date: 2026-07-17

# premium_score is anti-predictive as a gate — flags are features, not filters

On the unconditioned labeled cohort, the production filter `premium_score >= 2 AND
is_tradeable` produced **−5.53% OOS (n=46)** — **−3.54pp WORSE than no filter at all**. The
per-score means are non-monotone and small-n (Score 0 → −3.84%, 1 → −2.48%, 2 → +3.77% on
n=51). The composite is anti-predictive; component tweaks do not fix it.

Governing rule (INTELLIGENCE_BRIEF hard constraints): **premium flags are FEATURES, not
gates.** The 5 flags are functionally deterministic (Gemini-free); Gemini only powers webapp
text. Do not resurrect premium_score as a selection filter. Caveat: measured on the
regime-confounded `signals_labeled_v1` ([[labeled-v1-screen-not-validator]]).
