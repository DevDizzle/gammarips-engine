Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (picker context injection; no trader gate)
Source: docs/DECISIONS/2026-06-09-macro-sector-context-and-final-round-quant-priors.md
Date: 2026-07-17

# Macro/sector report context + quant.md priors injected at the tournament FINAL round only

The V6 tournament was blind to the macro/regime environment and sector rotation. Two matched
changes (each new report observable paired with a rule for acting on it), leakage-clean and
picker-pure — no trader gate, no rubric:
- **Report = the facts.** `overnight-report-generator` renders two deterministic,
  point-in-time (as-of scan night), fail-open sections: Macro & Regime Backdrop (FRED VIX
  level/trend, VIX/VIX3M slack, 10y/30y level/trend, risk-on/off) and a 12-ETF Sector Tape
  (momentum + drawdown-in-sigma + rotation flags). Every fetch degrades to UNKNOWN and can
  never 404 the report (an empty report strips ALL context from the tournament).
- **quant.md = the rulebook.** The hand-authored, ledger-independent priors file
  (`signal-judge/case_memory/quant.md`; `exemplars.md` deliberately excluded) is injected
  only at the CHAMPIONSHIP round (`k==1`) — **3 injections/pick, not ~30**. Rules Q13–Q18
  weigh the new context; Q19 is the delta-trap-escape prior ([[delta-trap-escape]]).

This is context for [[bracket-tournament-selection]], not a gate or a memory/rubric.
