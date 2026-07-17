Status: superseded
Type: finding
Tag: literature-established
Exit-context: exclusion-style literature tightenings on the V5.3 3-day stack
Source: docs/DECISIONS/2026-05-06-lit-audit-h11-h12-spread-moneyness.md
Date: 2026-07-17

# H11 spread 10→8% and H12 moneyness 15→10% — literature tightenings, both superseded

On 2026-05-06 two exclusion-style literature tightenings deployed off the V5.3 lit audit
([[literature-audit-v5-3-stack]]): **H11** tightened `recommended_spread_pct` 10%→8% at
enrichment (Muravyev-Pearson / Mayhew), and **H12** tightened moneyness 5–15%→5–10% at
signal-notifier (Aretz deep-OTM EV cliff). Both were deployed on mechanism, not a backtest
([[selection-vs-exclusion-filter-bars]]).

Both are superseded: the spread gate is permanently retired because this Polygon plan serves
no quotes ([[spread-gate-retired]]); and the moneyness cap was later re-widened to 0.13 after
a realized-option-PnL backtest showed the 10–13% increment is additive and that the H12
literature was a hold-to-expiry result that does not bind our short bracket
([[moneyness-band-10-13-otm]]).
