Status: active
Type: architecture
Tag: architecture-fact
Exit-context: applies to the paper trader's fill simulation under any bracket
Source: docs/DECISIONS/2026-06-04-pnl-sim-realism-fixes.md
Date: 2026-07-17

# Paper-trader fill realism — symmetric slippage, stale-timeout + late-fill guards

Three fixes removed an upward bias in `realized_return_pct` (all additive ledger columns;
bracket mechanics unchanged):
- **Symmetric slippage** — `SLIPPAGE_PCT = 0.02` applied BOTH sides (entry was slipped +2%
  but exits filled at the exact threshold). STOP/TRAIL fills model gap-through via
  `min(effective_stop, bar_low, bar_open)`; TIMEOUT marks-to-market at the last close with no
  slippage. `exit_slippage` records the fraction applied.
- **Stale-TIMEOUT guard** — a timeout bar from an EARLIER calendar day is tagged
  `STALE_NO_TIMEOUT_PRINT` + `illiquid_exit=True` instead of a clean TIMEOUT (a contract that
  stops printing day-1 no longer books a day-1 mark as a day-3 timeout).
- **Late/pre-market fill guard** — the 10:00 ET entry accepts a print only within
  `LATE_FILL_TOLERANCE_MIN = 30`; the bracket walk starts strictly after the entry bar so
  pre-entry bars never trigger exits.

These make the paper ledger a fair estimator; they are the trader-side complement to the
data-side [[pipeline-bug-hunt-2026-06-04]]. (Note the live exit is now same-day GIGO with a
−30% stop, [[v7-gigo-same-day-exit]]; the slippage/guard machinery is exit-agnostic.)
