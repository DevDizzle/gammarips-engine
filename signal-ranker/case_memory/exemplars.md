# Picker case-memory — exemplars (injection block)

_Generated 2026-06-03 23:05Z by build_case_memory.py — curated subset of the full bull.md/bear.md library, bounded for prompt injection._

These are CLOSED past trades explained with hindsight, grouped by the lesson they teach. They are PRIORS for analogical reasoning about today's candidates — not predictions, and not proof of edge (single 2026-Q2 regime).

> Outcome = option PnL (`realized_ret>0`), NOT stock direction (`is_win`). A trade where the stock moved your way but the option lost is the canonical lesson.

---

## BULLISH exemplars

### LIVE (authoritative)

```
CASE ADI-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [live_ledger]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 23.93 · spread +0.0%
  greeks Δ0.277 Γ0.0068 Θ-0.247 · IV 0.406 · mid 7.87
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 51
  headline "Analog Devices Reports Record Q2 Results and $1.5B AI-Power Acquisition, Sparking Massive Price Target Hike…"
WHY
  underlying +5.8%/+5.0%/+5.5% (favorable peak +9.2%); position move +5.5%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~77% · IV residual ~-91% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized -23%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BBY-2026-05-18-B  ·  BULLISH  ·  WON  ·  [live_ledger]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 4.31 · spread +0.0%
  greeks Δ0.291 Γ0.0434 Θ-0.054 · IV 0.526 · mid 1.20
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 49
  headline "North Dakota State Investment Board Buys New Shares in Best Buy Co., Inc. $BBY"
WHY
  underlying +2.4%/+5.4%/+5.6% (favorable peak +6.1%); position move +5.6%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~79% · IV residual ~-51% [inferred].
  convexity Γ·S = 2.51. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PAAS-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [live_ledger]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 126.04 · spread +0.0%
  greeks Δ0.385 Γ0.0568 Θ-0.086 · IV 0.617 · mid 1.65
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 44
  headline "Pan American Silver Releases 2025 Sustainability Report"
WHY
  underlying +3.5%/+6.9%/+4.1% (favorable peak +7.0%); position move +4.1%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~51% · IV residual ~-37% [inferred].
  convexity Γ·S = 3.03. exit TRAIL → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

### REPRESENTATIVE PATTERNS (backtest)

_Directional miss — underlying went against the position.  (n=229 in corpus)_

```
CASE CLS-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.427 Γ0.0052 Θ-1.103 · IV 0.943 · mid 23.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 74
  headline "BMO Capital Markets Hikes Celestica (CLS) Price Target to $450 Ahead of Q1 Earnings"
WHY
  underlying +2.9%/-11.9%/-8.2% (favorable peak +3.2%); position move -8.2%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-63% · IV residual ~17% [inferred].
  convexity Γ·S = 2.14. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FDX-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 5.33 · spread +0.0%
  greeks Δ0.340 Γ0.0203 Θ-0.437 · IV 0.328 · mid 3.93
  overnight_score 3 · flow DIRECTIONAL · catalyst M&A (0.90) · RSI 52
  headline "FedEx Board Formally Approves Freight Spin-Off; Record Date Set for May 15"
WHY
  underlying -1.1%/-2.7%/-1.3% (favorable peak -0.7%); position move -1.3%.
  decomp [first-order]: theta drag ~33% of premium / 3d · delta capture ~-43% · IV residual ~17% [inferred].
  convexity Γ·S = 7.73. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SATS-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 15 · V/OI 12.00 · spread +0.0%
  greeks Δ0.680 Γ0.0197 Θ-0.222 · IV 0.623 · mid 8.13
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 68
  headline "SATS Stock Jumps: EchoStar's $11B SpaceX Exposure Sparks Retail IPO Proxy Frenzy"
WHY
  underlying -9.4%/-12.4%/-13.2% (favorable peak -0.2%); position move -13.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-156% · IV residual ~104% [inferred].
  convexity Γ·S = 2.79. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

