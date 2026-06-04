# 2026-06-04 — Contract selection rewards tradeability, not unusualness

**Status:** IMPLEMENTED in the scanner (`_best_contract`). Deploy = overnight-scanner; takes effect next overnight scan.

## The bug
`_best_contract` (`src/enrichment/core/pipelines/overnight_scanner.py`) scores every chain contract and picks the max. The old score **rewarded low open interest**:

```
+ min(vol / max(oi, 1), 3.0) * 1.5   # V/OI — high when OI is near zero
```

So among OKTA's 6/12 calls it picked the **$127 swept lottery strike** (OI 5, ~35% *live* spread, untradeable) over the **$130 standard strike** (OI 48, fillable). The $127 won the V/OI term by ~+4 points *because* it's illiquid. The snapshot spread term piled on, scoring the $127 at a recorded **0.5%** spread that was actually **35%** live — scan-time spread is unreliable.

This is the whole liquidity saga in one function: unusual flow is the right signal for the **name + direction**, but using that same unusualness to pick the **contract** hands you the strike you can't trade.

## The fix
Rewrite the score to optimize **tradeability**. Open interest is the primary signal (standing size, accumulates over time, can't be faked by a single sweep); volume secondary; the snapshot spread is weighted lightly because it's noisy.

```
score =  min(oi/200, 1.0)*5.0                 # OI — PRIMARY liquidity
       + min(vol/200, 1.0)*2.0                # volume — secondary
       + (1.0 - spread_pct)*1.5               # spread — tertiary (snapshot-noisy)
       + (2.0 if 0.25<=delta<=0.50 else 0)    # sweet-spot delta
       + gamma*8.0                            # convexity (de-emphasized from 20x)
       - theta_drag                           # theta penalty
```

On the OKTA example this flips the pick to the **$130** (OI term: +1.2 vs +0.1), even though the $127's fake-tight spread still helps it a little — OI now dominates.

## What this does NOT change (deliberately)
- **No hard OI floor.** Scan-time OI is stale (a fresh sweep that builds OI overnight reads ~0 at scan — CAR went 3→103). A hard OI filter would re-introduce the staleness problem and reject contracts that recover. We only *prefer* OI in the score; we don't reject low-OI strikes outright.
- The hard filters stay: `spread_pct <= 0.40`, `vol >= 10`, DTE 7–90, moneyness 0.90–1.25.

## Next layer (separate)
The scorer uses scan-time data, which is unreliable for absolute fillability. The belt-and-suspenders is a **live fillability check at pick time** (07:30–10:00 ET): pull a fresh Polygon quote for the finalist contracts, compute the *real* bid/ask spread + depth, and take the highest-ranked finalist you can actually fill (else skip). That uses live data at the moment it matters; this scorer fix just stops actively selecting the ghost.
