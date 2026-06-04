# BEARISH case-memory

_Generated 2026-06-03 23:05Z by build_case_memory.py — DO NOT hand-edit; regenerate._

**Corpus:** 529 closed bearish trades · 170 WON / 359 LOST · mean option return -7.7% · 2 live / 527 backtest.

> Backtest cases span 2026-04-10 → 2026-06-01 — a single 2026-Q2 war-chop regime (vix3m ~20-21). Treat distilled PATTERNS as signal and individual case outcomes as anecdote. Live cases supersede backtest on the same contract.

> Outcome = realized option PnL (`realized_ret>0`), NOT `is_win` (stock direction). They disagree ~44% of the time — the gap is the lesson.

---

## LIVE (V5.4 ledger — authoritative)  (2)

```
CASE HTZ-2026-05-14-S  ·  BEARISH  ·  WON  ·  [live_ledger]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 2.26 · spread +0.0%
  greeks Δ-0.341 Γ0.2542 Θ-0.009 · IV 0.883 · mid 0.34
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Miss (0.70) · RSI 48
  headline "Hertz COO Sells Shares as Analyst Downgrades and Earnings Hangover Pressure Stock"
WHY
  underlying -5.1%/-10.8%/-15.4% (favorable peak +15.9%); position move +15.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~90% · IV residual ~-2% [inferred].
  convexity Γ·S = 1.48. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE OKTA-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [live_ledger]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 2.27 · spread +0.1%
  greeks Δ-0.327 Γ0.0227 Θ-0.123 · IV 0.802 · mid 3.02
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.45) · RSI 54
  headline "Freshworks and Okta shares are falling, what you need to know"
WHY
  underlying -1.1%/+2.5%/+4.7% (favorable peak +2.0%); position move -4.7%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-40% · IV residual ~50% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

---

## BACKTEST · WON  (169)

```
CASE DHI-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ-0.445 Γ0.0281 Θ-0.258 · IV 0.538 · mid 5.98
  overnight_score 6 · flow HEDGING · catalyst Earnings Beat (0.90) · RSI 64
  headline "D.R. Horton Reports Second Quarter 2026 Results; Stock Gains 2.4%"
WHY
  underlying +5.8%/+5.1%/+7.1% (favorable peak -4.3%); position move -7.1%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-81% · IV residual ~194% [inferred].
  convexity Γ·S = 4.31. exit TRAIL → realized +100%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FICO-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 0.19 · spread +0.1%
  greeks Δ-0.400 Γ0.0018 Θ-1.718 · IV 0.803 · mid 62.83
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 43
  headline "Fair Isaac Corporation Announces Date for Reporting of Second Quarter Fiscal 2026 Financial Results"
WHY
  underlying -6.4%/-5.5%/-3.1% (favorable peak +16.1%); position move +3.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~20% · IV residual ~68% [inferred].
  convexity Γ·S = 1.88. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE BSX-2026-05-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 3.00 · spread +0.0%
  greeks Δ-0.193 Γ0.0447 Θ-0.030 · IV 0.391 · mid 0.80
  overnight_score 4 · flow MIXED · catalyst — (—) · RSI 47
WHY
  underlying +1.1%/+0.9%/-11.7% (favorable peak +12.4%); position move +11.7%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~161% · IV residual ~-70% [inferred].
  convexity Γ·S = 2.56. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ACN-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 6.00 · spread +0.0%
  greeks Δ-0.308 Γ0.0137 Θ-0.119 · IV 0.408 · mid 13.32
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 47
  headline "Accenture (ACN) Hits Fresh 52-Week Lows as Revenue Guidance Miss Outweighs AI Partnership Momentum"
WHY
  underlying -0.3%/-2.5%/-8.6% (favorable peak +10.4%); position move +8.6%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~39% · IV residual ~44% [inferred].
  convexity Γ·S = 2.67. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FUBO-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 3.75 · spread +0.0%
  greeks Δ-0.371 Γ0.1952 Θ-0.016 · IV 0.750 · mid 0.37
  overnight_score 6 · flow HEDGING · catalyst Earnings Miss (0.90) · RSI 38
  headline "Fubo hits record $1.57B revenue but loses 200K subscribers after Disney deal"
WHY
  underlying +3.5%/-1.4%/-4.6% (favorable peak +6.1%); position move +4.6%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~48% · IV residual ~45% [inferred].
  convexity Γ·S = 2.04. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HTZ-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 15 · V/OI 1.38 · spread +0.0%
  greeks Δ-0.480 Γ0.3831 Θ-0.013 · IV 0.855 · mid 0.41
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.70) · RSI 49
  headline "Jefferies Raises Hertz (HTZ) Price Target to $6.00 Following Revenue Beat, Cites Tenuous Liquidity"
WHY
  underlying -1.2%/-6.3%/-11.9% (favorable peak +14.0%); position move +11.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~82% · IV residual ~8% [inferred].
  convexity Γ·S = 2.26. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE TYL-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 3.67 · spread +0.0%
  greeks Δ-0.669 Γ0.0171 Θ-0.426 · IV 0.433 · mid 14.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 43
  headline "Tyler Technologies Leans On FTR Deal To Accelerate Cloud And AI Shift Amid Insider Selling Concerns"
WHY
  underlying +3.3%/+1.2%/-2.6% (favorable peak +4.1%); position move +2.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~40% · IV residual ~49% [inferred].
  convexity Γ·S = 5.49. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WBD-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 1.00 · spread +0.0%
  greeks Δ-0.296 Γ0.1736 Θ-0.009 · IV 0.241 · mid 0.15
  overnight_score 5 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 36
  headline "Warner Bros. Discovery Sets Shareholder Meeting Date of April 23, 2026 to Approve Transaction with Paramoun…"
WHY
  underlying +0.6%/-0.3%/+0.2% (favorable peak +1.1%); position move -0.2%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-10% · IV residual ~108% [inferred].
  convexity Γ·S = 4.67. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ABT-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ-0.309 Γ0.0465 Θ-0.038 · IV 0.257 · mid 1.31
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.90) · RSI 25
  headline "Abbott Cuts Profit Forecast After $21 Billion Deal, Shares Fall 6% to 52-Week Low"
WHY
  underlying +1.4%/+0.6%/-2.9% (favorable peak +2.9%); position move +2.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~65% · IV residual ~24% [inferred].
  convexity Γ·S = 4.44. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE APP-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 6.05 · spread +0.1%
  greeks Δ-0.467 Γ0.0051 Θ-1.802 · IV 1.091 · mid 32.66
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 53
  headline "AppLovin (APP) Surges After Crushing Q1 Estimates and Raising Guidance on Strong Ad Tech Demand"
WHY
  underlying +6.4%/-0.1%/+2.0% (favorable peak +5.5%); position move -2.0%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-14% · IV residual ~110% [inferred].
  convexity Γ·S = 2.41. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CMG-2026-05-27-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.302 Γ0.1278 Θ-0.030 · IV 0.406 · mid 0.55
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 47
  headline "Chipotle brings back 'Summer of Extras' with free burritos, bonus points and exclusive offers"
WHY
  underlying -0.8%/-2.5%/-6.5% (favorable peak +6.8%); position move +6.5%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~118% · IV residual ~-21% [inferred].
  convexity Γ·S = 4.18. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HUBS-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI 0.12 · spread +0.0%
  greeks Δ-0.345 Γ0.0055 Θ-0.286 · IV 0.841 · mid 20.33
  overnight_score 2 · flow HEDGING · catalyst Analyst Downgrade (0.95) · RSI 37
  headline "HubSpot shares plunge as Citi and William Blair lead wave of analyst downgrades following Q1 results"
WHY
  underlying +3.6%/-16.1%/-18.6% (favorable peak +23.2%); position move +18.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~74% · IV residual ~10% [inferred].
  convexity Γ·S = 1.29. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE INOD-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 2.17 · spread +0.0%
  greeks Δ-0.264 Γ0.0114 Θ-0.623 · IV 3.382 · mid 6.81
  overnight_score 2 · flow HEDGING · catalyst Guidance Raise (1.00) · RSI 86
  headline "INOD Stock Surges Overnight As AI Spending Wave Fuels Record Q1: CEO Teases New $51M Customer Deal"
WHY
  underlying +86.0%/+127.5%/+101.8% (favorable peak -59.5%); position move -101.8%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~-180% · IV residual ~288% [inferred].
  convexity Γ·S = 0.52. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SCHW-2026-04-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.1%
  greeks Δ-0.492 Γ0.0548 Θ-0.136 · IV 0.446 · mid 2.74
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 56
  headline "Schwab Shares Bounce on Geopolitical Ceasefire Despite Looming Q1 Earnings and Credit Downgrades"
WHY
  underlying +1.6%/+3.6%/-4.3% (favorable peak +5.0%); position move +4.3%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~75% · IV residual ~20% [inferred].
  convexity Γ·S = 5.31. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TDG-2026-04-17-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 70.00 · spread +0.0%
  greeks Δ-0.551 Γ0.0058 Θ-0.554 · IV 0.202 · mid 35.70
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 56
  headline "TransDigm raises full-year 2026 guidance as preliminary Q2 results surpass expectations"
WHY
  underlying +0.7%/-4.8%/-6.2% (favorable peak +6.8%); position move +6.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~120% · IV residual ~-36% [inferred].
  convexity Γ·S = 7.31. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WING-2026-05-05-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI 4.20 · spread +0.0%
  greeks Δ-0.611 Γ0.0200 Θ-0.384 · IV 0.808 · mid 10.95
  overnight_score 4 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 24
  headline "Wingstop Same-Store Sales Decline for Seventh Quarter While Unit Growth Reaches 17%"
WHY
  underlying -0.9%/-8.1%/-11.6% (favorable peak +11.9%); position move +11.6%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~95% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.93. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE CHWY-2026-05-18-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.323 Γ0.1100 Θ-0.034 · IV 0.698 · mid 0.68
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 25
  headline "Chewy CEO Says Consumers Are 'Stretched' as Stock Hits New 52-Week Lows"
WHY
  underlying -9.1%/-6.7%/-7.9% (favorable peak +10.8%); position move +7.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~81% · IV residual ~14% [inferred].
  convexity Γ·S = 2.38. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CPB-2026-05-18-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 10 · V/OI 5.53 · spread +0.1%
  greeks Δ-0.550 Γ0.2894 Θ-0.027 · IV 0.393 · mid 0.65
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 40
  headline "Campbell's price target lowered to $20 from $23 at BofA as earnings loom"
WHY
  underlying -0.6%/-1.7%/-1.4% (favorable peak +3.8%); position move +1.4%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~25% · IV residual ~68% [inferred].
  convexity Γ·S = 5.89. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CSIQ-2026-04-14-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.490 Γ0.2211 Θ-0.037 · IV 0.834 · mid 0.72
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.40) · RSI 42
  headline "China weighs solar export curbs as US-Iran peace hopes spark relief rally"
WHY
  underlying +1.9%/-3.0%/-1.3% (favorable peak +5.2%); position move +1.3%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~12% · IV residual ~83% [inferred].
  convexity Γ·S = 2.96. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DKNG-2026-05-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 9.50 · spread +0.1%
  greeks Δ-0.311 Γ0.0984 Θ-0.023 · IV 0.522 · mid 0.83
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.40) · RSI 59
  headline "Citizens cuts DraftKings stock price target on handle growth concerns"
WHY
  underlying -1.1%/-6.3%/-1.3% (favorable peak +6.4%); position move +1.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~12% · IV residual ~76% [inferred].
  convexity Γ·S = 2.50. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MCD-2026-05-08-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 0.98 · spread +0.0%
  greeks Δ-0.027 Γ0.0030 Θ-0.019 · IV 0.249 · mid 0.84
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 25
  headline "McDonald's (MCD) Hits 52-Week Low as Analysts Slash Price Targets Citing Softening Industry Backdrop"
WHY
  underlying -0.4%/-0.3%/-0.0% (favorable peak +1.4%); position move +0.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~0% · IV residual ~87% [inferred].
  convexity Γ·S = 0.83. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NCLH-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 42 · V/OI n/a · spread +0.1%
  greeks Δ-0.347 Γ0.0842 Θ-0.019 · IV 0.645 · mid 1.04
  overnight_score 5 · flow HEDGING · catalyst Macro (0.85) · RSI 49
  headline "Airline, Cruise Stocks Slip as Oil Jumps After Iran Cease-fire Hopes Dash"
WHY
  underlying +4.8%/+1.1%/-3.5% (favorable peak +4.2%); position move +3.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~23% · IV residual ~62% [inferred].
  convexity Γ·S = 1.69. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TER-2026-04-27-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 3.12 · spread +0.1%
  greeks Δ-0.350 Γ0.0043 Θ-0.900 · IV 0.979 · mid 24.77
  overnight_score 5 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 69
  headline "Teradyne (TER) Scheduled to Report Q1 2026 Earnings After Market Close on April 28"
WHY
  underlying -5.4%/-23.8%/-14.6% (favorable peak +24.9%); position move +14.6%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~83% · IV residual ~8% [inferred].
  convexity Γ·S = 1.73. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE TSCO-2026-04-29-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 5.33 · spread +0.1%
  greeks Δ-0.257 Γ0.0664 Θ-0.021 · IV 0.444 · mid 0.73
  overnight_score 6 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 17
  headline "Tractor Supply (TSCO) Reaches New 12-Month Low Following Weak Earnings and Analyst Target Cuts"
WHY
  underlying +0.9%/-2.7%/-7.1% (favorable peak +7.2%); position move +7.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~87% · IV residual ~2% [inferred].
  convexity Γ·S = 2.31. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HD-2026-04-29-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 5.35 · spread +0.1%
  greeks Δ-0.465 Γ0.0136 Θ-0.199 · IV 0.325 · mid 11.76
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.45) · RSI 38
  headline "Home Depot (HD) Stock Falls Amid Market Uptick as Housing Pressure and Insider Selling Weigh on Sentiment"
WHY
  underlying +1.9%/+0.3%/-3.2% (favorable peak +3.3%); position move +3.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~41% · IV residual ~42% [inferred].
  convexity Γ·S = 4.39. exit TIMEOUT → realized +78%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AVAV-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ-0.332 Γ0.0121 Θ-0.312 · IV 0.701 · mid 7.90
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.35) · RSI 48
  headline "AeroVironment wins $14.6M U.S. Army drone contract for VAPOR Compact Long Endurance UAS"
WHY
  underlying +6.5%/+6.5%/+2.4% (favorable peak +0.2%); position move -2.4%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-20% · IV residual ~110% [inferred].
  convexity Γ·S = 2.39. exit TIMEOUT → realized +78%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE STLA-2026-04-28-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 1.56 · spread +0.1%
  greeks Δ-0.356 Γ0.3077 Θ-0.008 · IV 0.535 · mid 0.42
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.65) · RSI 49
  headline "Stellantis Investors Sue Over Alleged Concealment of EV Strategy Failures and $22 Billion in Charges"
WHY
  underlying -2.0%/-7.4%/-9.3% (favorable peak +10.7%); position move +9.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~62% · IV residual ~21% [inferred].
  convexity Γ·S = 2.42. exit TIMEOUT → realized +78%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PATH-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ-0.440 Γ0.2385 Θ-0.013 · IV 0.610 · mid 0.68
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 46
  headline "UiPath stock gains on Salesforce marketplace integration"
WHY
  underlying +2.1%/+3.1%/-4.5% (favorable peak +6.3%); position move +4.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~30% · IV residual ~52% [inferred].
  convexity Γ·S = 2.52. exit TIMEOUT → realized +76%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SHAK-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 8 · V/OI 4.55 · spread +0.0%
  greeks Δ-0.661 Γ0.0646 Θ-0.116 · IV 0.575 · mid 3.74
  overnight_score 7 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 24
  headline "Shake Shack Stock Plunges 30% After Brutal Q1 Earnings Report and CFO Transition"
WHY
  underlying -3.2%/-5.5%/-6.6% (favorable peak +6.9%); position move +6.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~75% · IV residual ~10% [inferred].
  convexity Γ·S = 4.13. exit TIMEOUT → realized +75%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AZ-2026-05-08-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 40 · V/OI 0.42 · spread +0.0%
  greeks Δ-0.385 Γ0.1977 Θ-0.009 · IV 0.803 · mid 0.80
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.75) · RSI 48
  headline "A2Z Cust2Mate Solutions to Host First Quarter 2026 Financial Results Conference Call on Friday, May 15, 2026"
WHY
  underlying +3.5%/-4.1%/-9.4% (favorable peak +9.5%); position move +9.4%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~32% · IV residual ~46% [inferred].
  convexity Γ·S = 1.41. exit TIMEOUT → realized +75%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LEN-2026-04-29-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 625.00 · spread +0.0%
  greeks Δ-0.408 Γ0.0524 Θ-0.091 · IV 0.405 · mid 1.88
  overnight_score 6 · flow HEDGING · catalyst Analyst Downgrade (0.45) · RSI 39
  headline "Lennar (LEN) Shares Fall 3.9% as Analyst EPS Estimates Move Lower"
WHY
  underlying +1.8%/-0.3%/-4.9% (favorable peak +5.0%); position move +4.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~94% · IV residual ~-6% [inferred].
  convexity Γ·S = 4.65. exit TIMEOUT → realized +74%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LMT-2026-04-17-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 21.00 · spread +0.0%
  greeks Δ-0.268 Γ0.0068 Θ-0.382 · IV 0.345 · mid 8.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 34
  headline "Lockheed Martin Shares Slip Below Key Moving Averages on Middle East Ceasefire Reports"
WHY
  underlying -1.8%/-3.4%/-6.2% (favorable peak +7.1%); position move +6.2%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~121% · IV residual ~-33% [inferred].
  convexity Γ·S = 4.02. exit TIMEOUT → realized +74%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AZN-2026-04-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 56.89 · spread +0.1%
  greeks Δ-0.403 Γ0.0303 Θ-0.105 · IV 0.269 · mid 3.60
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 47
  headline "AstraZeneca faces Farxiga patent cliff and Germany pricing headwinds ahead of Q1 earnings"
WHY
  underlying -1.3%/-2.6%/-3.7% (favorable peak +3.9%); position move +3.7%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~82% · IV residual ~-5% [inferred].
  convexity Γ·S = 5.90. exit TIMEOUT → realized +68%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ACN-2026-04-17-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 3.05 · spread +0.1%
  greeks Δ-0.324 Γ0.0190 Θ-0.169 · IV 0.407 · mid 4.39
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.40) · RSI 49
  headline "Accenture Upgraded to Buy Following 34% Share Price Decline and Valuation Contraction"
WHY
  underlying -1.3%/-1.6%/-3.8% (favorable peak +4.8%); position move +3.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~56% · IV residual ~23% [inferred].
  convexity Γ·S = 3.75. exit TIMEOUT → realized +67%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BKNG-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.348 Γ0.0288 Θ-0.166 · IV 0.368 · mid 2.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 35
  headline "Booking Holdings Faces Fresh Antitrust Probe in Italy as Regulatory Pressure Mounts"
WHY
  underlying +1.7%/-1.8%/-2.1% (favorable peak +2.4%); position move +2.1%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~56% · IV residual ~32% [inferred].
  convexity Γ·S = 4.54. exit TIMEOUT → realized +65%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MNDY-2026-05-08-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 40 · V/OI 0.21 · spread +0.1%
  greeks Δ-0.381 Γ0.0163 Θ-0.108 · IV 0.969 · mid 7.91
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.95) · RSI 52
  headline "monday.com Set to Release Q1 Earnings May 11 Amid Analyst Downgrades Citing Challenged SaaS Macro"
WHY
  underlying +6.7%/-0.1%/-6.1% (favorable peak +6.9%); position move +6.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~21% · IV residual ~42% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized +59%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TSCO-2026-04-30-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 675.00 · spread +0.0%
  greeks Δ-0.133 Γ0.0517 Θ-0.016 · IV 0.426 · mid 0.31
  overnight_score 3 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 20
  headline "Tractor Supply Stock In Shambles: Down 23% With 8-Day Losing Streak Following Earnings Miss"
WHY
  underlying -3.6%/-7.9%/-6.9% (favorable peak +8.9%); position move +6.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~104% · IV residual ~-29% [inferred].
  convexity Γ·S = 1.82. exit TIMEOUT → realized +59%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MELI-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 12.00 · spread +0.0%
  greeks Δ-0.283 Γ0.0019 Θ-0.821 · IV 0.329 · mid 32.50
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.95) · RSI 35
  headline "MercadoLibre falls 7% in after-hours as earnings miss overshadows revenue beat"
WHY
  underlying -12.7%/-16.7%/-15.6% (favorable peak +17.8%); position move +15.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~254% · IV residual ~-191% [inferred].
  convexity Γ·S = 3.52. exit TIMEOUT → realized +55%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE INTU-2026-05-15-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.390 Γ0.0068 Θ-0.777 · IV 0.737 · mid 16.20
  overnight_score 6 · flow HEDGING · catalyst Technical Breakout (0.85) · RSI 49
  headline "Intuit (INTU) Rebounds 3.9% Ahead of Q3 Earnings as Investors Weigh AI Roadmap Against 40% YTD Drawdown"
WHY
  underlying +2.6%/+1.7%/-2.3% (favorable peak +4.6%); position move +2.3%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~22% · IV residual ~45% [inferred].
  convexity Γ·S = 2.69. exit TIMEOUT → realized +52%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HON-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 29.67 · spread +0.0%
  greeks Δ-0.278 Γ0.0245 Θ-0.211 · IV 0.347 · mid 2.69
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 48
  headline "Honeywell Expected to Report Year-Over-Year Earnings Decline as Q1 2026 Earnings Date Approaches"
WHY
  underlying -3.3%/-4.3%/-6.7% (favorable peak +9.5%); position move +6.7%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~159% · IV residual ~-84% [inferred].
  convexity Γ·S = 5.63. exit TIMEOUT → realized +51%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PRIM-2026-05-14-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 0.38 · spread +0.1%
  greeks Δ-0.252 Γ0.0161 Θ-0.090 · IV 0.560 · mid 4.04
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 38
  headline "Primoris Services (PRIM) Shares Crater 50% Amid Expanded Renewables Issues – HBSS Investigation Launched"
WHY
  underlying -1.9%/-6.0%/-9.4% (favorable peak +10.3%); position move +9.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~68% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.86. exit TIMEOUT → realized +51%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TTD-2026-05-26-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.489 Γ0.0931 Θ-0.023 · IV 0.621 · mid 1.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 49
  headline "HSBC Downgrades Trade Desk to Reduce with $20 Price Target Following Soft Q2 Guidance"
WHY
  underlying +0.5%/-4.6%/-2.8% (favorable peak +6.2%); position move +2.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~17% · IV residual ~37% [inferred].
  convexity Γ·S = 2.06. exit TIMEOUT → realized +50%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AVAV-2026-04-30-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 4.16 · spread +0.0%
  greeks Δ-0.255 Γ0.0083 Θ-0.213 · IV 0.710 · mid 10.18
  overnight_score 4 · flow HEDGING · catalyst Product Launch (0.80) · RSI 48
  headline "AeroVironment Launches Halo_Shield C-UAS System Following Successful Navy Laser Trials"
WHY
  underlying -5.2%/-7.6%/-14.5% (favorable peak +14.6%); position move +14.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~71% · IV residual ~-16% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized +49%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE BA-2026-04-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.1%
  greeks Δ-0.499 Γ0.0246 Θ-0.300 · IV 0.434 · mid 7.16
  overnight_score 5 · flow HEDGING · catalyst Macro (0.65) · RSI 59
  headline "Boeing (BA) Shares Rally on Ceasefire Hopes and China Order Speculation Ahead of Q1 Earnings"
WHY
  underlying +0.7%/+0.8%/-1.5% (favorable peak +3.0%); position move +1.5%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~23% · IV residual ~37% [inferred].
  convexity Γ·S = 5.46. exit TIMEOUT → realized +47%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ANET-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI n/a · spread +0.1%
  greeks Δ-0.356 Γ0.0171 Θ-0.135 · IV 0.526 · mid 7.36
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.95) · RSI 38
  headline "Arista Networks Stock Dives as Supply Chain Warnings and Tepid Guidance Overshadow Q1 Beat"
WHY
  underlying -3.6%/-3.6%/-7.2% (favorable peak +8.1%); position move +7.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~51% · IV residual ~1% [inferred].
  convexity Γ·S = 2.52. exit TIMEOUT → realized +47%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SHOP-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ-0.325 Γ0.0177 Θ-0.103 · IV 0.599 · mid 5.70
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 41
  headline "Shopify Analysts Slash 2026 EPS Estimates by 37% Following Guidance Slowdown"
WHY
  underlying -1.2%/-8.2%/-10.6% (favorable peak +11.8%); position move +10.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~68% · IV residual ~-17% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized +45%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AVAV-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI 1.92 · spread +0.0%
  greeks Δ-0.267 Γ0.0115 Θ-0.478 · IV 0.824 · mid 10.45
  overnight_score 4 · flow HEDGING · catalyst Product Launch (0.85) · RSI 55
  headline "AeroVironment Shares Surge After Successful LOCUST Laser Weapon Test on U.S. Aircraft Carrier"
WHY
  underlying +0.0%/-3.9%/-6.6% (favorable peak +7.0%); position move +6.6%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~35% · IV residual ~22% [inferred].
  convexity Γ·S = 2.42. exit TIMEOUT → realized +44%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SHAK-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ-0.433 Γ0.0420 Θ-0.057 · IV 0.500 · mid 3.50
  overnight_score 7 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 22
  headline "Shake Shack Shares Crater to New 52-Week Lows as 'Guidance Void' and CFO Transition Spook Investors Post-Ea…"
WHY
  underlying +2.4%/-0.9%/-4.1% (favorable peak +4.4%); position move +4.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~32% · IV residual ~16% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized +43%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LYB-2026-05-15-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 33 · V/OI 0.09 · spread +0.0%
  greeks Δ-0.277 Γ0.0280 Θ-0.061 · IV 0.520 · mid 2.79
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 54
  headline "Evercore Issues Positive Forecast for LyondellBasell Amid Notable Insider Selling and Valuation Flags"
WHY
  underlying -1.2%/-2.7%/-5.0% (favorable peak +6.1%); position move +5.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~37% · IV residual ~12% [inferred].
  convexity Γ·S = 2.10. exit TIMEOUT → realized +43%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SPOT-2026-05-01-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 0.85 · spread +0.0%
  greeks Δ-0.274 Γ0.0054 Θ-0.291 · IV 0.461 · mid 11.07
  overnight_score 4 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 34
  headline "Spotify shares drop 13% as Q2 guidance for profit and subscribers misses analyst expectations"
WHY
  underlying -0.7%/-5.0%/-3.7% (favorable peak +6.9%); position move +3.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~40% · IV residual ~10% [inferred].
  convexity Γ·S = 2.37. exit TIMEOUT → realized +42%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MP-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 15 · V/OI 1.79 · spread +0.0%
  greeks Δ-0.469 Γ0.0434 Θ-0.118 · IV 0.706 · mid 3.54
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 50
  headline "MP Materials Insiders Liquidate $23M in Stock as Zacks Downgrades to Sell Post-Earnings"
WHY
  underlying -5.4%/-3.9%/-11.1% (favorable peak +13.6%); position move +11.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~94% · IV residual ~-42% [inferred].
  convexity Γ·S = 2.77. exit TIMEOUT → realized +42%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE TSCO-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.685 Γ0.1025 Θ-0.062 · IV 0.537 · mid 1.15
  overnight_score 6 · flow HEDGING · catalyst Earnings Miss (0.90) · RSI 25
  headline "Tractor Supply Shares Plunge 11% on Q1 Earnings Miss and Weak Same-Store Sales"
WHY
  underlying -1.5%/-3.5%/-7.2% (favorable peak +7.5%); position move +7.2%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~169% · IV residual ~-112% [inferred].
  convexity Γ·S = 4.06. exit TIMEOUT → realized +40%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ESI-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 20 · V/OI 0.41 · spread +0.0%
  greeks Δ-0.137 Γ0.0372 Θ-0.031 · IV 0.615 · mid 0.80
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.85) · RSI 70
  headline "Element Solutions (ESI) Stock Hits All-Time High at $39.60 Ahead of Q1 Earnings"
WHY
  underlying +0.1%/-3.9%/+5.5% (favorable peak +4.9%); position move -5.5%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-38% · IV residual ~89% [inferred].
  convexity Γ·S = 1.50. exit TRAIL → realized +39%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FICO-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.267 Γ0.0016 Θ-1.147 · IV 0.680 · mid 40.53
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 46
  headline "Mizuho initiates Fair Isaac stock coverage with Outperform rating, dismissing VantageScore risk"
WHY
  underlying +0.3%/-0.6%/-3.1% (favorable peak +4.9%); position move +3.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~22% · IV residual ~24% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized +38%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AZO-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 37 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.494 Γ0.0011 Θ-1.856 · IV 0.341 · mid 153.92
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 42
  headline "AutoZone (AZO) Stock Sinks As Market Gains: What You Should Know"
WHY
  underlying -0.5%/-1.8%/-1.4% (favorable peak +3.7%); position move +1.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~16% · IV residual ~25% [inferred].
  convexity Γ·S = 3.74. exit TIMEOUT → realized +37%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RGTI-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI 1.71 · spread +0.1%
  greeks Δ-0.293 Γ0.0541 Θ-0.030 · IV 1.083 · mid 1.23
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 59
  headline "Rigetti Computing (NASDAQ:RGTI) Now Covered by Analysts at Northland Securities with $20 Price Target"
WHY
  underlying +0.7%/-7.6%/-9.0% (favorable peak +11.8%); position move +9.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~39% · IV residual ~4% [inferred].
  convexity Γ·S = 0.99. exit TIMEOUT → realized +36%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MMM-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 3.33 · spread +0.1%
  greeks Δ-0.328 Γ0.0288 Θ-0.130 · IV 0.382 · mid 2.80
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.95) · RSI 52
  headline "3M Q1 2026 Earnings: Industrial Giant Faces Pressure Amid Softening Consumer Demand"
WHY
  underlying -1.9%/-3.7%/-4.3% (favorable peak +5.2%); position move +4.3%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~77% · IV residual ~-27% [inferred].
  convexity Γ·S = 4.35. exit TIMEOUT → realized +36%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AVAV-2026-05-05-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ-0.389 Γ0.0150 Θ-0.288 · IV 0.715 · mid 7.22
  overnight_score 7 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 37
  headline "AeroVironment (AVAV) Stock Slides Despite Breakthrough in Homeland Defense Laser Technology"
WHY
  underlying +4.6%/+0.9%/+1.0% (favorable peak +1.2%); position move -1.0%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-9% · IV residual ~55% [inferred].
  convexity Γ·S = 2.51. exit TIMEOUT → realized +34%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE COF-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 19.58 · spread +0.0%
  greeks Δ-0.158 Γ0.0099 Θ-0.105 · IV 0.465 · mid 1.40
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 46
  headline "Capital One Stock Pressured by Earnings Miss, NIM Compression, and $425M Regulatory Settlement"
WHY
  underlying +1.4%/+0.4%/-0.3% (favorable peak +0.9%); position move +0.3%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~6% · IV residual ~51% [inferred].
  convexity Γ·S = 1.89. exit TRAIL → realized +34%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ALB-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 6.20 · spread +0.1%
  greeks Δ-0.290 Γ0.0100 Θ-0.238 · IV 0.684 · mid 6.53
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 58
  headline "Albemarle Downgraded to Neutral by Baird as Valuation Concerns Mount After 47% YTD Rally"
WHY
  underlying +1.8%/-0.3%/-0.9% (favorable peak +3.5%); position move +0.9%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~8% · IV residual ~35% [inferred].
  convexity Γ·S = 1.94. exit TIMEOUT → realized +31%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MSTR-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 3.03 · spread +0.0%
  greeks Δ-0.394 Γ0.0098 Θ-0.170 · IV 0.647 · mid 13.76
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 56
  headline "Senate Crypto Vote Set for May 14 as MicroStrategy Dividend Funding Strategy Sparks Treasury Risk Concerns"