_Modest favorable move, but enough to finish green net of spread + theta.  (n=205 in corpus)_

```
CASE BE-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 13 · V/OI 2.00 · spread +0.0%
  greeks Δ0.267 Γ0.0056 Θ-0.739 · IV 1.126 · mid 10.43
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 59
  headline "Bloom Energy CAO Sells Shares as Stock Pulls Back from AI-Driven Record Highs"
WHY
  underlying -6.2%/-5.3%/+2.3% (favorable peak +6.2%); position move +2.3%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~16% · IV residual ~85% [inferred].
  convexity Γ·S = 1.54. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BX-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.324 Γ0.0247 Θ-0.071 · IV 0.369 · mid 3.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 61
  headline "Oppenheimer Upgrades Blackstone to Outperform, Calling It the Premier Franchise at a Bargain Price"
WHY
  underlying +3.7%/+6.9%/+5.2% (favorable peak +9.0%); position move +5.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~68% · IV residual ~19% [inferred].
  convexity Γ·S = 3.00. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAMT-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 13 · V/OI 0.34 · spread +0.0%
  greeks Δ0.132 Γ0.0069 Θ-0.244 · IV 0.849 · mid 2.55
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 55
  headline "Camtek Scheduled to Release Q1 2026 Results on May 12; Institutional Bulls Position for AI Growth"
WHY
  underlying -2.1%/+5.7%/+8.5% (favorable peak +10.0%); position move +8.5%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~82% · IV residual ~26% [inferred].
  convexity Γ·S = 1.29. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

_TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.  (n=123 in corpus)_

```
CASE ADI-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 40.00 · spread +0.0%
  greeks Δ0.320 Γ0.0289 Θ-0.262 · IV 0.201 · mid 2.55
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 75
  headline "Morgan Stanley Flags ADI as Top Pick as Chip Cycle Accelerates 'Faster Than Expected'"
WHY
  underlying +5.9%/+4.8%/+2.9% (favorable peak +7.1%); position move +2.9%.
  decomp [first-order]: theta drag ~31% of premium / 3d · delta capture ~140% · IV residual ~-169% [inferred].
  convexity Γ·S = 11.03. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE APP-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.400 Γ0.0040 Θ-1.115 · IV 0.943 · mid 22.80
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 58
  headline "AppLovin Stock Is Moving Higher Amid Q1 Earnings Tomorrow"
WHY
  underlying +0.7%/-1.3%/+5.0% (favorable peak +7.9%); position move +5.0%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~42% · IV residual ~-87% [inferred].
  convexity Γ·S = 1.89. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PGR-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.279 Γ0.0414 Θ-0.151 · IV 0.259 · mid 1.45
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 51
  headline "Progressive's Q1 Earnings Beat Estimates on Higher Premiums; Combined Ratio Hits Stellar 87.4%"
WHY
  underlying +1.1%/+0.7%/+1.3% (favorable peak +2.5%); position move +1.3%.
  decomp [first-order]: theta drag ~31% of premium / 3d · delta capture ~49% · IV residual ~-78% [inferred].
  convexity Γ·S = 8.34. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

_Was wrong on day 1; low theta + convexity let it win late on a single sharp move.  (n=106 in corpus)_

