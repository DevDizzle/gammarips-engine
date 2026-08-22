Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: same-day V7.1 replay (10:00 fill x 1.02 / +40% TP / -30% stop / 15:45 flat, real print at both anchors)
Source: FINDINGS_LEDGER §2026-08-22 (pool-vs-benchmark) and §2026-08-22 (liquid-universe funnel)
Date: 2026-08-22

# The scan is not a selection edge. Selection research is closed

Two pre-registered tests, run 2026-08-22, each with its decision rules written before
any data was pulled. (1) Pool-vs-benchmark, 87 days: the production pool against
liquidity-and-sector-matched controls and against random optionable controls, same
contract rule in every arm. Mean same-day return **pool -7.72%, matched -6.40%, random
-7.23%**. H1 A-B -1.33pp [-3.78, 1.04], H2 median-MFE A-B -1.57pp [-4.25, 0.92], H3 A-C
-0.50pp [-4.75, 3.84]. All three fail. (2) Liquid-universe funnel, 57 days: relative
UOA inside the top-100 liquid names against liquidity-matched random, +0.4pp [-1.7,
2.1] ([[liquid-universe-uoa-null]]).

Consequence, pre-committed in the spec's third branch: the product is the
opportunity-surface data and the liquidity machinery, never the pick. Stop spending on
selection research: no new feature searches, no re-slices, no era splits. The tests
detect ~5pp per trade and cannot detect 1-2pp, so a 1-2pp edge is not excluded, and it
is also not worth a research program. What measurably moves is executability: the liquid
universe takes UNFILLABLE from 40.5% to 6.1%. Earlier nulls this closes out:
[[ghost-rows-flatter-pool-composites]], [[contract-score-lead-dead]],
[[bracket-optimization-dead]].