WHY
  underlying +5.0%/-0.3%/-6.4% (favorable peak +9.0%); position move +6.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~33% · IV residual ~2% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized +31%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TARS-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.377 Γ0.0224 Θ-0.111 · IV 0.896 · mid 4.42
  overnight_score 5 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 44
  headline "No clear catalyst identified for Tarsus Pharmaceuticals' ~7% decline on April 16, 2026"
WHY
  underlying -0.7%/-2.6%/-4.7% (favorable peak +6.5%); position move +4.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~27% · IV residual ~10% [inferred].
  convexity Γ·S = 1.52. exit TIMEOUT → realized +30%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HD-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ-0.400 Γ0.0105 Θ-0.154 · IV 0.335 · mid 10.25
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 36
  headline "Home Depot (HD) Sees $23M Bearish Options Surge as Market Eyes Upcoming Q1 Earnings"
WHY
  underlying -0.3%/-2.8%/-2.3% (favorable peak +3.9%); position move +2.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~27% · IV residual ~6% [inferred].
  convexity Γ·S = 3.27. exit TIMEOUT → realized +29%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TYL-2026-05-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 27 · V/OI 0.69 · spread +0.0%
  greeks Δ-0.115 Γ0.0039 Θ-0.179 · IV 0.597 · mid 4.00
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 41
  headline "Tyler Technologies (TYL) Shares Underperform as Institutional Put Buying Surges on No Clear News"
WHY
  underlying +1.5%/-0.4%/-2.0% (favorable peak +2.9%); position move +2.0%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~18% · IV residual ~23% [inferred].
  convexity Γ·S = 1.20. exit TIMEOUT → realized +28%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LLY-2026-04-10-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ-0.472 Γ0.0038 Θ-1.029 · IV 0.486 · mid 42.45
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 48
  headline "Eli Lilly's Foundayo Launch Meets Institutional Skepticism as Price War Concerns Mount"
WHY
  underlying -1.1%/-1.8%/-3.7% (favorable peak +5.5%); position move +3.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~38% · IV residual ~-4% [inferred].
  convexity Γ·S = 3.52. exit TIMEOUT → realized +27%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TPG-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 0.14 · spread +0.0%
  greeks Δ-0.679 Γ0.1417 Θ-0.060 · IV 0.396 · mid 1.80
  overnight_score 4 · flow MECHANICAL · catalyst No Clear Catalyst (0.15) · RSI 56
  headline "TPG Inc. Declares $0.59 Dividend with May 8 Ex-Dividend Date Following Q1 Earnings Beat"
WHY
  underlying -1.0%/-2.0%/-1.0% (favorable peak +3.7%); position move +1.0%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~17% · IV residual ~20% [inferred].
  convexity Γ·S = 6.30. exit TIMEOUT → realized +27%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MDB-2026-05-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.412 Γ0.0046 Θ-0.589 · IV 0.957 · mid 30.93
  overnight_score 8 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 63
  headline "MongoDB stock may swing 15% on upcoming earnings report as valuation concerns mount"
WHY
  underlying +2.7%/-3.2%/-7.3% (favorable peak +7.8%); position move +7.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~31% · IV residual ~2% [inferred].
  convexity Γ·S = 1.47. exit TIMEOUT → realized +27%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LIF-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.563 Γ0.0320 Θ-0.084 · IV 0.967 · mid 6.87
  overnight_score 2 · flow HEDGING · catalyst Analyst Upgrade (0.80) · RSI 58
  headline "Life360 (LIF) Shares Gap Up on Unusually High Volume Following Analyst Rating Updates"
WHY
  underlying +5.9%/+5.6%/-1.0% (favorable peak +1.1%); position move +1.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~4% · IV residual ~26% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized +27%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ZS-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ-0.398 Γ0.0112 Θ-0.174 · IV 0.767 · mid 10.46
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 50
  headline "Zscaler Shares Jump as KeyBanc Survey Points to AI-Driven Budget Growth"
WHY
  underlying +2.2%/-4.8%/-2.9% (favorable peak +6.6%); position move +2.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~16% · IV residual ~16% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized +26%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LEU-2026-05-12-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 0.06 · spread +0.0%
  greeks Δ-0.388 Γ0.0076 Θ-0.260 · IV 0.796 · mid 16.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 49
  headline "Centrus Energy (LEU) Stock Trades Down as Analysts Trim Price Targets Following Q1 Profit Slump"
WHY
  underlying -5.0%/-5.0%/-9.8% (favorable peak +11.8%); position move +9.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~47% · IV residual ~-17% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized +26%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HTZ-2026-05-15-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 0.19 · spread +0.1%
  greeks Δ-0.429 Γ0.4298 Θ-0.009 · IV 0.696 · mid 0.28
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.75) · RSI 45
  headline "Hertz Burns Through $3.58 Billion in Cash as EV Misstep Hammers Profitability"
WHY
  underlying -6.0%/-10.8%/-11.8% (favorable peak +12.1%); position move +11.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~100% · IV residual ~-65% [inferred].
  convexity Γ·S = 2.38. exit TIMEOUT → realized +25%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE RDDT-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 1.71 · spread +0.0%
  greeks Δ-0.461 Γ0.0094 Θ-0.356 · IV 1.045 · mid 13.98
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.80) · RSI 58
  headline "Citizens cuts Reddit stock price target to $250 on tougher comps and monetization concerns"
WHY
  underlying +4.8%/-2.5%/-1.2% (favorable peak +4.0%); position move +1.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~6% · IV residual ~26% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized +25%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NCLH-2026-04-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ-0.427 Γ0.0933 Θ-0.018 · IV 0.598 · mid 1.63
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 52
  headline "UBS Maintains Neutral on NCLH, Slashes Price Target to $22 Amid Execution Missteps"
WHY
  underlying +4.1%/+4.2%/-1.1% (favorable peak +1.2%); position move +1.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~6% · IV residual ~22% [inferred].
  convexity Γ·S = 1.89. exit TIMEOUT → realized +25%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MP-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 11.67 · spread +0.1%
  greeks Δ-0.455 Γ0.0319 Θ-0.090 · IV 0.759 · mid 4.67
  overnight_score 4 · flow HEDGING · catalyst Insider Activity (0.65) · RSI 53
  headline "CEO James H. Litinsky Sells 259,179 Shares as MP Materials Tests Critical 200-Day Support"
WHY
  underlying +6.9%/+1.6%/+0.9% (favorable peak +1.2%); position move -0.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-6% · IV residual ~36% [inferred].
  convexity Γ·S = 1.94. exit TIMEOUT → realized +25%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TSCO-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 3.57 · spread +0.0%
  greeks Δ-0.255 Γ0.1101 Θ-0.034 · IV 0.410 · mid 0.40
  overnight_score 7 · flow HEDGING · catalyst Earnings Miss (0.90) · RSI 20
  headline "Tractor Supply Stock Plummets -18% With 5-Day Losing Streak Following Earnings and Revenue Miss"
WHY
  underlying -2.9%/-3.1%/-5.4% (favorable peak +6.5%); position move +5.4%.
  decomp [first-order]: theta drag ~26% of premium / 3d · delta capture ~126% · IV residual ~-75% [inferred].
  convexity Γ·S = 4.05. exit TIMEOUT → realized +25%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FN-2026-05-04-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 9.60 · spread +0.1%
  greeks Δ-0.498 Γ0.0034 Θ-0.509 · IV 0.538 · mid 56.17
  overnight_score 4 · flow HEDGING · catalyst Earnings Miss (0.90) · RSI 63
  headline "Fabrinet Stock Tumbles Despite Q3 Earnings Beat as Revenue Misses and Guidance Disappoints"
WHY
  underlying -8.0%/-5.4%/-12.8% (favorable peak +14.6%); position move +12.8%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~81% · IV residual ~-54% [inferred].
  convexity Γ·S = 2.43. exit TIMEOUT → realized +24%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AG-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 4.83 · spread +0.0%
  greeks Δ-0.478 Γ0.0993 Θ-0.037 · IV 0.824 · mid 1.92
  overnight_score 5 · flow HEDGING · catalyst Sector Rotation (0.85) · RSI 43
  headline "First Majestic Silver Stock Suddenly Slides Again as Tumbling Silver Prices Spark Broad Sell-off"
WHY
  underlying +1.5%/+1.1%/-3.7% (favorable peak +4.8%); position move +3.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~19% · IV residual ~12% [inferred].
  convexity Γ·S = 2.01. exit TIMEOUT → realized +24%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FISV-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 2.40 · spread +0.1%
  greeks Δ-0.458 Γ0.0630 Θ-0.042 · IV 0.403 · mid 2.65
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 36
  headline "Fiserv Sinks on Mixed Q1 Results: Revenue Miss and Margin Compression Spark Growth Concerns"
WHY
  underlying +1.2%/-1.1%/-3.1% (favorable peak +3.5%); position move +3.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~30% · IV residual ~-1% [inferred].
  convexity Γ·S = 3.53. exit TIMEOUT → realized +24%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FICO-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI 0.25 · spread +0.0%
  greeks Δ-0.286 Γ0.0017 Θ-0.916 · IV 0.593 · mid 39.60
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 53
  headline "FICO Shares Slide as Major Analysts Slash Price Targets and Institutional Selling Accelerates"
WHY
  underlying -0.5%/-2.5%/-1.4% (favorable peak +4.2%); position move +1.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~11% · IV residual ~19% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized +23%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ULTA-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 22.00 · spread +0.0%
  greeks Δ-0.423 Γ0.0054 Θ-0.464 · IV 0.518 · mid 25.85
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 31
  headline "Morgan Stanley and Piper Sandler Cut Ulta Beauty Price Targets as Macro Pressures Mount"
WHY
  underlying +1.2%/+0.4%/-2.5% (favorable peak +3.0%); position move +2.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~20% · IV residual ~8% [inferred].
  convexity Γ·S = 2.68. exit TIMEOUT → realized +22%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LLY-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ-0.406 Γ0.0031 Θ-0.568 · IV 0.427 · mid 43.59
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 38
  headline "Eli Lilly Stock Slides 4% As Initial Sales Data For New Drug Foundayo Disappoints"
WHY
  underlying -1.8%/-1.1%/-3.7% (favorable peak +3.8%); position move +3.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~30% · IV residual ~-4% [inferred].
  convexity Γ·S = 2.72. exit TIMEOUT → realized +22%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LITE-2026-05-26-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.311 Γ0.0013 Θ-1.338 · IV 0.961 · mid 66.39
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 50
  headline "Fisher Asset Management LLC Sells 282,086 Shares of Lumentum Holdings Inc. $LITE"
WHY
  underlying -0.9%/-5.5%/-6.1% (favorable peak +9.7%); position move +6.1%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~26% · IV residual ~1% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized +21%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIS-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 0.19 · spread +0.0%
  greeks Δ-0.457 Γ0.1299 Θ-0.035 · IV 0.331 · mid 1.32
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 33
  headline "Goldman Sachs and Cantor Fitzgerald Slash FIS Price Targets Following Q1 Earnings"
WHY
  underlying +1.5%/+0.6%/-1.3% (favorable peak +1.5%); position move +1.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~19% · IV residual ~10% [inferred].
  convexity Γ·S = 5.50. exit TRAIL → realized +21%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE RGTI-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 14 · V/OI 19.04 · spread +0.1%
  greeks Δ-0.134 Γ0.0538 Θ-0.029 · IV 1.176 · mid 0.25
  overnight_score 4 · flow HEDGING · catalyst Technical Breakout (0.30) · RSI 51
  headline "Rigetti Computing (NASDAQ:RGTI) Stock Price Down 8.3% - Here's Why"
WHY
  underlying -1.5%/+0.3%/-2.8% (favorable peak +4.8%); position move +2.8%.
  decomp [first-order]: theta drag ~35% of premium / 3d · delta capture ~25% · IV residual ~31% [inferred].
  convexity Γ·S = 0.91. exit TRAIL → realized +21%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DHI-2026-04-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ-0.413 Γ0.0302 Θ-0.231 · IV 0.524 · mid 4.43
  overnight_score 1 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 53
  headline "Mortgage Rates Surge to 6.46% Amid Geopolitical Tensions as D.R. Horton Prepares for Q2 Earnings"
WHY
  underlying +0.6%/-0.1%/-0.7% (favorable peak +1.1%); position move +0.7%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~9% · IV residual ~27% [inferred].
  convexity Γ·S = 4.36. exit TIMEOUT → realized +20%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DPZ-2026-05-18-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 30 · V/OI 0.08 · spread +0.0%
  greeks Δ-0.030 Γ0.0019 Θ-0.040 · IV 0.402 · mid 0.55
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 36
  headline "Domino's Pizza (DPZ) reported mixed quarterly results, with EPS of $4.13 missing estimates and shares tradi…"
WHY
  underlying +1.5%/+2.6%/+2.8% (favorable peak +0.9%); position move -2.8%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~-47% · IV residual ~88% [inferred].
  convexity Γ·S = 0.59. exit TRAIL → realized +19%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MRVL-2026-05-04-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 2.00 · spread +0.0%
  greeks Δ-0.593 Γ0.0092 Θ-0.183 · IV 0.762 · mid 27.58
  overnight_score 4 · flow HEDGING · catalyst No Clear Catalyst (0.30) · RSI 75
  headline "Marvell Technology, Inc. Announces Conference Call to Review First Quarter of Fiscal Year 2027 Financial Re…"
WHY
  underlying +3.1%/+5.2%/-2.2% (favorable peak +3.1%); position move +2.2%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~8% · IV residual ~14% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized +19%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SNOW-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI n/a · spread +0.1%
  greeks Δ-0.263 Γ0.0217 Θ-0.277 · IV 0.697 · mid 2.76
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 54
  headline "Snowflake (SNOW) Surges 10% on AI Tailwinds Before Pulling Back Amid Growth Deceleration Concerns"
WHY
  underlying +10.0%/+9.1%/+8.4% (favorable peak -3.4%); position move -8.4%.
  decomp [first-order]: theta drag ~30% of premium / 3d · delta capture ~-112% · IV residual ~161% [inferred].
  convexity Γ·S = 3.04. exit TRAIL → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LUV-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ-0.302 Γ0.0544 Θ-0.046 · IV 0.599 · mid 1.46
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 53
  headline "Southwest Airlines to Report Q1 Earnings: Zacks Rank #4 and Negative ESP Hint at Possible Miss"
WHY
  underlying -2.2%/-5.9%/-9.7% (favorable peak +11.9%); position move +9.7%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~84% · IV residual ~-57% [inferred].
  convexity Γ·S = 2.28. exit TRAIL → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE KTOS-2026-05-01-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 11.00 · spread +0.0%
  greeks Δ-0.310 Γ0.0244 Θ-0.075 · IV 0.773 · mid 3.75
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 38
  headline "Kratos Defense & Security Solutions Schedules First Quarter 2026 Earnings Conference Call for Wednesday, Ma…"
WHY
  underlying -0.2%/-4.4%/-0.9% (favorable peak +6.5%); position move +0.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~4% · IV residual ~20% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CRCL-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 20.00 · spread +0.1%
  greeks Δ-0.447 Γ0.0144 Θ-0.193 · IV 0.998 · mid 11.06
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 50
  headline "Circle (CRCL) Insider Nikhil Chandhok Sells 10,000 Shares as Stock Tests Critical $100 Support"
WHY
  underlying -0.3%/-4.6%/-5.7% (favorable peak +7.7%); position move +5.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~23% · IV residual ~0% [inferred].
  convexity Γ·S = 1.44. exit TIMEOUT → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SRPT-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 100.00 · spread +0.0%
  greeks Δ-0.416 Γ0.2105 Θ-0.046 · IV 0.613 · mid 0.80
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 44
  headline "Sarepta Dives 10% on 'Growth Reset' and CEO Retirement Despite Headline Earnings Beat"
WHY
  underlying -4.0%/-6.7%/-8.0% (favorable peak +9.4%); position move +8.0%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~87% · IV residual ~-52% [inferred].
  convexity Γ·S = 4.38. exit TIMEOUT → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ABT-2026-05-18-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 17 · V/OI 15.86 · spread +0.1%
  greeks Δ-0.494 Γ0.0735 Θ-0.062 · IV 0.285 · mid 3.36
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 45
  headline "Abbott Laboratories Stock (ABT) Moved Up by 3.04% on May 18: What Investors Need To Know"
WHY
  underlying +1.0%/+0.5%/-0.2% (favorable peak +1.2%); position move +0.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~2% · IV residual ~21% [inferred].
  convexity Γ·S = 6.46. exit TIMEOUT → realized +18%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ADBE-2026-05-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ-0.313 Γ0.0084 Θ-0.180 · IV 0.521 · mid 9.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 47
  headline "Adobe's Stock (ADBE) Is Still Paying for the AI Panic as Support Levels Crumble"
WHY
  underlying +0.3%/-1.5%/-2.4% (favorable peak +2.8%); position move +2.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~19% · IV residual ~4% [inferred].
  convexity Γ·S = 2.05. exit TIMEOUT → realized +17%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MRNA-2026-05-27-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 130.00 · spread +0.1%
  greeks Δ-0.352 Γ0.0337 Θ-0.057 · IV 0.745 · mid 2.75
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 46
  headline "FDA to convene public advisory committee on June 18 to review Moderna's mRNA seasonal flu vaccine"
WHY
  underlying -0.1%/-0.9%/-3.3% (favorable peak +7.2%); position move +3.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~20% · IV residual ~4% [inferred].
  convexity Γ·S = 1.61. exit TIMEOUT → realized +17%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MA-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI n/a · spread +0.0%
  greeks Δ-0.414 Γ0.0145 Θ-0.323 · IV 0.266 · mid 8.68
  overnight_score 1 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 45
  headline "UK FCA launches investigation into Mastercard and Visa over PayPal digital wallet funding conduct"
WHY
  underlying +1.8%/+0.7%/+1.2% (favorable peak +0.0%); position move -1.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-28% · IV residual ~56% [inferred].
  convexity Γ·S = 7.12. exit TRAIL → realized +17%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MMM-2026-04-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.475 Γ0.0342 Θ-0.131 · IV 0.356 · mid 5.50
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 56
  headline "3M: The PFAS Cloud Is Lifting, And What's Underneath Looks Really Good"
WHY
  underlying -0.2%/-1.0%/-1.5% (favorable peak +1.8%); position move +1.5%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~19% · IV residual ~4% [inferred].
  convexity Γ·S = 5.22. exit TIMEOUT → realized +17%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FSLR-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 0.11 · spread +0.0%
  greeks Δ-0.417 Γ0.0130 Θ-0.280 · IV 0.657 · mid 11.11
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 48
  headline "First Solar (FSLR) Projected to Post Quarterly Earnings on Thursday, April 30th"
WHY
  underlying +1.9%/+1.1%/-1.6% (favorable peak +3.4%); position move +1.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~12% · IV residual ~12% [inferred].
  convexity Γ·S = 2.52. exit TIMEOUT → realized +16%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE BX-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ-0.445 Γ0.0247 Θ-0.148 · IV 0.512 · mid 5.95
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 65
  headline "Blackstone Private Credit Redemption Concerns Persist Despite Earnings Milestone"
WHY
  underlying +0.7%/+0.7%/+0.3% (favorable peak +0.1%); position move -0.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-3% · IV residual ~26% [inferred].
  convexity Γ·S = 3.17. exit TIMEOUT → realized +16%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MTN-2026-04-10-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.371 Γ0.0213 Θ-0.097 · IV 0.447 · mid 4.58
  overnight_score 3 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 43
  headline "Vail Resorts (MTN) Slashes FY26 Guidance as Warm Weather Drives 19.5% March Visitation Drop"
WHY
  underlying +1.8%/+1.0%/+0.3% (favorable peak +1.6%); position move -0.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-3% · IV residual ~25% [inferred].
  convexity Γ·S = 2.73. exit TIMEOUT → realized +16%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CSGP-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.442 Γ0.0536 Θ-0.051 · IV 0.664 · mid 2.83
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.80) · RSI 44
  headline "Stephens and BMO Slash CoStar (CSGP) Price Targets Amid Homes.com Profitability Concerns"
WHY
  underlying -0.8%/+0.0%/-2.8% (favorable peak +3.2%); position move +2.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~18% · IV residual ~4% [inferred].
  convexity Γ·S = 2.15. exit TIMEOUT → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE EXPE-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 24.28 · spread +0.1%
  greeks Δ-0.403 Γ0.0098 Θ-0.514 · IV 0.784 · mid 12.79
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 53
  headline "Expedia Shares Slide After Abrupt CFO Transition Announcement and CFRA Downgrade"
WHY
  underlying +0.4%/-2.1%/-3.3% (favorable peak +4.9%); position move +3.3%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~26% · IV residual ~2% [inferred].
  convexity Γ·S = 2.46. exit TIMEOUT → realized +15%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE UPS-2026-05-01-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 16.75 · spread +0.0%
  greeks Δ-0.385 Γ0.0395 Θ-0.056 · IV 0.293 · mid 2.46
  overnight_score 3 · flow DIRECTIONAL · catalyst Guidance Cut (0.70) · RSI 58
  headline "UPS Cash Flow Red Flags Emerge as Analysts Question Dividend Sustainability Post-Earnings"
WHY
  underlying -10.5%/-8.8%/-7.1% (favorable peak +10.8%); position move +7.1%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~120% · IV residual ~-98% [inferred].
  convexity Γ·S = 4.25. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SPOT-2026-05-15-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.491 Γ0.0096 Θ-0.602 · IV 0.499 · mid 18.25
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.70) · RSI 41
  headline "Spotify (SPOT) institutional sentiment remains bearish as market digests Q1 guidance-driven valuation reset."
WHY
  underlying +1.8%/+1.1%/-0.8% (favorable peak +1.5%); position move +0.8%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~10% · IV residual ~15% [inferred].
  convexity Γ·S = 4.21. exit TIMEOUT → realized +15%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LULU-2026-05-08-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 13 · V/OI 7.14 · spread +0.0%
  greeks Δ-0.769 Γ0.0331 Θ-0.099 · IV 0.374 · mid 8.20
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 32
  headline "Lululemon CEO Transition Under Fire as Founder Chip Wilson Escalates Proxy Battle"
WHY
  underlying -3.7%/-4.6%/-7.6% (favorable peak +7.6%); position move +7.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~94% · IV residual ~-75% [inferred].
  convexity Γ·S = 4.34. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WIX-2026-04-14-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.623 Γ0.0283 Θ-0.082 · IV 0.740 · mid 7.95
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 26
  headline "Figma and Wix shares tumble as Anthropic targets AI web design market"
WHY
  underlying +9.9%/+7.6%/+6.9% (favorable peak -0.4%); position move -6.9%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-34% · IV residual ~52% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized +15%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE RH-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.364 Γ0.0168 Θ-0.236 · IV 0.718 · mid 7.47
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 56
  headline "RH Stock Rebuilds After Brutal Selloff As Long-Term Targets Impress"
WHY
  underlying -2.9%/-4.3%/-3.2% (favorable peak +5.9%); position move +3.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~22% · IV residual ~1% [inferred].
  convexity Γ·S = 2.39. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE UPST-2026-05-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 34 · V/OI 7.69 · spread +0.0%
  greeks Δ-0.496 Γ0.0707 Θ-0.032 · IV 0.654 · mid 2.39
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.80) · RSI 46
  headline "Upstart (UPST) Faces Critical June 8 Lawsuit Deadline Following Significant Q1 Earnings Miss"
WHY
  underlying +7.2%/+7.6%/+14.5% (favorable peak -1.5%); position move -14.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-86% · IV residual ~104% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized +14%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CEG-2026-04-17-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.352 Γ0.0129 Θ-0.389 · IV 0.505 · mid 7.77
  overnight_score 3 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 49
  headline "Constellation Energy shares slip as 2026 earnings guidance disappoints investors"
WHY
  underlying -2.9%/-6.2%/-3.1% (favorable peak +6.5%); position move +3.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~41% · IV residual ~-13% [inferred].
  convexity Γ·S = 3.84. exit TRAIL → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PM-2026-04-14-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ-0.423 Γ0.0304 Θ-0.151 · IV 0.378 · mid 4.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 40
  headline "Philip Morris International Faces Technical Breakdown Below $160 as Bearish Momentum Accelerates"
WHY
  underlying -1.4%/-2.0%/-1.1% (favorable peak +2.9%); position move +1.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~16% · IV residual ~8% [inferred].
  convexity Γ·S = 4.85. exit TIMEOUT → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE KTOS-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 0.27 · spread +0.1%
  greeks Δ-0.453 Γ0.0309 Θ-0.176 · IV 0.983 · mid 4.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 36
  headline "Defense Stocks Edge Lower as Geopolitical Risk Premium Unwinds Amid U.S.-Iran Ceasefire Optimism"
WHY
  underlying -6.5%/-3.6%/-5.9% (favorable peak +8.1%); position move +5.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~42% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WOLF-2026-05-15-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 8.00 · spread +0.0%
  greeks Δ-0.385 Γ0.0243 Θ-0.217 · IV 1.321 · mid 4.63
  overnight_score 4 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 75
  headline "Wolfspeed Shares Slump 12% as Brutal Margins and Cash Burn Offset AI Infrastructure Optimism"
WHY
  underlying -4.5%/-5.3%/-5.6% (favorable peak +13.4%); position move +5.6%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~29% · IV residual ~-2% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized +13%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE MDB-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.407 Γ0.0111 Θ-0.489 · IV 0.718 · mid 13.40
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.80) · RSI 47
  headline "MongoDB Shares Slip as Software Sector Pullback Intensifies Following ServiceNow and IBM Earnings"
WHY
  underlying +4.3%/+1.8%/+1.9% (favorable peak +0.9%); position move -1.9%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-14% · IV residual ~38% [inferred].
  convexity Γ·S = 2.81. exit TIMEOUT → realized +12%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PGY-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.463 Γ0.0897 Θ-0.031 · IV 1.091 · mid 1.92
  overnight_score 2 · flow MIXED · catalyst — (—) · RSI 69
WHY
  underlying +1.9%/+2.4%/-2.7% (favorable peak +3.1%); position move +2.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~9% · IV residual ~8% [inferred].
  convexity Γ·S = 1.32. exit TIMEOUT → realized +12%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LOW-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 1.00 · spread +0.1%
  greeks Δ-0.296 Γ0.0211 Θ-0.323 · IV 0.482 · mid 2.11
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 35
  headline "Truist Financial cuts Lowe's (LOW) price target to $280 ahead of Q1 earnings"
WHY
  underlying +1.4%/-0.9%/-1.1% (favorable peak +1.4%); position move +1.1%.
  decomp [first-order]: theta drag ~46% of premium / 3d · delta capture ~34% · IV residual ~24% [inferred].
  convexity Γ·S = 4.65. exit TRAIL → realized +12%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RDDT-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 5.25 · spread +0.0%
  greeks Δ-0.472 Γ0.0134 Θ-0.200 · IV 0.641 · mid 12.14
  overnight_score 5 · flow HEDGING · catalyst Analyst Downgrade (0.55) · RSI 50
  headline "Phillip Securities Downgrades Reddit to Accumulate on Normalizing Ad Growth Trajectory"
WHY
  underlying -1.6%/-6.5%/-4.2% (favorable peak +7.8%); position move +4.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~27% · IV residual ~-11% [inferred].
  convexity Γ·S = 2.22. exit TIMEOUT → realized +12%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PFSI-2026-05-01-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 0.19 · spread +0.0%
  greeks Δ-0.254 Γ0.0255 Θ-0.146 · IV 0.705 · mid 2.30
  overnight_score 2 · flow HEDGING · catalyst Analyst Upgrade (0.85) · RSI 53
  headline "Deutsche Bank Adds PennyMac Financial (PFSI) to Fresh Money Buy List Ahead of May 5 Earnings"
WHY
  underlying -2.4%/-5.0%/-5.5% (favorable peak +7.0%); position move +5.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~56% · IV residual ~-26% [inferred].
  convexity Γ·S = 2.35. exit TRAIL → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RIVN-2026-04-28-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 2.20 · spread +0.1%
  greeks Δ-0.487 Γ0.1089 Θ-0.019 · IV 0.717 · mid 1.64
  overnight_score 4 · flow HEDGING · catalyst Insider Activity (0.85) · RSI 50
  headline "Rivian (RIVN) Shares Slide as Investors Digest CEO Pay Package and Looming Q1 Earnings"
WHY
  underlying -0.5%/+1.6%/-6.9% (favorable peak +7.0%); position move +6.9%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~33% · IV residual ~-19% [inferred].
  convexity Γ·S = 1.76. exit TIMEOUT → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE OMC-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ-0.411 Γ0.0546 Θ-0.049 · IV 0.324 · mid 2.35
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 58
  headline "Omnicom (OMC) Faces FTC Action Over Alleged Ad Industry Collusion"
WHY
  underlying -0.1%/-0.3%/-0.9% (favorable peak +1.2%); position move +0.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~12% · IV residual ~5% [inferred].
  convexity Γ·S = 4.30. exit TIMEOUT → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TYL-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 0.25 · spread +0.0%
  greeks Δ-0.429 Γ0.0084 Θ-0.237 · IV 0.470 · mid 16.82
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 38
  headline "Tyler Technologies prices upsized $1.25B convertible senior notes offering with concurrent share repurchase"
WHY
  underlying -0.8%/-4.4%/-4.2% (favorable peak +5.7%); position move +4.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~34% · IV residual ~-19% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RBLX-2026-05-04-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.313 Γ0.0533 Θ-0.067 · IV 0.651 · mid 1.51
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.90) · RSI 33
  headline "Roblox Stock Surges 6% Monday: Is The Guidance Selloff Over?"
WHY
  underlying -7.4%/-8.0%/-5.9% (favorable peak +8.9%); position move +5.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~58% · IV residual ~-34% [inferred].
  convexity Γ·S = 2.54. exit TIMEOUT → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DLR-2026-04-17-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.299 Γ0.0222 Θ-0.198 · IV 0.396 · mid 3.80
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.85) · RSI 80
  headline "Digital Realty Trust Hits New 52-Week High Ahead of Q1 Earnings as Analysts Raise Targets"
WHY
  underlying +0.1%/-1.2%/-1.4% (favorable peak +1.8%); position move +1.4%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~22% · IV residual ~4% [inferred].
  convexity Γ·S = 4.52. exit TIMEOUT → realized +10%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ZETA-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 5.00 · spread +0.0%
  greeks Δ-0.380 Γ0.0834 Θ-0.022 · IV 0.776 · mid 1.58
  overnight_score 3 · flow DIRECTIONAL · catalyst Insider Activity (0.70) · RSI 62
  headline "Zeta Global Holdings Corp. Files Multiple Form 144s Following Earnings Date Announcement"
WHY
  underlying -1.9%/+0.1%/-5.8% (favorable peak +8.4%); position move +5.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~26% · IV residual ~-11% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized +10%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MNDY-2026-05-05-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 0.34 · spread +0.1%
  greeks Δ-0.339 Γ0.0158 Θ-0.096 · IV 0.897 · mid 6.77
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 52
  headline "monday.com faces critical May 11 earnings and lawsuit deadline amid software sector 'SaaSpocalypse' fears"
WHY
  underlying -2.6%/+0.6%/-5.1% (favorable peak +9.3%); position move +5.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~19% · IV residual ~-5% [inferred].
  convexity Γ·S = 1.20. exit TIMEOUT → realized +10%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WFC-2026-04-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 9.59 · spread +0.0%
  greeks Δ-0.229 Γ0.0565 Θ-0.052 · IV 0.324 · mid 0.74
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.75) · RSI 47
  headline "Wells Fargo (WFC) Stock Trades Down as Revenue Miss and Rising Expenses Weigh on Post-Earnings Sentiment"
WHY
  underlying -0.1%/-1.4%/-0.0% (favorable peak +1.7%); position move +0.0%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~1% · IV residual ~30% [inferred].
  convexity Γ·S = 4.55. exit TRAIL → realized +10%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TEM-2026-05-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 15.00 · spread +0.0%
  greeks Δ-0.294 Γ0.0630 Θ-0.068 · IV 0.618 · mid 1.26
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 43
  headline "Tempus AI price target lowered to $64 from $95 at H.C. Wainwright"
