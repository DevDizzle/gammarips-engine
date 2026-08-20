Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: same-day V7.1 labels (positive same-day return target)
Source: FINDINGS_LEDGER §2026-08-19 (tradeable subset); §2026-08-05 (pre-registration)
Date: 2026-08-19

# The contract_score cap-50-era lead is dead

The one lead the 2026-08-05 adjudication left open (cap-50-era, 06-11 to 07-27:
`contract_score` AUC 0.552 [0.515, 0.588] pooled, 0.564 day-demeaned) was pre-registered
for re-test once 15 fresh closed-label days accrued. **The re-test ran 2026-08-19 on
N=737 and the lead does not survive:** pooled **0.481** [0.457, 0.505], day-demeaned
0.484, tradeable-only 0.463 (n=183). A clean out-of-sample rejection of a pre-registered
hypothesis. **The question is CLOSED. Do not re-slice the cap-50 era looking for it.**

The companion fact from the same session: within-pool ranking has no demonstrated edge at
all. 14 leakage-safe features × 2 methods × 2 subsets = 56 looks produced 3 CI exclusions
of 0.50 against ~5.6 expected by chance, which is **below chance**. Stripping ghost rows
([[ghost-rows-flatter-pool-composites]]) did not reveal a hidden selection edge. It is
the second time a promising era slice on this pool dissolved out of sample
([[catalyst-atr-inversion-refuted]] was the first): treat any single-era AUC lead here as
unproven until it survives fresh days.
