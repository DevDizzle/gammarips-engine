# Bracket Sweep V1

**Source bars:** `/tmp/signal_bars_v1.pkl` (cached Polygon minute bars, 15-day window)  
**Sweep results:** `/tmp/sweep_results_v1.parquet`  
**Per-signal detail (best variant):** `/tmp/sweep_signal_detail_v1.pkl`  
**Variants tried:** 840  
**Best OOS variant:** `15:55 / tgt=none / stop=-20% / hold=3d`

## 1. Sweep overview

- **Variants tested:** 840
- **Min n_executed across variants:** 1552
- **Max n_executed across variants:** 1552
- **Median n_executed:** 1552
- **Variants with **positive in-sample avg_return:** 0 / 840
- **Variants with **positive OOS avg_return:** 0 / 840

## 2. Top 20 variants by **out-of-sample** avg_return

Sorted by chronological-holdout test_avg (newer 30% of scan_dates). OOS is the only number that matters; in-sample is shown for sanity.

| rank | variant | n | avg | win% | **OOS n** | **OOS avg** | **OOS win%** | OOS targ/stop/to |
|---|---|---|---|---|---|---|---|---|
| 1 | 15:55 / tgt=none / stop=-20% / hold=3d | 1552 |   -2.15% |  21.3% | 464 | **  -1.99%** |  19.6% | 0/354/110 |
| 2 | 15:45 / tgt=none / stop=-20% / hold=3d | 1552 |   -2.41% |  21.3% | 464 | **  -2.30%** |  19.4% | 0/355/109 |
| 3 | 15:30 / tgt=none / stop=-20% / hold=3d | 1552 |   -2.47% |  21.3% | 464 | **  -2.58%** |  19.0% | 0/357/107 |
| 4 | 15:55 / tgt=+150% / stop=-20% / hold=3d | 1552 |   -1.34% |  22.0% | 464 | **  -2.60%** |  20.0% | 16/352/96 |
| 5 | 15:55 / tgt=+200% / stop=-20% / hold=3d | 1552 |   -1.81% |  21.5% | 464 | **  -2.64%** |  19.6% | 10/354/100 |
| 6 | 15:45 / tgt=+200% / stop=-20% / hold=5d | 1552 |   -2.01% |  17.5% | 464 | **  -2.69%** |  17.5% | 16/371/77 |
| 7 | 15:55 / tgt=+200% / stop=-20% / hold=5d | 1552 |   -1.80% |  17.6% | 464 | **  -2.72%** |  17.5% | 16/371/77 |
| 8 | 15:45 / tgt=none / stop=-20% / hold=5d | 1552 |   -3.66% |  16.6% | 464 | **  -2.73%** |  17.0% | 0/373/91 |
| 9 | 15:55 / tgt=none / stop=-20% / hold=5d | 1552 |   -3.51% |  16.8% | 464 | **  -2.79%** |  17.0% | 0/373/91 |
| 10 | 15:45 / tgt=+200% / stop=-20% / hold=3d | 1552 |   -2.09% |  21.5% | 464 | **  -2.95%** |  19.4% | 10/355/99 |
| 11 | 15:55 / tgt=+150% / stop=-20% / hold=5d | 1552 |   -1.60% |  18.4% | 464 | **  -2.95%** |  18.1% | 23/368/73 |
| 12 | 15:45 / tgt=+150% / stop=-20% / hold=3d | 1552 |   -1.52% |  22.0% | 464 | **  -3.02%** |  19.8% | 15/353/96 |
| 13 | 15:30 / tgt=none / stop=-20% / hold=5d | 1552 |   -3.73% |  16.4% | 464 | **  -3.09%** |  16.4% | 0/375/89 |
| 14 | 15:30 / tgt=+200% / stop=-20% / hold=5d | 1552 |   -2.23% |  17.3% | 464 | **  -3.12%** |  16.8% | 16/373/75 |
| 15 | 15:30 / tgt=+200% / stop=-20% / hold=3d | 1552 |   -2.22% |  21.5% | 464 | **  -3.17%** |  19.0% | 10/357/97 |
| 16 | 15:00 / tgt=none / stop=-20% / hold=5d | 1552 |   -3.82% |  16.2% | 464 | **  -3.17%** |  16.6% | 0/373/91 |
| 17 | 15:55 / tgt=+150% / stop=-20% / hold=2d | 1552 |   -0.79% |  25.8% | 464 | **  -3.17%** |  22.0% | 13/336/115 |
| 18 | 15:00 / tgt=+200% / stop=-20% / hold=5d | 1552 |   -2.86% |  16.9% | 464 | **  -3.22%** |  17.0% | 15/371/78 |
| 19 | 15:30 / tgt=+150% / stop=-20% / hold=3d | 1552 |   -1.76% |  22.0% | 464 | **  -3.23%** |  19.4% | 15/355/94 |
| 20 | 15:45 / tgt=+150% / stop=-20% / hold=5d | 1552 |   -1.90% |  18.2% | 464 | **  -3.29%** |  17.9% | 22/369/73 |

