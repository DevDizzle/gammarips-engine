# 2026-08-25 — Moneyness: the two owner rulings do not conflict. Scope settled

**Status:** DECIDED. Owner delegated the call to this session on 2026-08-25.
No execution behavior changes. This ADR records why, so nobody re-opens it.

## The question

Two owner rulings about moneyness existed, five weeks apart, in different repos,
with unestablished scope overlap.

- **2026-06-02, engine.** `MONEYNESS_MAX` widened 0.10 to 0.13, owner-directed.
  Evidence: realized-option-PnL backtest, N=1,375, the 10-13% increment at +8.9%
  mean, 90% CI [+0.014, +0.163]. `docs/DECISIONS/2026-06-02-moneyness-cap-widen-to-13.md`.
- **2026-07-17, gammarips-trader.** Moneyness is descriptive context only. It
  never filters and it never ranks, at any band. Evidence: re-derivation at
  n=1,806 where the 10-15% bucket did not outperform and the split halves flip
  sign, +6.3% then -9.8%.

The open question was whether the later directive binds this engine's fallback
path, which still applies a moneyness band.

## What the code actually does

This is the fact that settles it, and nobody had checked it.

`MONEYNESS_MIN` (0.05) and `MONEYNESS_MAX` (0.13) are **defined in
`signal-notifier/main.py` and never used**. Grep across signal-notifier,
enrichment-trigger, forward-paper-trader and signal-judge returns the two
definition lines and nothing else.

The strict path sets `moneyness_where = ""`. It applies no moneyness gate at all.
That has been true since the bracket tournament removed the strict selection
gates on 2026-06-04, two days after the widening shipped.

The only live moneyness gate anywhere in the engine is on the fallback path:
`FALLBACK_MONEYNESS_MIN = 0.0` and `FALLBACK_MONEYNESS_MAX = 0.10`, explicitly
pinned and explicitly NOT coupled to `MONEYNESS_MAX`.

## The ruling

**1. The 2026-06-02 ruling is SUPERSEDED, effective 2026-06-04.** It governs a
constant that stopped gating anything two days later. The bracket-tournament
decision superseded it and nobody recorded that. It is not in conflict with the
2026-07-17 directive because it does not bind any live code path.

**2. The 2026-07-17 directive is ADOPTED as engine-wide doctrine for SELECTION.**
No moneyness gate, band, floor, cap, or rank may be added to any selection path.
This changes nothing, because the strict path already does exactly that. It is
recorded so that a future session cannot re-introduce one by citing the 06-02
ruling or the 10-13 band.

**3. It does NOT bind `FALLBACK_MONEYNESS_MIN` / `FALLBACK_MONEYNESS_MAX`. The
fallback band STAYS.**

The reason is that the two do different jobs. The evidence that killed moneyness
killed it as a **predictor of returns**: it does not separate winners from
losers, and its halves flip sign. The fallback band does not claim to predict
returns. It is a **risk bound on a pick that bypassed the tournament**. The
fallback fires when the strict path yields nothing, takes `df.iloc[0]`, and is
the one selection nothing else vetted. Bounding it away from deep OTM is tail-risk
control on an unvetted pick.

"This feature does not predict returns" does not imply "no bound on this feature
is useful". Those are separate claims and only the first one was tested.

**4. Public and MCP copy: moneyness is descriptive only, at any band.** No band
number may appear in subscriber-facing copy as a thing to trade toward. This
includes 10-13. A fresh band number reads as the gate coming back, which is the
same defect with a new figure.

## Consequences

- No deploy. No behavior change. Nothing to roll back.
- `MONEYNESS_MIN` / `MONEYNESS_MAX` are dead. They stay in place with a DEAD
  marker comment, because a bare `MONEYNESS_MAX = 0.13` reads as a live 0.13
  gate and that misreading is exactly what produced this question.
- Selection research stays closed. Do NOT re-test moneyness to check this
  ruling. [[selection-research-closed]] bans it and that ban covers
  reconciliation work.

## Follow-up, not part of this ruling

The fallback band's justification comment rests on a dead exit policy. It reads
"we hold MAX 3 days on a +80/-60 bracket, so theta is negligible". V7.1 exits
same day. The band survives this ruling on the tail-risk argument above, which
does not depend on the hold period. But the comment should be restated on
same-day terms so the next reader does not inherit a 3-day rationale. That is
engineering, and it is not a policy change.

## Provenance

Found during a cross-session audit with the `gammarips-trader` harness on
2026-08-25. Both sessions flagged the scope question to the owner separately and
neither attempted to settle it by agreement. The owner then delegated the call.
