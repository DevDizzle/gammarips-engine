# Trailing-liquidity backtest — 2026-05-19

Source: `profitscout-fida8.profit_scout.overnight_signals_enriched` (`recommended_contract IS NOT NULL AND is_win IS NOT NULL`).
N = 1,940.  Scan-date range: 2026-04-10 → 2026-05-14.

Feature: `active_days_20d` = number of the 20 US business days strictly before scan_date on which the OCC contract printed any volume (Polygon `/v2/aggs/.../1/day`, zero-filled to a 20-session grid).
Fillability: at least one `/v2/aggs/.../1/minute` bar with `v>0` on the next US business day after scan_date.

## Section A — Fillability by `active_days_20d` bucket

| Bucket | N | % fillable | N fillable |
|---|---:|---:|---:|
| [0-3] | 1403 | 50.0% | 701 |
| [4-7] | 308 | 62.7% | 193 |
| [8-13] | 164 | 74.4% | 122 |
| [14-20] | 65 | 87.7% | 57 |
| **All** | 1940 | 55.3% | 1073 |

## Section B — Edge by bucket (filled-only rows)

Filled-only N = 1073 of 1940 (55.3%).

| Bucket | N | Win rate | Mean d1 % | Mean d3 % | Mean peak_3d % |
|---|---:|---:|---:|---:|---:|
| [0-3] | 701 | 79.0% | 0.97% | 1.58% | 5.69% |
| [4-7] | 193 | 71.0% | 0.85% | 1.37% | 4.72% |
| [8-13] | 122 | 76.2% | 0.73% | 1.22% | 4.83% |
| [14-20] | 57 | 73.7% | 0.52% | 1.50% | 4.23% |

### Outcome-tier distribution (filled-only)

| Bucket | directional | flat | home_run | strong | wrong |
|---|---:|---:|---:|---:|---:|
| [0-3] | 152 (22%) | 78 (11%) | 280 (40%) | 122 (17%) | 69 (10%) |
| [4-7] | 45 (23%) | 29 (15%) | 60 (31%) | 32 (17%) | 27 (14%) |
| [8-13] | 28 (23%) | 13 (11%) | 43 (35%) | 22 (18%) | 16 (13%) |
| [14-20] | 9 (16%) | 6 (11%) | 19 (33%) | 14 (25%) | 9 (16%) |

## Section C — Cohort impact at gate `active_days_20d >= 8`

- Retained: 229 / 1,940 (11.8%)
- Filtered: 1,711 (88.2%)
- Win rate kept = 75.5%, filtered = 77.6%, all = 77.4%
- Fillability kept = 78.2%, filtered = 52.3%
- Trading days in window: 25
- Days with ZERO surviving candidates under this gate: 0 (0.0%)

### Threshold sweep

| Threshold | % retained | Win rate kept | Win rate filtered | Fill % kept | Days with zero survivors |
|---:|---:|---:|---:|---:|---:|
| >= 3 | 36.9% | 75.8% | 78.3% | 66.9% | 0 |
| >= 5 | 21.9% | 74.8% | 78.1% | 71.2% | 0 |
| >= 8 | 11.8% | 75.5% | 77.6% | 78.2% | 0 |
| >= 10 | 7.6% | 75.7% | 77.5% | 83.1% | 0 |
| >= 12 | 4.8% | 75.5% | 77.5% | 86.2% | 1 |
| >= 15 | 2.6% | 76.5% | 77.4% | 92.2% | 4 |

## Section D — Cross-tab `active_days_20d` × `overnight_score`

| Bucket | score=1 | score=2 | score=3 | score=4 | score=5 | score=6 | score=7 | score=8 | score=9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [0-3] | 75% (n=48) | 80% (n=165) | 73% (n=154) | 81% (n=293) | 78% (n=296) | 79% (n=277) | 78% (n=136) | 85% (n=33) | 100% (n=1) |
| [4-7] | 85% (n=13) | 72% (n=43) | 76% (n=37) | 79% (n=75) | 62% (n=65) | 80% (n=46) | 73% (n=26) | 0% (n=3) | — |
| [8-13] | 70% (n=10) | 62% (n=32) | 75% (n=28) | 73% (n=33) | 88% (n=32) | 84% (n=19) | 75% (n=8) | 100% (n=2) | — |
| [14-20] | 100% (n=4) | 71% (n=21) | 86% (n=7) | 76% (n=17) | 62% (n=8) | 60% (n=5) | 100% (n=3) | — | — |

## Section E — Recommendation

Headline: at threshold `active_days_20d >= 8`, fillability improves by 25.9 pp (kept 78.2% vs filtered 52.3%) and win rate moves by -2.1 pp (kept 75.5% vs filtered 77.6%) while retaining 11.8% of historical signals; 0/25 days would have zero survivors.