```
CASE U-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.377 Γ0.0635 Θ-0.052 · IV 0.942 · mid 1.33
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 65
  headline "Unity and Meta Extend Multi-Year Partnership to Power Next-Generation VR Experiences"
WHY
  underlying -5.8%/+0.7%/+3.2% (favorable peak +3.9%); position move +3.2%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~23% · IV residual ~68% [inferred].
  convexity Γ·S = 1.64. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ALB-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 0.01 · spread +0.1%
  greeks Δ0.352 Γ0.0083 Θ-0.196 · IV 0.661 · mid 9.80
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 59
  headline "Albemarle stock jumps after Q1 earnings beat highlights stronger lithium pricing and cash flow"
WHY
  underlying -1.1%/+1.8%/+4.5% (favorable peak +13.4%); position move +4.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~31% · IV residual ~55% [inferred].
  convexity Γ·S = 1.62. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE JBHT-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 0.30 · spread +0.0%
  greeks Δ0.380 Γ0.0129 Θ-0.161 · IV 0.394 · mid 8.60
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 52
  headline "Evercore ISI Lifts J.B. Hunt Transport Services Price Target to $248 From $239"
WHY
  underlying -1.6%/-1.2%/+5.8% (favorable peak +6.8%); position move +5.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~61% · IV residual ~24% [inferred].
  convexity Γ·S = 3.09. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

_Chop: underlying never moved enough either way; theta bled it out over the hold.  (n=92 in corpus)_

```
CASE CW-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 1.67 · spread +0.0%
  greeks Δ0.415 Γ0.0057 Θ-1.408 · IV 0.583 · mid 20.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 55
  headline "Curtiss-Wright Reports First Quarter 2026 Financial Results and Raises Full-Year 2026 Guidance"
WHY
  underlying +1.9%/-0.6%/+0.0% (favorable peak +2.9%); position move +0.0%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~1% · IV residual ~-36% [inferred].
  convexity Γ·S = 4.16. exit TIMEOUT → realized -57%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE XOM-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI 7.50 · spread +0.0%
  greeks Δ0.140 Γ0.0108 Θ-0.065 · IV 0.428 · mid 0.42
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 53
  headline "TotalEnergies Blowout Q1 Results and $1.5B Buyback Lift ExxonMobil Ahead of Friday Earnings"
WHY
  underlying -0.2%/-1.2%/-0.6% (favorable peak +0.7%); position move -0.6%.
  decomp [first-order]: theta drag ~46% of premium / 3d · delta capture ~-33% · IV residual ~25% [inferred].
  convexity Γ·S = 1.67. exit TIMEOUT → realized -54%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CIEN-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 1.78 · spread +0.0%
  greeks Δ0.286 Γ0.0052 Θ-1.462 · IV 0.767 · mid 15.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 62
  headline "Ciena partners with Cirion for Network-as-a-Service in Latin America to address AI network traffic bottlene…"
WHY
  underlying -0.6%/+2.6%/-0.9% (favorable peak +3.1%); position move -0.9%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~-10% · IV residual ~-15% [inferred].
  convexity Γ·S = 3.03. exit TIMEOUT → realized -54%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

_Large favorable move cleared the +80% target net of decay.  (n=72 in corpus)_

```
CASE MU-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 6.40 · spread +0.1%
  greeks Δ0.290 Γ0.0028 Θ-0.625 · IV 0.737 · mid 19.56
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.95) · RSI 72
  headline "D.A. Davidson Initiates Micron with $1,000 Price Target as AI Memory Supercycle Accelerates"
WHY
  underlying +6.3%/+18.1%/+22.9% (favorable peak +23.1%); position move +22.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~184% · IV residual ~-95% [inferred].
  convexity Γ·S = 1.53. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AAOI-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 29 · V/OI 2.29 · spread +0.0%
  greeks Δ0.401 Γ0.0061 Θ-0.424 · IV 1.419 · mid 13.70
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.90) · RSI 58
  headline "AOI Receives First Volume Order of 1.6T Data Center Transceivers from Major Hyperscale Customer Totaling Ov…"
WHY
  underlying +7.5%/+20.1%/+13.2% (favorable peak +25.5%); position move +13.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~59% · IV residual ~30% [inferred].
  convexity Γ·S = 0.93. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE ALAB-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.367 Γ0.0067 Θ-0.355 · IV 0.900 · mid 12.32
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 68
  headline "Astera Labs Posts Strong Q1 Beat and Raises Guidance on Robust AI Infrastructure Demand"
WHY
  underlying +13.3%/+33.4%/+38.2% (favorable peak +38.4%); position move +38.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~245% · IV residual ~-157% [inferred].
  convexity Γ·S = 1.45. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

_Fast convex move outran a short-DTE theta cliff — speed was the edge.  (n=14 in corpus)_

```
CASE STX-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 15.50 · spread +0.0%
  greeks Δ0.364 Γ0.0039 Θ-1.733 · IV 0.944 · mid 22.92
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.95) · RSI 77
  headline "Bank of America Hikes Seagate (STX) Price Target to $700 Citing Structural AI Storage Demand"
