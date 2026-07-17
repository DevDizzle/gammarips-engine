Status: active
Type: literature
Tag: literature-established
Exit-context: any hold that spans a scheduled earnings announcement
Source: De Silva/Smith/So (2026) RoF; Cao & Han (2013) JFE; Dubinsky & Johannes (2006); docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md
Date: 2026-07-17

# Earnings IV crush — never hold long single-leg options through the print

Implied volatility inflates into earnings and collapses immediately after; a long single-leg
option can lose heavily even when the direction call is right. De Silva/Smith/So (2026,
"Losing is Optional"): retail-flagged long-options trades through earnings lose **5–9% per
event, 10–14% on high-vol names** — a sample that maps directly onto our setup (large-cap,
OTM 5–15%, ~9 DTE, held through). IV-crush magnitude is 30–60% in the front month
(Dubinsky & Johannes 2006), worse on OTM short-dated strikes (near-pure vega). No literature
subset supports our trade structure through the print (the pre-EA-straddle boundary cases
require closing BEFORE the print and have compressed to negative post-2011).

The engine deliberately never backtested this on our small N — the literature settled it at
scale we cannot match. It is implemented as a hard exclusion rail at pick time
([[earnings-exclusion-rail]]); this is the epistemic model for exclusion filters
([[selection-vs-exclusion-filter-bars]]).
