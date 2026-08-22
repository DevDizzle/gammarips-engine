Status: active
Type: finding
Tag: null-on-cohort
Exit-context: same-day MFE/MAE from a 10:00 ET fill, no bracket (pre-registered study metric)
Source: FINDINGS_LEDGER §2026-08-22 (liquid-universe funnel)
Date: 2026-08-22

# Relative UOA inside the liquid universe is indistinguishable from liquidity-matched random

Pre-registered 2026-08-20, frozen at Phase 0, run 2026-08-22. Inside the top-100 liquid
names (share volume + chain dollar volume, 25-strike floor), a call-dollar-volume z-score
>= 2.0 against each name's own 20-session baseline picked 545 legs on 57 days. Against
200 seeded draws of liquidity-matched random names with the same contract rule, same-day
median MFE reads **B 14.0% vs C 13.6%, +0.4pp, 90% CI [-1.7, 2.1]**. Both half-windows
null. The test detects ~5pp, not 1-2pp: "no large edge", never "no edge".

What the liquid universe DOES fix is executability: **UNFILLABLE 40.5% -> 6.1%,
tradeable-by-10:00 17.9% -> 63.1%** against the production pool on the same tape and
window. The random control matches those numbers, so the gain is the universe, not the
signal. Decision rule 2 of the spec: the funnel is an executability and product call for
the owner, not a signal claim. Third independent null on selection edge on top of
liquidity, after [[ghost-rows-flatter-pool-composites]] and [[contract-score-lead-dead]].
Earnings rail not applied (data limit, declared in the spec).