WHY
  underlying +1.0%/+2.1%/+11.1% (favorable peak +1.6%); position move -11.1%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-119% · IV residual ~144% [inferred].
  convexity Γ·S = 2.91. exit TRAIL → realized +9%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RJF-2026-05-14-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 0.26 · spread +0.0%
  greeks Δ-0.203 Γ0.0200 Θ-0.058 · IV 0.301 · mid 1.80
  overnight_score 1 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 54
  headline "Raymond James Financial Declares Quarterly Dividend on Common Stock"
WHY
  underlying -0.9%/-0.7%/-2.9% (favorable peak +2.9%); position move +2.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~51% · IV residual ~-33% [inferred].
  convexity Γ·S = 3.11. exit TIMEOUT → realized +9%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RH-2026-04-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ-0.459 Γ0.0164 Θ-0.215 · IV 0.725 · mid 9.60
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 51
  headline "RH Investor Alert: RH Securities Fraud Investigation - Investors With Losses May Seek to Lead the Potential…"
WHY
  underlying +1.1%/+0.7%/-0.4% (favorable peak +1.7%); position move +0.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~3% · IV residual ~12% [inferred].
  convexity Γ·S = 2.24. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TPG-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 10.71 · spread +0.1%
  greeks Δ-0.179 Γ0.0412 Θ-0.024 · IV 0.478 · mid 0.62
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.30) · RSI 46
  headline "TPG Approaches Multi-Month Support as Bearish Institutional Options Volume Spikes"
WHY
  underlying +1.6%/-1.9%/-2.9% (favorable peak +3.3%); position move +2.9%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~36% · IV residual ~-16% [inferred].
  convexity Γ·S = 1.76. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MMYT-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ-0.338 Γ0.0403 Θ-0.058 · IV 0.689 · mid 2.67
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 59
  headline "Bank of America slashes MakeMyTrip (MMYT) price target to $60 from $105 on Q4 travel softness"
WHY
  underlying +6.6%/+3.7%/+0.3% (favorable peak +0.1%); position move -0.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-2% · IV residual ~16% [inferred].
  convexity Γ·S = 1.93. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PINS-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 338.43 · spread +0.1%
  greeks Δ-0.150 Γ0.0803 Θ-0.011 · IV 0.484 · mid 0.25
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 60
  headline "Pinterest's Earnings Surge: A Short-Lived Spike or a Start of a Recovery?"
WHY
  underlying +1.8%/+0.5%/-1.9% (favorable peak +3.3%); position move +1.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~24% · IV residual ~-3% [inferred].
  convexity Γ·S = 1.70. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE RH-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 30.00 · spread +0.0%
  greeks Δ-0.264 Γ0.0253 Θ-0.269 · IV 0.666 · mid 2.25
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 51
  headline "Most and least shorted stocks over $2B market cap: RH (RH) leads with 28.97% short interest"
WHY
  underlying +0.2%/-3.3%/-1.8% (favorable peak +5.6%); position move +1.8%.
  decomp [first-order]: theta drag ~36% of premium / 3d · delta capture ~28% · IV residual ~16% [inferred].
  convexity Γ·S = 3.38. exit TRAIL → realized +7%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ZS-2026-05-04-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ-0.374 Γ0.0105 Θ-0.173 · IV 0.782 · mid 11.27
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.40) · RSI 54
  headline "Zscaler (ZS) Ascends While Market Falls: Relief Rally Met with Massive Bearish Options Flow"
WHY
  underlying -0.6%/-2.4%/+7.4% (favorable peak +5.2%); position move -7.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-35% · IV residual ~47% [inferred].
  convexity Γ·S = 1.50. exit TIMEOUT → realized +7%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BLK-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 42 · V/OI n/a · spread +0.1%
  greeks Δ-0.447 Γ0.0040 Θ-0.449 · IV 0.285 · mid 38.75
  overnight_score 3 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 57
  headline "BlackRock Inc Stock (BLK) Moved Down by 3.05% on Apr 16: Key Drivers Unveiled"
WHY
  underlying +2.7%/+2.3%/+1.7% (favorable peak -1.1%); position move -1.7%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-21% · IV residual ~31% [inferred].
  convexity Γ·S = 4.12. exit TIMEOUT → realized +7%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LEN-2026-05-05-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 4.60 · spread +0.1%
  greeks Δ-0.465 Γ0.0676 Θ-0.122 · IV 0.421 · mid 1.86
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.70) · RSI 45
  headline "U.S. Labor Productivity Rises 0.8% in Q1 as Jobless Claims Fall to 200,000; Rates Pressure Homebuilders"
WHY
  underlying +5.0%/+1.8%/+2.5% (favorable peak -1.0%); position move -2.5%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-55% · IV residual ~81% [inferred].
  convexity Γ·S = 5.83. exit TRAIL → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RH-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.412 Γ0.0200 Θ-0.254 · IV 0.706 · mid 7.04
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.30) · RSI 52
  headline "RH (RH) Ascends While Market Falls: Some Facts to Note"
WHY
  underlying -0.4%/-1.5%/-3.7% (favorable peak +4.0%); position move +3.7%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~30% · IV residual ~-13% [inferred].
  convexity Γ·S = 2.77. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE COIN-2026-04-27-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 64.00 · spread +0.1%
  greeks Δ-0.270 Γ0.0067 Θ-0.209 · IV 0.774 · mid 9.35
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 54
  headline "Coinbase Q1 2026 Earnings Scheduled for May 7 Amid Rising Short Interest and Structural Competition Concerns"
WHY
  underlying -1.3%/-7.6%/-4.5% (favorable peak +9.7%); position move +4.5%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~26% · IV residual ~-13% [inferred].
  convexity Γ·S = 1.32. exit TRAIL → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AAOI-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 5.00 · spread +0.0%
  greeks Δ-0.433 Γ0.0070 Θ-0.766 · IV 2.017 · mid 21.17
  overnight_score 5 · flow HEDGING · catalyst Technical Breakout (0.65) · RSI 56
  headline "Simply Wall Street report suggests AAOI is significantly overvalued as stock retreats from highs"
WHY
  underlying +17.7%/+5.8%/-0.3% (favorable peak +1.7%); position move +0.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~1% · IV residual ~15% [inferred].
  convexity Γ·S = 0.96. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NOW-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 3.07 · spread +0.0%
  greeks Δ-0.296 Γ0.0245 Θ-0.068 · IV 0.498 · mid 2.97
  overnight_score 6 · flow HEDGING · catalyst Guidance Raise (0.85) · RSI 45
  headline "ServiceNow Targets $30 Billion Revenue by 2030 as AI Agent Momentum Accelerates"
WHY
  underlying -2.6%/-2.2%/-4.9% (favorable peak +5.2%); position move +4.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~46% · IV residual ~-33% [inferred].
  convexity Γ·S = 2.29. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAR-2026-05-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 20 · V/OI 18.50 · spread +0.1%
  greeks Δ-0.485 Γ0.0111 Θ-0.344 · IV 0.911 · mid 12.72
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 45
  headline "Avis Budget Group (CAR) Gains on Pricing Recovery Report Despite Analysts Maintaining Underweight Ratings"
WHY
  underlying -0.3%/-1.2%/+4.7% (favorable peak +3.4%); position move -4.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-30% · IV residual ~43% [inferred].
  convexity Γ·S = 1.86. exit TRAIL → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AVAV-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 9.00 · spread +0.0%
  greeks Δ-0.384 Γ0.0093 Θ-0.177 · IV 0.746 · mid 13.59
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.90) · RSI 35
  headline "Raymond James Issues Triple Downgrade as U.S. Space Force Reopens $1.4B Contract Bidding"
WHY
  underlying +2.7%/-1.9%/+0.3% (favorable peak +2.4%); position move -0.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-1% · IV residual ~11% [inferred].
  convexity Γ·S = 1.49. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DECK-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.401 Γ0.0242 Θ-0.194 · IV 0.818 · mid 5.05
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 34
  headline "Deckers (DECK) Facing 19% Earnings Contraction as Analysts Flag Brand Normalization"
WHY
  underlying +1.1%/-0.4%/+0.7% (favorable peak +1.0%); position move -0.7%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-5% · IV residual ~22% [inferred].
  convexity Γ·S = 2.28. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE GDDY-2026-04-24-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.185 Γ0.0146 Θ-0.071 · IV 0.700 · mid 2.67
  overnight_score 1 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 53
  headline "Earnings Preview: GoDaddy to Report Financial Results Post-market on April 30"
WHY
  underlying -2.0%/-0.9%/-0.3% (favorable peak +2.2%); position move +0.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~2% · IV residual ~11% [inferred].
  convexity Γ·S = 1.26. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LYFT-2026-04-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ-0.763 Γ0.1689 Θ-0.032 · IV 0.829 · mid 3.35
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 56
  headline "Lyft Underperforms Relief Rally as Analysts Slash Price Targets Ahead of May Earnings"
WHY
  underlying -2.8%/-1.4%/+0.3% (favorable peak +4.0%); position move -0.3%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-1% · IV residual ~9% [inferred].
  convexity Γ·S = 2.44. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TEM-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ-0.401 Γ0.0349 Θ-0.098 · IV 0.839 · mid 3.25
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 60
  headline "Jefferies Initiates Tempus AI (TEM) with Underperform Rating Amid Massive Insider Selling"
WHY
  underlying +2.7%/+4.3%/+1.3% (favorable peak -0.3%); position move -1.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-9% · IV residual ~23% [inferred].
  convexity Γ·S = 1.90. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MTN-2026-04-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ-0.263 Γ0.0200 Θ-0.084 · IV 0.430 · mid 2.62
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 47
  headline "BofA reiterates Vail Resorts stock rating on weak ski metrics, warns of guidance risk"
WHY
  underlying -0.8%/-1.5%/-0.7% (favorable peak +3.3%); position move +0.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~9% · IV residual ~6% [inferred].
  convexity Γ·S = 2.61. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE W-2026-04-30-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.290 Γ0.0490 Θ-0.153 · IV 0.747 · mid 1.04
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 32
  headline "Wayfair Shares Plunge After Earnings Miss and Cautious 'Choppy' Market Outlook"
WHY
  underlying +2.5%/+1.4%/-1.1% (favorable peak +2.1%); position move +1.1%.
  decomp [first-order]: theta drag ~44% of premium / 3d · delta capture ~20% · IV residual ~29% [inferred].
  convexity Γ·S = 3.13. exit TRAIL → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE COF-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 9.83 · spread +0.0%
  greeks Δ-0.252 Γ0.0160 Θ-0.072 · IV 0.320 · mid 3.44
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.30) · RSI 36
  headline "Capital One Financial (COF) Trading Down 1.3% as Stock Continues to Lag 200-Day Average"
WHY
  underlying +2.3%/+3.1%/+3.1% (favorable peak -0.3%); position move -3.1%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-41% · IV residual ~52% [inferred].
  convexity Γ·S = 2.91. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE OWL-2026-05-05-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.402 Γ0.1878 Θ-0.014 · IV 0.654 · mid 0.65
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 63
  headline "Blue Owl Capital Crystallizes 10x Gain on SpaceX Stake Amid Q1 Earnings Beat"
WHY
  underlying -2.0%/-3.7%/-1.8% (favorable peak +6.1%); position move +1.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~12% · IV residual ~-1% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAR-2026-05-04-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 1.43 · spread +0.0%
  greeks Δ-0.265 Γ0.0109 Θ-0.274 · IV 0.813 · mid 5.70
  overnight_score 7 · flow HEDGING · catalyst Analyst Downgrade (0.85) · RSI 42
  headline "Avis Budget Group (CAR) Shares Plunge 9.6% After JPMorgan Downgrade and Price Target Cut"
WHY
  underlying -4.9%/-2.4%/-8.5% (favorable peak +8.5%); position move +8.5%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~66% · IV residual ~-48% [inferred].
  convexity Γ·S = 1.84. exit TIMEOUT → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CSTM-2026-04-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 86.71 · spread +0.1%
  greeks Δ-0.432 Γ0.0716 Θ-0.044 · IV 0.705 · mid 1.97
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.40) · RSI 66
  headline "Constellium to Report First Quarter 2026 Results on April 29, 2026"
WHY
  underlying -1.1%/+1.8%/+0.0% (favorable peak +1.4%); position move -0.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-0% · IV residual ~11% [inferred].
  convexity Γ·S = 2.17. exit TIMEOUT → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RCL-2026-04-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 2.50 · spread +0.0%
  greeks Δ-0.327 Γ0.0074 Θ-0.243 · IV 0.588 · mid 12.20
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 43
  headline "BofA cuts Royal Caribbean price target to $310 on yield concerns and $90 crude oil headwinds"
WHY
  underlying -2.0%/+0.1%/-2.5% (favorable peak +3.0%); position move +2.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~18% · IV residual ~-9% [inferred].
  convexity Γ·S = 1.97. exit TIMEOUT → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MNDY-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI 0.64 · spread +0.0%
  greeks Δ-0.441 Γ0.0170 Θ-0.108 · IV 0.933 · mid 9.45
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 52
  headline "monday.com faces critical May 11 earnings and lawsuit deadline amid software sector 'SaaSpocalypse' fears"
WHY
  underlying +3.3%/-2.6%/+4.0% (favorable peak +6.9%); position move -4.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-14% · IV residual ~21% [inferred].
  convexity Γ·S = 1.26. exit TRAIL → realized +4%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LSCC-2026-04-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 43.42 · spread +0.1%
  greeks Δ-0.345 Γ0.0151 Θ-0.198 · IV 0.848 · mid 6.10
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.30) · RSI 66
  headline "Lattice Named 2026 Environment + Energy Leader Award Winner for MachXO5-NX FPGA"
WHY
  underlying +2.1%/+6.2%/+3.1% (favorable peak +0.5%); position move -3.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-21% · IV residual ~34% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized +3%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE UPST-2026-05-04-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 22.71 · spread +0.0%
  greeks Δ-0.440 Γ0.0497 Θ-0.090 · IV 1.141 · mid 2.84
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 54
  headline "Upstart Set to Report Q1 Earnings: What's in Store for the Stock?"
WHY
  underlying -2.8%/-10.5%/-9.6% (favorable peak +13.2%); position move +9.6%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~48% · IV residual ~-35% [inferred].
  convexity Γ·S = 1.60. exit TRAIL → realized +3%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE IDCC-2026-05-12-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI 2.67 · spread +0.1%
  greeks Δ-0.436 Γ0.0094 Θ-0.224 · IV 0.494 · mid 16.61
  overnight_score 1 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.30) · RSI 29
  headline "InterDigital Presents at Needham Conference Following 26% Post-Earnings Slide and Q2 Guidance Miss"
WHY
  underlying +0.1%/-0.2%/-3.5% (favorable peak +4.0%); position move +3.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~25% · IV residual ~-18% [inferred].
  convexity Γ·S = 2.52. exit TIMEOUT → realized +3%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CIEN-2026-05-22-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 26 · V/OI n/a · spread +0.0%
  greeks Δ-0.462 Γ0.0026 Θ-1.153 · IV 0.997 · mid 65.20
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.65) · RSI 61
  headline "Ciena (CIEN) Valuation Check After New AI And Cloud Networking Wins"
WHY
  underlying +3.2%/-0.3%/-2.3% (favorable peak +3.8%); position move +2.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~10% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized +3%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AVAV-2026-05-07-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 6.67 · spread +0.0%
  greeks Δ-0.421 Γ0.0107 Θ-0.198 · IV 0.706 · mid 12.65
  overnight_score 4 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 37
  headline "AeroVironment (AVAV) Stock Slides Despite Breakthrough in Homeland Defense Laser Technology"
WHY
  underlying +0.1%/-1.0%/+0.4% (favorable peak +5.9%); position move -0.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-2% · IV residual ~9% [inferred].
  convexity Γ·S = 1.80. exit TIMEOUT → realized +2%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AFRM-2026-05-06-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 3.75 · spread +0.0%
  greeks Δ-0.486 Γ0.0270 Θ-0.129 · IV 0.912 · mid 5.75
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 57
  headline "Affirm Beats Q3 Estimates and Raises Guidance; Shares Edge Lower on Sell-the-News Reaction"
WHY
  underlying +2.7%/-2.4%/+1.3% (favorable peak +5.6%); position move -1.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-7% · IV residual ~16% [inferred].
  convexity Γ·S = 1.77. exit TIMEOUT → realized +2%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NOW-2026-04-16-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.1%
  greeks Δ-0.273 Γ0.0188 Θ-0.135 · IV 0.758 · mid 3.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 44
  headline "Citi and Mizuho Slash ServiceNow Targets as AI Agent Fears Trigger 'SaaSpocalypse' Narrative"
WHY
  underlying +0.2%/+3.4%/+3.8% (favorable peak +0.3%); position move -3.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-30% · IV residual ~43% [inferred].
  convexity Γ·S = 1.81. exit TRAIL → realized +2%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DG-2026-05-27-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 2.07 · spread +0.0%
  greeks Δ-0.449 Γ0.0263 Θ-0.192 · IV 0.700 · mid 5.30
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 38
  headline "Dollar General was cut to Hold from Buy at Deutsche Bank, which has a $110 target price."
WHY
  underlying +5.3%/+6.0%/+5.4% (favorable peak -2.9%); position move -5.4%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-47% · IV residual ~60% [inferred].
  convexity Γ·S = 2.75. exit TIMEOUT → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DUOL-2026-05-18-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ-0.459 Γ0.0214 Θ-0.151 · IV 0.646 · mid 7.28
  overnight_score 8 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 60
  headline "Duolingo Consensus 2026 EPS Estimates Fall 32% as AI Spending Offsets Strong Q1 Results"
WHY
  underlying +0.8%/-5.7%/-6.7% (favorable peak +7.7%); position move +6.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~48% · IV residual ~-40% [inferred].
  convexity Γ·S = 2.42. exit TIMEOUT → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE COHR-2026-04-23-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 6.75 · spread +0.0%
  greeks Δ-0.494 Γ0.0037 Θ-0.591 · IV 1.012 · mid 50.14
  overnight_score 5 · flow HEDGING · catalyst Macro (0.75) · RSI 66
  headline "Coherent fell nearly 4% Thursday as the Nasdaq posted its worst session in a month, dragged lower by fading…"
WHY
  underlying -0.5%/-4.8%/-10.0% (favorable peak +13.8%); position move +10.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~33% · IV residual ~-28% [inferred].
  convexity Γ·S = 1.25. exit TIMEOUT → realized +1%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE HON-2026-04-21-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ-0.478 Γ0.0210 Θ-0.162 · IV 0.343 · mid 5.46
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 40
  headline "Honeywell (HON) Expected to Announce Q1 2026 Earnings Thursday; Shares Slip 3% in Pre-Earnings Positioning"
WHY
  underlying -1.0%/-3.5%/-4.1% (favorable peak +6.5%); position move +4.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~79% · IV residual ~-69% [inferred].
  convexity Γ·S = 4.66. exit TIMEOUT → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RBLX-2026-05-11-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 31 · V/OI 101.50 · spread +0.1%
  greeks Δ-0.490 Γ0.0529 Θ-0.047 · IV 0.628 · mid 3.21
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 28
  headline "Roblox Investigation Initiated Over Potential Securities Violations Following Guidance Slash"
WHY
  underlying +0.6%/+1.6%/+5.8% (favorable peak +2.8%); position move -5.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-37% · IV residual ~42% [inferred].
  convexity Γ·S = 2.19. exit TRAIL → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FICO-2026-04-15-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ-0.430 Γ0.0019 Θ-1.331 · IV 0.697 · mid 75.36
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 42
  headline "Barclays Slashes FICO Price Target as Stock Hits New 52-Week Lows"
WHY
  underlying +3.8%/+4.1%/+3.2% (favorable peak -0.0%); position move -3.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-19% · IV residual ~24% [inferred].
  convexity Γ·S = 2.00. exit TIMEOUT → realized +0%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SPGI-2026-05-20-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 1.50 · spread +0.0%
  greeks Δ-0.417 Γ0.0198 Θ-0.431 · IV 0.307 · mid 8.80
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 46
  headline "S&P Global stock rallied after Mobility Global Inc. commenced $2 billion private offering of senior notes"
WHY
  underlying -0.3%/+0.1%/-1.1% (favorable peak +2.1%); position move +1.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~21% · IV residual ~-6% [inferred].
  convexity Γ·S = 8.26. exit TIMEOUT → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIG-2026-04-14-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 44 · V/OI n/a · spread +0.0%
  greeks Δ-0.458 Γ0.0643 Θ-0.027 · IV 0.966 · mid 2.40
  overnight_score 4 · flow HEDGING · catalyst Sector Rotation (0.85) · RSI 34
  headline "Figma (NYSE:FIG) Hits New 12-Month Low Amid Sector-Wide Software Sell-Off"
WHY
  underlying +10.4%/+10.3%/+2.7% (favorable peak -1.0%); position move -2.7%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-10% · IV residual ~13% [inferred].
  convexity Γ·S = 1.18. exit TIMEOUT → realized +0%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MCO-2026-05-13-S  ·  BEARISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 4.41 · spread +0.1%
  greeks Δ-0.225 Γ0.0069 Θ-0.180 · IV 0.320 · mid 6.48
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.70) · RSI 42
  headline "Moody's Corp hits 20-day low amid economic challenges and rising inflation"
WHY
  underlying -1.5%/-2.1%/+1.2% (favorable peak +2.8%); position move -1.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-18% · IV residual ~26% [inferred].
  convexity Γ·S = 3.04. exit TRAIL → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

---

## BACKTEST · LOST  (358)

```
CASE BSX-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 24.08 · spread +0.1%
  greeks Δ-0.299 Γ0.0706 Θ-0.037 · IV 0.375 · mid 0.88
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 30
  headline "Boston Scientific hits 52-week low at $53.10 following guidance reset and FDA Class I software recall"
WHY
  underlying +0.9%/-0.7%/+5.4% (favorable peak +1.0%); position move -5.4%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-97% · IV residual ~50% [inferred].
  convexity Γ·S = 3.75. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUN-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 81.97 · spread +0.0%
  greeks Δ-0.736 Γ0.1673 Θ-0.020 · IV 0.679 · mid 1.74
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 56
  headline "Huntsman to Report Q1 2026 Results April 30 Amid Heavy Bearish Options Activity"
WHY
  underlying -3.0%/+5.2%/+7.1% (favorable peak +4.0%); position move -7.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-41% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.29. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 4.00 · spread +0.0%
  greeks Δ-0.357 Γ0.0089 Θ-0.360 · IV 0.558 · mid 9.43
  overnight_score 8 · flow HEDGING · catalyst Guidance Raise (0.85) · RSI 32
  headline "Intuit Stock Tumbles After Massive Workforce Cuts and Earnings Report"
WHY
  underlying +1.7%/+7.7%/+15.0% (favorable peak +1.5%); position move -15.0%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-174% · IV residual ~126% [inferred].
  convexity Γ·S = 2.75. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NOW-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI 5.93 · spread +0.1%
  greeks Δ-0.416 Γ0.0216 Θ-0.081 · IV 0.586 · mid 6.25
  overnight_score 6 · flow MIXED · catalyst — (—) · RSI 46
WHY
  underlying +5.0%/+14.3%/+12.5% (favorable peak -1.6%); position move -12.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-75% · IV residual ~19% [inferred].
  convexity Γ·S = 1.95. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ACN-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 1.00 · spread +0.1%
  greeks Δ-0.297 Γ0.0214 Θ-0.170 · IV 0.445 · mid 2.27
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 33
  headline "Accenture (ACN) Stock Drops to 52-Week Low as OpenAI Enters Deployment Services Market"
WHY
  underlying -6.0%/-3.4%/-0.6% (favorable peak +8.2%); position move +0.6%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~12% · IV residual ~-50% [inferred].
  convexity Γ·S = 3.63. exit STOP → realized -60%.
TAKEAWAY: Lost to decay with no decisive underlying move.
```

```
CASE ADSK-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ-0.317 Γ0.0142 Θ-0.216 · IV 0.487 · mid 6.58
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 33
  headline "Citigroup Slashes Autodesk Target to $246, Citing AI Disruption Fears and Valuation Reset"
WHY
  underlying +4.0%/+4.6%/+9.6% (favorable peak +0.9%); position move -9.6%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-101% · IV residual ~51% [inferred].
  convexity Γ·S = 3.11. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AEHR-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.432 Γ0.0207 Θ-0.387 · IV 1.413 · mid 7.31
  overnight_score 4 · flow HEDGING · catalyst Sector Rotation (0.75) · RSI 63
  headline "Shares of Semiconductor Companies Are Trading Lower Following Reports That OpenAI Has Missed Some Internal …"
WHY
  underlying -0.8%/+9.9%/+12.9% (favorable peak +5.3%); position move -12.9%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-63% · IV residual ~19% [inferred].
  convexity Γ·S = 1.71. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BE-2026-04-24-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 6.00 · spread +0.0%
  greeks Δ-0.261 Γ0.0038 Θ-0.399 · IV 1.193 · mid 15.80
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 71
  headline "Bloom Energy to Announce First Quarter 2026 Financial Results on April 28, 2026"
WHY
  underlying +1.5%/-2.1%/+24.6% (favorable peak +6.5%); position move -24.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-94% · IV residual ~41% [inferred].
  convexity Γ·S = 0.89. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CEG-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 17.00 · spread +0.0%
  greeks Δ-0.378 Γ0.0103 Θ-0.239 · IV 0.471 · mid 12.30
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 45
  headline "Utility shares surge on PJM's plans to speed up data center timeline"
WHY
  underlying +1.6%/+4.6%/+7.2% (favorable peak -0.1%); position move -7.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-62% · IV residual ~8% [inferred].
  convexity Γ·S = 2.91. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CF-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 9.00 · spread +0.0%
  greeks Δ-0.345 Γ0.0252 Θ-0.314 · IV 0.786 · mid 3.36
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 43
  headline "CF Industries Faces Production Headwinds as Yazoo City Outage Extended Through Q4 2026"
WHY
  underlying -0.9%/-4.0%/+3.9% (favorable peak +5.4%); position move -3.9%.
  decomp [first-order]: theta drag ~28% of premium / 3d · delta capture ~-49% · IV residual ~17% [inferred].
  convexity Γ·S = 3.01. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CLS-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 3.14 · spread +0.1%
  greeks Δ-0.460 Γ0.0054 Θ-0.479 · IV 0.713 · mid 31.80
  overnight_score 5 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 53
  headline "Celestica Stock Plunges 14% Despite Q1 Earnings Beat and Raised 2026 Outlook"
WHY
  underlying +4.1%/+13.3%/+15.9% (favorable peak +0.8%); position move -15.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-83% · IV residual ~27% [inferred].
  convexity Γ·S = 1.95. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CLSK-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.1%
  greeks Δ-0.363 Γ0.1515 Θ-0.017 · IV 0.903 · mid 0.74
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 55
  headline "Bitcoin Faces Stress Test Ahead of CPI as Fed Pressure Meets Institutional Flows"
WHY
  underlying +7.4%/+12.5%/+12.4% (favorable peak +3.7%); position move -12.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-61% · IV residual ~8% [inferred].
  convexity Γ·S = 1.52. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CPB-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 0.24 · spread +0.0%
  greeks Δ-0.467 Γ0.3527 Θ-0.027 · IV 0.355 · mid 0.41
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 48
  headline "Campbell Soup stock hasn't been this low in over 30 years."
WHY
  underlying +1.5%/+3.0%/+2.8% (favorable peak +0.6%); position move -2.8%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-66% · IV residual ~26% [inferred].
  convexity Γ·S = 7.23. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CRWD-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 3.77 · spread +0.0%
  greeks Δ-0.329 Γ0.0068 Θ-0.450 · IV 0.503 · mid 12.84
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 57
  headline "PANW, CRWD, NET: Here's Why Cybersecurity Stocks Are Falling Today"
WHY
  underlying +2.2%/+5.3%/+6.9% (favorable peak +0.0%); position move -6.9%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-79% · IV residual ~29% [inferred].
  convexity Γ·S = 3.03. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DASH-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 1.83 · spread +0.0%
  greeks Δ-0.420 Γ0.0294 Θ-0.293 · IV 0.575 · mid 3.05
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 34
  headline "DoorDash Stock Dips as 2026 Spending Worries and Margin Compression Fears Persist"
WHY
  underlying +3.1%/+6.8%/+9.1% (favorable peak +0.5%); position move -9.1%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~-187% · IV residual ~156% [inferred].
  convexity Γ·S = 4.38. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DHI-2026-05-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 5.00 · spread +0.0%
  greeks Δ-0.467 Γ0.0502 Θ-0.204 · IV 0.381 · mid 3.30
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.70) · RSI 49
  headline "D.R. Horton recently benefited from data showing strong U.S. pending home sales and an analyst report citin…"
WHY
  underlying -0.3%/+1.0%/+2.5% (favorable peak +2.2%); position move -2.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-52% · IV residual ~11% [inferred].
  convexity Γ·S = 7.23. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DOCN-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 9.50 · spread +0.0%
  greeks Δ-0.453 Γ0.0135 Θ-0.378 · IV 0.961 · mid 11.31
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.30) · RSI 60
  headline "Hippocratic AI Scales to 10 Million Patient Calls at 99.9% Clinical Safety on DigitalOcean's AI-Native Cloud"
WHY
  underlying +1.0%/+3.7%/+15.3% (favorable peak +1.3%); position move -15.3%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-92% · IV residual ~42% [inferred].
  convexity Γ·S = 2.03. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DUOL-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 11.00 · spread +0.1%
  greeks Δ-0.421 Γ0.0407 Θ-0.104 · IV 0.462 · mid 7.98
  overnight_score 7 · flow HEDGING · catalyst Guidance Cut (0.95) · RSI 60
  headline "Duolingo shares plummet 14% as weak bookings guidance overshadows earnings beat"
WHY
  underlying -5.6%/-4.7%/+3.1% (favorable peak +10.6%); position move -3.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-18% · IV residual ~-38% [inferred].
  convexity Γ·S = 4.48. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EL-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 100.33 · spread +0.1%
  greeks Δ-0.368 Γ0.0323 Θ-0.140 · IV 0.745 · mid 3.19
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 44
  headline "Estée Lauder (EL) Faces Earnings Test May 1 Amid Bearish Analyst Revisions and Negative ESP"
WHY
  underlying +1.3%/+4.8%/+7.5% (favorable peak +0.6%); position move -7.5%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-65% · IV residual ~18% [inferred].
  convexity Γ·S = 2.45. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EME-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 2.00 · spread +0.0%
  greeks Δ-0.310 Γ0.0034 Θ-1.111 · IV 0.576 · mid 24.10
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.85) · RSI 66
  headline "EMCOR Group (EME) Shares Pull Back 2.4% Ahead of Q1 2026 Earnings Release"
WHY
  underlying -3.5%/+3.2%/+4.6% (favorable peak +3.8%); position move -4.6%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-51% · IV residual ~5% [inferred].
  convexity Γ·S = 2.90. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FIGR-2026-05-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 111.20 · spread +0.0%
  greeks Δ-0.366 Γ0.0816 Θ-0.112 · IV 0.915 · mid 1.12
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.40) · RSI 43
  headline "Figure Technology Solutions CEO Michael Tannenbaum Sells Shares Under 10b5-1 Plan Following Strong Q1 Results"
WHY
  underlying -1.3%/+2.4%/-0.8% (favorable peak +2.3%); position move +0.8%.
  decomp [first-order]: theta drag ~30% of premium / 3d · delta capture ~9% · IV residual ~-40% [inferred].
  convexity Γ·S = 2.81. exit STOP → realized -60%.
TAKEAWAY: Lost to decay with no decisive underlying move.
```

