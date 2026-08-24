Status: active
Type: architecture
Tag: funnel
Exit-context: n/a (selection-universe change, exit mechanics unchanged)
Source: docs/DECISIONS/2026-08-24-liquid-universe-funnel.md
Date: 2026-08-24

# The scan universe is liquidity-first, not movers

Shipped 2026-08-24 on executability grounds, owner call. The scanner no longer keeps
universe names by `|price change| >= 1%`. It keeps the most liquid names by session
share volume (3M floor, pre-rank top 300), prices their chains, then ranks to the top
100 by `z_cross(log1p(chain dollar volume)) + z_cross(log1p(share volume))` with a
25-listed-strike floor. Open interest is not an input: no OI history exists in this
stack, so ranking on a current snapshot would be lookahead.

**This is not an edge claim.** [[liquid-universe-uoa-null]] found the selection signal
on top of the liquid universe is null, and [[selection-research-closed]] found the
production pool is not distinguishable from matched random contracts. The change ships
because the old funnel selected contracts that were HARDER to trade than random liquid
ones: 40.5% of pool legs unfillable at 10:00 ET against 6.1%, tradeable 17.9% against
63.1%. Fills, not returns.

The $500K directional UOA floor was dropped with it (owner call, same session). It
belonged to the UOA-first funnel; inside a liquid universe every name already carries
heavy flow, so it only thinned the pool, 44 BULLISH names to 30 on a 2026-08-24 midday
screen. Pool depth now floats with the market and a down day gives a smaller pool by
design. Cohort reset to 2026-08-25, `policy_version` unchanged. Kill switches:
`LIQUID_UNIVERSE`, `ENRICH_LIQUID_ONLY`, `ENRICH_UOA_FLOOR`.