WHY
  underlying -2.8%/+8.0%/+13.1% (favorable peak +17.0%); position move +13.1%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~124% · IV residual ~-21% [inferred].
  convexity Γ·S = 2.32. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE AAOI-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 7 · V/OI n/a · spread +0.0%
  greeks Δ0.370 Γ0.0121 Θ-0.779 · IV 1.367 · mid 4.98
  overnight_score 8 · flow DIRECTIONAL · catalyst Short Squeeze (0.85) · RSI 70
  headline "AAOI Stock Eyes Ninth Straight Gain Amid Data Center Boom, Retail Frenzy Builds"
WHY
  underlying +1.3%/+3.9%/-4.3% (favorable peak +10.2%); position move -4.3%.
  decomp [first-order]: theta drag ~47% of premium / 3d · delta capture ~-50% · IV residual ~177% [inferred].
  convexity Γ·S = 1.90. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE CAT-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 5.76 · spread +0.1%
  greeks Δ0.499 Γ0.0056 Θ-1.518 · IV 0.537 · mid 26.77
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 65
  headline "Caterpillar (CAT) Positioned for Long-Term Growth as Power Demand from Data Centers Surges Ahead of Q1 Earn…"
WHY
  underlying -1.0%/+8.8%/+8.8% (favorable peak +10.7%); position move +8.8%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~134% · IV residual ~-37% [inferred].
  convexity Γ·S = 4.57. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

_Lost to decay with no decisive underlying move.  (n=2 in corpus)_

```
CASE LQDA-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 94.44 · spread +0.1%
  greeks Δ0.532 Γ0.0685 Θ-0.156 · IV 0.649 · mid 2.31
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 83
  headline "Liquidia (LQDA) Tests 52-Week Highs as Analysts Raise Targets Following Robust Yutrepia Sales"
WHY
  underlying -1.6%/-3.0%/+0.1% (favorable peak +2.4%); position move +0.1%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~1% · IV residual ~-41% [inferred].
  convexity Γ·S = 4.25. exit STOP → realized -60%.
TAKEAWAY: Lost to decay with no decisive underlying move.
```

```
CASE ETN-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 1.38 · spread +0.1%
  greeks Δ0.434 Γ0.0110 Θ-0.527 · IV 0.434 · mid 10.79
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 65
  headline "Eaton Stock Just Hit a New High; The May 5 Earnings Test Is Bigger Than Usual"
WHY
  underlying -0.7%/-3.5%/-1.0% (favorable peak +2.2%); position move -1.0%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-17% · IV residual ~-29% [inferred].
  convexity Γ·S = 4.67. exit STOP → realized -60%.
TAKEAWAY: Lost to decay with no decisive underlying move.
```

---

## BEARISH exemplars

### LIVE (authoritative)

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

### REPRESENTATIVE PATTERNS (backtest)

_Directional miss — underlying went against the position.  (n=233 in corpus)_

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

_Modest favorable move, but enough to finish green net of spread + theta.  (n=84 in corpus)_

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

_Was wrong on day 1; low theta + convexity let it win late on a single sharp move.  (n=73 in corpus)_

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

_TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.  (n=71 in corpus)_

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

_Chop: underlying never moved enough either way; theta bled it out over the hold.  (n=51 in corpus)_

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

_Large favorable move cleared the +80% target net of decay.  (n=11 in corpus)_

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

_Lost to decay with no decisive underlying move.  (n=3 in corpus)_

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

_Fast convex move outran a short-DTE theta cliff — speed was the edge.  (n=1 in corpus)_

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