```
CASE GCT-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 11.23 · spread +0.0%
  greeks Δ-0.517 Γ0.0473 Θ-0.155 · IV 1.127 · mid 4.26
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 47
  headline "GigaCloud Technology (GCT) Scheduled to Report First Quarter 2026 Financial Results on May 7"
WHY
  underlying -3.7%/+2.8%/-2.1% (favorable peak +5.6%); position move +2.1%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~11% · IV residual ~-60% [inferred].
  convexity Γ·S = 2.07. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GLW-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 24.00 · spread +0.0%
  greeks Δ-0.297 Γ0.0109 Θ-0.159 · IV 0.658 · mid 6.42
  overnight_score 4 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 51
  headline "Corning falls after Q2 sales outlook misses estimates; Jim Cramer warns of 'Icarus moment'"
WHY
  underlying +1.1%/+2.4%/+14.7% (favorable peak -0.0%); position move -14.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-108% · IV residual ~55% [inferred].
  convexity Γ·S = 1.72. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUN-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 80.26 · spread +0.0%
  greeks Δ-0.620 Γ0.1892 Θ-0.025 · IV 0.745 · mid 1.33
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 50
  headline "Huntsman to Discuss First Quarter 2026 Results on May 1, 2026"
WHY
  underlying +8.5%/+10.4%/+7.3% (favorable peak -0.7%); position move -7.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-45% · IV residual ~-9% [inferred].
  convexity Γ·S = 2.51. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUT-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 256.60 · spread +0.1%
  greeks Δ-0.459 Γ0.0283 Θ-0.293 · IV 1.215 · mid 5.64
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 59
  headline "Hut 8 Announces Pricing of $3.25 Billion of Investment-Grade Senior Secured Notes for River Bend Data Cente…"
WHY
  underlying -1.5%/+5.1%/+6.8% (favorable peak +3.9%); position move -6.8%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-40% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.04. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ-0.316 Γ0.0097 Θ-0.752 · IV 0.609 · mid 11.75
  overnight_score 6 · flow HEDGING · catalyst Technical Breakout (0.75) · RSI 43
  headline "Intuit Rebounds 7% from 4-Year Lows as Tax Day Deadline and Dividend Payout Drive Short-Term Sentiment"
WHY
  underlying -0.7%/+0.9%/+3.9% (favorable peak +1.0%); position move -3.9%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-41% · IV residual ~-0% [inferred].
  convexity Γ·S = 3.78. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LLY-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI 3.09 · spread +0.0%
  greeks Δ-0.379 Γ0.0033 Θ-0.668 · IV 0.449 · mid 31.18
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 35
  headline "Eli Lilly Stock Slides As Initial Sales Data For New Oral Drug Foundayo Disappoints"
WHY
  underlying +0.7%/-2.0%/+7.6% (favorable peak +2.0%); position move -7.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-81% · IV residual ~27% [inferred].
  convexity Γ·S = 2.90. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDB-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.385 Γ0.0052 Θ-0.833 · IV 1.121 · mid 23.55
  overnight_score 8 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.80) · RSI 56
  headline "MongoDB drops 5.8% ahead of Thursday earnings"
WHY
  underlying -4.2%/+6.0%/+9.2% (favorable peak +4.8%); position move -9.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-46% · IV residual ~-3% [inferred].
  convexity Γ·S = 1.60. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NTNX-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 22 · V/OI 3.73 · spread +0.0%
  greeks Δ-0.496 Γ0.0449 Θ-0.077 · IV 0.773 · mid 4.10
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.95) · RSI 59
  headline "Nutanix (NTNX) Set to Report Q3 Earnings After Close Amid Significant EPS Revisions and AMD Dilution Overhang"
WHY
  underlying +0.0%/+4.9%/+11.9% (favorable peak +3.7%); position move -11.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-67% · IV residual ~13% [inferred].
  convexity Γ·S = 2.09. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PG-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 3.89 · spread +0.1%
  greeks Δ-0.470 Γ0.0787 Θ-0.058 · IV 0.162 · mid 2.07
  overnight_score 4 · flow HEDGING · catalyst Analyst Downgrade (0.75) · RSI 43
  headline "Procter & Gamble Shares Fall 2.6% as Analysts Trim Price Targets Following Revenue Miss"
WHY
  underlying +1.0%/+3.1%/+1.8% (favorable peak +0.9%); position move -1.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-60% · IV residual ~8% [inferred].
  convexity Γ·S = 11.28. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PSKY-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 0.10 · spread +0.0%
  greeks Δ-0.362 Γ0.5935 Θ-0.015 · IV 0.409 · mid 0.17
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 54
  headline "Wells Fargo Slashes Paramount Skydance (PSKY) Price Target to $7.00, Citing Valuation Risks"
WHY
  underlying +3.1%/+1.3%/-0.7% (favorable peak +2.1%); position move +0.7%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~15% · IV residual ~-48% [inferred].
  convexity Γ·S = 6.39. exit STOP → realized -60%.
TAKEAWAY: Lost to decay with no decisive underlying move.
```

