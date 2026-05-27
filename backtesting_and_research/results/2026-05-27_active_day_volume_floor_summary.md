# Active-day volume-floor sweep — 2026-05-27

Redefines an 'active day' as `vol >= MIN_DAILY_VOL` (was `vol > 0`) in the signal-notifier liquidity gate. Goal: pick the smallest floor that maximizes entry-day fillability with zero V5.4-eligible dry days.

## Part 1 — Entry-day fillability under gate `active_days(vol>=N) >= 5`

Cohort: prior backtest CSV, N=1,940, scan 2026-04-10 → 2026-05-14. Fillability label = >=1 entry-day minute bar with v>0.

| MIN_DAILY_VOL | retained | retain % | fill% kept | fill% filtered | fill lift (pp) |
|---:|---:|---:|---:|---:|---:|
| 1 | 424 | 21.9% | 71.2% | 50.9% | +15.9 |
| 5 | 143 | 7.4% | 83.2% | 53.1% | +27.9 |
| 10 | 83 | 4.3% | 88.0% | 53.9% | +32.6 |
| 25 | 37 | 1.9% | 86.5% | 54.7% | +31.2 |
| 50 | 20 | 1.0% | 75.0% | 55.1% | +19.7 |

(baseline fillability across all 1,940 rows = 55.3%)

## Part 2 — V5.4-eligible funnel impact (dry-day constraint)

Eligible cohort (Scenario-C BQ gates only; VIX/earnings not replayed, so candidates are an upper bound): N=87 over 24 scan days, 2026-04-17 → 2026-05-22.

| MIN_DAILY_VOL | candidates kept | retain % | median/day | dry days |
|---:|---:|---:|---:|---:|
| 1 | 50 | 57.5% | 2.0 | 2 |
| 5 | 23 | 26.4% | 1.0 | 10 |
| 10 | 9 | 10.3% | 0.0 | 17 |
| 25 | 3 | 3.4% | 0.0 | 22 |
| 50 | 1 | 1.1% | 0.0 | 23 |

## Part 3 — Named contract spot-check (ACTIVE_DAYS_MIN=5)

| ticker | scan | expected | ad@vol>=1 | ad@vol>=5 | ad@vol>=10 | ad@vol>=25 | ad@vol>=50 |
|---|---|---|---:|---:|---:|---:|---:|
| OKTA | 2026-05-12 | PASS (real fill) | 5✓ | 2✗ | 2✗ | 2✗ | 2✗ |
| KBR | 2026-05-13 | REJECT (incident) | 3✗ | 1✗ | 1✗ | 1✗ | 1✗ |
| HTZ | 2026-05-14 | PASS (real fill +80%) | 3✗ | 1✗ | 0✗ | 0✗ | 0✗ |
| BBY | 2026-05-18 | PASS (real fill +15%) | 6✓ | 1✗ | 1✗ | 0✗ | 0✗ |
| EQIX | 2026-05-20 | REJECT (INVALID_LIQUIDITY) | 6✓ | 1✗ | 0✗ | 0✗ | 0✗ |
| BLK | 2026-05-21 | REJECT (no entry bars) | 12✓ | 0✗ | 0✗ | 0✗ | 0✗ |

✓ = passes gate (active_days >= 5), ✗ = rejected.

