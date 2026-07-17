Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (data-contract definition)
Source: docs/DECISIONS/2026-05-09-moneyness-fix-and-trading-context-prompts.md
Date: 2026-07-17

# moneyness_pct is direction-aware (positive = OTM)

`moneyness_pct` is computed **direction-aware**, not as an absolute value:
- BULLISH (call): `(strike − spot) / spot`
- BEARISH (put): `(spot − strike) / spot`

so **positive = OTM, negative = ITM** for both directions. A 2026-05-09 fix corrected a bug
where it was `abs(strike − spot)/spot`, which let ITM contracts masquerade as OTM and pass an
OTM-band gate. This is the definition any moneyness reasoning must use
([[moneyness-band-10-13-otm]] operates on this signed value). The same decision added a
trading-context preamble to the (then Scorer/Picker) prompts.
