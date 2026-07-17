Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-06-04-contract-selection-liquidity.md
Date: 2026-07-17

# Contract selection rewards TRADEABILITY, not unusualness (OI-primary)

`_best_contract` (the scanner's strike picker) scores contracts to optimize **tradeability**:
open interest is the PRIMARY term (`min(oi/200,1)*5.0` — standing size that accumulates and
can't be faked by one sweep), volume secondary, snapshot spread weighted lightly (it is
noisy / unreliable).

Why: the old score REWARDED low OI via a `min(vol/max(oi,1),3)*1.5` V/OI term, so among
OKTA's calls it picked the $127 swept lottery strike (OI 5, ~35% live spread, untradeable)
over the fillable $130 (OI 48) — the V/OI term scored the illiquid strike higher BECAUSE it
was illiquid, and the snapshot spread recorded 0.5% when the live spread was 35%. The whole
liquidity saga in one function: unusual flow is the right signal for the NAME + DIRECTION,
but using that same unusualness to pick the CONTRACT hands you the strike you can't trade.
Complements [[oi-not-quality-signal]] (OI is a fillability signal, not a quality lever) and
the fabricated-spread fix ([[pipeline-bug-hunt-2026-06-04]]).