## 3. Best OOS variant per dimension

For each value of one dimension, the best OOS variant across all other dimensions. This shows whether one knob dominates or whether the result is a multi-knob interaction.

### Best per `entry_time`

| value | best variant | OOS avg | OOS win% | OOS n |
|---|---|---|---|---|
| 15:00 | 15:00 / tgt=none / stop=-20% / hold=5d |   -3.17% |  16.6% | 464 |
| 15:30 | 15:30 / tgt=none / stop=-20% / hold=3d |   -2.58% |  19.0% | 464 |
| 15:45 | 15:45 / tgt=none / stop=-20% / hold=3d |   -2.30% |  19.4% | 464 |
| 15:55 | 15:55 / tgt=none / stop=-20% / hold=3d |   -1.99% |  19.6% | 464 |

### Best per `target_pct`

| value | best variant | OOS avg | OOS win% | OOS n |
|---|---|---|---|---|
| none | 15:55 / tgt=none / stop=-20% / hold=3d |   -1.99% |  19.6% | 464 |
| +25% | 15:55 / tgt=+25% / stop=-20% / hold=5d |   -6.05% |  31.5% | 464 |
| +50% | 15:55 / tgt=+50% / stop=-20% / hold=5d |   -3.71% |  24.8% | 464 |
| +75% | 15:45 / tgt=+75% / stop=-20% / hold=5d |   -3.71% |  20.7% | 464 |
| +100% | 15:55 / tgt=+100% / stop=-20% / hold=3d |   -3.45% |  20.5% | 464 |
| +150% | 15:55 / tgt=+150% / stop=-20% / hold=3d |   -2.60% |  20.0% | 464 |
| +200% | 15:55 / tgt=+200% / stop=-20% / hold=3d |   -2.64% |  19.6% | 464 |

### Best per `stop_pct`

| value | best variant | OOS avg | OOS win% | OOS n |
|---|---|---|---|---|
| none | 15:55 / tgt=none / stop=none / hold=5d |   -8.16% |  33.6% | 464 |
| -20% | 15:55 / tgt=none / stop=-20% / hold=3d |   -1.99% |  19.6% | 464 |
| -35% | 15:00 / tgt=+200% / stop=-35% / hold=5d |   -7.59% |  23.3% | 464 |
| -50% | 15:00 / tgt=none / stop=-50% / hold=5d |   -8.69% |  28.4% | 464 |
| -75% | 15:45 / tgt=none / stop=-75% / hold=5d |   -9.33% |  33.4% | 464 |

### Best per `hold_days`

| value | best variant | OOS avg | OOS win% | OOS n |
|---|---|---|---|---|
| 2 | 15:55 / tgt=+150% / stop=-20% / hold=2d |   -3.17% |  22.0% | 464 |
| 3 | 15:55 / tgt=none / stop=-20% / hold=3d |   -1.99% |  19.6% | 464 |
| 5 | 15:45 / tgt=+200% / stop=-20% / hold=5d |   -2.69% |  17.5% | 464 |
| 7 | 15:55 / tgt=+50% / stop=-20% / hold=7d |   -3.99% |  23.9% | 464 |
| 10 | 15:55 / tgt=+50% / stop=-20% / hold=10d |   -4.19% |  23.7% | 464 |
| 15 | 15:55 / tgt=+50% / stop=-20% / hold=15d |   -4.16% |  23.7% | 464 |

## 4. Best variant deep-dive: `15:55 / tgt=none / stop=-20% / hold=3d`

- n = 1552, all-cohort avg =   -2.15%, win% =  21.3%
- OOS n = 464, OOS avg =   -1.99%, OOS win% =  19.6%

### Breakdown by `premium_score`

| premium_score | n | avg_return | win% |
|---|---|---|---|
| 0.0 | 1106 |   -0.74% |  21.3% |
| 1.0 | 394 |   -5.86% |  21.1% |
| 2.0 | 51 |   -3.66% |  21.6% |
| 3.0 | 1 |  -20.00% |   0.0% |

### Breakdown by `direction`

| direction | n | avg_return | win% |
|---|---|---|---|
| BEARISH | 815 |   -3.93% |  21.1% |
| BULLISH | 737 |   -0.18% |  21.4% |

### Breakdown by `recommended_oi` (quintiles)