```
CASE QS-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 0.47 · spread +0.1%
  greeks Δ-0.423 Γ0.2067 Θ-0.016 · IV 1.063 · mid 0.66
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.90) · RSI 53
  headline "QuantumScape Will Report Q1 Earnings Tomorrow. Here's What to Expect"
WHY
  underlying +4.7%/+6.2%/+3.4% (favorable peak +0.3%); position move -3.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-15% · IV residual ~-37% [inferred].
  convexity Γ·S = 1.44. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RDDT-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ-0.381 Γ0.0145 Θ-0.142 · IV 0.611 · mid 7.63
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 40
  headline "Meta launches 'Forum' discussion app, triggering competitive fears for Reddit"
WHY
  underlying +2.1%/+8.8%/+18.4% (favorable peak +1.5%); position move -18.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-130% · IV residual ~75% [inferred].
  convexity Γ·S = 2.05. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RH-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 5.33 · spread +0.1%
  greeks Δ-0.394 Γ0.0200 Θ-0.207 · IV 0.725 · mid 6.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 40
  headline "RH (RH) Stock Declines While Market Improves; Analysts Forecast Massive Earnings Miss"
WHY
  underlying +1.2%/+10.3%/+15.2% (favorable peak +5.9%); position move -15.2%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-117% · IV residual ~67% [inferred].
  convexity Γ·S = 2.41. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RH-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 2.50 · spread +0.0%
  greeks Δ-0.228 Γ0.0148 Θ-0.225 · IV 0.781 · mid 2.30
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.30) · RSI 55
  headline "RH Faces Persistent Headwinds as Analysts Highlight Weak Luxury Demand and Housing Market Stagnation"
WHY
  underlying +1.5%/+5.2%/+9.3% (favorable peak +0.2%); position move -9.3%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~-126% · IV residual ~95% [inferred].
  convexity Γ·S = 2.01. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RKLB-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ-0.449 Γ0.0180 Θ-0.117 · IV 0.892 · mid 9.46
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 69
  headline "Rocket Lab (RKLB) Stock Blasts 26% Higher on Record Q1 Revenue and $2.2B Backlog Surpassing Expectations"
WHY
  underlying +7.5%/-0.2%/+33.9% (favorable peak +1.1%); position move -33.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-127% · IV residual ~70% [inferred].
  convexity Γ·S = 1.42. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ROKU-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 6.66 · spread +0.1%
  greeks Δ-0.319 Γ0.0185 Θ-0.210 · IV 0.820 · mid 4.44
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.95) · RSI 59
  headline "Roku set to report Q1 2026 earnings on April 30 as analysts highlight platform momentum"
WHY
  underlying +0.3%/+3.8%/+10.1% (favorable peak +1.9%); position move -10.1%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-81% · IV residual ~35% [inferred].
  convexity Γ·S = 2.08. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SBET-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.1%
  greeks Δ-0.443 Γ0.3107 Θ-0.018 · IV 1.016 · mid 0.40
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 44
  headline "No significant news found for SBET in the past 48 hours."
WHY
  underlying +2.8%/+9.5%/+16.1% (favorable peak +3.5%); position move -16.1%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-116% · IV residual ~70% [inferred].
  convexity Γ·S = 2.03. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SHOP-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 29 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.457 Γ0.0229 Θ-0.116 · IV 0.581 · mid 6.55
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.25) · RSI 46
  headline "Shopify (SHOP) Valuation Check As AI Growth And Thrive Capital Investment Put Future Cash Flows In Focus"
WHY
  underlying +7.9%/+11.4%/+16.4% (favorable peak -0.3%); position move -16.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-122% · IV residual ~68% [inferred].
  convexity Γ·S = 2.44. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TEM-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ-0.473 Γ0.0394 Θ-0.073 · IV 0.860 · mid 3.14
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 35
  headline "Jefferies initiates Tempus AI stock with underperform rating, citing unclear catalyst path and $35 price ta…"
WHY
  underlying +7.1%/+15.3%/+31.4% (favorable peak +0.9%); position move -31.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-203% · IV residual ~150% [inferred].
  convexity Γ·S = 1.69. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TEM-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 8.77 · spread +0.1%
  greeks Δ-0.281 Γ0.0441 Θ-0.147 · IV 0.988 · mid 1.52
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.45) · RSI 48
  headline "Tempus to Host Inaugural Investor Day on May 29, 2026"
WHY
  underlying +10.9%/+10.0%/+11.6% (favorable peak -1.1%); position move -11.6%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~-107% · IV residual ~76% [inferred].
  convexity Γ·S = 2.21. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TMO-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 8 · V/OI 3.00 · spread +0.0%
  greeks Δ-0.654 Γ0.0138 Θ-0.556 · IV 0.384 · mid 24.20
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 45
  headline "Thermo Fisher Scientific (TMO) Announces Results of Annual Shareholder Meeting"
WHY
  underlying +6.8%/+8.0%/+8.3% (favorable peak -1.1%); position move -8.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-102% · IV residual ~49% [inferred].
  convexity Γ·S = 6.28. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE USAR-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 2.97 · spread +0.1%
  greeks Δ-0.607 Γ0.1008 Θ-0.086 · IV 1.139 · mid 2.37
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 57
  headline "Rare Earth Stocks Sink on U.S. Price Floor, Trading Bloc Plans; USAR Down 3%"
WHY
  underlying +17.9%/+19.5%/+16.1% (favorable peak -2.5%); position move -16.1%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-91% · IV residual ~42% [inferred].
  convexity Γ·S = 2.22. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VG-2026-05-08-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 27 · V/OI 6.15 · spread +0.0%
  greeks Δ-0.458 Γ0.1431 Θ-0.020 · IV 0.898 · mid 1.10
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 41
  headline "VG Insiders Cash Out as Stock Sinks Into Earnings"
WHY
  underlying +1.5%/+15.9%/+13.5% (favorable peak +0.0%); position move -13.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-65% · IV residual ~10% [inferred].
  convexity Γ·S = 1.64. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VST-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ-0.215 Γ0.0165 Θ-0.301 · IV 0.752 · mid 2.42
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 45
  headline "Vistra Corp. (VST) Short Interest Surges 20.4% as Shares Break Key Technical Support"
WHY
  underlying +2.6%/+1.0%/+4.6% (favorable peak -0.7%); position move -4.6%.
  decomp [first-order]: theta drag ~37% of premium / 3d · delta capture ~-63% · IV residual ~40% [inferred].
  convexity Γ·S = 2.53. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WDAY-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.479 Γ0.0339 Θ-0.244 · IV 0.622 · mid 4.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 37
  headline "DA Davidson Slashes Workday (WDAY) Price Target to $125 from $250 Citing Growth Concerns"
WHY
  underlying +5.3%/+5.9%/+5.1% (favorable peak -0.3%); position move -5.1%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-63% · IV residual ~20% [inferred].
  convexity Γ·S = 4.00. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WIX-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.279 Γ0.0221 Θ-0.089 · IV 0.793 · mid 3.16
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 36
  headline "Anthropic set to launch AI design tool this week, threatening Wix core business"
WHY
  underlying -0.7%/+10.0%/+12.2% (favorable peak +3.0%); position move -12.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-74% · IV residual ~23% [inferred].
  convexity Γ·S = 1.52. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE XP-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 0.88 · spread +0.0%
  greeks Δ-0.274 Γ0.1369 Θ-0.052 · IV 0.941 · mid 0.35
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.70) · RSI 39
  headline "Zacks Upgrades XP to Buy Ahead of May 18 Earnings as Analysts Trim Revenue Estimates"
WHY
  underlying -0.7%/-1.5%/-5.3% (favorable peak +7.7%); position move +5.3%.
  decomp [first-order]: theta drag ~45% of premium / 3d · delta capture ~73% · IV residual ~-88% [inferred].
  convexity Γ·S = 2.41. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ZS-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.287 Γ0.0100 Θ-0.372 · IV 0.963 · mid 6.93
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 72
  headline "Zscaler to release third quarter fiscal year 2026 earnings after the market closes on Tuesday, May 26, 2026."
WHY
  underlying -2.0%/+4.5%/+5.8% (favorable peak +3.3%); position move -5.8%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-42% · IV residual ~-2% [inferred].
  convexity Γ·S = 1.74. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZS-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.446 Γ0.0225 Θ-0.197 · IV 0.660 · mid 6.84
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 32
  headline "BTIG Downgrades Zscaler to Neutral, Removing Price Target Amid Intensifying Competition from Cloudflare and…"
WHY
  underlying +0.0%/+6.8%/+9.5% (favorable peak +1.5%); position move -9.5%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-76% · IV residual ~25% [inferred].
  convexity Γ·S = 2.75. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CRDO-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ-0.394 Γ0.0076 Θ-0.316 · IV 1.118 · mid 17.82
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 49
  headline "Credo Technology Group (CRDO) Slumps 8.7% as Technical Indicators Turn Negative Ahead of June Earnings"
WHY
  underlying +8.1%/+17.1%/+23.8% (favorable peak +4.7%); position move -23.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-82% · IV residual ~27% [inferred].
  convexity Γ·S = 1.19. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MNDY-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 0.01 · spread +0.1%
  greeks Δ-0.303 Γ0.0211 Θ-0.189 · IV 1.228 · mid 4.06
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.65) · RSI 46
  headline "MNDY INVESTOR ALERT: Multiple Law Firms Announce Securities Fraud Class Action Lawsuits Against monday.com"
WHY
  underlying -1.2%/+9.1%/+16.0% (favorable peak +4.2%); position move -16.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-80% · IV residual ~34% [inferred].
  convexity Γ·S = 1.41. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SCHW-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.1%
  greeks Δ-0.429 Γ0.0495 Θ-0.073 · IV 0.355 · mid 3.01
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.82) · RSI 50
  headline "Morgan Stanley Trims Charles Schwab Price Target to $135 Ahead of Q1 Earnings"
WHY
  underlying +2.1%/+3.8%/+5.8% (favorable peak +0.6%); position move -5.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-78% · IV residual ~25% [inferred].
  convexity Γ·S = 4.69. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VST-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.467 Γ0.0209 Θ-0.124 · IV 0.491 · mid 8.70
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 32
  headline "A Look At Vistra (VST) Valuation After Strong Q1 Results And Ongoing Buybacks"
WHY
  underlying -1.5%/+5.3%/+9.0% (favorable peak +3.0%); position move -9.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-66% · IV residual ~12% [inferred].
  convexity Γ·S = 2.86. exit TIMEOUT → realized -59%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NKE-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ-0.398 Γ0.1201 Θ-0.035 · IV 0.338 · mid 0.91
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 30
  headline "Nike Stock Hits 12-Year Low as Analysts Warn of Declining Basketball Hype and Competitive Gains by Adidas"
WHY
  underlying -0.1%/+1.8%/+3.1% (favorable peak +1.0%); position move -3.1%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-58% · IV residual ~11% [inferred].
  convexity Γ·S = 5.18. exit TIMEOUT → realized -59%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SHOP-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.450 Γ0.0234 Θ-0.091 · IV 0.525 · mid 7.13
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Cut (0.80) · RSI 44
  headline "Shopify Guidance Concerns Overshadow Q1 Beat as AI Investment Costs Weigh on Margins"
WHY
  underlying +1.6%/+9.7%/+13.2% (favorable peak +1.0%); position move -13.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-87% · IV residual ~33% [inferred].
  convexity Γ·S = 2.45. exit TIMEOUT → realized -58%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZS-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 5.60 · spread +0.0%
  greeks Δ-0.343 Γ0.0118 Θ-0.253 · IV 0.828 · mid 10.83
  overnight_score 5 · flow HEDGING · catalyst Sector Rotation (0.70) · RSI 60
  headline "Cybersecurity stocks jump as Fortinet earnings spark sector-wide growth optimism"
WHY
  underlying +0.8%/+5.7%/+14.6% (favorable peak +4.0%); position move -14.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-70% · IV residual ~21% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized -57%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PSKY-2026-05-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 0.07 · spread +0.0%
  greeks Δ-0.325 Γ0.4911 Θ-0.009 · IV 0.359 · mid 0.25
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.78) · RSI 46
  headline "Democratic senators raise alarm over foreign investment in Paramount, Warner Bros merger"
WHY
  underlying +1.8%/+0.9%/+3.3% (favorable peak -0.1%); position move -3.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-44% · IV residual ~-1% [inferred].
  convexity Γ·S = 5.05. exit TIMEOUT → realized -56%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ANET-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 1.00 · spread +0.1%
  greeks Δ-0.410 Γ0.0195 Θ-0.132 · IV 0.514 · mid 5.94
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.70) · RSI 41
  headline "Arista Networks CTO Kenneth Duda sells $8.1 million in stock under 10b5-1 plan"
WHY
  underlying +5.8%/+9.6%/+12.5% (favorable peak +1.0%); position move -12.5%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-121% · IV residual ~73% [inferred].
  convexity Γ·S = 2.74. exit TIMEOUT → realized -55%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MMYT-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.444 Γ0.0793 Θ-0.032 · IV 0.435 · mid 2.08
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.65) · RSI 52
  headline "MakeMyTrip Shrugs Off Analyst Price Target Cuts as Summer Travel Bookings Drive 21% Rally"
WHY
  underlying +5.1%/+7.2%/+14.3% (favorable peak -1.1%); position move -14.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-137% · IV residual ~86% [inferred].
  convexity Γ·S = 3.54. exit TIMEOUT → realized -55%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FIS-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 2.33 · spread +0.0%
  greeks Δ-0.403 Γ0.1429 Θ-0.054 · IV 0.390 · mid 0.95
  overnight_score 8 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 39
  headline "Fidelity National Information Services Shares Near 52-Week Lows as Analysts Warn of 'Value Trap' Risks"
WHY
  underlying -0.5%/+0.0%/+1.8% (favorable peak +1.9%); position move -1.8%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-33% · IV residual ~-5% [inferred].
  convexity Γ·S = 6.04. exit TIMEOUT → realized -55%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FCX-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 51.00 · spread +0.0%
  greeks Δ-0.476 Γ0.0468 Θ-0.043 · IV 0.481 · mid 3.20
  overnight_score 3 · flow HEDGING · catalyst Analyst Downgrade (0.85) · RSI 36
  headline "Morgan Stanley Downgrades Freeport-McMoRan on Grasberg Production Delays and Rising Costs"
WHY
  underlying +3.8%/+9.6%/+9.1% (favorable peak -1.2%); position move -9.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-75% · IV residual ~25% [inferred].
  convexity Γ·S = 2.60. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PGY-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ-0.288 Γ0.0855 Θ-0.022 · IV 1.106 · mid 0.92
  overnight_score 2 · flow HEDGING · catalyst Macro (0.45) · RSI 54
  headline "Pagaya Announces Timing of First Quarter 2026 Earnings Release"
WHY
  underlying +4.2%/+13.8%/+17.9% (favorable peak -1.8%); position move -17.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-70% · IV residual ~23% [inferred].
  convexity Γ·S = 1.07. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CTSH-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 0.35 · spread +0.1%
  greeks Δ-0.347 Γ0.0689 Θ-0.045 · IV 0.421 · mid 1.40
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.65) · RSI 46
  headline "Citigroup Lowers Cognizant (CTSH) Price Target to $51 Following Broad Reset of Expectations"
WHY
  underlying +2.6%/+3.9%/+7.6% (favorable peak -0.0%); position move -7.6%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-98% · IV residual ~54% [inferred].
  convexity Γ·S = 3.57. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EOG-2026-04-17-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 6.50 · spread +0.1%
  greeks Δ-0.473 Γ0.0481 Θ-0.123 · IV 0.334 · mid 2.22
  overnight_score 4 · flow HEDGING · catalyst Macro (0.85) · RSI 39
  headline "Oil Prices Fall Amid Hormuz Reopening and Ceasefire Optimism as Fed Cautions on Rate Cuts"
WHY
  underlying +0.6%/+3.1%/+3.6% (favorable peak +0.3%); position move -3.6%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-98% · IV residual ~60% [inferred].
  convexity Γ·S = 6.18. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ANET-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 3.68 · spread +0.0%
  greeks Δ-0.401 Γ0.0235 Θ-0.176 · IV 0.549 · mid 4.70
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 35
  headline "ANET Stock Sinks After CEO Says Chip Shortages Will Weigh On Margins Through 2026"
WHY
  underlying +4.5%/+3.1%/+8.3% (favorable peak +0.8%); position move -8.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-97% · IV residual ~55% [inferred].
  convexity Γ·S = 3.20. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APP-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 4.00 · spread +0.1%
  greeks Δ-0.464 Γ0.0048 Θ-1.931 · IV 1.236 · mid 37.83
  overnight_score 6 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 50
  headline "AppLovin CEO Divests $23M as Institutional Put Buying Spikes Ahead of Q1 Earnings"
WHY
  underlying +0.7%/+3.7%/+7.1% (favorable peak +2.2%); position move -7.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-39% · IV residual ~2% [inferred].
  convexity Γ·S = 2.12. exit TIMEOUT → realized -52%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE U-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ-0.451 Γ0.0575 Θ-0.083 · IV 1.196 · mid 2.64
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 66
  headline "Needham raises Unity Software stock price target on Vector growth following Q1 revenue beat"
WHY
  underlying -0.2%/-2.2%/+3.0% (favorable peak +5.6%); position move -3.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-14% · IV residual ~-28% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized -51%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ELF-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.555 Γ0.0483 Θ-0.115 · IV 0.651 · mid 4.59
  overnight_score 4 · flow HEDGING · catalyst Macro (0.65) · RSI 43
  headline "e.l.f. Beauty Shares Surge as Geopolitical Tensions Ease; Goldman Sachs Reaffirms Buy Rating"
WHY
  underlying +0.8%/+5.8%/+7.3% (favorable peak +1.6%); position move -7.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-57% · IV residual ~14% [inferred].
  convexity Γ·S = 3.15. exit TIMEOUT → realized -51%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DAVE-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 26 · V/OI 2.24 · spread +0.1%
  greeks Δ-0.275 Γ0.0091 Θ-0.228 · IV 0.603 · mid 7.46
  overnight_score 4 · flow HEDGING · catalyst Technical Breakout (0.65) · RSI 43
  headline "Dave Inc (DAVE) Pulls Back 5.2% as Technical Indicators Signal Overbought Exhaustion Post-Earnings"
WHY
  underlying +9.1%/+12.2%/+17.7% (favorable peak -1.2%); position move -17.7%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-149% · IV residual ~107% [inferred].
  convexity Γ·S = 2.07. exit TIMEOUT → realized -51%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LITE-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 24 · V/OI 7.80 · spread +0.1%
  greeks Δ-0.476 Γ0.0018 Θ-1.785 · IV 0.971 · mid 103.80
  overnight_score 6 · flow HEDGING · catalyst Sector Rotation (0.85) · RSI 49
  headline "Applied Optoelectronics Slumps 10%, Lumentum Dives 9% as AI Optics Profit-Takers Strike"
WHY
  underlying +0.6%/-1.9%/+9.0% (favorable peak +4.5%); position move -9.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-36% · IV residual ~-9% [inferred].
  convexity Γ·S = 1.59. exit TIMEOUT → realized -51%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CEG-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ-0.071 Γ0.0032 Θ-0.068 · IV 0.471 · mid 1.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 35
  headline "Constellation Energy (CEG) Posts 64% Revenue Jump but Guidance Midpoint Trails Analyst Estimates"
WHY
  underlying -1.9%/-2.4%/+5.3% (favorable peak +4.2%); position move -5.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-55% · IV residual ~16% [inferred].
  convexity Γ·S = 0.85. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SNDK-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ-0.445 Γ0.0012 Θ-3.939 · IV 1.483 · mid 129.60
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.95) · RSI 64
  headline "SanDisk (SNDK) Braces for Q1 Earnings as Institutions Hedge Massive YTD Gains Amid 'Overvalued' Warnings"
WHY
  underlying +6.2%/+9.4%/+18.4% (favorable peak -4.6%); position move -18.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-63% · IV residual ~22% [inferred].
  convexity Γ·S = 1.21. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AAOI-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 3.50 · spread +0.1%
  greeks Δ-0.401 Γ0.0071 Θ-0.991 · IV 2.172 · mid 19.52
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 57
  headline "Applied Optoelectronics Shares Gap Down - Should You Sell? Analyst Consensus Points to 60% Downside Risk"
WHY
  underlying -5.8%/+4.8%/+12.7% (favorable peak +7.1%); position move -12.7%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-38% · IV residual ~3% [inferred].
  convexity Γ·S = 1.03. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RCL-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 3.89 · spread +0.0%
  greeks Δ-0.430 Γ0.0124 Θ-0.352 · IV 0.572 · mid 10.35
  overnight_score 4 · flow HEDGING · catalyst Regulatory (0.75) · RSI 39
  headline "Royal Caribbean Slides After Mexico Reviews Water Park Plan"
WHY
  underlying -2.1%/+0.5%/+3.1% (favorable peak +8.1%); position move -3.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-32% · IV residual ~-7% [inferred].
  convexity Γ·S = 3.13. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ALAB-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 0.50 · spread +0.1%
  greeks Δ-0.286 Γ0.0074 Θ-0.471 · IV 1.177 · mid 9.93
  overnight_score 5 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 61
  headline "Astera Labs (NASDAQ:ALAB) Shares Down 6.6% - Here's Why"
WHY
  underlying +7.4%/+6.2%/+10.6% (favorable peak +0.8%); position move -10.6%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-56% · IV residual ~20% [inferred].
  convexity Γ·S = 1.36. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SMCI-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.1%
  greeks Δ-0.497 Γ0.1115 Θ-0.067 · IV 0.803 · mid 1.67
  overnight_score 5 · flow MIXED · catalyst — (—) · RSI 51
WHY
  underlying +4.7%/+5.1%/+9.4% (favorable peak -2.0%); position move -9.4%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-72% · IV residual ~35% [inferred].
  convexity Γ·S = 2.90. exit TIMEOUT → realized -49%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SEZL-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ-0.410 Γ0.0212 Θ-0.113 · IV 1.031 · mid 7.03
  overnight_score 2 · flow DIRECTIONAL · catalyst Insider Activity (0.80) · RSI 43
  headline "Sezzle Director Resigns Over Governance Disagreements Amidst Software Sector Breakdown"
WHY
  underlying +10.9%/+15.3%/+21.0% (favorable peak -2.0%); position move -21.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-75% · IV residual ~31% [inferred].
  convexity Γ·S = 1.30. exit TIMEOUT → realized -49%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ACN-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ-0.356 Γ0.0259 Θ-0.252 · IV 0.442 · mid 3.96
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 44
  headline "Accenture Rallies 7% Off 52-Week Lows as Markets Weigh Guidance Cut Against AI Potential"
WHY
  underlying -0.8%/+1.1%/+1.1% (favorable peak +1.3%); position move -1.1%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-18% · IV residual ~-11% [inferred].
  convexity Γ·S = 4.97. exit TIMEOUT → realized -49%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TMO-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 0.43 · spread +0.1%
  greeks Δ-0.376 Γ0.0129 Θ-0.370 · IV 0.330 · mid 6.86
  overnight_score 1 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 36
  headline "RBC Capital Initiates TMO at Sector Perform as Market Weighs Soft Organic Growth Against Q1 Earnings Beat"
WHY
  underlying -2.2%/-1.4%/-0.1% (favorable peak +2.9%); position move +0.1%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~2% · IV residual ~-35% [inferred].
  convexity Γ·S = 5.79. exit TIMEOUT → realized -49%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DG-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ-0.499 Γ0.0579 Θ-0.159 · IV 0.371 · mid 2.87
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.35) · RSI 44
  headline "Dollar General Expands AI-Enabled In-Store Audio Network to 12,000 Locations"
WHY
  underlying +1.6%/+4.2%/+4.0% (favorable peak -0.2%); position move -4.0%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-85% · IV residual ~54% [inferred].
  convexity Γ·S = 7.04. exit TIMEOUT → realized -48%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE W-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 1.82 · spread +0.0%
  greeks Δ-0.448 Γ0.0482 Θ-0.118 · IV 0.645 · mid 3.55
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.60) · RSI 50
  headline "Wayfair outfits your home and patio for Memorial Day with up to 70% off furniture"
WHY
  underlying +7.2%/+9.1%/+8.5% (favorable peak -3.8%); position move -8.5%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-72% · IV residual ~34% [inferred].
  convexity Γ·S = 3.23. exit TIMEOUT → realized -48%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SMR-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 37 · V/OI 5.67 · spread +0.0%
  greeks Δ-0.255 Γ0.0762 Θ-0.018 · IV 1.119 · mid 0.81
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 51
  headline "Citigroup Cuts NuScale Power (SMR) Price Target to $9.00 as Fluor Continues Share Exit"
WHY
  underlying -4.2%/+5.4%/+2.7% (favorable peak +8.4%); position move -2.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-10% · IV residual ~-30% [inferred].
  convexity Γ·S = 0.90. exit TIMEOUT → realized -47%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUBS-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 22 · V/OI 0.29 · spread +0.0%
  greeks Δ-0.480 Γ0.0107 Θ-0.326 · IV 0.764 · mid 15.30
  overnight_score 7 · flow HEDGING · catalyst No Clear Catalyst (0.20) · RSI 43
  headline "HubSpot Retail Sentiment Surges as Stock Tests Multi-Year Lows Below $200"
WHY
  underlying +1.4%/+0.4%/+11.4% (favorable peak +0.9%); position move -11.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-71% · IV residual ~31% [inferred].
  convexity Γ·S = 2.13. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WDC-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.365 Γ0.0034 Θ-0.673 · IV 0.843 · mid 34.52
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 58
  headline "Former Samsung Executive Warns of Memory Supply Glut; Western Digital Shares Pull Back from AI Highs"
WHY
  underlying -0.6%/+0.2%/+6.1% (favorable peak +5.4%); position move -6.1%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-29% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.55. exit TIMEOUT → realized -45%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TER-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.530 Γ0.0093 Θ-0.610 · IV 0.661 · mid 19.00
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 46
  headline "Teradyne Issued Lowered Financial Outlook for Q2 2026, Forecasting Sequential Decline in Revenue and EPS"
WHY
  underlying -5.0%/-4.8%/+1.9% (favorable peak +8.4%); position move -1.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-18% · IV residual ~-17% [inferred].
  convexity Γ·S = 3.14. exit TIMEOUT → realized -45%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AVAV-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.277 Γ0.0171 Θ-0.237 · IV 0.643 · mid 3.65
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 35
  headline "AeroVironment Q3 revenue and EPS miss estimates as gross margins compress to 27%"
WHY
  underlying +2.2%/+1.4%/+3.7% (favorable peak +0.6%); position move -3.7%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-44% · IV residual ~19% [inferred].
  convexity Γ·S = 2.70. exit TIMEOUT → realized -45%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MRNA-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 10 · V/OI 11.00 · spread +0.1%
  greeks Δ-0.499 Γ0.0759 Θ-0.098 · IV 0.644 · mid 2.46
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 39
  headline "Moderna Stock Gives Back Early Gains as Analysts Label Hantavirus Rally 'Sentiment-Driven, Not Fundamental'"
WHY
  underlying -5.0%/+0.0%/-1.8% (favorable peak +5.2%); position move +1.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~17% · IV residual ~-50% [inferred].
  convexity Γ·S = 3.65. exit TIMEOUT → realized -44%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TPL-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ-0.421 Γ0.0067 Θ-0.393 · IV 0.494 · mid 21.48
  overnight_score 2 · flow HEDGING · catalyst Insider Activity (0.85) · RSI 41
  headline "Texas Pacific Land plunges after CEO of top shareholder Horizon Kinetics dies"
WHY
  underlying -0.9%/+2.0%/+2.7% (favorable peak +5.1%); position move -2.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-22% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.85. exit TIMEOUT → realized -44%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SYF-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ-0.344 Γ0.0489 Θ-0.045 · IV 0.353 · mid 1.95
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 73
  headline "Synchrony Financial (SYF) to Release Earnings April 21 Amid Proposed 10% Interest Cap Headwinds"
WHY
  underlying +0.6%/-0.5%/+3.7% (favorable peak +0.8%); position move -3.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-49% · IV residual ~13% [inferred].
  convexity Γ·S = 3.69. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ALAB-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 2.94 · spread +0.0%
  greeks Δ-0.331 Γ0.0084 Θ-0.741 · IV 1.302 · mid 11.05
  overnight_score 5 · flow HEDGING · catalyst Analyst Downgrade (0.75) · RSI 70
  headline "Astera Labs: The Story Just Re-Entered The Bubble Phase (Rating Downgrade)"
WHY
  underlying -6.8%/+0.1%/-1.0% (favorable peak +8.7%); position move +1.0%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~6% · IV residual ~-29% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized -43%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CIEN-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ-0.503 Γ0.0038 Θ-0.663 · IV 0.777 · mid 50.80
  overnight_score 5 · flow HEDGING · catalyst Technical Breakout (0.75) · RSI 61
  headline "Ciena (CIEN) Reaches New 1-Year High Near $500 Before Pulling Back on Heavy Insider Selling"
WHY
  underlying +1.8%/+6.0%/+8.6% (favorable peak +2.8%); position move -8.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-40% · IV residual ~1% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE U-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ-0.457 Γ0.0720 Θ-0.045 · IV 0.945 · mid 2.21
  overnight_score 4 · flow MIXED · catalyst — (—) · RSI 58
WHY
  underlying +2.4%/+10.8%/+13.7% (favorable peak -1.3%); position move -13.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-65% · IV residual ~28% [inferred].
  convexity Γ·S = 1.64. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LEN-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 1.83 · spread +0.1%
  greeks Δ-0.228 Γ0.0355 Θ-0.121 · IV 0.528 · mid 1.38
  overnight_score 1 · flow DIRECTIONAL · catalyst Macro (0.40) · RSI 53
  headline "Lennar Corporation Declares Quarterly Dividends as Analysts Maintain Bearish Outlook Amid Softening Housing…"
WHY
  underlying +0.2%/+0.4%/+0.1% (favorable peak +0.8%); position move -0.1%.
  decomp [first-order]: theta drag ~26% of premium / 3d · delta capture ~-1% · IV residual ~-16% [inferred].
  convexity Γ·S = 3.34. exit TIMEOUT → realized -43%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE PM-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.1%
  greeks Δ-0.202 Γ0.0240 Θ-0.191 · IV 0.486 · mid 1.39
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 38
  headline "Philip Morris stock price forecast: bearish momentum prevails as PM slides toward support at $151"
WHY
  underlying -0.6%/+0.4%/+0.2% (favorable peak +1.5%); position move -0.2%.
  decomp [first-order]: theta drag ~41% of premium / 3d · delta capture ~-5% · IV residual ~3% [inferred].
  convexity Γ·S = 3.77. exit TIMEOUT → realized -43%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FICO-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 33 · V/OI n/a · spread +0.1%
  greeks Δ-0.547 Γ0.0020 Θ-1.109 · IV 0.588 · mid 110.72
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 54
  headline "Steve Eisman Short Thesis and VantageScore Competition Overshadow FICO's Recent Earnings Beat"
WHY
  underlying +7.6%/+8.0%/+12.0% (favorable peak +0.4%); position move -12.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-65% · IV residual ~25% [inferred].
  convexity Γ·S = 2.24. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PATH-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.1%
  greeks Δ-0.423 Γ0.1785 Θ-0.011 · IV 0.674 · mid 0.79
  overnight_score 4 · flow HEDGING · catalyst Technical Breakout (0.65) · RSI 40
  headline "UiPath Rebounds From Record Lows as Analysts Weigh Agentic AI Growth Against Guidance Concerns"
WHY
  underlying -1.0%/+4.8%/+4.8% (favorable peak +2.1%); position move -4.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-26% · IV residual ~-12% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -42%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAR-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 43 · V/OI n/a · spread +0.0%
  greeks Δ-0.365 Γ0.0015 Θ-1.060 · IV 1.791 · mid 99.08
  overnight_score 5 · flow DIRECTIONAL · catalyst Short Squeeze (0.95) · RSI 89
  headline "Avis and Hertz Drop as Car Rental Short Squeeze Shows Signs of Stalling"
WHY
  underlying +13.4%/+24.8%/+53.8% (favorable peak +8.3%); position move -53.8%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-78% · IV residual ~40% [inferred].
  convexity Γ·S = 0.61. exit TIMEOUT → realized -42%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZETA-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ-0.379 Γ0.0997 Θ-0.017 · IV 0.779 · mid 1.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.90) · RSI 35
  headline "Zeta Global Holdings shares slide after Culper Research alleges consentless data usage and round-trip revenue."
WHY
  underlying +7.0%/+10.9%/+18.9% (favorable peak +0.4%); position move -18.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-91% · IV residual ~54% [inferred].
  convexity Γ·S = 1.46. exit TIMEOUT → realized -41%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KKR-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ-0.464 Γ0.0512 Θ-0.144 · IV 0.468 · mid 3.28
  overnight_score 5 · flow HEDGING · catalyst Technical Breakout (0.80) · RSI 60
  headline "KKR Jumps 6.4% as Investors Focus on Record $23B Flagship Fund Close and Improving Sentiment"
WHY
  underlying +2.3%/+5.8%/+4.0% (favorable peak -0.5%); position move -4.0%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-55% · IV residual ~27% [inferred].
  convexity Γ·S = 5.02. exit TIMEOUT → realized -41%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DPZ-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.053 Γ0.0022 Θ-0.074 · IV 0.429 · mid 1.98
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.35) · RSI 44
  headline "Domino's Pizza Hits Near 52-Week Lows Amid Analyst Target Cuts and Macro Headwinds"
WHY
  underlying +0.8%/+0.9%/+0.6% (favorable peak +1.0%); position move -0.6%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-6% · IV residual ~-24% [inferred].
  convexity Γ·S = 0.82. exit TIMEOUT → realized -41%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BTDR-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.322 Γ0.0826 Θ-0.025 · IV 1.146 · mid 1.27
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.80) · RSI 53
  headline "Bitdeer Technologies Group misses first quarter earnings and revenue estimates as losses widen"
WHY
  underlying -2.4%/+1.0%/+13.5% (favorable peak +7.2%); position move -13.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-45% · IV residual ~10% [inferred].
  convexity Γ·S = 1.09. exit TIMEOUT → realized -41%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TEL-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 22.43 · spread +0.1%
  greeks Δ-0.317 Γ0.0126 Θ-0.114 · IV 0.401 · mid 6.60
  overnight_score 3 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 40
  headline "TE Connectivity Stock Slides 9% as Q2 Guidance Underwhelms Investors"
WHY
  underlying +0.8%/+5.3%/+2.3% (favorable peak -0.1%); position move -2.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-23% · IV residual ~-13% [inferred].
  convexity Γ·S = 2.59. exit TIMEOUT → realized -41%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE COIN-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 2.39 · spread +0.1%
  greeks Δ-0.387 Γ0.0104 Θ-0.294 · IV 0.761 · mid 11.62
  overnight_score 6 · flow HEDGING · catalyst Regulatory (0.85) · RSI 52
  headline "New York Attorney General Files $2.2 Billion Lawsuit Against Coinbase Over Prediction Markets"
WHY
  underlying -6.4%/-3.3%/-1.5% (favorable peak +8.5%); position move +1.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~9% · IV residual ~-42% [inferred].
  convexity Γ·S = 2.01. exit TIMEOUT → realized -41%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE COF-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 6.83 · spread +0.1%
  greeks Δ-0.512 Γ0.0312 Θ-0.142 · IV 0.312 · mid 5.79
  overnight_score 1 · flow HEDGING · catalyst Macro (0.70) · RSI 45
  headline "US-Iran Conflict Rattles Markets as Financials Lead Broad Market Decline"
WHY
  underlying -0.1%/+1.8%/+1.4% (favorable peak +0.5%); position move -1.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-24% · IV residual ~-10% [inferred].
  convexity Γ·S = 5.92. exit TIMEOUT → realized -40%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE COF-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ-0.186 Γ0.0187 Θ-0.108 · IV 0.356 · mid 1.56
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.80) · RSI 38
  headline "Capital One (COF) Stock Falls as Credit Losses Overshadow Its Payments Powerhouse Ambitions"
WHY
  underlying -0.1%/-1.3%/+1.0% (favorable peak +1.4%); position move -1.0%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-22% · IV residual ~3% [inferred].
  convexity Γ·S = 3.43. exit TIMEOUT → realized -40%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RBLX-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 2.79 · spread +0.0%
  greeks Δ-0.487 Γ0.0778 Θ-0.106 · IV 0.695 · mid 2.12
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 44
  headline "Roblox Stock Slides to New Low as Safety Changes Weigh on Outlook"
WHY
  underlying -0.8%/+1.8%/+2.5% (favorable peak +1.3%); position move -2.5%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-26% · IV residual ~2% [inferred].
  convexity Γ·S = 3.58. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APP-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.468 Γ0.0048 Θ-1.718 · IV 1.152 · mid 34.35
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 51
  headline "SEC Confirms Active Investigation into AppLovin Data Practices as Insider Selling Accelerates"
WHY
  underlying -1.2%/-0.6%/+2.4% (favorable peak +4.2%); position move -2.4%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-15% · IV residual ~-9% [inferred].
  convexity Γ·S = 2.16. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NBIS-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 3.25 · spread +0.0%
  greeks Δ-0.403 Γ0.0087 Θ-0.228 · IV 1.028 · mid 16.41
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 49
  headline "Nebius Group Stock Slumps as Rally Runs Out Ahead of Q1 Earnings"
WHY
  underlying +4.2%/+2.0%/+14.0% (favorable peak +1.0%); position move -14.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-47% · IV residual ~12% [inferred].
  convexity Γ·S = 1.18. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FICO-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 1.44 · spread +0.1%
  greeks Δ-0.346 Γ0.0016 Θ-0.913 · IV 0.615 · mid 96.96
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 50
  headline "Study of nearly 20M mortgages says FICO Score 10T predicts defaults best"
WHY
  underlying +0.6%/+0.7%/+6.5% (favorable peak +1.9%); position move -6.5%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-24% · IV residual ~-11% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE COIN-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.435 Γ0.0138 Θ-0.316 · IV 0.691 · mid 11.72
  overnight_score 8 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 49
  headline "Bitcoin Falls Near $76,700 as ETF Outflows Hit $649M"
WHY
  underlying +2.1%/+1.0%/+2.2% (favorable peak +2.1%); position move -2.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-15% · IV residual ~-15% [inferred].
  convexity Γ·S = 2.61. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APP-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 23 · V/OI n/a · spread +0.1%
  greeks Δ-0.432 Γ0.0038 Θ-0.872 · IV 0.956 · mid 39.50
  overnight_score 6 · flow HEDGING · catalyst Technical Breakout (0.75) · RSI 53
  headline "AppLovin Shares Surge on Short-Seller Retraction while Institutional Put Volume Hits $108M"
WHY
  underlying +7.2%/+7.5%/+10.1% (favorable peak -0.0%); position move -10.1%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-48% · IV residual ~16% [inferred].
  convexity Γ·S = 1.64. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MOS-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 40 · V/OI n/a · spread +0.0%
  greeks Δ-0.414 Γ0.1233 Θ-0.015 · IV 0.422 · mid 1.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 45
  headline "Mosaic Withdraws 2026 Phosphate Guidance as Surging Sulfur Costs Drive Massive Q1 Earnings Miss"
WHY
  underlying +0.5%/+5.4%/+6.9% (favorable peak +1.4%); position move -6.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-56% · IV residual ~22% [inferred].
  convexity Γ·S = 2.77. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UPST-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ-0.339 Γ0.0373 Θ-0.039 · IV 0.993 · mid 2.88
  overnight_score 4 · flow DIRECTIONAL · catalyst Institutional Activity (0.75) · RSI 52
  headline "Baillie Gifford & Co. Makes New $33.19 Million Investment in Upstart Holdings, Inc. $UPST"
WHY
  underlying +5.2%/+18.9%/+17.9% (favorable peak -1.7%); position move -17.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-59% · IV residual ~26% [inferred].
  convexity Γ·S = 1.05. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NCLH-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 5.60 · spread +0.0%
  greeks Δ-0.364 Γ0.1115 Θ-0.016 · IV 0.596 · mid 1.04
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 38
  headline "JPMorgan Trims NCLH Price Target to $18 Citing Geopolitical Booking Headwinds and Fuel Volatility"
WHY
  underlying -0.1%/+2.2%/+5.7% (favorable peak +2.9%); position move -5.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-36% · IV residual ~3% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SITM-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 17.00 · spread +0.1%
  greeks Δ-0.260 Γ0.0025 Θ-1.269 · IV 1.175 · mid 25.75
  overnight_score 2 · flow HEDGING · catalyst Insider Activity (0.75) · RSI 64
  headline "SiTime Insiders Sell $11.28M in Shares as Stock Pulls Back from All-Time Highs"
WHY
  underlying +2.2%/+9.0%/+8.3% (favorable peak +0.8%); position move -8.3%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-43% · IV residual ~21% [inferred].
  convexity Γ·S = 1.28. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ADBE-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 2.95 · spread +0.1%
  greeks Δ-0.401 Γ0.0099 Θ-0.200 · IV 0.517 · mid 11.93
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 45
  headline "Adobe (ADBE) shares hit new 52-week lows as 'AI replacement' narrative reaches fever pitch"
WHY
  underlying -0.9%/+0.4%/+7.8% (favorable peak +1.6%); position move -7.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-63% · IV residual ~31% [inferred].
  convexity Γ·S = 2.38. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TYL-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 0.16 · spread +0.0%
  greeks Δ-0.392 Γ0.0104 Θ-0.304 · IV 0.485 · mid 11.00
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 41
  headline "Tyler Technologies Closes Upsized $1.4 Billion Convertible Senior Notes Offering"
WHY
  underlying -1.6%/-0.4%/+1.9% (favorable peak +2.5%); position move -1.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-21% · IV residual ~-8% [inferred].
  convexity Γ·S = 3.20. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NOW-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 20.00 · spread +0.0%
  greeks Δ-0.477 Γ0.0263 Θ-0.081 · IV 0.553 · mid 6.10
  overnight_score 6 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 40
  headline "ServiceNow stock sinks 18% as solid Q1 results fail to ease investor fears over geopolitical risks and marg…"
WHY
  underlying -0.7%/+2.6%/+3.5% (favorable peak +3.4%); position move -3.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-24% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.34. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KMI-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 2.88 · spread +0.1%
  greeks Δ-0.350 Γ0.2090 Θ-0.023 · IV 0.284 · mid 0.59
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 39
  headline "Kinder Morgan FY 2026 Guidance Misses Consensus Following Weather-Driven Q1 Beat; Wolfe Research Downgrades"
WHY
  underlying +0.0%/-2.5%/+0.2% (favorable peak +3.2%); position move -0.2%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-4% · IV residual ~-21% [inferred].
  convexity Γ·S = 6.63. exit TIMEOUT → realized -36%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BMNR-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 7.10 · spread +0.0%
  greeks Δ-0.468 Γ0.0761 Θ-0.028 · IV 0.811 · mid 2.22
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 45
  headline "BitMine Immersion Technologies Files to Register Resale of 501,545 Common Shares for Existing Holders"
WHY
  underlying +3.6%/+5.9%/+10.3% (favorable peak +0.7%); position move -10.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-45% · IV residual ~13% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized -36%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PSKY-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 0.61 · spread +0.1%
  greeks Δ-0.430 Γ0.3101 Θ-0.016 · IV 0.578 · mid 0.32
  overnight_score 3 · flow MIXED · catalyst — (—) · RSI 52
WHY
  underlying +1.8%/-0.1%/+3.4% (favorable peak +1.8%); position move -3.4%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-48% · IV residual ~28% [inferred].
  convexity Γ·S = 3.29. exit TIMEOUT → realized -36%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EL-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.1%
  greeks Δ-0.520 Γ0.0622 Θ-0.131 · IV 0.524 · mid 3.10
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 44
  headline "Barclays Slashes Estée Lauder Price Target to $72 Amid Fundamental Concerns and M&A Speculation"
WHY
  underlying +0.2%/-1.4%/-0.3% (favorable peak +2.9%); position move +0.3%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~4% · IV residual ~-26% [inferred].
  convexity Γ·S = 4.75. exit TIMEOUT → realized -35%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CIFR-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 38 · V/OI 9.00 · spread +0.0%
  greeks Δ-0.480 Γ0.0610 Θ-0.033 · IV 1.061 · mid 2.54
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 49
  headline "CIFR Stock Wobbles As Earnings Miss And Insider Sale Hit Radar"
WHY
  underlying -1.7%/+1.9%/+12.6% (favorable peak +7.8%); position move -12.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-45% · IV residual ~14% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized -35%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CRCL-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 6.00 · spread +0.0%
  greeks Δ-0.416 Γ0.0162 Θ-0.153 · IV 0.899 · mid 8.90
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 45
  headline "Circle Internet Group (CRCL) slips as investors weigh Drift-hack lawsuit overhang ahead of May earnings"
WHY
  underlying +1.3%/-3.7%/+5.7% (favorable peak +4.7%); position move -5.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-25% · IV residual ~-5% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized -35%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CLF-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.1%
  greeks Δ-0.567 Γ0.2626 Θ-0.021 · IV 0.856 · mid 0.75
  overnight_score 7 · flow DIRECTIONAL · catalyst Macro (0.72) · RSI 49
  headline "Iron Ore Futures Slide as Global Steel Demand Forecasts Are Revised Lower"
WHY
  underlying +3.3%/+4.5%/+6.9% (favorable peak +1.3%); position move -6.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-47% · IV residual ~21% [inferred].
  convexity Γ·S = 2.37. exit TIMEOUT → realized -35%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MCO-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ-0.455 Γ0.0075 Θ-0.297 · IV 0.406 · mid 19.23
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 41
  headline "Morgan Stanley Lowers Price Target on Moody's (MCO) to $489 Amid Valuation Concerns"
WHY
  underlying +2.9%/+2.5%/+4.5% (favorable peak +0.5%); position move -4.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-46% · IV residual ~16% [inferred].
  convexity Γ·S = 3.22. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VST-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 33 · V/OI 1.18 · spread +0.0%
  greeks Δ-0.758 Γ0.0170 Θ-0.083 · IV 0.453 · mid 17.23
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 35
  headline "Vistra Energy Corp stock hits 52-week low at 138.38 USD amid AI-power sector sell-off"
WHY
  underlying -2.1%/-3.6%/+3.1% (favorable peak +5.0%); position move -3.1%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-19% · IV residual ~-14% [inferred].
  convexity Γ·S = 2.37. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AXON-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ-0.307 Γ0.0039 Θ-0.511 · IV 0.864 · mid 20.51
  overnight_score 4 · flow HEDGING · catalyst Analyst Upgrade (0.75) · RSI 30
  headline "Citizens reiterates Axon stock rating on strong growth outlook with $825 price target"
WHY
  underlying +5.9%/+11.8%/+9.3% (favorable peak -2.8%); position move -9.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-50% · IV residual ~23% [inferred].
  convexity Γ·S = 1.40. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KTOS-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.494 Γ0.0424 Θ-0.137 · IV 0.699 · mid 4.25
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 41
  headline "Kratos wins $446.8M Space Force ground contract for missile warning system"
WHY
  underlying +4.6%/+4.7%/+6.1% (favorable peak +1.0%); position move -6.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-50% · IV residual ~26% [inferred].
  convexity Γ·S = 2.98. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DECK-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 20.00 · spread +0.0%
  greeks Δ-0.392 Γ0.0557 Θ-0.148 · IV 0.416 · mid 1.15
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.50) · RSI 53
  headline "Analysts' Focus On Sales Growth Despite Softer Earnings Might Change The Case For Investing In Deckers Outd…"
WHY
  underlying +0.0%/+0.8%/-0.9% (favorable peak +2.0%); position move +0.9%.
  decomp [first-order]: theta drag ~39% of premium / 3d · delta capture ~31% · IV residual ~-26% [inferred].
  convexity Γ·S = 6.00. exit TIMEOUT → realized -33%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE UPST-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 28 · V/OI 2.00 · spread +0.1%
  greeks Δ-0.470 Γ0.0710 Θ-0.039 · IV 0.708 · mid 2.32
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.40) · RSI 47
  headline "Upstart Faces June 8 Class Action Deadline as AI Model Performance Under Scrutiny"
WHY
  underlying +0.0%/-1.0%/+6.2% (favorable peak +3.2%); position move -6.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-36% · IV residual ~8% [inferred].
  convexity Γ·S = 2.05. exit TIMEOUT → realized -33%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SNOW-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 5.61 · spread +0.0%
  greeks Δ-0.253 Γ0.0100 Θ-0.165 · IV 0.786 · mid 5.44
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 54
  headline "Snowflake (SNOW) Surges 10% on AI Tailwinds Before Pulling Back Amid Growth Deceleration Concerns"
WHY
  underlying -1.4%/+8.5%/+7.6% (favorable peak +3.9%); position move -7.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-50% · IV residual ~26% [inferred].
  convexity Γ·S = 1.41. exit TIMEOUT → realized -33%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LEN-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 2.50 · spread +0.1%
  greeks Δ-0.288 Γ0.0351 Θ-0.060 · IV 0.401 · mid 1.77
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 40
  headline "Fannie Mae Reverses Housing Outlook: Mortgage Rates Forecasted to Remain Above 6% Through 2026"
WHY
  underlying -4.6%/-2.5%/+2.4% (favorable peak +4.7%); position move -2.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-34% · IV residual ~12% [inferred].
  convexity Γ·S = 3.10. exit TIMEOUT → realized -32%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RH-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 1.00 · spread +0.0%
  greeks Δ-0.465 Γ0.0184 Θ-0.184 · IV 0.702 · mid 8.00
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 51
  headline "Most and least shorted stocks over $2B market cap: RH (RH) leads with 28.97% short interest"
WHY
  underlying +6.7%/+8.2%/+8.4% (favorable peak -3.2%); position move -8.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-61% · IV residual ~36% [inferred].
  convexity Γ·S = 2.27. exit TIMEOUT → realized -31%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE OMC-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ-0.400 Γ0.0474 Θ-0.048 · IV 0.365 · mid 2.42
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.30) · RSI 48
  headline "Omnicom Schedules First Quarter 2026 Earnings Release and Conference Call"
WHY
  underlying +0.6%/+2.0%/+3.6% (favorable peak +0.2%); position move -3.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-46% · IV residual ~20% [inferred].
  convexity Γ·S = 3.60. exit TIMEOUT → realized -31%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AXON-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 15 · V/OI 2.60 · spread +0.1%
  greeks Δ-0.550 Γ0.0074 Θ-0.657 · IV 0.682 · mid 31.75
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 41
  headline "Axon stock dips as investor pitches AI upside at Sohn conference"
WHY
  underlying +3.0%/+4.0%/+6.0% (favorable peak +2.9%); position move -6.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-39% · IV residual ~14% [inferred].
  convexity Γ·S = 2.80. exit TIMEOUT → realized -31%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LITE-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 18.00 · spread +0.0%
  greeks Δ-0.406 Γ0.0029 Θ-2.922 · IV 0.963 · mid 53.78
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.70) · RSI 49
  headline "Thinking of Riding on Lumentum Stock? Don't -- Until You Consider This Red Flag"
WHY
  underlying -4.6%/-5.2%/+0.3% (favorable peak +10.6%); position move -0.3%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-2% · IV residual ~-12% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized -31%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE HUT-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 3.50 · spread +0.0%
  greeks Δ-0.356 Γ0.0179 Θ-0.156 · IV 1.067 · mid 4.73
  overnight_score 4 · flow MIXED · catalyst — (—) · RSI 65
WHY
  underlying -4.8%/-6.2%/+0.1% (favorable peak +8.5%); position move -0.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-1% · IV residual ~-20% [inferred].
  convexity Γ·S = 1.35. exit TIMEOUT → realized -31%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DVN-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 6.00 · spread +0.0%
  greeks Δ-0.337 Γ0.0643 Θ-0.029 · IV 0.403 · mid 1.75
  overnight_score 3 · flow HEDGING · catalyst M&A (0.90) · RSI 41
  headline "Devon Energy Lifts Dividend 33%, OKs $8B Buyback Following Coterra Merger Completion"
WHY
  underlying +0.7%/+3.1%/+3.2% (favorable peak +0.3%); position move -3.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-28% · IV residual ~3% [inferred].
  convexity Γ·S = 2.91. exit TIMEOUT → realized -31%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZS-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ-0.437 Γ0.0095 Θ-0.193 · IV 0.798 · mid 15.36
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 61
  headline "Cisco's robust earnings and upgraded forecast fuel optimism in software sector, lifting Zscaler"
WHY
  underlying +4.8%/+13.7%/+14.0% (favorable peak +1.0%); position move -14.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-61% · IV residual ~35% [inferred].
  convexity Γ·S = 1.46. exit TIMEOUT → realized -31%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WDAY-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 2.00 · spread +0.0%
  greeks Δ-0.444 Γ0.0215 Θ-0.160 · IV 0.606 · mid 6.75
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.80) · RSI 49
  headline "The Goldman Sachs Group Issues Pessimistic Forecast for Workday (NASDAQ:WDAY) Stock Price"
WHY
  underlying +0.4%/+4.8%/+17.9% (favorable peak +1.9%); position move -17.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-146% · IV residual ~123% [inferred].
  convexity Γ·S = 2.66. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MNDY-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 0.03 · spread +0.1%
  greeks Δ-0.400 Γ0.0250 Θ-0.130 · IV 0.931 · mid 4.95
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 51
  headline "Why Is Monday.com Stock Crashing, and is it a Buy Right Now?"
WHY
  underlying -7.4%/-2.8%/-2.5% (favorable peak +10.9%); position move +2.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~14% · IV residual ~-36% [inferred].
  convexity Γ·S = 1.75. exit TIMEOUT → realized -30%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TDG-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 0.36 · spread +0.0%
  greeks Δ-0.457 Γ0.0039 Θ-0.645 · IV 0.282 · mid 37.11
  overnight_score 3 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 46
  headline "TransDigm Insiders Sell Over $17M in Stock as Analysts Trim Price Targets Post-Earnings"
WHY
  underlying -2.5%/+0.3%/+0.0% (favorable peak +3.0%); position move -0.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-0% · IV residual ~-25% [inferred].
  convexity Γ·S = 4.57. exit TIMEOUT → realized -30%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TMO-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 0.33 · spread +0.0%
  greeks Δ-0.331 Γ0.0097 Θ-0.274 · IV 0.318 · mid 6.56
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.65) · RSI 38
  headline "Thermo Fisher Scientific Hits 4-Week Low as Organic Growth Concerns Overshadow Earnings Beat"
WHY
  underlying +0.9%/+2.2%/+2.6% (favorable peak +0.6%); position move -2.6%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-60% · IV residual ~42% [inferred].
  convexity Γ·S = 4.49. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SNOW-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 1.45 · spread +0.1%
  greeks Δ-0.281 Γ0.0150 Θ-0.226 · IV 0.736 · mid 4.41
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.65) · RSI 44
  headline "SNOW DEADLINE ALERT: Law Firms Remind Investors of April 27 Securities Class Action Deadline as Insider Sel…"
WHY
  underlying -0.9%/-4.3%/-1.1% (favorable peak +6.7%); position move +1.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~10% · IV residual ~-25% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized -30%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE FICO-2026-04-24-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 0.50 · spread +0.0%
  greeks Δ-0.386 Γ0.0022 Θ-1.575 · IV 0.728 · mid 53.90
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 42
  headline "Mizuho Initiates on Fair Isaac (FICO) With an Outperform; Says the Market Has Overreacted"
WHY
  underlying +0.9%/+0.6%/+3.9% (favorable peak +2.0%); position move -3.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-28% · IV residual ~7% [inferred].
  convexity Γ·S = 2.22. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TEL-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 0.06 · spread +0.1%
  greeks Δ-0.378 Γ0.0223 Θ-0.192 · IV 0.393 · mid 5.10
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 38
  headline "TE Connectivity Stock Down 2.3% as Post-Earnings Sell-Off Accelerates Despite Raised Outlook"
WHY
  underlying +0.5%/+3.6%/+1.5% (favorable peak +1.2%); position move -1.5%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-23% · IV residual ~5% [inferred].
  convexity Γ·S = 4.56. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WYNN-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 20.00 · spread +0.0%
  greeks Δ-0.234 Γ0.0430 Θ-0.113 · IV 0.450 · mid 0.92
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 35
  headline "Wynn Resorts Shares Fade Despite Q1 Earnings Beat as Macau Market Moderation Concerns Persist"
WHY
  underlying -1.1%/-1.9%/-1.9% (favorable peak +3.2%); position move +1.9%.
  decomp [first-order]: theta drag ~37% of premium / 3d · delta capture ~47% · IV residual ~-39% [inferred].
  convexity Γ·S = 4.19. exit TIMEOUT → realized -29%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE EL-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.329 Γ0.0330 Θ-0.210 · IV 0.894 · mid 2.34
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 44
  headline "Estee Lauder seeking funding for potential Puig takeover, Expansion reports"
WHY
  underlying +1.1%/+0.7%/+2.6% (favorable peak +1.6%); position move -2.6%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~-28% · IV residual ~25% [inferred].
  convexity Γ·S = 2.50. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ACN-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ-0.371 Γ0.0184 Θ-0.166 · IV 0.425 · mid 5.31
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 42
  headline "HSBC Lowers Accenture Price Target to $210 Citing Slowing Bookings Momentum"
WHY
  underlying +1.9%/+1.9%/+3.8% (favorable peak -0.5%); position move -3.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-51% · IV residual ~31% [inferred].
  convexity Γ·S = 3.51. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE QBTS-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 37 · V/OI 11.00 · spread +0.0%
  greeks Δ-0.189 Γ0.0489 Θ-0.020 · IV 0.969 · mid 0.75
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 50
  headline "D-Wave Quantum (QBTS) Shares Down 3.8% as Resale Overhang and Insider Selling Pressure Continue"
WHY
  underlying +0.9%/+12.0%/+13.1% (favorable peak +5.5%); position move -13.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-60% · IV residual ~39% [inferred].
  convexity Γ·S = 0.89. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FIGR-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 0.46 · spread +0.1%
  greeks Δ-0.323 Γ0.0460 Θ-0.080 · IV 1.106 · mid 1.84
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 46
  headline "Figure Technology Solutions Announces Date for First Quarter 2026 Results"
WHY
  underlying +4.4%/+1.1%/+6.7% (favorable peak +4.8%); position move -6.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-38% · IV residual ~23% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AVAV-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 4.67 · spread +0.0%
  greeks Δ-0.335 Γ0.0161 Θ-0.285 · IV 0.695 · mid 6.95
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 38
  headline "Pentagon Drone Surge: AeroVironment (AVAV), Palantir (PLTR), and Kratos (KTOS) Lead Defense Stock Rally"
WHY
  underlying -4.4%/-2.3%/-3.0% (favorable peak +5.0%); position move +3.0%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~24% · IV residual ~-40% [inferred].
  convexity Γ·S = 2.66. exit TIMEOUT → realized -28%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PSKY-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 26 · V/OI 110.33 · spread +0.1%
  greeks Δ-0.488 Γ0.2977 Θ-0.010 · IV 0.482 · mid 0.56
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 49
  headline "Warner Bros. falls after report Paramount hiring lawyer for possible court battle"
WHY
  underlying -0.9%/+1.5%/+3.3% (favorable peak +1.6%); position move -3.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-31% · IV residual ~8% [inferred].
  convexity Γ·S = 3.11. exit TIMEOUT → realized -28%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SMCI-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 4.44 · spread +0.1%
  greeks Δ-0.455 Γ0.0572 Θ-0.045 · IV 0.893 · mid 2.17
  overnight_score 7 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 51
  headline "Super Micro Computer Faces DOJ Indictment and Oracle Order Cancellation Ahead of Q3 Earnings"
WHY
  underlying -3.4%/+0.6%/-0.6% (favorable peak +6.6%); position move +0.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~3% · IV residual ~-25% [inferred].
  convexity Γ·S = 1.56. exit TIMEOUT → realized -28%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE COIN-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI 3.86 · spread +0.0%
  greeks Δ-0.497 Γ0.0103 Θ-0.206 · IV 0.687 · mid 14.48
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 42
  headline "Institutional sell-off intensifies, Coinbase premium drops to monthly low"
WHY
  underlying -3.5%/+1.2%/+5.0% (favorable peak +6.0%); position move -5.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-31% · IV residual ~7% [inferred].
  convexity Γ·S = 1.85. exit TIMEOUT → realized -28%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AAOI-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 43 · V/OI n/a · spread +0.0%
  greeks Δ-0.257 Γ0.0046 Θ-0.262 · IV 1.459 · mid 14.81
  overnight_score 5 · flow HEDGING · catalyst Technical Breakout (0.30) · RSI 66
  headline "Applied Optoelectronics Shares Under Pressure as Investors Take Profits Following AI-Driven Surge"
WHY
  underlying +10.4%/+11.8%/+14.7% (favorable peak +4.3%); position move -14.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-36% · IV residual ~14% [inferred].
  convexity Γ·S = 0.66. exit TIMEOUT → realized -28%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BBY-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 54.29 · spread +0.1%
  greeks Δ-0.443 Γ0.0548 Θ-0.065 · IV 0.522 · mid 2.65
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 33
  headline "Best Buy shares hit a new 52-week low after Citigroup cut its price target from $69 to $60"
WHY
  underlying +2.1%/+1.4%/+4.3% (favorable peak -0.5%); position move -4.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-39% · IV residual ~20% [inferred].
  convexity Γ·S = 3.04. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DAL-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ-0.173 Γ0.0247 Θ-0.035 · IV 0.483 · mid 1.04
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 48
  headline "Airline stocks face pressure as temporary U.S.-Iran ceasefire falters, reigniting fuel cost concerns"
WHY
  underlying -1.4%/+1.1%/+2.6% (favorable peak +2.1%); position move -2.6%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-29% · IV residual ~13% [inferred].
  convexity Γ·S = 1.66. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE IBM-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ-0.450 Γ0.0115 Θ-0.163 · IV 0.452 · mid 13.18
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 35
  headline "IBM Downgraded to Underweight at Barclays on Consulting Growth Concerns; Shares Drop 2.5%"
WHY
  underlying +3.1%/+4.1%/+6.1% (favorable peak -0.4%); position move -6.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-48% · IV residual ~25% [inferred].
  convexity Γ·S = 2.65. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TYL-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 5.00 · spread +0.0%
  greeks Δ-0.124 Γ0.0043 Θ-0.171 · IV 0.545 · mid 3.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 45
  headline "Tyler Technologies Shares Under Pressure Despite $1.44B Debt Raise and Buyback Program"
WHY
  underlying -2.7%/-1.3%/-3.1% (favorable peak +3.9%); position move +3.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~36% · IV residual ~-47% [inferred].
  convexity Γ·S = 1.36. exit TIMEOUT → realized -26%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CCJ-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 50.10 · spread +0.0%
  greeks Δ-0.385 Γ0.0218 Θ-0.211 · IV 0.740 · mid 5.07
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 47
  headline "Cameco (CCJ) Trading Down as Investors Weigh Nuclear Pullback Ahead of Earnings"
WHY
  underlying +7.7%/+5.5%/+3.5% (favorable peak -1.3%); position move -3.5%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-30% · IV residual ~17% [inferred].
  convexity Γ·S = 2.49. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ONON-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ-0.143 Γ0.0441 Θ-0.021 · IV 0.554 · mid 0.42
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 39
  headline "HSBC Slashes ONON Price Target to $47 as Legal Probes into CEO Departure Intensify"
WHY
  underlying +1.9%/+6.1%/+5.6% (favorable peak +1.2%); position move -5.6%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-64% · IV residual ~53% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CHTR-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.360 Γ0.0268 Θ-0.190 · IV 0.502 · mid 3.77
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 33
  headline "Charter shares slip as broadband subscriber losses and Q1 earnings miss fuel market skepticism"
WHY
  underlying -0.8%/+1.4%/+1.5% (favorable peak +1.7%); position move -1.5%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-20% · IV residual ~10% [inferred].
  convexity Γ·S = 3.89. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LULU-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.331 Γ0.0182 Θ-0.118 · IV 0.580 · mid 5.47
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.85) · RSI 26
  headline "Lululemon Settlement Talks With Founder Chip Wilson Collapse, Setting Stage for Contentious Proxy Battle"
WHY
  underlying -0.9%/+4.1%/+5.4% (favorable peak +3.0%); position move -5.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-39% · IV residual ~20% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDB-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 8.00 · spread +0.0%
  greeks Δ-0.462 Γ0.0065 Θ-0.410 · IV 0.829 · mid 30.33
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 67
  headline "MongoDB shares jump as company unveils new enterprise AI capabilities at MongoDB.local London"
WHY
  underlying +10.6%/+12.9%/+11.1% (favorable peak -6.3%); position move -11.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-45% · IV residual ~23% [inferred].
  convexity Γ·S = 1.73. exit TIMEOUT → realized -25%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APP-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 3.00 · spread +0.1%
  greeks Δ-0.421 Γ0.0036 Θ-0.737 · IV 0.875 · mid 40.38
  overnight_score 5 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 51
  headline "AppLovin (APP) Faces Split Sentiment: Bullish Analyst Deep-Dives vs. Near-Term Earnings Uncertainty"
WHY
  underlying +3.1%/+6.4%/+7.1% (favorable peak -0.9%); position move -7.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-33% · IV residual ~13% [inferred].
  convexity Γ·S = 1.61. exit TIMEOUT → realized -25%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FIX-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 5.00 · spread +0.0%
  greeks Δ-0.191 Γ0.0008 Θ-1.501 · IV 0.633 · mid 40.40
  overnight_score 2 · flow HEDGING · catalyst Macro (0.85) · RSI 50
  headline "Comfort Systems USA falls as higher-rate fears and insider selling weigh on sentiment"
WHY
  underlying -1.6%/-1.0%/-1.0% (favorable peak +5.3%); position move +1.0%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~9% · IV residual ~-23% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized -25%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TTMI-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.454 Γ0.0130 Θ-0.199 · IV 0.899 · mid 12.68
  overnight_score 4 · flow HEDGING · catalyst Technical Breakout (0.70) · RSI 65
  headline "TTM Technologies Stock Stumbles After Rally as AI Infrastructure Enthusiasm Cools"
WHY
  underlying -3.4%/-3.2%/+4.6% (favorable peak +7.1%); position move -4.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-20% · IV residual ~0% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TPG-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 17 · V/OI 0.70 · spread +0.0%
  greeks Δ-0.085 Γ0.0240 Θ-0.028 · IV 0.688 · mid 0.30
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 52
  headline "Goldman Sachs and BofA Slash TPG Price Targets Citing Challenging 2026 Outlook for Asset Managers"
WHY
  underlying -1.0%/-2.0%/+1.6% (favorable peak +3.2%); position move -1.6%.
  decomp [first-order]: theta drag ~28% of premium / 3d · delta capture ~-20% · IV residual ~24% [inferred].
  convexity Γ·S = 1.03. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ENPH-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 3.80 · spread +0.0%
  greeks Δ-0.429 Γ0.0553 Θ-0.131 · IV 1.228 · mid 2.72
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 42
  headline "ENPH CLASS ACTION DEADLINE TONIGHT: Faruqi & Faruqi, LLP Reminds Enphase Energy Investors of Securities Cla…"
WHY
  underlying -0.8%/+4.4%/+6.7% (favorable peak +1.2%); position move -6.7%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-36% · IV residual ~27% [inferred].
  convexity Γ·S = 1.87. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE OWL-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 5.83 · spread +0.1%
  greeks Δ-0.465 Γ0.1981 Θ-0.013 · IV 0.657 · mid 0.78
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 59
  headline "Blue Owl Capital stock surges on SpaceX gains and Q1 earnings beat"
WHY
  underlying +1.4%/+7.7%/+5.6% (favorable peak -0.5%); position move -5.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-33% · IV residual ~15% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UBER-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 4.88 · spread +0.0%
  greeks Δ-0.141 Γ0.0272 Θ-0.030 · IV 0.388 · mid 0.52
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.65) · RSI 49
  headline "Uber Q1 Revenue Misses Estimates Despite Strong Bookings Growth"
WHY
  underlying -0.0%/+0.5%/+0.5% (favorable peak +2.4%); position move -0.5%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-10% · IV residual ~4% [inferred].
  convexity Γ·S = 2.03. exit TIMEOUT → realized -24%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AZO-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.350 Γ0.0009 Θ-2.269 · IV 0.407 · mid 88.70
  overnight_score 2 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 47
  headline "AutoZone Shares Drop as DIY Traffic Declines and Institutional Investors Trim Holdings"
WHY
  underlying +2.4%/+2.3%/+3.1% (favorable peak +0.9%); position move -3.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-42% · IV residual ~26% [inferred].
  convexity Γ·S = 2.93. exit TIMEOUT → realized -23%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CVX-2026-04-24-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ-0.480 Γ0.0210 Θ-0.094 · IV 0.310 · mid 8.08
  overnight_score 3 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 41
  headline "Exxon Stock and Chevron Stock Are Up 20%+ YTD - Why the Long Oil Trade Is Stalling Out"
WHY
  underlying -0.2%/+1.7%/+3.8% (favorable peak +0.8%); position move -3.8%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-42% · IV residual ~22% [inferred].
  convexity Γ·S = 3.89. exit TIMEOUT → realized -23%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UBER-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 4.13 · spread +0.1%
  greeks Δ-0.449 Γ0.0488 Θ-0.102 · IV 0.525 · mid 3.04
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 54
  headline "Uber Acquires 11.5% Stake in Lucid, Plans 35,000-Vehicle Robotaxi Order as Part of $10B AV Pivot"
WHY
  underlying -1.2%/-1.2%/+0.9% (favorable peak +2.7%); position move -0.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-10% · IV residual ~-2% [inferred].
  convexity Γ·S = 3.69. exit TIMEOUT → realized -23%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE NET-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 51.00 · spread +0.1%
  greeks Δ-0.418 Γ0.0090 Θ-0.391 · IV 0.875 · mid 16.45
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.40) · RSI 53
  headline "Cloudflare shares underperform as macro uncertainty and AI-native security threats weigh on high-valuation …"
WHY
  underlying +1.0%/+3.6%/+1.7% (favorable peak +1.7%); position move -1.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-9% · IV residual ~-6% [inferred].
  convexity Γ·S = 1.84. exit TIMEOUT → realized -22%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MA-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ-0.049 Γ0.0022 Θ-0.062 · IV 0.294 · mid 1.02
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 45
  headline "UK FCA launches investigation into Mastercard and Visa over PayPal digital wallet funding conduct"
WHY
  underlying -1.0%/+0.8%/-0.3% (favorable peak +1.5%); position move +0.3%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~8% · IV residual ~-11% [inferred].
  convexity Γ·S = 1.08. exit TIMEOUT → realized -22%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE RBLX-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.1%
  greeks Δ-0.363 Γ0.0235 Θ-0.076 · IV 0.850 · mid 4.69
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 48
  headline "Roblox stock rises as premium membership rollout planned for April 2026 drives optimism"
WHY
  underlying +1.1%/+3.7%/+4.8% (favorable peak +1.7%); position move -4.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-22% · IV residual ~5% [inferred].
  convexity Γ·S = 1.36. exit TIMEOUT → realized -21%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDT-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 1.00 · spread +0.1%
  greeks Δ-0.430 Γ0.0740 Θ-0.044 · IV 0.253 · mid 0.75
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.80) · RSI 29
  headline "Medtronic (MDT) Sees Significant Dip as Analysts Slash Price Targets Amid One-Time Charges and Sector Weakness"
WHY
  underlying +1.5%/+2.2%/+1.6% (favorable peak -0.8%); position move -1.6%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-76% · IV residual ~72% [inferred].
  convexity Γ·S = 6.07. exit TIMEOUT → realized -21%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DUOL-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ-0.472 Γ0.0182 Θ-0.184 · IV 0.950 · mid 8.60
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 39
  headline "Duolingo stock hits 52-week low at $91.59 as analysts cite slowing user growth and AI execution risks."
WHY
  underlying +8.0%/+13.1%/+9.9% (favorable peak -1.2%); position move -9.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-50% · IV residual ~36% [inferred].
  convexity Γ·S = 1.66. exit TIMEOUT → realized -21%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HD-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 14.00 · spread +0.0%
  greeks Δ-0.258 Γ0.0098 Θ-0.153 · IV 0.333 · mid 5.75
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 40
  headline "Home Depot stock slides as MACD flashes strong sell signal; internal fraud scheme details emerge"
WHY
  underlying -3.5%/-2.6%/-0.3% (favorable peak +4.2%); position move +0.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~4% · IV residual ~-16% [inferred].
  convexity Γ·S = 3.17. exit TIMEOUT → realized -20%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AZO-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 33 · V/OI 0.52 · spread +0.1%
  greeks Δ-0.190 Γ0.0008 Θ-1.393 · IV 0.353 · mid 45.95
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.30) · RSI 36
  headline "AutoZone to Release Third Quarter Fiscal 2026 Earnings May 26, 2026"
WHY
  underlying +1.3%/+0.8%/+3.0% (favorable peak +1.2%); position move -3.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-41% · IV residual ~29% [inferred].
  convexity Γ·S = 2.57. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SCHW-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 9.65 · spread +0.0%
  greeks Δ-0.454 Γ0.0560 Θ-0.048 · IV 0.287 · mid 2.66
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 38
  headline "Premier Fund Managers Slashing SCHW Stake by 56% Triggers Technical Breakdown Below 200-Day SMA"
WHY
  underlying -1.0%/-1.9%/+0.8% (favorable peak +2.1%); position move -0.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-12% · IV residual ~-3% [inferred].
  convexity Γ·S = 5.01. exit TIMEOUT → realized -20%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE NET-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 45 · V/OI 6.67 · spread +0.0%
  greeks Δ-0.465 Γ0.0098 Θ-0.175 · IV 0.609 · mid 14.20
  overnight_score 6 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 43
  headline "Cloudflare Shares Stabilize Near $196 as Analysts Weigh Execution Risk of 1,100-Person Layoff and AI Pivot"
WHY
  underlying -3.5%/-0.5%/+3.3% (favorable peak +4.0%); position move -3.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-21% · IV residual ~4% [inferred].
  convexity Γ·S = 1.89. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDT-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 11.00 · spread +0.1%
  greeks Δ-0.337 Γ0.0599 Θ-0.030 · IV 0.224 · mid 1.40
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 36
  headline "Truist Financial Issues Pessimistic Forecast for Medtronic (NYSE:MDT) Stock Price"
WHY
  underlying -3.5%/-2.1%/-1.4% (favorable peak +3.6%); position move +1.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~29% · IV residual ~-43% [inferred].
  convexity Γ·S = 5.09. exit TIMEOUT → realized -20%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MMYT-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ-0.579 Γ0.0422 Θ-0.060 · IV 0.706 · mid 8.71
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.65) · RSI 57
  headline "MakeMyTrip (MMYT) Receives IBD Relative Strength Rating Upgrade to 91 Amid Volatile Recovery"
WHY
  underlying +2.0%/+8.8%/+5.8% (favorable peak +0.1%); position move -5.8%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-18% · IV residual ~0% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UPST-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ-0.319 Γ0.0664 Θ-0.032 · IV 0.680 · mid 1.31
  overnight_score 8 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 44
  headline "INVESTOR ALERT: Berger Montague Advises Investors to Inquire About a Securities Fraud Class Action Against …"
WHY
  underlying +0.5%/+3.2%/+3.3% (favorable peak +4.2%); position move -3.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-22% · IV residual ~10% [inferred].
  convexity Γ·S = 1.85. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VG-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 4.86 · spread +0.1%
  greeks Δ-0.374 Γ0.1201 Θ-0.020 · IV 0.923 · mid 0.97
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 41
  headline "Venture Global (VG) Analyst Estimates Revised 16% Lower Ahead of May 12 Earnings Report"
WHY
  underlying -2.6%/-4.6%/-3.2% (favorable peak +7.0%); position move +3.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~15% · IV residual ~-28% [inferred].
  convexity Γ·S = 1.44. exit TIMEOUT → realized -20%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AG-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 40 · V/OI n/a · spread +0.0%
  greeks Δ-0.450 Γ0.0839 Θ-0.023 · IV 0.745 · mid 1.89
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 43
  headline "Silver Surges 3.1% to $77.81 on Peace Deal Hopes While First Majestic Silver Lags"
WHY
  underlying +4.3%/+1.1%/+5.8% (favorable peak +1.3%); position move -5.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-27% · IV residual ~11% [inferred].
  convexity Γ·S = 1.63. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BSX-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.634 Γ0.0600 Θ-0.030 · IV 0.361 · mid 4.70
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 30
  headline "Boston Scientific Guidance Cut Triggers 52-Week Low as Analysts Trim Estimates"
WHY
  underlying +0.0%/+1.1%/-3.7% (favorable peak +4.2%); position move +3.7%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~28% · IV residual ~-45% [inferred].
  convexity Γ·S = 3.36. exit TIMEOUT → realized -20%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TPG-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.256 Γ0.0457 Θ-0.040 · IV 0.573 · mid 1.16
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.65) · RSI 58
  headline "TD Cowen Cuts TPG PT Amid Q1 Preview for Asset Managers"
WHY
  underlying +3.9%/+3.2%/+4.4% (favorable peak -0.8%); position move -4.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-42% · IV residual ~33% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CRCL-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 21.00 · spread +0.0%
  greeks Δ-0.361 Γ0.0146 Θ-0.193 · IV 0.888 · mid 7.75
  overnight_score 8 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 51
  headline "Morgan Stanley Raises Circle Internet Group (CRCL) Price Target to $106, Maintains Equalweight Rating"
WHY
  underlying -0.3%/+0.2%/+3.1% (favorable peak +2.4%); position move -3.1%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-16% · IV residual ~4% [inferred].
  convexity Γ·S = 1.63. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LYB-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI 0.11 · spread +0.0%
  greeks Δ-0.472 Γ0.0307 Θ-0.075 · IV 0.554 · mid 5.15
  overnight_score 2 · flow HEDGING · catalyst Earnings Beat (0.75) · RSI 53
  headline "LyondellBasell targets $500m incremental cash flow in 2026 as Middle East disruptions reshape petrochemical…"
WHY
  underlying -0.8%/-1.4%/+1.0% (favorable peak +2.1%); position move -1.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-7% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.28. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDB-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ-0.393 Γ0.0091 Θ-0.290 · IV 0.684 · mid 17.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 31
  headline "Zacks Names MongoDB 'Bear of the Day' Amid AI Agent Disruption Fears"
WHY
  underlying +4.5%/+3.4%/+8.0% (favorable peak +0.6%); position move -8.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-41% · IV residual ~27% [inferred].
  convexity Γ·S = 2.05. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 6.40 · spread +0.0%
  greeks Δ-0.437 Γ0.0082 Θ-0.271 · IV 0.493 · mid 21.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 33
  headline "Intuit Shares Plunge as AI Fears and Lowered TurboTax Outlook Overshadow Earnings Beat"
WHY
  underlying -4.9%/-3.8%/-2.2% (favorable peak +6.1%); position move +2.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~14% · IV residual ~-29% [inferred].
  convexity Γ·S = 2.64. exit TIMEOUT → realized -19%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LITE-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 125.00 · spread +0.0%
  greeks Δ-0.463 Γ0.0017 Θ-1.328 · IV 0.881 · mid 106.90
  overnight_score 5 · flow HEDGING · catalyst Earnings Beat (0.90) · RSI 54
  headline "Lumentum Tumbles Despite Blowout Fiscal Q3 Report as Investors Pivot to Debt and Dilution Concerns"
WHY
  underlying +1.3%/+18.0%/+11.2% (favorable peak +3.0%); position move -11.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-43% · IV residual ~29% [inferred].
  convexity Γ·S = 1.49. exit TIMEOUT → realized -18%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZS-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 3.33 · spread +0.1%
  greeks Δ-0.403 Γ0.0124 Θ-0.167 · IV 0.766 · mid 9.95
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 42
  headline "Zscaler (ZS) Is Considered a Good Investment by Brokers: Is That True?"
WHY
  underlying +7.0%/+8.8%/+8.2% (favorable peak -1.0%); position move -8.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-43% · IV residual ~31% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized -18%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UAL-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 2.43 · spread +0.0%
  greeks Δ-0.333 Γ0.0219 Θ-0.082 · IV 0.584 · mid 4.15
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.90) · RSI 45
  headline "United Airlines Slashes 2026 Profit Forecast as Fuel Costs Surge Following Middle East Conflict"
WHY
  underlying -0.5%/+1.4%/+0.2% (favorable peak +3.4%); position move -0.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-2% · IV residual ~-10% [inferred].
  convexity Γ·S = 2.01. exit TIMEOUT → realized -17%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE WING-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.1%
  greeks Δ-0.518 Γ0.0085 Θ-0.310 · IV 0.867 · mid 23.35
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.35) · RSI 52
  headline "Wingstop (WING) Stock Drops Despite Market Gains; Consensus EPS Projection Moved 2.72% Lower"
WHY
  underlying -2.8%/+2.6%/+4.0% (favorable peak +4.8%); position move -4.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-17% · IV residual ~4% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RH-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 3.33 · spread +0.1%
  greeks Δ-0.423 Γ0.0256 Θ-0.304 · IV 0.706 · mid 5.56
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.70) · RSI 47
  headline "INVESTOR ALERT: Pomerantz Law Firm Investigates Claims On Behalf of Investors of RH - RH"
WHY
  underlying -0.7%/-0.7%/-2.2% (favorable peak +2.6%); position move +2.2%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~23% · IV residual ~-24% [inferred].
  convexity Γ·S = 3.41. exit TIMEOUT → realized -17%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RJF-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ-0.418 Γ0.0287 Θ-0.090 · IV 0.323 · mid 3.20
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.80) · RSI 54
  headline "Financials Capitulate: Major banks and advisors act as an anchor on the broader index as capital rotates in…"
WHY
  underlying +0.6%/+0.9%/+2.4% (favorable peak +1.0%); position move -2.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-48% · IV residual ~39% [inferred].
  convexity Γ·S = 4.33. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MRVL-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 3.02 · spread +0.1%
  greeks Δ-0.349 Γ0.0099 Θ-0.224 · IV 0.838 · mid 11.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 72
  headline "A Look At Marvell Technology (MRVL) Valuation After A Sharp AI Data Center Pivot"
WHY
  underlying +2.2%/+7.8%/+7.6% (favorable peak +1.3%); position move -7.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-37% · IV residual ~26% [inferred].
  convexity Γ·S = 1.52. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SMCI-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 88.53 · spread +0.1%
  greeks Δ-0.478 Γ0.0642 Θ-0.054 · IV 0.868 · mid 2.75
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.75) · RSI 60
  headline "Supermicro to Report Third Quarter Fiscal 2026 Financial Results on May 5th"
WHY
  underlying -8.3%/-0.3%/-4.6% (favorable peak +10.7%); position move +4.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~23% · IV residual ~-34% [inferred].
  convexity Γ·S = 1.87. exit TIMEOUT → realized -17%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TPG-2026-04-17-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 0.70 · spread +0.1%
  greeks Δ-0.459 Γ0.0606 Θ-0.049 · IV 0.534 · mid 3.21
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.30) · RSI 61
  headline "TPG Inc. (TPG) to Announce First Quarter 2026 Financial Results on May 1"
WHY
  underlying -0.7%/+0.5%/+1.3% (favorable peak +1.4%); position move -1.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-9% · IV residual ~-4% [inferred].
  convexity Γ·S = 2.72. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SCHW-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ-0.347 Γ0.0421 Θ-0.038 · IV 0.291 · mid 2.11
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 43
  headline "Charles Schwab Rolls Out Bitcoin and Ethereum Trading Amid Strategic Banking Business Shrinkage"
WHY
  underlying +1.6%/+3.3%/+2.6% (favorable peak -0.4%); position move -2.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-39% · IV residual ~28% [inferred].
  convexity Γ·S = 3.76. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SCCO-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 19.53 · spread +0.0%
  greeks Δ-0.515 Γ0.0208 Θ-0.355 · IV 0.631 · mid 8.50
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 46
  headline "Wells Fargo Cuts Southern Copper (SCCO) Price Target Amid Copper Rally"
WHY
  underlying -4.3%/-5.4%/-3.6% (favorable peak +6.5%); position move +3.6%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~39% · IV residual ~-43% [inferred].
  convexity Γ·S = 3.71. exit TIMEOUT → realized -17%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LITE-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 35.00 · spread +0.1%
  greeks Δ-0.335 Γ0.0015 Θ-1.241 · IV 0.919 · mid 68.21
  overnight_score 5 · flow HEDGING · catalyst Sector Rotation (0.85) · RSI 47
  headline "Lumentum Dives 9% as AI Optics Profit-Takers Strike and Prominent AI Investor Exits Stake"
WHY
  underlying +11.1%/+9.1%/+4.9% (favorable peak +1.0%); position move -4.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-21% · IV residual ~10% [inferred].
  convexity Γ·S = 1.26. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ABT-2026-04-24-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 3.12 · spread +0.0%
  greeks Δ-0.455 Γ0.0547 Θ-0.042 · IV 0.260 · mid 2.85
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 25
  headline "Abbott Reports Promising Data on Heart Treatment Technology Amidst Continued Post-Earnings Pressure"
WHY
  underlying +1.8%/+3.0%/+0.2% (favorable peak +0.3%); position move -0.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-3% · IV residual ~-9% [inferred].
  convexity Γ·S = 4.98. exit TIMEOUT → realized -16%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE LULU-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ-0.373 Γ0.0285 Θ-0.148 · IV 0.480 · mid 4.18
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 32
  headline "Lululemon shares edge higher, clawing back ground near 52-week lows amid CEO transition skepticism"
WHY
  underlying +1.4%/+2.6%/+0.7% (favorable peak +0.5%); position move -0.7%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-9% · IV residual ~3% [inferred].
  convexity Γ·S = 3.71. exit TIMEOUT → realized -16%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FIS-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.512 Γ0.0693 Θ-0.038 · IV 0.426 · mid 2.65
  overnight_score 2 · flow DIRECTIONAL · catalyst Sector Rotation (0.15) · RSI 47
  headline "Wall Street Erases Recent Losses as Tech Sector Rallies; FIS Lags Peers Amidst Continued Technical Weakness"
WHY
  underlying +2.9%/+3.5%/+3.2% (favorable peak -0.3%); position move -3.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-29% · IV residual ~18% [inferred].
  convexity Γ·S = 3.26. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HL-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 21 · V/OI 18.82 · spread +0.0%
  greeks Δ-0.524 Γ0.1386 Θ-0.026 · IV 0.698 · mid 1.31
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.50) · RSI 43
  headline "Hecla Mining Co (HL) Shares Fall 3.6% -- GF Value Says Still Overvalued"
WHY
  underlying +3.8%/+4.9%/+3.5% (favorable peak +3.3%); position move -3.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-24% · IV residual ~14% [inferred].
  convexity Γ·S = 2.35. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EL-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 41.00 · spread +0.0%
  greeks Δ-0.438 Γ0.0349 Θ-0.209 · IV 0.853 · mid 4.26
  overnight_score 2 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 48
  headline "Estee Lauder taps JP Morgan to finance Puig takeover bid, Spanish daily Expansion says"
WHY
  underlying -2.6%/-1.5%/-1.9% (favorable peak +4.1%); position move +1.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~15% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized -16%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MA-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 20.00 · spread +0.0%
  greeks Δ-0.473 Γ0.0114 Θ-0.189 · IV 0.229 · mid 14.40
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 47
  headline "Mastercard Beats Q1 Estimates but Shares Slide on Cautious Guidance and April Growth Slowdown"
WHY
  underlying -1.5%/+0.4%/-1.2% (favorable peak +2.1%); position move +1.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~19% · IV residual ~-31% [inferred].
  convexity Γ·S = 5.75. exit TIMEOUT → realized -16%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CVNA-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 15.00 · spread +0.0%
  greeks Δ-0.392 Γ0.0055 Θ-0.380 · IV 0.603 · mid 23.48
  overnight_score 5 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 55
  headline "Carvana Q1 Earnings Beat Estimates on Record Retail Unit Growth as Stock Prepares for 5-for-1 Split"
WHY
  underlying -1.6%/-0.9%/+1.8% (favorable peak +3.9%); position move -1.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-11% · IV residual ~1% [inferred].
  convexity Γ·S = 2.09. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UAL-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.1%
  greeks Δ-0.424 Γ0.0254 Θ-0.107 · IV 0.588 · mid 5.25
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.92) · RSI 52
  headline "Trump Announces Strait of Hormuz Blockade as Ceasefire Talks Fail; United CEO Warns of $11B Fuel Cost Surge"
WHY
  underlying -1.2%/+0.8%/-2.2% (favorable peak +3.3%); position move +2.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~17% · IV residual ~-27% [inferred].
  convexity Γ·S = 2.45. exit TIMEOUT → realized -16%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RH-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ-0.422 Γ0.0185 Θ-0.198 · IV 0.710 · mid 6.95
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 42
  headline "RH Hovers Near 6-Year Lows as Analysts Maintain Cautious Outlook Following Q4 Earnings Miss"
WHY
  underlying +0.5%/+4.1%/+3.1% (favorable peak +1.0%); position move -3.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-24% · IV residual ~17% [inferred].
  convexity Γ·S = 2.33. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MRNA-2026-05-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 7 · V/OI 2.29 · spread +0.1%
  greeks Δ-0.713 Γ0.0805 Θ-0.091 · IV 0.618 · mid 3.38
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 44
  headline "Moderna (MRNA) Flu Vaccine Review Scheduled by FDA for June 2026 Amid Heavy Insider Selling"
WHY
  underlying -0.8%/-0.5%/+0.7% (favorable peak +2.3%); position move -0.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-7% · IV residual ~0% [inferred].
  convexity Γ·S = 3.81. exit TIMEOUT → realized -15%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TER-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 11.00 · spread +0.1%
  greeks Δ-0.457 Γ0.0057 Θ-0.473 · IV 0.800 · mid 22.52
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.95) · RSI 38
  headline "Teradyne Plunges 17% as Soft Guidance Offsets Record AI-Driven Q1 Results"
WHY
  underlying +12.1%/+12.8%/+10.2% (favorable peak -6.7%); position move -10.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-63% · IV residual ~55% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized -15%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZS-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 14.00 · spread +0.0%
  greeks Δ-0.410 Γ0.0127 Θ-0.249 · IV 0.827 · mid 10.31
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 55
  headline "Zscaler to Host Third Quarter Fiscal Year 2026 Earnings Conference Call on May 26"
WHY
  underlying +4.3%/+5.2%/+10.2% (favorable peak +2.1%); position move -10.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-59% · IV residual ~52% [inferred].
  convexity Γ·S = 1.86. exit TIMEOUT → realized -15%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BMNR-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 1.00 · spread +0.1%
  greeks Δ-0.543 Γ0.0798 Θ-0.045 · IV 0.920 · mid 2.38
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 53
  headline "Bitmine Immersion Technologies Tumbles as CLARITY Act Regulatory Roadblock Hits Crypto Equities"
WHY
  underlying +0.6%/-2.0%/-2.4% (favorable peak +6.5%); position move +2.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~12% · IV residual ~-21% [inferred].
  convexity Γ·S = 1.76. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE VST-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI 3.57 · spread +0.1%
  greeks Δ-0.306 Γ0.0116 Θ-0.142 · IV 0.596 · mid 7.77
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.80) · RSI 52
  headline "Raymond James and Morgan Stanley Slash Vistra Price Targets Citing Weak ERCOT Demand"
WHY
  underlying -4.5%/-2.0%/-3.6% (favorable peak +5.0%); position move +3.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~23% · IV residual ~-32% [inferred].
  convexity Γ·S = 1.86. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HTZ-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 2.50 · spread +0.1%
  greeks Δ-0.253 Γ0.2123 Θ-0.007 · IV 0.822 · mid 0.30
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 53
  headline "Hertz Liquidity Path Is the Swing Factor for Risk-Tolerant Buyers as Cash Burn Hits $3.5B"
WHY
  underlying -7.1%/-4.7%/-5.8% (favorable peak +9.2%); position move +5.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~30% · IV residual ~-37% [inferred].
  convexity Γ·S = 1.31. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SHOP-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI 4.00 · spread +0.0%
  greeks Δ-0.353 Γ0.0183 Θ-0.086 · IV 0.605 · mid 6.39
  overnight_score 8 · flow HEDGING · catalyst Technical Breakout (0.65) · RSI 34
  headline "Shopify Stock Hits 'Rock Bottom' Support as Analysts Flag Aggressive Institutional Distribution"
WHY
  underlying +2.9%/+5.1%/+3.7% (favorable peak +1.5%); position move -3.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-20% · IV residual ~10% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized -14%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APP-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 7.33 · spread +0.0%
  greeks Δ-0.340 Γ0.0034 Θ-0.912 · IV 0.982 · mid 26.93
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.40) · RSI 53
  headline "AppLovin (APP) Drops 6% as Institutional Rotation and Unresolved SEC Probe Weigh on Sentiment"
WHY
  underlying -1.3%/+1.3%/-1.1% (favorable peak +5.0%); position move +1.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~6% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.54. exit TIMEOUT → realized -14%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BILL-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 29.43 · spread +0.0%
  greeks Δ-0.456 Γ0.0515 Θ-0.106 · IV 1.060 · mid 2.92
  overnight_score 4 · flow HEDGING · catalyst Technical Breakout (0.75) · RSI 41
  headline "BILL Hits New 52-Week Low as Critical Support Fails, Triggering Technical Sell-Off"
WHY
  underlying +1.4%/+2.4%/+2.9% (favorable peak +1.1%); position move -2.9%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-17% · IV residual ~14% [inferred].
  convexity Γ·S = 1.89. exit TIMEOUT → realized -14%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SMR-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 11.20 · spread +0.1%
  greeks Δ-0.437 Γ0.1098 Θ-0.020 · IV 0.981 · mid 1.48
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 52
  headline "Nuscale Power: Sell, True Revenue Is Far, Far Away"
WHY
  underlying +1.0%/+5.0%/+6.8% (favorable peak +4.4%); position move -6.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-24% · IV residual ~15% [inferred].
  convexity Γ·S = 1.32. exit TIMEOUT → realized -14%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AAOI-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI 6.67 · spread +0.0%
  greeks Δ-0.426 Γ0.0059 Θ-0.362 · IV 1.294 · mid 27.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.75) · RSI 50
  headline "Applied Optoelectronics Shares Slide as Earnings Miss and Insider Selling Weigh on Sentiment"
WHY
  underlying +7.0%/+9.8%/+7.5% (favorable peak +1.0%); position move -7.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-20% · IV residual ~10% [inferred].
  convexity Γ·S = 0.97. exit TIMEOUT → realized -13%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LYB-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 0.03 · spread +0.0%
  greeks Δ-0.356 Γ0.0327 Θ-0.059 · IV 0.488 · mid 3.09
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 51
  headline "LyondellBasell targets $500m incremental cash flow in 2026 as Middle East disruptions reshape petrochemical…"
WHY
  underlying +1.1%/+0.3%/-0.4% (favorable peak +1.1%); position move +0.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~3% · IV residual ~-10% [inferred].
  convexity Γ·S = 2.40. exit TIMEOUT → realized -13%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE HUBS-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 26 · V/OI 0.02 · spread +0.0%
  greeks Δ-0.441 Γ0.0106 Θ-0.276 · IV 0.695 · mid 15.65
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 44
  headline "HubSpot Bearish Sentiment Persists as Institutions Target $200 Level Following Post-Earnings Relief Rally"
WHY
  underlying -2.0%/-0.6%/-1.6% (favorable peak +3.8%); position move +1.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~9% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized -13%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE FFIV-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ-0.573 Γ0.0096 Θ-0.260 · IV 0.487 · mid 16.15
  overnight_score 1 · flow DIRECTIONAL · catalyst Sector Rotation (0.40) · RSI 55
  headline "F5 Inc. stock: Why its multi-cloud security edge matters more now for U.S. investors"
WHY
  underlying +3.0%/+3.9%/+5.0% (favorable peak -0.3%); position move -5.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-53% · IV residual ~45% [inferred].
  convexity Γ·S = 2.88. exit TIMEOUT → realized -12%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE QBTS-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 41 · V/OI 0.87 · spread +0.1%
  greeks Δ-0.475 Γ0.0627 Θ-0.030 · IV 0.938 · mid 2.65
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 50
  headline "D-Wave Quantum Shares Fall as 81% Revenue Contraction Triggers Valuation Reset Concerns"
WHY
  underlying -6.3%/-10.6%/-5.2% (favorable peak +12.9%); position move +5.2%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~19% · IV residual ~-28% [inferred].
  convexity Γ·S = 1.28. exit TIMEOUT → realized -12%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CLSK-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.474 Γ0.1150 Θ-0.020 · IV 0.934 · mid 1.33
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 59
  headline "CleanSpark (CLSK) Expected to Release Q2 2026 Results on May 7 Amid Analyst Price Target Trims"
WHY
  underlying +5.3%/+10.2%/+19.1% (favorable peak +0.4%); position move -19.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-83% · IV residual ~75% [inferred].
  convexity Γ·S = 1.40. exit TIMEOUT → realized -12%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ADP-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 20 · V/OI 0.98 · spread +0.0%
  greeks Δ-0.483 Γ0.0256 Θ-0.155 · IV 0.309 · mid 6.30
  overnight_score 4 · flow HEDGING · catalyst Analyst Upgrade (0.75) · RSI 58
  headline "Wells Fargo Upgrades ADP to Equal Weight on Stabilizing Fundamentals and Valuation Relief"
WHY
  underlying +3.9%/+2.8%/+2.9% (favorable peak -0.3%); position move -2.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-48% · IV residual ~43% [inferred].
  convexity Γ·S = 5.50. exit TIMEOUT → realized -12%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FIGR-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 2.57 · spread +0.1%
  greeks Δ-0.343 Γ0.0364 Θ-0.051 · IV 0.946 · mid 3.60
  overnight_score 2 · flow DIRECTIONAL · catalyst Insider Activity (0.40) · RSI 52
  headline "Figure Technology Solutions CEO Michael Tannenbaum Sells $4.2M in Stock Ahead of Q1 Earnings"
WHY
  underlying +3.8%/+2.7%/+6.3% (favorable peak +1.5%); position move -6.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-21% · IV residual ~14% [inferred].
  convexity Γ·S = 1.28. exit TIMEOUT → realized -12%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDB-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI n/a · spread +0.1%
  greeks Δ-0.452 Γ0.0054 Θ-0.953 · IV 1.108 · mid 29.45
  overnight_score 8 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.75) · RSI 71
  headline "MongoDB (MDB) to Release Quarterly Earnings on Thursday, May 28; Analysts Expect $1.18 EPS"
WHY
  underlying -3.5%/-0.9%/-6.6% (favorable peak +7.7%); position move +6.6%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~33% · IV residual ~-35% [inferred].
  convexity Γ·S = 1.77. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HUM-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 13.38 · spread +0.0%
  greeks Δ-0.531 Γ0.0183 Θ-0.196 · IV 0.380 · mid 9.85
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 74
  headline "Humana stock falls despite Q1 2026 beat as Star ratings decline clouds outlook"
WHY
  underlying -1.2%/+0.6%/+1.3% (favorable peak +2.3%); position move -1.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-17% · IV residual ~11% [inferred].
  convexity Γ·S = 4.32. exit TIMEOUT → realized -11%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.395 Γ0.0079 Θ-0.252 · IV 0.509 · mid 11.13
  overnight_score 7 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 31
  headline "Intuit Shares Slump as TurboTax Guidance Cut and 17% Job Cuts Fuel AI Disruption Fears"
WHY
  underlying +1.1%/+2.8%/+8.9% (favorable peak +1.3%); position move -8.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-96% · IV residual ~92% [inferred].
  convexity Γ·S = 2.41. exit TIMEOUT → realized -11%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PRIM-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI 0.46 · spread +0.0%
  greeks Δ-0.286 Γ0.0168 Θ-0.090 · IV 0.558 · mid 4.13
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 37
  headline "Primoris Services (PRIM) Bounces 8.8% After Mizuho Upgrade and Valuation Bottom-Fishing Following Earnings …"
WHY
  underlying -1.0%/-1.3%/+1.0% (favorable peak +3.0%); position move -1.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-8% · IV residual ~4% [inferred].
  convexity Γ·S = 1.93. exit TIMEOUT → realized -11%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE WING-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ-0.349 Γ0.0076 Θ-0.312 · IV 0.934 · mid 13.79
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.45) · RSI 49
  headline "Oil Prices Above $110 Weigh on Restaurant Sector Ahead of Wingstop Q1 Earnings"
WHY
  underlying +5.5%/+7.0%/+1.7% (favorable peak +0.0%); position move -1.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-8% · IV residual ~4% [inferred].
  convexity Γ·S = 1.42. exit TIMEOUT → realized -11%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DUOL-2026-05-08-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.497 Γ0.0203 Θ-0.111 · IV 0.600 · mid 8.74
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 54
  headline "Duolingo slumps as sharply slower bookings outlook and AI-driven margin compression overshadow Q1 beat"
WHY
  underlying -2.6%/-1.8%/-2.8% (favorable peak +6.6%); position move +2.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~17% · IV residual ~-24% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BX-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 1.00 · spread +0.0%
  greeks Δ-0.340 Γ0.0349 Θ-0.097 · IV 0.381 · mid 1.98
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 44
  headline "Blackstone Shares Hit 20-Day Low as Zacks Downgrades to Strong Sell Amid $4B Deal Collapse"
WHY
  underlying -0.7%/-3.1%/-0.9% (favorable peak +4.4%); position move +0.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~18% · IV residual ~-14% [inferred].
  convexity Γ·S = 4.11. exit TIMEOUT → realized -10%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AEIS-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 10.43 · spread +0.1%
  greeks Δ-0.432 Γ0.0074 Θ-0.228 · IV 0.439 · mid 20.85
  overnight_score 6 · flow HEDGING · catalyst Guidance Cut (0.95) · RSI 60
  headline "Advanced Energy Industries (AEIS) Shares Tumble Over 8% After Q2 Guidance Misses Expectations Despite Q1 Ea…"
WHY
  underlying -10.7%/-6.8%/-9.1% (favorable peak +13.5%); position move +9.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~73% · IV residual ~-80% [inferred].
  convexity Γ·S = 2.86. exit TIMEOUT → realized -10%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RBLX-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ-0.377 Γ0.0275 Θ-0.114 · IV 0.934 · mid 3.66
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 51
  headline "Goldman Sachs Trims Roblox Price Target to $125 Ahead of Q1 Earnings as Engagement Concerns Mount"
WHY
  underlying -7.0%/-6.0%/-3.6% (favorable peak +11.8%); position move +3.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~22% · IV residual ~-23% [inferred].
  convexity Γ·S = 1.64. exit TIMEOUT → realized -10%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HTZ-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 0.62 · spread +0.0%
  greeks Δ-0.307 Γ0.1656 Θ-0.012 · IV 1.208 · mid 0.50
  overnight_score 6 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 51
  headline "Hertz Q1 Revenue Hits 3-Year High but Substantial Cash Burn and Negative EBITDA Persist"
WHY
  underlying +6.4%/+1.3%/-0.7% (favorable peak +6.7%); position move +0.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~2% · IV residual ~-5% [inferred].
  convexity Γ·S = 1.01. exit TIMEOUT → realized -10%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE SPOT-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 2.00 · spread +0.0%
  greeks Δ-0.407 Γ0.0061 Θ-0.320 · IV 0.482 · mid 12.65
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 31
  headline "Spotify Downgraded to Peer Perform at Wolfe Research on Revenue Growth Concerns"
WHY
  underlying +1.4%/+1.9%/-0.4% (favorable peak +2.0%); position move +0.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~5% · IV residual ~-7% [inferred].
  convexity Γ·S = 2.54. exit TIMEOUT → realized -10%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE VLO-2026-04-17-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 17.50 · spread +0.0%
  greeks Δ-0.301 Γ0.0109 Θ-0.133 · IV 0.427 · mid 7.88
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.95) · RSI 45
  headline "Refiners Slump as Iran Announces Reopening of Strait of Hormuz, Erasing Geopolitical Risk Premium"
WHY
  underlying +1.2%/+4.4%/+4.8% (favorable peak +0.2%); position move -4.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-41% · IV residual ~37% [inferred].
  convexity Γ·S = 2.45. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE REGN-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.485 Γ0.0047 Θ-0.395 · IV 0.362 · mid 34.40
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.70) · RSI 44
  headline "FDA Rejects Regeneron's Bid for Extended Dosing of EYLEA HD Beyond 16 Weeks"
WHY
  underlying +0.8%/+0.5%/+2.0% (favorable peak +1.0%); position move -2.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-20% · IV residual ~14% [inferred].
  convexity Γ·S = 3.34. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AVAV-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ-0.290 Γ0.0081 Θ-0.203 · IV 0.678 · mid 8.72
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 50
  headline "AeroVironment Introduces MAYHEM 10: Multi-Role Launched Effects System at AAAA 2026"
WHY
  underlying -5.2%/-2.4%/+4.0% (favorable peak +7.8%); position move -4.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-27% · IV residual ~25% [inferred].
  convexity Γ·S = 1.63. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RDDT-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 3.60 · spread +0.1%
  greeks Δ-0.388 Γ0.0172 Θ-0.193 · IV 0.568 · mid 6.97
  overnight_score 5 · flow HEDGING · catalyst Analyst Downgrade (0.55) · RSI 50
  headline "Phillip Securities Downgrades Reddit to Accumulate on Normalizing Ad Growth Trajectory"
WHY
  underlying -5.0%/-2.7%/-7.1% (favorable peak +8.3%); position move +7.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~65% · IV residual ~-65% [inferred].
  convexity Γ·S = 2.82. exit TIMEOUT → realized -9%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AZO-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ-0.489 Γ0.0014 Θ-1.866 · IV 0.293 · mid 111.65
  overnight_score 1 · flow MIXED · catalyst — (—) · RSI 50
WHY
  underlying +2.4%/+2.7%/+3.3% (favorable peak -0.4%); position move -3.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-51% · IV residual ~47% [inferred].
  convexity Γ·S = 5.00. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDB-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI 5.00 · spread +0.0%
  greeks Δ-0.359 Γ0.0054 Θ-0.338 · IV 0.837 · mid 22.12
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 49
  headline "ServiceNow Falls 12% on Weak Guidance, Dragging Down High-Growth Software Names Like MongoDB"
WHY
  underlying +0.0%/-2.9%/+2.0% (favorable peak +5.2%); position move -2.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-9% · IV residual ~4% [inferred].
  convexity Γ·S = 1.40. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AVAV-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ-0.269 Γ0.0078 Θ-0.179 · IV 0.675 · mid 13.71
  overnight_score 3 · flow HEDGING · catalyst Analyst Upgrade (0.75) · RSI 46
  headline "AeroVironment Appoints Raytheon Veteran Dr. Robert Smith as COO to Scale Manufacturing"
WHY
  underlying +0.1%/+2.1%/+3.9% (favorable peak +1.0%); position move -3.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-15% · IV residual ~10% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DUOL-2026-04-17-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 14.00 · spread +0.1%
  greeks Δ-0.377 Γ0.0132 Θ-0.129 · IV 0.854 · mid 8.70
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 54
  headline "Duolingo Files Annual Report (Form ARS) as Analyst Consensus Shifts Toward 'Hold'"
WHY
  underlying +4.3%/+2.1%/+5.0% (favorable peak +0.6%); position move -5.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-22% · IV residual ~17% [inferred].
  convexity Γ·S = 1.33. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.492 Γ0.0076 Θ-0.484 · IV 0.571 · mid 22.95
  overnight_score 4 · flow HEDGING · catalyst Regulatory (0.85) · RSI 42
  headline "IRS Makes Free Direct File System Permanent, Raising Competitive Fears for Intuit's TurboTax"
WHY
  underlying +3.3%/+1.7%/+4.5% (favorable peak +0.6%); position move -4.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-37% · IV residual ~34% [inferred].
  convexity Γ·S = 2.90. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TDG-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 0.86 · spread +0.0%
  greeks Δ-0.403 Γ0.0029 Θ-2.457 · IV 0.657 · mid 37.38
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 41
  headline "TransDigm Group Q2 2026 Earnings Report Scheduled for May 5 Before Market Open"
WHY
  underlying +3.6%/+7.3%/+8.0% (favorable peak -2.0%); position move -8.0%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-100% · IV residual ~111% [inferred].
  convexity Γ·S = 3.33. exit TIMEOUT → realized -8%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE REGN-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.487 Γ0.0071 Θ-0.489 · IV 0.341 · mid 24.48
  overnight_score 2 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 29
  headline "Regeneron shares fall 7% on Eylea sales decline and regulatory delays despite earnings beat"
WHY
  underlying +3.0%/+2.2%/+3.3% (favorable peak -0.4%); position move -3.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-45% · IV residual ~43% [inferred].
  convexity Γ·S = 4.86. exit TIMEOUT → realized -8%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SPOT-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ-0.138 Γ0.0025 Θ-0.273 · IV 0.553 · mid 6.75
  overnight_score 5 · flow HEDGING · catalyst No Clear Catalyst (0.40) · RSI 62
  headline "KeyBanc raises Spotify stock price target on AI personalization ahead of April 28 earnings"
WHY
  underlying +1.0%/+1.0%/-1.7% (favorable peak +1.8%); position move +1.7%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~18% · IV residual ~-15% [inferred].
  convexity Γ·S = 1.31. exit TIMEOUT → realized -8%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MMYT-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI 0.36 · spread +0.0%
  greeks Δ-0.474 Γ0.0432 Θ-0.050 · IV 0.666 · mid 3.60
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 45
  headline "MakeMyTrip (MMYT) Stock Sinks As Market Gains; Earnings Projected to Fall 26% YoY"
WHY
  underlying -4.1%/-3.8%/-3.7% (favorable peak +5.5%); position move +3.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~22% · IV residual ~-26% [inferred].
  convexity Γ·S = 1.94. exit TIMEOUT → realized -8%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ULTA-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 21.50 · spread +0.1%
  greeks Δ-0.370 Γ0.0055 Θ-0.515 · IV 0.520 · mid 18.68
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.45) · RSI 37
  headline "Ulta Beauty Sentiment Shifts Bearish as Options Volume Surges Despite Analyst Buy Ratings"
WHY
  underlying -1.3%/-3.9%/-2.7% (favorable peak +4.8%); position move +2.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~27% · IV residual ~-27% [inferred].
  convexity Γ·S = 2.82. exit TIMEOUT → realized -8%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE KKR-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 280.00 · spread +0.0%
  greeks Δ-0.442 Γ0.0375 Θ-0.072 · IV 0.407 · mid 3.83
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 41
  headline "KKR Management Signals 2026 Profit Targets at Risk as Exit Markets Remain Clogged"
WHY
  underlying +0.4%/-0.3%/+0.7% (favorable peak +1.4%); position move -0.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-8% · IV residual ~5% [inferred].
  convexity Γ·S = 3.54. exit TIMEOUT → realized -8%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE LRCX-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 89.43 · spread +0.1%
  greeks Δ-0.312 Γ0.0067 Θ-0.300 · IV 0.694 · mid 12.03
  overnight_score 4 · flow HEDGING · catalyst Earnings Miss (0.90) · RSI 62
  headline "Lam Research (LRCX) heading into earnings this Wednesday after ASML update pressured chip-equipment stocks"
WHY
  underlying -1.8%/+0.9%/-1.7% (favorable peak +3.8%); position move +1.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~12% · IV residual ~-12% [inferred].
  convexity Γ·S = 1.77. exit TIMEOUT → realized -7%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AFRM-2026-05-08-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 34 · V/OI 3.50 · spread +0.0%
  greeks Δ-0.478 Γ0.0318 Θ-0.071 · IV 0.645 · mid 5.62
  overnight_score 4 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 57
  headline "Affirm Stock Down as Revenue Miss Offsets Earnings Beat and Raised Guidance"
WHY
  underlying +3.8%/+2.2%/-0.7% (favorable peak +6.7%); position move +0.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~4% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.04. exit TIMEOUT → realized -7%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ROKU-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 3.14 · spread +0.0%
  greeks Δ-0.359 Γ0.0159 Θ-0.115 · IV 0.646 · mid 5.83
  overnight_score 4 · flow HEDGING · catalyst Insider Activity (0.85) · RSI 67
  headline "Roku Insider Charles Collier Sells 205,807 Shares for $23.67 Million as Stock Hits Multi-Year Highs"
WHY
  underlying +3.7%/+0.7%/+1.0% (favorable peak +1.0%); position move -1.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-7% · IV residual ~5% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -7%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BSX-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI n/a · spread +0.1%
  greeks Δ-0.504 Γ0.0678 Θ-0.030 · IV 0.321 · mid 2.67
  overnight_score 2 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 36
  headline "Boston Scientific stock hits 52-week low as analysts slash price targets following guidance reset"
WHY
  underlying -2.2%/-1.4%/-3.3% (favorable peak +4.1%); position move +3.3%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~37% · IV residual ~-40% [inferred].
  convexity Γ·S = 3.96. exit TIMEOUT → realized -7%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE IDCC-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 33 · V/OI 0.76 · spread +0.0%
  greeks Δ-0.464 Γ0.0114 Θ-0.207 · IV 0.453 · mid 10.17
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 27
  headline "Why InterDigital Stock Is Suddenly Sliding: Traders Reassess Growth Roadmap"
WHY
  underlying +1.3%/+1.7%/+2.2% (favorable peak +1.0%); position move -2.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-26% · IV residual ~26% [inferred].
  convexity Γ·S = 2.97. exit TIMEOUT → realized -7%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PAYX-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 0.07 · spread +0.1%
  greeks Δ-0.493 Γ0.0316 Θ-0.064 · IV 0.400 · mid 4.95
  overnight_score 2 · flow HEDGING · catalyst Macro (0.85) · RSI 55
  headline "U.S. Companies Added 109,000 Jobs in April, Most Since Early 2025, ADP Says"
WHY
  underlying -0.4%/-0.4%/-0.6% (favorable peak +2.4%); position move +0.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~5% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.98. exit TIMEOUT → realized -7%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE OMC-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.1%
  greeks Δ-0.458 Γ0.0519 Θ-0.052 · IV 0.348 · mid 2.92
  overnight_score 1 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 54
  headline "No significant news found for Omnicom Group (OMC) in the past 24 hours"
WHY
  underlying +1.6%/+1.5%/+1.3% (favorable peak -0.7%); position move -1.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-16% · IV residual ~15% [inferred].
  convexity Γ·S = 4.02. exit TIMEOUT → realized -6%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FSLR-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ-0.490 Γ0.0123 Θ-0.269 · IV 0.566 · mid 14.07
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.45) · RSI 66
  headline "Argus Lowers First Solar Price Target to $250 Amid 2026 Growth Concerns"
WHY
  underlying +2.9%/+1.6%/+2.3% (favorable peak +2.4%); position move -2.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-19% · IV residual ~18% [inferred].
  convexity Γ·S = 2.81. exit TIMEOUT → realized -6%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WYNN-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 3.20 · spread +0.0%
  greeks Δ-0.250 Γ0.0303 Θ-0.072 · IV 0.410 · mid 1.87
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.65) · RSI 48
  headline "Resorts World becomes New York City's first full casino as Wynn, MGM, and Caesars sit out the party"
WHY
  underlying +2.8%/+1.7%/-0.8% (favorable peak +1.9%); position move +0.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~11% · IV residual ~-5% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized -6%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE RBLX-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ-0.440 Γ0.0276 Θ-0.126 · IV 0.970 · mid 5.65
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.45) · RSI 53
  headline "Roblox Introduces Age-Based Accounts and Expanded Parental Controls in Major Safety Push"
WHY
  underlying +1.1%/+0.9%/+3.4% (favorable peak +0.5%); position move -3.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-16% · IV residual ~17% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized -6%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HON-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ-0.476 Γ0.0202 Θ-0.092 · IV 0.275 · mid 8.20
  overnight_score 5 · flow MIXED · catalyst — (—) · RSI 33
WHY
  underlying -0.5%/-1.1%/-0.7% (favorable peak +2.1%); position move +0.7%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~8% · IV residual ~-11% [inferred].
  convexity Γ·S = 4.34. exit TIMEOUT → realized -6%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BSX-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.695 Γ0.0639 Θ-0.095 · IV 0.530 · mid 5.78
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 39
  headline "BSX Shareholder Alert: Boston Scientific Corporation Securities Class Action Lawsuit Investors With Losses …"
WHY
  underlying +1.2%/-0.6%/+0.6% (favorable peak +0.7%); position move -0.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-5% · IV residual ~4% [inferred].
  convexity Γ·S = 4.08. exit TIMEOUT → realized -6%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE RH-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 3.67 · spread +0.0%
  greeks Δ-0.364 Γ0.0153 Θ-0.192 · IV 0.698 · mid 6.33
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 53
  headline "RH Stock At Six-Year Low: Analysts Warn Of Short-Term Pressure, Weak Housing Trends"
WHY
  underlying -1.4%/-0.4%/-0.8% (favorable peak +3.1%); position move +0.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~6% · IV residual ~-3% [inferred].
  convexity Γ·S = 2.12. exit TIMEOUT → realized -6%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MMYT-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 0.13 · spread +0.0%
  greeks Δ-0.307 Γ0.0398 Θ-0.100 · IV 0.889 · mid 2.20
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 55
  headline "MakeMyTrip Faces Regulatory Investigation, Shortseller Claims"
WHY
  underlying -0.7%/+1.4%/-1.4% (favorable peak +2.9%); position move +1.4%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~9% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.89. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PSKY-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 0.04 · spread +0.0%
  greeks Δ-0.380 Γ0.4998 Θ-0.019 · IV 0.515 · mid 0.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 41
  headline "Paramount Skydance Shares Under Pressure as Wells Fargo Maintains Underweight Rating with $7 Price Target"
WHY
  underlying -2.2%/-2.9%/-2.1% (favorable peak +4.0%); position move +2.1%.
  decomp [first-order]: theta drag ~37% of premium / 3d · delta capture ~53% · IV residual ~-21% [inferred].
  convexity Γ·S = 5.05. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CGNX-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ-0.284 Γ0.0331 Θ-0.058 · IV 0.665 · mid 1.88
  overnight_score 4 · flow MIXED · catalyst — (—) · RSI 61
WHY
  underlying +0.6%/+1.6%/+1.5% (favorable peak +1.1%); position move -1.5%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-13% · IV residual ~17% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -5%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUM-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ-0.436 Γ0.0119 Θ-0.154 · IV 0.518 · mid 9.65
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 59
  headline "Humana Shares Cool as Market Refocuses on 2026 Earnings Gap Despite 2027 CMS Rate Reprieve"
WHY
  underlying +3.2%/+2.1%/+3.2% (favorable peak +1.1%); position move -3.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-28% · IV residual ~29% [inferred].
  convexity Γ·S = 2.30. exit TIMEOUT → realized -4%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE QCOM-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.1%
  greeks Δ-0.307 Γ0.0236 Θ-0.122 · IV 0.460 · mid 3.31
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 57
  headline "JPMorgan downgrades Qualcomm to Neutral, slashes price target to $140 on smartphone and datacenter concerns"
WHY
  underlying +1.3%/+2.3%/+0.8% (favorable peak +0.0%); position move -0.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-10% · IV residual ~18% [inferred].
  convexity Γ·S = 3.17. exit TIMEOUT → realized -3%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE NBIS-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 63.67 · spread +0.0%
  greeks Δ-0.427 Γ0.0082 Θ-0.248 · IV 1.040 · mid 18.71
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 56
  headline "Nebius Shares Swing $19 in a Day as Investors Weigh $18 Billion Build-Out Against Upcoming Q1 Results"
WHY
  underlying -6.5%/-2.6%/-4.6% (favorable peak +8.5%); position move +4.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~15% · IV residual ~-15% [inferred].
  convexity Γ·S = 1.18. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LFUS-2026-05-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 521.00 · spread +0.1%
  greeks Δ-0.401 Γ0.0055 Θ-0.384 · IV 0.511 · mid 24.45
  overnight_score 5 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.85) · RSI 67
  headline "Littelfuse Outlines Growth Strategy at 2026 Investor Day as Shares Trade Down"
WHY
  underlying -3.0%/-5.2%/-6.5% (favorable peak +9.3%); position move +6.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~49% · IV residual ~-47% [inferred].
  convexity Γ·S = 2.53. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE VST-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI 3.80 · spread +0.1%
  greeks Δ-0.453 Γ0.0139 Θ-0.180 · IV 0.619 · mid 10.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.20) · RSI 51
  headline "Vistra (VST) Pulls Back as Technical Support Weakens Ahead of Q1 Results"
WHY
  underlying -2.9%/-2.4%/-1.7% (favorable peak +3.4%); position move +1.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~12% · IV residual ~-9% [inferred].
  convexity Γ·S = 2.22. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TDG-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 1.40 · spread +0.0%
  greeks Δ-0.426 Γ0.0037 Θ-0.598 · IV 0.273 · mid 23.67
  overnight_score 3 · flow HEDGING · catalyst Guidance Raise (0.85) · RSI 50
  headline "TransDigm Group (TDG) Lifts Annual Outlook On Strong Q2 Results, Acquisitions; Stock Up 7% In Pre-Market"
WHY
  underlying -0.6%/+0.2%/-1.7% (favorable peak +2.6%); position move +1.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~36% · IV residual ~-30% [inferred].
  convexity Γ·S = 4.47. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PATH-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ-0.281 Γ0.1634 Θ-0.008 · IV 0.659 · mid 0.42
  overnight_score 7 · flow MIXED · catalyst — (—) · RSI 30
WHY
  underlying +7.9%/+6.8%/+13.1% (favorable peak +0.3%); position move -13.1%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-82% · IV residual ~86% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BLSH-2026-05-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 21 · V/OI 7.50 · spread +0.0%
  greeks Δ-0.434 Γ0.0577 Θ-0.062 · IV 0.779 · mid 2.53
  overnight_score 3 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 42
  headline "Bullish (BLSH) Misses Q1 Earnings Estimates by 18.7% as Trading Activity Softens"
WHY
  underlying -2.2%/-3.6%/-4.6% (favorable peak +5.9%); position move +4.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~28% · IV residual ~-23% [inferred].
  convexity Γ·S = 2.07. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LMT-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 1.83 · spread +0.0%
  greeks Δ-0.386 Γ0.0090 Θ-0.927 · IV 0.494 · mid 12.04
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 26
  headline "Lockheed Martin (LMT) Stock Moved Down by 3.17% on Apr 22: Drivers Behind the Movement - TradingKey"
WHY
  underlying -4.6%/-7.6%/-7.6% (favorable peak +9.3%); position move +7.6%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~135% · IV residual ~-114% [inferred].
  convexity Γ·S = 5.00. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MA-2026-05-01-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 11.50 · spread +0.0%
  greeks Δ-0.806 Γ0.0118 Θ-0.218 · IV 0.251 · mid 16.91
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 43
  headline "Mastercard Q1 2026 earnings beat estimates, April slowdown"
WHY
  underlying +1.9%/+0.3%/-0.7% (favorable peak +1.2%); position move +0.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~17% · IV residual ~-15% [inferred].
  convexity Γ·S = 5.86. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE IBP-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ-0.593 Γ0.0112 Θ-0.767 · IV 0.752 · mid 19.70
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 30
  headline "Installed Building Products Misses Q1 Expectations; Wells Fargo and Stephens Cut Price Targets Amid Residen…"
WHY
  underlying -27.6%/-26.5%/-31.1% (favorable peak +32.1%); position move +31.1%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~281% · IV residual ~-271% [inferred].
  convexity Γ·S = 3.36. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ESTA-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ-0.460 Γ0.0257 Θ-0.108 · IV 0.871 · mid 13.70
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.70) · RSI 53
  headline "Establishment Labs Director Sells $2.45 Million in Stock as Short Interest Surges"
WHY
  underlying +4.0%/+3.8%/-0.7% (favorable peak +0.9%); position move +0.7%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~2% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.66. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE LMT-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ-0.069 Γ0.0026 Θ-0.092 · IV 0.321 · mid 1.38
  overnight_score 5 · flow HEDGING · catalyst Analyst Downgrade (0.75) · RSI 26
  headline "JPMorgan Lowers Lockheed Martin (LMT) Price Target to $605.00 Following Earnings Miss and Executive Retirement"
WHY
  underlying +1.0%/+0.7%/-0.5% (favorable peak +1.7%); position move +0.5%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~12% · IV residual ~6% [inferred].
  convexity Γ·S = 1.30. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE UBER-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 577.00 · spread +0.0%
  greeks Δ-0.088 Γ0.0144 Θ-0.024 · IV 0.477 · mid 0.42
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 51
  headline "Federal Jury Finds Uber Liable in Bellwether Sexual-Assault Case; AI Infrastructure Costs Pressure Margins"
WHY
  underlying -0.1%/+2.1%/-0.8% (favorable peak +1.6%); position move +0.8%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~12% · IV residual ~3% [inferred].
  convexity Γ·S = 1.07. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE WMT-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 26 · V/OI 1.00 · spread +0.1%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 12.98
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 34
  headline "Walmart stock slides as cautious guidance and fuel costs offset Q1 revenue beat"
WHY
  underlying -1.4%/-1.4%/-1.1% (favorable peak +2.4%); position move +1.1%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CF-2026-04-14-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ-0.354 Γ0.0221 Θ-0.132 · IV 0.561 · mid 4.60
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 47
  headline "Goldman Sachs Lifts CF Target to $132 but Cautions Upside is 'Priced In' Amid Geopolitical Supply Risks"
WHY
  underlying +1.6%/+4.8%/-5.3% (favorable peak +7.8%); position move +5.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~48% · IV residual ~-42% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE DHI-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 0.99 · spread +0.0%
  greeks Δ-0.416 Γ0.0299 Θ-0.121 · IV 0.403 · mid 2.94
  overnight_score 7 · flow DIRECTIONAL · catalyst Macro (0.80) · RSI 35
  headline "D.R. Horton Slumps as Iran War Tensions Drive Oil Over $110, Crushing Housing Rate-Cut Hopes"
WHY
  underlying +1.6%/-0.5%/+4.7% (favorable peak +1.1%); position move -4.7%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-90% · IV residual ~101% [inferred].
  convexity Γ·S = 4.05. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NFLX-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 0.45 · spread +0.1%
  greeks Δ-0.842 Γ0.0280 Θ-0.031 · IV 0.341 · mid 11.10
  overnight_score 5 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 44
  headline "Netflix Price Target Lowered to $110 at Bernstein on Margin Visibility Concerns"
WHY
  underlying -2.4%/-1.7%/-2.1% (favorable peak +2.9%); position move +2.1%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~15% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.65. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SHOP-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI n/a · spread +0.0%
  greeks Δ-0.305 Γ0.0176 Θ-0.079 · IV 0.580 · mid 4.05
  overnight_score 6 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 34
  headline "Shopify Tops US$3.1b Revenue as Growth and Profit Outlooks Cool"
WHY
  underlying -4.4%/-2.4%/+0.4% (favorable peak +5.8%); position move -0.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-3% · IV residual ~7% [inferred].
  convexity Γ·S = 1.75. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE KTOS-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 1.98 · spread +0.0%
  greeks Δ-0.351 Γ0.0244 Θ-0.091 · IV 0.858 · mid 4.24
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 34
  headline "Kratos Defense & Security Solutions Schedules First Quarter 2026 Earnings Conference Call for Wednesday, Ma…"
WHY
  underlying -3.4%/+2.3%/+0.6% (favorable peak +4.2%); position move -0.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-3% · IV residual ~8% [inferred].
  convexity Γ·S = 1.50. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ODD-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ-0.336 Γ0.1793 Θ-0.027 · IV 0.751 · mid 0.55
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.20) · RSI 44
  headline "Oddity Tech (ODD) Relief Rally Faces Institutional Headwinds as Bearish Options Volume Surges"
WHY
  underlying -1.7%/-0.7%/+4.0% (favorable peak +4.8%); position move -4.0%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-35% · IV residual ~48% [inferred].
  convexity Γ·S = 2.61. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HWM-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ-0.677 Γ0.0131 Θ-0.207 · IV 0.466 · mid 12.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 46
  headline "Howmet Aerospace slides 3.8% as investors focus on forward-growth pace ahead of Q1 results"
WHY
  underlying +2.2%/+0.6%/+0.3% (favorable peak +1.2%); position move -0.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-5% · IV residual ~8% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE UBER-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 40 · V/OI 55.67 · spread +0.0%
  greeks Δ-0.373 Γ0.0486 Θ-0.035 · IV 0.330 · mid 2.10
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 40
  headline "Uber reportedly mulling full Delivery Hero takeover, shares drop"
WHY
  underlying -2.4%/-1.5%/-1.3% (favorable peak +3.1%); position move +1.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~16% · IV residual ~-13% [inferred].
  convexity Γ·S = 3.49. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RACE-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.250 Γ0.0089 Θ-0.151 · IV 0.343 · mid 5.51
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 45
  headline "Ferrari Shares Drop Over 6% After Unveiling First Five-Seat Electric Vehicle 'Luce'"
WHY
  underlying +1.0%/+5.0%/+3.1% (favorable peak +0.8%); position move -3.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-47% · IV residual ~53% [inferred].
  convexity Γ·S = 2.94. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GDDY-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 0.99 · spread +0.0%
  greeks Δ-0.325 Γ0.0272 Θ-0.165 · IV 0.792 · mid 5.33
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.75) · RSI 50
  headline "Q4 Rundown: GoDaddy (NYSE:GDDY) Vs Other E-commerce Software Stocks"
WHY
  underlying +1.5%/-0.5%/+0.6% (favorable peak +2.4%); position move -0.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-3% · IV residual ~11% [inferred].
  convexity Γ·S = 2.31. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE EL-2026-05-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 15 · V/OI 2.60 · spread +0.0%
  greeks Δ-0.783 Γ0.0456 Θ-0.059 · IV 0.383 · mid 4.70
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 53
  headline "Estée Lauder Narrows Full-Year EPS Outlook, Flags 2% Sales Headwind for Q4 Amid Broad Restructuring"
WHY
  underlying -1.6%/-2.3%/-2.6% (favorable peak +3.1%); position move +2.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~35% · IV residual ~-34% [inferred].
  convexity Γ·S = 3.74. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HUT-2026-04-23-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 23.00 · spread +0.0%
  greeks Δ-0.408 Γ0.0206 Θ-0.248 · IV 1.179 · mid 5.42
  overnight_score 3 · flow HEDGING · catalyst No Clear Catalyst (0.15) · RSI 71
  headline "Hut 8 Schedules First Quarter 2026 Earnings Release and Conference Call for May 6"
WHY
  underlying -2.4%/-3.9%/-8.5% (favorable peak +11.8%); position move +8.5%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~50% · IV residual ~-38% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE WSM-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 1.42 · spread +0.1%
  greeks Δ-0.715 Γ0.0121 Θ-0.106 · IV 0.460 · mid 27.39
  overnight_score 2 · flow HEDGING · catalyst Technical Breakout (0.40) · RSI 44
  headline "Homebuyers and Sellers Both Grow Cautious as Mortgage Rates Tick Higher"
WHY
  underlying +3.4%/+1.7%/+1.0% (favorable peak -0.2%); position move -1.0%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-5% · IV residual ~4% [inferred].
  convexity Γ·S = 2.18. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LEN-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 222.60 · spread +0.1%
  greeks Δ-0.769 Γ0.0467 Θ-0.129 · IV 0.500 · mid 6.69
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 44
  headline "US housing slowdown leaves buyers squeezed between high prices, rents and down payments"
WHY
  underlying -2.0%/-6.6%/-4.5% (favorable peak +6.7%); position move +4.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~47% · IV residual ~-43% [inferred].
  convexity Γ·S = 4.21. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TMO-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 0.94 · spread +0.0%
  greeks Δ-0.251 Γ0.0068 Θ-0.172 · IV 0.320 · mid 6.23
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.70) · RSI 33
  headline "Thermo Fisher Scientific (TMO) Valuation Check After Recent Share Price Weakness"
WHY
  underlying +0.8%/+2.2%/+3.1% (favorable peak +0.7%); position move -3.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-54% · IV residual ~61% [inferred].
  convexity Γ·S = 2.98. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.330 Γ0.0049 Θ-0.369 · IV 0.611 · mid 18.26
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 48
  headline "Intuit Unveils AI-Powered QuickBooks Workforce Platform Amidst Growing Sector-Wide AI Disruption Fears"
WHY
  underlying +4.7%/+2.0%/+1.2% (favorable peak +0.9%); position move -1.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-9% · IV residual ~13% [inferred].
  convexity Γ·S = 1.90. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MCK-2026-05-08-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 40 · V/OI 0.27 · spread +0.0%
  greeks Δ-0.485 Γ0.0060 Θ-0.316 · IV 0.280 · mid 17.69
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 20
  headline "McKesson Misses Q4 Revenue Estimates, Announces $13 Billion Medical-Surgical Spinoff Plans"
WHY
  underlying -1.5%/-0.2%/+0.1% (favorable peak +1.7%); position move -0.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-3% · IV residual ~6% [inferred].
  convexity Γ·S = 4.39. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MDT-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.462 Γ0.0487 Θ-0.043 · IV 0.329 · mid 3.12
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 44
  headline "AI Models Turn More Cautious on Medtronic as Technicals Weaken and Guidance Resets"
WHY
  underlying +1.6%/+1.1%/+1.1% (favorable peak +0.8%); position move -1.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-12% · IV residual ~14% [inferred].
  convexity Γ·S = 3.76. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE QBTS-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ-0.523 Γ0.0594 Θ-0.056 · IV 1.267 · mid 3.19
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 62
  headline "D-Wave Quantum (QBTS) slides 5.1% amid post-rally profit-taking and lingering secondary-resale overhang"
WHY
  underlying +4.3%/-5.2%/-9.2% (favorable peak +12.1%); position move +9.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~31% · IV residual ~-27% [inferred].
  convexity Γ·S = 1.21. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AR-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.168 Γ0.0544 Θ-0.015 · IV 0.410 · mid 0.25
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 39
  headline "US Natural Gas Prices Decline to $2.88 on Elevated Storage and Mild Weather Forecasts"
WHY
  underlying -1.9%/+0.0%/-0.1% (favorable peak +2.5%); position move +0.1%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~3% · IV residual ~13% [inferred].
  convexity Γ·S = 1.95. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AXP-2026-05-11-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 45 · V/OI 4.00 · spread +0.0%
  greeks Δ-0.439 Γ0.0131 Θ-0.125 · IV 0.278 · mid 10.68
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 45
  headline "S&P Gains Capped by Iran Diplomatic Setback as American Express Extends 3-Day Slide"
WHY
  underlying +0.6%/-0.9%/+0.1% (favorable peak +1.5%); position move -0.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-2% · IV residual ~3% [inferred].
  convexity Γ·S = 4.09. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DUOL-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ-0.295 Γ0.0179 Θ-0.088 · IV 0.597 · mid 4.90
  overnight_score 6 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 54
  headline "Duolingo Shares Plummet as AI Cost Headwinds and Weak Bookings Guidance Trigger 2026 Strategy Concerns"
WHY
  underlying +1.0%/+9.2%/+3.8% (favorable peak +1.9%); position move -3.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-24% · IV residual ~27% [inferred].
  convexity Γ·S = 1.87. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ESI-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.226 Γ0.0609 Θ-0.042 · IV 0.563 · mid 1.00
  overnight_score 1 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 70
  headline "Element Solutions Inc. to Release 2026 First Quarter Financial Results After Market Close Today"
WHY
  underlying -3.9%/+5.4%/+5.5% (favorable peak +4.9%); position move -5.5%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-50% · IV residual ~61% [inferred].
  convexity Γ·S = 2.46. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NEE-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ-0.748 Γ0.0480 Θ-0.032 · IV 0.260 · mid 6.03
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 50
  headline "NextEra Energy (NEE) Stock Dips While Market Gains: Key Facts - April 13, 2026"
WHY
  underlying -1.1%/-1.1%/-0.5% (favorable peak +2.5%); position move +0.5%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~6% · IV residual ~-6% [inferred].
  convexity Γ·S = 4.43. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE REPL-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ-0.316 Γ0.4557 Θ-0.006 · IV 1.457 · mid 0.20
  overnight_score 5 · flow HEDGING · catalyst Regulatory (0.95) · RSI 24
  headline "Replimune Gets Second FDA CRL for Melanoma Drug BLA, Stock Crashes"
WHY
  underlying -0.9%/-5.5%/-15.1% (favorable peak +15.9%); position move +15.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~52% · IV residual ~-44% [inferred].
  convexity Γ·S = 1.00. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SBET-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ-0.430 Γ0.1642 Θ-0.010 · IV 0.993 · mid 1.06
  overnight_score 4 · flow HEDGING · catalyst Analyst Upgrade (0.90) · RSI 47
  headline "HC Wainwright Joins TD Cowen in Initiating SharpLink Gaming (SBET) with Buy Rating and $10 Target"
WHY
  underlying +6.6%/+13.0%/+15.5% (favorable peak -4.9%); position move -15.5%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-42% · IV residual ~43% [inferred].
  convexity Γ·S = 1.10. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE STZ-2026-05-08-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 81.00 · spread +0.0%
  greeks Δ-0.478 Γ0.0485 Θ-0.122 · IV 0.290 · mid 3.34
  overnight_score 2 · flow DIRECTIONAL · catalyst Insider Activity (0.40) · RSI 41
  headline "Constellation Brands Executives Sell Shares as Stock Struggles Post-Earnings"
WHY
  underlying -3.9%/-3.8%/-5.2% (favorable peak +6.1%); position move +5.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~110% · IV residual ~-101% [inferred].
  convexity Γ·S = 7.18. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TECK-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 24 · V/OI 151.00 · spread +0.1%
  greeks Δ-0.096 Γ0.0220 Θ-0.026 · IV 0.525 · mid 0.43
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.45) · RSI 51
  headline "Teck Resources Faces Valuation Risk as Analysts Maintain Targets Well Below Current Market Price"
WHY
  underlying +1.8%/+9.2%/+7.0% (favorable peak -1.3%); position move -7.0%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-89% · IV residual ~105% [inferred].
  convexity Γ·S = 1.25. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BLSH-2026-05-26-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 9 · V/OI 12.50 · spread +0.0%
  greeks Δ-0.732 Γ0.0735 Θ-0.075 · IV 0.802 · mid 3.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 39
  headline "Bullish Global reported Q1 2026 EPS of -$3.85 vs. $0.16 forecast, missing by 2,506%; stock fell 10.18%"
WHY
  underlying -1.0%/+3.3%/+0.7% (favorable peak +4.2%); position move -0.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-5% · IV residual ~9% [inferred].
  convexity Γ·S = 2.55. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE APP-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 26 · V/OI 10.00 · spread +0.0%
  greeks Δ-0.479 Γ0.0049 Θ-0.601 · IV 0.635 · mid 32.20
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 53
  headline "AppLovin Corporation stock downgraded to Hold following technical weakness and institutional stake reduction."
WHY
  underlying +6.8%/+17.9%/+24.5% (favorable peak -3.2%); position move -24.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-176% · IV residual ~180% [inferred].
  convexity Γ·S = 2.38. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WDAY-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI n/a · spread +0.0%
  greeks Δ-0.280 Γ0.0160 Θ-0.223 · IV 0.819 · mid 4.20
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.90) · RSI 52
  headline "Citigroup Cuts Workday to Neutral Without Price Target Ahead of Q1 Earnings"
WHY
  underlying -3.8%/+1.2%/-2.0% (favorable peak +6.0%); position move +2.0%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~17% · IV residual ~-3% [inferred].
  convexity Γ·S = 2.03. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BANC-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ-0.935 Γ0.1751 Θ-0.001 · IV 0.188 · mid 1.65
  overnight_score 1 · flow DIRECTIONAL · catalyst Macro (0.20) · RSI 59
  headline "Regional Banks Under Pressure as Yields Surge; BANC Earnings Scheduled for April 22"
WHY
  underlying +0.7%/+0.4%/+0.7% (favorable peak +1.3%); position move -0.7%.
  decomp [first-order]: theta drag ~0% of premium / 3d · delta capture ~-7% · IV residual ~6% [inferred].
  convexity Γ·S = 3.23. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MDT-2026-04-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ-0.294 Γ0.0723 Θ-0.036 · IV 0.220 · mid 1.01
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.70) · RSI 42
  headline "Truist Financial Issues Pessimistic Forecast for Medtronic (NYSE:MDT) Stock Price"
WHY
  underlying -1.7%/-1.0%/-2.4% (favorable peak +2.4%); position move +2.4%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~61% · IV residual ~-52% [inferred].
  convexity Γ·S = 6.30. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RCL-2026-04-16-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ-0.428 Γ0.0080 Θ-0.269 · IV 0.591 · mid 17.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 42
  headline "UBS Slashes Royal Caribbean 2026 Yield Forecast to 1.5% as Geopolitical Risks Cool European Demand"
WHY
  underlying +7.3%/+6.1%/+2.1% (favorable peak -1.7%); position move -2.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-14% · IV residual ~17% [inferred].
  convexity Γ·S = 2.13. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MELI-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ-0.474 Γ0.0014 Θ-1.340 · IV 0.487 · mid 111.05
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 54
  headline "MercadoLibre Faces $52M Bearish Flow as Analysts Slash Price Targets Amid Mounting Margin Pressure"
WHY
  underlying +3.3%/+3.8%/+5.5% (favorable peak +0.7%); position move -5.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-42% · IV residual ~44% [inferred].
  convexity Γ·S = 2.48. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAKE-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 115.38 · spread +0.0%
  greeks Δ-0.534 Γ0.0364 Θ-0.137 · IV 0.806 · mid 5.50
  overnight_score 3 · flow HEDGING · catalyst Earnings Beat (0.90) · RSI 60
  headline "The Cheesecake Factory (NASDAQ:CAKE) Surprises With Q1 CY2026 Sales and EPS Beat"
WHY
  underlying +0.3%/-3.9%/-5.4% (favorable peak +5.8%); position move +5.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~33% · IV residual ~-27% [inferred].
  convexity Γ·S = 2.28. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MELI-2026-05-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 26 · V/OI 5.50 · spread +0.0%
  greeks Δ-0.404 Γ0.0023 Θ-1.169 · IV 0.375 · mid 49.45
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 47
  headline "MercadoLibre (MELI) Shares Under Pressure as Margin Compression Reaches 600 Bps Amid Investment Cycle"
WHY
  underlying -1.0%/+1.9%/+1.9% (favorable peak +2.9%); position move -1.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-25% · IV residual ~31% [inferred].
  convexity Γ·S = 3.86. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TDG-2026-04-21-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 1.00 · spread +0.0%
  greeks Δ-0.122 Γ0.0015 Θ-0.603 · IV 0.440 · mid 5.89
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.85) · RSI 47
  headline "TransDigm director Nicholas Howley sells $12.8m in stock as company prices $1.5B in new debt"
WHY
  underlying -1.5%/-3.3%/-4.8% (favorable peak +5.8%); position move +4.8%.
  decomp [first-order]: theta drag ~31% of premium / 3d · delta capture ~119% · IV residual ~-90% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE DECK-2026-05-04-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ-0.450 Γ0.0237 Θ-0.105 · IV 0.597 · mid 6.41
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 35
  headline "Deckers Outdoor Corporation Receives Consensus Recommendation of 'Hold' from Brokerages"
WHY
  underlying +0.9%/+6.4%/+5.2% (favorable peak +0.9%); position move -5.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-36% · IV residual ~39% [inferred].
  convexity Γ·S = 2.31. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TLN-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 22.00 · spread +0.0%
  greeks Δ-0.369 Γ0.0079 Θ-0.502 · IV 0.629 · mid 29.50
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 54
  headline "Talen Energy slips as investors weigh new debt financing and regulatory scrutiny tied to pending PJM gas-pl…"
WHY
  underlying -4.8%/-2.0%/-0.3% (favorable peak +5.2%); position move +0.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~1% · IV residual ~2% [inferred].
  convexity Γ·S = 2.74. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DUOL-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.393 Γ0.0235 Θ-0.149 · IV 0.617 · mid 5.96
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.60) · RSI 58
  headline "Duolingo Stock Stages Relief Rally After Post-Earnings Plunge to Multi-Year Lows"
WHY
  underlying +1.1%/+1.8%/-4.7% (favorable peak +4.8%); position move +4.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~35% · IV residual ~-29% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE EXPE-2026-04-28-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 25.00 · spread +0.0%
  greeks Δ-0.303 Γ0.0083 Θ-0.240 · IV 0.620 · mid 10.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 48
  headline "Booking Holdings lowers FY26 outlook to reflect Middle East conflict; travel peers slump"
WHY
  underlying +3.5%/+2.6%/+4.0% (favorable peak +3.6%); position move -4.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-29% · IV residual ~35% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APPF-2026-04-10-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.405 Γ0.0145 Θ-0.146 · IV 0.611 · mid 6.30
  overnight_score 3 · flow HEDGING · catalyst Technical Breakout (0.25) · RSI 25
  headline "AppFolio (APPF) Reaches New 12-Month Low Ahead of Q1 Earnings Date Announcement"
WHY
  underlying +3.6%/+3.8%/+8.0% (favorable peak +0.1%); position move -8.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-74% · IV residual ~79% [inferred].
  convexity Γ·S = 2.08. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE IRM-2026-04-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ-0.353 Γ0.0265 Θ-0.149 · IV 0.557 · mid 3.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 55
  headline "Iron Mountain (IRM) Slated to Release First-Quarter 2026 Results on April 30"
WHY
  underlying -0.1%/+1.6%/+11.7% (favorable peak +2.4%); position move -11.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-134% · IV residual ~144% [inferred].
  convexity Γ·S = 2.99. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VRT-2026-05-18-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ-0.462 Γ0.0057 Θ-0.454 · IV 0.719 · mid 30.67
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 48
  headline "Vertiv Shares Plummet as Investor Conference Highlights Valuation Risks Amid Yield Surge"
WHY
  underlying -5.0%/-7.1%/-4.8% (favorable peak +7.5%); position move +4.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~25% · IV residual ~-22% [inferred].
  convexity Γ·S = 1.94. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CAH-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ-0.520 Γ0.0225 Θ-0.079 · IV 0.275 · mid 9.37
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 32
  headline "Cardinal Health Lifts 2026 Outlook But Shares Fall on Revenue Miss and $184M Impairment"
WHY
  underlying +1.2%/+2.2%/+2.1% (favorable peak +0.5%); position move -2.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-23% · IV residual ~23% [inferred].
  convexity Γ·S = 4.33. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CLS-2026-05-15-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 0.79 · spread +0.0%
  greeks Δ-0.438 Γ0.0050 Θ-0.375 · IV 0.673 · mid 28.09
  overnight_score 2 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 45
  headline "Celestica Shares Slide as AI Infrastructure Spending Concerns Surface Amid Sector Rotation"
WHY
  underlying -4.4%/-5.4%/-3.4% (favorable peak +9.5%); position move +3.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~19% · IV residual ~-17% [inferred].
  convexity Γ·S = 1.78. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE NPO-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ-0.280 Γ0.0078 Θ-0.171 · IV 0.430 · mid 6.12
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 66
  headline "Enpro Reports First Quarter 2026 Results; Raises Full-Year Guidance"
WHY
  underlying +2.8%/+4.8%/+3.1% (favorable peak +0.5%); position move -3.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-43% · IV residual ~50% [inferred].
  convexity Γ·S = 2.34. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE STZ-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.585 Γ0.0319 Θ-0.065 · IV 0.256 · mid 6.60
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 41
  headline "Constellation Brands (STZ) Down 7.9% Since Last Earnings Report: Can It Rebound?"
WHY
  underlying -1.3%/-2.7%/-6.5% (favorable peak +7.2%); position move +6.5%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~88% · IV residual ~-87% [inferred].
  convexity Γ·S = 4.86. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ZS-2026-05-07-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 3.00 · spread +0.0%
  greeks Δ-0.297 Γ0.0182 Θ-0.223 · IV 0.635 · mid 7.30
  overnight_score 5 · flow HEDGING · catalyst Sector Rotation (0.85) · RSI 61
  headline "Zscaler stock surges 9% on Fortinet's earnings beat and sector-wide SaaS rally"
WHY
  underlying -0.4%/-2.6%/-4.3% (favorable peak +5.0%); position move +4.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~27% · IV residual ~-20% [inferred].
  convexity Γ·S = 2.78. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE WD-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ-0.322 Γ0.0429 Θ-0.037 · IV 0.467 · mid 2.20
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 69
  headline "Walker & Dunlop Q1 EPS crushes forecasts, driving stock gain amid surging transaction volumes"
WHY
  underlying +3.1%/+2.7%/+1.2% (favorable peak +2.5%); position move -1.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-9% · IV residual ~12% [inferred].
  convexity Γ·S = 2.28. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WGS-2026-05-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ-0.363 Γ0.0316 Θ-0.060 · IV 0.830 · mid 3.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.85) · RSI 40
  headline "Director Casdin Capital Acquires 500,000 Shares of GeneDx (WGS) Following Massive Guidance Reset"
WHY
  underlying +5.8%/+5.8%/+10.5% (favorable peak +1.8%); position move -10.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-49% · IV residual ~52% [inferred].
  convexity Γ·S = 1.41. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AEM-2026-04-20-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ-0.275 Γ0.0129 Θ-0.172 · IV 0.463 · mid 5.80
  overnight_score 4 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 55
  headline "AGNICO EAGLE TO CONSOLIDATE FINLAND'S CENTRAL LAPLAND GREENSTONE BELT IN THREE SEPARATE TRANSACTIONS"
WHY
  underlying -6.1%/-5.7%/-8.1% (favorable peak +9.5%); position move +8.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~83% · IV residual ~-76% [inferred].
  convexity Γ·S = 2.79. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE STZ-2026-05-27-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 35 · V/OI 33.00 · spread +0.0%
  greeks Δ-0.635 Γ0.0262 Θ-0.076 · IV 0.325 · mid 6.70
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 41
  headline "Constellation Brands (STZ) slides as investors weigh lingering growth concerns and recent capital-markets m…"
WHY
  underlying -1.1%/-3.4%/-5.2% (favorable peak +5.9%); position move +5.2%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~71% · IV residual ~-69% [inferred].
  convexity Γ·S = 3.76. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CAR-2026-04-22-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 6.67 · spread +0.0%
  greeks Δ-0.494 Γ0.0018 Θ-2.822 · IV 2.504 · mid 106.81
  overnight_score 6 · flow HEDGING · catalyst Secondary Offering (0.95) · RSI 60
  headline "Avis Budget Stock Tanking 47% After Record $850 Peak as ATM Offering and Earnings Shift Signal Squeeze End"
WHY
  underlying -48.4%/-54.0%/-57.9% (favorable peak +59.0%); position move +57.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~119% · IV residual ~-113% [inferred].
  convexity Γ·S = 0.79. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TEAM-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 0.96 · spread +0.0%
  greeks Δ-0.422 Γ0.0272 Θ-0.167 · IV 0.792 · mid 4.80
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 57
  headline "Atlassian shares under pressure following removal from Nasdaq-100 index"
WHY
  underlying -5.2%/-4.9%/+2.9% (favorable peak +8.0%); position move -2.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-22% · IV residual ~31% [inferred].
  convexity Γ·S = 2.32. exit TIMEOUT → realized -1%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SEZL-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 36 · V/OI 2.86 · spread +0.0%
  greeks Δ-0.509 Γ0.0250 Θ-0.084 · IV 0.521 · mid 7.20
  overnight_score 2 · flow HEDGING · catalyst Regulatory (0.75) · RSI 68
  headline "Court allows Sezzle's core antitrust claims against Shopify to proceed"
WHY
  underlying +2.8%/+3.8%/-1.0% (favorable peak +5.7%); position move +1.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~7% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.49. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE FISV-2026-05-08-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ-0.382 Γ0.0547 Θ-0.037 · IV 0.413 · mid 1.88
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 36
  headline "Fiserv Analysts Slash Price Targets as Organic Revenue Slump and Transformation Costs Weigh on Outlook"
WHY
  underlying -2.0%/-1.1%/-5.6% (favorable peak +6.0%); position move +5.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~63% · IV residual ~-58% [inferred].
  convexity Γ·S = 3.03. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TDG-2026-05-05-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 3.33 · spread +0.0%
  greeks Δ-0.444 Γ0.0034 Θ-0.576 · IV 0.280 · mid 35.17
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.88) · RSI 53
  headline "TransDigm Q2 2026 EPS of $9.85 beats estimates; full-year revenue guidance raised to $10.36B midpoint"
WHY
  underlying +3.5%/+4.3%/+2.0% (favorable peak -1.5%); position move -2.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-30% · IV residual ~34% [inferred].
  convexity Γ·S = 4.07. exit TIMEOUT → realized -1%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BLSH-2026-05-12-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ-0.451 Γ0.0532 Θ-0.154 · IV 1.082 · mid 2.91
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.90) · RSI 55
  headline "Bullish (BLSH) Scheduled for Q1 Earnings May 14 Amid Analyst Warnings of Slowing Trading Volumes"
WHY
  underlying -2.3%/-7.8%/-16.7% (favorable peak +17.1%); position move +16.7%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~111% · IV residual ~-95% [inferred].
  convexity Γ·S = 2.28. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RACE-2026-04-29-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 6.25 · spread +0.0%
  greeks Δ-0.532 Γ0.0113 Θ-0.442 · IV 0.503 · mid 16.50
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 41
  headline "Ferrari (RACE) Faces Earnings Skepticism as Analysts Warn of Potential 2026 Guidance Revisions"
WHY
  underlying +2.9%/+1.1%/+0.4% (favorable peak +0.1%); position move -0.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-4% · IV residual ~12% [inferred].
  convexity Γ·S = 3.80. exit TIMEOUT → realized -1%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ADP-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 0.48 · spread +0.1%
  greeks Δ-0.382 Γ0.0492 Θ-0.171 · IV 0.243 · mid 2.72
  overnight_score 7 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 58
  headline "ADP Beats Q3 Estimates, Raises FY26 Guidance and Announces $6 Billion Share Buyback"
WHY
  underlying +3.3%/+2.8%/+2.2% (favorable peak +0.6%); position move -2.2%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-63% · IV residual ~81% [inferred].
  convexity Γ·S = 10.19. exit TRAIL → realized -0%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WGS-2026-04-13-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ-0.416 Γ0.0258 Θ-0.167 · IV 1.130 · mid 5.88
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 37
  headline "GeneDx Stock Plunges 8.9% on Analyst Downgrades; Cathie Wood Buys the Dip"
WHY
  underlying +9.6%/+10.6%/+7.3% (favorable peak -1.0%); position move -7.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-31% · IV residual ~40% [inferred].
  convexity Γ·S = 1.58. exit TIMEOUT → realized -0%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RIOT-2026-04-30-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 12.27 · spread +0.0%
  greeks Δ-0.544 Γ0.1136 Θ-0.031 · IV 0.840 · mid 2.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 54
  headline "Riot Platforms Surges 7.7% on Q1 Revenue Beat and AMD Data Center Expansion Despite $500M Net Loss"
WHY
  underlying +7.3%/+8.4%/+18.0% (favorable peak -5.3%); position move -18.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-85% · IV residual ~89% [inferred].
  convexity Γ·S = 1.96. exit TRAIL → realized -0%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LULU-2026-05-06-S  ·  BEARISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ-0.434 Γ0.0469 Θ-0.185 · IV 0.413 · mid 3.41
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.40) · RSI 32
  headline "Lululemon shares edge higher, clawing back ground near 52-week lows amid CEO transition skepticism"
WHY
  underlying +1.2%/-0.7%/-4.3% (favorable peak +4.5%); position move +4.3%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~73% · IV residual ~-56% [inferred].
  convexity Γ·S = 6.20. exit TRAIL → realized +0%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```
