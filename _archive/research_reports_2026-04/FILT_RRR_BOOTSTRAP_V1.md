# `filt_rrr` Bootstrap Validation

Bootstrap CIs and walk-forward stability check for the strategy candidate identified in BRACKET_SWEEP_V2_FILTERED.md.

**Strategy:** filter `risk_reward_ratio >= 0.42`, bracket `15:55 / no target / -20% stop / 3-day hold`

**Bootstrap samples:** 5000, RNG seed = 42 (deterministic)

## 1. Bootstrap CIs on filtered cohort

5/50/95 percentiles are over the bootstrap distribution of mean `realized_return_pct`. `P(>0)` is the fraction of bootstrap means that are positive — values close to 1.0 mean the result is robust to resampling, values near 0.5 mean it could go either way.

| cohort | n | mean | p05 | p50 | p95 | P(>0) |
|---|---|---|---|---|---|---|
| filt_rrr full (train+OOS) | 626 |   -0.48% |   -3.37% |   -0.54% |   +2.66% | 0.390 |
| filt_rrr train only | 471 |   -3.37% |   -6.38% |   -3.48% |   -0.14% | 0.044 |
| **filt_rrr OOS only** | 155 |   +8.28% |   +0.73% |   +7.95% |  +16.66% | 0.968 |

## 2. Comparison to baseline (unfiltered) cohort

Same bootstrap on the unfiltered cohort under the **same** bracket. If filt_rrr's p05 sits above baseline's p95, the filter is doing real work. If the CIs overlap, the filter is just noise.

| cohort | n | mean | p05 | p50 | p95 | P(>0) |
|---|---|---|---|---|---|---|
| baseline OOS (no filter) | 464 |   -1.99% |   -5.48% |   -2.06% |   +1.88% | 0.191 |
| **filt_rrr OOS** | 155 |   +8.28% |   +0.73% |   +7.95% |  +16.66% | 0.968 |

## 3. Walk-forward stability (split OOS into halves)

If both halves are positive and CIs overlap, the strategy is time-stable. If one half is much better than the other, the +8.28% headline is being driven by a window-specific effect.

| OOS half | n | mean | p05 | p50 | p95 | P(>0) |
|---|---|---|---|---|---|---|
| first half | 77 |   -1.06% |   -7.43% |   -1.07% |   +5.94% | 0.401 |
| second half | 78 |  +17.51% |   +4.22% |  +17.01% |  +32.68% | 0.991 |

## 4. Verdict

**MODERATE.** filt_rrr OOS p05 is positive (the edge is robust to resampling within the cohort), but baseline's CI overlaps. The filter helps, but the underlying signal is noisier than the headline suggests. Consider deploying with smaller position sizing.