| recommended_oi | n | avg_return | win% |
|---|---|---|---|
| (-0.001, 2.0] | 329 |   +0.41% |  23.1% |
| (2.0, 17.0] | 296 |   -3.17% |  22.0% |
| (17.0, 97.0] | 307 |   +3.75% |  25.7% |
| (97.0, 794.8] | 309 |   -5.14% |  17.5% |
| (794.8, 92920.0] | 311 |   -6.74% |  18.0% |

### Breakdown by `recommended_volume` (quintiles)

| recommended_volume | n | avg_return | win% |
|---|---|---|---|
| (9.999, 28.0] | 312 |   -0.14% |  25.3% |
| (28.0, 126.4] | 309 |   -1.84% |  22.0% |
| (126.4, 516.4] | 310 |   +0.77% |  23.5% |
| (516.4, 2066.4] | 310 |   -1.91% |  18.7% |
| (2066.4, 43234.0] | 311 |   -7.62% |  16.7% |

### Breakdown by `recommended_dte` (quintiles)

| recommended_dte | n | avg_return | win% |
|---|---|---|---|
| (6.999, 13.0] | 345 |   -2.55% |  15.1% |
| (13.0, 20.0] | 286 |   -0.83% |  21.3% |
| (20.0, 27.0] | 307 |   -4.79% |  20.5% |
| (27.0, 34.8] | 303 |   +0.26% |  24.1% |
| (34.8, 45.0] | 311 |   -2.66% |  26.0% |

### Breakdown by `recommended_spread_pct` (quintiles)

| recommended_spread_pct | n | avg_return | win% |
|---|---|---|---|
| (-0.001, 0.0734] | 311 |   +0.38% |  27.3% |
| (0.0734, 0.168] | 310 |   -2.56% |  22.6% |
| (0.168, 0.256] | 311 |   +2.78% |  21.5% |
| (0.256, 0.333] | 323 |   -4.82% |  17.3% |
| (0.333, 0.4] | 297 |   -6.63% |  17.5% |

### Breakdown by `recommended_mid_price` (quintiles)

| recommended_mid_price | n | avg_return | win% |
|---|---|---|---|
| (0.049, 1.21] | 313 |   -1.60% |  19.8% |
| (1.21, 2.67] | 310 |   -4.40% |  20.6% |
| (2.67, 5.296] | 308 |   +1.13% |  22.4% |
| (5.296, 10.844] | 310 |   -3.24% |  23.2% |
| (10.844, 101.0] | 311 |   -2.62% |  20.3% |

## 5. Red-flag check (simulator-artifact concentration)

Per the V3.1 decision note, the simulator's mid-bar pricing materially overstates fillable prices on illiquid contracts. If the best variant concentrates its winners in low-OI / high-spread / low-mid-price buckets, those wins are likely fictional.

| feature | winners median | losers median | winners mean | losers mean | flag |
|---|---|---|---|---|---|
| `recommended_oi` | 29.000 | 45.000 | 943.070 | 1429.641 | |
| `recommended_volume` | 192.000 | 288.500 | 940.873 | 1479.843 | |
| `recommended_spread_pct` | 0.182 | 0.221 | 0.181 | 0.210 | |
| `recommended_mid_price` | 3.980 | 3.855 | 6.722 | 7.069 | |
| `recommended_dte` | 27.000 | 23.000 | 25.694 | 23.223 | |

**Returns excluding suspicious buckets:**

| filter | n | avg | win% |
|---|---|---|---|
| ALL | 1552 |   -2.15% |  21.3% |
| oi >= 50 | 740 |   -3.55% |  19.5% |
| oi >= 100 | 616 |   -5.89% |  17.9% |
| oi >= 50 AND vol >= 100 | 657 |   -3.00% |  19.5% |
| mid_price >= 1.00 | 1309 |   -2.60% |  21.5% |
| spread_pct <= 0.20 | 735 |   -0.08% |  24.6% |
| oi>=50 AND vol>=100 AND mid>=1 AND spread<=0.20 | 114 |   +0.96% |  26.3% |

## 6. Realistic 1-trade-per-scan_date strategy

User goal is 1 trade per scan_date (or even 1 per week). For each scan_date, pick the highest `premium_score` signal (tiebreak: highest `recommended_oi`). This is the realistic execution path under the best variant.

- **Picks:** 27 (one per scan_date)
- **All-cohort avg:**   -9.49%, win% =  18.5%
- **OOS avg:**   -3.61%, OOS win% =  22.2%, OOS n = 9

- **Cumulative P&L** at $1000/trade: $-2,563 over 27 trades (avg $-94.9/trade)
- **Max drawdown** in cumulative curve: $-2,550

