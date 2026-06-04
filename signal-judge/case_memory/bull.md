# BULLISH case-memory

_Generated 2026-06-03 23:05Z by build_case_memory.py — DO NOT hand-edit; regenerate._

**Corpus:** 846 closed bullish trades · 398 WON / 448 LOST · mean option return +4.1% · 3 live / 843 backtest.

> Backtest cases span 2026-04-10 → 2026-06-01 — a single 2026-Q2 war-chop regime (vix3m ~20-21). Treat distilled PATTERNS as signal and individual case outcomes as anecdote. Live cases supersede backtest on the same contract.

> Outcome = realized option PnL (`realized_ret>0`), NOT `is_win` (stock direction). They disagree ~44% of the time — the gap is the lesson.

---

## LIVE (V5.4 ledger — authoritative)  (3)

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

---

## BACKTEST · WON  (397)

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
CASE APLD-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.333 Γ0.0497 Θ-0.076 · IV 1.036 · mid 1.33
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 61
  headline "Needham Reaffirms Buy Rating on Applied Digital as CoreWeave Lease Adjustments Lower Capital Costs"
WHY
  underlying -2.7%/+0.7%/+12.9% (favorable peak +15.8%); position move +12.9%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~104% · IV residual ~-7% [inferred].
  convexity Γ·S = 1.60. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE APT-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 21 · V/OI 1.00 · spread +0.0%
  greeks Δ0.323 Γ0.2260 Θ-0.013 · IV 1.008 · mid 0.05
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 84
  headline "Alpha Pro Tech (APT) Stock Hits 52-Week High as Volume Surges Ahead of Q1 Earnings"
WHY
  underlying -0.6%/+2.5%/-2.0% (favorable peak +15.7%); position move -2.0%.
  decomp [first-order]: theta drag ~80% of premium / 3d · delta capture ~-84% · IV residual ~244% [inferred].
  convexity Γ·S = 1.46. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AXTI-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 15 · V/OI 8.83 · spread +0.0%
  greeks Δ0.421 Γ0.0160 Θ-0.318 · IV 1.611 · mid 6.90
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 54
  headline "Investors position ahead of AXT's Q1 2026 earnings report as AI demand fuels substrate growth"
WHY
  underlying +11.5%/+35.1%/+49.1% (favorable peak +50.6%); position move +49.1%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~213% · IV residual ~-119% [inferred].
  convexity Γ·S = 1.14. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

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

```
CASE CRCL-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.341 Γ0.0130 Θ-0.242 · IV 1.028 · mid 7.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 57
  headline "Circle (CRCL) Slated to Report Q1 Earnings May 11 Amid Bullish Options Surge and Regulatory Clarity"
WHY
  underlying +0.4%/+16.3%/+9.2% (favorable peak +23.6%); position move +9.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~45% · IV residual ~44% [inferred].
  convexity Γ·S = 1.48. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE DELL-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 42 · V/OI n/a · spread +0.1%
  greeks Δ0.296 Γ0.0087 Θ-0.166 · IV 0.609 · mid 6.43
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.75) · RSI 65
  headline "Evercore ISI Highlights Speculative Reports of Nvidia Negotiating Acquisition of Large PC Firm; Dell Shares…"
WHY
  underlying +1.8%/+5.8%/+10.0% (favorable peak +11.0%); position move +10.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~89% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.68. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ETN-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 3.43 · spread +0.0%
  greeks Δ0.554 Γ0.0154 Θ-0.599 · IV 0.397 · mid 10.47
  overnight_score 4 · flow HEDGING · catalyst Guidance Cut (0.85) · RSI 49
  headline "Eaton (ETN) Is Down 7.8% After Raising 2026 Guidance Amid Margin Pressure and AI Bet"
WHY
  underlying -5.5%/-4.7%/-0.6% (favorable peak -0.1%); position move -0.6%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-13% · IV residual ~110% [inferred].
  convexity Γ·S = 6.49. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIX-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 15.69 · spread +0.1%
  greeks Δ0.313 Γ0.0018 Θ-2.404 · IV 0.526 · mid 40.08
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 69
  headline "Comfort Systems USA (FIX) Hits New Highs as AI Data Center Backlog Surges to $12.5 Billion"
WHY
  underlying +1.5%/+2.8%/+6.9% (favorable peak +8.9%); position move +6.9%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~99% · IV residual ~-1% [inferred].
  convexity Γ·S = 3.34. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
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

```
CASE LUV-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.341 Γ0.0599 Θ-0.051 · IV 0.590 · mid 1.27
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.80) · RSI 54
  headline "Southwest Airlines (LUV) projected to post Q1 2026 results on April 22nd amid rising airline M&A speculation"
WHY
  underlying -2.6%/+2.4%/+0.3% (favorable peak +7.7%); position move +0.3%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~3% · IV residual ~89% [inferred].
  convexity Γ·S = 2.50. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MAR-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.291 Γ0.0163 Θ-0.225 · IV 0.269 · mid 3.30
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.70) · RSI 71
  headline "Marriott Bonvoy and Singapore Airlines team up for loyalty crossover"
WHY
  underlying -0.8%/-1.2%/+3.1% (favorable peak +3.5%); position move +3.1%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~99% · IV residual ~2% [inferred].
  convexity Γ·S = 5.97. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MPWR-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.325 Γ0.0016 Θ-1.498 · IV 0.590 · mid 45.95
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 74
  headline "Stifel and KeyBanc Raise MPWR Price Targets to $1,500 on AI-Driven Enterprise Data Growth"
WHY
  underlying +4.7%/+6.3%/+8.9% (favorable peak +10.3%); position move +8.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~88% · IV residual ~1% [inferred].
  convexity Γ·S = 2.18. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MPWR-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 0.30 · spread +0.0%
  greeks Δ0.371 Γ0.0014 Θ-1.815 · IV 0.615 · mid 58.20
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 54
  headline "Monolithic Power Systems Rebounds 4.5% as NVIDIA Earnings Validate AI Power Management Demand"
WHY
  underlying +0.5%/+2.4%/+7.1% (favorable peak +10.4%); position move +7.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~70% · IV residual ~19% [inferred].
  convexity Γ·S = 2.24. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NEM-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 8.05 · spread +0.1%
  greeks Δ0.325 Γ0.0309 Θ-0.243 · IV 0.675 · mid 2.59
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 48
  headline "Newmont (NEM) Q1 preview: Analysts highlight stronger portfolio and cash value focus ahead of earnings"
WHY
  underlying -0.7%/+7.9%/+3.8% (favorable peak +8.0%); position move +3.8%.
  decomp [first-order]: theta drag ~28% of premium / 3d · delta capture ~53% · IV residual ~55% [inferred].
  convexity Γ·S = 3.45. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NET-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.265 Γ0.0065 Θ-0.210 · IV 0.696 · mid 6.93
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 58
  headline "Oppenheimer Projects Q1 Earnings Beat for Cloudflare, Reiterates $300 Price Target"
WHY
  underlying +3.1%/+12.4%/+14.3% (favorable peak +15.4%); position move +14.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~119% · IV residual ~-30% [inferred].
  convexity Γ·S = 1.41. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE NVTS-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 29.00 · spread +0.0%
  greeks Δ0.332 Γ0.0630 Θ-0.030 · IV 1.204 · mid 1.30
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 63
  headline "Navitas Semiconductor Reports Q1 Revenue Surprise and AI Infrastructure Momentum Amidst Post-Earnings Profi…"
WHY
  underlying +15.3%/+43.4%/+21.9% (favorable peak +50.9%); position move +21.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~88% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.00. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE OSCR-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 16 · V/OI 32.50 · spread +0.0%
  greeks Δ0.177 Γ0.0824 Θ-0.025 · IV 0.824 · mid 0.41
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 83
  headline "Oscar Health (OSCR) Shares Surge as UBS Hikes Price Target Following Record Q1 Profitability"
WHY
  underlying +10.6%/+16.3%/+18.8% (favorable peak +18.8%); position move +18.8%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~146% · IV residual ~-47% [inferred].
  convexity Γ·S = 1.48. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE PANW-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.281 Γ0.0087 Θ-0.312 · IV 0.640 · mid 6.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.80) · RSI 71
  headline "Palo Alto and CrowdStrike Stocks Fall on Cybersecurity Gloom"
WHY
  underlying +3.7%/+13.4%/+20.9% (favorable peak +21.9%); position move +20.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~228% · IV residual ~-133% [inferred].
  convexity Γ·S = 2.17. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE RCL-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI n/a · spread +0.1%
  greeks Δ0.338 Γ0.0147 Θ-0.315 · IV 0.479 · mid 2.75
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 47
  headline "Royal Caribbean Group Q1 Earnings Beat and Guidance Raise Fuel Analyst Price Target Hikes to $350+"
WHY
  underlying -1.6%/+2.8%/+5.7% (favorable peak +8.1%); position move +5.7%.
  decomp [first-order]: theta drag ~34% of premium / 3d · delta capture ~182% · IV residual ~-68% [inferred].
  convexity Γ·S = 3.82. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SNDK-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.309 Γ0.0010 Θ-1.603 · IV 0.917 · mid 45.00
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 74
  headline "SanDisk (SNDK) Stock Gains 8.3% on Market-Beating Q3 Results and Robust AI-Driven Outlook"
WHY
  underlying +5.8%/+18.5%/+18.8% (favorable peak +21.3%); position move +18.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~153% · IV residual ~-62% [inferred].
  convexity Γ·S = 1.15. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

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
CASE TRGP-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI 0.02 · spread +0.0%
  greeks Δ0.422 Γ0.0154 Θ-0.138 · IV 0.315 · mid 8.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 57
  headline "Targa Resources Lifts 2026 Outlook Amid Record Q1 Permian Volumes and 25% Dividend Hike"
WHY
  underlying +0.8%/+4.0%/+5.6% (favorable peak +5.9%); position move +5.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~74% · IV residual ~11% [inferred].
  convexity Γ·S = 3.89. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE UPS-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 3.00 · spread +0.0%
  greeks Δ0.489 Γ0.0430 Θ-0.047 · IV 0.306 · mid 3.20
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 46
  headline "ProShare Advisors LLC and Banque Cantonale Vaudoise Lift Stakes in UPS Amid Sector Volatility"
WHY
  underlying -0.6%/+2.2%/+3.1% (favorable peak +3.8%); position move +3.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~47% · IV residual ~37% [inferred].
  convexity Γ·S = 4.25. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WDC-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI 17.00 · spread +0.0%
  greeks Δ0.256 Γ0.0027 Θ-0.538 · IV 0.788 · mid 15.25
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 76
  headline "Western Digital Share Swap Highlights Separation Progress and AI-Driven Valuation Gap"
WHY
  underlying -4.0%/-0.7%/+6.8% (favorable peak +8.7%); position move +6.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~55% · IV residual ~36% [inferred].
  convexity Γ·S = 1.32. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WOLF-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI 1.28 · spread +0.1%
  greeks Δ0.414 Γ0.0332 Θ-0.083 · IV 1.433 · mid 1.73
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 63
  headline "Wolfspeed Just Got a $698 Million Lifeline—Here's Why That Changes Everything"
WHY
  underlying +24.5%/+21.7%/+24.0% (favorable peak +36.3%); position move +24.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~170% · IV residual ~-76% [inferred].
  convexity Γ·S = 0.98. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE WOLF-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 7.00 · spread +0.0%
  greeks Δ0.403 Γ0.0237 Θ-0.191 · IV 2.439 · mid 4.88
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 79
  headline "Wolfspeed Shares Surge as Debt Refinancing and AI Pivot Offset Massive Q3 Earnings Miss"
WHY
  underlying +17.6%/+23.3%/+27.2% (favorable peak +39.2%); position move +27.2%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~82% · IV residual ~9% [inferred].
  convexity Γ·S = 0.87. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE WULF-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI 6.50 · spread +0.1%
  greeks Δ0.687 Γ0.0966 Θ-0.070 · IV 1.089 · mid 2.04
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 62
  headline "Morgan Stanley Raises TeraWulf Target to $41.50 Citing AI Data Center Pivot"
WHY
  underlying -3.7%/+4.5%/+2.5% (favorable peak +8.8%); position move +2.5%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~17% · IV residual ~73% [inferred].
  convexity Γ·S = 2.01. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE STRL-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 0.98 · spread +0.1%
  greeks Δ0.308 Γ0.0041 Θ-1.044 · IV 0.830 · mid 12.52
  overnight_score 4 · flow MIXED · catalyst — (—) · RSI 64
WHY
  underlying +3.3%/+2.7%/+56.3% (favorable peak +56.6%); position move +56.3%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~715% · IV residual ~-610% [inferred].
  convexity Γ·S = 2.11. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
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
CASE ALB-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 0.42 · spread +0.0%
  greeks Δ0.311 Γ0.0114 Θ-0.315 · IV 0.740 · mid 7.17
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 52
  headline "Albemarle (ALB) Q1 2026 Preview: EPS Est. $1.31, Reports May 6"
WHY
  underlying +2.2%/+1.0%/+4.0% (favorable peak +15.9%); position move +4.0%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~33% · IV residual ~60% [inferred].
  convexity Γ·S = 2.17. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AMAT-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 2.00 · spread +0.0%
  greeks Δ0.308 Γ0.0050 Θ-0.372 · IV 0.595 · mid 14.60
  overnight_score 4 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 53
  headline "Applied Materials Announces Agreement to Acquire NEXX Business from ASMPT to Accelerate AI Packaging Roadmap"
WHY
  underlying +0.6%/+5.6%/+10.2% (favorable peak +11.2%); position move +10.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~83% · IV residual ~4% [inferred].
  convexity Γ·S = 1.93. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AXP-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.1%
  greeks Δ0.300 Γ0.0152 Θ-0.298 · IV 0.377 · mid 4.58
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 54
  headline "Berkshire Hathaway's American Express & Visa: 2026 Analysis of Price Declines and Long-Term Strength"
WHY
  underlying +3.3%/+4.3%/+5.0% (favorable peak +6.0%); position move +5.0%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~102% · IV residual ~-2% [inferred].
  convexity Γ·S = 4.76. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BNL-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 0.99 · spread +0.0%
  greeks Δ0.259 Γ0.1131 Θ-0.017 · IV 0.517 · mid 0.13
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 68
  headline "Broadstone Net Lease joins S&P SmallCap 600, boosting institutional visibility ahead of earnings"
WHY
  underlying -0.4%/-1.1%/-2.5% (favorable peak +0.6%); position move -2.5%.
  decomp [first-order]: theta drag ~39% of premium / 3d · delta capture ~-102% · IV residual ~221% [inferred].
  convexity Γ·S = 2.30. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAR-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 20 · V/OI 11.00 · spread +0.0%
  greeks Δ0.423 Γ0.0017 Θ-2.220 · IV 1.953 · mid 52.14
  overnight_score 6 · flow MECHANICAL · catalyst Short Squeeze (0.85) · RSI 93
  headline "CAR Stock Rockets As Travel Turmoil Fuels Avis Budget Rally; Short Squeeze Intensifies"
WHY
  underlying +23.3%/+44.6%/-10.1% (favorable peak +71.6%); position move -10.1%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-41% · IV residual ~133% [inferred].
  convexity Γ·S = 0.85. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
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

```
CASE CDNS-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 22 · V/OI 4.00 · spread +0.1%
  greeks Δ0.146 Γ0.0046 Θ-0.258 · IV 0.608 · mid 3.06
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 71
  headline "Needham & Company LLC Raises Cadence Design Systems (NASDAQ:CDNS) Price Target to $400.00"
WHY
  underlying -5.2%/+0.4%/+1.5% (favorable peak +2.0%); position move +1.5%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~23% · IV residual ~82% [inferred].
  convexity Γ·S = 1.54. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CIEN-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 5.33 · spread +0.0%
  greeks Δ0.380 Γ0.0030 Θ-1.407 · IV 1.105 · mid 30.60
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 54
  headline "Ciena price target raised to $658 from $345 at Citi ahead of Q2 results"
WHY
  underlying +3.3%/+5.8%/+12.0% (favorable peak +12.5%); position move +12.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~78% · IV residual ~16% [inferred].
  convexity Γ·S = 1.57. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CME-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ0.336 Γ0.0196 Θ-0.097 · IV 0.216 · mid 4.45
  overnight_score 2 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 36
  headline "CME Group Expands Equity Index Dividend Suite Effective May 11, 2026"
WHY
  underlying +0.5%/+1.6%/+5.6% (favorable peak +5.9%); position move +5.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~120% · IV residual ~-33% [inferred].
  convexity Γ·S = 5.53. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CMI-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 27 · V/OI 0.50 · spread +0.1%
  greeks Δ0.062 Γ0.0016 Θ-0.166 · IV 0.422 · mid 4.35
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 45
  headline "Cummins Lifts 2026 Outlook on Power Systems Strength at Analyst Day"
WHY
  underlying +0.1%/+4.7%/+4.6% (favorable peak +5.5%); position move +4.6%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~41% · IV residual ~50% [inferred].
  convexity Γ·S = 1.05. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE COHR-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.362 Γ0.0084 Θ-0.881 · IV 0.879 · mid 9.70
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 67
  headline "Coherent (COHR) Advances Silicon Carbide Tech for 10kV AI Datacenter Applications; JPMorgan Raises PT to $300"
WHY
  underlying -1.7%/+4.7%/+10.1% (favorable peak +10.1%); position move +10.1%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~118% · IV residual ~-11% [inferred].
  convexity Γ·S = 2.64. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE CRCL-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ0.427 Γ0.0155 Θ-0.250 · IV 0.928 · mid 6.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 57
  headline "Circle positioning USDC as 'native currency' for Autonomous AI Agents ahead of Q1 earnings"
WHY
  underlying +15.9%/+8.8%/+11.3% (favorable peak +23.2%); position move +11.3%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~92% · IV residual ~1% [inferred].
  convexity Γ·S = 1.76. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CRWD-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.286 Γ0.0066 Θ-0.510 · IV 0.499 · mid 8.22
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 64
  headline "CrowdStrike Integrates Anthropic's Claude Opus 4.7 AI Model Directly Across Falcon Security Platform"
WHY
  underlying +1.6%/-0.2%/+7.8% (favorable peak +8.0%); position move +7.8%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~127% · IV residual ~-29% [inferred].
  convexity Γ·S = 3.11. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CVNA-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.477 Γ0.0327 Θ-0.088 · IV 0.672 · mid 2.99
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 35
  headline "Carvana (CVNA) Is Down 7.1% After Expanding Into Stellantis Dealerships With Record New-Car Sales"
WHY
  underlying -0.8%/+5.2%/+8.1% (favorable peak +13.2%); position move +8.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~84% · IV residual ~5% [inferred].
  convexity Γ·S = 2.12. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CVS-2026-04-24-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.311 Γ0.0378 Θ-0.039 · IV 0.358 · mid 1.70
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.30) · RSI 55
  headline "CVS Health to hold first quarter 2026 earnings conference call on May 6"
WHY
  underlying +0.5%/+3.9%/+7.6% (favorable peak +7.7%); position move +7.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~109% · IV residual ~-22% [inferred].
  convexity Γ·S = 2.94. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DLR-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.363 Γ0.0252 Θ-0.296 · IV 0.476 · mid 3.67
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 77
  headline "Digital Realty Trust (NYSE:DLR) Hits New 12-Month High After Analyst Upgrade"
WHY
  underlying -0.1%/+1.7%/+4.0% (favorable peak +4.3%); position move +4.0%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~77% · IV residual ~27% [inferred].
  convexity Γ·S = 4.94. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DOCN-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 40.41 · spread +0.0%
  greeks Δ0.332 Γ0.0172 Θ-0.441 · IV 1.397 · mid 3.85
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 61
  headline "DigitalOcean Unveils AI-Native Cloud Stack for Production Agentic Workloads Ahead of Q1 Earnings"
WHY
  underlying -0.5%/+6.1%/+12.3% (favorable peak +12.7%); position move +12.3%.
  decomp [first-order]: theta drag ~34% of premium / 3d · delta capture ~103% · IV residual ~11% [inferred].
  convexity Γ·S = 1.67. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE FTNT-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 4.67 · spread +0.0%
  greeks Δ0.382 Γ0.0543 Θ-0.146 · IV 0.384 · mid 2.24
  overnight_score 2 · flow HEDGING · catalyst Guidance Raise (0.90) · RSI 81
  headline "Fortinet (FTNT) Sets New 1-Year High After NVIDIA AI Integration and Guidance Raise"
WHY
  underlying +3.4%/+7.0%/+7.8% (favorable peak +8.3%); position move +7.8%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~152% · IV residual ~-52% [inferred].
  convexity Γ·S = 6.18. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FTNT-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.411 Γ0.0366 Θ-0.090 · IV 0.357 · mid 3.00
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 85
  headline "Fortinet shares hit new 52-week high as analysts raise price targets following blowout Q1 results and guida…"
WHY
  underlying -1.4%/+1.9%/+5.6% (favorable peak +5.7%); position move +5.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~88% · IV residual ~1% [inferred].
  convexity Γ·S = 4.22. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HPE-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.360 Γ0.1043 Θ-0.019 · IV 0.448 · mid 0.65
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 66
  headline "HPE Jumps as Goldman Sachs Raises Price Target to $30 and Deepens NVIDIA AI Partnership"
WHY
  underlying +2.1%/+7.4%/+11.1% (favorable peak +14.4%); position move +11.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~159% · IV residual ~-70% [inferred].
  convexity Γ·S = 2.70. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE HUT-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 15.56 · spread +0.0%
  greeks Δ0.433 Γ0.0256 Θ-0.226 · IV 1.042 · mid 4.65
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 64
  headline "Hut 8 Closes $3.25 Billion Investment-Grade Financing for Google-Linked AI Data Center Project"
WHY
  underlying +1.4%/+4.6%/+41.5% (favorable peak +44.6%); position move +41.5%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~298% · IV residual ~-203% [inferred].
  convexity Γ·S = 1.97. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE IONQ-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 11.00 · spread +0.1%
  greeks Δ0.410 Γ0.0272 Θ-0.082 · IV 1.034 · mid 3.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 63
  headline "IonQ and Florida LambdaRail Deploy Live Quantum-Safe Network Corridor as Commercialization Scales"
WHY
  underlying +2.4%/+1.4%/+6.4% (favorable peak +8.9%); position move +6.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~34% · IV residual ~53% [inferred].
  convexity Γ·S = 1.23. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE KMI-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 150.00 · spread +0.0%
  greeks Δ0.141 Γ0.0959 Θ-0.008 · IV 0.248 · mid 0.16
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 51
  headline "Mexico Plans $8 Billion in Gas Pipelines to Boost Power Sector, Increasing US Import Capacity"
WHY
  underlying +0.6%/+1.7%/+3.6% (favorable peak +3.8%); position move +3.6%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~101% · IV residual ~-5% [inferred].
  convexity Γ·S = 3.09. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LEN-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 4.00 · spread +0.0%
  greeks Δ0.265 Γ0.0428 Θ-0.082 · IV 0.429 · mid 0.98
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 48
  headline "Lennar Edges Higher as Surge in Buyer Demand Provides Tailwinds for Homebuilders"
WHY
  underlying +1.7%/+1.8%/+2.3% (favorable peak +3.6%); position move +2.3%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~53% · IV residual ~52% [inferred].
  convexity Γ·S = 3.74. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LUV-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.1%
  greeks Δ0.324 Γ0.0613 Θ-0.039 · IV 0.539 · mid 1.17
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 46
  headline "Southwest Airlines, Colliers International, and More Stocks See Action From Activist Investors"
WHY
  underlying -0.3%/+4.3%/+5.4% (favorable peak +7.2%); position move +5.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~59% · IV residual ~31% [inferred].
  convexity Γ·S = 2.43. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MCHP-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 28 · V/OI 1.76 · spread +0.1%
  greeks Δ0.655 Γ0.0286 Θ-0.086 · IV 0.493 · mid 7.10
  overnight_score 8 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 59
  headline "Microchip Technology Gains as Analysts Raise Price Targets Following Strong Earnings Guidance and Inventory…"
WHY
  underlying -3.6%/-0.6%/+4.3% (favorable peak +6.3%); position move +4.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~37% · IV residual ~46% [inferred].
  convexity Γ·S = 2.69. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE OKLO-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.480 Γ0.0205 Θ-0.161 · IV 1.103 · mid 5.06
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 66
  headline "OKLO Surges 33% in a Week on Space Power Catalyst: Buy Now?"
WHY
  underlying -8.1%/+6.3%/+12.2% (favorable peak +18.4%); position move +12.2%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~79% · IV residual ~10% [inferred].
  convexity Γ·S = 1.40. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ON-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 10 · V/OI 4.08 · spread +0.0%
  greeks Δ0.745 Γ0.0265 Θ-0.189 · IV 0.663 · mid 8.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 75
  headline "ON Semiconductor Data Center Revenue Seen Doubling As Cycle Turns; Stock Hits 52-Week High"
WHY
  underlying -2.9%/+7.9%/+10.4% (favorable peak +11.1%); position move +10.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~94% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.84. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE PANW-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.429 Γ0.0258 Θ-0.177 · IV 0.424 · mid 4.19
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 50
  headline "Piper Sandler Reiterates $265 Price Target as Palo Alto Networks Gains Momentum on AI Integration and Overs…"
WHY
  underlying -0.6%/+1.0%/+2.7% (favorable peak +4.8%); position move +2.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~46% · IV residual ~47% [inferred].
  convexity Γ·S = 4.19. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE QCOM-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI 2.81 · spread +0.1%
  greeks Δ0.436 Γ0.0179 Θ-0.139 · IV 0.447 · mid 6.87
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 71
  headline "Qualcomm stock falls 5% as cautious Q3 guidance triggers profit-taking after 34% weekly rally"
WHY
  underlying +10.8%/+14.4%/+20.3% (favorable peak +32.8%); position move +20.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~217% · IV residual ~-131% [inferred].
  convexity Γ·S = 3.02. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE RCL-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 11.67 · spread +0.0%
  greeks Δ0.396 Γ0.0120 Θ-0.283 · IV 0.514 · mid 7.47
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 43
  headline "Goldman Sachs and Bernstein Defend Royal Caribbean (RCL), Citing Overblown Reaction to Mexico Project Delay"
WHY
  underlying +2.5%/+0.9%/+5.4% (favorable peak +5.8%); position move +5.4%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~73% · IV residual ~18% [inferred].
  convexity Γ·S = 3.04. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RDDT-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 29 · V/OI 4.55 · spread +0.0%
  greeks Δ0.629 Γ0.0135 Θ-0.188 · IV 0.636 · mid 13.10
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 51
  headline "Reddit Stock Surges Wednesday Afternoon: What's Driving The Move?"
WHY
  underlying +8.8%/+14.1%/+15.3% (favorable peak +18.4%); position move +15.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~114% · IV residual ~-29% [inferred].
  convexity Γ·S = 2.08. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE RDW-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 45 · V/OI 15.00 · spread +0.0%
  greeks Δ0.494 Γ0.0777 Θ-0.023 · IV 1.195 · mid 0.94
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 64
  headline "Redwire (RDW) Price Targets Raised to $15 by Analysts as Space and Defense Backlog Hits Record $498 Million"
WHY
  underlying -4.9%/-5.8%/+15.0% (favorable peak +20.1%); position move +15.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~96% · IV residual ~-9% [inferred].
  convexity Γ·S = 0.94. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SIRI-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 75.00 · spread +0.0%
  greeks Δ0.290 Γ0.1391 Θ-0.018 · IV 0.360 · mid 0.28
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 60
  headline "SiriusXM and NASCAR Announce Multi-Year Renewal of Broadcasting Agreement through 2028"
WHY
  underlying +7.2%/+6.8%/+9.5% (favorable peak +11.3%); position move +9.5%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~267% · IV residual ~-167% [inferred].
  convexity Γ·S = 3.76. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TRTX-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.211 Γ0.3361 Θ-0.004 · IV 0.372 · mid 0.05
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 58
  headline "TPG RE Finance Trust, Inc. Announces First Quarter 2026 Earnings Release and Conference Call Dates"
WHY
  underlying -0.1%/+0.8%/+1.0% (favorable peak +1.9%); position move +1.0%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~34% · IV residual ~70% [inferred].
  convexity Γ·S = 2.79. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TWLO-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 2.00 · spread +0.0%
  greeks Δ0.460 Γ0.0188 Θ-0.203 · IV 0.474 · mid 10.10
  overnight_score 6 · flow DIRECTIONAL · catalyst Insider Activity (0.60) · RSI 54
  headline "Sachem Head entities trim Twilio (NYSE: TWLO) stake with 1M-share sale"
WHY
  underlying +1.7%/+5.0%/+25.3% (favorable peak +27.4%); position move +25.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~209% · IV residual ~-123% [inferred].
  convexity Γ·S = 3.41. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE VRT-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 3.80 · spread +0.0%
  greeks Δ0.256 Γ0.0066 Θ-0.556 · IV 0.723 · mid 10.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 63
  headline "Citigroup Raises Vertiv (VRT) Price Target to $414 as AI Infrastructure Demand Intensifies"
WHY
  underlying -0.0%/+8.2%/+8.0% (favorable peak +9.4%); position move +8.0%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~64% · IV residual ~31% [inferred].
  convexity Γ·S = 2.26. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WDC-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.284 Γ0.0039 Θ-0.706 · IV 0.783 · mid 17.07
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 76
  headline "Western Digital Share Swap Highlights Separation Progress and AI-Driven Valuation Gap"
WHY
  underlying +3.5%/+11.2%/+5.4% (favorable peak +13.2%); position move +5.4%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~41% · IV residual ~51% [inferred].
  convexity Γ·S = 1.80. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AAOI-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.342 Γ0.0071 Θ-0.542 · IV 1.222 · mid 7.56
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 61
  headline "Applied Optoelectronics Soars 24% as Rosenblatt Hikes Price Target to $220 on AI-Driven 800G Demand"
WHY
  underlying +1.8%/+20.7%/+10.1% (favorable peak +26.4%); position move +10.1%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~85% · IV residual ~17% [inferred].
  convexity Γ·S = 1.32. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE ALB-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.295 Γ0.0147 Θ-0.248 · IV 0.581 · mid 3.46
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 63
  headline "Albemarle (ALB) Trading Higher Following Oppenheimer Price Target Raise to $222"
WHY
  underlying -2.4%/+13.6%/+4.2% (favorable peak +13.6%); position move +4.2%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~67% · IV residual ~34% [inferred].
  convexity Γ·S = 2.79. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AMAT-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.429 Γ0.0075 Θ-0.597 · IV 0.575 · mid 16.02
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.80) · RSI 50
  headline "Morgan Stanley Downgrades AMAT While Raising Peer Targets, Triggering 5% Sell-Off"
WHY
  underlying -1.7%/+3.1%/+3.3% (favorable peak +4.2%); position move +3.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~37% · IV residual ~54% [inferred].
  convexity Γ·S = 3.12. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE BE-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 10.00 · spread +0.0%
  greeks Δ0.342 Γ0.0066 Θ-0.969 · IV 1.138 · mid 13.22
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 66
  headline "NASA Artemis Report and AI Data Center Demand Ignite 12% Rally in Bloom Energy"
WHY
  underlying -1.1%/+2.1%/+6.9% (favorable peak +9.2%); position move +6.9%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~50% · IV residual ~52% [inferred].
  convexity Γ·S = 1.86. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAT-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 1.86 · spread +0.1%
  greeks Δ0.314 Γ0.0038 Θ-0.597 · IV 0.382 · mid 17.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.88) · RSI 54
  headline "Caterpillar Power & Energy President Reframes Data Center Story as Decades-Long Recurring Revenue Engine at…"
WHY
  underlying -0.8%/+0.8%/+4.1% (favorable peak +4.2%); position move +4.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~63% · IV residual ~27% [inferred].
  convexity Γ·S = 3.33. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CEG-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 4.40 · spread +0.0%
  greeks Δ0.274 Γ0.0153 Θ-0.424 · IV 0.490 · mid 3.80
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 47
  headline "US Department of Energy approves US$1.00 billion loan to restart Constellation Energy's Crane nuclear plant"
WHY
  underlying +2.0%/+9.2%/+9.8% (favorable peak +10.9%); position move +9.8%.
  decomp [first-order]: theta drag ~33% of premium / 3d · delta capture ~202% · IV residual ~-88% [inferred].
  convexity Γ·S = 4.39. exit TARGET → realized +80%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE CVE-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.392 Γ0.1229 Θ-0.022 · IV 0.437 · mid 0.83
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 56
  headline "Cenovus Energy (CVE) Receives Average Recommendation of 'Buy' from Brokerages"
WHY
  underlying -5.5%/-4.0%/-1.3% (favorable peak -0.8%); position move -1.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-16% · IV residual ~104% [inferred].
  convexity Γ·S = 3.19. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DDOG-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 0.79 · spread +0.0%
  greeks Δ0.452 Γ0.0133 Θ-0.247 · IV 0.779 · mid 8.80
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 71
  headline "DA Davidson Reiterates Buy on Datadog with $225 Target Ahead of Q1 Earnings Catalyst"
WHY
  underlying -0.7%/-2.0%/+28.7% (favorable peak +35.4%); position move +28.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~216% · IV residual ~-128% [inferred].
  convexity Γ·S = 1.95. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DDOG-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 27.67 · spread +0.0%
  greeks Δ0.755 Γ0.0241 Θ-0.148 · IV 0.275 · mid 11.90
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.80) · RSI 82
  headline "Snowflake Surges on Earnings Beat and Massive $6 Billion AWS Partnership, Lifting Cloud Software Peers"
WHY
  underlying +1.5%/+11.5%/+25.1% (favorable peak +25.7%); position move +25.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~353% · IV residual ~-269% [inferred].
  convexity Γ·S = 5.34. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE DELL-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 5.89 · spread +0.0%
  greeks Δ0.409 Γ0.0057 Θ-0.456 · IV 0.772 · mid 17.88
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.95) · RSI 78
  headline "Dell Stock Rallies Ahead of Earnings as AI Server Backlog Hits $43B and Lenovo Results Signal PC Recovery"
WHY
  underlying +0.1%/+3.9%/+38.0% (favorable peak +40.7%); position move +38.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~265% · IV residual ~-177% [inferred].
  convexity Γ·S = 1.74. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE ENPH-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 14 · V/OI n/a · spread +0.1%
  greeks Δ0.556 Γ0.0301 Θ-0.184 · IV 1.062 · mid 5.83
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 77
  headline "Enphase powers to 52-week high as Goldman points to data center transformer opportunity"
WHY
  underlying +2.7%/+7.3%/+12.7% (favorable peak +16.6%); position move +12.7%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~76% · IV residual ~14% [inferred].
  convexity Γ·S = 1.88. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE FTAI-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 4.93 · spread +0.1%
  greeks Δ0.602 Γ0.0098 Θ-0.464 · IV 0.850 · mid 21.19
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 36
  headline "FTAI Aviation (FTAI) Reports Earnings Tomorrow: What To Expect"
WHY
  underlying -1.3%/+15.6%/+11.1% (favorable peak +17.8%); position move +11.1%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~68% · IV residual ~19% [inferred].
  convexity Γ·S = 2.13. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HSY-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.408 Γ0.0395 Θ-0.140 · IV 0.261 · mid 2.10
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 53
  headline "S&P Global Ratings revises Hershey outlook to stable on cocoa deflation and profit expansion hopes"
WHY
  underlying -1.9%/+1.6%/+1.2% (favorable peak +2.7%); position move +1.2%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~44% · IV residual ~56% [inferred].
  convexity Γ·S = 7.70. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LRCX-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.447 Γ0.0102 Θ-0.446 · IV 0.634 · mid 19.17
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 51
  headline "Semiconductor Stocks Under Pressure as Inflation Fears and Samsung Strike Risk Weigh on Tech Sector"
WHY
  underlying -1.6%/+5.1%/+8.7% (favorable peak +9.1%); position move +8.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~57% · IV residual ~30% [inferred].
  convexity Γ·S = 2.83. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MCO-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 6.04 · spread +0.1%
  greeks Δ0.482 Γ0.0094 Θ-0.326 · IV 0.341 · mid 15.40
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 57
  headline "Moody's (MCO) Reports Earnings April 22: Wall Street Expects Strong EPS Growth"
WHY
  underlying +1.0%/+0.9%/+2.5% (favorable peak +6.0%); position move +2.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~36% · IV residual ~51% [inferred].
  convexity Γ·S = 4.27. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE OKLO-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.266 Γ0.0176 Θ-0.147 · IV 1.079 · mid 2.38
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 56
  headline "Oklo (OKLO) Share Price Pulls Back to $72 as NRC Approval Fails to Prevent Mid-Week Selloff"
WHY
  underlying +0.9%/+8.8%/+2.5% (favorable peak +10.9%); position move +2.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~20% · IV residual ~78% [inferred].
  convexity Γ·S = 1.26. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE QCOM-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 3.00 · spread +0.0%
  greeks Δ0.280 Γ0.0077 Θ-0.478 · IV 0.921 · mid 6.62
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 66
  headline "Qualcomm's shares plunged on Wednesday over U.S. export concerns about its AI chip deal with ByteDance"
WHY
  underlying +4.2%/+7.5%/-1.9% (favorable peak +11.4%); position move -1.9%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~-19% · IV residual ~120% [inferred].
  convexity Γ·S = 1.80. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SNDK-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 6.50 · spread +0.0%
  greeks Δ0.315 Γ0.0017 Θ-4.386 · IV 1.418 · mid 39.09
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 71
  headline "SanDisk Hits New All-Time Highs as AI Data Center Boom Triggers Massive Institutional Buying Ahead of Earnings"
WHY
  underlying -4.8%/+1.1%/+9.3% (favorable peak +9.4%); position move +9.3%.
  decomp [first-order]: theta drag ~34% of premium / 3d · delta capture ~73% · IV residual ~40% [inferred].
  convexity Γ·S = 1.62. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SNPS-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 15.00 · spread +0.0%
  greeks Δ0.441 Γ0.0089 Θ-1.022 · IV 0.606 · mid 14.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 71
  headline "Synopsys Partners with TSMC to Power Next-Generation AI Systems with Silicon Proven IP and Certified EDA Flows"
WHY
  underlying -4.3%/+4.9%/+4.5% (favorable peak +5.2%); position move +4.5%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~67% · IV residual ~35% [inferred].
  convexity Γ·S = 4.25. exit TARGET → realized +80%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TEAM-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 15 · V/OI 15.87 · spread +0.0%
  greeks Δ0.619 Γ0.0314 Θ-0.153 · IV 0.648 · mid 6.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 59
  headline "Why Atlassian Stock Is Quietly Surging Higher"
WHY
  underlying +4.7%/+20.8%/+30.2% (favorable peak +34.0%); position move +30.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~262% · IV residual ~-175% [inferred].
  convexity Γ·S = 2.79. exit TARGET → realized +80%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE TSEM-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 25.00 · spread +0.0%
  greeks Δ0.434 Γ0.0068 Θ-0.478 · IV 0.968 · mid 15.81
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 63
  headline "Tower Semiconductor (TSEM) Surges Ahead of Q1 Earnings as AI Networking and Defense Partnerships Drive Inst…"
WHY
  underlying -3.5%/+18.3%/+22.6% (favorable peak +23.8%); position move +22.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~142% · IV residual ~-53% [inferred].
  convexity Γ·S = 1.56. exit TARGET → realized +80%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PPG-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 1.25 · spread +0.0%
  greeks Δ0.434 Γ0.0514 Θ-0.155 · IV 0.432 · mid 2.15
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 46
  headline "PPG beats quarterly profit, revenue estimates on pricing strength; reaffirms 2026 outlook"
WHY
  underlying -2.8%/+0.8%/-0.2% (favorable peak +1.7%); position move -0.2%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~-3% · IV residual ~100% [inferred].
  convexity Γ·S = 5.53. exit TIMEOUT → realized +75%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HON-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.274 Γ0.0154 Θ-0.096 · IV 0.311 · mid 3.10
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 48
  headline "Honeywell Aerospace spin-off set for June 29, 2026, as company confirms final stages of portfolio breakup"
WHY
  underlying -0.0%/+0.1%/+3.0% (favorable peak +3.7%); position move +3.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~58% · IV residual ~26% [inferred].
  convexity Γ·S = 3.35. exit TIMEOUT → realized +75%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE U-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 11.87 · spread +0.1%
  greeks Δ0.526 Γ0.0986 Θ-0.054 · IV 0.709 · mid 1.41
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 61
  headline "Wall Street Analysts Think Unity Software (U) Could Surge 37.62%"
WHY
  underlying +7.9%/+9.8%/+15.9% (favorable peak +17.3%); position move +15.9%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~164% · IV residual ~-78% [inferred].
  convexity Γ·S = 2.74. exit TIMEOUT → realized +75%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE HSY-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 0.83 · spread +0.0%
  greeks Δ0.345 Γ0.0522 Θ-0.097 · IV 0.195 · mid 3.40
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 42
  headline "Hershey cuts 2026 outlook on high cocoa costs and weak consumer demand"
WHY
  underlying +2.5%/+3.1%/+2.1% (favorable peak +4.8%); position move +2.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~39% · IV residual ~43% [inferred].
  convexity Γ·S = 9.75. exit TIMEOUT → realized +74%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DELL-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 4.82 · spread +0.0%
  greeks Δ0.438 Γ0.0073 Θ-0.285 · IV 0.696 · mid 16.58
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 59
  headline "Evercore ISI raises Dell stock price target to $270 on AI growth momentum at Dell World"
WHY
  underlying -1.2%/+2.1%/+6.2% (favorable peak +6.9%); position move +6.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~39% · IV residual ~39% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized +73%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NBIS-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 3.03 · spread +0.1%
  greeks Δ0.472 Γ0.0105 Θ-0.271 · IV 0.990 · mid 11.56
  overnight_score 6 · flow MIXED · catalyst — (—) · RSI 51
WHY
  underlying +11.8%/+27.6%/+27.3% (favorable peak +30.2%); position move +27.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~154% · IV residual ~-74% [inferred].
  convexity Γ·S = 1.45. exit TIMEOUT → realized +73%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE UAL-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 5.20 · spread +0.1%
  greeks Δ0.525 Γ0.0264 Θ-0.094 · IV 0.539 · mid 6.42
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 48
  headline "United Airlines (UAL) Recovers 2.5% as Analysts Defend Long-Term Thesis Despite Fuel Cost Headwinds"
WHY
  underlying -2.6%/+1.2%/+8.1% (favorable peak +8.5%); position move +8.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~61% · IV residual ~15% [inferred].
  convexity Γ·S = 2.44. exit TIMEOUT → realized +72%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HAL-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.467 Γ0.0820 Θ-0.024 · IV 0.373 · mid 1.86
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 55
  headline "Halliburton (HAL) Q1 Earnings Countdown: Institutional Flow Surges Ahead of April 21 Report"
WHY
  underlying -2.6%/-3.9%/+0.0% (favorable peak +1.4%); position move +0.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~0% · IV residual ~75% [inferred].
  convexity Γ·S = 3.13. exit TIMEOUT → realized +72%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DOCN-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.497 Γ0.0407 Θ-0.230 · IV 0.816 · mid 4.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.82) · RSI 50
  headline "Bank of America Boosts DigitalOcean (DOCN) Price Target to $107, Citing Strong AI Tailwinds"
WHY
  underlying +13.8%/+10.2%/+15.3% (favorable peak +20.3%); position move +15.3%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~131% · IV residual ~-45% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized +71%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE NEE-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 13.13 · spread +0.0%
  greeks Δ0.299 Γ0.0647 Θ-0.044 · IV 0.230 · mid 0.77
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 55
  headline "J.P. Morgan raises NextEra Energy price target to $105, reiterates Overweight rating on AI power demand tai…"
WHY
  underlying -2.4%/-6.9%/-5.9% (favorable peak -0.6%); position move -5.9%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-218% · IV residual ~303% [inferred].
  convexity Γ·S = 6.19. exit TIMEOUT → realized +67%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TMUS-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 7 · V/OI n/a · spread +0.0%
  greeks Δ0.062 Γ0.0132 Θ-0.073 · IV 0.322 · mid 0.39
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 41
  headline "Morgan Stanley Initiates T-Mobile as 'Top Pick' with $260 Price Target"
WHY
  underlying +0.3%/+0.6%/-0.9% (favorable peak +4.9%); position move -0.9%.
  decomp [first-order]: theta drag ~56% of premium / 3d · delta capture ~-28% · IV residual ~151% [inferred].
  convexity Γ·S = 2.60. exit TIMEOUT → realized +67%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AMAT-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.363 Γ0.0062 Θ-0.501 · IV 0.606 · mid 14.15
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 61
  headline "Applied Materials Strengthens $5B Silicon Valley R&D Hub with Advantest Partnership"
WHY
  underlying +2.3%/+2.4%/+5.8% (favorable peak +6.6%); position move +5.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~58% · IV residual ~19% [inferred].
  convexity Γ·S = 2.44. exit TIMEOUT → realized +67%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MARA-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ0.363 Γ0.1049 Θ-0.017 · IV 0.928 · mid 0.72
  overnight_score 5 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 59
  headline "Marathon Digital to Acquire Long Ridge Energy for $1.5B in Strategic AI Infrastructure Pivot"
WHY
  underlying +3.2%/+6.1%/+13.7% (favorable peak +14.5%); position move +13.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~79% · IV residual ~-6% [inferred].
  convexity Γ·S = 1.20. exit TIMEOUT → realized +67%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE APA-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 30 · V/OI 5.00 · spread +0.0%
  greeks Δ0.531 Γ0.0709 Θ-0.038 · IV 0.533 · mid 2.21
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 46
  headline "U.S. energy stocks climb as crude prices surge on Iran tensions; APA raises 2026 oil outlook"
WHY
  underlying -0.3%/+0.1%/+5.1% (favorable peak +5.3%); position move +5.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~45% · IV residual ~25% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized +65%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CLS-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.1%
  greeks Δ0.582 Γ0.0169 Θ-0.538 · IV 0.377 · mid 9.37
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.90) · RSI 56
  headline "RBC Capital raises Celestica stock price target to $440 on strong demand outlook"
WHY
  underlying +8.8%/+11.3%/+11.7% (favorable peak +13.3%); position move +11.7%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~274% · IV residual ~-193% [inferred].
  convexity Γ·S = 6.38. exit TIMEOUT → realized +64%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE AAL-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.629 Γ0.1509 Θ-0.012 · IV 0.551 · mid 1.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 65
  headline "American Airlines Surges 4.6% as BMO Raises Target and AAA Predicts Record Summer Travel Demand"
WHY
  underlying +1.9%/+9.3%/+9.8% (favorable peak +13.3%); position move +9.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~84% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.05. exit TIMEOUT → realized +64%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE GLXY-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 6.19 · spread +0.1%
  greeks Δ0.287 Γ0.0729 Θ-0.059 · IV 0.857 · mid 0.96
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 65
  headline "Compass Point Raises Galaxy Digital Target to $41 on HPC Pipeline Visibility and Earnings Beat"
WHY
  underlying +3.8%/+7.9%/+10.7% (favorable peak +12.3%); position move +10.7%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~90% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.05. exit TIMEOUT → realized +63%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE COP-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 4.00 · spread +0.0%
  greeks Δ0.377 Γ0.0399 Θ-0.086 · IV 0.335 · mid 2.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 47
  headline "ConocoPhillips Set for FCF Surge as Oil Surges Post-Strait of Hormuz Disruption; Analysts Raise Targets to …"
WHY
  underlying +2.9%/+4.7%/+5.2% (favorable peak +5.9%); position move +5.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~82% · IV residual ~-11% [inferred].
  convexity Γ·S = 4.75. exit TIMEOUT → realized +62%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE STX-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 6.00 · spread +0.0%
  greeks Δ0.420 Γ0.0022 Θ-0.965 · IV 0.761 · mid 48.50
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 59
  headline "Seagate CEO says building new factories 'would take too long', sparking capacity concerns"
WHY
  underlying -1.0%/+1.4%/+9.4% (favorable peak +9.5%); position move +9.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~60% · IV residual ~7% [inferred].
  convexity Γ·S = 1.60. exit TIMEOUT → realized +61%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NEM-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 13.76 · spread +0.1%
  greeks Δ0.274 Γ0.0229 Θ-0.073 · IV 0.437 · mid 2.59
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 46
  headline "Newmont (NEM) Is Down 10.0% After Launching $6 Billion Buyback And Posting Stronger Q1 Results"
WHY
  underlying -0.3%/+0.4%/+6.0% (favorable peak +6.7%); position move +6.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~69% · IV residual ~0% [inferred].
  convexity Γ·S = 2.48. exit TIMEOUT → realized +61%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE XYZ-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.356 Γ0.0320 Θ-0.055 · IV 0.560 · mid 2.69
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.45) · RSI 56
  headline "Needham and Oppenheimer Lift XYZ Price Targets to $90 Citing AI Efficiency and Leaner Operations"
WHY
  underlying +3.2%/+6.4%/+9.3% (favorable peak +9.9%); position move +9.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~76% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.99. exit TIMEOUT → realized +60%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LUNR-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.445 Γ0.0424 Θ-0.113 · IV 1.224 · mid 7.28
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 60
  headline "Intuitive Machines tumbles after NASA picks rivals for lunar rover work"
WHY
  underlying +15.7%/+31.1%/+25.7% (favorable peak +34.1%); position move +25.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~55% · IV residual ~10% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized +60%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE WOLF-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ0.389 Γ0.0191 Θ-0.138 · IV 1.249 · mid 4.67
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 70
  headline "Wolfspeed: The Post-Bankruptcy Reset Is Working; Citrini Sets $85 Target on AI Pivot"
WHY
  underlying +18.6%/+19.2%/+25.4% (favorable peak +37.9%); position move +25.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~124% · IV residual ~-55% [inferred].
  convexity Γ·S = 1.12. exit TIMEOUT → realized +60%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE HPQ-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 2.96 · spread +0.0%
  greeks Δ0.441 Γ0.1145 Θ-0.018 · IV 0.439 · mid 1.33
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 73
  headline "HP beats revenue, profit estimates as AI PC and Windows 11 refresh boost demand"
WHY
  underlying -1.9%/+6.1%/+15.1% (favorable peak +15.9%); position move +15.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~128% · IV residual ~-65% [inferred].
  convexity Γ·S = 2.92. exit TIMEOUT → realized +59%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE UBER-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.1%
  greeks Δ0.479 Γ0.0404 Θ-0.054 · IV 0.420 · mid 3.25
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 48
  headline "Uber & Ace Hardware Collaborate on Nationwide Delivery; Launches Lucid Gravity Robotaxi Testing in San Fran…"
WHY
  underlying +0.8%/+6.8%/+5.7% (favorable peak +7.9%); position move +5.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~61% · IV residual ~2% [inferred].
  convexity Γ·S = 2.93. exit TIMEOUT → realized +58%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CRWD-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 3.80 · spread +0.0%
  greeks Δ0.475 Γ0.0044 Θ-0.898 · IV 0.642 · mid 25.85
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 83
  headline "BTIG Hikes CrowdStrike Price Target to $621 as Platform Consolidation Strategy Wins Enterprise Spend"
WHY
  underlying +4.2%/+3.8%/+9.4% (favorable peak +9.6%); position move +9.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~103% · IV residual ~-35% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized +58%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PL-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 44 · V/OI n/a · spread +0.1%
  greeks Δ0.497 Γ0.0374 Θ-0.049 · IV 0.900 · mid 3.01
  overnight_score 3 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 57
  headline "Planet Labs Achieves Technical Milestone with Onboard AI Object Detection via NVIDIA Jetson Orin"
WHY
  underlying +1.4%/+17.6%/+13.4% (favorable peak +18.6%); position move +13.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~75% · IV residual ~-13% [inferred].
  convexity Γ·S = 1.27. exit TIMEOUT → realized +57%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE BBY-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.256 Γ0.0422 Θ-0.032 · IV 0.391 · mid 1.05
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 44
  headline "BBY Defies Goldman Double-Downgrade as Cooling Inflation Sparks Retail Relief Rally"
WHY
  underlying +2.1%/+4.2%/+5.9% (favorable peak +6.4%); position move +5.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~89% · IV residual ~-23% [inferred].
  convexity Γ·S = 2.62. exit TIMEOUT → realized +57%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ARE-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.399 Γ0.0573 Θ-0.040 · IV 0.519 · mid 1.45
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.30) · RSI 45
  headline "Alexandria Real Estate Equities Pays Q1 Dividend Amidst 'Trough' Year Projections"
WHY
  underlying +4.9%/+5.6%/+7.1% (favorable peak +8.3%); position move +7.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~89% · IV residual ~-24% [inferred].
  convexity Γ·S = 2.60. exit TIMEOUT → realized +57%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MPWR-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 0.69 · spread +0.0%
  greeks Δ0.402 Γ0.0015 Θ-2.999 · IV 0.760 · mid 71.90
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 76
  headline "Monolithic Power Systems to Report First Quarter 2026 Results on April 30, 2026"
WHY
  underlying -5.3%/-3.8%/+1.7% (favorable peak +2.2%); position move +1.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~15% · IV residual ~54% [inferred].
  convexity Γ·S = 2.34. exit TIMEOUT → realized +57%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE RKLB-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ0.464 Γ0.0195 Θ-0.115 · IV 0.877 · mid 5.71
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.82) · RSI 56
  headline "Rocket Lab Completes Mynaric Acquisition, Adding Laser Optical Communications to Space Systems Portfolio"
WHY
  underlying +12.7%/+15.2%/+21.5% (favorable peak +22.7%); position move +21.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~129% · IV residual ~-67% [inferred].
  convexity Γ·S = 1.43. exit TIMEOUT → realized +56%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE OSCR-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 3.56 · spread +0.1%
  greeks Δ0.544 Γ0.0973 Θ-0.025 · IV 0.650 · mid 1.69
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 83
  headline "Oscar Health (OSCR) Shares Surge as UBS Hikes Price Target Following Record Q1 Profitability"
WHY
  underlying +2.1%/+5.4%/+13.7% (favorable peak +13.9%); position move +13.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~92% · IV residual ~-32% [inferred].
  convexity Γ·S = 2.03. exit TIMEOUT → realized +56%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE LFUS-2026-05-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.388 Γ0.0049 Θ-0.453 · IV 0.527 · mid 22.89
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 79
  headline "Littelfuse to Host 2026 Investor Day in New York City on May 14; Analysts Expect New 5-Year Targets"
WHY
  underlying -4.4%/-7.3%/-9.4% (favorable peak +0.6%); position move -9.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-76% · IV residual ~137% [inferred].
  convexity Γ·S = 2.33. exit TIMEOUT → realized +55%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ANET-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.1%
  greeks Δ0.227 Γ0.0104 Θ-0.100 · IV 0.540 · mid 3.54
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.70) · RSI 66
  headline "Arista Networks Inc Stock (ANET) Closed Up by 3.13% on Apr 13: What Investors Need To Know"
WHY
  underlying +1.5%/+1.5%/+5.9% (favorable peak +5.9%); position move +5.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~58% · IV residual ~6% [inferred].
  convexity Γ·S = 1.58. exit TIMEOUT → realized +55%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ALAB-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.1%
  greeks Δ0.441 Γ0.0066 Θ-0.328 · IV 0.965 · mid 13.37
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 79
  headline "RBC Boosts Astera Labs (ALAB) Price Target to $250 Following $100B Amazon-Anthropic AI Infrastructure Deal"
WHY
  underlying +1.1%/+2.9%/+10.9% (favorable peak +11.6%); position move +10.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~69% · IV residual ~-7% [inferred].
  convexity Γ·S = 1.27. exit TIMEOUT → realized +54%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ANET-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.254 Γ0.0113 Θ-0.136 · IV 0.573 · mid 4.15
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 72
  headline "Arista Networks (ANET) Shares Surge After JPMorgan Raises Price Target to $200 on AI Infrastructure Strength"
WHY
  underlying +2.0%/+3.6%/+7.4% (favorable peak +8.0%); position move +7.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~72% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized +54%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ADI-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.481 Γ0.0097 Θ-0.614 · IV 0.508 · mid 14.85
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 70
  headline "Analog Devices (ADI) Hits All-Time High as Analysts Cite Pricing Power and AI-Driven Data Center Growth"
WHY
  underlying +1.5%/+0.8%/+3.8% (favorable peak +4.6%); position move +3.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~51% · IV residual ~15% [inferred].
  convexity Γ·S = 4.06. exit TIMEOUT → realized +54%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WOLF-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 3.33 · spread +0.1%
  greeks Δ0.528 Γ0.0215 Θ-0.086 · IV 0.921 · mid 6.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 84
  headline "Wolfspeed (WOLF) Soars to All-Time High as Losses Slashed and AI Momentum Builds"
WHY
  underlying +16.5%/+30.2%/+15.7% (favorable peak +37.3%); position move +15.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~72% · IV residual ~-15% [inferred].
  convexity Γ·S = 1.15. exit TIMEOUT → realized +53%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE PFGC-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.327 Γ0.0368 Θ-0.061 · IV 0.380 · mid 2.15
  overnight_score 7 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 56
  headline "No major headlines found for PFGC in the past 24 hours"
WHY
  underlying -0.8%/-0.6%/+4.4% (favorable peak +4.4%); position move +4.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~60% · IV residual ~1% [inferred].
  convexity Γ·S = 3.29. exit TIMEOUT → realized +52%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WDC-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.339 Γ0.0056 Θ-0.887 · IV 0.908 · mid 14.30
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 70
  headline "Top Analyst Boosts Western Digital (WDC) Stock Price Target Ahead of Q3 Earnings Even After 116% YTD Surge"
WHY
  underlying +0.4%/+3.0%/+4.5% (favorable peak +7.9%); position move +4.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~39% · IV residual ~31% [inferred].
  convexity Γ·S = 2.08. exit TIMEOUT → realized +51%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SPG-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 28 · V/OI 0.08 · spread +0.1%
  greeks Δ0.590 Γ0.0279 Θ-0.090 · IV 0.248 · mid 6.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 56
  headline "Simon raises 2026 real estate FFO outlook to $13.10-$13.25 per share amid 9% redevelopment yields"
WHY
  underlying +0.4%/+0.2%/+1.4% (favorable peak +1.5%); position move +1.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~26% · IV residual ~29% [inferred].
  convexity Γ·S = 5.69. exit TIMEOUT → realized +51%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TGT-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.742 Γ0.0322 Θ-0.095 · IV 0.371 · mid 9.39
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.20) · RSI 57
  headline "Target shares fall after six-session winning streak; analysts remain focused on turnaround momentum"
WHY
  underlying +0.6%/+2.1%/+1.4% (favorable peak +3.3%); position move +1.4%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~14% · IV residual ~40% [inferred].
  convexity Γ·S = 4.10. exit TIMEOUT → realized +51%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAMT-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 0.45 · spread +0.0%
  greeks Δ0.702 Γ0.0098 Θ-0.727 · IV 1.155 · mid 12.15
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 62
  headline "Camtek (CAMT) Surges 8% as AI Semiconductor Rally Intensifies Ahead of Q1 Earnings"
WHY
  underlying -4.7%/+1.5%/+2.4% (favorable peak +6.6%); position move +2.4%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~28% · IV residual ~40% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized +51%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SNDK-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 26.00 · spread +0.0%
  greeks Δ0.424 Γ0.0017 Θ-4.426 · IV 1.288 · mid 65.25
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 73
  headline "Sandisk (SNDK) Stock Rockets on Explosive AI-Driven Earnings and Nasdaq-100 Inclusion"
WHY
  underlying -6.3%/-0.6%/+2.5% (favorable peak +4.2%); position move +2.5%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~17% · IV residual ~54% [inferred].
  convexity Γ·S = 1.77. exit TIMEOUT → realized +50%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SHOP-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.378 Γ0.0168 Θ-0.190 · IV 0.763 · mid 5.18
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 48
  headline "US markets rise on Middle East de-escalation hopes; SHOP outpaces market with 2.3% gain"
WHY
  underlying +8.3%/+7.9%/+11.5% (favorable peak +13.3%); position move +11.5%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~99% · IV residual ~-37% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized +50%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE DUOL-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 5.80 · spread +0.0%
  greeks Δ0.383 Γ0.0141 Θ-0.318 · IV 1.197 · mid 5.29
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 57
  headline "Duolingo (DUOL) Rebounds Near 52-Week Lows as Investors Weigh Strategic Pivot Ahead of May 4 Earnings"
WHY
  underlying +0.5%/+3.6%/+4.7% (favorable peak +8.0%); position move +4.7%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~36% · IV residual ~31% [inferred].
  convexity Γ·S = 1.50. exit TIMEOUT → realized +49%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ULTA-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 11.54 · spread +0.0%
  greeks Δ0.291 Γ0.0137 Θ-0.567 · IV 0.340 · mid 3.00
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 43
  headline "Ulta Beauty to Report First Quarter Fiscal 2026 Results and Participate in Upcoming Investor Conference"
WHY
  underlying +2.2%/+2.4%/+0.7% (favorable peak +4.6%); position move +0.7%.
  decomp [first-order]: theta drag ~57% of premium / 3d · delta capture ~32% · IV residual ~73% [inferred].
  convexity Γ·S = 6.91. exit TIMEOUT → realized +49%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CRDO-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 22 · V/OI 2.57 · spread +0.0%
  greeks Δ0.318 Γ0.0099 Θ-0.291 · IV 0.796 · mid 5.41
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 62
  headline "Credo Technology (CRDO) Shares Bounce 10% as AI Networking Demand and DustPhotonics Acquisition Synergy Fue…"
WHY
  underlying -1.0%/+4.9%/+2.4% (favorable peak +7.1%); position move +2.4%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~25% · IV residual ~39% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized +49%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DELL-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.449 Γ0.0116 Θ-0.183 · IV 0.567 · mid 10.65
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 68
  headline "Nvidia denies reports of PC manufacturer acquisition talks following Dell and HP share surge"
WHY
  underlying -2.8%/-6.6%/+1.7% (favorable peak +2.1%); position move +1.7%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~14% · IV residual ~40% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized +48%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PM-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 0.06 · spread +0.0%
  greeks Δ0.383 Γ0.0336 Θ-0.141 · IV 0.344 · mid 3.05
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 50
  headline "Philip Morris trims annual profit forecast amid nicotine pouch uncertainty"
WHY
  underlying +1.5%/+2.3%/+4.0% (favorable peak +5.6%); position move +4.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~81% · IV residual ~-19% [inferred].
  convexity Γ·S = 5.46. exit TIMEOUT → realized +48%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DAVE-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ0.293 Γ0.0121 Θ-0.184 · IV 0.559 · mid 4.04
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.72) · RSI 48
  headline "Dave Inc. Gains Momentum as Fintech Sector Sees Renewed Institutional Interest Amid Profitability Shift"
WHY
  underlying +5.2%/+15.3%/+24.0% (favorable peak +24.7%); position move +24.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~324% · IV residual ~-265% [inferred].
  convexity Γ·S = 2.24. exit TIMEOUT → realized +45%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CCJ-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 4.33 · spread +0.1%
  greeks Δ0.326 Γ0.0248 Θ-0.119 · IV 0.536 · mid 2.85
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 44
  headline "Kazatomprom Confirms 10% Production Cut for 2026, Removing 20M Pounds from Global Supply Pipeline"
WHY
  underlying -0.7%/+2.3%/+4.2% (favorable peak +5.2%); position move +4.2%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~52% · IV residual ~5% [inferred].
  convexity Γ·S = 2.69. exit TIMEOUT → realized +45%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE STX-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.404 Γ0.0056 Θ-0.473 · IV 0.353 · mid 19.22
  overnight_score 5 · flow HEDGING · catalyst Guidance Raise (0.95) · RSI 70
  headline "Seagate Technology (STX) Surges 15% as AI Storage Demand Drives Massive Earnings Beat and Guidance Hike"
WHY
  underlying +11.1%/+16.3%/+25.5% (favorable peak +25.7%); position move +25.5%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~311% · IV residual ~-259% [inferred].
  convexity Γ·S = 3.23. exit TIMEOUT → realized +44%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE BK-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 0.08 · spread +0.0%
  greeks Δ0.880 Γ0.0410 Θ-0.070 · IV 0.259 · mid 8.15
  overnight_score 2 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 51
  headline "BNY Mellon Eyes Institutional Bitcoin, Ethereum Custody for Investors in UAE"
WHY
  underlying -0.1%/+1.4%/+2.1% (favorable peak +2.6%); position move +2.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~30% · IV residual ~17% [inferred].
  convexity Γ·S = 5.35. exit TIMEOUT → realized +44%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE RH-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.319 Γ0.0107 Θ-0.199 · IV 0.835 · mid 6.53
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.72) · RSI 57
  headline "RH Outperforms S&P 500 as Analysts Highlight Potential H1 2026 Revenue Surge from Delayed Sourcebooks"
WHY
  underlying +3.7%/+7.7%/+7.2% (favorable peak +9.6%); position move +7.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~49% · IV residual ~4% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized +43%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AMD-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI 10.00 · spread +0.0%
  greeks Δ0.308 Γ0.0031 Θ-0.561 · IV 0.704 · mid 18.09
  overnight_score 7 · flow MIXED · catalyst — (—) · RSI 77
WHY
  underlying -1.7%/+2.8%/+2.4% (favorable peak +4.6%); position move +2.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~21% · IV residual ~31% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized +43%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WPM-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.1%
  greeks Δ0.663 Γ0.0328 Θ-0.224 · IV 0.468 · mid 5.82
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.90) · RSI 62
  headline "Gold Shatters $4,700 and Silver Eyes the $100 Frontier Amid Global Unrest and U.S. Fiscal Risks"
WHY
  underlying -0.1%/-2.0%/+3.2% (favorable peak +4.4%); position move +3.2%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~53% · IV residual ~1% [inferred].
  convexity Γ·S = 4.84. exit TIMEOUT → realized +42%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ABNB-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ0.335 Γ0.0230 Θ-0.133 · IV 0.463 · mid 2.23
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 63
  headline "Airbnb (ABNB) Options Traders Maintain Bullish Skew as Technicals Improve Post-Bond Offering"
WHY
  underlying +0.2%/+2.9%/+4.4% (favorable peak +4.6%); position move +4.4%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~91% · IV residual ~-31% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized +42%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TER-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.1%
  greeks Δ0.542 Γ0.0090 Θ-0.938 · IV 0.745 · mid 19.11
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 67
  headline "Susquehanna and Cantor Fitzgerald Raise Teradyne (TER) Price Targets to $415 Following Intel-Terafab Momentum"
WHY
  underlying -0.2%/+0.1%/+4.1% (favorable peak +4.4%); position move +4.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~42% · IV residual ~14% [inferred].
  convexity Γ·S = 3.29. exit TIMEOUT → realized +42%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MDB-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.268 Γ0.0041 Θ-0.391 · IV 0.905 · mid 14.36
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 67
  headline "MongoDB shares jump as company unveils new enterprise AI capabilities at MongoDB.local London"
WHY
  underlying +2.1%/+0.4%/+5.2% (favorable peak +8.1%); position move +5.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~29% · IV residual ~21% [inferred].
  convexity Γ·S = 1.20. exit TIMEOUT → realized +42%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HPE-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 126.53 · spread +0.1%
  greeks Δ0.524 Γ0.0835 Θ-0.028 · IV 0.537 · mid 1.78
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 69
  headline "HPE Identified as Top Stock to Own by May 1st Amid AI Server Momentum and Analyst Hikes"
WHY
  underlying -0.7%/-0.2%/+4.4% (favorable peak +4.8%); position move +4.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~37% · IV residual ~8% [inferred].
  convexity Γ·S = 2.40. exit TIMEOUT → realized +41%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE C-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 3.12 · spread +0.0%
  greeks Δ0.417 Γ0.0313 Θ-0.069 · IV 0.318 · mid 3.55
  overnight_score 7 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 51
  headline "Citigroup (C) Stock Trades Up as Easing Oil Prices Reduce Inflation Fears"
WHY
  underlying +0.3%/+0.2%/+1.6% (favorable peak +2.1%); position move +1.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~24% · IV residual ~23% [inferred].
  convexity Γ·S = 3.91. exit TIMEOUT → realized +41%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SATS-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 142.86 · spread +0.0%
  greeks Δ0.430 Γ0.0162 Θ-0.145 · IV 0.621 · mid 5.45
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 55
  headline "EchoStar (SATS) Q1 Earnings: Shares Rise as SpaceX Proxy Narrative and FMR 10% Stake Fuel Bullish Momentum"
WHY
  underlying +1.6%/+1.8%/+4.8% (favorable peak +8.1%); position move +4.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~48% · IV residual ~0% [inferred].
  convexity Γ·S = 2.06. exit TIMEOUT → realized +40%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BE-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.294 Γ0.0071 Θ-0.626 · IV 1.222 · mid 8.79
  overnight_score 5 · flow HEDGING · catalyst Partnership (0.95) · RSI 69
  headline "Bloom Energy and Oracle Announce Landmark 2.8 Gigawatt Fuel Cell Deal for AI Data Centers"
WHY
  underlying +5.0%/+6.3%/+10.5% (favorable peak +13.2%); position move +10.5%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~73% · IV residual ~-12% [inferred].
  convexity Γ·S = 1.47. exit TIMEOUT → realized +40%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE WDAY-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI 14.33 · spread +0.0%
  greeks Δ0.349 Γ0.0132 Θ-0.126 · IV 0.690 · mid 3.98
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 44
  headline "Workday Integrates Sana AI with Microsoft 365 Copilot as Agentic AI Revenue Hits $400M"
WHY
  underlying +5.3%/+8.5%/+8.9% (favorable peak +14.4%); position move +8.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~93% · IV residual ~-43% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized +40%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CRDO-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 12.00 · spread +0.0%
  greeks Δ0.496 Γ0.0072 Θ-0.330 · IV 0.977 · mid 15.23
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.88) · RSI 65
  headline "Rothschild Redburn Buy Rating Backs Credo Shift To Optics At High P/E"
WHY
  underlying -2.3%/+5.0%/+7.5% (favorable peak +8.4%); position move +7.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~45% · IV residual ~1% [inferred].
  convexity Γ·S = 1.33. exit TIMEOUT → realized +40%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MSTR-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.453 Γ0.0108 Θ-0.178 · IV 0.650 · mid 11.84
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.82) · RSI 59
  headline "MicroStrategy Set to Report Q1 Earnings May 5 as Analysts Raise Price Targets on Bitcoin Growth"
WHY
  underlying +7.1%/+11.1%/+13.0% (favorable peak +15.1%); position move +13.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~82% · IV residual ~-38% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized +39%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE MTSI-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 0.13 · spread +0.1%
  greeks Δ0.354 Γ0.0079 Θ-0.539 · IV 0.831 · mid 9.77
  overnight_score 2 · flow DIRECTIONAL · catalyst Partnership (0.75) · RSI 54
  headline "MACOM to enter long-term supply agreements and equity investment with IQE"
WHY
  underlying +1.5%/+6.0%/+7.0% (favorable peak +7.6%); position move +7.0%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~67% · IV residual ~-12% [inferred].
  convexity Γ·S = 2.10. exit TIMEOUT → realized +39%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE IBM-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 37 · V/OI n/a · spread +0.1%
  greeks Δ0.289 Γ0.0117 Θ-0.135 · IV 0.379 · mid 5.16
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 45
  headline "BofA Maintains Buy Rating on IBM Ahead of Q1 Earnings as AI Disruption Fears Fade"
WHY
  underlying +1.9%/+4.5%/+5.5% (favorable peak +6.4%); position move +5.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~74% · IV residual ~-27% [inferred].
  convexity Γ·S = 2.81. exit TIMEOUT → realized +39%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HON-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.408 Γ0.0267 Θ-0.173 · IV 0.293 · mid 4.40
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 65
  headline "Quantinuum IPO Targets $12.7B Valuation: Honeywell Spinoff Reports $31M in 2025 Revenue"
WHY
  underlying -0.1%/+0.6%/+2.6% (favorable peak +3.5%); position move +2.6%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~57% · IV residual ~-6% [inferred].
  convexity Γ·S = 6.18. exit TIMEOUT → realized +39%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE BMO-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 0.06 · spread +0.1%
  greeks Δ0.433 Γ0.0356 Θ-0.060 · IV 0.236 · mid 2.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Strategic Restructuring (0.78) · RSI 58
  headline "BMO Sells Transportation Finance Business to Stonepeak to Enhance Capital Efficiency; Analysts Grow Bullish…"
WHY
  underlying -0.3%/+0.5%/+0.7% (favorable peak +1.2%); position move +0.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~20% · IV residual ~26% [inferred].
  convexity Γ·S = 5.45. exit TIMEOUT → realized +39%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE OKLO-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 6.10 · spread +0.0%
  greeks Δ0.418 Γ0.0210 Θ-0.105 · IV 0.973 · mid 3.60
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 47
  headline "Oklo shares jumped 12.3% on Wednesday... supported by bullish coverage tied to AI power demand and Oklo's r…"
WHY
  underlying +4.0%/+5.3%/+9.8% (favorable peak +17.1%); position move +9.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~71% · IV residual ~-24% [inferred].
  convexity Γ·S = 1.31. exit TIMEOUT → realized +38%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE MU-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.397 Γ0.0058 Θ-0.812 · IV 0.700 · mid 17.45
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 61
  headline "UBS Hikes Micron PT to $535 Citing Sold-Out HBM4 Capacity and Durable Memory Super-Cycle"
WHY
  underlying +8.5%/+7.2%/+10.5% (favorable peak +12.8%); position move +10.5%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~108% · IV residual ~-56% [inferred].
  convexity Γ·S = 2.59. exit TIMEOUT → realized +38%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE KLAC-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.262 Γ0.0012 Θ-1.584 · IV 0.555 · mid 25.91
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 67
  headline "KLA shares fall as U.S. export-control fallout weighs on chip-equipment group"
WHY
  underlying -0.8%/+2.5%/+3.3% (favorable peak +3.4%); position move +3.3%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~58% · IV residual ~-2% [inferred].
  convexity Γ·S = 2.10. exit TIMEOUT → realized +38%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FSLR-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.415 Γ0.0105 Θ-0.186 · IV 0.523 · mid 8.25
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 61
  headline "Goldman Sachs Raises First Solar (FSLR) Price Target to $310 Following Record Q1 Earnings Beat"
WHY
  underlying -0.2%/+3.6%/+3.0% (favorable peak +4.7%); position move +3.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~32% · IV residual ~13% [inferred].
  convexity Γ·S = 2.23. exit TIMEOUT → realized +38%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PYPL-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.1%
  greeks Δ0.341 Γ0.0453 Θ-0.034 · IV 0.484 · mid 1.73
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 59
  headline "PayPal Shares Surge 5% as Technical Breakout and Analyst Price Target Hike Signal Potential Recovery"
WHY
  underlying +1.0%/+4.3%/+4.8% (favorable peak +5.1%); position move +4.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~45% · IV residual ~-2% [inferred].
  convexity Γ·S = 2.15. exit TIMEOUT → realized +37%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MELI-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 7 · V/OI n/a · spread +0.1%
  greeks Δ0.724 Γ0.0042 Θ-1.812 · IV 0.323 · mid 22.92
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 48
  headline "Michael Burry Builds Positions in MercadoLibre (NASDAQ: MELI) Following Post-Earnings Selloff"
WHY
  underlying -0.8%/-1.8%/+1.1% (favorable peak +1.9%); position move +1.1%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~58% · IV residual ~3% [inferred].
  convexity Γ·S = 7.10. exit TIMEOUT → realized +37%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NVTS-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.427 Γ0.0573 Θ-0.059 · IV 1.651 · mid 1.53
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 63
  headline "Navitas Semiconductor Reports Q1 Revenue Surprise and AI Infrastructure Momentum Amidst Post-Earnings Profi…"
WHY
  underlying -5.0%/-10.0%/+3.7% (favorable peak +3.7%); position move +3.7%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~18% · IV residual ~31% [inferred].
  convexity Γ·S = 1.01. exit TIMEOUT → realized +37%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE EBAY-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ0.316 Γ0.0281 Θ-0.068 · IV 0.394 · mid 2.20
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 75
  headline "eBay Challenges 52-Week Highs as Institutional Optimism Mounts Ahead of Q1 Earnings"
WHY
  underlying +2.4%/+0.7%/+0.9% (favorable peak +2.6%); position move +0.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~14% · IV residual ~32% [inferred].
  convexity Γ·S = 2.94. exit TIMEOUT → realized +37%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SPOT-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.1%
  greeks Δ0.375 Γ0.0110 Θ-0.651 · IV 0.407 · mid 7.89
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.88) · RSI 55
  headline "Morgan Stanley assumes Spotify stock coverage with overweight rating and $630 price target"
WHY
  underlying +1.4%/+5.4%/+5.4% (favorable peak +7.9%); position move +5.4%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~130% · IV residual ~-69% [inferred].
  convexity Γ·S = 5.53. exit TIMEOUT → realized +36%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LRCX-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 16.96 · spread +0.0%
  greeks Δ0.421 Γ0.0067 Θ-0.328 · IV 0.627 · mid 15.58
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 66
  headline "Lam Research Corp Stock (LRCX) Moved Down by 3.60% on May 7: What Investors Need To Know"
WHY
  underlying -3.6%/-1.0%/-0.4% (favorable peak +1.0%); position move -0.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-3% · IV residual ~45% [inferred].
  convexity Γ·S = 2.00. exit TIMEOUT → realized +36%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ULTA-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 25.00 · spread +0.0%
  greeks Δ0.348 Γ0.0108 Θ-0.488 · IV 0.336 · mid 9.50
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.75) · RSI 41
  headline "Ulta Beauty issues fiscal year 2026 guidance below estimates; institutional whales see opportunity in the dip"
WHY
  underlying -2.6%/+0.1%/+0.6% (favorable peak +2.1%); position move +0.6%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~12% · IV residual ~39% [inferred].
  convexity Γ·S = 5.73. exit TIMEOUT → realized +35%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AI-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 0.05 · spread +0.1%
  greeks Δ0.470 Γ0.2381 Θ-0.012 · IV 0.690 · mid 0.57
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 44
  headline "C3.ai's Options Anomaly: A Squeeze in the Making?"
WHY
  underlying +1.2%/+2.9%/+5.0% (favorable peak +6.9%); position move +5.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~35% · IV residual ~6% [inferred].
  convexity Γ·S = 2.03. exit TRAIL → realized +35%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CRDO-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 0.91 · spread +0.0%
  greeks Δ0.429 Γ0.0065 Θ-0.350 · IV 1.047 · mid 21.50
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.30) · RSI 62
  headline "Credo Technology Group Shares Down 5% Amid Broader Tech Pullback"
WHY
  underlying +0.1%/+11.6%/+5.5% (favorable peak +12.0%); position move +5.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~21% · IV residual ~19% [inferred].
  convexity Γ·S = 1.23. exit TRAIL → realized +34%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE FSLR-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 9.12 · spread +0.0%
  greeks Δ0.439 Γ0.0099 Θ-0.287 · IV 0.605 · mid 11.18
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.82) · RSI 64
  headline "First Solar Surges on GameChange Solar Partnership and Record Q1 Net Income"
WHY
  underlying +4.6%/+8.4%/+13.5% (favorable peak +16.2%); position move +13.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~126% · IV residual ~-84% [inferred].
  convexity Γ·S = 2.35. exit TIMEOUT → realized +34%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE KLAC-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.366 Γ0.0014 Θ-1.770 · IV 0.533 · mid 64.15
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 73
  headline "ASML CEO signals chip demand surpassing supply, sparking bullish flow in KLA Corp ahead of April 29 earnings."
WHY
  underlying -2.7%/-3.4%/-0.2% (favorable peak -0.2%); position move -0.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-3% · IV residual ~45% [inferred].
  convexity Γ·S = 2.46. exit TIMEOUT → realized +34%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MA-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.333 Γ0.0186 Θ-0.382 · IV 0.234 · mid 4.00
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 55
  headline "Citigroup Maintains Buy Rating on Mastercard, Adjusts Price Target to $675 Amid Macro Uncertainty"
WHY
  underlying +1.3%/+1.0%/+1.6% (favorable peak +2.8%); position move +1.6%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~68% · IV residual ~-5% [inferred].
  convexity Γ·S = 9.54. exit TRAIL → realized +34%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AEM-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 15 · V/OI n/a · spread +0.0%
  greeks Δ0.235 Γ0.0171 Θ-0.184 · IV 0.402 · mid 1.05
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 54
  headline "Gold Miners Retreat as Precious Metals Consolidate; Institutional Support Remains Robust for Agnico Eagle"
WHY
  underlying +0.2%/+2.7%/+0.9% (favorable peak +4.6%); position move +0.9%.
  decomp [first-order]: theta drag ~53% of premium / 3d · delta capture ~45% · IV residual ~41% [inferred].
  convexity Γ·S = 3.67. exit TIMEOUT → realized +33%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WDC-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.301 Γ0.0056 Θ-1.116 · IV 0.974 · mid 11.60
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 73
  headline "AI-Driven Sold-Out 2026 Capacity Could Be A Game Changer For Western Digital (WDC)"
WHY
  underlying +1.4%/+5.0%/+5.3% (favorable peak +8.5%); position move +5.3%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~52% · IV residual ~9% [inferred].
  convexity Γ·S = 2.17. exit TIMEOUT → realized +33%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE VRSN-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 0.15 · spread +0.0%
  greeks Δ0.256 Γ0.0120 Θ-0.192 · IV 0.396 · mid 5.80
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 60
  headline "VeriSign (VRSN) shares are climbing as investors react to upbeat analyst sentiment and rising excitement ah…"
WHY
  underlying +0.0%/+2.7%/-0.2% (favorable peak +2.8%); position move -0.2%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-3% · IV residual ~45% [inferred].
  convexity Γ·S = 3.24. exit TRAIL → realized +33%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LLY-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.384 Γ0.0041 Θ-0.633 · IV 0.333 · mid 26.06
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 62
  headline "Eli Lilly's Foundayo and Zepbound show strong weight loss maintenance in late-phase trials presented at ECO…"
WHY
  underlying +3.4%/+3.1%/+5.4% (favorable peak +6.0%); position move +5.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~79% · IV residual ~-39% [inferred].
  convexity Γ·S = 4.03. exit TIMEOUT → realized +32%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RKLB-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.633 Γ0.0157 Θ-0.132 · IV 0.938 · mid 10.18
  overnight_score 8 · flow DIRECTIONAL · catalyst Product Launch (0.95) · RSI 65
  headline "Rocket Lab Soars on Gauss Propulsion Launch, Mynaric Acquisition, and 'Golden Dome' Defense Tailwinds"
WHY
  underlying +2.3%/+7.9%/+4.5% (favorable peak +10.9%); position move +4.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~23% · IV residual ~13% [inferred].
  convexity Γ·S = 1.30. exit TIMEOUT → realized +32%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ETN-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 2.50 · spread +0.0%
  greeks Δ0.473 Γ0.0106 Θ-0.343 · IV 0.400 · mid 12.23
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.60) · RSI 42
  headline "Eaton Corp Technical Breakout Supported by Massive Institutional Call Buying"
WHY
  underlying +0.5%/+3.1%/+6.2% (favorable peak +7.9%); position move +6.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~91% · IV residual ~-50% [inferred].
  convexity Γ·S = 4.01. exit TIMEOUT → realized +32%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SEDG-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 7.30 · spread +0.0%
  greeks Δ0.571 Γ0.0450 Θ-0.226 · IV 1.399 · mid 3.75
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 49
  headline "SolarEdge Continues to Expand C&I Storage Suite in Europe and Asia with New Higher Capacity Commercial Stor…"
WHY
  underlying +0.1%/-3.1%/+4.2% (favorable peak +5.0%); position move +4.2%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~27% · IV residual ~23% [inferred].
  convexity Γ·S = 1.93. exit TIMEOUT → realized +32%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SITM-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 3.25 · spread +0.0%
  greeks Δ0.491 Γ0.0030 Θ-1.091 · IV 0.958 · mid 40.45
  overnight_score 4 · flow DIRECTIONAL · catalyst M&A (0.90) · RSI 79
  headline "SiTime Jumps on S&P MidCap 400 Inclusion and Reported $3B Renesas Timing Business Acquisition"
WHY
  underlying -0.9%/-0.7%/+5.3% (favorable peak +6.1%); position move +5.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~34% · IV residual ~6% [inferred].
  convexity Γ·S = 1.61. exit TIMEOUT → realized +31%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LRN-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.427 Γ0.0194 Θ-0.136 · IV 0.753 · mid 5.64
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.62) · RSI 68
  headline "Stride Announces Date for Third Quarter Fiscal Year 2026 Earnings Call"
WHY
  underlying +0.5%/+3.6%/+5.2% (favorable peak +6.0%); position move +5.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~37% · IV residual ~1% [inferred].
  convexity Γ·S = 1.82. exit TIMEOUT → realized +31%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AZN-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.396 Γ0.0232 Θ-0.113 · IV 0.285 · mid 4.15
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 64
  headline "Astrazeneca PLC ADS receives Investment Bank Analyst Rating Update"
WHY
  underlying -1.6%/-1.9%/+0.2% (favorable peak +0.5%); position move +0.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~4% · IV residual ~35% [inferred].
  convexity Γ·S = 4.74. exit TIMEOUT → realized +31%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ALB-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.478 Γ0.0128 Θ-0.216 · IV 0.545 · mid 10.76
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 59
  headline "Albemarle stock jumps after Q1 earnings beat highlights stronger lithium pricing and cash flow"
WHY
  underlying +3.0%/+5.7%/+9.0% (favorable peak +14.7%); position move +9.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~77% · IV residual ~-40% [inferred].
  convexity Γ·S = 2.47. exit TIMEOUT → realized +31%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE GNK-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ0.274 Γ0.1358 Θ-0.012 · IV 0.344 · mid 0.35
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 54
  headline "Genco Shipping & Trading Launches Shareholder Website to Defend Against Diana Shipping Takeover Attempt"
WHY
  underlying +2.8%/+2.2%/+3.7% (favorable peak +4.1%); position move +3.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~68% · IV residual ~-27% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized +31%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WMS-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI 0.99 · spread +0.0%
  greeks Δ0.066 Γ0.0069 Θ-0.043 · IV 0.485 · mid 1.50
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 43
  headline "Advanced Drainage Systems Beats Q4 Estimates and Raises FY2026 Guidance"
WHY
  underlying -1.2%/-2.8%/+0.9% (favorable peak +1.4%); position move +0.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~6% · IV residual ~34% [inferred].
  convexity Γ·S = 0.95. exit TIMEOUT → realized +31%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CLS-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 66.40 · spread +0.1%
  greeks Δ0.487 Γ0.0075 Θ-0.747 · IV 0.647 · mid 15.45
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.90) · RSI 63
  headline "Celestica Shares Surge After Analyst Upgrades and 1.6TbE Switch Launch Offset Post-Earnings Selloff"
WHY
  underlying +2.3%/+2.7%/+2.0% (favorable peak +6.2%); position move +2.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~25% · IV residual ~19% [inferred].
  convexity Γ·S = 3.07. exit TIMEOUT → realized +30%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WLAC-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 20.83 · spread +0.0%
  greeks Δ0.634 Γ0.0399 Θ-0.044 · IV 1.544 · mid 4.40
  overnight_score 2 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 69
  headline "Willow Lane Acquisition Corp. Announces Shareholder Approval of Business Combination with Boost Run Holding…"
WHY
  underlying +1.0%/+1.0%/+1.0% (favorable peak +4.6%); position move +1.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~3% · IV residual ~31% [inferred].
  convexity Γ·S = 0.74. exit TIMEOUT → realized +30%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DG-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI n/a · spread +0.1%
  greeks Δ0.865 Γ0.0299 Θ-0.106 · IV 0.432 · mid 7.51
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.40) · RSI 38
  headline "Dollar General (DG) Stock Gains 1.5% as Investors Eye Valuation Gap vs. Surging Retail Sector"
WHY
  underlying -1.3%/-1.2%/+1.0% (favorable peak +2.3%); position move +1.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~13% · IV residual ~21% [inferred].
  convexity Γ·S = 3.47. exit TIMEOUT → realized +30%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE POET-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 1.12 · spread +0.1%
  greeks Δ0.457 Γ0.1560 Θ-0.022 · IV 0.921 · mid 0.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 77
  headline "POET Technologies Jumps After Responding to Short Report and Clarifying PFIC Status"
WHY
  underlying +24.6%/+14.3%/+47.3% (favorable peak +51.2%); position move +47.3%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~634% · IV residual ~-586% [inferred].
  convexity Γ·S = 1.60. exit TRAIL → realized +29%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CENX-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 37 · V/OI 0.00 · spread +0.1%
  greeks Δ0.310 Γ0.0250 Θ-0.069 · IV 0.733 · mid 2.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 50
  headline "Century Aluminum Beats Q1 2026 Forecasts, Raises Q2 EBITDA Guidance Amid Mt. Holly Expansion"
WHY
  underlying +5.1%/+6.9%/+2.1% (favorable peak +8.6%); position move +2.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~16% · IV residual ~21% [inferred].
  convexity Γ·S = 1.50. exit TRAIL → realized +29%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE GS-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 2.21 · spread +0.1%
  greeks Δ0.340 Γ0.0060 Θ-0.561 · IV 0.277 · mid 11.66
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 58
  headline "DBS Bank Hikes Goldman Sachs Price Target to $1,050 Amid AI Partnership and Banking Strength"
WHY
  underlying +0.9%/+1.0%/+2.0% (favorable peak +2.5%); position move +2.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~55% · IV residual ~-12% [inferred].
  convexity Γ·S = 5.61. exit TIMEOUT → realized +29%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE IBKR-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 3.33 · spread +0.0%
  greeks Δ0.272 Γ0.0532 Θ-0.073 · IV 0.373 · mid 0.93
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 65
  headline "Interactive Brokers Launches Direct Access to South Korean Equities Amid Record Client Growth"
WHY
  underlying +0.8%/+1.4%/+1.1% (favorable peak +2.5%); position move +1.1%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~26% · IV residual ~26% [inferred].
  convexity Γ·S = 4.45. exit TIMEOUT → realized +28%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LNC-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.1%
  greeks Δ0.661 Γ0.0890 Θ-0.025 · IV 0.406 · mid 2.55
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 55
  headline "BofA Cuts Lincoln National (LNC) Price Target to $37; Maintains Neutral Rating"
WHY
  underlying -0.4%/+2.4%/+3.1% (favorable peak +3.4%); position move +3.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~29% · IV residual ~2% [inferred].
  convexity Γ·S = 3.21. exit TIMEOUT → realized +28%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CRML-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.558 Γ0.0814 Θ-0.024 · IV 1.130 · mid 1.79
  overnight_score 6 · flow HEDGING · catalyst M&A (0.90) · RSI 58
  headline "Critical Metals Corp. Closes Acquisition of Final 50.5% Interest in Tanbreez, Bringing Current Ownership to…"
WHY
  underlying -2.3%/+1.4%/+4.6% (favorable peak +10.6%); position move +4.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~18% · IV residual ~13% [inferred].
  convexity Γ·S = 1.04. exit TIMEOUT → realized +27%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CLS-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 506.00 · spread +0.1%
  greeks Δ0.441 Γ0.0056 Θ-1.043 · IV 0.924 · mid 20.81
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 74
  headline "Celestica (CLS) Expected to Announce Q1 Earnings April 27 as AI-Driven Infrastructure Demand Fuels Technica…"
WHY
  underlying +1.3%/+1.8%/+1.4% (favorable peak +3.9%); position move +1.4%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~12% · IV residual ~30% [inferred].
  convexity Γ·S = 2.21. exit TIMEOUT → realized +27%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ROKU-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 10.00 · spread +0.0%
  greeks Δ0.452 Γ0.0254 Θ-0.132 · IV 0.479 · mid 4.85
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 73
  headline "Roku Shares Up 2% Following Citigroup Price Target Hike to $120 Post-Earnings Beat"
WHY
  underlying -1.3%/+1.6%/+0.5% (favorable peak +3.0%); position move +0.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~6% · IV residual ~29% [inferred].
  convexity Γ·S = 3.20. exit TIMEOUT → realized +27%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE QCOM-2026-04-24-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.563 Γ0.0166 Θ-0.115 · IV 0.474 · mid 10.93
  overnight_score 8 · flow DIRECTIONAL · catalyst Partnership (0.90) · RSI 73
  headline "Qualcomm shares jump on report of OpenAI smartphone chip partnership"
WHY
  underlying +0.9%/+0.8%/+4.8% (favorable peak +8.2%); position move +4.8%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~37% · IV residual ~-7% [inferred].
  convexity Γ·S = 2.46. exit TIMEOUT → realized +26%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FSLR-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 2.00 · spread +0.0%
  greeks Δ0.453 Γ0.0106 Θ-0.218 · IV 0.599 · mid 11.84
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 55
  headline "First Solar Reports Q1 Earnings Beat with Record 29% Margins on AI Power Demand"
WHY
  underlying +4.9%/+4.7%/+8.7% (favorable peak +9.8%); position move +8.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~67% · IV residual ~-36% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized +26%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TE-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ0.492 Γ0.0818 Θ-0.027 · IV 1.376 · mid 1.62
  overnight_score 8 · flow DIRECTIONAL · catalyst Insider Activity (0.85) · RSI 78
  headline "T1 Energy (TE) Rockets 32% to New 52-Week Peak Following 10M Share Stake by AI-Investor Leopold Aschenbrenner"
WHY
  underlying +4.9%/+3.5%/+1.1% (favorable peak +9.4%); position move +1.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~3% · IV residual ~27% [inferred].
  convexity Γ·S = 0.86. exit TRAIL → realized +25%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AMPX-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.450 Γ0.0573 Θ-0.040 · IV 1.075 · mid 2.07
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 59
  headline "Amprius Technologies Q1 2026 Financial Results and Business Updates Scheduled for May 7"
WHY
  underlying -0.9%/-3.2%/+1.6% (favorable peak +3.1%); position move +1.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~7% · IV residual ~23% [inferred].
  convexity Γ·S = 1.21. exit TIMEOUT → realized +25%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DUOL-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 14 · V/OI n/a · spread +0.1%
  greeks Δ0.534 Γ0.0278 Θ-0.206 · IV 0.705 · mid 5.82
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 56
  headline "Duolingo Stock Surges as it Bounces Off 52-Week Lows Amid Renewed AI Strategy Optimism"
WHY
  underlying -2.8%/+1.3%/-0.8% (favorable peak +3.8%); position move -0.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-8% · IV residual ~43% [inferred].
  convexity Γ·S = 2.87. exit TIMEOUT → realized +25%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FLY-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 10.00 · spread +0.0%
  greeks Δ0.374 Γ0.0456 Θ-0.118 · IV 1.089 · mid 2.08
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 60
  headline "Firefly Aerospace Reports Record $80.9M Q1 Revenue and EPS Beat, Fueling 22% Post-Earnings Surge"
WHY
  underlying -3.6%/-0.9%/-0.8% (favorable peak +3.3%); position move -0.8%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-6% · IV residual ~47% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized +24%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ETN-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 29.00 · spread +0.1%
  greeks Δ0.464 Γ0.0089 Θ-0.270 · IV 0.357 · mid 14.55
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 66
  headline "Eaton Expands Operations in Nebraska to Meet Increasing Switchgear Demand Driven by AI Data Center Boom"
WHY
  underlying +0.3%/+0.9%/+1.9% (favorable peak +3.3%); position move +1.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~24% · IV residual ~5% [inferred].
  convexity Γ·S = 3.62. exit TIMEOUT → realized +24%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MELI-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.338 Γ0.0015 Θ-1.656 · IV 0.491 · mid 57.30
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 52
  headline "Is It Time To Reassess MercadoLibre (MELI) After Steady Gains And DCF Upside?"
WHY
  underlying +1.4%/+1.7%/-1.0% (favorable peak +3.6%); position move -1.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-10% · IV residual ~43% [inferred].
  convexity Γ·S = 2.66. exit TIMEOUT → realized +24%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MS-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI n/a · spread +0.1%
  greeks Δ0.708 Γ0.0307 Θ-0.134 · IV 0.297 · mid 8.32
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 66
  headline "BMO Capital Markets Increases Morgan Stanley (NYSE: MS) Price Target to $220.00"
WHY
  underlying -0.3%/+0.8%/+0.9% (favorable peak +2.1%); position move +0.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~15% · IV residual ~15% [inferred].
  convexity Γ·S = 5.78. exit TIMEOUT → realized +24%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CCJ-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 6.11 · spread +0.0%
  greeks Δ0.405 Γ0.0305 Θ-0.187 · IV 0.565 · mid 3.88
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 49
  headline "Scotiabank Hikes Cameco Price Target to $175 as Nuclear Renaissance Accelerates Amid Operational Pullback"
WHY
  underlying +2.9%/+0.2%/-1.2% (favorable peak +4.1%); position move -1.2%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-14% · IV residual ~53% [inferred].
  convexity Γ·S = 3.57. exit TRAIL → realized +24%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AXTI-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 15 · V/OI n/a · spread +0.0%
  greeks Δ0.575 Γ0.0120 Θ-0.422 · IV 1.515 · mid 13.70
  overnight_score 8 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 55
  headline "AXT Inc. Forecasts Record Indium Phosphide Demand for AI Infrastructure; Guides Q2 Profitability Well Above…"
WHY
  underlying +15.7%/+34.6%/+26.8% (favorable peak +36.9%); position move +26.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~118% · IV residual ~-84% [inferred].
  convexity Γ·S = 1.26. exit TIMEOUT → realized +24%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE MO-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 44 · V/OI 1.67 · spread +0.0%
  greeks Δ0.362 Γ0.0660 Θ-0.023 · IV 0.238 · mid 1.05
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 55
  headline "Altria Group (MO) Beats Q1 Estimates, Rolls Out on! PLUS to 100,000 Stores"
WHY
  underlying +2.4%/+3.6%/+4.6% (favorable peak +4.7%); position move +4.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~110% · IV residual ~-80% [inferred].
  convexity Γ·S = 4.62. exit TIMEOUT → realized +24%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RDDT-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 45 · V/OI n/a · spread +0.1%
  greeks Δ0.288 Γ0.0100 Θ-0.135 · IV 0.611 · mid 5.80
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 53
  headline "Assessing Reddit (RDDT) Valuation After A Mixed Month Of Share Price Moves"
WHY
  underlying -4.5%/-3.4%/-2.0% (favorable peak +1.0%); position move -2.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-16% · IV residual ~46% [inferred].
  convexity Γ·S = 1.60. exit TIMEOUT → realized +24%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PSX-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.115 Γ0.0107 Θ-0.058 · IV 0.347 · mid 1.12
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 63
  headline "Goldman Sachs Raises Phillips 66 Price Target to $207 on Strong Refining Outlook"
WHY
  underlying +1.4%/-0.3%/-3.2% (favorable peak +2.7%); position move -3.2%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-59% · IV residual ~98% [inferred].
  convexity Γ·S = 1.92. exit TIMEOUT → realized +24%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CRDO-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.396 Γ0.0177 Θ-0.182 · IV 0.581 · mid 5.19
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.95) · RSI 67
  headline "Credo to Acquire DustPhotonics for $750M to Accelerate 1.6T/3.2T Silicon Photonics Roadmap"
WHY
  underlying +18.7%/+25.3%/+18.3% (favorable peak +25.8%); position move +18.3%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~188% · IV residual ~-154% [inferred].
  convexity Γ·S = 2.38. exit TRAIL → realized +23%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CAT-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 3.92 · spread +0.1%
  greeks Δ0.396 Γ0.0042 Θ-0.656 · IV 0.372 · mid 25.73
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 75
  headline "Caterpillar Surges 10% to Record High After Blowout Q1 Results Fueled by AI Power Demand"
WHY
  underlying -0.0%/-1.7%/+1.6% (favorable peak +2.1%); position move +1.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~22% · IV residual ~9% [inferred].
  convexity Γ·S = 3.76. exit TIMEOUT → realized +23%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AXTI-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 30.00 · spread +0.0%
  greeks Δ0.428 Γ0.0094 Θ-0.396 · IV 1.431 · mid 11.38
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.90) · RSI 62
  headline "AXT Inc. (AXTI) Shares Surge 16% on Record AI Backlog and Q2 Profitability Guidance"
WHY
  underlying +16.4%/+9.6%/+1.4% (favorable peak +18.3%); position move +1.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~7% · IV residual ~27% [inferred].
  convexity Γ·S = 1.14. exit TIMEOUT → realized +23%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE VZ-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI n/a · spread +0.1%
  greeks Δ0.298 Γ0.0691 Θ-0.019 · IV 0.314 · mid 0.72
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 47
  headline "Verizon to report first-quarter earnings on April 27, 2026"
WHY
  underlying -1.8%/-0.3%/+0.0% (favorable peak +3.0%); position move +0.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~1% · IV residual ~30% [inferred].
  convexity Γ·S = 3.26. exit TRAIL → realized +23%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DASH-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 5.60 · spread +0.0%
  greeks Δ0.405 Γ0.0272 Θ-0.267 · IV 0.512 · mid 3.83
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 42
  headline "DoorDash Rebound Signal: Analysts See Double-Digit Upside Following Strong Q2 Guidance and Retail Expansion"
WHY
  underlying -4.9%/-1.2%/-2.1% (favorable peak +0.0%); position move -2.1%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-36% · IV residual ~80% [inferred].
  convexity Γ·S = 4.43. exit TIMEOUT → realized +23%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE GEL-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI 0.22 · spread +0.1%
  greeks Δ0.865 Γ0.1651 Θ-0.003 · IV 0.252 · mid 1.80
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 35
  headline "Genesis Energy Q1 EPS Misses by 122% on Operational Issues; Maintains 2026 Guidance"
WHY
  underlying +0.4%/-0.3%/-3.8% (favorable peak +0.4%); position move -3.8%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-30% · IV residual ~53% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized +23%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WES-2026-05-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.104 Γ0.0590 Θ-0.007 · IV 0.219 · mid 0.12
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 69
  headline "Western Midstream beats Q1 expectations, announces $1.6B acquisition and receives Stifel upgrade"
WHY
  underlying +1.1%/+1.4%/+3.9% (favorable peak +4.3%); position move +3.9%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~154% · IV residual ~-114% [inferred].
  convexity Γ·S = 2.68. exit TRAIL → realized +23%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAR-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ0.471 Γ0.0032 Θ-2.319 · IV 1.935 · mid 27.30
  overnight_score 5 · flow DIRECTIONAL · catalyst Short Squeeze (0.95) · RSI 94
  headline "Avis Budget Group jumps 24% as short-squeeze and TSA airport chaos intensify"
WHY
  underlying +10.9%/+6.7%/+21.0% (favorable peak +21.8%); position move +21.0%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~135% · IV residual ~-87% [inferred].
  convexity Γ·S = 1.19. exit TRAIL → realized +22%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE PNC-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 1.71 · spread +0.0%
  greeks Δ0.452 Γ0.0503 Θ-0.202 · IV 0.253 · mid 2.56
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 44
  headline "Big Bank Earnings Gave Financials a Lift, But Wall Street Is Still Cautious"
WHY
  underlying -0.3%/+0.1%/-0.1% (favorable peak +1.1%); position move -0.1%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~-3% · IV residual ~49% [inferred].
  convexity Γ·S = 10.73. exit TRAIL → realized +22%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AA-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 3.35 · spread +0.1%
  greeks Δ0.329 Γ0.0438 Θ-0.062 · IV 0.487 · mid 1.59
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 51
  headline "B. Riley Raises Alcoa (AA) Price Target to $96 on Aluminum Supply Disruptions"
WHY
  underlying +3.5%/+4.7%/+1.0% (favorable peak +6.7%); position move +1.0%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~14% · IV residual ~20% [inferred].
  convexity Γ·S = 2.86. exit TRAIL → realized +22%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIX-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 4.50 · spread +0.1%
  greeks Δ0.385 Γ0.0012 Θ-2.260 · IV 0.692 · mid 70.55
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 66
  headline "Comfort Systems USA (FIX) Rebounds as Analysts Raise EPS Forecasts Ahead of Q1 Results"
WHY
  underlying +1.8%/+1.4%/+4.5% (favorable peak +4.8%); position move +4.5%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~40% · IV residual ~-9% [inferred].
  convexity Γ·S = 2.04. exit TIMEOUT → realized +22%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FDX-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.478 Γ0.0120 Θ-0.197 · IV 0.280 · mid 11.36
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.92) · RSI 62
  headline "FedEx Freight Spin-Off Confirmed for June 1 as Analysts Raise Targets to $470 Following Massive Earnings Beat"
WHY
  underlying +3.0%/+3.4%/+3.6% (favorable peak +4.9%); position move +3.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~58% · IV residual ~-31% [inferred].
  convexity Γ·S = 4.58. exit TIMEOUT → realized +22%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ULTA-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.506 Γ0.0084 Θ-0.418 · IV 0.351 · mid 28.39
  overnight_score 1 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 38
  headline "Analysts See 'Ultimate Entry' as Ulta Beauty Stabilizes Following Post-Earnings Reset"
WHY
  underlying +1.2%/+2.4%/+2.4% (favorable peak +4.2%); position move +2.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~23% · IV residual ~3% [inferred].
  convexity Γ·S = 4.42. exit TIMEOUT → realized +22%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HUM-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 6.17 · spread +0.0%
  greeks Δ0.672 Γ0.0097 Θ-0.223 · IV 0.574 · mid 21.46
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 76
  headline "Humana Inc. to Release First Quarter 2026 Results on April 29, 2026"
WHY
  underlying +2.7%/+8.7%/+5.7% (favorable peak +10.4%); position move +5.7%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~40% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.18. exit TIMEOUT → realized +21%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TLN-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 175.50 · spread +0.1%
  greeks Δ0.420 Γ0.0080 Θ-0.668 · IV 0.656 · mid 11.20
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 60
  headline "Talen Energy Completes $4 Billion Refinancing and Expands 1,920 MW AWS Nuclear Deal Ahead of Q1 Earnings"
WHY
  underlying -0.1%/+3.3%/+3.4% (favorable peak +5.1%); position move +3.4%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~47% · IV residual ~-7% [inferred].
  convexity Γ·S = 3.00. exit TIMEOUT → realized +21%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE KLAC-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 1.77 · spread +0.0%
  greeks Δ0.547 Γ0.0017 Θ-2.216 · IV 0.529 · mid 97.72
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 69
  headline "KLA Corporation (KLAC) slated to reveal earnings on April 29 as Wolfe Research raises price target to $2,000"
WHY
  underlying +0.2%/+6.8%/+4.9% (favorable peak +7.0%); position move +4.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~49% · IV residual ~-21% [inferred].
  convexity Γ·S = 3.02. exit TIMEOUT → realized +21%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ADI-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.478 Γ0.0109 Θ-0.310 · IV 0.369 · mid 12.15
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 78
  headline "S&P Global Ratings Upgrades Analog Devices to 'A' Citing Robust Business Resilience and Product Leadership"
WHY
  underlying -1.5%/+0.1%/+6.0% (favorable peak +7.2%); position move +6.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~90% · IV residual ~-61% [inferred].
  convexity Γ·S = 4.15. exit TIMEOUT → realized +21%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LQDA-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 7 · V/OI 50.00 · spread +0.0%
  greeks Δ0.781 Γ0.0391 Θ-0.150 · IV 0.884 · mid 4.82
  overnight_score 6 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 87
  headline "9-Day Rally Sends Liquidia Stock Up 55% Following Blockbuster Q1 Earnings and Yutrepia Launch Success"
WHY
  underlying -4.0%/-3.9%/+1.1% (favorable peak +2.1%); position move +1.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~11% · IV residual ~19% [inferred].
  convexity Γ·S = 2.32. exit TIMEOUT → realized +21%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE LUNR-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 44 · V/OI n/a · spread +0.0%
  greeks Δ0.361 Γ0.0468 Θ-0.035 · IV 0.968 · mid 1.77
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 59
  headline "Stifel Downgrades LUNR to Hold on Valuation, But Raises Price Target as NASA LTV Award Looms"
WHY
  underlying +0.9%/+15.3%/+16.5% (favorable peak +19.2%); position move +16.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~80% · IV residual ~-53% [inferred].
  convexity Γ·S = 1.11. exit TIMEOUT → realized +21%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE ISRG-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.356 Γ0.0096 Θ-0.775 · IV 0.511 · mid 9.85
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 48
  headline "Intuitive Surgical (ISRG) Set to Report Q1 Earnings on April 21 Amid Rising Institutional Interest"
WHY
  underlying +0.2%/-2.0%/+0.4% (favorable peak +1.5%); position move +0.4%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~7% · IV residual ~37% [inferred].
  convexity Γ·S = 4.48. exit TIMEOUT → realized +20%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE STX-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 34.33 · spread +0.1%
  greeks Δ0.396 Γ0.0038 Θ-1.495 · IV 0.731 · mid 24.19
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 84
  headline "Seagate Capacity Allocated Through 2027 as AI Storage Demand Triggers $1,000 Price Targets"
WHY
  underlying +1.6%/+6.1%/+8.2% (favorable peak +9.0%); position move +8.2%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~97% · IV residual ~-59% [inferred].
  convexity Γ·S = 2.75. exit TRAIL → realized +20%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AA-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.417 Γ0.0277 Θ-0.081 · IV 0.670 · mid 4.98
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 58
  headline "Alcoa (AA) lifts Q1 2026 earnings as aluminum prices rise despite weaker revenue"
WHY
  underlying -6.8%/-5.5%/-4.6% (favorable peak -4.1%); position move -4.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-27% · IV residual ~52% [inferred].
  convexity Γ·S = 1.95. exit TIMEOUT → realized +20%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MRVL-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 10.18 · spread +0.0%
  greeks Δ0.467 Γ0.0098 Θ-0.289 · IV 0.887 · mid 12.55
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 77
  headline "Marvell Technology Re-Rated as AI Infrastructure Leader Following Scalable Earnings Growth Projections"
WHY
  underlying -0.1%/-0.9%/+2.2% (favorable peak +4.7%); position move +2.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~13% · IV residual ~13% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized +20%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ROKU-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 22.00 · spread +0.0%
  greeks Δ0.411 Γ0.0160 Θ-0.122 · IV 0.631 · mid 6.61
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 74
  headline "Roku Hits New 12-Month High After Surpassing 100 Million Streaming Households Milestone"
WHY
  underlying +2.2%/-1.8%/+1.9% (favorable peak +3.3%); position move +1.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~13% · IV residual ~12% [inferred].
  convexity Γ·S = 1.86. exit TIMEOUT → realized +20%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MRVL-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.450 Γ0.0086 Θ-0.308 · IV 0.947 · mid 12.90
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 63
  headline "Shares of networking chips designer Marvell Technology MRVL fell 5.3% after a broad-based sell-off hit the …"
WHY
  underlying +4.3%/+10.6%/+12.9% (favorable peak +15.2%); position move +12.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~76% · IV residual ~-49% [inferred].
  convexity Γ·S = 1.45. exit TIMEOUT → realized +20%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE LUNR-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.1%
  greeks Δ0.455 Γ0.0507 Θ-0.073 · IV 1.204 · mid 1.85
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 67
  headline "Rocket Lab Surges 9%, Intuitive Machines Jumps 6% as Space Sector Catches Fire on NASA Contracts and New Tech"
WHY
  underlying +1.1%/+0.9%/+2.0% (favorable peak +9.5%); position move +2.0%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~13% · IV residual ~18% [inferred].
  convexity Γ·S = 1.38. exit TRAIL → realized +19%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIG-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 38 · V/OI 50.00 · spread +0.0%
  greeks Δ0.361 Γ0.0564 Θ-0.033 · IV 1.019 · mid 1.42
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 51
  headline "Figma (FIG) Rises 7% Ahead of May 14 Earnings as AI Disruption Fears Subside"
WHY
  underlying -2.7%/-3.4%/+3.0% (favorable peak +7.7%); position move +3.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~15% · IV residual ~11% [inferred].
  convexity Γ·S = 1.13. exit TIMEOUT → realized +19%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CRWV-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ0.495 Γ0.0125 Θ-0.158 · IV 0.918 · mid 11.07
  overnight_score 6 · flow MECHANICAL · catalyst Partnership (0.95) · RSI 67
  headline "CoreWeave Secures $21B Meta Deal and Anthropic Partnership in 48-Hour AI Infrastructure Blitz"
WHY
  underlying +8.1%/+14.9%/+16.4% (favorable peak +19.0%); position move +16.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~75% · IV residual ~-51% [inferred].
  convexity Γ·S = 1.28. exit TIMEOUT → realized +19%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE FN-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 2.27 · spread +0.1%
  greeks Δ0.604 Γ0.0022 Θ-1.994 · IV 1.192 · mid 89.00
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 60
  headline "Fabrinet (FN) Earnings Expected to Grow: Should You Buy?"
WHY
  underlying -6.9%/-6.0%/-0.2% (favorable peak +0.4%); position move -0.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-1% · IV residual ~27% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized +19%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE IRM-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.345 Γ0.0381 Θ-0.186 · IV 0.482 · mid 2.09
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 61
  headline "Iron Mountain Pulls Back 5.7% From Record Highs Following Post-Earnings Surge and Insider Share Sale"
WHY
  underlying -0.1%/+1.2%/-0.9% (favorable peak +1.5%); position move -0.9%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~-19% · IV residual ~65% [inferred].
  convexity Γ·S = 4.81. exit TIMEOUT → realized +19%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RKLB-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 20 · V/OI 2.14 · spread +0.1%
  greeks Δ0.426 Γ0.0120 Θ-0.321 · IV 1.130 · mid 11.18
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 71
  headline "Rocket Lab Hits Engine Production Milestone as Space Force Visit Ignites Defense Optimism"
WHY
  underlying +5.1%/+2.0%/+7.6% (favorable peak +10.9%); position move +7.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~36% · IV residual ~-9% [inferred].
  convexity Γ·S = 1.50. exit TIMEOUT → realized +19%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CF-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI 83.33 · spread +0.0%
  greeks Δ0.498 Γ0.0199 Θ-0.131 · IV 0.557 · mid 6.95
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 52
  headline "CF Industries slides 3.7% as fertilizer 'risk premium' cools ahead of Q1 results"
WHY
  underlying -1.1%/+2.5%/+0.5% (favorable peak +3.2%); position move +0.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~4% · IV residual ~20% [inferred].
  convexity Γ·S = 2.46. exit TIMEOUT → realized +19%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HUT-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ0.448 Γ0.0299 Θ-0.248 · IV 0.980 · mid 3.71
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 76
  headline "Cantor Fitzgerald Hikes Hut 8 Price Target to $80, Citing AI Infrastructure Growth"
WHY
  underlying -3.1%/+2.2%/-0.3% (favorable peak +5.3%); position move -0.3%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-3% · IV residual ~41% [inferred].
  convexity Γ·S = 2.36. exit TRAIL → realized +19%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE GE-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 54.14 · spread +0.1%
  greeks Δ0.230 Γ0.0159 Θ-0.281 · IV 0.372 · mid 2.41
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.70) · RSI 53
  headline "GE Aerospace Maintains 'Strong Buy' Consensus as Analysts Target $350+ Following Strategic Defense Engine Wins"
WHY
  underlying -1.1%/-2.0%/-3.1% (favorable peak +0.0%); position move -3.1%.
  decomp [first-order]: theta drag ~35% of premium / 3d · delta capture ~-88% · IV residual ~141% [inferred].
  convexity Γ·S = 4.78. exit TRAIL → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WDAY-2026-04-28-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 3.33 · spread +0.0%
  greeks Δ0.406 Γ0.0285 Θ-0.280 · IV 0.696 · mid 3.70
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 45
  headline "Workday Stock Hits a Five-Year Low as $400 Million in AI ARR Goes Unnoticed"
WHY
  underlying +1.0%/+1.0%/+4.8% (favorable peak +8.1%); position move +4.8%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~63% · IV residual ~-23% [inferred].
  convexity Γ·S = 3.45. exit TRAIL → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NVTS-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 8 · V/OI n/a · spread +0.1%
  greeks Δ0.324 Γ0.0500 Θ-0.148 · IV 1.605 · mid 1.48
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 67
  headline "Navitas Semiconductor (NASDAQ:NVTS) Sets New 12-Month High - What's Next?"
WHY
  underlying -1.3%/-7.9%/-13.9% (favorable peak +3.2%); position move -13.9%.
  decomp [first-order]: theta drag ~30% of premium / 3d · delta capture ~-88% · IV residual ~136% [inferred].
  convexity Γ·S = 1.44. exit TRAIL → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE EQR-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ0.312 Γ0.0904 Θ-0.023 · IV 0.233 · mid 0.97
  overnight_score 1 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 50
  headline "Equity Residential reaches $56 million settlement in antitrust class action"
WHY
  underlying +3.6%/+4.9%/+2.2% (favorable peak +4.9%); position move +2.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~44% · IV residual ~-19% [inferred].
  convexity Γ·S = 5.47. exit TRAIL → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIX-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ0.291 Γ0.0010 Θ-1.711 · IV 0.679 · mid 56.26
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 65
  headline "Four Data Center Stocks Flash Bullish Signs, Outpace Market Recovery"
WHY
  underlying +2.2%/+3.6%/+3.5% (favorable peak +5.0%); position move +3.5%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~29% · IV residual ~-2% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized +18%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BE-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ0.319 Γ0.0041 Θ-0.432 · IV 0.925 · mid 11.75
  overnight_score 7 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 79
  headline "Bloom Energy Shares Skyrocket on Blowout Q1 Earnings and Massive 2.45 GW Oracle AI Data Center Deal"
WHY
  underlying -1.6%/+0.9%/+0.2% (favorable peak +5.2%); position move +0.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~2% · IV residual ~27% [inferred].
  convexity Γ·S = 1.19. exit TIMEOUT → realized +17%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FSLY-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 22 · V/OI 3.00 · spread +0.0%
  greeks Δ0.410 Γ0.0431 Θ-0.080 · IV 1.471 · mid 2.09
  overnight_score 3 · flow MIXED · catalyst — (—) · RSI 49
WHY
  underlying -0.9%/-5.7%/+2.4% (favorable peak +3.0%); position move +2.4%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~12% · IV residual ~17% [inferred].
  convexity Γ·S = 1.08. exit TIMEOUT → realized +17%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HUM-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 4.74 · spread +0.1%
  greeks Δ0.321 Γ0.0114 Θ-0.130 · IV 0.381 · mid 5.76
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 73
  headline "Humana Price Targets Raised by Multiple Analysts Following Earnings 'Reset' and Guidance Reaffirmation"
WHY
  underlying +0.7%/+3.5%/+3.8% (favorable peak +5.8%); position move +3.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~51% · IV residual ~-27% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized +17%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIGR-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 3.33 · spread +0.0%
  greeks Δ0.341 Γ0.0780 Θ-0.113 · IV 0.732 · mid 1.42
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 71
  headline "Figure Technology Solutions Reports Record Q1 2026 Results; Mizuho Raises Price Target to $55"
WHY
  underlying +0.1%/-10.7%/-16.2% (favorable peak +3.4%); position move -16.2%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~-168% · IV residual ~209% [inferred].
  convexity Γ·S = 3.37. exit TRAIL → realized +17%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PGR-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ0.499 Γ0.0215 Θ-0.113 · IV 0.323 · mid 6.35
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 48
  headline "Progressive (PGR) Expected to Announce Earnings on Wednesday; Zacks Predicts a Beat"
WHY
  underlying -1.5%/+0.8%/+2.0% (favorable peak +2.9%); position move +2.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~31% · IV residual ~-9% [inferred].
  convexity Γ·S = 4.30. exit TIMEOUT → realized +17%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WDC-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.455 Γ0.0042 Θ-0.542 · IV 0.840 · mid 31.65
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.82) · RSI 68
  headline "Citi Raises Western Digital Target to $405 as AI Data Demand Supercharges Storage Pricing"
WHY
  underlying +3.0%/+3.4%/+6.1% (favorable peak +7.7%); position move +6.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~32% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized +17%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE C-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 0.72 · spread +0.1%
  greeks Δ0.863 Γ0.0210 Θ-0.110 · IV 0.486 · mid 11.17
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.35) · RSI 53
  headline "SoftBank-backed Opay Taps Citigroup for U.S. IPO Amid Global Stagflation Warnings"
WHY
  underlying +1.9%/+1.6%/+2.8% (favorable peak +4.7%); position move +2.8%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~27% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.64. exit TIMEOUT → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE APA-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 33 · V/OI 0.43 · spread +0.1%
  greeks Δ0.635 Γ0.0649 Θ-0.033 · IV 0.491 · mid 2.12
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 53
  headline "APA Corporation Price Surges as Analysts Lift Targets to $46 on Stronger Free Cash Flow and Production Outlook"
WHY
  underlying +3.0%/+5.0%/+0.9% (favorable peak +6.7%); position move +0.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~10% · IV residual ~11% [inferred].
  convexity Γ·S = 2.53. exit TRAIL → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LLY-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 45 · V/OI 27.00 · spread +0.1%
  greeks Δ0.356 Γ0.0033 Θ-0.498 · IV 0.337 · mid 26.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.78) · RSI 56
  headline "Eli Lilly's Tirzepatide Clinical Trial Footprint Expands 30% as Company Celebrates 150-Year Anniversary at …"
WHY
  underlying +2.2%/+4.9%/+3.9% (favorable peak +5.6%); position move +3.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~50% · IV residual ~-29% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WOLF-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI n/a · spread +0.1%
  greeks Δ0.351 Γ0.0330 Θ-0.134 · IV 1.304 · mid 2.52
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.85) · RSI 79
  headline "Wolfspeed Shares Surge as Debt Refinancing and AI Pivot Offset Massive Q3 Earnings Miss"
WHY
  underlying +4.8%/+8.2%/+16.8% (favorable peak +25.2%); position move +16.8%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~101% · IV residual ~-69% [inferred].
  convexity Γ·S = 1.42. exit TIMEOUT → realized +16%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE TWLO-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ0.254 Γ0.0130 Θ-0.182 · IV 0.747 · mid 2.67
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 59
  headline "Twilio Surges 8% as Voice AI Narrative and Analyst Upgrades Drive Pre-Earnings Momentum"
WHY
  underlying +2.2%/+4.5%/+8.6% (favorable peak +8.6%); position move +8.6%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~110% · IV residual ~-73% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LULU-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 10.00 · spread +0.0%
  greeks Δ0.410 Γ0.0155 Θ-0.146 · IV 0.621 · mid 6.90
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.85) · RSI 46
  headline "Lululemon Resolves Feud With Founder Chip Wilson"
WHY
  underlying +0.2%/+0.1%/+0.8% (favorable peak +2.5%); position move +0.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~6% · IV residual ~16% [inferred].
  convexity Γ·S = 2.04. exit TIMEOUT → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MPWR-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 40 · V/OI 0.61 · spread +0.0%
  greeks Δ0.348 Γ0.0013 Θ-1.388 · IV 0.549 · mid 72.47
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 63
  headline "KeyBanc Raises Monolithic Power Systems (MPWR) Price Target to $2,000 on AI Strength"
WHY
  underlying +3.8%/-0.1%/+3.1% (favorable peak +4.7%); position move +3.1%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~24% · IV residual ~-2% [inferred].
  convexity Γ·S = 2.03. exit TIMEOUT → realized +16%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AMAT-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI 10.88 · spread +0.1%
  greeks Δ0.435 Γ0.0054 Θ-0.470 · IV 0.612 · mid 27.87
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 62
  headline "Semiconductor Equipment Stocks Slide on Fears of Stricter U.S. Export Controls to China"
WHY
  underlying -5.9%/-5.5%/-2.6% (favorable peak -2.2%); position move -2.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-16% · IV residual ~37% [inferred].
  convexity Γ·S = 2.20. exit TIMEOUT → realized +16%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE FTNT-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 26 · V/OI n/a · spread +0.0%
  greeks Δ0.411 Γ0.0263 Θ-0.115 · IV 0.414 · mid 3.58
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 88
  headline "Fortinet Sees AI Data Centers, OT Security and Sovereign SASE Fueling Pipeline"
WHY
  underlying +0.0%/-4.5%/-3.2% (favorable peak +0.7%); position move -3.2%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-49% · IV residual ~74% [inferred].
  convexity Γ·S = 3.52. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE EL-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 38 · V/OI 57.00 · spread +0.1%
  greeks Δ0.155 Γ0.0205 Θ-0.037 · IV 0.446 · mid 1.15
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.90) · RSI 58
  headline "Estée Lauder Rallies as 40% Earnings Beat and China Comeback Narrative Ignite Turnaround"
WHY
  underlying +1.9%/+6.6%/+4.9% (favorable peak +8.1%); position move +4.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~53% · IV residual ~-28% [inferred].
  convexity Γ·S = 1.67. exit TRAIL → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SCCO-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ0.704 Γ0.0154 Θ-0.141 · IV 0.447 · mid 19.01
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 55
  headline "Southern Copper Declares $1.00 Dividend as Record Q1 Earnings Support Bullish Outlook"
WHY
  underlying +3.2%/+3.2%/+6.8% (favorable peak +7.0%); position move +6.8%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~45% · IV residual ~-28% [inferred].
  convexity Γ·S = 2.76. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LLY-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.415 Γ0.0037 Θ-0.616 · IV 0.364 · mid 27.60
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 53
  headline "Eli Lilly (LLY) Surges 9.6% on Massive Q1 Earnings Beat and Guidance Hike"
WHY
  underlying +3.1%/+3.6%/+5.8% (favorable peak +6.2%); position move +5.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~82% · IV residual ~-60% [inferred].
  convexity Γ·S = 3.46. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MMM-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 3.08 · spread +0.0%
  greeks Δ0.471 Γ0.0397 Θ-0.095 · IV 0.273 · mid 3.60
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.78) · RSI 58
  headline "3M Joins AI Infrastructure Partnership on Expanded Beam Optical Connectivity for Data Centers"
WHY
  underlying +0.6%/+1.6%/+2.4% (favorable peak +3.4%); position move +2.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~47% · IV residual ~-24% [inferred].
  convexity Γ·S = 6.02. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIX-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.401 Γ0.0013 Θ-2.223 · IV 0.702 · mid 81.62
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.40) · RSI 63
  headline "Stifel Raises Comfort Systems USA (FIX) Price Target to $1,819 Amid Data Center Growth"
WHY
  underlying +2.8%/+4.6%/+4.2% (favorable peak +7.0%); position move +4.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~34% · IV residual ~-11% [inferred].
  convexity Γ·S = 2.01. exit TIMEOUT → realized +15%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE USAR-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.426 Γ0.0781 Θ-0.058 · IV 1.005 · mid 1.02
  overnight_score 8 · flow DIRECTIONAL · catalyst M&A (0.95) · RSI 69
  headline "USAR to Acquire Serra Verde for $2.8 Billion—Deal Creates Largest Non-Asian Rare Earth Producer"
WHY
  underlying +1.2%/+12.5%/+2.3% (favorable peak +14.9%); position move +2.3%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~21% · IV residual ~10% [inferred].
  convexity Γ·S = 1.76. exit TRAIL → realized +14%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CNC-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 0.58 · spread +0.0%
  greeks Δ0.419 Γ0.1102 Θ-0.074 · IV 0.378 · mid 1.23
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 66
  headline "Barclays raises Centene (CNC) price target to $75 from $63, citing managed care tailwinds"
WHY
  underlying +2.8%/+3.0%/+4.2% (favorable peak +4.8%); position move +4.2%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~81% · IV residual ~-49% [inferred].
  convexity Γ·S = 6.30. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE GE-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.277 Γ0.0103 Θ-0.136 · IV 0.340 · mid 4.65
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 41
  headline "GE Aerospace (NYSE:GE) Shares Up 2.3% After Analyst Upgrade and Q1 Earnings Beat"
WHY
  underlying +0.8%/+0.8%/+2.4% (favorable peak +2.5%); position move +2.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~41% · IV residual ~-18% [inferred].
  convexity Γ·S = 2.91. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE STX-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI 1.00 · spread +0.1%
  greeks Δ0.738 Γ0.0038 Θ-1.466 · IV 0.928 · mid 44.13
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 72
  headline "Seagate (STX) Hits All-Time High as UBS Joins Bullish Chorus Ahead of Earnings"
WHY
  underlying +3.6%/+5.0%/+4.7% (favorable peak +8.6%); position move +4.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~44% · IV residual ~-20% [inferred].
  convexity Γ·S = 2.13. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WES-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 0.01 · spread +0.0%
  greeks Δ0.560 Γ0.2919 Θ-0.031 · IV 0.219 · mid 0.65
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 61
  headline "Western Midstream raised at Stifel on strong start to 2026, moving higher in 2027"
WHY
  underlying +0.4%/+1.5%/+2.8% (favorable peak +3.5%); position move +2.8%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~106% · IV residual ~-78% [inferred].
  convexity Γ·S = 12.64. exit TRAIL → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FCX-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 29 · V/OI 10.08 · spread +0.0%
  greeks Δ0.709 Γ0.0322 Θ-0.066 · IV 0.592 · mid 6.68
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 53
  headline "Barclays Initiates Coverage of Freeport-McMoRan (FCX) with Overweight Rating"
WHY
  underlying +3.5%/+3.3%/+5.4% (favorable peak +6.1%); position move +5.4%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~36% · IV residual ~-19% [inferred].
  convexity Γ·S = 2.05. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SBGI-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.621 Γ0.1748 Θ-0.013 · IV 0.488 · mid 0.78
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 72
  headline "Sinclair (SBGI) Analyst Consensus Remains 'Buy' as Management Explores Strategic Separations and Partnershi…"
WHY
  underlying +4.4%/+5.7%/+7.9% (favorable peak +10.0%); position move +7.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~98% · IV residual ~-79% [inferred].
  convexity Γ·S = 2.72. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SHAK-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.458 Γ0.0204 Θ-0.098 · IV 0.589 · mid 6.09
  overnight_score 3 · flow MIXED · catalyst — (—) · RSI 62
WHY
  underlying +2.1%/+4.2%/+2.6% (favorable peak +6.2%); position move +2.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~19% · IV residual ~-1% [inferred].
  convexity Γ·S = 2.01. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAT-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 5.33 · spread +0.0%
  greeks Δ0.483 Γ0.0041 Θ-0.884 · IV 0.482 · mid 34.11
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 62
  headline "Caterpillar Q1 Earnings: Power Generation Demand Surges on Data Center Growth as Shares Dip on Cautious Gui…"
WHY
  underlying +9.9%/+9.8%/+8.0% (favorable peak +11.7%); position move +8.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~92% · IV residual ~-70% [inferred].
  convexity Γ·S = 3.34. exit TIMEOUT → realized +14%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CVNA-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.405 Γ0.0046 Θ-0.802 · IV 0.881 · mid 22.02
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.85) · RSI 66
  headline "Carvana (CVNA) Option Markets Price in 12.2% Move Ahead of April 29 Earnings and May Stock Split"
WHY
  underlying +1.5%/+0.9%/+0.8% (favorable peak +2.2%); position move +0.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~6% · IV residual ~18% [inferred].
  convexity Γ·S = 1.84. exit TIMEOUT → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ANET-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ0.267 Γ0.0105 Θ-0.172 · IV 0.625 · mid 5.39
  overnight_score 4 · flow DIRECTIONAL · catalyst Insider Activity (0.65) · RSI 69
  headline "Arista Networks (NYSE:ANET) Shares Down 2.5% After Insider Selling"
WHY
  underlying -4.2%/-2.2%/+0.1% (favorable peak +0.6%); position move +0.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~1% · IV residual ~22% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized +13%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE DIS-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.264 Γ0.0291 Θ-0.051 · IV 0.338 · mid 1.77
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 61
  headline "Disney Shares Slip 1.3% in Quiet Trading Session Ahead of Q2 Earnings Webcast"
WHY
  underlying +0.5%/-0.6%/-1.6% (favorable peak +1.9%); position move -1.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-25% · IV residual ~47% [inferred].
  convexity Γ·S = 3.04. exit TIMEOUT → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RKLB-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 31 · V/OI 2.00 · spread +0.0%
  greeks Δ0.284 Γ0.0162 Θ-0.118 · IV 0.875 · mid 5.95
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 57
  headline "Rocket Lab (RKLB) Bullish Sentiment Surges Ahead of May Earnings as Backlog Reaches $1.85B"
WHY
  underlying -4.5%/-6.4%/+0.3% (favorable peak +1.6%); position move +0.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~1% · IV residual ~18% [inferred].
  convexity Γ·S = 1.33. exit TIMEOUT → realized +13%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CLS-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 2.00 · spread +0.0%
  greeks Δ0.378 Γ0.0044 Θ-0.719 · IV 0.839 · mid 19.55
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 77
  headline "Celestica (CLS) Could Be One Of The Biggest Winners In AI Infrastructure"
WHY
  underlying -0.3%/-2.8%/+1.8% (favorable peak +4.4%); position move +1.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~14% · IV residual ~10% [inferred].
  convexity Γ·S = 1.78. exit TIMEOUT → realized +13%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SNOW-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 37 · V/OI n/a · spread +0.1%
  greeks Δ0.286 Γ0.0107 Θ-0.150 · IV 0.736 · mid 4.31
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 36
  headline "Evercore ISI Maintains Outperform Rating on Snowflake, Highlighting 50% Undervaluation Despite Target Trim"
WHY
  underlying +6.7%/+6.0%/+6.3% (favorable peak +11.8%); position move +6.3%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~56% · IV residual ~-33% [inferred].
  convexity Γ·S = 1.45. exit TRAIL → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAMT-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 0.45 · spread +0.0%
  greeks Δ0.503 Γ0.0139 Θ-0.548 · IV 0.920 · mid 12.70
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 53
  headline "Camtek (CAMT) Sees Bullish Analyst Revisions Ahead of May 12 Earnings Report"
WHY
  underlying +7.9%/+10.9%/+5.7% (favorable peak +12.3%); position move +5.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~41% · IV residual ~-15% [inferred].
  convexity Γ·S = 2.55. exit TIMEOUT → realized +13%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE SATS-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ0.286 Γ0.0167 Θ-0.173 · IV 0.670 · mid 4.54
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 62
  headline "EchoStar (SATS) jumps as SpaceX/Starlink regulatory momentum lifts sentiment around its spectrum/SpaceX-lin…"
WHY
  underlying -2.4%/+1.5%/+2.2% (favorable peak +5.7%); position move +2.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~18% · IV residual ~7% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized +13%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AFL-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.934 Γ0.0166 Θ-0.044 · IV 0.364 · mid 10.78
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 52
  headline "Evercore Upgrades Aflac to Strong Buy as Japan Post Holdings Trims Stake"
WHY
  underlying +1.3%/+1.1%/+2.1% (favorable peak +2.4%); position move +2.1%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~20% · IV residual ~-6% [inferred].
  convexity Γ·S = 1.84. exit TIMEOUT → realized +13%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE REGN-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.363 Γ0.0062 Θ-0.675 · IV 0.392 · mid 14.60
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.65) · RSI 40
  headline "Regeneron Reports First Quarter 2026 Financial Results, Surpassing Earnings Estimates and Announcing $3 Bil…"
WHY
  underlying -1.0%/+1.7%/-0.0% (favorable peak +2.4%); position move -0.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-0% · IV residual ~27% [inferred].
  convexity Γ·S = 4.42. exit TIMEOUT → realized +12%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE IBM-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ0.478 Γ0.0080 Θ-0.443 · IV 0.860 · mid 15.63
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 54
  headline "IBM Shares Sell Off as Software Growth Slows and AI Disruption Fears Persist Post-Q1 Results"
WHY
  underlying -8.3%/-7.9%/-9.5% (favorable peak -7.5%); position move -9.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-73% · IV residual ~94% [inferred].
  convexity Γ·S = 2.00. exit TRAIL → realized +12%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE RBLX-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.343 Γ0.0230 Θ-0.071 · IV 0.775 · mid 3.42
  overnight_score 3 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 55
  headline "Roblox Announces 'Roblox Plus' Subscription Launch and Q1 Earnings Date for April 30"
WHY
  underlying -0.2%/+2.3%/+1.4% (favorable peak +6.6%); position move +1.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~8% · IV residual ~10% [inferred].
  convexity Γ·S = 1.39. exit TIMEOUT → realized +12%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ON-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.479 Γ0.0203 Θ-0.133 · IV 0.619 · mid 8.22
  overnight_score 7 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 59
  headline "Semiconductor Stocks Slide Ahead of NVIDIA Results as Treasury Yields Hit 16-Month Highs"
WHY
  underlying -3.1%/+0.7%/+0.2% (favorable peak +1.3%); position move +0.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~1% · IV residual ~15% [inferred].
  convexity Γ·S = 2.22. exit TIMEOUT → realized +12%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE IREN-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.276 Γ0.0235 Θ-0.148 · IV 1.240 · mid 1.62
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 68
  headline "IREN Jumps on $3.4 Billion NVIDIA AI Cloud Deal and $2.1 Billion Share Investment Option"
WHY
  underlying +11.4%/+3.9%/+11.8% (favorable peak +19.9%); position move +11.8%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~110% · IV residual ~-71% [inferred].
  convexity Γ·S = 1.29. exit TRAIL → realized +11%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE CIEN-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.461 Γ0.0069 Θ-1.327 · IV 0.777 · mid 16.16
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 62
  headline "Investors prioritize data center components in short supply such as memory, optical: BNP"
WHY
  underlying +4.1%/+6.7%/+5.8% (favorable peak +8.9%); position move +5.8%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~79% · IV residual ~-43% [inferred].
  convexity Γ·S = 3.29. exit TIMEOUT → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ROKU-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.297 Γ0.0395 Θ-0.177 · IV 0.443 · mid 1.79
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 72
  headline "Roku Maintains CTV Dominance with 36% North American Market Share Following Blockbuster Q1 Results"
WHY
  underlying -1.0%/+1.2%/+0.1% (favorable peak +2.7%); position move +0.1%.
  decomp [first-order]: theta drag ~30% of premium / 3d · delta capture ~1% · IV residual ~39% [inferred].
  convexity Γ·S = 5.06. exit TRAIL → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CIEN-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.489 Γ0.0025 Θ-1.131 · IV 1.025 · mid 53.12
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 57
  headline "Cirion Launches Initial Phase of On-Demand NaaS Connectivity in Latin America with Ciena"
WHY
  underlying +5.9%/+5.2%/+8.6% (favorable peak +9.2%); position move +8.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~44% · IV residual ~-27% [inferred].
  convexity Γ·S = 1.40. exit TIMEOUT → realized +11%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FLY-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.500 Γ0.0435 Θ-0.112 · IV 1.095 · mid 3.30
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 59
  headline "Space Earnings Heat Up: Rocket Lab Tops $200M, Firefly Hits Record Revenue, Redwire Backlog Surges"
WHY
  underlying +0.1%/+7.8%/+2.8% (favorable peak +10.9%); position move +2.8%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~17% · IV residual ~4% [inferred].
  convexity Γ·S = 1.71. exit TRAIL → realized +10%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE QUBT-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 40 · V/OI n/a · spread +0.0%
  greeks Δ0.485 Γ0.0814 Θ-0.025 · IV 1.208 · mid 1.84
  overnight_score 8 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 64
  headline "Quantum Computing Stocks Rally on Reports of Potential U.S. Government Funding and Equity Stakes"
WHY
  underlying -5.1%/-7.2%/-0.6% (favorable peak +1.8%); position move -0.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-2% · IV residual ~16% [inferred].
  convexity Γ·S = 1.00. exit TIMEOUT → realized +10%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NVAX-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 9.52 · spread +0.0%
  greeks Δ0.394 Γ0.2210 Θ-0.012 · IV 0.669 · mid 0.57
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.92) · RSI 70
  headline "Novavax Surges 15% on Surprise Q1 Profit and Strategic Matrix-M Adjuvant Partnership with Pfizer"
WHY
  underlying -1.4%/+8.0%/+1.5% (favorable peak +14.9%); position move +1.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~10% · IV residual ~7% [inferred].
  convexity Γ·S = 2.07. exit TRAIL → realized +10%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE BBY-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.482 Γ0.0517 Θ-0.042 · IV 0.383 · mid 2.64
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 64
  headline "Best Buy Stock On Fire: Up 12% With 6-Day Winning Streak"
WHY
  underlying +15.8%/+20.8%/+16.2% (favorable peak +21.2%); position move +16.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~191% · IV residual ~-176% [inferred].
  convexity Γ·S = 3.33. exit TIMEOUT → realized +10%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AEM-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 13 · V/OI n/a · spread +0.1%
  greeks Δ0.452 Γ0.0204 Θ-0.290 · IV 0.458 · mid 6.03
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 59
  headline "Gold Overtakes U.S. Treasuries as World's Largest Central Bank Reserve Asset for First Time in Three Decades"
WHY
  underlying -0.6%/+0.5%/-2.0% (favorable peak +1.9%); position move -2.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-33% · IV residual ~57% [inferred].
  convexity Γ·S = 4.46. exit TRAIL → realized +10%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE PANW-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.496 Γ0.0095 Θ-0.287 · IV 0.588 · mid 15.32
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 78
  headline "Palo Alto Networks Market Cap Tops $200B as Analysts Raise Targets on AI Security Leadership"
WHY
  underlying -3.0%/-0.4%/+2.2% (favorable peak +2.2%); position move +2.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~17% · IV residual ~-2% [inferred].
  convexity Γ·S = 2.36. exit TIMEOUT → realized +10%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE AXTI-2026-04-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 15 · V/OI n/a · spread +0.0%
  greeks Δ0.466 Γ0.0150 Θ-0.342 · IV 2.056 · mid 9.18
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.70) · RSI 58
  headline "AXT Inc (AXTI) Shares Slide 7% Amid $43M Insider Sell-Off and Valuation Alarms"
WHY
  underlying +30.0%/+31.2%/+25.2% (favorable peak +32.3%); position move +25.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~80% · IV residual ~-59% [inferred].
  convexity Γ·S = 0.95. exit TIMEOUT → realized +10%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE APP-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 10.00 · spread +0.0%
  greeks Δ0.398 Γ0.0031 Θ-0.713 · IV 0.705 · mid 23.65
  overnight_score 8 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 69
  headline "AppLovin surges as Morgan Stanley sees conversion rates rising"
WHY
  underlying +5.6%/+8.0%/+8.1% (favorable peak +9.5%); position move +8.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~77% · IV residual ~-58% [inferred].
  convexity Γ·S = 1.78. exit TIMEOUT → realized +10%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TSEM-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 8.42 · spread +0.0%
  greeks Δ0.371 Γ0.0143 Θ-0.591 · IV 0.846 · mid 4.26
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 54
  headline "Tower Semiconductor and Axiro Announce Volume Production of U.S.-Made Radar Beamforming ICs for Defense"
WHY
  underlying +11.0%/+9.5%/+8.0% (favorable peak +12.2%); position move +8.0%.
  decomp [first-order]: theta drag ~42% of premium / 3d · delta capture ~138% · IV residual ~-87% [inferred].
  convexity Γ·S = 2.85. exit TRAIL → realized +9%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE MOD-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.673 Γ0.0074 Θ-0.327 · IV 0.744 · mid 30.00
  overnight_score 1 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 56
  headline "Oppenheimer Reaffirms Buy Rating on Modine (MOD), Raising Price Target to $271"
WHY
  underlying +3.6%/+6.9%/+5.2% (favorable peak +9.3%); position move +5.2%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~27% · IV residual ~-15% [inferred].
  convexity Γ·S = 1.75. exit TIMEOUT → realized +9%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ALAB-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.340 Γ0.0070 Θ-0.329 · IV 0.897 · mid 10.45
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 66
  headline "Astera Labs Braces for Earnings as Amazon Partnership Fuels Analyst Optimism"
WHY
  underlying -1.1%/+3.0%/+2.2% (favorable peak +6.4%); position move +2.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~14% · IV residual ~4% [inferred].
  convexity Γ·S = 1.39. exit TIMEOUT → realized +9%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE STLA-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 3.33 · spread +0.1%
  greeks Δ0.439 Γ0.2483 Θ-0.007 · IV 0.548 · mid 0.53
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 71
  headline "Stellantis and Microsoft strike a 5-year AI deal covering 100+ initiatives as Q1 shipments jump 12%"
WHY
  underlying +0.8%/-0.3%/-1.4% (favorable peak +2.4%); position move -1.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-10% · IV residual ~23% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized +9%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE URBN-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.334 Γ0.0536 Θ-0.060 · IV 0.403 · mid 1.45
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 60
  headline "Urban Outfitters (URBN) Technical: Fast Bullish Crossover and 50-Day Moving Average Breakout"
WHY
  underlying +6.8%/+9.6%/+7.5% (favorable peak +10.8%); position move +7.5%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~121% · IV residual ~-100% [inferred].
  convexity Γ·S = 3.73. exit TIMEOUT → realized +9%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE IONQ-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 4.76 · spread +0.1%
  greeks Δ0.419 Γ0.0261 Θ-0.101 · IV 1.095 · mid 3.51
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 63
  headline "IonQ Stock Falls 11% Post-Earnings Despite 755% Revenue Growth and Raised 2026 Guidance"
WHY
  underlying +9.5%/-0.7%/+2.6% (favorable peak +11.4%); position move +2.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~15% · IV residual ~2% [inferred].
  convexity Γ·S = 1.25. exit TRAIL → realized +9%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NBIS-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI n/a · spread +0.1%
  greeks Δ0.399 Γ0.0074 Θ-0.483 · IV 1.205 · mid 16.85
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 62
  headline "Nebius (NBIS) Stock: Key Metrics to Monitor Ahead of Q1 Results on May 13"
WHY
  underlying -4.2%/+0.7%/-3.1% (favorable peak +6.3%); position move -3.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-13% · IV residual ~30% [inferred].
  convexity Γ·S = 1.37. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE VRT-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.339 Γ0.0058 Θ-0.318 · IV 0.618 · mid 15.62
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 66
  headline "Vertiv Holdings Is About to Report Q1 Earnings; Options Traders Expect a 9.16% Move"
WHY
  underlying -2.3%/+3.0%/+3.5% (favorable peak +5.7%); position move +3.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~24% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CVNA-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 33.00 · spread +0.0%
  greeks Δ0.322 Γ0.0040 Θ-0.524 · IV 0.761 · mid 15.32
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 70
  headline "Carvana Shares Break $400 Threshold as Sector Rotation Favors Online Retail Ahead of Earnings"
WHY
  underlying -0.3%/+3.7%/+0.3% (favorable peak +3.7%); position move +0.3%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~2% · IV residual ~16% [inferred].
  convexity Γ·S = 1.60. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE VRT-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI 31.00 · spread +0.0%
  greeks Δ0.246 Γ0.0054 Θ-0.264 · IV 0.605 · mid 7.83
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 57
  headline "Vertiv (VRT) Surges as Wall Street Raises Price Targets Following Q1 Earnings Beat and Strategic Liquid-Coo…"
WHY
  underlying +7.3%/+7.2%/+8.1% (favorable peak +8.7%); position move +8.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~78% · IV residual ~-60% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized +8%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AXP-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 15.00 · spread +0.0%
  greeks Δ0.387 Γ0.0132 Θ-0.156 · IV 0.284 · mid 6.65
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 51
  headline "American Express Q1 2026 Earnings Beat: Premium Card Spending Hits 3-Year High"
WHY
  underlying -0.9%/-1.0%/+1.3% (favorable peak +1.6%); position move +1.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~25% · IV residual ~-10% [inferred].
  convexity Γ·S = 4.22. exit TIMEOUT → realized +8%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE STX-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 6.50 · spread +0.0%
  greeks Δ0.388 Γ0.0019 Θ-1.311 · IV 0.823 · mid 51.95
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 72
  headline "Seagate (STX) Stock Surges to Record $843 as Wall Street Sets $1,000 Price Targets"
WHY
  underlying +2.9%/+4.1%/+4.0% (favorable peak +7.1%); position move +4.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~25% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized +7%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AFRM-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.382 Γ0.0304 Θ-0.115 · IV 0.863 · mid 3.13
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 72
  headline "Affirm Holdings: Citigroup's $100 Price Target Crowns the Historical Leap into Profitability!"
WHY
  underlying +7.0%/+11.2%/+7.2% (favorable peak +14.0%); position move +7.2%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~53% · IV residual ~-34% [inferred].
  convexity Γ·S = 1.83. exit TIMEOUT → realized +7%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AXTI-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 23 · V/OI 15.50 · spread +0.1%
  greeks Δ0.371 Γ0.0079 Θ-0.388 · IV 1.556 · mid 8.28
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 73
  headline "Why AXT Stock Is Suddenly Tumbling Today"
WHY
  underlying -0.8%/-6.4%/+0.7% (favorable peak +9.0%); position move +0.7%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~4% · IV residual ~17% [inferred].
  convexity Γ·S = 0.97. exit TIMEOUT → realized +7%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TDG-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 125.88 · spread +0.1%
  greeks Δ0.200 Γ0.0051 Θ-0.976 · IV 0.305 · mid 7.04
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.88) · RSI 53
  headline "TransDigm Q2 2026 EPS of $9.85 beats estimates; full-year revenue guidance raised to $10.36B midpoint"
WHY
  underlying -2.2%/-3.5%/-4.1% (favorable peak +0.7%); position move -4.1%.
  decomp [first-order]: theta drag ~42% of premium / 3d · delta capture ~-144% · IV residual ~193% [inferred].
  convexity Γ·S = 6.32. exit TRAIL → realized +7%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE KVUE-2026-05-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 2.17 · spread +0.1%
  greeks Δ0.315 Γ0.5163 Θ-0.014 · IV 0.260 · mid 0.20
  overnight_score 2 · flow DIRECTIONAL · catalyst M&A (0.75) · RSI 45
  headline "Barclays Lifts Kenvue Target to US$19 as Acquisition by Kimberly-Clark Advances"
WHY
  underlying +0.0%/-0.5%/-0.1% (favorable peak +1.3%); position move -0.1%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-2% · IV residual ~29% [inferred].
  convexity Γ·S = 8.87. exit TRAIL → realized +7%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SITM-2026-05-11-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.529 Γ0.0018 Θ-1.224 · IV 0.761 · mid 78.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 90
  headline "Roth Capital Raises SiTime (SITM) Price Target to $900 Following Massive Guidance Raise"
WHY
  underlying -6.0%/-7.3%/-9.0% (favorable peak -2.3%); position move -9.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-55% · IV residual ~66% [inferred].
  convexity Γ·S = 1.64. exit TIMEOUT → realized +7%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NVMI-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ0.488 Γ0.0041 Θ-0.644 · IV 0.661 · mid 32.30
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 66
  headline "Nova (NVMI) Hits New 52-Week High as TSMC’s Record Q1 Revenue Sparks Semi Sector Breakout"
WHY
  underlying +1.6%/+2.1%/+1.4% (favorable peak +3.5%); position move +1.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~11% · IV residual ~2% [inferred].
  convexity Γ·S = 2.07. exit TIMEOUT → realized +7%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE XYZ-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI 8.33 · spread +0.0%
  greeks Δ0.271 Γ0.0381 Θ-0.053 · IV 0.415 · mid 1.32
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 67
  headline "Block (XYZ) Q1 Earnings: 27% Gross Profit Growth and Raised 2026 Guidance Drive Post-Market Surge"
WHY
  underlying +6.7%/+4.3%/+2.8% (favorable peak +10.0%); position move +2.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~41% · IV residual ~-22% [inferred].
  convexity Γ·S = 2.67. exit TRAIL → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NRG-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 3.33 · spread +0.0%
  greeks Δ0.444 Γ0.0193 Θ-0.280 · IV 0.668 · mid 5.70
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 48
  headline "NRG Energy Successfully Completes $1.5 Billion Debt Tender Offer Ahead of Q1 Earnings"
WHY
  underlying -1.4%/-0.5%/+1.2% (favorable peak +2.4%); position move +1.2%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~14% · IV residual ~7% [inferred].
  convexity Γ·S = 3.00. exit TIMEOUT → realized +6%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE ADI-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.422 Γ0.0157 Θ-0.572 · IV 0.387 · mid 7.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 70
  headline "Analog Devices price target raised to $415 from $370 at Goldman Sachs"
WHY
  underlying -1.7%/+0.2%/+1.7% (favorable peak +1.7%); position move +1.7%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~40% · IV residual ~-11% [inferred].
  convexity Γ·S = 6.52. exit TRAIL → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE EBAY-2026-05-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 13.00 · spread +0.0%
  greeks Δ0.290 Γ0.0258 Θ-0.055 · IV 0.341 · mid 2.29
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 68
  headline "eBay Rejects GameStop's $56 Billion Unsolicited Takeover Bid, Citing Standalone Growth Potential"
WHY
  underlying +0.2%/+2.8%/+1.3% (favorable peak +3.4%); position move +1.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~18% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.91. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RKLB-2026-05-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 15.00 · spread +0.1%
  greeks Δ0.420 Γ0.0161 Θ-0.312 · IV 0.950 · mid 7.77
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 76
  headline "New Street initiates Rocket Lab at Buy, calling it the only Western space platform on a scale with SpaceX"
WHY
  underlying +6.8%/+0.5%/+5.6% (favorable peak +11.5%); position move +5.6%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~38% · IV residual ~-20% [inferred].
  convexity Γ·S = 2.00. exit TRAIL → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE VNOM-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 0.03 · spread +0.1%
  greeks Δ0.475 Γ0.0802 Θ-0.028 · IV 0.344 · mid 1.80
  overnight_score 1 · flow DIRECTIONAL · catalyst Guidance Raise (0.80) · RSI 51
  headline "Capital World Investors Discloses 12.4% Stake in Viper Energy (VNOM) Following Raised 2026 Guidance"
WHY
  underlying +2.7%/+3.0%/+2.2% (favorable peak +3.7%); position move +2.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~28% · IV residual ~-17% [inferred].
  convexity Γ·S = 3.82. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ZS-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.544 Γ0.0096 Θ-0.211 · IV 0.774 · mid 16.38
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 66
  headline "Zscaler Shares Rise After Raising Full-Year ARR Guidance and Software Sector Optimism"
WHY
  underlying +8.5%/+8.8%/+8.3% (favorable peak +13.6%); position move +8.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~45% · IV residual ~-34% [inferred].
  convexity Γ·S = 1.54. exit TIMEOUT → realized +6%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE AFRM-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 10.00 · spread +0.0%
  greeks Δ0.416 Γ0.0293 Θ-0.075 · IV 0.615 · mid 3.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 61
  headline "Affirm Shares Surge as BNPL Integration Rolls Out Across Google Pay and Gemini AI Ecosystem"
WHY
  underlying +1.7%/+5.4%/+6.3% (favorable peak +7.7%); position move +6.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~52% · IV residual ~-39% [inferred].
  convexity Γ·S = 2.03. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ANET-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.472 Γ0.0147 Θ-0.228 · IV 0.624 · mid 8.48
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 75
  headline "Evercore ISI adds Arista Networks to 'TAP' list, reiterates $200 target ahead of earnings"
WHY
  underlying +3.6%/+6.5%/+3.4% (favorable peak +7.0%); position move +3.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~32% · IV residual ~-18% [inferred].
  convexity Γ·S = 2.45. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MRVL-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.676 Γ0.0083 Θ-0.222 · IV 0.804 · mid 26.27
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.20) · RSI 69
  headline "Marvell Technology (-7.1%): Profit-Taking Hits After 50% Rally"
WHY
  underlying +2.0%/-5.2%/+0.8% (favorable peak +4.2%); position move +0.8%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~4% · IV residual ~5% [inferred].
  convexity Γ·S = 1.39. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE LCII-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.675 Γ0.0169 Θ-0.129 · IV 0.587 · mid 11.66
  overnight_score 9 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 53
  headline "The Bull Case For LCI Industries (LCII) Could Change Following Analyst Upgrades And Diversification Moves"
WHY
  underlying -5.6%/-6.6%/-3.4% (favorable peak +8.1%); position move -3.4%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-25% · IV residual ~35% [inferred].
  convexity Γ·S = 2.15. exit TIMEOUT → realized +6%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE TE-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 40 · V/OI n/a · spread +0.0%
  greeks Δ0.652 Γ0.1004 Θ-0.017 · IV 1.376 · mid 1.70
  overnight_score 7 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 68
  headline "T1 Energy Inc. faces heavy selling as regulatory investigation news sparks renewed fears"
WHY
  underlying +29.3%/+35.6%/+33.9% (favorable peak +41.5%); position move +33.9%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~105% · IV residual ~-96% [inferred].
  convexity Γ·S = 0.81. exit TIMEOUT → realized +6%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE BE-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 4.33 · spread +0.0%
  greeks Δ0.401 Γ0.0044 Θ-0.498 · IV 1.016 · mid 22.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 77
  headline "Bloom Energy Reports Record Q1, Raises Guidance on Massive Oracle AI Data Center Deal"
WHY
  underlying +2.5%/+1.9%/+4.2% (favorable peak +6.9%); position move +4.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~21% · IV residual ~-9% [inferred].
  convexity Γ·S = 1.25. exit TIMEOUT → realized +6%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE ROKU-2026-05-01-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ0.444 Γ0.0219 Θ-0.109 · IV 0.476 · mid 4.75
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.92) · RSI 71
  headline "Roku Surges 6% on Q1 Earnings Beat and Swing to Profitability; 100 Million Household Milestone Reached"
WHY
  underlying +2.0%/+0.7%/+3.6% (favorable peak +4.0%); position move +3.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~41% · IV residual ~-29% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DAL-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 27.50 · spread +0.1%
  greeks Δ0.568 Γ0.0421 Θ-0.054 · IV 0.444 · mid 4.48
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 51
  headline "Delta Air Lines Named Among Top 3 Trending Stocks by Analysts Ahead of May Dividend"
WHY
  underlying +1.5%/+0.8%/+4.2% (favorable peak +4.9%); position move +4.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~36% · IV residual ~-28% [inferred].
  convexity Γ·S = 2.86. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AXTI-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 2.83 · spread +0.0%
  greeks Δ0.499 Γ0.0105 Θ-0.710 · IV 3.120 · mid 9.88
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 64
  headline "AXT stock tumbles 9% on public offering announcement and Q1 revenue guidance"
WHY
  underlying -4.8%/+10.4%/-4.4% (favorable peak +14.4%); position move -4.4%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~-18% · IV residual ~44% [inferred].
  convexity Γ·S = 0.83. exit TRAIL → realized +5%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE TER-2026-05-26-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 6.20 · spread +0.0%
  greeks Δ0.418 Γ0.0063 Θ-0.749 · IV 0.745 · mid 15.27
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 60
  headline "Teradyne Stock Surges on AI Chip Testing Boom as AI Revenue Share Hits 60%"
WHY
  underlying -3.4%/-1.7%/-3.8% (favorable peak +4.5%); position move -3.8%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-41% · IV residual ~60% [inferred].
  convexity Γ·S = 2.46. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CDW-2026-05-05-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI 92.16 · spread +0.1%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 13.54
  overnight_score 8 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 26
  headline "CDW Stock Plunges 20% as Margin Squeeze Offsets AI-Driven Revenue Beat"
WHY
  underlying -20.3%/-19.4%/-23.4% (favorable peak -6.2%); position move -23.4%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~-0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TRAIL → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CL-2026-04-24-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 4.50 · spread +0.1%
  greeks Δ0.310 Γ0.0794 Θ-0.038 · IV 0.221 · mid 1.35
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 48
  headline "Rothschild Redburn upgrades Colgate-Palmolive to Buy, raising price target to $100 on resilient growth prof…"
WHY
  underlying -0.6%/+1.2%/-0.2% (favorable peak +2.0%); position move -0.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-4% · IV residual ~17% [inferred].
  convexity Γ·S = 6.72. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SBUX-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ0.621 Γ0.0321 Θ-0.054 · IV 0.345 · mid 5.60
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 58
  headline "Jefferies Upgrades Starbucks to Hold as China Franchise Exit and U.S. Stabilization Improve Visibility"
WHY
  underlying +1.0%/+0.9%/+0.9% (favorable peak +1.7%); position move +0.9%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~10% · IV residual ~-2% [inferred].
  convexity Γ·S = 3.13. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE JPM-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.700 Γ0.0184 Θ-0.193 · IV 0.276 · mid 12.50
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.78) · RSI 58
  headline "Evercore ISI Raises JPM Target to $340 Following Q1 Earnings Beat and Private Credit Expansion"
WHY
  underlying -0.1%/-0.8%/+0.5% (favorable peak +1.2%); position move +0.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~9% · IV residual ~1% [inferred].
  convexity Γ·S = 5.73. exit TIMEOUT → realized +5%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE MP-2026-04-30-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 0.98 · spread +0.0%
  greeks Δ0.413 Γ0.0276 Θ-0.101 · IV 0.774 · mid 2.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 59
  headline "Zacks Reports +100% Earnings ESP for MP Materials Ahead of Q1 Results"
WHY
  underlying +0.9%/+0.2%/+3.1% (favorable peak +5.5%); position move +3.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~42% · IV residual ~-22% [inferred].
  convexity Γ·S = 1.83. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AXP-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.241 Γ0.0098 Θ-0.138 · IV 0.306 · mid 3.75
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 62
  headline "American Express Has A Spring Pattern: History Says April 14 Is The Buy Signal"
WHY
  underlying +1.0%/+1.6%/+0.6% (favorable peak +2.6%); position move +0.6%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~12% · IV residual ~3% [inferred].
  convexity Γ·S = 3.18. exit TIMEOUT → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DAVE-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 0.97 · spread +0.0%
  greeks Δ0.254 Γ0.0107 Θ-0.640 · IV 0.749 · mid 4.40
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 76
  headline "Dave Inc. (DAVE) Hits 52-Week High as Analysts Raise Price Targets to $345 Ahead of May 5 Earnings"
WHY
  underlying +0.1%/+1.9%/+1.5% (favorable peak +2.4%); position move +1.5%.
  decomp [first-order]: theta drag ~44% of premium / 3d · delta capture ~24% · IV residual ~24% [inferred].
  convexity Γ·S = 2.94. exit TRAIL → realized +5%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE PG-2026-04-24-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.363 Γ0.0342 Θ-0.051 · IV 0.223 · mid 3.25
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 55
  headline "P&G Q3 Earnings: Organic Sales Rise 3% on First Volume Growth in a Year; Dividend Raised"
WHY
  underlying +0.1%/+0.7%/-1.2% (favorable peak +2.0%); position move -1.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-19% · IV residual ~28% [inferred].
  convexity Γ·S = 5.06. exit TRAIL → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SITM-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI 4.14 · spread +0.0%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 58.15
  overnight_score 2 · flow HEDGING · catalyst Guidance Raise (1.00) · RSI 88
  headline "SiTime Shares Surge 29% on Blowout Q1 Results and Massive Guidance Raise Driven by AI Demand"
WHY
  underlying +27.9%/+33.6%/+44.6% (favorable peak +44.6%); position move +44.6%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized +4%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE NSC-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 21 · V/OI 0.05 · spread +0.0%
  greeks Δ0.767 Γ0.0129 Θ-0.181 · IV 0.300 · mid 16.29
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 65
  headline "Norfolk Southern stock hits all-time high at 323.38 USD"
WHY
  underlying -5.5%/-6.4%/-6.3% (favorable peak -0.8%); position move -6.3%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-97% · IV residual ~104% [inferred].
  convexity Γ·S = 4.22. exit TRAIL → realized +4%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CAR-2026-04-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.472 Γ0.0013 Θ-3.497 · IV 2.280 · mid 65.80
  overnight_score 5 · flow HEDGING · catalyst Short Squeeze (0.95) · RSI 95
  headline "Avis Stock Up Another 23% Amid Short Squeeze; Two Investors Control Over 100% of Shares"
WHY
  underlying +17.3%/-27.1%/-62.4% (favorable peak +39.2%); position move -62.4%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-273% · IV residual ~292% [inferred].
  convexity Γ·S = 0.80. exit TRAIL → realized +4%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE WDC-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.462 Γ0.0067 Θ-0.678 · IV 0.758 · mid 18.04
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 67
  headline "Citi Raises Western Digital Target to $405 as AI Data Demand Supercharges Storage Pricing"
WHY
  underlying +4.6%/+4.2%/+3.3% (favorable peak +5.2%); position move +3.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~30% · IV residual ~-15% [inferred].
  convexity Γ·S = 2.36. exit TRAIL → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MTZ-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.341 Γ0.0063 Θ-0.385 · IV 0.578 · mid 12.15
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.88) · RSI 68
  headline "Clear Street and Stifel Raise MasTec (MTZ) Price Targets to $400+ Citing Datacenter and Power Delivery Growth"
WHY
  underlying +3.6%/+3.8%/+3.7% (favorable peak +5.1%); position move +3.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~37% · IV residual ~-24% [inferred].
  convexity Γ·S = 2.27. exit TIMEOUT → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE AMAT-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.300 Γ0.0080 Θ-0.872 · IV 0.627 · mid 7.52
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 61
  headline "Mizuho raises Applied Materials stock price target to $540 on WFE outlook"
WHY
  underlying +0.3%/+0.4%/+2.2% (favorable peak +3.5%); position move +2.2%.
  decomp [first-order]: theta drag ~35% of premium / 3d · delta capture ~40% · IV residual ~-1% [inferred].
  convexity Γ·S = 3.60. exit TRAIL → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MPWR-2026-05-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 0.05 · spread +0.0%
  greeks Δ0.410 Γ0.0015 Θ-2.374 · IV 0.649 · mid 65.77
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 57
  headline "Monolithic Power Systems (NASDAQ:MPWR) Reaches New 12-Month High"
WHY
  underlying +0.8%/-3.3%/-4.8% (favorable peak +2.3%); position move -4.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-48% · IV residual ~63% [inferred].
  convexity Γ·S = 2.49. exit TRAIL → realized +4%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE WMS-2026-05-15-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 33 · V/OI 0.95 · spread +0.0%
  greeks Δ0.453 Γ0.0198 Θ-0.124 · IV 0.489 · mid 6.23
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.85) · RSI 38
  headline "Advanced Drainage Systems (WMS) to Release Q4 2026 Earnings on May 21, Before Market Open"
WHY
  underlying -0.3%/-3.0%/+0.9% (favorable peak +1.1%); position move +0.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~9% · IV residual ~1% [inferred].
  convexity Γ·S = 2.68. exit TIMEOUT → realized +3%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CHTR-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 14 · V/OI n/a · spread +0.0%
  greeks Δ0.375 Γ0.0119 Θ-0.430 · IV 0.677 · mid 7.21
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 62
  headline "Charter Communications Surges 7% as Spectrum TV App Expansion and Cox Merger Progress Bolster Sentiment"
WHY
  underlying +0.3%/+3.7%/+2.5% (favorable peak +5.7%); position move +2.5%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~31% · IV residual ~-10% [inferred].
  convexity Γ·S = 2.82. exit TIMEOUT → realized +3%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE URI-2026-04-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 7.72 · spread +0.1%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 35.74
  overnight_score 5 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 60
  headline "United Rentals surges after Q1 beat, higher 2026 outlook"
WHY
  underlying +22.9%/+21.4%/+19.6% (favorable peak +24.7%); position move +19.6%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized +3%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE TMUS-2026-05-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 8 · V/OI 16.00 · spread +0.1%
  greeks Δ0.884 Γ0.0165 Θ-0.136 · IV 0.401 · mid 14.63
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.80) · RSI 43
  headline "Deutsche Telekom Raises 2026 Guidance on Strong T-Mobile US Performance"
WHY
  underlying -1.1%/-2.7%/+0.2% (favorable peak +0.7%); position move +0.2%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~2% · IV residual ~3% [inferred].
  convexity Γ·S = 3.14. exit TIMEOUT → realized +3%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE OSCR-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 8.33 · spread +0.0%
  greeks Δ0.493 Γ0.0917 Θ-0.025 · IV 0.774 · mid 0.90
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 77
  headline "Oscar Health (OSCR) to Release Quarterly Earnings on May 6; Analysts Expect Massive EPS Turnaround"
WHY
  underlying +3.0%/+3.1%/+3.6% (favorable peak +4.7%); position move +3.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~35% · IV residual ~-24% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized +3%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TER-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI n/a · spread +0.1%
  greeks Δ0.443 Γ0.0060 Θ-1.705 · IV 1.132 · mid 21.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 74
  headline "Teradyne price target raised to $440 from $325 at UBS"
WHY
  underlying +4.3%/+0.3%/-5.2% (favorable peak +5.3%); position move -5.2%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~-44% · IV residual ~71% [inferred].
  convexity Γ·S = 2.39. exit TRAIL → realized +3%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DLR-2026-04-16-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 14 · V/OI n/a · spread +0.0%
  greeks Δ0.371 Γ0.0269 Θ-0.190 · IV 0.358 · mid 2.27
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 80
  headline "Digital Realty (DLR) Reaches New 52-Week High as Institutional Flow Surges Ahead of Q1 Earnings"
WHY
  underlying +2.3%/+2.4%/+1.1% (favorable peak +3.0%); position move +1.1%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~36% · IV residual ~-9% [inferred].
  convexity Γ·S = 5.35. exit TIMEOUT → realized +2%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIG-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 42 · V/OI 101.00 · spread +0.1%
  greeks Δ0.459 Γ0.0716 Θ-0.027 · IV 0.721 · mid 1.65
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 52
  headline "Figma (FIG) Stock Surges 19% as AI Tools Drive Stronger Revenue Forecast and Enterprise Growth"
WHY
  underlying +13.2%/+20.4%/+15.0% (favorable peak +27.7%); position move +15.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~84% · IV residual ~-77% [inferred].
  convexity Γ·S = 1.45. exit TRAIL → realized +2%.
TAKEAWAY: Large favorable move cleared the +80% target net of decay.
```

```
CASE ELF-2026-04-29-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 5.67 · spread +0.1%
  greeks Δ0.402 Γ0.0311 Θ-0.112 · IV 0.829 · mid 3.28
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 36
  headline "Baird Slashes ELF Beauty Price Target to $90 Amid Insider Selling and Margin Concerns"
WHY
  underlying +4.7%/-1.0%/+1.3% (favorable peak +5.6%); position move +1.3%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~9% · IV residual ~3% [inferred].
  convexity Γ·S = 1.90. exit TIMEOUT → realized +2%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE TXN-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 26 · V/OI 20.00 · spread +0.0%
  greeks Δ0.340 Γ0.0097 Θ-0.265 · IV 0.453 · mid 9.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 72
  headline "Texas Instruments (TXN) Stock Surges to 52-Week Peak on AI Power Chip Momentum"
WHY
  underlying +5.1%/+2.7%/+2.2% (favorable peak +7.2%); position move +2.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~24% · IV residual ~-14% [inferred].
  convexity Γ·S = 3.01. exit TIMEOUT → realized +2%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE RSI-2026-05-04-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 0.92 · spread +0.1%
  greeks Δ0.364 Γ0.0807 Θ-0.021 · IV 0.484 · mid 1.15
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 77
  headline "Rush Street Interactive Raises 2026 Guidance Following Record Q1 Revenue Beat and 51% MAU Growth"
WHY
  underlying +5.1%/+0.4%/+0.5% (favorable peak +5.4%); position move +0.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~5% · IV residual ~2% [inferred].
  convexity Γ·S = 2.24. exit TRAIL → realized +2%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE QCOM-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 40 · V/OI 477.00 · spread +0.1%
  greeks Δ0.421 Γ0.0061 Θ-0.318 · IV 0.816 · mid 17.99
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.90) · RSI 72
  headline "Qualcomm soars 11% as Stellantis deepens AI vehicle partnership and automotive revenue hits record highs"
WHY
  underlying +4.5%/-2.0%/+2.2% (favorable peak +8.3%); position move +2.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~12% · IV residual ~-5% [inferred].
  convexity Γ·S = 1.46. exit TRAIL → realized +2%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CAT-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.472 Γ0.0049 Θ-0.778 · IV 0.373 · mid 34.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 67
  headline "Caterpillar (NYSE:CAT) Stock Price Down 3.3% on Insider Selling by Multiple Executives"
WHY
  underlying +0.2%/+3.5%/+1.8% (favorable peak +3.7%); position move +1.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~23% · IV residual ~-14% [inferred].
  convexity Γ·S = 4.41. exit TRAIL → realized +2%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE FIX-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.536 Γ0.0012 Θ-2.305 · IV 0.708 · mid 140.31
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 69
  headline "Comfort Systems USA (FIX) Maintains 'Strong Buy' Rating as AI Data Center Demand Drives Record $11.9B Backlog"
WHY
  underlying -0.1%/-2.7%/-0.0% (favorable peak +0.5%); position move -0.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-0% · IV residual ~6% [inferred].
  convexity Γ·S = 1.97. exit TIMEOUT → realized +2%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE STZ-2026-04-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.525 Γ0.0404 Θ-0.086 · IV 0.249 · mid 4.80
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.60) · RSI 50
  headline "Constellation Brands Reports Q4 Beat but Shares Pressure on Soft FY27 Guidance and Leadership Transition"
WHY
  underlying -0.0%/+1.5%/-0.6% (favorable peak +2.2%); position move -0.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-10% · IV residual ~17% [inferred].
  convexity Γ·S = 6.34. exit TIMEOUT → realized +2%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE SPOT-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 44 · V/OI n/a · spread +0.1%
  greeks Δ0.487 Γ0.0044 Θ-0.433 · IV 0.512 · mid 34.22
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 57
  headline "Spotify (SPOT) Gains 1.4% as Institutions Build Positions Two Weeks Ahead of Earnings"
WHY
  underlying +3.9%/+3.9%/+4.9% (favorable peak +6.3%); position move +4.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~36% · IV residual ~-31% [inferred].
  convexity Γ·S = 2.24. exit TIMEOUT → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE HUT-2026-04-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 9 · V/OI n/a · spread +0.0%
  greeks Δ0.398 Γ0.0335 Θ-0.237 · IV 0.994 · mid 3.95
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 72
  headline "Hut 8 stock climbs as price breaks above all major trend averages following AI infrastructure pivot"
WHY
  underlying -0.9%/-1.1%/+4.4% (favorable peak +6.0%); position move +4.4%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~32% · IV residual ~-12% [inferred].
  convexity Γ·S = 2.40. exit TIMEOUT → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE VAL-2026-05-08-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 40 · V/OI 3.34 · spread +0.1%
  greeks Δ0.463 Γ0.0261 Θ-0.079 · IV 0.474 · mid 4.97
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 49
  headline "Valaris secures $447M contract extension with Petrobras as energy services stocks continue rally"
WHY
  underlying +2.4%/+2.3%/+4.1% (favorable peak +4.8%); position move +4.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~37% · IV residual ~-31% [inferred].
  convexity Γ·S = 2.48. exit TIMEOUT → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CVNA-2026-05-22-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 20 · V/OI 333.33 · spread +0.0%
  greeks Δ0.068 Γ0.0137 Θ-0.031 · IV 0.588 · mid 0.35
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.78) · RSI 44
  headline "Carvana's Spectacular Turnaround: Operational Reality or Valuation Trap?"
WHY
  underlying +2.7%/+6.9%/+7.6% (favorable peak +10.0%); position move +7.6%.
  decomp [first-order]: theta drag ~26% of premium / 3d · delta capture ~101% · IV residual ~-73% [inferred].
  convexity Γ·S = 0.94. exit TIMEOUT → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE SATS-2026-05-14-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 9.00 · spread +0.1%
  greeks Δ0.461 Γ0.0181 Θ-0.208 · IV 0.660 · mid 1.92
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 63
  headline "New Street initiates EchoStar stock with buy rating on SpaceX deal and $161 price target"
WHY
  underlying +1.6%/+1.0%/+1.0% (favorable peak +9.0%); position move +1.0%.
  decomp [first-order]: theta drag ~32% of premium / 3d · delta capture ~34% · IV residual ~-0% [inferred].
  convexity Γ·S = 2.45. exit TRAIL → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE NEM-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 11.00 · spread +0.0%
  greeks Δ0.488 Γ0.0244 Θ-0.096 · IV 0.462 · mid 8.18
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 55
  headline "Newmont Corporation Shares Soften as Gold Prices Consolidate Amid Geopolitical De-escalation"
WHY
  underlying +2.7%/+6.3%/+5.5% (favorable peak +6.8%); position move +5.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~37% · IV residual ~-32% [inferred].
  convexity Γ·S = 2.77. exit TIMEOUT → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE DASH-2026-05-07-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.303 Γ0.0121 Θ-0.147 · IV 0.542 · mid 4.85
  overnight_score 6 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 44
  headline "DoorDash Q1 Earnings Top Estimates, Shares Surge 17% on Strong Q2 Guidance"
WHY
  underlying -4.3%/-8.2%/-9.4% (favorable peak +0.0%); position move -9.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-101% · IV residual ~111% [inferred].
  convexity Γ·S = 2.08. exit TIMEOUT → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE USAR-2026-04-23-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.352 Γ0.0492 Θ-0.040 · IV 1.036 · mid 1.70
  overnight_score 5 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 64
  headline "USA Rare Earth (NASDAQ:USAR) Shares Down 9.1% - Here's What Happened"
WHY
  underlying -5.3%/+1.8%/-1.4% (favorable peak +4.2%); position move -1.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-7% · IV residual ~15% [inferred].
  convexity Γ·S = 1.13. exit TRAIL → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE CRDO-2026-04-27-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 24 · V/OI 12.82 · spread +0.1%
  greeks Δ0.314 Γ0.0078 Θ-0.337 · IV 0.987 · mid 7.75
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.70) · RSI 67
  headline "Credo Technology Group (NASDAQ:CRDO) Trading Down 7.5% Following Insider Selling"
WHY
  underlying -8.1%/-2.6%/-3.6% (favorable peak +0.0%); position move -3.6%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-26% · IV residual ~40% [inferred].
  convexity Γ·S = 1.40. exit TRAIL → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE NOG-2026-04-13-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ0.462 Γ0.1049 Θ-0.024 · IV 0.471 · mid 1.25
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 45
  headline "Q1 EPS Forecast for Northern Oil and Gas Raised by Analyst - MarketBeat"
WHY
  underlying -5.8%/-5.1%/-5.4% (favorable peak -1.5%); position move -5.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-54% · IV residual ~61% [inferred].
  convexity Γ·S = 2.86. exit TIMEOUT → realized +1%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE WING-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 5.11 · spread +0.1%
  greeks Δ0.370 Γ0.0081 Θ-0.328 · IV 0.864 · mid 10.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 52
  headline "Wingstop Celebrates 4/20 with Return of Fan-Favorite Hot Box Ahead of Q1 Earnings"
WHY
  underlying +1.4%/-3.6%/-3.2% (favorable peak +4.2%); position move -3.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-22% · IV residual ~32% [inferred].
  convexity Γ·S = 1.59. exit TRAIL → realized +1%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE CCL-2026-05-20-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI 2.00 · spread +0.0%
  greeks Δ0.163 Γ0.0612 Θ-0.018 · IV 0.562 · mid 0.31
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.90) · RSI 50
  headline "Carnival Stock Surges as Oil Prices Crash on Iran Peace Prospect"
WHY
  underlying +0.6%/-0.2%/+2.6% (favorable peak +4.1%); position move +2.6%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~36% · IV residual ~-18% [inferred].
  convexity Γ·S = 1.59. exit TIMEOUT → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE MPWR-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI 1.56 · spread +0.0%
  greeks Δ0.413 Γ0.0012 Θ-1.535 · IV 0.567 · mid 88.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 63
  headline "Monolithic Power Systems (MPWR) Hits Record Highs on AI Data Center Strength as Analysts Lift Targets to $2…"
WHY
  underlying -4.6%/-3.1%/+0.5% (favorable peak +0.7%); position move +0.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~4% · IV residual ~2% [inferred].
  convexity Γ·S = 2.04. exit TIMEOUT → realized +0%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE KLAC-2026-04-17-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 0.63 · spread +0.1%
  greeks Δ0.453 Γ0.0015 Θ-1.953 · IV 0.531 · mid 79.75
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 69
  headline "Global chip equipment sales reach record $135B as AI drives investment surge"
WHY
  underlying +0.8%/-0.3%/+1.2% (favorable peak +1.8%); position move +1.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~12% · IV residual ~-4% [inferred].
  convexity Γ·S = 2.71. exit TIMEOUT → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE VRT-2026-04-10-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.1%
  greeks Δ0.319 Γ0.0065 Θ-0.367 · IV 0.679 · mid 10.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 67
  headline "BofA raises Vertiv stock price target to $330 on data center demand"
WHY
  underlying +1.6%/+5.2%/+2.1% (favorable peak +5.9%); position move +2.1%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~19% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.91. exit TRAIL → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE BX-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 3.08 · spread +0.1%
  greeks Δ0.272 Γ0.0259 Θ-0.070 · IV 0.361 · mid 2.04
  overnight_score 5 · flow DIRECTIONAL · catalyst M&A (0.80) · RSI 51
  headline "Sony and GIC Venture Nearing $4 Billion Deal to Acquire Music Catalog From Blackstone"
WHY
  underlying -2.6%/-0.2%/-4.0% (favorable peak +1.0%); position move -4.0%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-65% · IV residual ~75% [inferred].
  convexity Γ·S = 3.18. exit TRAIL → realized +0%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE VTRS-2026-05-06-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.360 Γ0.0964 Θ-0.083 · IV 1.570 · mid 0.10
  overnight_score 7 · flow HEDGING · catalyst Earnings Beat (0.85) · RSI 80
  headline "Viatris rises as Q1 beat indicates growth momentum"
WHY
  underlying +9.0%/+7.6%/+6.1% (favorable peak +9.9%); position move +6.1%.
  decomp [first-order]: theta drag ~250% of premium / 3d · delta capture ~349% · IV residual ~-99% [inferred].
  convexity Γ·S = 1.54. exit TRAIL → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

```
CASE KTOS-2026-05-18-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.326 Γ0.0346 Θ-0.063 · IV 0.658 · mid 1.88
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.45) · RSI 36
  headline "Kratos Defense Shares Rebound as Pentagon AI Pivot Supercharges Defense Sector Outlook"
WHY
  underlying -1.4%/+3.0%/+0.8% (favorable peak +3.1%); position move +0.8%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~8% · IV residual ~2% [inferred].
  convexity Γ·S = 1.88. exit TIMEOUT → realized +0%.
TAKEAWAY: Was wrong on day 1; low theta + convexity let it win late on a single sharp move.
```

```
CASE HPE-2026-05-21-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 7 · V/OI 2.06 · spread +0.0%
  greeks Δ0.728 Γ0.1631 Θ-0.045 · IV 0.408 · mid 1.22
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 71
  headline "Morgan Stanley Hikes HPE Price Target to $33 Following Strong AI Infrastructure Growth and Activist Interest"
WHY
  underlying +10.6%/+12.0%/+9.5% (favorable peak +13.6%); position move +9.5%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~193% · IV residual ~-182% [inferred].
  convexity Γ·S = 5.54. exit TIMEOUT → realized +0%.
TAKEAWAY: Fast convex move outran a short-DTE theta cliff — speed was the edge.
```

```
CASE KLAC-2026-05-12-B  ·  BULLISH  ·  WON  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 0.32 · spread +0.0%
  greeks Δ0.345 Γ0.0012 Θ-1.567 · IV 0.527 · mid 64.81
  overnight_score 3 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 56
  headline "KLA Corporation Announces Ten-to-One Stock Split and 21% Dividend Hike Amid Sector-Wide Semiconductor Pullback"
WHY
  underlying +2.1%/+4.5%/-0.4% (favorable peak +5.5%); position move -0.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-4% · IV residual ~11% [inferred].
  convexity Γ·S = 2.23. exit TRAIL → realized +0%.
TAKEAWAY: Modest favorable move, but enough to finish green net of spread + theta.
```

---

## BACKTEST · LOST  (446)

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

```
CASE TRGP-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 0.02 · spread +0.1%
  greeks Δ0.227 Γ0.0118 Θ-0.175 · IV 0.384 · mid 3.09
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 60
  headline "Targa Resources (TRGP) Stockholders Ratify 2026 Governance Proposals as Institutional Bulls Target $290+"
WHY
  underlying -2.3%/-2.9%/-5.5% (favorable peak -0.5%); position move -5.5%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-109% · IV residual ~66% [inferred].
  convexity Γ·S = 3.19. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WYNN-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.337 Γ0.0336 Θ-0.091 · IV 0.407 · mid 2.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 44
  headline "Wynn Resorts Beats Q1 Earnings Estimates, Announces $950M Macau Tower Expansion"
WHY
  underlying -0.7%/-4.8%/-7.6% (favorable peak +1.3%); position move -7.6%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-125% · IV residual ~78% [inferred].
  convexity Γ·S = 3.62. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AA-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 11.50 · spread +0.0%
  greeks Δ0.480 Γ0.0415 Θ-0.084 · IV 0.559 · mid 1.56
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 57
  headline "Alcoa to Participate in Bank of America Global Metals, Mining and Steel Conference 2026"
WHY
  underlying +1.2%/-2.4%/-7.5% (favorable peak +3.1%); position move -7.5%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-157% · IV residual ~113% [inferred].
  convexity Γ·S = 2.81. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AAOI-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 22 · V/OI 8.00 · spread +0.0%
  greeks Δ0.402 Γ0.0062 Θ-0.548 · IV 1.416 · mid 15.14
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 54
  headline "Wall Street raises AAOI price target to $220 citing strong Amazon-linked 800G demand and AI production expa…"
WHY
  underlying +1.2%/-4.8%/-10.8% (favorable peak +6.9%); position move -10.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-51% · IV residual ~2% [inferred].
  convexity Γ·S = 1.10. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AAOI-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 3.14 · spread +0.0%
  greeks Δ0.497 Γ0.0052 Θ-0.720 · IV 1.599 · mid 26.11
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.85) · RSI 62
  headline "Applied Optoelectronics Files for $600 Million At-The-Market Equity Offering to Fuel AI Infrastructure Growth"
WHY
  underlying -6.5%/-14.9%/-15.8% (favorable peak -1.5%); position move -15.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-61% · IV residual ~10% [inferred].
  convexity Γ·S = 1.05. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ACMR-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.270 Γ0.0225 Θ-0.285 · IV 1.076 · mid 2.17
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 86
  headline "ACM Research surges after filing highlights 65% order growth and SPM tool momentum"
WHY
  underlying +4.8%/-2.3%/-7.4% (favorable peak +6.3%); position move -7.4%.
  decomp [first-order]: theta drag ~39% of premium / 3d · delta capture ~-82% · IV residual ~61% [inferred].
  convexity Γ·S = 2.00. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AMBA-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 21 · V/OI 4.06 · spread +0.1%
  greeks Δ0.361 Γ0.0147 Θ-0.225 · IV 1.154 · mid 4.25
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 73
  headline "Ambarella Announces First Quarter Fiscal Year 2027 Earnings Conference Call to be Held May 28, 2026"
WHY
  underlying +1.4%/-20.3%/-16.5% (favorable peak +4.0%); position move -16.5%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-127% · IV residual ~82% [inferred].
  convexity Γ·S = 1.33. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AMGN-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 1.56 · spread +0.1%
  greeks Δ0.311 Γ0.0129 Θ-0.235 · IV 0.334 · mid 5.55
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 43
  headline "Amgen (AMGN) to Release Q1 Earnings on Thursday; Focus Sharpens on Obesity Drug MariTide"
WHY
  underlying -1.3%/-1.4%/-1.9% (favorable peak +1.0%); position move -1.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-37% · IV residual ~-11% [inferred].
  convexity Γ·S = 4.45. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
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
CASE B-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 44 · V/OI 12.00 · spread +0.0%
  greeks Δ0.529 Γ0.0565 Θ-0.033 · IV 0.447 · mid 2.39
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 64
  headline "Barrick's Q1 2026 Earnings and Cash Flow Accelerate on Gold Beat: Guidance Affirmed, $3B Buyback Announced"
WHY
  underlying -2.1%/-5.9%/-11.4% (favorable peak +0.1%); position move -11.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-116% · IV residual ~60% [inferred].
  convexity Γ·S = 2.59. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BE-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 6.25 · spread +0.0%
  greeks Δ0.283 Γ0.0068 Θ-0.982 · IV 1.107 · mid 10.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 67
  headline "Bloom Energy price target raised to $250 at Clear Street as AI power demand accelerates"
WHY
  underlying +4.7%/-4.8%/-10.7% (favorable peak +7.0%); position move -10.7%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~-88% · IV residual ~57% [inferred].
  convexity Γ·S = 1.97. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BE-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 2.00 · spread +0.0%
  greeks Δ0.432 Γ0.0057 Θ-0.942 · IV 1.141 · mid 10.43
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 70
  headline "Federal Pacific Awards Bloom Energy Largest Single Order for AI Data Center Infrastructure"
WHY
  underlying -9.1%/-14.7%/-13.9% (favorable peak -4.8%); position move -13.9%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~-174% · IV residual ~141% [inferred].
  convexity Γ·S = 1.74. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CMRE-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 21 · V/OI 0.03 · spread +0.0%
  greeks Δ0.572 Γ0.2384 Θ-0.015 · IV 0.418 · mid 0.99
  overnight_score 1 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 42
  headline "Assessing Costamare (CMRE) Valuation After Weaker Q1 2026 Results And Ongoing Fleet Expansion"
WHY
  underlying -2.5%/-5.1%/-3.6% (favorable peak -0.4%); position move -3.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-33% · IV residual ~-22% [inferred].
  convexity Γ·S = 3.86. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DUOL-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 3.00 · spread +0.0%
  greeks Δ0.313 Γ0.0114 Θ-0.163 · IV 0.892 · mid 3.65
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 62
  headline "Duolingo (DUOL) Set to Report Q1 2026 Earnings Today; Institutional Flow Signals Bullish Bias"
WHY
  underlying -0.9%/-6.5%/-5.6% (favorable peak +4.2%); position move -5.6%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-53% · IV residual ~7% [inferred].
  convexity Γ·S = 1.27. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ENTG-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 2.86 · spread +0.1%
  greeks Δ0.398 Γ0.0140 Θ-0.164 · IV 0.654 · mid 7.32
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.65) · RSI 47
  headline "Entegris (ENTG) Shares Fall 4.0% -- GF Value Says Still Overvalued Despite Q1 Earnings Beat"
WHY
  underlying -4.4%/-8.7%/-10.8% (favorable peak -2.2%); position move -10.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-82% · IV residual ~29% [inferred].
  convexity Γ·S = 1.96. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EPD-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI n/a · spread +0.0%
  greeks Δ0.404 Γ0.2422 Θ-0.019 · IV 0.204 · mid 0.42
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.15) · RSI 45
  headline "EPD continues to strengthen its balance sheet through disciplined capital allocation and the reinvestment o…"
WHY
  underlying -1.3%/-3.2%/-2.1% (favorable peak +0.3%); position move -2.1%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-75% · IV residual ~29% [inferred].
  convexity Γ·S = 9.20. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ETN-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 4.29 · spread +0.0%
  greeks Δ0.329 Γ0.0083 Θ-0.275 · IV 0.376 · mid 9.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 51
  headline "Eaton (ETN) Expanding Switchgear Capacity for AI Data Center Buildout as Electrical Orders Surge 240%"
WHY
  underlying +0.3%/-1.8%/-6.2% (favorable peak +0.7%); position move -6.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-88% · IV residual ~37% [inferred].
  convexity Γ·S = 3.39. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
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

```
CASE FCEL-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.420 Γ0.0810 Θ-0.033 · IV 1.451 · mid 1.20
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 83
  headline "FuelCell Energy Rally Builds As Data Center Demand Grows"
WHY
  underlying +3.1%/-5.3%/-9.5% (favorable peak +5.3%); position move -9.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-39% · IV residual ~-13% [inferred].
  convexity Γ·S = 0.96. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FCX-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 1.92 · spread +0.0%
  greeks Δ0.297 Γ0.0383 Θ-0.068 · IV 0.538 · mid 1.64
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 60
  headline "Freeport-McMoRan Inc. (NYSE:FCX) Receives Average Rating of "Moderate Buy" from Analysts"
WHY
  underlying +1.7%/+0.2%/-4.6% (favorable peak +4.3%); position move -4.6%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-55% · IV residual ~7% [inferred].
  convexity Γ·S = 2.53. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FDX-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.403 Γ0.0108 Θ-0.208 · IV 0.287 · mid 6.60
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 68
  headline "FedEx Hits New 52-Week High as UPS Earnings Beat Ignites Logistics Sector Rally"
WHY
  underlying -2.4%/-11.3%/-10.1% (favorable peak +0.1%); position move -10.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-248% · IV residual ~197% [inferred].
  convexity Γ·S = 4.37. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GEV-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI n/a · spread +0.1%
  greeks Δ0.491 Γ0.0038 Θ-1.514 · IV 0.460 · mid 48.22
  overnight_score 7 · flow HEDGING · catalyst Guidance Raise (0.95) · RSI 81
  headline "GE Vernova Raises 2026 Guidance as AI Data Center Orders in April Already Surpass Entire First Quarter"
WHY
  underlying -0.0%/-2.5%/-5.3% (favorable peak +1.5%); position move -5.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-62% · IV residual ~11% [inferred].
  convexity Γ·S = 4.32. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GNK-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 27 · V/OI 0.11 · spread +0.1%
  greeks Δ0.349 Γ0.2870 Θ-0.009 · IV 0.194 · mid 0.53
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.88) · RSI 60
  headline "Genco Shipping (GNK) Gained 2.5% Amid Ongoing Proxy Battle With Diana Shipping"
WHY
  underlying -1.1%/-6.1%/-3.0% (favorable peak +1.2%); position move -3.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-49% · IV residual ~-6% [inferred].
  convexity Γ·S = 7.02. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HIMS-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.387 Γ0.0497 Θ-0.086 · IV 1.139 · mid 1.91
  overnight_score 7 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 75
  headline "HIMS Stock Surges 48% In One Week Following FDA Peptide Review Announcement and RFK Jr. Support"
WHY
  underlying -4.0%/-6.4%/-9.2% (favorable peak +1.4%); position move -9.2%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-58% · IV residual ~11% [inferred].
  convexity Γ·S = 1.54. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HLT-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 1.00 · spread +0.1%
  greeks Δ0.301 Γ0.0235 Θ-0.304 · IV 0.300 · mid 5.95
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 47
  headline "Hilton Worldwide (HLT) Price Target Raised to $353 by Susquehanna as Sector RevPAR Trends Positive"
WHY
  underlying -0.4%/-1.5%/-1.9% (favorable peak +0.8%); position move -1.9%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-30% · IV residual ~-14% [inferred].
  convexity Γ·S = 7.54. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HON-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 27.00 · spread +0.0%
  greeks Δ0.418 Γ0.0275 Θ-0.208 · IV 0.315 · mid 4.86
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 50
  headline "Honeywell to Release First Quarter Financial Results and Hold its Investor Conference Call on Thursday, Apr…"
WHY
  underlying -1.6%/-4.9%/-5.8% (favorable peak +0.0%); position move -5.8%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-117% · IV residual ~70% [inferred].
  convexity Γ·S = 6.41. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HSY-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 0.81 · spread +0.1%
  greeks Δ0.257 Γ0.0291 Θ-0.208 · IV 0.375 · mid 1.52
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 35
  headline "Hershey (HSY) Reports Q1 Earnings Beat as Collapsing Cocoa Prices Signal Margin Recovery"
WHY
  underlying -1.8%/-3.6%/-3.8% (favorable peak +0.1%); position move -3.8%.
  decomp [first-order]: theta drag ~41% of premium / 3d · delta capture ~-121% · IV residual ~102% [inferred].
  convexity Γ·S = 5.50. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE IBKR-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 7 · V/OI 2.05 · spread +0.0%
  greeks Δ0.837 Γ0.0533 Θ-0.079 · IV 0.359 · mid 3.06
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 71
  headline "Interactive Brokers Group Hits All-Time High as Macro Optimism and Record Earnings Fuel Growth"
WHY
  underlying -1.4%/-2.4%/-5.5% (favorable peak -0.3%); position move -5.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-132% · IV residual ~80% [inferred].
  convexity Γ·S = 4.70. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.252 Γ0.0044 Θ-0.394 · IV 0.625 · mid 9.85
  overnight_score 8 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 51
  headline "Intuit (INTU) Set to Report Q3 Earnings Today with Strong AI Expectations and Consensus EPS of $12.57"
WHY
  underlying -0.9%/-4.8%/-23.8% (favorable peak +5.2%); position move -23.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-246% · IV residual ~198% [inferred].
  convexity Γ·S = 1.78. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KLAC-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 0.75 · spread +0.0%
  greeks Δ0.125 Γ0.0006 Θ-0.936 · IV 0.548 · mid 13.40
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 58
  headline "KLA Corporation Announces Ten-to-One Stock Split and $7 Billion Share Repurchase Authorization"
WHY
  underlying +2.3%/-2.5%/-5.0% (favorable peak +3.3%); position move -5.0%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-87% · IV residual ~48% [inferred].
  convexity Γ·S = 1.20. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KLAC-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 0.32 · spread +0.0%
  greeks Δ0.427 Γ0.0013 Θ-1.836 · IV 0.534 · mid 91.45
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.88) · RSI 61
  headline "KLA Corporation Raises 2026 Advanced Packaging Outlook Amid Surging AI Infrastructure Demand"
WHY
  underlying -4.8%/-7.2%/-8.0% (favorable peak -2.6%); position move -8.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-71% · IV residual ~17% [inferred].
  convexity Γ·S = 2.41. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KLAC-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 3.90 · spread +0.1%
  greeks Δ0.564 Γ0.0015 Θ-2.998 · IV 0.620 · mid 106.00
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 71
  headline "KLA Corporation (KLAC) Scheduled to Report Q3 Fiscal 2026 Results on April 29; Analysts Expect AI Demand Boost"
WHY
  underlying -4.8%/-4.4%/-7.9% (favorable peak -2.3%); position move -7.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-80% · IV residual ~28% [inferred].
  convexity Γ·S = 2.91. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LMT-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 17 · V/OI 18.93 · spread +0.0%
  greeks Δ0.031 Γ0.0011 Θ-0.121 · IV 0.528 · mid 0.88
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.78) · RSI 42
  headline "Lockheed Martin (LMT) Secures $879.1M Contract for Aircraft Armament; Fitch Affirms 'A' Rating"
WHY
  underlying -0.3%/-1.1%/-1.0% (favorable peak +0.4%); position move -1.0%.
  decomp [first-order]: theta drag ~41% of premium / 3d · delta capture ~-19% · IV residual ~1% [inferred].
  convexity Γ·S = 0.60. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LNG-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 3.10 · spread +0.0%
  greeks Δ0.298 Γ0.0129 Θ-0.203 · IV 0.393 · mid 4.85
  overnight_score 3 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 34
  headline "Cheniere Energy Slumps on GAAP Derivative Loss Despite Raising Full-Year Guidance and Posting Adjusted Earn…"
WHY
  underlying -3.0%/-8.4%/-10.9% (favorable peak -1.1%); position move -10.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-181% · IV residual ~133% [inferred].
  convexity Γ·S = 3.49. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MBLY-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 4.36 · spread +0.1%
  greeks Δ0.397 Γ0.1709 Θ-0.016 · IV 0.761 · mid 0.58
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 78
  headline "Mobileye Beats on Q1 Earnings, Raises Outlook, Sets $250M Buyback"
WHY
  underlying -1.4%/-4.8%/-11.3% (favorable peak +1.3%); position move -11.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-81% · IV residual ~30% [inferred].
  convexity Γ·S = 1.80. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MCHP-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI n/a · spread +0.1%
  greeks Δ0.412 Γ0.0312 Θ-0.169 · IV 0.694 · mid 3.65
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 86
  headline "Microchip Technology Launches AI Data Center Timing Modules Amid Sector-Wide Rally Triggered by Texas Instr…"
WHY
  underlying -1.3%/-4.2%/-7.0% (favorable peak +0.9%); position move -7.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-72% · IV residual ~26% [inferred].
  convexity Γ·S = 2.83. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MDGL-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.534 Γ0.0055 Θ-0.374 · IV 0.397 · mid 27.30
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 48
  headline "Madrigal Pharmaceuticals (MDGL) Posts Q1 Earnings Beat as Rezdiffra Achieves Blockbuster Status"
WHY
  underlying -0.9%/-5.5%/-7.9% (favorable peak +0.4%); position move -7.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-84% · IV residual ~28% [inferred].
  convexity Γ·S = 2.99. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MELI-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 6.50 · spread +0.0%
  greeks Δ0.441 Γ0.0016 Θ-1.781 · IV 0.487 · mid 79.91
  overnight_score 5 · flow HEDGING · catalyst Earnings Miss (0.95) · RSI 35
  headline "MercadoLibre falls 7% in after-hours as earnings miss overshadows revenue beat"
WHY
  underlying +1.6%/-11.3%/-15.4% (favorable peak +2.7%); position move -15.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-157% · IV residual ~103% [inferred].
  convexity Γ·S = 2.86. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE META-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 11 · V/OI n/a · spread +0.0%
  greeks Δ0.263 Γ0.0062 Θ-0.760 · IV 0.470 · mid 4.25
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 57
  headline "Meta launches paid subscriptions for Instagram, Facebook, WhatsApp"
WHY
  underlying +0.0%/-0.4%/-5.5% (favorable peak +1.2%); position move -5.5%.
  decomp [first-order]: theta drag ~54% of premium / 3d · delta capture ~-215% · IV residual ~209% [inferred].
  convexity Γ·S = 3.94. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MO-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 22 · V/OI 6.67 · spread +0.0%
  greeks Δ0.620 Γ0.0922 Θ-0.032 · IV 0.237 · mid 2.08
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 57
  headline "Altria Group Shares Retrace From 52-Week Highs as Institutional Call Volume Surges to $13.7M"
WHY
  underlying -0.4%/-0.6%/-3.9% (favorable peak +1.0%); position move -3.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-83% · IV residual ~28% [inferred].
  convexity Γ·S = 6.67. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MRNA-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ0.420 Γ0.0294 Θ-0.079 · IV 0.778 · mid 5.20
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.90) · RSI 61
  headline "Deadly Hantavirus Reaches US After Cruise Ship Outbreak; MRNA, NVAX Stocks Jump"
WHY
  underlying -2.7%/-2.0%/-7.2% (favorable peak +9.4%); position move -7.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-32% · IV residual ~-24% [inferred].
  convexity Γ·S = 1.60. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NRG-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.1%
  greeks Δ0.404 Γ0.0356 Θ-0.223 · IV 0.476 · mid 2.85
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.80) · RSI 48
  headline "PJM Expedites Data Center Power Procurement, Boosting Outlook for NRG Energy"
WHY
  underlying -1.7%/-2.1%/-4.5% (favorable peak +0.8%); position move -4.5%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~-90% · IV residual ~54% [inferred].
  convexity Γ·S = 5.00. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE OUST-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 4.02 · spread +0.0%
  greeks Δ0.332 Γ0.0303 Θ-0.062 · IV 1.144 · mid 2.31
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 70
  headline "Ouster Stock Surges After NVIDIA Drive Hyperion Qualification for Rev8 Lidar Sensors"
WHY
  underlying +2.0%/+2.0%/-10.0% (favorable peak +5.5%); position move -10.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-49% · IV residual ~-3% [inferred].
  convexity Γ·S = 1.04. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PG-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 58.00 · spread +0.0%
  greeks Δ0.252 Γ0.0312 Θ-0.048 · IV 0.225 · mid 1.56
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 57
  headline "Procter & Gamble investing $205 million in Georgia logistics facility"
WHY
  underlying -1.1%/-2.7%/-4.9% (favorable peak -0.5%); position move -4.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-117% · IV residual ~66% [inferred].
  convexity Γ·S = 4.60. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
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

```
CASE PH-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 4.84 · spread +0.0%
  greeks Δ0.807 Γ0.0028 Θ-0.897 · IV 0.494 · mid 111.31
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 48
  headline "Parker-Hannifin (PH) Scheduled to Release Q3 2026 Earnings April 30; Analysts Expect $7.81 EPS"
WHY
  underlying -4.0%/-6.9%/-8.4% (favorable peak -2.7%); position move -8.4%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-58% · IV residual ~0% [inferred].
  convexity Γ·S = 2.70. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE POET-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.661 Γ0.0759 Θ-0.021 · IV 1.185 · mid 1.96
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 74
  headline "POET Technologies Shares Gap Down -7.4% After Massive AI-Driven Rally and Short-Seller Rebuttal"
WHY
  underlying +28.8%/-32.2%/-31.5% (favorable peak +32.3%); position move -31.5%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-125% · IV residual ~68% [inferred].
  convexity Γ·S = 0.89. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RCL-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 4.00 · spread +0.0%
  greeks Δ0.381 Γ0.0178 Θ-0.484 · IV 0.530 · mid 4.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 47
  headline "Cruise card spending jumps 15.8% in April, Bank of America data shows"
WHY
  underlying +0.4%/-1.5%/-4.4% (favorable peak +4.2%); position move -4.4%.
  decomp [first-order]: theta drag ~35% of premium / 3d · delta capture ~-105% · IV residual ~80% [inferred].
  convexity Γ·S = 4.69. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RDDT-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 5.33 · spread +0.0%
  greeks Δ0.271 Γ0.0112 Θ-0.369 · IV 0.996 · mid 5.17
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 54
  headline "Reddit (RDDT) to Release Q1 2026 Earnings on April 30; Options Market Pricing in Double-Digit Swing"
WHY
  underlying +3.4%/-4.5%/-4.6% (favorable peak +5.3%); position move -4.6%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-37% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.74. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SNOW-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.356 Γ0.0157 Θ-0.188 · IV 0.612 · mid 5.29
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.78) · RSI 48
  headline "Snowflake Reaffirms Guidance and Appoints New CRO Ahead of AI Pulse Product Event"
WHY
  underlying +0.3%/+3.4%/-2.7% (favorable peak +4.2%); position move -2.7%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-27% · IV residual ~-22% [inferred].
  convexity Γ·S = 2.35. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE STRL-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.431 Γ0.0033 Θ-2.695 · IV 0.867 · mid 35.08
  overnight_score 5 · flow HEDGING · catalyst Guidance Raise (0.95) · RSI 78
  headline "Sterling Infrastructure Raises 2026 Guidance Significantly Following Record Q1 Results"
WHY
  underlying -8.4%/-4.7%/-2.0% (favorable peak -0.7%); position move -2.0%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~-22% · IV residual ~-15% [inferred].
  convexity Γ·S = 2.96. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE THC-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 13.54 · spread +0.1%
  greeks Δ0.370 Γ0.0151 Θ-0.296 · IV 0.660 · mid 6.10
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 35
  headline "Tenet to Report its First Quarter 2026 Results on April 30th"
WHY
  underlying +1.5%/-0.2%/+3.3% (favorable peak +5.9%); position move +3.3%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~35% · IV residual ~-80% [inferred].
  convexity Γ·S = 2.68. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TTE-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 0.68 · spread +0.0%
  greeks Δ0.609 Γ0.0897 Θ-0.084 · IV 0.281 · mid 2.30
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.75) · RSI 47
  headline "TotalEnergies SE stock: $2.2 billion renewables JV in Asia lifts low-carbon profile"
WHY
  underlying -3.9%/-5.2%/-5.5% (favorable peak -3.5%); position move -5.5%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-136% · IV residual ~87% [inferred].
  convexity Γ·S = 8.39. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE USAR-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 1.00 · spread +0.0%
  greeks Δ0.440 Γ0.0799 Θ-0.060 · IV 1.003 · mid 1.02
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.95) · RSI 70
  headline "USA Rare Earth Announces Definitive Agreement to Acquire Serra Verde Group for ~$2.8 Billion"
WHY
  underlying +11.2%/+1.1%/-4.3% (favorable peak +13.6%); position move -4.3%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-43% · IV residual ~0% [inferred].
  convexity Γ·S = 1.83. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VRT-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ0.274 Γ0.0076 Θ-0.700 · IV 0.817 · mid 5.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 68
  headline "Vertiv Holdings Is About to Report Q1 Earnings. Options Traders Expect a 10.3% Move in VRT Stock."
WHY
  underlying -0.6%/-2.9%/+2.3% (favorable peak +3.4%); position move +2.3%.
  decomp [first-order]: theta drag ~36% of premium / 3d · delta capture ~35% · IV residual ~-58% [inferred].
  convexity Γ·S = 2.38. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE VRT-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI 2.71 · spread +0.0%
  greeks Δ0.493 Γ0.0049 Θ-0.398 · IV 0.628 · mid 24.56
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 72
  headline "Strong Buy Rating Issued for Vertiv (VRT) with Optimistic Price Target"
WHY
  underlying -1.4%/-9.7%/-14.2% (favorable peak -0.6%); position move -14.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-108% · IV residual ~52% [inferred].
  convexity Γ·S = 1.86. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WOLF-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 7 · V/OI n/a · spread +0.0%
  greeks Δ0.297 Γ0.0223 Θ-0.350 · IV 1.522 · mid 2.28
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 76
  headline "Wolfspeed Shares Surge 24% as Citrini Names it a Top AI Pick Post-Restructuring"
WHY
  underlying +0.6%/+5.8%/-9.0% (favorable peak +16.3%); position move -9.0%.
  decomp [first-order]: theta drag ~46% of premium / 3d · delta capture ~-81% · IV residual ~67% [inferred].
  convexity Γ·S = 1.55. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WPM-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.483 Γ0.0359 Θ-0.261 · IV 0.534 · mid 3.14
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 54
  headline "Wheaton Precious Metals Announces Record Q1 2026 Earnings and 18% Dividend Increase"
WHY
  underlying -2.2%/+3.2%/+6.9% (favorable peak +8.2%); position move +6.9%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~142% · IV residual ~-177% [inferred].
  convexity Γ·S = 4.83. exit STOP → realized -60%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE WYNN-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 2.00 · spread +0.0%
  greeks Δ0.311 Γ0.0417 Θ-0.156 · IV 0.488 · mid 1.87
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 44
  headline "Wynn Resorts Beats Q1 Earnings Estimates, Announces $950M Macau Tower Expansion"
WHY
  underlying +1.3%/+0.6%/-3.6% (favorable peak +2.6%); position move -3.6%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~-63% · IV residual ~29% [inferred].
  convexity Γ·S = 4.43. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GEHC-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI 5.33 · spread +0.0%
  greeks Δ0.499 Γ0.0521 Θ-0.052 · IV 0.373 · mid 2.27
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 44
  headline "GE HealthCare to announce first quarter 2026 results on April 29; analysts eye margin recovery"
WHY
  underlying -2.8%/-15.6%/-13.7% (favorable peak +0.6%); position move -13.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-212% · IV residual ~159% [inferred].
  convexity Γ·S = 3.67. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LOW-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 5.25 · spread +0.0%
  greeks Δ0.227 Γ0.0175 Θ-0.118 · IV 0.316 · mid 1.82
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.80) · RSI 39
  headline "Lowe's Posts Q1 Beat: Tepid Stock Reaction Underscores Housing Market Still in Limbo"
WHY
  underlying -1.6%/-2.7%/-4.1% (favorable peak -0.7%); position move -4.1%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-112% · IV residual ~71% [inferred].
  convexity Γ·S = 3.87. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WFC-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 9.62 · spread +0.0%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 6.35
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.70) · RSI 34
  headline "Wells Fargo upgraded to Buy from Accumulate at Phillip Securities"
WHY
  underlying -4.4%/-7.0%/-5.0% (favorable peak -0.2%); position move -5.0%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~-0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit STOP → realized -60%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TXN-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.427 Γ0.0079 Θ-0.283 · IV 0.508 · mid 14.15
  overnight_score 8 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 70
  headline "Bank of America lifts Texas Instruments price target to $370, names it top AI power semiconductor pick"
WHY
  underlying -0.5%/-3.7%/-7.6% (favorable peak +1.2%); position move -7.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-73% · IV residual ~20% [inferred].
  convexity Γ·S = 2.50. exit TIMEOUT → realized -59%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CL-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 3.61 · spread +0.0%
  greeks Δ0.327 Γ0.1190 Θ-0.064 · IV 0.215 · mid 0.92
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.40) · RSI 64
  headline "Colgate-Palmolive Vote Keeps DEI Criteria And Combined Chair CEO Structure"
WHY
  underlying +0.4%/-1.3%/-3.1% (favorable peak +1.1%); position move -3.1%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-102% · IV residual ~65% [inferred].
  convexity Γ·S = 10.87. exit TIMEOUT → realized -57%.
TAKEAWAY: Directional miss — underlying went against the position.
```

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
CASE MELI-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 2.00 · spread +0.0%
  greeks Δ0.356 Γ0.0015 Θ-1.713 · IV 0.483 · mid 57.30
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 55
  headline "MercadoLibre (MELI) Overdue for Stock Split as Institutions Accumulate on Deep Pullback"
WHY
  underlying +0.2%/-2.4%/-3.7% (favorable peak +2.1%); position move -3.7%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-42% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.84. exit TIMEOUT → realized -57%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RBLX-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.448 Γ0.0280 Θ-0.117 · IV 0.879 · mid 4.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 58
  headline "Roblox Launches Unified Age-Based Safety System and 'Roblox Plus' Subscription Service"
WHY
  underlying -0.9%/-3.5%/-10.3% (favorable peak +4.2%); position move -10.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-71% · IV residual ~23% [inferred].
  convexity Γ·S = 1.73. exit TIMEOUT → realized -57%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GXO-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 0.11 · spread +0.0%
  greeks Δ0.558 Γ0.0589 Θ-0.101 · IV 0.628 · mid 3.22
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 50
  headline "GXO Logistics scheduled to release Q1 2026 results after market close on Tuesday, May 5"
WHY
  underlying -17.7%/-11.3%/-11.2% (favorable peak -6.9%); position move -11.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-109% · IV residual ~62% [inferred].
  convexity Γ·S = 3.31. exit TIMEOUT → realized -56%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VST-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.306 Γ0.0208 Θ-0.171 · IV 0.503 · mid 2.21
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 45
  headline "Vistra Q1 Earnings Beat Estimates as AI-Driven Power Demand Reaffirms Long-Term Bull Case"
WHY
  underlying -3.4%/-6.2%/-6.7% (favorable peak -1.1%); position move -6.7%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~-140% · IV residual ~107% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized -56%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MPWR-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 6.60 · spread +0.0%
  greeks Δ0.143 Γ0.0008 Θ-0.996 · IV 0.596 · mid 21.09
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.80) · RSI 60
  headline "Monolithic Power Systems (MPWR) Price Target Raised to $2,000 at KeyBanc Following Q1 Earnings Beat"
WHY
  underlying -4.0%/-7.9%/-9.0% (favorable peak -1.6%); position move -9.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-99% · IV residual ~59% [inferred].
  convexity Γ·S = 1.24. exit TIMEOUT → realized -55%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LUV-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 6.00 · spread +0.0%
  greeks Δ0.263 Γ0.0539 Θ-0.030 · IV 0.507 · mid 0.86
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 46
  headline "Southwest Airlines Shares Surge After Analysts Boost Forecasts Following Record Q1 Revenue and Profit Turna…"
WHY
  underlying -3.2%/-3.7%/-5.7% (favorable peak +0.9%); position move -5.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-68% · IV residual ~24% [inferred].
  convexity Γ·S = 2.13. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RH-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 63.33 · spread +0.0%
  greeks Δ0.511 Γ0.0191 Θ-0.492 · IV 0.955 · mid 8.36
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 61
  headline "Restoration Hardware Holdings Inc stock upgraded to Buy Candidate"
WHY
  underlying +3.9%/+3.4%/+4.0% (favorable peak +5.7%); position move +4.0%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~35% · IV residual ~-71% [inferred].
  convexity Γ·S = 2.74. exit TIMEOUT → realized -54%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
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

```
CASE KR-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 6.86 · spread +0.0%
  greeks Δ0.581 Γ0.0822 Θ-0.064 · IV 0.345 · mid 1.88
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 47
  headline "Erste Group initiates Kroger with Buy rating, citing multi-year EPS upside and defensive resilience."
WHY
  underlying -2.7%/-4.6%/-3.1% (favorable peak -0.7%); position move -3.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-67% · IV residual ~24% [inferred].
  convexity Γ·S = 5.68. exit TIMEOUT → realized -54%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AMAT-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 4.12 · spread +0.1%
  greeks Δ0.558 Γ0.0052 Θ-0.459 · IV 0.594 · mid 33.25
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 69
  headline "Applied Materials Joins Tesla's Terafab Project, Validating Equipment Roadmap for Next-Gen Fabs"
WHY
  underlying -2.9%/-8.6%/-8.3% (favorable peak -0.0%); position move -8.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-58% · IV residual ~9% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized -53%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AXTI-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 6.50 · spread +0.0%
  greeks Δ0.484 Γ0.0128 Θ-0.712 · IV 2.343 · mid 9.96
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.92) · RSI 67
  headline "AXT (AXTI) Breaks to New Highs as $550M War Chest Validates AI Growth Strategy"
WHY
  underlying -13.4%/-12.4%/-19.3% (favorable peak -3.9%); position move -19.3%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-82% · IV residual ~50% [inferred].
  convexity Γ·S = 1.12. exit TIMEOUT → realized -53%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ABNB-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 3.36 · spread +0.0%
  greeks Δ0.319 Γ0.0393 Θ-0.190 · IV 0.407 · mid 1.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 69
  headline "Wells Fargo Upgrades Airbnb to Overweight With a $178 Target: Is the Business Inflection Point Finally Here?"
WHY
  underlying -1.6%/-0.9%/-2.2% (favorable peak -0.1%); position move -2.2%.
  decomp [first-order]: theta drag ~32% of premium / 3d · delta capture ~-55% · IV residual ~33% [inferred].
  convexity Γ·S = 5.67. exit TIMEOUT → realized -53%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MP-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI n/a · spread +0.1%
  greeks Δ0.284 Γ0.0274 Θ-0.137 · IV 0.831 · mid 1.50
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 57
  headline "Wedbush Raises MP Materials Price Target to $100 Following Q1 Earnings Beat and Record Production"
WHY
  underlying -4.8%/-7.2%/-7.2% (favorable peak +5.7%); position move -7.2%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~-99% · IV residual ~74% [inferred].
  convexity Γ·S = 1.99. exit TIMEOUT → realized -52%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LITE-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ0.378 Γ0.0015 Θ-1.807 · IV 0.974 · mid 63.75
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 62
  headline "Rothschild & Co Initiates Lumentum at Buy with $1,270 Target Citing AI Infrastructure Leadership"
WHY
  underlying +2.8%/+4.7%/-0.6% (favorable peak +7.5%); position move -0.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-3% · IV residual ~-40% [inferred].
  convexity Γ·S = 1.42. exit TIMEOUT → realized -51%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE EOSE-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 20.00 · spread +0.1%
  greeks Δ0.413 Γ0.1318 Θ-0.017 · IV 1.188 · mid 0.62
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 63
  headline "Eos Energy Enterprises (EOSE) Anticipated to Release Q1 2026 Results on May 13th Amid Surging Momentum"
WHY
  underlying +7.0%/+1.1%/+3.4% (favorable peak +24.2%); position move +3.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~18% · IV residual ~-61% [inferred].
  convexity Γ·S = 1.06. exit TIMEOUT → realized -51%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RIOT-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ0.299 Γ0.0759 Θ-0.018 · IV 0.743 · mid 0.77
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 65
  headline "Riot Platforms Ignites Rally as Bulls Seize Control on AI Pivot and GENIUS Act Regulatory Tailwind"
WHY
  underlying +4.3%/+0.3%/-2.6% (favorable peak +8.9%); position move -2.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-17% · IV residual ~-26% [inferred].
  convexity Γ·S = 1.32. exit TIMEOUT → realized -51%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TMUS-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.266 Γ0.0179 Θ-0.143 · IV 0.391 · mid 2.95
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 41
  headline "T-Mobile to Host Q1 2026 Earnings Call on April 28 Amid Merger Speculation and Analyst Upgrades"
WHY
  underlying -2.2%/-5.8%/-3.8% (favorable peak -0.1%); position move -3.8%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-66% · IV residual ~30% [inferred].
  convexity Γ·S = 3.47. exit TIMEOUT → realized -51%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE OKLO-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ0.443 Γ0.0161 Θ-0.159 · IV 1.079 · mid 6.58
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.90) · RSI 60
  headline "NRC Grants Accelerated Approval for Oklo's Aurora Powerhouse Design Ahead of Pivotal Q1 Earnings"
WHY
  underlying -5.8%/-10.8%/-14.0% (favorable peak -1.9%); position move -14.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-73% · IV residual ~30% [inferred].
  convexity Γ·S = 1.26. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AXTI-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI n/a · spread +0.1%
  greeks Δ0.448 Γ0.0062 Θ-0.363 · IV 1.550 · mid 18.14
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 63
  headline "Optical AI Boom: AXT, Inc. (AXTI) Pulls Back 6% as Institutions Load $160 Calls for July 2026"
WHY
  underlying -7.4%/-12.7%/-22.2% (favorable peak +0.7%); position move -22.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-73% · IV residual ~28% [inferred].
  convexity Γ·S = 0.82. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BA-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 14 · V/OI 6.00 · spread +0.0%
  greeks Δ0.858 Γ0.0127 Θ-0.155 · IV 0.387 · mid 20.35
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 52
  headline "Boeing stock drops 4.5% as Trump's 200-jet China deal fails to meet 500-jet whisper numbers"
WHY
  underlying -3.8%/-3.8%/-6.2% (favorable peak -1.0%); position move -6.2%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-60% · IV residual ~12% [inferred].
  convexity Γ·S = 2.90. exit TIMEOUT → realized -50%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GE-2026-04-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.309 Γ0.0099 Θ-0.175 · IV 0.348 · mid 6.97
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 59
  headline "GE Aerospace to set up F404 engine depot for Indian Air Force ahead of April 21 earnings"
WHY
  underlying -1.3%/-6.2%/-4.4% (favorable peak +0.2%); position move -4.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-61% · IV residual ~21% [inferred].
  convexity Γ·S = 3.16. exit TIMEOUT → realized -48%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TPR-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 6.00 · spread +0.0%
  greeks Δ0.458 Γ0.0357 Θ-0.111 · IV 0.352 · mid 4.20
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.90) · RSI 39
  headline "Tapestry (TPR) Raises FY26 Guidance After Massive Q3 Earnings Beat; Plans $1.6B Shareholder Return"
WHY
  underlying -0.1%/-1.3%/-0.6% (favorable peak +2.8%); position move -0.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-9% · IV residual ~-31% [inferred].
  convexity Γ·S = 4.77. exit TIMEOUT → realized -47%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FICO-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 0.32 · spread +0.1%
  greeks Δ0.363 Γ0.0045 Θ-0.999 · IV 0.350 · mid 20.68
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 43
  headline "FICO raises fiscal 2026 guidance as mortgage scores drive 39% revenue surge"
WHY
  underlying +3.3%/+1.4%/+2.5% (favorable peak +8.4%); position move +2.5%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~44% · IV residual ~-76% [inferred].
  convexity Γ·S = 4.56. exit TIMEOUT → realized -47%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LYV-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ0.258 Γ0.0177 Θ-0.101 · IV 0.381 · mid 2.08
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 61
  headline "Jury Resumes Deliberations in Live Nation Antitrust Trial Amid Record 2026 Ticket Sales"
WHY
  underlying +0.3%/-6.0%/-3.1% (favorable peak +1.7%); position move -3.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-64% · IV residual ~32% [inferred].
  convexity Γ·S = 2.93. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ABNB-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 6.89 · spread +0.0%
  greeks Δ0.356 Γ0.0250 Θ-0.094 · IV 0.372 · mid 6.11
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 49
  headline "DA Davidson and RBC Capital raise Airbnb price targets following strong Q1 revenue beat and raised 2026 out…"
WHY
  underlying -1.1%/-3.0%/-2.5% (favorable peak +1.1%); position move -2.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-20% · IV residual ~-22% [inferred].
  convexity Γ·S = 3.43. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ORCL-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 12.00 · spread +0.1%
  greeks Δ0.296 Γ0.0106 Θ-0.140 · IV 0.561 · mid 5.19
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 59
  headline "Wedbush Crowns Oracle a Foundational AI Infrastructure Play With a $225 Price Target"
WHY
  underlying -0.2%/-4.2%/-5.5% (favorable peak +0.2%); position move -5.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-54% · IV residual ~16% [inferred].
  convexity Γ·S = 1.84. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ELF-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 27 · V/OI 6.25 · spread +0.0%
  greeks Δ0.278 Γ0.0238 Θ-0.089 · IV 0.853 · mid 2.24
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 41
  headline "e.l.f. Beauty Confirms Q4 Fiscal 2026 Earnings Date for May 20 Following Strategic IDL Partnership Launch"
WHY
  underlying -9.3%/-8.5%/-11.7% (favorable peak -0.9%); position move -11.7%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-88% · IV residual ~55% [inferred].
  convexity Γ·S = 1.45. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DY-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 34 · V/OI 5.79 · spread +0.0%
  greeks Δ0.637 Γ0.0042 Θ-0.518 · IV 0.654 · mid 48.02
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 64
  headline "Dycom Industries (DY) Earnings Expected to Grow: What to Know Ahead of Q1 Release"
WHY
  underlying -3.0%/-6.9%/-8.3% (favorable peak -0.9%); position move -8.3%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-50% · IV residual ~8% [inferred].
  convexity Γ·S = 1.88. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ABR-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.311 Γ0.3294 Θ-0.004 · IV 0.549 · mid 0.10
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 31
  headline "Arbor Realty Trust Gathers Momentum After Strategic CLO Redemption and Liquidity Boost"
WHY
  underlying -5.8%/-8.1%/-6.9% (favorable peak -2.5%); position move -6.9%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-127% · IV residual ~93% [inferred].
  convexity Γ·S = 1.95. exit TIMEOUT → realized -46%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE IBM-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.086 Γ0.0047 Θ-0.074 · IV 0.420 · mid 0.83
  overnight_score 9 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 66
  headline "IBM and U.S. Department of Commerce Announce $1 Billion Quantum Chip Foundry Deal"
WHY
  underlying +0.3%/-0.9%/+0.9% (favorable peak +4.5%); position move +0.9%.
  decomp [first-order]: theta drag ~27% of premium / 3d · delta capture ~23% · IV residual ~-41% [inferred].
  convexity Γ·S = 1.18. exit TIMEOUT → realized -45%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CRWD-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 3.50 · spread +0.0%
  greeks Δ0.325 Γ0.0071 Θ-0.532 · IV 0.508 · mid 10.22
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 61
  headline "Mizuho Upgrades CrowdStrike to Outperform with $520 Price Target on AI Security Leadership"
WHY
  underlying +0.1%/-0.5%/-1.9% (favorable peak +2.0%); position move -1.9%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-28% · IV residual ~-1% [inferred].
  convexity Γ·S = 3.23. exit TIMEOUT → realized -45%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MSTR-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 2.64 · spread +0.1%
  greeks Δ0.432 Γ0.0106 Θ-0.266 · IV 0.717 · mid 11.93
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 61
  headline "MicroStrategy May Have Added 2,543 Bitcoin to Its Treasury, Report Says"
WHY
  underlying -5.1%/-10.9%/-11.9% (favorable peak -2.5%); position move -11.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-81% · IV residual ~43% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized -45%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HON-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 3.12 · spread +0.1%
  greeks Δ0.489 Γ0.0394 Θ-0.237 · IV 0.315 · mid 3.84
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 30
  headline "Honeywell's stock drops as sales miss confirms fears of Middle East shipping disruptions; Aerospace spinoff…"
WHY
  underlying +1.9%/+1.0%/-0.3% (favorable peak +2.5%); position move -0.3%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-9% · IV residual ~-17% [inferred].
  convexity Γ·S = 8.29. exit TIMEOUT → realized -45%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE WOLF-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ0.411 Γ0.0128 Θ-0.176 · IV 1.429 · mid 7.34
  overnight_score 6 · flow HEDGING · catalyst Analyst Upgrade (0.85) · RSI 89
  headline "Citrini Research Sets $85 Target for Wolfspeed, Citing Silicon Carbide as Essential AI Infrastructure"
WHY
  underlying -11.2%/-15.2%/-15.9% (favorable peak -0.7%); position move -15.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-62% · IV residual ~25% [inferred].
  convexity Γ·S = 0.89. exit TIMEOUT → realized -44%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LLY-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 8.33 · spread +0.0%
  greeks Δ0.498 Γ0.0035 Θ-0.680 · IV 0.335 · mid 46.47
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 71
  headline "Eli Lilly's Vaccine Push Reshapes Growth Story Beyond Obesity And Diabetes"
WHY
  underlying +4.1%/+2.0%/-0.1% (favorable peak +6.1%); position move -0.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-1% · IV residual ~-38% [inferred].
  convexity Γ·S = 3.84. exit TIMEOUT → realized -44%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE APA-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI n/a · spread +0.1%
  greeks Δ0.544 Γ0.1016 Θ-0.050 · IV 0.478 · mid 1.74
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 53
  headline "Zacks Upgrades APA Corporation to 'Strong Buy' Following Earnings Beat"
WHY
  underlying -2.5%/-1.3%/-4.6% (favorable peak +2.7%); position move -4.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-57% · IV residual ~22% [inferred].
  convexity Γ·S = 4.00. exit TIMEOUT → realized -44%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ULTA-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 23.33 · spread +0.0%
  greeks Δ0.187 Γ0.0050 Θ-0.253 · IV 0.359 · mid 5.33
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 40
  headline "Ulta Beauty (ULTA) Stock Slides as Market Rises: Facts to Know Before You Trade"
WHY
  underlying +1.4%/+0.3%/-2.3% (favorable peak +2.1%); position move -2.3%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-43% · IV residual ~14% [inferred].
  convexity Γ·S = 2.65. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NVTS-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.369 Γ0.0323 Θ-0.134 · IV 1.696 · mid 2.83
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 76
  headline "Vicor's Guidance Lift and AI Power Infrastructure Narrative Propel Navitas to New Highs"
WHY
  underlying -9.2%/-10.3%/-16.3% (favorable peak +0.5%); position move -16.3%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-68% · IV residual ~39% [inferred].
  convexity Γ·S = 1.03. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WULF-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 10.00 · spread +0.0%
  greeks Δ0.554 Γ0.0680 Θ-0.036 · IV 0.820 · mid 2.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 61
  headline "TeraWulf Q1 AI Revenue Surge to $21M Validates Pivot as Institutional Bulls Ignore GAAP Loss"
WHY
  underlying -0.1%/-2.5%/-1.2% (favorable peak +4.1%); position move -1.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-6% · IV residual ~-33% [inferred].
  convexity Γ·S = 1.59. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GLW-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.348 Γ0.0104 Θ-0.272 · IV 0.777 · mid 7.03
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.90) · RSI 71
  headline "Corning (NYSE:GLW) Trading Up as Analysts Re-Rate Stock on $6B Meta AI Infrastructure Deal"
WHY
  underlying -1.3%/-3.9%/-5.2% (favorable peak -0.3%); position move -5.2%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-45% · IV residual ~14% [inferred].
  convexity Γ·S = 1.83. exit TIMEOUT → realized -43%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TER-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.363 Γ0.0053 Θ-0.367 · IV 0.612 · mid 15.63
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 51
  headline "Teradyne upgraded at JP Morgan as firm says sell-off provides 'attractive' entry point"
WHY
  underlying +7.1%/-0.8%/+0.7% (favorable peak +7.3%); position move +0.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~6% · IV residual ~-42% [inferred].
  convexity Γ·S = 1.91. exit TIMEOUT → realized -43%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE IESC-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 15 · V/OI 1.00 · spread +0.0%
  greeks Δ0.167 Γ0.0027 Θ-0.764 · IV 0.792 · mid 7.26
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 59
  headline "IES Holdings Announces Fiscal 2026 Second Quarter Results Earnings Release Schedule for May 1, 2026"
WHY
  underlying +12.6%/+14.6%/+9.5% (favorable peak +18.0%); position move +9.5%.
  decomp [first-order]: theta drag ~32% of premium / 3d · delta capture ~125% · IV residual ~-136% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized -42%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SMCI-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.429 Γ0.0437 Θ-0.045 · IV 0.928 · mid 2.02
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 58
  headline "Super Micro Computer Stock Jumps 9% Despite Oracle Canceling $1.4B Contract: What's Really Driving the Move?"
WHY
  underlying -4.2%/-6.3%/-9.5% (favorable peak +1.4%); position move -9.5%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-59% · IV residual ~23% [inferred].
  convexity Γ·S = 1.27. exit TIMEOUT → realized -42%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TEAM-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.472 Γ0.0255 Θ-0.181 · IV 0.762 · mid 5.83
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 71
  headline "Atlassian stock jumps 30% after Cloud revenue hits $1.1 billion and FY26 guidance is raised"
WHY
  underlying -0.9%/-4.7%/-0.8% (favorable peak +2.0%); position move -0.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-6% · IV residual ~-26% [inferred].
  convexity Γ·S = 2.37. exit TIMEOUT → realized -42%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE LRCX-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.187 Γ0.0051 Θ-0.204 · IV 0.590 · mid 5.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 66
  headline "Lam Research Corp Stock (LRCX) Moved Down by 3.60% on May 7: What Investors Need To Know"
WHY
  underlying +2.6%/+3.3%/+0.9% (favorable peak +4.7%); position move +0.9%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~9% · IV residual ~-40% [inferred].
  convexity Γ·S = 1.46. exit TIMEOUT → realized -41%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ALLY-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 0.24 · spread +0.1%
  greeks Δ0.576 Γ0.1678 Θ-0.031 · IV 0.262 · mid 1.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 61
  headline "Ally Financial price target raised to $54 from $50 at Truist following Q1 results"
WHY
  underlying -2.2%/-3.1%/-2.7% (favorable peak -0.4%); position move -2.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-59% · IV residual ~26% [inferred].
  convexity Γ·S = 7.45. exit TIMEOUT → realized -41%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NRG-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 0.11 · spread +0.0%
  greeks Δ0.293 Γ0.0144 Θ-0.098 · IV 0.436 · mid 4.26
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 35
  headline "NRG Reaffirms 2026 Outlook Despite Q1 EPS Miss, Bolstered by AI Data Center Demand"
WHY
  underlying -4.3%/-9.9%/-12.3% (favorable peak +0.3%); position move -12.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-133% · IV residual ~99% [inferred].
  convexity Γ·S = 2.27. exit TIMEOUT → realized -40%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LITE-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 3.57 · spread +0.1%
  greeks Δ0.463 Γ0.0013 Θ-1.824 · IV 1.009 · mid 95.31
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 59
  headline "Lumentum to Join Nasdaq-100 Index on May 18 as AI Infrastructure Demand Drives Record Growth"
WHY
  underlying -3.1%/-11.7%/-11.2% (favorable peak -1.4%); position move -11.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-54% · IV residual ~20% [inferred].
  convexity Γ·S = 1.29. exit TIMEOUT → realized -40%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ALB-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 45 · V/OI 10.00 · spread +0.0%
  greeks Δ0.280 Γ0.0068 Θ-0.192 · IV 0.673 · mid 9.21
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 63
  headline "Albemarle Crushes Q1 Estimates as Lithium Prices Rebound; UBS Reiterates Buy with $230 Target"
WHY
  underlying -2.1%/-4.3%/-9.0% (favorable peak -0.5%); position move -9.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-57% · IV residual ~23% [inferred].
  convexity Γ·S = 1.43. exit TIMEOUT → realized -40%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MAR-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 25.00 · spread +0.0%
  greeks Δ0.358 Γ0.0146 Θ-0.225 · IV 0.278 · mid 5.90
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.70) · RSI 65
  headline "Marriott (MAR) Raises Full-Year Guidance and Dividend as Premium Travel Demand Outpaces Peers"
WHY
  underlying +3.2%/+3.2%/+0.5% (favorable peak +3.9%); position move +0.5%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~11% · IV residual ~-39% [inferred].
  convexity Γ·S = 5.45. exit TIMEOUT → realized -40%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CRDO-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 3.33 · spread +0.0%
  greeks Δ0.530 Γ0.0061 Θ-0.436 · IV 1.155 · mid 23.60
  overnight_score 8 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 63
  headline "Expanded AI Optical Portfolio Might Change The Case For Investing In Credo Technology Group Holding (CRDO)"
WHY
  underlying -4.6%/-7.1%/-13.3% (favorable peak +2.1%); position move -13.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-59% · IV residual ~26% [inferred].
  convexity Γ·S = 1.21. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CIEN-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 3.75 · spread +0.0%
  greeks Δ0.493 Γ0.0040 Θ-1.224 · IV 0.853 · mid 34.49
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 62
  headline "AI Infrastructure Demand positions company to capture market share and support stronger revenue growth"
WHY
  underlying +5.9%/-1.1%/+0.6% (favorable peak +7.2%); position move +0.6%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~5% · IV residual ~-33% [inferred].
  convexity Γ·S = 2.18. exit TIMEOUT → realized -39%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MPWR-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI 0.83 · spread +0.0%
  greeks Δ0.367 Γ0.0015 Θ-2.151 · IV 0.602 · mid 60.73
  overnight_score 7 · flow MIXED · catalyst — (—) · RSI 62
WHY
  underlying -2.6%/-1.8%/-5.8% (favorable peak +2.7%); position move -5.8%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-58% · IV residual ~30% [inferred].
  convexity Γ·S = 2.53. exit TIMEOUT → realized -39%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LASR-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 13 · V/OI 5.00 · spread +0.0%
  greeks Δ0.596 Γ0.0273 Θ-0.205 · IV 0.927 · mid 6.50
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 57
  headline "Stifel Raises nLIGHT (LASR) Price Target to $85 on Strong Defense Momentum and HADES Product Launch"
WHY
  underlying +3.9%/+3.6%/+0.8% (favorable peak +5.9%); position move +0.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~6% · IV residual ~-35% [inferred].
  convexity Γ·S = 2.15. exit TIMEOUT → realized -38%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CVS-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 8.67 · spread +0.0%
  greeks Δ0.381 Γ0.0467 Θ-0.046 · IV 0.288 · mid 1.90
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 60
  headline "CVS Health price target raised to $106 from $101 at Barclays"
WHY
  underlying +1.0%/-1.2%/-1.6% (favorable peak +2.3%); position move -1.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-29% · IV residual ~-2% [inferred].
  convexity Γ·S = 4.30. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APLD-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI 3.75 · spread +0.0%
  greeks Δ0.375 Γ0.0360 Θ-0.056 · IV 1.032 · mid 2.35
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 61
  headline "Applied Digital Confirms Three Sites in Exclusivity with Hyperscalers for 1GW Data Center Pipeline"
WHY
  underlying +12.1%/+7.9%/+3.8% (favorable peak +18.8%); position move +3.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~20% · IV residual ~-51% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized -38%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TXN-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 4.00 · spread +0.0%
  greeks Δ0.151 Γ0.0156 Θ-0.230 · IV 0.369 · mid 1.20
  overnight_score 6 · flow MIXED · catalyst — (—) · RSI 77
WHY
  underlying -0.0%/-0.1%/-0.0% (favorable peak +1.0%); position move -0.0%.
  decomp [first-order]: theta drag ~58% of premium / 3d · delta capture ~-1% · IV residual ~20% [inferred].
  convexity Γ·S = 4.38. exit TIMEOUT → realized -38%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ABBV-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 14.00 · spread +0.1%
  greeks Δ0.481 Γ0.0199 Θ-0.135 · IV 0.348 · mid 7.10
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 45
  headline "AbbVie hikes 2026 outlook as Skyrizi, Rinvoq offset Humira slump"
WHY
  underlying +3.6%/+1.3%/+2.1% (favorable peak +5.4%); position move +2.1%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~29% · IV residual ~-61% [inferred].
  convexity Γ·S = 4.06. exit TIMEOUT → realized -38%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SHOP-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 1.13 · spread +0.1%
  greeks Δ0.302 Γ0.0169 Θ-0.268 · IV 0.851 · mid 6.65
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 52
  headline "ATB Capital Upgrades Shopify to Outperform on Agentic Commerce Growth Potential"
WHY
  underlying -1.3%/-3.0%/-3.6% (favorable peak +1.2%); position move -3.6%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-21% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.12. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EPD-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI 3.67 · spread +0.0%
  greeks Δ0.222 Γ0.1854 Θ-0.013 · IV 0.187 · mid 0.24
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 66
  headline "JPMorgan and Citigroup Boost EPD Price Targets Citing Strong Fee-Based Cash Flows and Record Volumes"
WHY
  underlying +0.9%/-0.2%/+0.0% (favorable peak +1.8%); position move +0.0%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~1% · IV residual ~-22% [inferred].
  convexity Γ·S = 7.31. exit TIMEOUT → realized -38%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TT-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 0.88 · spread +0.1%
  greeks Δ0.440 Γ0.0092 Θ-0.210 · IV 0.260 · mid 16.77
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 49
  headline "Trane Technologies (TT) Beats Q1 Estimates, Raises 2026 Guidance on Data Center Cooling Strength"
WHY
  underlying +2.2%/-1.6%/-2.4% (favorable peak +3.0%); position move -2.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-30% · IV residual ~-4% [inferred].
  convexity Γ·S = 4.39. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE STX-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 3.21 · spread +0.0%
  greeks Δ0.473 Γ0.0026 Θ-1.508 · IV 0.818 · mid 63.30
  overnight_score 6 · flow DIRECTIONAL · catalyst Insider Activity (0.85) · RSI 73
  headline "Loop Capital raises Seagate (STX) price target to $1,140, citing AI-driven earnings momentum."
WHY
  underlying -6.9%/-7.8%/-5.6% (favorable peak +0.7%); position move -5.6%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-33% · IV residual ~3% [inferred].
  convexity Γ·S = 2.07. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAT-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.263 Γ0.0030 Θ-0.526 · IV 0.420 · mid 17.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 72
  headline "Wells Fargo raises Caterpillar stock price target to $960 on data center demand"
WHY
  underlying -0.5%/-0.8%/-2.1% (favorable peak +0.5%); position move -2.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-27% · IV residual ~-2% [inferred].
  convexity Γ·S = 2.52. exit TIMEOUT → realized -38%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MPWR-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 2.00 · spread +0.1%
  greeks Δ0.488 Γ0.0013 Θ-1.433 · IV 0.542 · mid 108.75
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 63
  headline "Monolithic Power Systems (MPWR) Hits Record Highs on AI Data Center Strength as Analysts Lift Targets to $2…"
WHY
  underlying +4.0%/-0.8%/+0.8% (favorable peak +4.7%); position move +0.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~6% · IV residual ~-39% [inferred].
  convexity Γ·S = 2.13. exit TIMEOUT → realized -37%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE HUT-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.453 Γ0.0272 Θ-0.167 · IV 0.943 · mid 5.03
  overnight_score 5 · flow MIXED · catalyst — (—) · RSI 70
WHY
  underlying +2.8%/+1.9%/+1.7% (favorable peak +7.0%); position move +1.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~10% · IV residual ~-37% [inferred].
  convexity Γ·S = 1.90. exit TIMEOUT → realized -37%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ENTG-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 33 · V/OI 0.75 · spread +0.1%
  greeks Δ0.319 Γ0.0135 Θ-0.145 · IV 0.656 · mid 7.32
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 42
  headline "Entegris Appoints Sukhi Nagesh as CFO Effective May 18 Amid Broad Semiconductor Sector Pullback"
WHY
  underlying -4.4%/-6.7%/-4.0% (favorable peak +2.4%); position move -4.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-23% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE XYZ-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 7.83 · spread +0.1%
  greeks Δ0.465 Γ0.0325 Θ-0.121 · IV 0.719 · mid 4.02
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 63
  headline "Block (XYZ) Nears Key Breakout Level Ahead of Earnings as BTIG and Cantor Fitzgerald Reiterate Bullish Targets"
WHY
  underlying +0.1%/-0.8%/-1.4% (favorable peak +2.3%); position move -1.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-11% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.34. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LOW-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 20.00 · spread +0.0%
  greeks Δ0.302 Γ0.0193 Θ-0.141 · IV 0.297 · mid 3.95
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.35) · RSI 50
  headline "Treasury Yields Rise to 4.3% Pressuring Home Improvement Sector; LOW Sees Bullish Flow"
WHY
  underlying +0.6%/-0.3%/-1.1% (favorable peak +1.0%); position move -1.1%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-20% · IV residual ~-6% [inferred].
  convexity Γ·S = 4.74. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MP-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.355 Γ0.0274 Θ-0.106 · IV 0.796 · mid 2.23
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 68
  headline "Wedbush Projects $90 for MP Materials: Is This the Only Real Play on American Rare Earth Independence?"
WHY
  underlying -0.7%/+4.5%/-4.4% (favorable peak +4.8%); position move -4.4%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-46% · IV residual ~24% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -37%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SPOT-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.277 Γ0.0085 Θ-0.768 · IV 0.478 · mid 7.35
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 62
  headline "KeyBanc raises Spotify stock price target to $745 on AI personalization and margin expansion ahead of Q1 ea…"
WHY
  underlying +0.1%/+1.0%/+1.1% (favorable peak +2.4%); position move +1.1%.
  decomp [first-order]: theta drag ~31% of premium / 3d · delta capture ~21% · IV residual ~-26% [inferred].
  convexity Γ·S = 4.53. exit TIMEOUT → realized -37%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CLSK-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 2.03 · spread +0.1%
  greeks Δ0.697 Γ0.0905 Θ-0.021 · IV 0.996 · mid 1.91
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 70
  headline "CleanSpark (CLSK) Stock Gains on Texas AI Data Center Expansion and Northland 'Strong Buy' Upgrade"
WHY
  underlying -4.0%/-7.6%/-10.9% (favorable peak -0.5%); position move -10.9%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-51% · IV residual ~18% [inferred].
  convexity Γ·S = 1.15. exit TIMEOUT → realized -36%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CLSK-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 2.03 · spread +0.1%
  greeks Δ0.656 Γ0.1049 Θ-0.019 · IV 0.915 · mid 1.91
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 67
  headline "CleanSpark shares jumping as Bitcoin breaks above 78,000 USD, driven by broad risk-on mood and AI infrastru…"
WHY
  underlying +4.3%/+0.2%/-3.6% (favorable peak +8.1%); position move -3.6%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-15% · IV residual ~-18% [inferred].
  convexity Γ·S = 1.28. exit TIMEOUT → realized -36%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WDC-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 15.00 · spread +0.0%
  greeks Δ0.354 Γ0.0058 Θ-1.397 · IV 1.071 · mid 12.85
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 74
  headline "Top Analyst Boosts Western Digital (WDC) Stock Price Target Ahead of Q3 Earnings Even After 116% YTD Surge"
WHY
  underlying +3.6%/+3.8%/+3.0% (favorable peak +7.0%); position move +3.0%.
  decomp [first-order]: theta drag ~33% of premium / 3d · delta capture ~32% · IV residual ~-36% [inferred].
  convexity Γ·S = 2.24. exit TIMEOUT → realized -36%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RCL-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.383 Γ0.0097 Θ-0.223 · IV 0.484 · mid 16.04
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 46
  headline "Royal Caribbean Stock Soars After Blowout Q1 Earnings Beat and Record Booking Volumes"
WHY
  underlying +0.7%/-1.6%/+0.1% (favorable peak +3.1%); position move +0.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~1% · IV residual ~-32% [inferred].
  convexity Γ·S = 2.56. exit TIMEOUT → realized -36%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE GEV-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 4.10 · spread +0.0%
  greeks Δ0.263 Γ0.0023 Θ-0.844 · IV 0.462 · mid 20.18
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 59
  headline "GEV Climbs to $1,090 as the AI Power Bottleneck Lifts Backlog to $163B"
WHY
  underlying -3.8%/-7.2%/-7.2% (favorable peak -2.2%); position move -7.2%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-102% · IV residual ~79% [inferred].
  convexity Γ·S = 2.55. exit TIMEOUT → realized -36%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BLK-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 4.80 · spread +0.0%
  greeks Δ0.240 Γ0.0053 Θ-0.576 · IV 0.254 · mid 8.34
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.80) · RSI 64
  headline "BlackRock CEO Larry Fink Joins Trump-Xi China Summit as AI Infrastructure Pivot Gains Momentum"
WHY
  underlying +0.1%/+1.1%/-1.0% (favorable peak +1.7%); position move -1.0%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-31% · IV residual ~16% [inferred].
  convexity Γ·S = 5.81. exit TIMEOUT → realized -35%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE SNOW-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.477 Γ0.0105 Θ-0.254 · IV 0.793 · mid 12.07
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 66
  headline "Snowflake Shares Gap Up Ahead of Q1 Earnings as Analysts Reiterate $325 Price Targets on AI Potential"
WHY
  underlying +3.2%/+1.7%/+0.8% (favorable peak +7.8%); position move +0.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~5% · IV residual ~-34% [inferred].
  convexity Γ·S = 1.73. exit TIMEOUT → realized -35%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE SKLZ-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 0.17 · spread +0.1%
  greeks Δ0.581 Γ0.1012 Θ-0.019 · IV 1.739 · mid 1.39
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 55
  headline "Skillz (SKLZ) Stock Gains 10% Following Q1 Earnings and $420M Jury Verdict Momentum"
WHY
  underlying -3.6%/-7.8%/-8.4% (favorable peak +4.0%); position move -8.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-24% · IV residual ~-7% [inferred].
  convexity Γ·S = 0.70. exit TIMEOUT → realized -35%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MS-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 4.47 · spread +0.1%
  greeks Δ0.530 Γ0.0231 Θ-0.102 · IV 0.294 · mid 7.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 65
  headline "Erste Group Bank Upgrades Morgan Stanley to Buy as MSIM Launches Stablecoin Reserve Portfolio"
WHY
  underlying -0.2%/-1.4%/-0.7% (favorable peak +1.5%); position move -0.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-10% · IV residual ~-21% [inferred].
  convexity Γ·S = 4.40. exit TIMEOUT → realized -35%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DASH-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 17.65 · spread +0.0%
  greeks Δ0.437 Γ0.0116 Θ-0.222 · IV 0.611 · mid 9.55
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 70
  headline "Cathie Wood's Ark Invest snapped up Amazon and DoorDash stock on Monday"
WHY
  underlying -3.9%/-4.0%/-6.7% (favorable peak +0.4%); position move -6.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-59% · IV residual ~31% [inferred].
  convexity Γ·S = 2.20. exit TIMEOUT → realized -35%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DINO-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI n/a · spread +0.1%
  greeks Δ0.303 Γ0.0662 Θ-0.095 · IV 0.434 · mid 0.92
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 69
  headline "HF Sinclair Q1 2026 EPS of $0.69 beat forecast of $0.07 by 886%"
WHY
  underlying -4.6%/-5.4%/-2.8% (favorable peak -2.3%); position move -2.8%.
  decomp [first-order]: theta drag ~31% of premium / 3d · delta capture ~-68% · IV residual ~64% [inferred].
  convexity Γ·S = 4.93. exit TIMEOUT → realized -35%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SPHR-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 1.40 · spread +0.1%
  greeks Δ0.273 Γ0.0131 Θ-0.108 · IV 0.563 · mid 4.00
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 52
  headline "Sphere Entertainment (SPHR) Q1 2026 Earnings: EPS and Revenue Crush Expectations, Analysts Raise Price Targ…"
WHY
  underlying -2.5%/-7.2%/-0.6% (favorable peak +2.1%); position move -0.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-5% · IV residual ~-21% [inferred].
  convexity Γ·S = 1.79. exit TIMEOUT → realized -35%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MCHP-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ0.492 Γ0.0510 Θ-0.072 · IV 0.362 · mid 2.85
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 80
  headline "As the 'geopolitical discount' evaporates, chipmakers see strong buy-side interest across logic and memory …"
WHY
  underlying +9.9%/+8.4%/+5.3% (favorable peak +11.8%); position move +5.3%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~75% · IV residual ~-102% [inferred].
  convexity Γ·S = 4.20. exit TIMEOUT → realized -34%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE NNE-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 20 · V/OI 5.00 · spread +0.0%
  greeks Δ0.304 Γ0.0531 Θ-0.057 · IV 1.015 · mid 1.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 58
  headline "NANO Nuclear signs MOU with Supermicro for AI data center power"
WHY
  underlying +3.3%/-1.3%/-1.5% (favorable peak +8.3%); position move -1.5%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-12% · IV residual ~-5% [inferred].
  convexity Γ·S = 1.46. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PSX-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.271 Γ0.0224 Θ-0.140 · IV 0.381 · mid 2.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 63
  headline "Raymond James raises Phillips 66 price target to $215 following Q1 earnings beat"
WHY
  underlying +1.0%/-3.8%/-5.7% (favorable peak +1.6%); position move -5.7%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-128% · IV residual ~113% [inferred].
  convexity Γ·S = 3.99. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UAMY-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.585 Γ0.0750 Θ-0.025 · IV 1.298 · mid 2.15
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.88) · RSI 62
  headline "U.S. Antimony Surges as Mining Restart and $248M Defense Backlog Fuel Domestic Critical Mineral Monopoly Th…"
WHY
  underlying +1.2%/-2.2%/-7.2% (favorable peak +5.0%); position move -7.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-23% · IV residual ~-7% [inferred].
  convexity Γ·S = 0.90. exit TIMEOUT → realized -34%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EOG-2026-04-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.610 Γ0.0290 Θ-0.083 · IV 0.345 · mid 6.71
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 44
  headline "Trump's latest statement: The U.S. war with Iran has ended; Oil prices drop as geopolitical premium fades"
WHY
  underlying -1.7%/+0.4%/-3.9% (favorable peak +0.9%); position move -3.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-47% · IV residual ~17% [inferred].
  convexity Γ·S = 3.87. exit TIMEOUT → realized -33%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NOW-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 57.00 · spread +0.1%
  greeks Δ0.475 Γ0.0236 Θ-0.085 · IV 0.558 · mid 5.24
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 41
  headline "ServiceNow Beats Q1 Estimates and Raises Full-Year Guidance Driven by AI Product Momentum"
WHY
  underlying +0.3%/+0.4%/-1.4% (favorable peak +4.3%); position move -1.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-12% · IV residual ~-17% [inferred].
  convexity Γ·S = 2.13. exit TIMEOUT → realized -33%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LUV-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ0.514 Γ0.1135 Θ-0.068 · IV 0.541 · mid 1.36
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.85) · RSI 43
  headline "Southwest Airlines (LUV) Price Target Raised to $47.00 at TD Cowen"
WHY
  underlying -0.5%/-2.6%/-0.7% (favorable peak +0.9%); position move -0.7%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-11% · IV residual ~-7% [inferred].
  convexity Γ·S = 4.33. exit TIMEOUT → realized -33%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AAP-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 0.94 · spread +0.0%
  greeks Δ0.297 Γ0.0426 Θ-0.066 · IV 0.569 · mid 0.71
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 59
  headline "Advance Auto Parts (AAP) stock soars 14.4% on massive Q1 earnings beat and margin recovery"
WHY
  underlying -1.1%/-6.0%/-0.6% (favorable peak +0.9%); position move -0.6%.
  decomp [first-order]: theta drag ~28% of premium / 3d · delta capture ~-15% · IV residual ~10% [inferred].
  convexity Γ·S = 2.50. exit TIMEOUT → realized -33%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MRVL-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 26 · V/OI 4.10 · spread +0.1%
  greeks Δ0.459 Γ0.0080 Θ-0.378 · IV 0.940 · mid 15.32
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 71
  headline "Marvell (MRVL) price targets hiked to $220 by Melius and Citi as AI demand accelerates"
WHY
  underlying +6.1%/+1.2%/+4.3% (favorable peak +11.2%); position move +4.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~25% · IV residual ~-51% [inferred].
  convexity Γ·S = 1.58. exit TIMEOUT → realized -33%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE USAR-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 12.17 · spread +0.0%
  greeks Δ0.432 Γ0.0585 Θ-0.082 · IV 1.157 · mid 1.90
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 63
  headline "USA Rare Earth Announces Date for Release of First Quarter 2026 Results and Conference Call"
WHY
  underlying +4.3%/-3.8%/-1.7% (favorable peak +4.6%); position move -1.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-10% · IV residual ~-9% [inferred].
  convexity Γ·S = 1.61. exit TIMEOUT → realized -33%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE XOM-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 8 · V/OI 30.00 · spread +0.0%
  greeks Δ0.844 Γ0.0182 Θ-0.178 · IV 0.541 · mid 14.88
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 54
  headline "ExxonMobil Stock Drops 4% as Geopolitical Risk Premium Unwinds Amid Ceasefire Hopes"
WHY
  underlying -0.6%/-0.9%/-4.1% (favorable peak +2.0%); position move -4.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-37% · IV residual ~8% [inferred].
  convexity Γ·S = 2.85. exit TIMEOUT → realized -32%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SCCO-2026-04-10-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ0.319 Γ0.0119 Θ-0.201 · IV 0.570 · mid 5.29
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 60
  headline "Goldman Sachs Upgrades Southern Copper to Neutral Citing Copper Scarcity Premium"
WHY
  underlying +2.0%/+0.4%/-1.7% (favorable peak +3.3%); position move -1.7%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-20% · IV residual ~-1% [inferred].
  convexity Γ·S = 2.29. exit TIMEOUT → realized -32%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INOD-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 10.00 · spread +0.0%
  greeks Δ0.385 Γ0.0229 Θ-0.243 · IV 0.917 · mid 5.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 69
  headline "Innodata Surges on Record Q1 Results and New $51M Big Tech Engagement"
WHY
  underlying +0.5%/-6.8%/+4.1% (favorable peak +5.7%); position move +4.1%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~30% · IV residual ~-47% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized -32%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PPG-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI n/a · spread +0.1%
  greeks Δ0.351 Γ0.0491 Θ-0.133 · IV 0.417 · mid 1.97
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 49
  headline "PPG Industries: Strong End-Market Positioning Paints a Favorable Long-Term Growth Outlook (Morningstar)"
WHY
  underlying -1.5%/-2.3%/-1.9% (favorable peak -0.1%); position move -1.9%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-36% · IV residual ~24% [inferred].
  convexity Γ·S = 5.30. exit TIMEOUT → realized -32%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CW-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI 0.99 · spread +0.0%
  greeks Δ0.431 Γ0.0039 Θ-0.497 · IV 0.399 · mid 24.90
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 55
  headline "Curtiss-Wright Reports First Quarter 2026 Financial Results and Raises Full-Year 2026 Guidance"
WHY
  underlying -2.5%/-1.8%/-1.9% (favorable peak +1.0%); position move -1.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-25% · IV residual ~-1% [inferred].
  convexity Γ·S = 2.91. exit TIMEOUT → realized -32%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TLN-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 26 · V/OI 66.67 · spread +0.0%
  greeks Δ0.388 Γ0.0064 Θ-0.459 · IV 0.608 · mid 14.20
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 55
  headline "Talen Energy price target raised to $499 from $498 at Morgan Stanley"
WHY
  underlying +4.4%/+2.0%/+2.4% (favorable peak +6.0%); position move +2.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~25% · IV residual ~-47% [inferred].
  convexity Γ·S = 2.39. exit TIMEOUT → realized -32%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HON-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 26 · V/OI n/a · spread +0.0%
  greeks Δ0.423 Γ0.0225 Θ-0.131 · IV 0.284 · mid 5.46
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 61
  headline "Honeywell prepares for major strategic transformation with July 2026 aerospace spin-off and Quantinuum funding"
WHY
  underlying +1.7%/+1.6%/+2.2% (favorable peak +3.5%); position move +2.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~39% · IV residual ~-64% [inferred].
  convexity Γ·S = 5.12. exit TIMEOUT → realized -32%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LEN-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 3.83 · spread +0.0%
  greeks Δ0.467 Γ0.0461 Θ-0.111 · IV 0.465 · mid 2.34
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.70) · RSI 45
  headline "U.S. Labor Productivity Rises 0.8% in Q1 as Jobless Claims Fall to 200,000; Rates Pressure Homebuilders"
WHY
  underlying -3.1%/-2.4%/-3.8% (favorable peak +1.0%); position move -3.8%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-69% · IV residual ~52% [inferred].
  convexity Γ·S = 4.17. exit TIMEOUT → realized -31%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE JBL-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 0.47 · spread +0.0%
  greeks Δ0.305 Γ0.0069 Θ-0.216 · IV 0.428 · mid 10.00
  overnight_score 2 · flow HEDGING · catalyst Sector Rotation (0.75) · RSI 65
  headline "Jabil Inc.'s Stock Price Plummets 6.1% Amid Sector Rotation and Insider Selling Reports"
WHY
  underlying +10.4%/+3.7%/+5.3% (favorable peak +10.4%); position move +5.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~55% · IV residual ~-79% [inferred].
  convexity Γ·S = 2.31. exit TIMEOUT → realized -31%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE IBM-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.381 Γ0.0159 Θ-0.110 · IV 0.307 · mid 5.31
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.80) · RSI 41
  headline "IBM Stock Rises After Unveiling 'IBM Bob' AI Platform and Receiving HSBC Upgrade"
WHY
  underlying +0.5%/-0.6%/-0.8% (favorable peak +2.2%); position move -0.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-14% · IV residual ~-10% [inferred].
  convexity Γ·S = 3.68. exit TIMEOUT → realized -31%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE NET-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.459 Γ0.0094 Θ-0.350 · IV 0.792 · mid 13.16
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 53
  headline "Piper Sandler Upgrades Cloudflare (NET) to Overweight with $222 Target on AI Infrastructure Strength"
WHY
  underlying +1.4%/+1.3%/+0.1% (favorable peak +3.5%); position move +0.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~1% · IV residual ~-23% [inferred].
  convexity Γ·S = 1.93. exit TIMEOUT → realized -31%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BE-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ0.469 Γ0.0061 Θ-0.639 · IV 0.936 · mid 19.42
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 78
  headline "Bloom Energy Signals Breakout Growth on AI Demand with Blowout Q1 and Raised FY26 Guidance"
WHY
  underlying -0.6%/+1.6%/-1.7% (favorable peak +4.3%); position move -1.7%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-12% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.78. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TWLO-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 26 · V/OI 0.63 · spread +0.0%
  greeks Δ0.262 Γ0.0118 Θ-0.179 · IV 0.567 · mid 4.25
  overnight_score 8 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 61
  headline "Twilio Recognized as a Leader in the 2026 Gartner Magic Quadrant for CPaaS for the Fourth Consecutive Year"
WHY
  underlying +0.9%/-3.4%/-1.7% (favorable peak +1.6%); position move -1.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-20% · IV residual ~3% [inferred].
  convexity Γ·S = 2.21. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CLS-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.308 Γ0.0049 Θ-0.573 · IV 0.708 · mid 10.00
  overnight_score 3 · flow DIRECTIONAL · catalyst Guidance Raise (0.90) · RSI 50
  headline "Celestica Raises 2026 Outlook to $10.15 EPS on AI Infrastructure Strength"
WHY
  underlying -6.9%/-9.3%/-7.9% (favorable peak -0.7%); position move -7.9%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-101% · IV residual ~89% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized -30%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE YUM-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ0.345 Γ0.0306 Θ-0.081 · IV 0.272 · mid 3.25
  overnight_score 1 · flow DIRECTIONAL · catalyst M&A (0.65) · RSI 51
  headline "Pizza Hut edges closer to finding new owners as Yum! Brands explores divestiture"
WHY
  underlying +2.0%/+1.4%/+0.5% (favorable peak +2.9%); position move +0.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~9% · IV residual ~-31% [inferred].
  convexity Γ·S = 4.88. exit TIMEOUT → realized -29%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DOCN-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 31 · V/OI 26.50 · spread +0.0%
  greeks Δ0.414 Γ0.0152 Θ-0.167 · IV 0.986 · mid 6.65
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 59
  headline "Barclays Lifts DigitalOcean (DOCN) Price Target to $105, Citing AI Software Inflection"
WHY
  underlying +5.7%/+6.6%/+7.0% (favorable peak +10.8%); position move +7.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~39% · IV residual ~-61% [inferred].
  convexity Γ·S = 1.36. exit TIMEOUT → realized -29%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TFC-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 4.93 · spread +0.1%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 5.00
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 46
  headline "Truist (TFC) Q1 Earnings Beat and Analyst Upgrades Drive Bullish Institutional Sentiment Despite Short-Term…"
WHY
  underlying -1.3%/-3.6%/-3.9% (favorable peak -0.3%); position move -3.9%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~-0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE C-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 10.00 · spread +0.0%
  greeks Δ0.559 Γ0.0308 Θ-0.074 · IV 0.320 · mid 6.50
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 51
  headline "Citigroup Investor Day: CEO Jane Fraser Sets New Profitability Targets as Restructuring Enters Final Phase"
WHY
  underlying -2.7%/-2.5%/-2.1% (favorable peak +2.2%); position move -2.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-23% · IV residual ~-3% [inferred].
  convexity Γ·S = 3.98. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BKNG-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.305 Γ0.0231 Θ-0.138 · IV 0.440 · mid 3.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 48
  headline "Booking Holdings CEO Defends Valuation, Citing Data Advantage Over AI Threats"
WHY
  underlying +3.1%/+4.0%/+2.5% (favorable peak +4.4%); position move +2.5%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~42% · IV residual ~-57% [inferred].
  convexity Γ·S = 3.77. exit TIMEOUT → realized -29%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE NVTS-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.396 Γ0.0621 Θ-0.032 · IV 1.217 · mid 1.55
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.90) · RSI 60
  headline "Navitas Semiconductor Shares Slide 10% Ahead of Q1 Earnings as Analysts Flag Guidance Risks"
WHY
  underlying +10.2%/+4.8%/-0.8% (favorable peak +13.9%); position move -0.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-3% · IV residual ~-19% [inferred].
  convexity Γ·S = 0.99. exit TIMEOUT → realized -29%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CL-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 2.00 · spread +0.0%
  greeks Δ0.135 Γ0.0451 Θ-0.032 · IV 0.263 · mid 0.41
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 56
  headline "Colgate-Palmolive (CL) Price Target Raised to $100 at Goldman Sachs and Morgan Stanley Following Q1 Beat"
WHY
  underlying +2.1%/+1.2%/+1.4% (favorable peak +3.2%); position move +1.4%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~40% · IV residual ~-45% [inferred].
  convexity Γ·S = 3.90. exit TIMEOUT → realized -29%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE C-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 1.90 · spread +0.1%
  greeks Δ0.343 Γ0.0293 Θ-0.065 · IV 0.307 · mid 4.28
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 65
  headline "Citigroup (C) Hits 52-Week High Following Blowout Q1 Earnings and Debt Tender Offer Announcement"
WHY
  underlying -0.9%/-1.3%/-0.5% (favorable peak +0.2%); position move -0.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-5% · IV residual ~-20% [inferred].
  convexity Γ·S = 3.80. exit TIMEOUT → realized -29%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AEM-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.436 Γ0.0157 Θ-0.216 · IV 0.524 · mid 7.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 35
  headline "Agnico Eagle Mines Slated to Report Q1 2026 Earnings April 30 Following Strategic Expansion in Finland"
WHY
  underlying -3.0%/-0.5%/-3.0% (favorable peak +0.4%); position move -3.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-34% · IV residual ~15% [inferred].
  convexity Γ·S = 2.97. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CF-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI n/a · spread +0.0%
  greeks Δ0.307 Γ0.0153 Θ-0.092 · IV 0.505 · mid 4.22
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 57
  headline "CF Industries shares surge as global fertilizer prices jump on escalating conflict with Iran and Strait of …"
WHY
  underlying -4.1%/-6.1%/-3.9% (favorable peak -0.7%); position move -3.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-38% · IV residual ~15% [inferred].
  convexity Γ·S = 2.00. exit TIMEOUT → realized -29%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FN-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 0.85 · spread +0.0%
  greeks Δ0.306 Γ0.0021 Θ-0.845 · IV 0.757 · mid 21.16
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 57
  headline "Fabrinet (FN) Stock Gains 10% on High Volume as AI Data Center Narrative Regains Momentum"
WHY
  underlying +7.2%/+3.7%/+0.6% (favorable peak +7.6%); position move +0.6%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~6% · IV residual ~-22% [inferred].
  convexity Γ·S = 1.47. exit TIMEOUT → realized -28%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FTAI-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 14 · V/OI n/a · spread +0.0%
  greeks Δ0.385 Γ0.0095 Θ-0.547 · IV 0.800 · mid 13.71
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 50
  headline "FTAI Aviation slides as investors refocus on cash-flow outlook and macro risk"
WHY
  underlying +2.1%/+1.3%/-6.8% (favorable peak +9.5%); position move -6.8%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-48% · IV residual ~32% [inferred].
  convexity Γ·S = 2.42. exit TIMEOUT → realized -28%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE COF-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.315 Γ0.0181 Θ-0.101 · IV 0.334 · mid 4.21
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 50
  headline "Capital One Missed Q1 Estimates, But the Credit Story Investors Fear Is Actually Improving"
WHY
  underlying -0.9%/-0.5%/-2.2% (favorable peak +0.7%); position move -2.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-32% · IV residual ~11% [inferred].
  convexity Γ·S = 3.42. exit TIMEOUT → realized -28%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RKLB-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 7.62 · spread +0.1%
  greeks Δ0.465 Γ0.0113 Θ-0.291 · IV 1.041 · mid 10.34
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.88) · RSI 70
  headline "Rocket Lab Shares Rebound as Institutional Buyers Target $138 Resistance Following Macro Shakeout"
WHY
  underlying -2.9%/+2.4%/-4.4% (favorable peak +3.2%); position move -4.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-26% · IV residual ~7% [inferred].
  convexity Γ·S = 1.48. exit TIMEOUT → realized -28%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EMR-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 2.37 · spread +0.0%
  greeks Δ0.789 Γ0.0172 Θ-0.154 · IV 0.578 · mid 13.89
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.80) · RSI 52
  headline "Emerson Electric Raises FY2026 EPS Guidance Floor on Record Software and Grid Management Demand"
WHY
  underlying +6.9%/+2.0%/+2.1% (favorable peak +8.0%); position move +2.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~17% · IV residual ~-41% [inferred].
  convexity Γ·S = 2.38. exit TIMEOUT → realized -28%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CRCL-2026-04-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.467 Γ0.0175 Θ-0.196 · IV 0.842 · mid 6.78
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 56
  headline "Circle founder confirms Arc Network token launch as CRCL debuts institutional payments platform"
WHY
  underlying +0.0%/+1.9%/+0.4% (favorable peak +5.4%); position move +0.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~3% · IV residual ~-21% [inferred].
  convexity Γ·S = 1.85. exit TIMEOUT → realized -27%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ZETA-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 2.80 · spread +0.0%
  greeks Δ0.341 Γ0.0956 Θ-0.019 · IV 0.613 · mid 0.42
  overnight_score 8 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 57
  headline "ZETA Reinstated by B of A Securities -- Price Target Announced at $24"
WHY
  underlying -4.6%/-4.4%/-5.9% (favorable peak +3.1%); position move -5.9%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-93% · IV residual ~79% [inferred].
  convexity Γ·S = 1.83. exit TIMEOUT → realized -27%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RKLB-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 17.00 · spread +0.0%
  greeks Δ0.346 Γ0.0161 Θ-0.122 · IV 0.892 · mid 4.54
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 56
  headline "Rocket Lab Wins $190 Million Defense Contract and Partners with Meta on Orbital Power Systems"
WHY
  underlying -4.5%/-2.7%/-4.5% (favorable peak +1.6%); position move -4.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-29% · IV residual ~10% [inferred].
  convexity Γ·S = 1.33. exit TIMEOUT → realized -27%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UNH-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 8 · V/OI n/a · spread +0.0%
  greeks Δ0.983 Γ0.0031 Θ-0.041 · IV 0.217 · mid 25.45
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 61
  headline "UNH Maintained by Bernstein -- Price Target Raised to $492"
WHY
  underlying -0.4%/-1.0%/-1.1% (favorable peak +1.4%); position move -1.1%.
  decomp [first-order]: theta drag ~0% of premium / 3d · delta capture ~-16% · IV residual ~-10% [inferred].
  convexity Γ·S = 1.20. exit TIMEOUT → realized -27%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ALB-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.1%
  greeks Δ0.269 Γ0.0078 Θ-0.208 · IV 0.640 · mid 2.10
  overnight_score 7 · flow HEDGING · catalyst Analyst Upgrade (0.90) · RSI 72
  headline "Albemarle Stock Pops As Analysts Hike Lithium Outlook"
WHY
  underlying -8.3%/-9.6%/-8.0% (favorable peak -3.5%); position move -8.0%.
  decomp [first-order]: theta drag ~30% of premium / 3d · delta capture ~-220% · IV residual ~223% [inferred].
  convexity Γ·S = 1.67. exit TIMEOUT → realized -27%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HSY-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 8 · V/OI 160.00 · spread +0.1%
  greeks Δ0.609 Γ0.0384 Θ-0.220 · IV 0.341 · mid 4.15
  overnight_score 1 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 48
  headline "S&P Global Ratings revises The Hershey Co. outlook to stable from negative on expected EBITDA expansion"
WHY
  underlying -0.2%/+2.1%/+0.1% (favorable peak +2.7%); position move +0.1%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~4% · IV residual ~-15% [inferred].
  convexity Γ·S = 7.32. exit TIMEOUT → realized -27%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE INOD-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.554 Γ0.0228 Θ-0.262 · IV 0.959 · mid 6.25
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 76
  headline "Innodata (INOD) Up After Hiking 2026 Revenue Growth Outlook To ~40% Or More"
WHY
  underlying -1.4%/-8.2%/-1.4% (favorable peak +3.5%); position move -1.4%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-12% · IV residual ~-1% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SHOO-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 142.19 · spread +0.0%
  greeks Δ0.668 Γ0.0644 Θ-0.068 · IV 0.746 · mid 3.16
  overnight_score 1 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 49
  headline "Steven Madden (SHOO) to Release Quarterly Earnings on Wednesday, May 6; Analysts Eye Guidance to Offset Q1 …"
WHY
  underlying +1.6%/+1.4%/-1.5% (favorable peak +2.7%); position move -1.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-12% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.38. exit TIMEOUT → realized -26%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SPHR-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 3.75 · spread +0.0%
  greeks Δ0.326 Γ0.0132 Θ-0.115 · IV 0.565 · mid 8.30
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.80) · RSI 58
  headline "Sphere Entertainment to Announce Q1 Earnings on May 5 with Morgan Stanley Raising Price Target to $158"
WHY
  underlying +0.1%/+5.5%/+0.2% (favorable peak +9.2%); position move +0.2%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~1% · IV residual ~-23% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -26%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TSEM-2026-05-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.320 Γ0.0051 Θ-0.444 · IV 0.908 · mid 16.85
  overnight_score 3 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 63
  headline "Tower Semiconductor (TSEM) slips as investors take profits after a sharp post-earnings run"
WHY
  underlying n/a/n/a/n/a (favorable peak n/a); position move n/a.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~n/a% · IV residual ~n/a% [inferred].
  convexity Γ·S = 1.42. exit TIMEOUT → realized -26%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ALB-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 0.83 · spread +0.0%
  greeks Δ0.380 Γ0.0104 Θ-0.238 · IV 0.640 · mid 8.02
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 59
  headline "Citigroup Raises Albemarle (ALB) Price Target to $210 Amid Lithium Market Rebound"
WHY
  underlying -2.1%/-2.7%/-5.1% (favorable peak +1.6%); position move -5.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-48% · IV residual ~31% [inferred].
  convexity Γ·S = 2.07. exit TIMEOUT → realized -25%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TGT-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.478 Γ0.0427 Θ-0.075 · IV 0.278 · mid 3.12
  overnight_score 8 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 68
  headline "Target Stock Maintains Upward Trajectory Toward 52-Week Highs Despite Lack of Immediate News Catalysts"
WHY
  underlying +1.5%/+0.3%/-0.0% (favorable peak +2.2%); position move -0.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-0% · IV residual ~-18% [inferred].
  convexity Γ·S = 5.56. exit TIMEOUT → realized -25%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AAOI-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 13 · V/OI 0.80 · spread +0.0%
  greeks Δ0.382 Γ0.0063 Θ-0.856 · IV 1.949 · mid 6.85
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 65
  headline "Applied Optoelectronics lands $71M upsized 800G order, ships to second hyperscale customer"
WHY
  underlying -10.1%/-15.4%/-5.8% (favorable peak -4.8%); position move -5.8%.
  decomp [first-order]: theta drag ~37% of premium / 3d · delta capture ~-52% · IV residual ~64% [inferred].
  convexity Γ·S = 1.01. exit TIMEOUT → realized -25%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TRGP-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 0.30 · spread +0.0%
  greeks Δ0.130 Γ0.0091 Θ-0.089 · IV 0.310 · mid 1.58
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 65
  headline "Targa Resources Reports Record Q1 2026 Financial Results and Increases Financial Outlook for 2026"
WHY
  underlying -0.2%/+2.2%/-0.3% (favorable peak +2.3%); position move -0.3%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-7% · IV residual ~-1% [inferred].
  convexity Γ·S = 2.45. exit TIMEOUT → realized -25%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CIEN-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 7 · V/OI n/a · spread +0.0%
  greeks Δ0.499 Γ0.0070 Θ-1.513 · IV 0.799 · mid 20.00
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 65
  headline "Bank of America and JPMorgan Raise CIEN Price Targets to $550, Citing 'Optical Super-Cycle' and AI Cloud Gr…"
WHY
  underlying +2.5%/+1.6%/+2.2% (favorable peak +5.5%); position move +2.2%.
  decomp [first-order]: theta drag ~23% of premium / 3d · delta capture ~27% · IV residual ~-29% [inferred].
  convexity Γ·S = 3.46. exit TIMEOUT → realized -25%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CRM-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 24.00 · spread +0.1%
  greeks Δ0.586 Γ0.0119 Θ-0.161 · IV 0.530 · mid 14.82
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 51
  headline "Salesforce (CRM) Stock Bounces 4% as Software Sector Rallies and Company Clarifies AI Revenue Reporting Str…"
WHY
  underlying +0.9%/+1.7%/-1.4% (favorable peak +3.5%); position move -1.4%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-10% · IV residual ~-11% [inferred].
  convexity Γ·S = 2.19. exit TIMEOUT → realized -25%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RDDT-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.438 Γ0.0104 Θ-0.312 · IV 0.879 · mid 11.21
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 68
  headline "Reddit to Announce First Quarter Results on Thursday, April 30, 2026"
WHY
  underlying -5.7%/-1.2%/-8.0% (favorable peak +1.0%); position move -8.0%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-52% · IV residual ~36% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VRT-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.555 Γ0.0084 Θ-0.550 · IV 0.712 · mid 20.23
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 68
  headline "Citigroup and BofA Raise Vertiv Price Targets to $340 and $330 as AI Infrastructure Demand Accelerates"
WHY
  underlying +3.5%/+0.4%/-1.9% (favorable peak +4.2%); position move -1.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-16% · IV residual ~0% [inferred].
  convexity Γ·S = 2.53. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MCK-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 27 · V/OI 0.26 · spread +0.0%
  greeks Δ0.639 Γ0.0067 Θ-0.424 · IV 0.268 · mid 28.12
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.80) · RSI 41
  headline "McKesson (MCK) Reports Strong Q4 Results, Provides Fiscal 2027 Guidance, and Reaffirms Long-Term Financial …"
WHY
  underlying -0.1%/-1.6%/-1.3% (favorable peak +0.8%); position move -1.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-23% · IV residual ~3% [inferred].
  convexity Γ·S = 5.11. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PSX-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 25.00 · spread +0.0%
  greeks Δ0.510 Γ0.0425 Θ-0.132 · IV 0.268 · mid 6.13
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.75) · RSI 51
  headline "Phillips 66 Preliminary Guidance Flags $900M Hedging Loss and Collateral Outflows"
WHY
  underlying +2.1%/-0.1%/+0.3% (favorable peak +3.4%); position move +0.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~5% · IV residual ~-22% [inferred].
  convexity Γ·S = 7.40. exit TIMEOUT → realized -24%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE PCG-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.1%
  greeks Δ0.478 Γ0.2046 Θ-0.009 · IV 0.313 · mid 0.66
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 48
  headline "Jefferies Downgrades PG&E to Hold on Wildfire Liability Risks; Shares Slide 4%"
WHY
  underlying -1.0%/-2.0%/-2.1% (favorable peak +0.5%); position move -2.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-27% · IV residual ~7% [inferred].
  convexity Γ·S = 3.63. exit TIMEOUT → realized -24%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CDE-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.478 Γ0.0990 Θ-0.034 · IV 0.784 · mid 1.25
  overnight_score 3 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 49
  headline "Coeur Mining Completes New Gold Acquisition, Launches $750M Buyback and Inaugural Dividend"
WHY
  underlying -6.8%/-2.3%/-4.7% (favorable peak -0.6%); position move -4.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-35% · IV residual ~20% [inferred].
  convexity Γ·S = 1.96. exit TIMEOUT → realized -23%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MPWR-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 1.57 · spread +0.1%
  greeks Δ0.375 Γ0.0012 Θ-1.443 · IV 0.593 · mid 80.07
  overnight_score 2 · flow DIRECTIONAL · catalyst Guidance Raise (0.90) · RSI 66
  headline "Monolithic Power Systems price target raised to $2,000 at KeyBanc following AI-driven guidance raise"
WHY
  underlying +0.9%/+5.0%/+0.2% (favorable peak +5.6%); position move +0.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~1% · IV residual ~-19% [inferred].
  convexity Γ·S = 1.85. exit TIMEOUT → realized -23%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ALB-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 4.00 · spread +0.0%
  greeks Δ0.391 Γ0.0119 Θ-0.415 · IV 0.835 · mid 7.67
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 53
  headline "Analysts Raise Albemarle Earnings Estimates as Lithium Prices Rebound Toward CNY 160,000"
WHY
  underlying +3.0%/+1.6%/-0.1% (favorable peak +4.2%); position move -0.1%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-1% · IV residual ~-6% [inferred].
  convexity Γ·S = 2.27. exit TIMEOUT → realized -23%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TXN-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 27.00 · spread +0.0%
  greeks Δ0.383 Γ0.0175 Θ-0.441 · IV 0.458 · mid 5.06
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 76
  headline "Texas Instruments Beats Q1 Estimates and Raises Guidance on Strong Industrial and Data Center Demand"
WHY
  underlying +3.8%/+4.4%/+2.6% (favorable peak +5.1%); position move +2.6%.
  decomp [first-order]: theta drag ~26% of premium / 3d · delta capture ~57% · IV residual ~-54% [inferred].
  convexity Γ·S = 5.16. exit TIMEOUT → realized -23%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MS-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 13.50 · spread +0.0%
  greeks Δ0.047 Γ0.0066 Θ-0.026 · IV 0.269 · mid 0.30
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 64
  headline "Morgan Stanley's role as a lead underwriter on the SpaceX IPO positions the firm to secure significant unde…"
WHY
  underlying +1.4%/+1.6%/+2.0% (favorable peak +3.1%); position move +2.0%.
  decomp [first-order]: theta drag ~26% of premium / 3d · delta capture ~63% · IV residual ~-59% [inferred].
  convexity Γ·S = 1.30. exit TIMEOUT → realized -22%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SNPS-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 1.62 · spread +0.0%
  greeks Δ0.320 Γ0.0072 Θ-1.157 · IV 0.669 · mid 10.52
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 61
  headline "Synopsys (SNPS) Gains 1.8% as Analysts Reiterate Buy Ratings Ahead of Next Week's Earnings"
WHY
  underlying +4.1%/+6.1%/+4.4% (favorable peak +7.0%); position move +4.4%.
  decomp [first-order]: theta drag ~33% of premium / 3d · delta capture ~67% · IV residual ~-56% [inferred].
  convexity Γ·S = 3.64. exit TIMEOUT → realized -22%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ZM-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 9 · V/OI 54.80 · spread +0.1%
  greeks Δ0.496 Γ0.0296 Θ-0.284 · IV 0.806 · mid 5.22
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Miss (0.75) · RSI 61
  headline "Zoom Communications Misses Q1 EPS Estimates but Beats Revenue on AI Momentum and Enterprise Strength"
WHY
  underlying -0.5%/-4.6%/-2.7% (favorable peak +1.0%); position move -2.7%.
  decomp [first-order]: theta drag ~16% of premium / 3d · delta capture ~-27% · IV residual ~21% [inferred].
  convexity Γ·S = 3.05. exit TIMEOUT → realized -22%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VZ-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 2.14 · spread +0.0%
  greeks Δ0.432 Γ0.1149 Θ-0.015 · IV 0.212 · mid 1.28
  overnight_score 3 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 48
  headline "Verizon Raises 2026 Earnings Guidance as Customer Retention and Convergence Strategy Improve Churn"
WHY
  underlying -0.3%/-1.8%/-1.0% (favorable peak +0.6%); position move -1.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-15% · IV residual ~-3% [inferred].
  convexity Γ·S = 5.42. exit TIMEOUT → realized -22%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CART-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.317 Γ0.0539 Θ-0.068 · IV 0.690 · mid 1.15
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 69
  headline "Jefferies Upgrades Instacart to Buy as OpenAI Pivot Eases AI-Disruption Fears"
WHY
  underlying -2.6%/-1.1%/-3.0% (favorable peak +1.7%); position move -3.0%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-37% · IV residual ~33% [inferred].
  convexity Γ·S = 2.37. exit TIMEOUT → realized -22%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UNH-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 22 · V/OI 2.86 · spread +0.0%
  greeks Δ0.765 Γ0.0091 Θ-0.238 · IV 0.356 · mid 32.14
  overnight_score 6 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 65
  headline "Warren Buffett's Berkshire Hathaway Exits 5 Million Share UNH Stake Following 47% Recovery Rally"
WHY
  underlying -0.2%/+1.3%/-1.7% (favorable peak +1.9%); position move -1.7%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-15% · IV residual ~-4% [inferred].
  convexity Γ·S = 3.49. exit TIMEOUT → realized -21%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KLAC-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 4.82 · spread +0.1%
  greeks Δ0.299 Γ0.0013 Θ-1.184 · IV 0.453 · mid 49.10
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 61
  headline "KLA Corporation Announces Ten-to-One Stock Split and 21% Quarterly Cash Dividend Increase"
WHY
  underlying +6.0%/+4.6%/+2.7% (favorable peak +7.6%); position move +2.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~29% · IV residual ~-43% [inferred].
  convexity Γ·S = 2.26. exit TIMEOUT → realized -21%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE COIN-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 8.08 · spread +0.1%
  greeks Δ0.532 Γ0.0102 Θ-0.239 · IV 0.662 · mid 16.12
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 51
  headline "Bitmine Stakes $508M ETH via Coinbase Prime as Institutional Demand Surges Ahead of Earnings"
WHY
  underlying +6.1%/+3.4%/+3.5% (favorable peak +9.2%); position move +3.5%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~22% · IV residual ~-38% [inferred].
  convexity Γ·S = 1.96. exit TIMEOUT → realized -21%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LMT-2026-04-10-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ0.491 Γ0.0084 Θ-0.491 · IV 0.328 · mid 21.69
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 44
  headline "Lockheed Martin Wins $4.76 Billion Patriot Deal as Iran Tensions Rise"
WHY
  underlying +1.0%/-0.3%/-0.4% (favorable peak +1.4%); position move -0.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-6% · IV residual ~-8% [inferred].
  convexity Γ·S = 5.13. exit TIMEOUT → realized -21%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE GM-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 19.92 · spread +0.1%
  greeks Δ0.636 Γ0.0415 Θ-0.076 · IV 0.450 · mid 5.98
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 56
  headline "Wolfe Research names GM a 'positive setup' ahead of Q1 earnings despite EV truck program delay"
WHY
  underlying -0.1%/-0.7%/-1.3% (favorable peak +0.9%); position move -1.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-11% · IV residual ~-6% [inferred].
  convexity Γ·S = 3.28. exit TIMEOUT → realized -21%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GS-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 3.33 · spread +0.0%
  greeks Δ0.497 Γ0.0043 Θ-0.452 · IV 0.285 · mid 33.53
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.65) · RSI 63
  headline "Goldman Sachs Alternatives Acquires FGI Worldwide to Deepen Private Credit Push"
WHY
  underlying +1.4%/-0.7%/-0.9% (favorable peak +2.1%); position move -0.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-13% · IV residual ~-3% [inferred].
  convexity Γ·S = 4.08. exit TIMEOUT → realized -20%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CMRE-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 34 · V/OI 0.07 · spread +0.0%
  greeks Δ0.647 Γ0.1951 Θ-0.011 · IV 0.355 · mid 0.96
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 56
  headline "Costamare (CMRE) Surpasses Q1 Estimates as Red Sea Disruptions Fuel 89% Revenue Growth"
WHY
  underlying -2.1%/-2.0%/-4.3% (favorable peak +0.4%); position move -4.3%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-51% · IV residual ~34% [inferred].
  convexity Γ·S = 3.42. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NBIS-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 36 · V/OI n/a · spread +0.1%
  greeks Δ0.377 Γ0.0079 Θ-0.257 · IV 0.920 · mid 8.97
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.95) · RSI 76
  headline "Nebius Group in Talks to Acquire AI21 Labs Following $27B Meta Contract and Goldman Sachs Upgrade to $205"
WHY
  underlying -0.9%/-5.8%/-4.6% (favorable peak +1.2%); position move -4.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-32% · IV residual ~20% [inferred].
  convexity Γ·S = 1.32. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WDAY-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 27 · V/OI 5.00 · spread +0.0%
  greeks Δ0.477 Γ0.0320 Θ-0.097 · IV 0.337 · mid 4.81
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 47
  headline "Workday (WDAY) Reports Impressive Q1 Earnings Beat, Exceeding Analyst Expectations"
WHY
  underlying +5.2%/+1.8%/+2.2% (favorable peak +9.7%); position move +2.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~26% · IV residual ~-40% [inferred].
  convexity Γ·S = 3.89. exit TIMEOUT → realized -20%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AAP-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 6.00 · spread +0.0%
  greeks Δ0.470 Γ0.0390 Θ-0.072 · IV 0.700 · mid 3.79
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 44
  headline "Evercore ISI Adds Advance Auto Parts to 'Tactical Outperform' List Ahead of Earnings"
WHY
  underlying +14.4%/+13.1%/+7.6% (favorable peak +21.4%); position move +7.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~48% · IV residual ~-63% [inferred].
  convexity Γ·S = 2.00. exit TIMEOUT → realized -20%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE EBAY-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.589 Γ0.0325 Θ-0.086 · IV 0.361 · mid 5.85
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 72
  headline "GameStop increases eBay economic exposure to 6.55% in amended filing"
WHY
  underlying -1.5%/-2.7%/-3.1% (favorable peak -0.0%); position move -3.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-37% · IV residual ~21% [inferred].
  convexity Γ·S = 3.86. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BE-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 44 · V/OI 5.75 · spread +0.0%
  greeks Δ0.431 Γ0.0038 Θ-0.486 · IV 1.092 · mid 22.52
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.90) · RSI 65
  headline "Bloom Energy Expands Oracle Partnership for Up to 2.8 GW of Fuel Cells as AI Demand Surges"
WHY
  underlying +3.2%/+8.1%/-1.7% (favorable peak +10.4%); position move -1.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-9% · IV residual ~-4% [inferred].
  convexity Γ·S = 1.06. exit TIMEOUT → realized -20%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZM-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.330 Γ0.0356 Θ-0.085 · IV 0.458 · mid 1.49
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 66
  headline "Zoom (ZM) Breaks Above 200-Day Moving Average as Markets Anticipate AI-Driven Earnings Beat"
WHY
  underlying -2.6%/-1.1%/+1.7% (favorable peak +1.9%); position move +1.7%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~34% · IV residual ~-36% [inferred].
  convexity Γ·S = 3.17. exit TIMEOUT → realized -19%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LITE-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 16 · V/OI 8.00 · spread +0.0%
  greeks Δ0.349 Γ0.0018 Θ-2.277 · IV 1.111 · mid 63.60
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.65) · RSI 55
  headline "Lumentum (LITE) Slides 5% on Convertible Note Exchange; Institutional Flow Remains Aggressively Bullish"
WHY
  underlying +4.4%/+1.2%/+5.3% (favorable peak +7.1%); position move +5.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~25% · IV residual ~-33% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized -19%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE VST-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 3.22 · spread +0.1%
  greeks Δ0.762 Γ0.0125 Θ-0.227 · IV 0.674 · mid 19.51
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 59
  headline "Vistra Corp. (VST) Shares Up 1.2% as Analysts Forecast Growth Amid Nuclear Supercycle News"
WHY
  underlying -3.3%/-7.7%/-5.2% (favorable peak -2.0%); position move -5.2%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-34% · IV residual ~19% [inferred].
  convexity Γ·S = 2.08. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TWLO-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 8 · V/OI 4.82 · spread +0.0%
  greeks Δ0.437 Γ0.0162 Θ-0.556 · IV 1.058 · mid 6.89
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 71
  headline "BofA Double-Upgrades Twilio From Underperform to Buy and Nearly Doubles the Target"
WHY
  underlying -5.9%/-4.4%/-5.2% (favorable peak -1.0%); position move -5.2%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~-50% · IV residual ~55% [inferred].
  convexity Γ·S = 2.44. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UAN-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 0.18 · spread +0.0%
  greeks Δ0.451 Γ0.0164 Θ-0.124 · IV 0.597 · mid 8.10
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 52
  headline "Strait of Hormuz Closure Drives Global Nitrogen Supply Shock; CVR Partners Positioned as Domestic Beneficiary"
WHY
  underlying -3.0%/-0.8%/-3.2% (favorable peak +1.3%); position move -3.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-23% · IV residual ~9% [inferred].
  convexity Γ·S = 2.15. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DG-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI 3.67 · spread +0.0%
  greeks Δ0.466 Γ0.0229 Θ-0.115 · IV 0.514 · mid 5.84
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 36
  headline "Dollar General Launches New 'simmer & stir' Private Label Brand and Enhances Retail Media Network"
WHY
  underlying -0.5%/-0.5%/-3.2% (favorable peak +0.5%); position move -3.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-30% · IV residual ~17% [inferred].
  convexity Γ·S = 2.68. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE Q-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 20 · V/OI 1.88 · spread +0.1%
  greeks Δ0.132 Γ0.0096 Θ-0.117 · IV 0.642 · mid 1.60
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 71
  headline "Qnity Electronics (NYSE:Q) Sets New 52-Week High Amid NVIDIA Collaboration and Institutional Buying"
WHY
  underlying -0.4%/-4.8%/-2.2% (favorable peak +0.2%); position move -2.2%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~-26% · IV residual ~29% [inferred].
  convexity Γ·S = 1.39. exit TIMEOUT → realized -19%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DIS-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 12.50 · spread +0.0%
  greeks Δ0.381 Γ0.0435 Θ-0.049 · IV 0.272 · mid 1.90
  overnight_score 5 · flow DIRECTIONAL · catalyst Guidance Raise (0.75) · RSI 51
  headline "Erste Group raises Disney FY2026 estimates to $6.86 amid 'Blockbuster Summer' campaign launch and leadershi…"
WHY
  underlying -0.5%/-1.0%/-0.8% (favorable peak +0.5%); position move -0.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-16% · IV residual ~5% [inferred].
  convexity Γ·S = 4.52. exit TIMEOUT → realized -19%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CVNA-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.473 Γ0.0053 Θ-0.620 · IV 0.796 · mid 23.60
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 63
  headline "Carvana (CVNA) Short Interest Rises to 14.6% as Analysts Maintain 'Buy' Consensus Ahead of Q1 Earnings"
WHY
  underlying +4.2%/+3.3%/+0.8% (favorable peak +7.4%); position move +0.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~6% · IV residual ~-17% [inferred].
  convexity Γ·S = 1.92. exit TIMEOUT → realized -18%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DAL-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 42 · V/OI n/a · spread +0.0%
  greeks Δ0.694 Γ0.0346 Θ-0.046 · IV 0.428 · mid 6.60
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 57
  headline "Delta Air Lines Jumps as Easing Oil Prices and Post-Earnings Momentum Drive Investor Confidence"
WHY
  underlying +2.6%/+1.9%/+0.5% (favorable peak +7.3%); position move +0.5%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~3% · IV residual ~-20% [inferred].
  convexity Γ·S = 2.42. exit TIMEOUT → realized -18%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TEAM-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 115.50 · spread +0.1%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 7.12
  overnight_score 4 · flow HEDGING · catalyst Earnings Beat (0.95) · RSI 48
  headline "Atlassian lifts annual revenue forecast as AI features, enterprise sales boost growth"
WHY
  underlying +29.6%/+35.8%/+34.6% (favorable peak +40.4%); position move +34.6%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized -18%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE POET-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 36 · V/OI 27.00 · spread +0.1%
  greeks Δ0.572 Γ0.0761 Θ-0.029 · IV 1.237 · mid 2.17
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 54
  headline "POET Technologies Shares Slide as Investors Digest $400M Dilution and Lawsuit Noise"
WHY
  underlying -0.5%/-0.7%/-7.9% (favorable peak +1.5%); position move -7.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-28% · IV residual ~14% [inferred].
  convexity Γ·S = 1.02. exit TIMEOUT → realized -18%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ALAB-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.497 Γ0.0063 Θ-0.316 · IV 0.932 · mid 20.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 67
  headline "Astera Labs (ALAB) Golden Cross Tells Investors About the Next Leg Up Ahead of Earnings"
WHY
  underlying -0.7%/+6.4%/+5.5% (favorable peak +14.3%); position move +5.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~28% · IV residual ~-41% [inferred].
  convexity Γ·S = 1.27. exit TIMEOUT → realized -18%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GNK-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.676 Γ0.1005 Θ-0.023 · IV 0.545 · mid 1.70
  overnight_score 1 · flow DIRECTIONAL · catalyst M&A (0.90) · RSI 56
  headline "Genco Faces Intensified Control Contest As Diana Pushes Cash Offer"
WHY
  underlying +2.5%/+1.3%/-3.7% (favorable peak +3.7%); position move -3.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-35% · IV residual ~22% [inferred].
  convexity Γ·S = 2.40. exit TIMEOUT → realized -18%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BJ-2026-04-10-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.1%
  greeks Δ0.821 Γ0.0282 Θ-0.042 · IV 0.328 · mid 8.29
  overnight_score 1 · flow DIRECTIONAL · catalyst Macro (0.40) · RSI 40
  headline "BJ's Wholesale edges lower in risk-off session dominated by macro uncertainty and oil price volatility."
WHY
  underlying +0.5%/-1.1%/-2.2% (favorable peak +1.3%); position move -2.2%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-20% · IV residual ~4% [inferred].
  convexity Γ·S = 2.61. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ANET-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 10.00 · spread +0.0%
  greeks Δ0.204 Γ0.0091 Θ-0.127 · IV 0.578 · mid 3.60
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 65
  headline "Arista Networks to Announce Q1 2026 Financial Results on Tuesday, May 5, 2026"
WHY
  underlying -0.0%/-0.1%/-1.4% (favorable peak +3.7%); position move -1.4%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-14% · IV residual ~7% [inferred].
  convexity Γ·S = 1.57. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AXON-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 24.70 · spread +0.1%
  greeks Δ0.476 Γ0.0054 Θ-1.096 · IV 0.962 · mid 24.25
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 43
  headline "Axon (AXON) to Report First Quarter 2026 Financial Results on May 6"
WHY
  underlying +1.4%/+2.3%/+0.9% (favorable peak +3.7%); position move +0.9%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~7% · IV residual ~-10% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized -17%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE META-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 16.00 · spread +0.0%
  greeks Δ0.496 Γ0.0044 Θ-0.473 · IV 0.405 · mid 34.42
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.88) · RSI 62
  headline "Meta Strikes Multibillion-Dollar Deal with Amazon to Power 'Agentic AI' Ahead of Q1 Earnings"
WHY
  underlying +0.5%/-0.5%/-0.9% (favorable peak +1.1%); position move -0.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-9% · IV residual ~-4% [inferred].
  convexity Γ·S = 2.94. exit TIMEOUT → realized -17%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FSLR-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 3.00 · spread +0.1%
  greeks Δ0.470 Γ0.0074 Θ-0.374 · IV 0.689 · mid 16.80
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 76
  headline "First Solar, Inc. Given Average Rating of 'Moderate Buy' by Analysts"
WHY
  underlying +10.9%/+12.1%/+10.7% (favorable peak +14.6%); position move +10.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~82% · IV residual ~-92% [inferred].
  convexity Γ·S = 2.03. exit TIMEOUT → realized -17%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE EOG-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 0.91 · spread +0.0%
  greeks Δ0.317 Γ0.0289 Θ-0.132 · IV 0.440 · mid 1.25
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 45
  headline "Siebert Williams raises EOG Resources price target to $177 from $160 following bullish sector outlook"
WHY
  underlying +0.4%/+1.1%/+0.5% (favorable peak +2.0%); position move +0.5%.
  decomp [first-order]: theta drag ~32% of premium / 3d · delta capture ~18% · IV residual ~-3% [inferred].
  convexity Γ·S = 3.82. exit TIMEOUT → realized -17%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CVNA-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 8 · V/OI 668.33 · spread +0.1%
  greeks Δ0.186 Γ0.0039 Θ-1.065 · IV 1.073 · mid 6.26
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 73
  headline "Carvana climbs as traders position for expected Q1 earnings beat and upcoming 5-for-1 stock split"
WHY
  underlying -3.3%/-1.8%/-2.4% (favorable peak -0.7%); position move -2.4%.
  decomp [first-order]: theta drag ~51% of premium / 3d · delta capture ~-30% · IV residual ~64% [inferred].
  convexity Γ·S = 1.61. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MP-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI 2.10 · spread +0.0%
  greeks Δ0.297 Γ0.0202 Θ-0.084 · IV 0.812 · mid 3.47
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 57
  headline "U.S. Needs $2T for Its 'Made in America' Push. That Might Be the Easy Part."
WHY
  underlying -2.7%/-0.2%/-3.4% (favorable peak +2.2%); position move -3.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-20% · IV residual ~10% [inferred].
  convexity Γ·S = 1.35. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VZ-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.357 Γ0.1619 Θ-0.024 · IV 0.225 · mid 0.52
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.75) · RSI 50
  headline "Verizon Communications (VZ) Price Target Raised to $52.00 Following Guidance Hike and Q1 Subscriber Beat"
WHY
  underlying -0.5%/-0.3%/-1.0% (favorable peak +0.5%); position move -1.0%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-33% · IV residual ~30% [inferred].
  convexity Γ·S = 7.70. exit TIMEOUT → realized -17%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MRK-2026-04-10-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 27 · V/OI n/a · spread +0.0%
  greeks Δ0.178 Γ0.0263 Θ-0.049 · IV 0.300 · mid 1.10
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 58
  headline "Merck Secures EU Approval for Keytruda in Ovarian Cancer and Announces $1 Billion Biologics Expansion Amid …"
WHY
  underlying -1.0%/-1.2%/-2.9% (favorable peak -0.1%); position move -2.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-57% · IV residual ~54% [inferred].
  convexity Γ·S = 3.19. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE APLD-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.483 Γ0.0596 Θ-0.056 · IV 0.928 · mid 2.29
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 53
  headline "Applied Digital Post-Earnings Clarity Confirms Accelerated Path To $1 Billion NOI Target"
WHY
  underlying +14.0%/+11.6%/+9.0% (favorable peak +15.7%); position move +9.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~52% · IV residual ~-61% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized -16%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE INTU-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 11.00 · spread +0.0%
  greeks Δ0.390 Γ0.0105 Θ-0.676 · IV 0.530 · mid 8.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 48
  headline "Jefferies analysis indicates beat for Intuit's TurboTax"
WHY
  underlying +0.0%/+1.0%/-5.3% (favorable peak +3.5%); position move -5.3%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~-100% · IV residual ~108% [inferred].
  convexity Γ·S = 4.27. exit TIMEOUT → realized -16%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LMT-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI n/a · spread +0.1%
  greeks Δ0.561 Γ0.0087 Θ-0.241 · IV 0.270 · mid 21.40
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 27
  headline "Israel Greenlights Plan To Buy New Fighter Squadrons From Lockheed Martin, Boeing in $119B Deal"
WHY
  underlying -1.8%/-0.8%/-1.1% (favorable peak +0.4%); position move -1.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-15% · IV residual ~3% [inferred].
  convexity Γ·S = 4.50. exit TIMEOUT → realized -15%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RH-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 38.46 · spread +0.0%
  greeks Δ0.501 Γ0.0183 Θ-0.286 · IV 0.794 · mid 5.10
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.72) · RSI 53
  headline "RH CEO pens letter to city of Milan, announces opening of RH Milan"
WHY
  underlying +4.4%/+2.4%/+4.0% (favorable peak +8.7%); position move +4.0%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~52% · IV residual ~-51% [inferred].
  convexity Γ·S = 2.44. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AMGN-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.357 Γ0.0130 Θ-0.223 · IV 0.319 · mid 7.05
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.65) · RSI 47
  headline "UBS Group Raises Amgen (NASDAQ:AMGN) Price Target to $400.00 as Pipeline Optimism Grows"
WHY
  underlying -1.5%/-1.2%/-0.4% (favorable peak +0.2%); position move -0.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-8% · IV residual ~2% [inferred].
  convexity Γ·S = 4.56. exit TIMEOUT → realized -15%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BE-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.489 Γ0.0099 Θ-0.220 · IV 0.613 · mid 14.02
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 64
  headline "Bloom Energy secures up to 2.8 GW fuel cell deal with Oracle to power AI and cloud infrastructure"
WHY
  underlying +24.0%/+21.0%/+18.9% (favorable peak +29.9%); position move +18.9%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~117% · IV residual ~-127% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE C-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI 84.80 · spread +0.0%
  greeks Δ0.356 Γ0.0296 Θ-0.064 · IV 0.302 · mid 2.64
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 63
  headline "Citigroup Creates New Investment Banking Unit for Financial Sponsors"
WHY
  underlying -0.5%/-1.2%/-0.9% (favorable peak +1.7%); position move -0.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-16% · IV residual ~8% [inferred].
  convexity Γ·S = 3.83. exit TIMEOUT → realized -15%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE PL-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 20 · V/OI 15.40 · spread +0.0%
  greeks Δ0.463 Γ0.0258 Θ-0.151 · IV 1.458 · mid 4.55
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 64
  headline "Planet Labs Shares Hit All-Time High Amid SpaceX IPO Hype and Pelican Satellite Success"
WHY
  underlying +9.0%/+13.8%/+15.9% (favorable peak +16.7%); position move +15.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~72% · IV residual ~-77% [inferred].
  convexity Γ·S = 1.14. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PL-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 5.78 · spread +0.0%
  greeks Δ0.477 Γ0.0243 Θ-0.211 · IV 1.580 · mid 5.00
  overnight_score 7 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 73
  headline "RKLB, SIDU and PL: Space Stocks Rally To 52-Week Highs As SpaceX IPO Anticipation Builds"
WHY
  underlying +1.8%/+1.3%/-8.0% (favorable peak +2.5%); position move -8.0%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-38% · IV residual ~36% [inferred].
  convexity Γ·S = 1.23. exit TIMEOUT → realized -15%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAVA-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 2.50 · spread +0.0%
  greeks Δ0.355 Γ0.0201 Θ-0.144 · IV 0.758 · mid 4.67
  overnight_score 2 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 62
  headline "JPMorgan and Roth/MKM Lead Wave of Analyst Upgrades for CAVA, Citing Strong 2026 Growth Outlook"
WHY
  underlying -3.4%/-3.3%/-0.9% (favorable peak +0.3%); position move -0.9%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-6% · IV residual ~1% [inferred].
  convexity Γ·S = 1.89. exit TIMEOUT → realized -15%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CRDO-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 1.81 · spread +0.1%
  greeks Δ0.647 Γ0.0107 Θ-0.403 · IV 0.878 · mid 7.90
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 77
  headline "Credo Technology Shares Climb 6% After Key Trading Signal; Amazon-Anthropic Deal Named Credo as Beneficiary"
WHY
  underlying +3.4%/+1.2%/+6.4% (favorable peak +8.5%); position move +6.4%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~96% · IV residual ~-95% [inferred].
  convexity Γ·S = 1.95. exit TIMEOUT → realized -15%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GME-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.1%
  greeks Δ0.381 Γ0.0611 Θ-0.030 · IV 0.676 · mid 0.87
  overnight_score 8 · flow DIRECTIONAL · catalyst M&A (0.95) · RSI 65
  headline "GameStop Is Offering to Buy eBay for $56 Billion, CEO Ryan Cohen Says"
WHY
  underlying -10.1%/-8.7%/-5.1% (favorable peak -1.4%); position move -5.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-60% · IV residual ~55% [inferred].
  convexity Γ·S = 1.62. exit TIMEOUT → realized -15%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUT-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 34.00 · spread +0.0%
  greeks Δ0.359 Γ0.0165 Θ-0.260 · IV 1.011 · mid 4.12
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.90) · RSI 74
  headline "Hut 8 Secures $9.8 Billion AI Data Center Lease, Pivoting to Infrastructure Utility Model"
WHY
  underlying +0.9%/+1.9%/-4.5% (favorable peak +4.6%); position move -4.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-42% · IV residual ~47% [inferred].
  convexity Γ·S = 1.77. exit TIMEOUT → realized -15%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AMAT-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 79.67 · spread +0.1%
  greeks Δ0.458 Γ0.0057 Θ-0.396 · IV 0.541 · mid 21.57
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.82) · RSI 65
  headline "Applied Materials Stock (AMAT) Rises as Japanese Giant Joins Multibillion-Dollar R&D Center; Tesla Terafab …"
WHY
  underlying +0.1%/+3.4%/+0.3% (favorable peak +4.2%); position move +0.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~3% · IV residual ~-12% [inferred].
  convexity Γ·S = 2.29. exit TIMEOUT → realized -14%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MDGL-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.647 Γ0.0040 Θ-0.643 · IV 0.639 · mid 50.00
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 61
  headline "Madrigal Pharmaceuticals (NASDAQ:MDGL) Share Price Crosses Above 200 Day Moving Average"
WHY
  underlying +1.4%/+0.4%/+0.6% (favorable peak +2.3%); position move +0.6%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~4% · IV residual ~-14% [inferred].
  convexity Γ·S = 2.09. exit TIMEOUT → realized -14%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CVX-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 45 · V/OI 8.33 · spread +0.0%
  greeks Δ0.395 Γ0.0223 Θ-0.072 · IV 0.268 · mid 4.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 44
  headline "Goldman Sachs Raises Chevron (CVX) Price Target to $216, Citing Production Strength and Cash Flow Outlook"
WHY
  underlying +0.7%/+0.7%/+1.0% (favorable peak +1.5%); position move +1.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~17% · IV residual ~-26% [inferred].
  convexity Γ·S = 4.11. exit TIMEOUT → realized -14%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE QURE-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 40 · V/OI 11.00 · spread +0.0%
  greeks Δ0.434 Γ0.0308 Θ-0.065 · IV 1.369 · mid 3.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 77
  headline "uniQure Surges 15% as UK MHRA Meeting Clears Path for Huntington’s Disease Gene Therapy Filing"
WHY
  underlying -0.1%/+5.2%/+5.5% (favorable peak +7.8%); position move +5.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~21% · IV residual ~-29% [inferred].
  convexity Γ·S = 0.85. exit TIMEOUT → realized -14%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LASR-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 20 · V/OI n/a · spread +0.1%
  greeks Δ0.459 Γ0.0235 Θ-0.166 · IV 0.962 · mid 5.81
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 57
  headline "nLIGHT (LASR) Reports Q1 EPS of $0.20, Doubling Estimates on Surging Defense Demand"
WHY
  underlying +14.9%/+13.4%/+8.8% (favorable peak +17.4%); position move +8.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~51% · IV residual ~-56% [inferred].
  convexity Γ·S = 1.74. exit TIMEOUT → realized -14%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE OHI-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 30 · V/OI 0.05 · spread +0.0%
  greeks Δ0.639 Γ0.1080 Θ-0.021 · IV 0.255 · mid 1.79
  overnight_score 8 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 66
  headline "UBS Raises Omega Healthcare (OHI) Price Target to $54 as Institutional Demand Surges"
WHY
  underlying +0.9%/+1.4%/-0.1% (favorable peak +2.1%); position move -0.1%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-2% · IV residual ~-8% [inferred].
  convexity Γ·S = 5.22. exit TIMEOUT → realized -14%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE EME-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 1.81 · spread +0.0%
  greeks Δ0.824 Γ0.0025 Θ-0.375 · IV 0.318 · mid 81.28
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 66
  headline "EMCOR Group Raises FY 2026 Guidance Following Record Q1 Earnings Beat and 33% Growth in Electrical Construc…"
WHY
  underlying +1.1%/-1.0%/-1.2% (favorable peak +2.0%); position move -1.2%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-12% · IV residual ~-0% [inferred].
  convexity Γ·S = 2.35. exit TIMEOUT → realized -14%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE GILD-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 3.00 · spread +0.0%
  greeks Δ0.269 Γ0.0316 Θ-0.042 · IV 0.238 · mid 2.96
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 40
  headline "Gilead Prices $3 Billion of Senior Unsecured Notes as Management Points to H2 Growth Catalysts"
WHY
  underlying +0.1%/+0.7%/+0.9% (favorable peak +2.1%); position move +0.9%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~10% · IV residual ~-19% [inferred].
  convexity Γ·S = 4.09. exit TIMEOUT → realized -13%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DAVE-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.551 Γ0.0073 Θ-0.481 · IV 0.782 · mid 22.61
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 80
  headline "Dave Stock Surges as New Bull Story Takes Hold with 'Pay in Four' BNPL Launch and Guidance Hike"
WHY
  underlying +2.9%/+0.1%/+0.2% (favorable peak +5.0%); position move +0.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~1% · IV residual ~-8% [inferred].
  convexity Γ·S = 2.01. exit TIMEOUT → realized -13%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE GLW-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 25.55 · spread +0.0%
  greeks Δ0.493 Γ0.0127 Θ-0.299 · IV 0.669 · mid 10.91
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 58
  headline "Corning shares rebound as AI-driven optical demand overshadows temporary solar maintenance costs"
WHY
  underlying +1.1%/+2.2%/-0.5% (favorable peak +4.2%); position move -0.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-5% · IV residual ~-0% [inferred].
  convexity Γ·S = 2.44. exit TIMEOUT → realized -13%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE TECK-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ0.418 Γ0.0470 Θ-0.054 · IV 0.497 · mid 2.35
  overnight_score 3 · flow DIRECTIONAL · catalyst Macro (0.88) · RSI 64
  headline "Oil Prices Jump Above $100/Barrel After Trump Orders Hormuz Blockade"
WHY
  underlying +2.6%/+1.5%/+0.8% (favorable peak +3.1%); position move +0.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~8% · IV residual ~-14% [inferred].
  convexity Γ·S = 2.70. exit TIMEOUT → realized -13%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE UPST-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI n/a · spread +0.1%
  greeks Δ0.464 Γ0.0475 Θ-0.108 · IV 1.168 · mid 2.56
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 67
  headline "Upstart Announces Multi-Year $1.2B Forward-Flow Agreement with Centerbridge Partners to Buy Consumer Loans"
WHY
  underlying -5.5%/-3.6%/-4.7% (favorable peak -1.1%); position move -4.7%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-30% · IV residual ~29% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized -13%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE COIN-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.251 Γ0.0090 Θ-0.331 · IV 0.801 · mid 5.55
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 57
  headline "Coinbase (COIN) Stock Surges After Stablecoin Deal Reached in Senate"
WHY
  underlying -2.6%/-2.5%/-4.9% (favorable peak +2.9%); position move -4.9%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-45% · IV residual ~50% [inferred].
  convexity Γ·S = 1.83. exit TIMEOUT → realized -13%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE WRBY-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.454 Γ0.0538 Θ-0.061 · IV 0.981 · mid 2.58
  overnight_score 4 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 66
  headline "Warby Parker shares surge on Q1 revenue beat and Google AI glasses partnership"
WHY
  underlying -6.4%/-1.0%/+0.4% (favorable peak +4.0%); position move +0.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~2% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.55. exit TIMEOUT → realized -13%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MTZ-2026-04-10-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ0.498 Γ0.0062 Θ-0.390 · IV 0.578 · mid 23.69
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 73
  headline "MasTec Backlog Surges to $19B Driven by Surging AI Data Center and Clean Energy Demand"
WHY
  underlying +1.2%/+1.3%/+1.1% (favorable peak +2.9%); position move +1.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~8% · IV residual ~-16% [inferred].
  convexity Γ·S = 2.25. exit TIMEOUT → realized -13%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RDDT-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.281 Γ0.0083 Θ-0.202 · IV 0.807 · mid 5.96
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 66
  headline "Reddit to Announce First Quarter Results on Thursday, April 30, 2026"
WHY
  underlying +0.8%/+2.4%/-3.5% (favorable peak +3.8%); position move -3.5%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-27% · IV residual ~24% [inferred].
  convexity Γ·S = 1.35. exit TIMEOUT → realized -13%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ASTS-2026-04-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 44 · V/OI n/a · spread +0.1%
  greeks Δ0.399 Γ0.0117 Θ-0.148 · IV 1.065 · mid 7.87
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 49
  headline "Amazon’s $11.6B Globalstar Deal Triggers ASTS Sell-Off Ahead of Critical BlueBird 7 Launch"
WHY
  underlying -1.9%/+2.7%/-3.4% (favorable peak +3.6%); position move -3.4%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-15% · IV residual ~8% [inferred].
  convexity Γ·S = 1.03. exit TIMEOUT → realized -13%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EBAY-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 8 · V/OI 62.00 · spread +0.0%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 12.03
  overnight_score 6 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 52
  headline "eBay Rejects GameStop CEO Ryan Cohen's $56 Billion Acquisition Proposal"
WHY
  underlying +1.3%/-1.0%/-0.0% (favorable peak +1.5%); position move -0.0%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~-0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized -12%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MELI-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 2.23 · spread +0.0%
  greeks Δ0.462 Γ0.0018 Θ-2.145 · IV 0.513 · mid 61.75
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 50
  headline "MercadoLibre CEO signals loan-book sales to mitigate credit risk ahead of May 7 earnings"
WHY
  underlying +3.2%/+1.2%/+1.4% (favorable peak +4.7%); position move +1.4%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~18% · IV residual ~-20% [inferred].
  convexity Γ·S = 3.17. exit TIMEOUT → realized -12%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HUM-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 4.83 · spread +0.0%
  greeks Δ0.180 Γ0.0066 Θ-0.184 · IV 0.466 · mid 4.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.88) · RSI 80
  headline "Deutsche Bank upgrades Humana stock rating on earnings outlook; raises price target to $441"
WHY
  underlying -0.1%/+1.3%/-0.8% (favorable peak +1.7%); position move -0.8%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-11% · IV residual ~12% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized -12%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE LLY-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 35.00 · spread +0.0%
  greeks Δ0.460 Γ0.0041 Θ-1.434 · IV 0.538 · mid 30.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 47
  headline "Eli Lilly's Foundayo Records Strong First-Week Prescriptions as FDA Targets GLP-1 Copycats"
WHY
  underlying -0.8%/-2.6%/-0.6% (favorable peak +0.3%); position move -0.6%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-9% · IV residual ~11% [inferred].
  convexity Γ·S = 3.82. exit TIMEOUT → realized -12%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE HPE-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 26 · V/OI n/a · spread +0.0%
  greeks Δ0.489 Γ0.0572 Θ-0.053 · IV 0.690 · mid 2.34
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 79
  headline "Wall Street Zen Upgrades HPE to Buy as Elliott Management Discloses $927M Stake"
WHY
  underlying +1.3%/-1.0%/+1.7% (favorable peak +2.7%); position move +1.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~13% · IV residual ~-18% [inferred].
  convexity Γ·S = 2.15. exit TIMEOUT → realized -12%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE APA-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 3.90 · spread +0.1%
  greeks Δ0.475 Γ0.0969 Θ-0.040 · IV 0.488 · mid 1.60
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 40
  headline "APA Corp Q1 2026 beats estimates, stock dips on future guidance concerns"
WHY
  underlying +3.2%/+4.3%/+4.0% (favorable peak +5.5%); position move +4.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~42% · IV residual ~-46% [inferred].
  convexity Γ·S = 3.45. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CI-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 14 · V/OI n/a · spread +0.0%
  greeks Δ0.429 Γ0.0156 Θ-0.343 · IV 0.456 · mid 6.06
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 54
  headline "The Cigna Group to Release First Quarter 2026 Financial Results on April 30"
WHY
  underlying +0.8%/+1.3%/+0.1% (favorable peak +3.4%); position move +0.1%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~2% · IV residual ~3% [inferred].
  convexity Γ·S = 4.30. exit TIMEOUT → realized -11%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CLSK-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 402.00 · spread +0.0%
  greeks Δ0.449 Γ0.1019 Θ-0.021 · IV 0.941 · mid 1.11
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 63
  headline "Needham Raises CleanSpark (CLSK) Price Target to $18 on Advanced Hyperscaler Discussions"
WHY
  underlying +4.6%/+13.1%/+9.0% (favorable peak +14.1%); position move +9.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~47% · IV residual ~-53% [inferred].
  convexity Γ·S = 1.31. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AXTI-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.546 Γ0.0104 Θ-0.325 · IV 1.998 · mid 12.50
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 61
  headline "AXT Inc. prices 8.56M shares at $64.25 in $550M underwritten public offering to fund AI capacity expansion"
WHY
  underlying +16.0%/+0.4%/+1.6% (favorable peak +20.2%); position move +1.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~5% · IV residual ~-8% [inferred].
  convexity Γ·S = 0.78. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HNGE-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 33 · V/OI 0.03 · spread +0.1%
  greeks Δ0.520 Γ0.0437 Θ-0.058 · IV 0.559 · mid 3.30
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 71
  headline "Hinge Health (HNGE) price target increased by 20.86% to 70.92 following blowout Q1 earnings and raised 2026…"
WHY
  underlying +0.4%/+0.8%/+0.4% (favorable peak +2.4%); position move +0.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~4% · IV residual ~-9% [inferred].
  convexity Γ·S = 2.38. exit TIMEOUT → realized -11%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FULT-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI 0.14 · spread +0.0%
  greeks Δ0.371 Γ0.2223 Θ-0.014 · IV 0.311 · mid 0.60
  overnight_score 1 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 62
  headline "Fulton Financial Corporation Announces Q1 2026 Earnings Release for April 22"
WHY
  underlying -0.1%/+1.0%/-2.0% (favorable peak +2.9%); position move -2.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-27% · IV residual ~23% [inferred].
  convexity Γ·S = 4.86. exit TIMEOUT → realized -11%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MS-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 14 · V/OI n/a · spread +0.0%
  greeks Δ0.904 Γ0.0202 Θ-0.051 · IV 0.221 · mid 12.16
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 70
  headline "Morgan Stanley's Q1 'Delivers A Home Run' With Strength In Investment Banking, Trading"
WHY
  underlying +0.8%/+1.8%/+1.1% (favorable peak +3.1%); position move +1.1%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~15% · IV residual ~-24% [inferred].
  convexity Γ·S = 3.79. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE INOD-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 10 · V/OI 3.75 · spread +0.0%
  greeks Δ0.477 Γ0.0351 Θ-0.213 · IV 1.447 · mid 3.66
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 57
  headline "Innodata schedules Q1 2026 earnings release for May 7"
WHY
  underlying -0.2%/+1.7%/-0.2% (favorable peak +4.9%); position move -0.2%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-1% · IV residual ~8% [inferred].
  convexity Γ·S = 1.60. exit TIMEOUT → realized -11%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE SNPS-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.291 Γ0.0056 Θ-0.309 · IV 0.442 · mid 9.79
  overnight_score 4 · flow DIRECTIONAL · catalyst Regulatory (0.90) · RSI 61
  headline "Synopsys Receives Final Regulatory Clearance for $35 Billion Ansys Acquisition; NASA Taps Firm for Artemis …"
WHY
  underlying +1.9%/+4.5%/+6.0% (favorable peak +8.9%); position move +6.0%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~79% · IV residual ~-80% [inferred].
  convexity Γ·S = 2.49. exit TIMEOUT → realized -11%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE IREN-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.410 Γ0.0248 Θ-0.090 · IV 1.080 · mid 3.05
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.90) · RSI 64
  headline "IREN Partners with NVIDIA and Reports Rumored $9.7B Microsoft AI Cloud Contract"
WHY
  underlying +0.9%/+2.1%/-5.3% (favorable peak +4.8%); position move -5.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-34% · IV residual ~32% [inferred].
  convexity Γ·S = 1.18. exit TIMEOUT → realized -10%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NBIS-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.1%
  greeks Δ0.330 Γ0.0074 Θ-0.200 · IV 0.884 · mid 10.18
  overnight_score 8 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 73
  headline "Goldman Sachs raises Nebius price target to $205 on $27B Meta AI contract"
WHY
  underlying +4.8%/+7.9%/+7.0% (favorable peak +9.2%); position move +7.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~35% · IV residual ~-39% [inferred].
  convexity Γ·S = 1.15. exit TIMEOUT → realized -10%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AMGN-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 9.10 · spread +0.1%
  greeks Δ0.451 Γ0.0270 Θ-0.198 · IV 0.217 · mid 4.93
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.55) · RSI 50
  headline "Amgen Shares Climb as Shareholders Affirm Leadership and Strategy at Annual Meeting"
WHY
  underlying +0.6%/-0.4%/-0.4% (favorable peak +1.9%); position move -0.4%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-12% · IV residual ~15% [inferred].
  convexity Γ·S = 9.10. exit TIMEOUT → realized -10%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE XOM-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ0.085 Γ0.0094 Θ-0.028 · IV 0.314 · mid 0.75
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 47
  headline "Global Oil Prices Surge on U.S.-Iran Hostilities, Lifting XOM as Analysts Hike Targets"
WHY
  underlying -0.0%/+0.6%/+1.4% (favorable peak +1.6%); position move +1.4%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~23% · IV residual ~-22% [inferred].
  convexity Γ·S = 1.41. exit TIMEOUT → realized -10%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SEDG-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 26 · V/OI n/a · spread +0.0%
  greeks Δ0.387 Γ0.0197 Θ-0.144 · IV 1.178 · mid 4.90
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 66
  headline "SolarEdge Surges to Two-Year High on Tax Credit Rush and AI-Energy Speculation"
WHY
  underlying +14.2%/+18.2%/+18.1% (favorable peak +22.2%); position move +18.1%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~89% · IV residual ~-90% [inferred].
  convexity Γ·S = 1.22. exit TIMEOUT → realized -10%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE IONQ-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 35 · V/OI 7.00 · spread +0.0%
  greeks Δ0.294 Γ0.0199 Θ-0.087 · IV 0.941 · mid 3.11
  overnight_score 6 · flow DIRECTIONAL · catalyst Macro (0.90) · RSI 65
  headline "Trump Administration unveils $2 billion quantum computing grant program, lifting IonQ and sector peers"
WHY
  underlying +8.1%/+8.0%/+11.1% (favorable peak +13.4%); position move +11.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~62% · IV residual ~-63% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized -10%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GTLB-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.466 Γ0.0623 Θ-0.043 · IV 0.884 · mid 1.95
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.75) · RSI 59
  headline "GitLab (GTLB) Deepens Anthropic Integration to Power Duo Agents With Claude Models"
WHY
  underlying +1.5%/+6.4%/+2.1% (favorable peak +6.8%); position move +2.1%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~13% · IV residual ~-15% [inferred].
  convexity Γ·S = 1.56. exit TIMEOUT → realized -9%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BMNR-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 22.88 · spread +0.0%
  greeks Δ0.455 Γ0.0853 Θ-0.026 · IV 0.764 · mid 1.40
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 41
  headline "Bitmine Emerges As Ethereum Proxy With NYSE Uplisting And MAVAN Staking"
WHY
  underlying +1.1%/-2.6%/-1.0% (favorable peak +3.4%); position move -1.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-6% · IV residual ~3% [inferred].
  convexity Γ·S = 1.65. exit TIMEOUT → realized -9%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE LLY-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 44 · V/OI n/a · spread +0.0%
  greeks Δ0.418 Γ0.0034 Θ-0.539 · IV 0.334 · mid 33.20
  overnight_score 6 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 60
  headline "Eli Lilly Invests Another $4.5 Billion in U.S. Manufacturing as Weight-Loss Drugs Takeoff"
WHY
  underlying +2.4%/+1.5%/+1.5% (favorable peak +3.2%); position move +1.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~19% · IV residual ~-23% [inferred].
  convexity Γ·S = 3.38. exit TIMEOUT → realized -9%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AG-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ0.395 Γ0.0664 Θ-0.026 · IV 0.795 · mid 1.48
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.78) · RSI 45
  headline "First Majestic Silver Tracking Ahead Of Guidance Following Q1 Production Results"
WHY
  underlying +3.6%/+1.8%/+1.3% (favorable peak +4.6%); position move +1.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~7% · IV residual ~-11% [inferred].
  convexity Γ·S = 1.38. exit TIMEOUT → realized -9%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE DDOG-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI n/a · spread +0.0%
  greeks Δ0.451 Γ0.0161 Θ-0.205 · IV 0.732 · mid 6.80
  overnight_score 7 · flow HEDGING · catalyst Technical Breakout (0.85) · RSI 61
  headline "Datadog Stock Rockets 23% With 6-Day Winning Streak"
WHY
  underlying -0.3%/+1.8%/-1.4% (favorable peak +4.8%); position move -1.4%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-12% · IV residual ~13% [inferred].
  convexity Γ·S = 2.08. exit TIMEOUT → realized -9%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TRMD-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 21 · V/OI 10.00 · spread +0.0%
  greeks Δ0.000 Γn/a Θn/a · IV n/a · mid 2.20
  overnight_score 2 · flow DIRECTIONAL · catalyst Sector Rotation (0.70) · RSI 40
  headline "TORM plc (CPH:TRMD A) Is About To Go Ex-Dividend, And It Pays A 6.7% Yield"
WHY
  underlying -6.2%/-8.7%/-6.0% (favorable peak -3.3%); position move -6.0%.
  decomp [first-order]: theta drag ~n/a% of premium / 3d · delta capture ~-0% · IV residual ~n/a% [inferred].
  convexity Γ·S = n/a. exit TIMEOUT → realized -8%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE MTSI-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 31 · V/OI n/a · spread +0.1%
  greeks Δ0.496 Γ0.0083 Θ-0.320 · IV 0.625 · mid 16.75
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 65
  headline "MTSI Maintained by B of A Securities -- Price Target Raised to $305"
WHY
  underlying +0.1%/-0.9%/-0.8% (favorable peak +0.9%); position move -0.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~-7% · IV residual ~4% [inferred].
  convexity Γ·S = 2.18. exit TIMEOUT → realized -8%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CAMT-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI 0.05 · spread +0.0%
  greeks Δ0.334 Γ0.0108 Θ-0.373 · IV 0.871 · mid 6.50
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 53
  headline "Camtek Stock Slides After Record High Surge as Investors Lock in Profits"
WHY
  underlying +4.0%/+6.3%/+3.4% (favorable peak +8.9%); position move +3.4%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~31% · IV residual ~-22% [inferred].
  convexity Γ·S = 1.95. exit TIMEOUT → realized -8%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SHAK-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 50.80 · spread +0.0%
  greeks Δ0.286 Γ0.0205 Θ-0.096 · IV 0.570 · mid 3.19
  overnight_score 1 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 55
  headline "DA Davidson Reaffirms Buy Rating with $125 Target on Shake Shack (SHAK) Citing Operational Efficiencies"
WHY
  underlying +0.5%/+2.3%/-1.8% (favorable peak +3.7%); position move -1.8%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-16% · IV residual ~18% [inferred].
  convexity Γ·S = 2.06. exit TIMEOUT → realized -7%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UPS-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.454 Γ0.0339 Θ-0.062 · IV 0.358 · mid 3.85
  overnight_score 5 · flow DIRECTIONAL · catalyst Macro (0.65) · RSI 63
  headline "UPS To Release First-Quarter 2026 Results On Tuesday, April 28, 2026"
WHY
  underlying +1.3%/+2.0%/+1.2% (favorable peak +2.9%); position move +1.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~15% · IV residual ~-17% [inferred].
  convexity Γ·S = 3.56. exit TIMEOUT → realized -7%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AFL-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 15 · V/OI 3.43 · spread +0.1%
  greeks Δ0.434 Γ0.0649 Θ-0.078 · IV 0.255 · mid 2.21
  overnight_score 1 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 62
  headline "Aflac (AFL) to Release Q1 2026 Financial Results on April 29"
WHY
  underlying +0.3%/-0.1%/-0.1% (favorable peak +1.0%); position move -0.1%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-1% · IV residual ~5% [inferred].
  convexity Γ·S = 7.45. exit TIMEOUT → realized -7%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE HNGE-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 40 · V/OI 0.16 · spread +0.1%
  greeks Δ0.188 Γ0.0322 Θ-0.029 · IV 0.450 · mid 1.10
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 81
  headline "Hinge Health Reports Blockbuster Q1 Beat, Raises FY2026 Revenue Guidance to $798M-$804M"
WHY
  underlying -2.3%/-1.4%/-3.5% (favorable peak +0.9%); position move -3.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-33% · IV residual ~35% [inferred].
  convexity Γ·S = 1.80. exit TIMEOUT → realized -7%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZBRA-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 19.87 · spread +0.1%
  greeks Δ0.631 Γ0.0118 Θ-0.425 · IV 0.699 · mid 16.65
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.85) · RSI 53
  headline "Zebra Technologies Divests Robotics Division to Skild AI, Raises 2026 EPS Guidance to $18.00"
WHY
  underlying +0.4%/-1.1%/+0.9% (favorable peak +1.4%); position move +0.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~8% · IV residual ~-7% [inferred].
  convexity Γ·S = 2.68. exit TIMEOUT → realized -7%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MDB-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 5.90 · spread +0.0%
  greeks Δ0.462 Γ0.0058 Θ-0.406 · IV 0.847 · mid 21.14
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 52
  headline "MongoDB Shares Surge as Software Sector Rebound Eases 'SaaSpocalypse' Concerns"
WHY
  underlying +0.5%/+1.2%/+0.7% (favorable peak +3.6%); position move +0.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~4% · IV residual ~-5% [inferred].
  convexity Γ·S = 1.53. exit TIMEOUT → realized -7%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE NEM-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 17.00 · spread +0.0%
  greeks Δ0.351 Γ0.0211 Θ-0.098 · IV 0.477 · mid 3.63
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.95) · RSI 59
  headline "Newmont Jumps After Record Q1 Cash Flow and Expanded $6B Buyback Plan"
WHY
  underlying -3.8%/-8.9%/-10.8% (favorable peak -1.0%); position move -10.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-126% · IV residual ~128% [inferred].
  convexity Γ·S = 2.55. exit TIMEOUT → realized -7%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AVAV-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 28 · V/OI 13.50 · spread +0.1%
  greeks Δ0.553 Γ0.0116 Θ-0.252 · IV 0.761 · mid 13.00
  overnight_score 3 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 40
  headline "AeroVironment Expands AV_Halo Platform with INSTINCT and DETECT for Autonomous Edge Decision-Making"
WHY
  underlying -0.5%/+6.3%/+11.2% (favorable peak +14.4%); position move +11.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~78% · IV residual ~-79% [inferred].
  convexity Γ·S = 1.90. exit TIMEOUT → realized -7%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CLS-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 26 · V/OI n/a · spread +0.0%
  greeks Δ0.468 Γ0.0054 Θ-0.568 · IV 0.754 · mid 20.07
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 50
  headline "Celestica Leads Newcomers To Best Growth Stock Lists Following Goldman Sachs Conviction List Inclusion"
WHY
  underlying +0.9%/-2.6%/-4.5% (favorable peak +3.7%); position move -4.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-38% · IV residual ~40% [inferred].
  convexity Γ·S = 1.98. exit TIMEOUT → realized -7%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE INTU-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 2.53 · spread +0.0%
  greeks Δ0.391 Γ0.0080 Θ-0.579 · IV 0.573 · mid 15.00
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.75) · RSI 48
  headline "Intuit Completes FedNow Certification to Enable Instant Payments for QuickBooks"
WHY
  underlying -1.3%/-3.0%/-0.3% (favorable peak +2.0%); position move -0.3%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~-3% · IV residual ~9% [inferred].
  convexity Γ·S = 3.20. exit TIMEOUT → realized -6%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE SIRI-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 21 · V/OI 3.70 · spread +0.0%
  greeks Δ0.429 Γ0.1685 Θ-0.021 · IV 0.331 · mid 0.86
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 71
  headline "Sirius XM Shares Surge 7.2% Following J.P. Morgan Conference Spotlight and Earnings Beat"
WHY
  underlying -0.3%/+2.2%/+2.3% (favorable peak +3.9%); position move +2.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~34% · IV residual ~-33% [inferred].
  convexity Γ·S = 4.88. exit TIMEOUT → realized -6%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GOOG-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI 5.00 · spread +0.0%
  greeks Δ0.315 Γ0.0091 Θ-0.177 · IV 0.340 · mid 7.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 70
  headline "Google confirmed a planned up to $40 billion commitment to AI startup Anthropic"
WHY
  underlying +1.8%/+1.5%/+1.5% (favorable peak +3.2%); position move +1.5%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~20% · IV residual ~-20% [inferred].
  convexity Γ·S = 3.12. exit TIMEOUT → realized -6%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SKYT-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ0.433 Γ0.2769 Θ-0.027 · IV 0.284 · mid 1.05
  overnight_score 3 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 55
  headline "IonQ to Acquire SkyWater Technology, Creating the Only Vertically Integrated Full-Stack Quantum Platform Co…"
WHY
  underlying +7.9%/+10.8%/+11.8% (favorable peak +13.4%); position move +11.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~141% · IV residual ~-140% [inferred].
  convexity Γ·S = 8.06. exit TIMEOUT → realized -6%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MDB-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 24 · V/OI 5.00 · spread +0.0%
  greeks Δ0.280 Γ0.0039 Θ-0.611 · IV 1.009 · mid 12.12
  overnight_score 6 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 74
  headline "Citi Opens Positive Catalyst Watch on MongoDB, Raising Price Target to $450 on AI-Driven Demand"
WHY
  underlying +1.4%/-0.3%/-3.8% (favorable peak +5.8%); position move -3.8%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~-29% · IV residual ~38% [inferred].
  convexity Γ·S = 1.30. exit TIMEOUT → realized -6%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE BA-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 9.50 · spread +0.1%
  greeks Δ0.736 Γ0.0130 Θ-0.128 · IV 0.358 · mid 18.09
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.65) · RSI 53
  headline "“Truss-Based Wing Configuration” Tests Send Boeing Stock Plummeting Amid Post-Earnings Volatility"
WHY
  underlying +2.2%/+1.5%/-1.3% (favorable peak +3.3%); position move -1.3%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-11% · IV residual ~8% [inferred].
  convexity Γ·S = 2.90. exit TIMEOUT → realized -6%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAVA-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 7.00 · spread +0.0%
  greeks Δ0.455 Γ0.0306 Θ-0.158 · IV 0.664 · mid 4.88
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 55
  headline "Benchmark Raises CAVA Price Target to $110 on Strong Traffic Trends"
WHY
  underlying +0.1%/+2.6%/-0.1% (favorable peak +5.7%); position move -0.1%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-1% · IV residual ~5% [inferred].
  convexity Γ·S = 2.79. exit TIMEOUT → realized -6%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE URBN-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 211.11 · spread +0.0%
  greeks Δ0.444 Γ0.0376 Θ-0.271 · IV 1.068 · mid 3.29
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 49
  headline "Urban Outfitters (URBN) Q1 2027 Earnings Report Scheduled for May 20, 2026"
WHY
  underlying +0.2%/+1.2%/+0.1% (favorable peak +1.9%); position move +0.1%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~1% · IV residual ~18% [inferred].
  convexity Γ·S = 2.58. exit TIMEOUT → realized -5%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AG-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 10.00 · spread +0.0%
  greeks Δ0.289 Γ0.0597 Θ-0.029 · IV 0.873 · mid 1.05
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 47
  headline "Short Supply Hits Silver for 6th Straight Year: 2 Winning Stocks to Own Now"
WHY
  underlying +0.1%/-6.6%/-2.7% (favorable peak +0.6%); position move -2.7%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-16% · IV residual ~19% [inferred].
  convexity Γ·S = 1.28. exit TIMEOUT → realized -5%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUM-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 23 · V/OI n/a · spread +0.0%
  greeks Δ0.368 Γ0.0101 Θ-0.310 · IV 0.503 · mid 3.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 87
  headline "Humana Jumps as CMS Rate Victory and OBBA Implementation Fuel Margin Recovery Thesis"
WHY
  underlying +3.2%/+2.0%/+3.3% (favorable peak +5.3%); position move +3.3%.
  decomp [first-order]: theta drag ~24% of premium / 3d · delta capture ~95% · IV residual ~-75% [inferred].
  convexity Γ·S = 2.99. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE APLD-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 38 · V/OI 18.57 · spread +0.0%
  greeks Δ0.347 Γ0.0327 Θ-0.055 · IV 1.029 · mid 2.29
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 60
  headline "Applied Digital Secures $7.5 Billion 15-Year Hyperscaler Lease for Delta Forge 1 AI Campus"
WHY
  underlying -4.6%/-2.9%/+1.7% (favorable peak +5.0%); position move +1.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~9% · IV residual ~-6% [inferred].
  convexity Γ·S = 1.10. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LUNR-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 2.20 · spread +0.0%
  greeks Δ0.472 Γ0.0568 Θ-0.132 · IV 1.196 · mid 2.31
  overnight_score 8 · flow DIRECTIONAL · catalyst Partnership (0.80) · RSI 60
  headline "Intuitive Machines Secures Prime Contracts to Operate Key NASA and KARI Lunar Imaging Instruments"
WHY
  underlying -3.4%/+0.2%/+1.9% (favorable peak +4.2%); position move +1.9%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~13% · IV residual ~-1% [inferred].
  convexity Γ·S = 1.91. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MU-2026-04-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 44 · V/OI n/a · spread +0.0%
  greeks Δ0.257 Γ0.0027 Θ-0.456 · IV 0.758 · mid 15.03
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.90) · RSI 66
  headline "Lynx Equity Skyrockets MU Price Target to $825 Citing Sold-Out 2026 HBM Capacity"
WHY
  underlying -2.0%/-1.8%/-2.3% (favorable peak +1.1%); position move -2.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-18% · IV residual ~22% [inferred].
  convexity Γ·S = 1.24. exit TIMEOUT → realized -5%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ZM-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 28 · V/OI 111.28 · spread +0.1%
  greeks Δ0.488 Γ0.0287 Θ-0.102 · IV 0.554 · mid 4.88
  overnight_score 5 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.20) · RSI 62
  headline "Mittleman Value Partners Highlights Zoom as AI Beneficiary Amidst Global Market Volatility"
WHY
  underlying +2.2%/+0.9%/+1.3% (favorable peak +3.6%); position move +1.3%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~11% · IV residual ~-10% [inferred].
  convexity Γ·S = 2.58. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE HUT-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 16 · V/OI n/a · spread +0.0%
  greeks Δ0.409 Γ0.0228 Θ-0.207 · IV 1.011 · mid 4.45
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 69
  headline "Hut 8 Signs Landmark $9.8 Billion, 15-Year AI Data Center Lease for Beacon Point Campus"
WHY
  underlying +35.3%/+25.7%/+22.3% (favorable peak +38.3%); position move +22.3%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~165% · IV residual ~-156% [inferred].
  convexity Γ·S = 1.84. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ULTA-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 13 · V/OI 146.00 · spread +0.0%
  greeks Δ0.498 Γ0.0066 Θ-0.921 · IV 0.613 · mid 22.88
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 48
  headline "Ulta Beauty Q1 2026 Earnings in 11 days from now on Tue Jun 2nd, after the market close"
WHY
  underlying +0.2%/-1.5%/+1.0% (favorable peak +2.3%); position move +1.0%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~11% · IV residual ~-4% [inferred].
  convexity Γ·S = 3.38. exit TIMEOUT → realized -5%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE WFC-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ0.353 Γ0.0642 Θ-0.050 · IV 0.292 · mid 1.40
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Miss (0.85) · RSI 46
  headline "Wells Fargo Gets Three Price Target Cuts in One Day: Is the ROTCE Recovery Story Falling Apart?"
WHY
  underlying +1.2%/+1.4%/+2.1% (favorable peak +2.9%); position move +2.1%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~42% · IV residual ~-36% [inferred].
  convexity Γ·S = 5.15. exit TIMEOUT → realized -5%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CLS-2026-05-11-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 4.33 · spread +0.0%
  greeks Δ0.392 Γ0.0061 Θ-0.718 · IV 0.759 · mid 16.30
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 52
  headline "Celestica Moves DS6000-Series 1.6TbE AI Networking Switches to Commercial Availability Following Blowout Gu…"
WHY
  underlying -1.8%/-2.2%/+0.2% (favorable peak +0.4%); position move +0.2%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~1% · IV residual ~7% [inferred].
  convexity Γ·S = 2.34. exit TIMEOUT → realized -4%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AKAM-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 4.00 · spread +0.0%
  greeks Δ0.491 Γ0.0210 Θ-0.175 · IV 0.536 · mid 6.70
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.88) · RSI 62
  headline "Akamai Prices Upsized $3.0B Convertible Offering to Fuel AI Cloud Expansion Post-Anthropic Deal"
WHY
  underlying +1.9%/+2.6%/+3.2% (favorable peak +4.6%); position move +3.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~34% · IV residual ~-31% [inferred].
  convexity Γ·S = 3.02. exit TIMEOUT → realized -4%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TGT-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 4.00 · spread +0.0%
  greeks Δ0.361 Γ0.0252 Θ-0.082 · IV 0.384 · mid 3.21
  overnight_score 5 · flow DIRECTIONAL · catalyst Partnership (0.72) · RSI 67
  headline "Target Partners With Pokémon For Exclusive 30th Anniversary Collection"
WHY
  underlying +1.8%/+3.3%/+2.2% (favorable peak +4.1%); position move +2.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~31% · IV residual ~-28% [inferred].
  convexity Γ·S = 3.22. exit TIMEOUT → realized -4%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AMAT-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.438 Γ0.0054 Θ-0.361 · IV 0.548 · mid 21.23
  overnight_score 4 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.10) · RSI 62
  headline "Applied Materials Hits All-Time Highs as AI Chip Infrastructure Demand Accelerates"
WHY
  underlying -1.3%/-0.7%/+1.6% (favorable peak +1.8%); position move +1.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~14% · IV residual ~-13% [inferred].
  convexity Γ·S = 2.16. exit TIMEOUT → realized -4%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CAMT-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 9 · V/OI 0.10 · spread +0.0%
  greeks Δ0.399 Γ0.0134 Θ-0.594 · IV 0.895 · mid 8.10
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 62
  headline "Camtek (CAMT) Surges 8% as AI Semiconductor Rally Intensifies Ahead of Q1 Earnings"
WHY
  underlying +2.7%/-2.1%/+4.2% (favorable peak +5.0%); position move +4.2%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~41% · IV residual ~-23% [inferred].
  convexity Γ·S = 2.64. exit TIMEOUT → realized -4%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TLN-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 3.50 · spread +0.0%
  greeks Δ0.405 Γ0.0063 Θ-0.418 · IV 0.582 · mid 23.20
  overnight_score 3 · flow DIRECTIONAL · catalyst Earnings Beat (0.80) · RSI 54
  headline "Talen Energy Reports Q1 Profitability Return, Beating Estimates Amid AI-Power Demand Surge"
WHY
  underlying -6.3%/-5.8%/-10.8% (favorable peak +1.2%); position move -10.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-70% · IV residual ~72% [inferred].
  convexity Γ·S = 2.35. exit TIMEOUT → realized -4%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ROKU-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI n/a · spread +0.0%
  greeks Δ0.421 Γ0.0207 Θ-0.111 · IV 0.484 · mid 6.08
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 72
  headline "Roku Maintains CTV Dominance with 36% North American Market Share Following Blockbuster Q1 Results"
WHY
  underlying +2.3%/+1.1%/+0.8% (favorable peak +3.7%); position move +0.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~7% · IV residual ~-5% [inferred].
  convexity Γ·S = 2.62. exit TIMEOUT → realized -4%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CAT-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 23 · V/OI 3.12 · spread +0.0%
  greeks Δ0.266 Γ0.0039 Θ-0.607 · IV 0.363 · mid 10.35
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.75) · RSI 67
  headline "Top Caterpillar Executive Executes Massive Stock Sale That Turns Heads on Wall Street"
WHY
  underlying -1.1%/+0.9%/-2.6% (favorable peak +1.2%); position move -2.6%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-61% · IV residual ~75% [inferred].
  convexity Γ·S = 3.59. exit TIMEOUT → realized -4%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HUBB-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 2.09 · spread +0.0%
  greeks Δ0.602 Γ0.0067 Θ-0.285 · IV 0.351 · mid 79.47
  overnight_score 2 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 38
  headline "Hubbell to Acquire NSI Industries for $3 Billion to Scale Electrical and Data Center Portfolios"
WHY
  underlying -0.1%/-0.6%/-1.4% (favorable peak +1.5%); position move -1.4%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-5% · IV residual ~3% [inferred].
  convexity Γ·S = 3.28. exit TIMEOUT → realized -4%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE VLO-2026-05-01-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 5.00 · spread +0.0%
  greeks Δ0.497 Γ0.0116 Θ-0.172 · IV 0.417 · mid 11.90
  overnight_score 4 · flow DIRECTIONAL · catalyst Macro (0.85) · RSI 57
  headline "Valero Shares Slip Despite Blowout Q1 Earnings as Oil Prices Retreat from $100"
WHY
  underlying +1.9%/+2.7%/-4.1% (favorable peak +3.5%); position move -4.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-43% · IV residual ~44% [inferred].
  convexity Γ·S = 2.86. exit TIMEOUT → realized -3%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LYFT-2026-04-28-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 22.08 · spread +0.0%
  greeks Δ0.392 Γ0.1327 Θ-0.019 · IV 0.710 · mid 0.86
  overnight_score 4 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.65) · RSI 52
  headline "LYFT Stock Falls As Wall Street Flags Uber Competition Concerns Ahead of Q1 Earnings"
WHY
  underlying +0.8%/-0.5%/+1.4% (favorable peak +1.9%); position move +1.4%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~9% · IV residual ~-6% [inferred].
  convexity Γ·S = 1.89. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ETN-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 34 · V/OI 45.00 · spread +0.0%
  greeks Δ0.534 Γ0.0086 Θ-0.285 · IV 0.391 · mid 20.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 47
  headline "Eaton Shares Bounce as AI Power Demand and Massive Backlog Offset Isolated Analyst Caution"
WHY
  underlying +3.0%/+3.8%/+2.7% (favorable peak +4.7%); position move +2.7%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~28% · IV residual ~-26% [inferred].
  convexity Γ·S = 3.37. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ULTA-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 65.00 · spread +0.0%
  greeks Δ0.407 Γ0.0100 Θ-0.395 · IV 0.299 · mid 9.25
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 54
  headline "Jefferies upgrades Ulta Beauty stock rating on makeup momentum"
WHY
  underlying +3.4%/+3.0%/+1.9% (favorable peak +4.6%); position move +1.9%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~46% · IV residual ~-37% [inferred].
  convexity Γ·S = 5.51. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BIIB-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 13 · V/OI n/a · spread +0.0%
  greeks Δ0.749 Γ0.0289 Θ-0.143 · IV 0.294 · mid 7.45
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.80) · RSI 59
  headline "Biogen Stock Gains Despite Extended FDA Review For Alzheimer's Therapy"
WHY
  underlying +2.3%/+3.1%/+5.7% (favorable peak +6.5%); position move +5.7%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~111% · IV residual ~-108% [inferred].
  convexity Γ·S = 5.59. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CIFR-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 35 · V/OI 10.00 · spread +0.0%
  greeks Δ0.595 Γ0.0458 Θ-0.048 · IV 1.097 · mid 2.86
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 69
  headline "Cipher Mining stock hits all-time high of 25.55 USD"
WHY
  underlying -2.3%/-6.0%/-4.6% (favorable peak -0.1%); position move -4.6%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-24% · IV residual ~26% [inferred].
  convexity Γ·S = 1.15. exit TIMEOUT → realized -3%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HXL-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 105.26 · spread +0.0%
  greeks Δ0.822 Γ0.0400 Θ-0.059 · IV 0.348 · mid 6.82
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 59
  headline "Hexcel Reports Strong Q1 2026 Results with 34% EPS Beat on Robust Aerospace Demand"
WHY
  underlying +3.7%/+1.9%/+0.2% (favorable peak +4.2%); position move +0.2%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~2% · IV residual ~-2% [inferred].
  convexity Γ·S = 3.62. exit TIMEOUT → realized -3%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ADI-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.406 Γ0.0074 Θ-0.351 · IV 0.456 · mid 13.87
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 70
  headline "Analog Devices price target raised to $415 from $370 at Goldman Sachs"
WHY
  underlying +2.7%/+0.9%/+2.9% (favorable peak +3.5%); position move +2.9%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~34% · IV residual ~-29% [inferred].
  convexity Γ·S = 2.99. exit TIMEOUT → realized -3%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE WSO-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.226 Γ0.0074 Θ-0.209 · IV 0.344 · mid 4.32
  overnight_score 3 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 64
  headline "Watsco To Go Ex-Dividend On April 16th, 2026 With 3.3 USD Dividend Per Share"
WHY
  underlying +1.4%/+3.4%/+5.4% (favorable peak +5.7%); position move +5.4%.
  decomp [first-order]: theta drag ~15% of premium / 3d · delta capture ~118% · IV residual ~-106% [inferred].
  convexity Γ·S = 3.10. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE FRO-2026-04-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 30 · V/OI n/a · spread +0.1%
  greeks Δ0.389 Γ0.0740 Θ-0.033 · IV 0.533 · mid 1.49
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.75) · RSI 50
  headline "U.S. stocks rally and crude oil prices ease as hopes climb for US-Iran peace talks"
WHY
  underlying +3.9%/+2.9%/+8.7% (favorable peak +11.7%); position move +8.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~77% · IV residual ~-73% [inferred].
  convexity Γ·S = 2.53. exit TRAIL → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE RBC-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.473 Γ0.0071 Θ-0.420 · IV 0.353 · mid 29.40
  overnight_score 3 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 53
  headline "Canada's banking regulator warns major lenders about appraisal practices as condo prices crash"
WHY
  underlying +3.2%/+4.4%/+3.4% (favorable peak +5.8%); position move +3.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~32% · IV residual ~-30% [inferred].
  convexity Γ·S = 4.04. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CIEN-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 114.43 · spread +0.1%
  greeks Δ0.364 Γ0.0043 Θ-1.152 · IV 0.836 · mid 18.50
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 64
  headline "Ciena shares hit a new 52-week high on strong volume as analysts highlight 'optical super-cycle'"
WHY
  underlying +1.5%/+2.1%/+3.3% (favorable peak +6.5%); position move +3.3%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~34% · IV residual ~-17% [inferred].
  convexity Γ·S = 2.27. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE UAL-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.381 Γ0.0222 Θ-0.084 · IV 0.551 · mid 3.88
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Cut (0.80) · RSI 46
  headline "United Airlines Slashes 2026 Guidance on Fuel Shock Despite Q1 Earnings Beat and Labor Deal Ratification"
WHY
  underlying -0.3%/-4.0%/+5.6% (favorable peak +6.2%); position move +5.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~51% · IV residual ~-46% [inferred].
  convexity Γ·S = 2.06. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AXTI-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 3.33 · spread +0.0%
  greeks Δ0.492 Γ0.0093 Θ-0.247 · IV 1.864 · mid 12.17
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.92) · RSI 59
  headline "AXT Inc. (AXTI) Reports Q1 Beat, Guides for Q2 Profitability on Record AI Backlog"
WHY
  underlying +21.2%/+33.8%/+35.8% (favorable peak +39.2%); position move +35.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~114% · IV residual ~-110% [inferred].
  convexity Γ·S = 0.74. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SBAC-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 26 · V/OI 80.50 · spread +0.1%
  greeks Δ0.826 Γ0.0142 Θ-0.088 · IV 0.324 · mid 17.13
  overnight_score 1 · flow DIRECTIONAL · catalyst Guidance Raise (0.75) · RSI 45
  headline "SBA Communications Corporation to Speak at the JP Morgan 2026 Global Technology, Media and Communications C…"
WHY
  underlying -1.9%/-2.6%/-0.5% (favorable peak +0.5%); position move -0.5%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~-5% · IV residual ~4% [inferred].
  convexity Γ·S = 2.92. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE DLR-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI n/a · spread +0.0%
  greeks Δ0.165 Γ0.0264 Θ-0.110 · IV 0.277 · mid 4.86
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.85) · RSI 62
  headline "Digital Realty cut to Hold at HSBC as strong AFFO growth already priced in"
WHY
  underlying -0.9%/-0.9%/+2.3% (favorable peak +2.5%); position move +2.3%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~16% · IV residual ~-11% [inferred].
  convexity Γ·S = 5.19. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GD-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.294 Γ0.0172 Θ-0.118 · IV 0.203 · mid 3.19
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.72) · RSI 50
  headline "General Dynamics exhibits a positive outlook due to its improving fundamentals and growth in unspent budget…"
WHY
  underlying -0.9%/-1.0%/-1.3% (favorable peak +0.0%); position move -1.3%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-41% · IV residual ~50% [inferred].
  convexity Γ·S = 5.89. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE KLAC-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 14 · V/OI 2.50 · spread +0.0%
  greeks Δ0.796 Γ0.0013 Θ-2.222 · IV 0.618 · mid 202.65
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 54
  headline "KLA Corp (KLAC) Exceeds Q3 Expectations and Raises Guidance, but Shares Slide on Valuation Reset"
WHY
  underlying -1.4%/-2.1%/-1.0% (favorable peak +1.0%); position move -1.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-7% · IV residual ~8% [inferred].
  convexity Γ·S = 2.33. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE PRAX-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 14 · V/OI 1.25 · spread +0.1%
  greeks Δ0.456 Γ0.0063 Θ-0.860 · IV 0.988 · mid 22.21
  overnight_score 1 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 48
  headline "Praxis Precision Medicines Inc. (PRAX): Rare Triple-Catalyst Setup in Neurology"
WHY
  underlying +1.7%/+5.9%/+4.5% (favorable peak +8.2%); position move +4.5%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~30% · IV residual ~-20% [inferred].
  convexity Γ·S = 2.02. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE NNE-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 30 · V/OI 3.99 · spread +0.1%
  greeks Δ0.291 Γ0.0560 Θ-0.036 · IV 0.939 · mid 1.09
  overnight_score 2 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 58
  headline "NANO Nuclear Slides 10% After Explosive Rally on Super Micro Computer AI Partnership"
WHY
  underlying +27.7%/+17.3%/+20.6% (favorable peak +28.5%); position move +20.6%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~125% · IV residual ~-117% [inferred].
  convexity Γ·S = 1.27. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ACN-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 38 · V/OI 5.00 · spread +0.0%
  greeks Δ0.218 Γ0.0099 Θ-0.114 · IV 0.516 · mid 3.35
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 47
  headline "Accenture Federal Services and OpenAI enter strategic collaboration to advance U.S. federal AI adoption"
WHY
  underlying -0.4%/+0.9%/+0.2% (favorable peak +4.1%); position move +0.2%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~2% · IV residual ~6% [inferred].
  convexity Γ·S = 1.76. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BKNG-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 17 · V/OI n/a · spread +0.1%
  greeks Δ0.492 Γ0.0200 Θ-0.224 · IV 0.517 · mid 5.72
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 54
  headline "Booking Holdings (BKNG) Outpaces Stock Market Gains: What You Should Know - April 13, 2026"
WHY
  underlying +2.2%/+4.8%/+4.1% (favorable peak +6.2%); position move +4.1%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~63% · IV residual ~-53% [inferred].
  convexity Γ·S = 3.54. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ALB-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 15 · V/OI 29.00 · spread +0.0%
  greeks Δ0.394 Γ0.0131 Θ-0.376 · IV 0.712 · mid 6.22
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 56
  headline "Zacks Upgrades Albemarle to Strong Buy as Moody's Shifts Outlook to Stable on Lithium Recovery"
WHY
  underlying -4.9%/-10.2%/-12.5% (favorable peak -1.4%); position move -12.5%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~-160% · IV residual ~176% [inferred].
  convexity Γ·S = 2.63. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FIG-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.369 Γ0.0588 Θ-0.033 · IV 1.036 · mid 1.31
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 54
  headline "Figma (FIG) Consolidates Near All-Time Lows Ahead of May 14 Earnings as Institutions Accumulate"
WHY
  underlying -0.7%/+5.9%/+6.4% (favorable peak +10.7%); position move +6.4%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~35% · IV residual ~-29% [inferred].
  convexity Γ·S = 1.14. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE APO-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 21 · V/OI n/a · spread +0.0%
  greeks Δ0.536 Γ0.0308 Θ-0.124 · IV 0.399 · mid 5.05
  overnight_score 7 · flow DIRECTIONAL · catalyst Partnership (0.85) · RSI 68
  headline "Apollo and Blackstone in talks to provide $35 billion in financing to Broadcom for AI chip development"
WHY
  underlying -0.1%/-1.1%/-3.2% (favorable peak +0.4%); position move -3.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-46% · IV residual ~52% [inferred].
  convexity Γ·S = 4.18. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DOCN-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 37 · V/OI n/a · spread +0.0%
  greeks Δ0.635 Γ0.0088 Θ-0.224 · IV 0.877 · mid 13.22
  overnight_score 7 · flow DIRECTIONAL · catalyst Guidance Raise (0.95) · RSI 79
  headline "DigitalOcean Surges 40% as AI-Native Cloud Shift Drives Massive Guidance Raise and S&P Index Promotion"
WHY
  underlying +5.4%/-1.5%/+7.3% (favorable peak +7.9%); position move +7.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~54% · IV residual ~-51% [inferred].
  convexity Γ·S = 1.34. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CC-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 10.00 · spread +0.0%
  greeks Δ0.389 Γ0.1207 Θ-0.029 · IV 0.523 · mid 1.12
  overnight_score 1 · flow DIRECTIONAL · catalyst Technical Breakout (0.30) · RSI 53
  headline "The Chemours Company (CC) To Go Ex-Dividend On May 15th, 2026"
WHY
  underlying -7.0%/-7.7%/-12.5% (favorable peak -2.3%); position move -12.5%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-108% · IV residual ~114% [inferred].
  convexity Γ·S = 3.00. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SEDG-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 35 · V/OI 11.11 · spread +0.0%
  greeks Δ0.636 Γ0.0260 Θ-0.079 · IV 0.976 · mid 4.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Product Launch (0.85) · RSI 59
  headline "SolarEdge Shares Jump 10% on $55M Legal Settlement Progress and New Commercial Storage Launch"
WHY
  underlying -3.2%/+0.0%/-6.5% (favorable peak +3.4%); position move -6.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-41% · IV residual ~44% [inferred].
  convexity Γ·S = 1.23. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE EMR-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 31 · V/OI n/a · spread +0.0%
  greeks Δ0.456 Γ0.0255 Θ-0.101 · IV 0.392 · mid 5.00
  overnight_score 2 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.90) · RSI 43
  headline "Emerson Electric (EMR) to Release Quarterly Earnings on Tuesday, May 5; Analysts Expect $1.55 EPS"
WHY
  underlying +2.2%/+9.2%/+4.2% (favorable peak +10.3%); position move +4.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~51% · IV residual ~-47% [inferred].
  convexity Γ·S = 3.46. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE ON-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI 3.00 · spread +0.0%
  greeks Δ0.458 Γ0.0152 Θ-0.175 · IV 0.700 · mid 7.72
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 73
  headline "Bank of America Lifts onsemi (ON) Target to $138, Citing AI Data Center Power Surge and Cyclical Inflection"
WHY
  underlying -1.7%/-2.5%/-5.0% (favorable peak +1.6%); position move -5.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-38% · IV residual ~43% [inferred].
  convexity Γ·S = 1.93. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SATS-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 6.00 · spread +0.0%
  greeks Δ0.377 Γ0.0165 Θ-0.211 · IV 0.729 · mid 9.00
  overnight_score 5 · flow DIRECTIONAL · catalyst M&A (0.80) · RSI 50
  headline "EchoStar slides as traders digest SpaceX-linked catalyst and spectrum deal details"
WHY
  underlying -3.3%/-4.1%/-4.7% (favorable peak +2.4%); position move -4.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-25% · IV residual ~30% [inferred].
  convexity Γ·S = 2.12. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE USAR-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 8.00 · spread +0.1%
  greeks Δ0.597 Γ0.0587 Θ-0.032 · IV 0.991 · mid 2.80
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 67
  headline "USA Rare Earth Nears Definitive $1.6 Billion U.S. Government Funding Agreement"
WHY
  underlying +13.2%/+14.5%/+27.4% (favorable peak +30.1%); position move +27.4%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~116% · IV residual ~-115% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE COHR-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 36 · V/OI n/a · spread +0.0%
  greeks Δ0.295 Γ0.0033 Θ-0.508 · IV 0.946 · mid 17.83
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.80) · RSI 72
  headline "Coherent Corp. Announces Timing of FY2026 Third Quarter Earnings Release for May 6"
WHY
  underlying -3.6%/-4.1%/-8.3% (favorable peak +1.8%); position move -8.3%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-48% · IV residual ~54% [inferred].
  convexity Γ·S = 1.17. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SATS-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.458 Γ0.0124 Θ-0.160 · IV 0.693 · mid 10.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.90) · RSI 64
  headline "FCC Approves EchoStar's $40B Spectrum Sale; SATS Emerges as Top SpaceX IPO Proxy"
WHY
  underlying -0.6%/-0.5%/+3.3% (favorable peak +7.3%); position move +3.3%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~21% · IV residual ~-18% [inferred].
  convexity Γ·S = 1.69. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CAR-2026-04-10-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 20 · V/OI n/a · spread +0.0%
  greeks Δ0.671 Γ0.0031 Θ-1.054 · IV 1.644 · mid 48.03
  overnight_score 5 · flow DIRECTIONAL · catalyst Short Squeeze (0.95) · RSI 92
  headline "Avis Budget Group (CAR) Stock Surges Close to 200% in Single Month Amid Historic Short Squeeze Dynamics"
WHY
  underlying +23.7%/+37.2%/+31.9% (favorable peak +38.4%); position move +31.9%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~134% · IV residual ~-129% [inferred].
  convexity Γ·S = 0.92. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE COHR-2026-04-29-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI 2.88 · spread +0.1%
  greeks Δ0.409 Γ0.0050 Θ-0.546 · IV 0.892 · mid 21.45
  overnight_score 5 · flow DIRECTIONAL · catalyst Insider Activity (0.85) · RSI 52
  headline "COHERENT CORP. Passive Investment Disclosure (>5%) Filed April 29, 2026"
WHY
  underlying +4.8%/+8.1%/+8.2% (favorable peak +14.2%); position move +8.2%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~48% · IV residual ~-42% [inferred].
  convexity Γ·S = 1.51. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AXP-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 34 · V/OI 10.00 · spread +0.0%
  greeks Δ0.087 Γ0.0050 Θ-0.074 · IV 0.308 · mid 1.20
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.88) · RSI 65
  headline "American Express (AXP) Expected to Announce Q1 Earnings on Thursday; Analysts Maintain Overweight Ratings"
WHY
  underlying -0.5%/-0.6%/+0.4% (favorable peak +1.9%); position move +0.4%.
  decomp [first-order]: theta drag ~18% of premium / 3d · delta capture ~9% · IV residual ~8% [inferred].
  convexity Γ·S = 1.67. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CRML-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 1.67 · spread +0.0%
  greeks Δ0.350 Γ0.0864 Θ-0.045 · IV 1.398 · mid 0.82
  overnight_score 7 · flow DIRECTIONAL · catalyst M&A (0.90) · RSI 68
  headline "Critical Metals Secures 92.5% of Tanbreez Project and Announces $835M European Lithium Deal"
WHY
  underlying -17.9%/-21.2%/-11.9% (favorable peak -6.0%); position move -11.9%.
  decomp [first-order]: theta drag ~17% of premium / 3d · delta capture ~-73% · IV residual ~88% [inferred].
  convexity Γ·S = 1.25. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DDOG-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 13 · V/OI 5.29 · spread +0.0%
  greeks Δ0.338 Γ0.0162 Θ-0.306 · IV 0.900 · mid 4.75
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.80) · RSI 59
  headline "Datadog gets 90-day upside catalyst watch at Citi ahead of earnings and DASH conference"
WHY
  underlying +2.5%/+1.6%/+3.5% (favorable peak +5.0%); position move +3.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~32% · IV residual ~-15% [inferred].
  convexity Γ·S = 2.10. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GEL-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 26 · V/OI 0.00 · spread +0.0%
  greeks Δ0.723 Γ0.1453 Θ-0.014 · IV 0.529 · mid 1.45
  overnight_score 1 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 41
  headline "Genesis Energy (GEL) Reaffirms 2026 Growth Guidance as Technical Indicators Signal 25:1 Risk-Reward Setup"
WHY
  underlying -5.3%/-6.1%/-5.0% (favorable peak +0.5%); position move -5.0%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-40% · IV residual ~41% [inferred].
  convexity Γ·S = 2.35. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE HSY-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 10 · V/OI 12.33 · spread +0.0%
  greeks Δ0.054 Γ0.0093 Θ-0.061 · IV 0.364 · mid 0.15
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 50
  headline "S&P Global Ratings revises Hershey outlook to stable from negative on expected EBITDA expansion"
WHY
  underlying +0.6%/-0.5%/-0.7% (favorable peak +2.2%); position move -0.7%.
  decomp [first-order]: theta drag ~121% of premium / 3d · delta capture ~-49% · IV residual ~168% [inferred].
  convexity Γ·S = 1.78. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE IRM-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 29 · V/OI n/a · spread +0.1%
  greeks Δ0.290 Γ0.0264 Θ-0.076 · IV 0.388 · mid 2.77
  overnight_score 1 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 67
  headline "Wells Fargo Boosts Iron Mountain (IRM) Price Target to $135 Ahead of Q1 Earnings"
WHY
  underlying -0.9%/-1.0%/-3.8% (favorable peak +0.7%); position move -3.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~-47% · IV residual ~53% [inferred].
  convexity Γ·S = 3.09. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE LMND-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI 34.00 · spread +0.1%
  greeks Δ0.366 Γ0.0232 Θ-0.177 · IV 1.077 · mid 3.90
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 59
  headline "Lemonade Set to Report Q1 Earnings April 29 as Web Traffic Surges 43% and Loss Ratios Improve"
WHY
  underlying -3.8%/-3.2%/-3.7% (favorable peak +1.8%); position move -3.7%.
  decomp [first-order]: theta drag ~14% of premium / 3d · delta capture ~-24% · IV residual ~35% [inferred].
  convexity Γ·S = 1.59. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE NBIS-2026-04-23-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 28 · V/OI n/a · spread +0.0%
  greeks Δ0.294 Γ0.0079 Θ-0.273 · IV 0.994 · mid 7.72
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 67
  headline "Nebius Group Stock Takes Off on AI Deal Frenzy including $46 billion in contracts with Meta and Microsoft"
WHY
  underlying -6.3%/-7.7%/-13.7% (favorable peak +5.2%); position move -13.7%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~-82% · IV residual ~91% [inferred].
  convexity Γ·S = 1.24. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE OSCR-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 17 · V/OI n/a · spread +0.0%
  greeks Δ0.340 Γ0.0847 Θ-0.046 · IV 0.783 · mid 0.71
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 78
  headline "Oscar Health (OSCR) Notches 5-Year High on CMS Updates"
WHY
  underlying -3.1%/-7.4%/-12.5% (favorable peak -0.8%); position move -12.5%.
  decomp [first-order]: theta drag ~19% of premium / 3d · delta capture ~-151% · IV residual ~169% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE PVLA-2026-05-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 33 · V/OI n/a · spread +0.0%
  greeks Δ0.365 Γ0.0170 Θ-0.129 · IV 0.642 · mid 5.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Product Launch (0.80) · RSI 41
  headline "Palvella Therapeutics Announces New Data from the Phase 2 TOIVA Trial of QTORIN™ Rapamycin in Cutaneous Ven…"
WHY
  underlying -8.0%/-4.4%/+1.1% (favorable peak +1.1%); position move +1.1%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~9% · IV residual ~-3% [inferred].
  convexity Γ·S = 1.94. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TEM-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI n/a · spread +0.1%
  greeks Δ0.324 Γ0.0308 Θ-0.087 · IV 0.791 · mid 2.07
  overnight_score 4 · flow DIRECTIONAL · catalyst Partnership (0.80) · RSI 63
  headline "Tempus AI Scales Multimodal AI Partnership with Bristol Myers Squibb; Presents 31 Abstracts at AACR 2026"
WHY
  underlying -2.9%/-2.2%/-9.4% (favorable peak +1.9%); position move -9.4%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~-83% · IV residual ~94% [inferred].
  convexity Γ·S = 1.75. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CRDO-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 29 · V/OI n/a · spread +0.0%
  greeks Δ0.272 Γ0.0058 Θ-0.332 · IV 1.030 · mid 4.46
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.30) · RSI 62
  headline "Credo Technology Group Shares Down 5% Amid Broader Tech Pullback"
WHY
  underlying -5.0%/-4.9%/+6.0% (favorable peak +6.2%); position move +6.0%.
  decomp [first-order]: theta drag ~22% of premium / 3d · delta capture ~73% · IV residual ~-52% [inferred].
  convexity Γ·S = 1.16. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SHOP-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.499 Γ0.0143 Θ-0.152 · IV 0.638 · mid 8.82
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.80) · RSI 64
  headline "CIBC Provides Q1 Preview for Shopify; Says Strong Quarter And 2026 Outlook Expected"
WHY
  underlying -3.0%/-2.4%/-8.1% (favorable peak +1.6%); position move -8.1%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-62% · IV residual ~65% [inferred].
  convexity Γ·S = 1.93. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DECK-2026-05-26-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 9 · V/OI 5.50 · spread +0.0%
  greeks Δ0.640 Γ0.0484 Θ-0.158 · IV 0.428 · mid 3.84
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 66
  headline "Deckers Outdoor (DECK) Stock Jumps After Record Sales, Earnings Beat, and $3.5B Buyback Authorization"
WHY
  underlying +2.6%/+2.6%/+2.2% (favorable peak +3.9%); position move +2.2%.
  decomp [first-order]: theta drag ~12% of premium / 3d · delta capture ~40% · IV residual ~-30% [inferred].
  convexity Γ·S = 5.40. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MDB-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 38 · V/OI 6.50 · spread +0.1%
  greeks Δ0.286 Γ0.0045 Θ-0.349 · IV 0.891 · mid 10.05
  overnight_score 4 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 53
  headline "Alger Management Defends MongoDB in Q1 Letter, Arguing Market Overreacted to Guidance Shortfall"
WHY
  underlying +0.8%/+0.2%/+10.9% (favorable peak +14.9%); position move +10.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~82% · IV residual ~-73% [inferred].
  convexity Γ·S = 1.19. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE SNPS-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.0%
  greeks Δ0.253 Γ0.0048 Θ-0.252 · IV 0.461 · mid 9.00
  overnight_score 2 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 52
  headline "Synopsys Secures Regulatory Approval for $35B Ansys Takeover, Launches Integrated AI Design Tools"
WHY
  underlying +0.2%/+5.0%/+5.6% (favorable peak +7.6%); position move +5.6%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~66% · IV residual ~-59% [inferred].
  convexity Γ·S = 1.99. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GEL-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 0.01 · spread +0.0%
  greeks Δ0.074 Γ0.0605 Θ-0.005 · IV 0.475 · mid 0.05
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 37
  headline "Genesis Energy, L.P. Reaffirms 2026 Guidance Amid Macro Energy Tailwinds"
WHY
  underlying -0.1%/+0.9%/+1.9% (favorable peak +2.0%); position move +1.9%.
  decomp [first-order]: theta drag ~29% of premium / 3d · delta capture ~45% · IV residual ~-18% [inferred].
  convexity Γ·S = 0.97. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE MAR-2026-05-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 34.40 · spread +0.0%
  greeks Δ0.140 Γ0.0091 Θ-0.132 · IV 0.263 · mid 1.90
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.70) · RSI 72
  headline "Marriott International (NASDAQ:MAR) Hits New 12-Month High on Analyst Upgrade"
WHY
  underlying -0.0%/-2.7%/-2.3% (favorable peak +0.7%); position move -2.3%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-65% · IV residual ~84% [inferred].
  convexity Γ·S = 3.51. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TEAM-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 20 · V/OI 8.77 · spread +0.0%
  greeks Δ0.530 Γ0.0251 Θ-0.160 · IV 1.005 · mid 7.85
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Downgrade (0.75) · RSI 50
  headline "Atlassian (TEAM) Reaches New 1-Year Low After Analysts Slash Price Targets Citing AI Risks"
WHY
  underlying +6.8%/+6.4%/+10.6% (favorable peak +13.5%); position move +10.6%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~48% · IV residual ~-44% [inferred].
  convexity Γ·S = 1.68. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TGT-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 36 · V/OI 35.00 · spread +0.0%
  greeks Δ0.308 Γ0.0226 Θ-0.074 · IV 0.378 · mid 3.10
  overnight_score 3 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 49
  headline "RBC Capital raises Target price target to $132, citing consumer turnaround momentum ahead of Q1 earnings."
WHY
  underlying -3.3%/-3.8%/-9.0% (favorable peak -0.3%); position move -9.0%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-117% · IV residual ~122% [inferred].
  convexity Γ·S = 2.95. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE TRTX-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 43 · V/OI 1.00 · spread +0.0%
  greeks Δ0.321 Γ0.4139 Θ-0.003 · IV 0.299 · mid 0.15
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 59
  headline "TPG RE Finance Trust (TRTX) and Sun Hung Kai Properties (SUHJY): Which Is the Better Value Option?"
WHY
  underlying +0.5%/-0.6%/+0.2% (favorable peak +1.3%); position move +0.2%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~4% · IV residual ~0% [inferred].
  convexity Γ·S = 3.54. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE ETN-2026-05-12-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.0% · DTE 16 · V/OI 4.58 · spread +0.0%
  greeks Δ0.721 Γ0.0104 Θ-0.342 · IV 0.376 · mid 20.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 49
  headline "KeyBanc Raises PT on Eaton Corporation (ETN) to $480 Following AI Data Center Momentum"
WHY
  underlying +1.3%/+1.6%/-0.5% (favorable peak +2.1%); position move -0.5%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-8% · IV residual ~11% [inferred].
  convexity Γ·S = 4.18. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE HRI-2026-05-04-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 44 · V/OI 1.62 · spread +0.0%
  greeks Δ0.576 Γ0.0218 Θ-0.082 · IV 0.407 · mid 12.40
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.75) · RSI 56
  headline "Herc Holdings Shares Sink as Leverage Concerns Overshadow Q1 Earnings Beat"
WHY
  underlying +5.6%/+9.8%/+6.4% (favorable peak +11.7%); position move +6.4%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~37% · IV residual ~-37% [inferred].
  convexity Γ·S = 2.70. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE URI-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI n/a · spread +0.0%
  greeks Δ0.480 Γ0.0040 Θ-0.601 · IV 0.405 · mid 38.55
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 64
  headline "United Rentals (URI) Earnings Expected to Grow: What to Know Ahead of Next Week's Release"
WHY
  underlying +2.0%/+1.3%/+0.8% (favorable peak +4.9%); position move +0.8%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~8% · IV residual ~-6% [inferred].
  convexity Γ·S = 3.21. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MRNA-2026-04-24-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 34 · V/OI 5.00 · spread +0.0%
  greeks Δ0.473 Γ0.0349 Θ-0.068 · IV 0.734 · mid 5.95
  overnight_score 5 · flow DIRECTIONAL · catalyst Regulatory (0.75) · RSI 46
  headline "CureVac sues Moderna over mRNA patents as analysts warn of negative earnings ahead of May 1 report"
WHY
  underlying -4.0%/-7.1%/-9.9% (favorable peak +1.2%); position move -9.9%.
  decomp [first-order]: theta drag ~3% of premium / 3d · delta capture ~-40% · IV residual ~41% [inferred].
  convexity Γ·S = 1.77. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE RACE-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.300 Γ0.0080 Θ-0.189 · IV 0.348 · mid 8.50
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.85) · RSI 66
  headline "Ferrari AGM Approves €3.615 Dividend and Renewed 10% Share Buyback Authorization"
WHY
  underlying -0.0%/-3.8%/-3.8% (favorable peak +0.0%); position move -3.8%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-50% · IV residual ~55% [inferred].
  convexity Γ·S = 2.97. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE AAPL-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.008 Γ0.0009 Θ-0.011 · IV 0.346 · mid 0.07
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 62
  headline "Apple Stock Rises 3% as Bank of America Lifts Price Target to $325 on Services Strength"
WHY
  underlying -1.1%/+1.4%/+2.5% (favorable peak +2.9%); position move +2.5%.
  decomp [first-order]: theta drag ~47% of premium / 3d · delta capture ~74% · IV residual ~-29% [inferred].
  convexity Γ·S = 0.24. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE PSA-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 28 · V/OI 0.14 · spread +0.0%
  greeks Δ0.036 Γ0.0040 Θ-0.026 · IV 0.230 · mid 0.32
  overnight_score 7 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.75) · RSI 52
  headline "Scotiabank Forecasts Strong Price Appreciation for Public Storage (NYSE:PSA) Stock with New $340.00 Price T…"
WHY
  underlying +0.7%/+0.8%/+0.5% (favorable peak +1.9%); position move +0.5%.
  decomp [first-order]: theta drag ~25% of premium / 3d · delta capture ~18% · IV residual ~5% [inferred].
  convexity Γ·S = 1.22. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE WSBF-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 1.00 · spread +0.0%
  greeks Δ0.648 Γ0.1911 Θ-0.008 · IV 0.314 · mid 1.20
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 61
  headline "Waterstone Financial Expands Share Buyback Program by 2 Million Shares (11.9% of Float)"
WHY
  underlying +1.4%/+2.4%/+3.3% (favorable peak +3.5%); position move +3.3%.
  decomp [first-order]: theta drag ~2% of premium / 3d · delta capture ~32% · IV residual ~-32% [inferred].
  convexity Γ·S = 3.46. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE CIEN-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.369 Γ0.0037 Θ-0.885 · IV 0.838 · mid 24.90
  overnight_score 5 · flow DIRECTIONAL · catalyst Sector Rotation (0.65) · RSI 64
  headline "BofA and JPMorgan Raise CIEN Targets to $550 Citing AI Infrastructure Super-Cycle"
WHY
  underlying +3.4%/+4.4%/+1.5% (favorable peak +5.8%); position move +1.5%.
  decomp [first-order]: theta drag ~11% of premium / 3d · delta capture ~11% · IV residual ~-2% [inferred].
  convexity Γ·S = 1.83. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TWLO-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.473 Γ0.0141 Θ-0.142 · IV 0.598 · mid 9.41
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 66
  headline "Exane Asset Management Buys New Holdings in Twilio Inc. $TWLO"
WHY
  underlying +3.9%/+3.7%/+7.4% (favorable peak +10.4%); position move +7.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~52% · IV residual ~-49% [inferred].
  convexity Γ·S = 1.97. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE LLY-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI n/a · spread +0.0%
  greeks Δ0.489 Γ0.0035 Θ-0.593 · IV 0.329 · mid 39.98
  overnight_score 7 · flow DIRECTIONAL · catalyst Product Launch (0.95) · RSI 65
  headline "Eli Lilly's Next-Gen Obesity Drug Retatrutide Delivers 28% Weight Loss in Pivotal Phase 3 Trial"
WHY
  underlying +2.2%/+2.2%/+4.0% (favorable peak +4.9%); position move +4.0%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~50% · IV residual ~-48% [inferred].
  convexity Γ·S = 3.62. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE COP-2026-05-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 6.00 · spread +0.0%
  greeks Δ0.494 Γ0.0371 Θ-0.097 · IV 0.356 · mid 4.10
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.75) · RSI 52
  headline "ConocoPhillips Surges as 13F Filings Confirm Institutional Pivot to Energy Value"
WHY
  underlying -1.5%/-1.6%/-4.7% (favorable peak +1.7%); position move -4.7%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-70% · IV residual ~75% [inferred].
  convexity Γ·S = 4.54. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE URBN-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 2.60 · spread +0.1%
  greeks Δ0.271 Γ0.0288 Θ-0.081 · IV 0.620 · mid 2.47
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.40) · RSI 58
  headline "Urban Outfitters (NASDAQ:URBN) Stock Price Passes Above 200 Day Moving Average - Here's What Happened"
WHY
  underlying -3.5%/-5.0%/-2.8% (favorable peak +0.7%); position move -2.8%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-22% · IV residual ~30% [inferred].
  convexity Γ·S = 2.08. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CR-2026-05-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 27 · V/OI 11.46 · spread +0.1%
  greeks Δ0.853 Γ0.0135 Θ-0.081 · IV 0.352 · mid 29.75
  overnight_score 4 · flow DIRECTIONAL · catalyst Guidance Raise (0.75) · RSI 47
  headline "Crane Co stock (US2243271037): solid Q1 growth and higher guidance draw investor attention"
WHY
  underlying +2.5%/+3.6%/+2.0% (favorable peak +5.0%); position move +2.0%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~10% · IV residual ~-11% [inferred].
  convexity Γ·S = 2.36. exit TIMEOUT → realized -2%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE EOG-2026-05-06-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 8 · V/OI 620.00 · spread +0.0%
  greeks Δ0.810 Γ0.0292 Θ-0.143 · IV 0.446 · mid 8.66
  overnight_score 4 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 40
  headline "EOG Resources Beats Q1 Estimates on Strong Output; Analysts Raise Price Targets Post-Earnings"
WHY
  underlying -2.8%/-3.5%/-1.0% (favorable peak -0.9%); position move -1.0%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-13% · IV residual ~16% [inferred].
  convexity Γ·S = 3.93. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE SPGI-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness -0.1% · DTE 38 · V/OI n/a · spread +0.0%
  greeks Δ0.899 Γ0.0051 Θ-0.102 · IV 0.253 · mid 46.91
  overnight_score 5 · flow DIRECTIONAL · catalyst M&A (0.85) · RSI 41
  headline "Mobility Global raises $2B in private debt ahead S&P spin-off"
WHY
  underlying -1.7%/-0.1%/-0.4% (favorable peak +1.2%); position move -0.4%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-3% · IV residual ~2% [inferred].
  convexity Γ·S = 2.14. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE AKAM-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI n/a · spread +0.1%
  greeks Δ0.484 Γ0.0215 Θ-0.168 · IV 0.776 · mid 7.04
  overnight_score 2 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 43
  headline "Akamai (AKAM) Expansion Plans | Akamai posts 2.8% EPS beat on solid edge AI demand"
WHY
  underlying -1.0%/-1.9%/-1.2% (favorable peak +0.4%); position move -1.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~-8% · IV residual ~13% [inferred].
  convexity Γ·S = 2.09. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAR-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.627 Γ0.0007 Θ-3.323 · IV 2.366 · mid 204.40
  overnight_score 7 · flow HEDGING · catalyst Short Squeeze (0.95) · RSI 96
  headline "Avis Budget Group (CAR) Stock Surges 23% in Wild Short Squeeze Frenzy"
WHY
  underlying -37.8%/-67.9%/-71.4% (favorable peak +18.7%); position move -71.4%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-156% · IV residual ~159% [inferred].
  convexity Γ·S = 0.52. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE FTAI-2026-05-14-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 7 · V/OI 3.80 · spread +0.0%
  greeks Δ0.339 Γ0.0137 Θ-0.642 · IV 0.710 · mid 8.98
  overnight_score 2 · flow DIRECTIONAL · catalyst Earnings Miss (0.75) · RSI 52
  headline "FTAI Aviation Reaffirms $1.6B EBITDA Outlook as Revenue Surges 44%, Overcoming EPS Miss"
WHY
  underlying -8.1%/-10.9%/-13.7% (favorable peak -1.0%); position move -13.7%.
  decomp [first-order]: theta drag ~21% of premium / 3d · delta capture ~-134% · IV residual ~153% [inferred].
  convexity Γ·S = 3.54. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ALLY-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 7 · V/OI 0.03 · spread +0.0%
  greeks Δ0.469 Γ0.1958 Θ-0.052 · IV 0.319 · mid 0.56
  overnight_score 1 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 58
  headline "Goldman Sachs Raises Ally Financial Price Target to $56, Citing Improving Net Interest Margins"
WHY
  underlying +1.0%/-2.4%/-2.2% (favorable peak +1.6%); position move -2.2%.
  decomp [first-order]: theta drag ~28% of premium / 3d · delta capture ~-80% · IV residual ~106% [inferred].
  convexity Γ·S = 8.58. exit TRAIL → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE COST-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 42 · V/OI n/a · spread +0.1%
  greeks Δ0.307 Γ0.0043 Θ-0.361 · IV 0.235 · mid 14.62
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.75) · RSI 57
  headline "Costco To Go Ex-Dividend On May 1st, 2026 With 1.47 USD Dividend Per Share"
WHY
  underlying -0.3%/-0.2%/+0.2% (favorable peak +1.7%); position move +0.2%.
  decomp [first-order]: theta drag ~7% of premium / 3d · delta capture ~4% · IV residual ~2% [inferred].
  convexity Γ·S = 4.39. exit TIMEOUT → realized -2%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE FTNT-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 24 · V/OI 5.00 · spread +0.0%
  greeks Δ0.332 Γ0.0311 Θ-0.089 · IV 0.526 · mid 3.11
  overnight_score 6 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 58
  headline "Fortinet (FTNT) Shares Climb as Investors Look Past Vulnerability Headlines Ahead of Q1 Results"
WHY
  underlying +0.1%/+0.5%/-1.6% (favorable peak +2.1%); position move -1.6%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~-15% · IV residual ~22% [inferred].
  convexity Γ·S = 2.66. exit TIMEOUT → realized -2%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE UNH-2026-04-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 45 · V/OI n/a · spread +0.1%
  greeks Δ0.437 Γ0.0134 Θ-0.138 · IV 0.267 · mid 9.87
  overnight_score 6 · flow DIRECTIONAL · catalyst Regulatory (0.85) · RSI 68
  headline "UnitedHealth Group (UNH) Trading 2.9% Higher as CMS Medicare Rate Boost Ignites Investor Optimism"
WHY
  underlying +0.4%/+0.3%/+1.1% (favorable peak +2.1%); position move +1.1%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~15% · IV residual ~-12% [inferred].
  convexity Γ·S = 4.21. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE COHR-2026-04-30-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 21 · V/OI 5.00 · spread +0.0%
  greeks Δ0.340 Γ0.0045 Θ-0.698 · IV 1.053 · mid 16.00
  overnight_score 5 · flow DIRECTIONAL · catalyst Analyst Upgrade (0.85) · RSI 57
  headline "Rothschild Redburn Initiates Coherent (COHR) with Buy Rating and $455 Price Target Ahead of Earnings"
WHY
  underlying +3.1%/+3.2%/+5.0% (favorable peak +8.9%); position move +5.0%.
  decomp [first-order]: theta drag ~13% of premium / 3d · delta capture ~34% · IV residual ~-22% [inferred].
  convexity Γ·S = 1.44. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AMAT-2026-05-07-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 35 · V/OI 6.00 · spread +0.0%
  greeks Δ0.306 Γ0.0047 Θ-0.382 · IV 0.587 · mid 18.04
  overnight_score 6 · flow DIRECTIONAL · catalyst No Clear Catalyst (0.30) · RSI 65
  headline "Applied Materials (AMAT) Stock Price Down 4.1% - Here's What Happened"
WHY
  underlying +6.0%/+8.0%/+5.0% (favorable peak +9.2%); position move +5.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~35% · IV residual ~-30% [inferred].
  convexity Γ·S = 1.92. exit TRAIL → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GS-2026-04-17-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 41 · V/OI 8.50 · spread +0.1%
  greeks Δ0.384 Γ0.0044 Θ-0.426 · IV 0.282 · mid 22.34
  overnight_score 6 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 66
  headline "Goldman Sachs Seeks SEC Approval for New Bitcoin ETF Following Blockbuster Q1 Earnings"
WHY
  underlying +1.7%/+0.1%/+1.0% (favorable peak +2.8%); position move +1.0%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~15% · IV residual ~-10% [inferred].
  convexity Γ·S = 4.08. exit TIMEOUT → realized -1%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE MOD-2026-05-08-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 40 · V/OI 11.69 · spread +0.1%
  greeks Δ0.484 Γ0.0052 Θ-0.389 · IV 0.837 · mid 26.60
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 64
  headline "Modine Promotes Art Laszlo to President of Newly Created Data Centers Segment"
WHY
  underlying +4.3%/+1.2%/+2.3% (favorable peak +5.1%); position move +2.3%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~11% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.43. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE BAC-2026-04-15-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 22 · V/OI n/a · spread +0.0%
  greeks Δ0.865 Γ0.0504 Θ-0.022 · IV 0.318 · mid 4.69
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 73
  headline "Bank of America (BAC) Exceeds Q1 Expectations on Trading and Deal Surge"
WHY
  underlying -1.5%/-0.8%/-0.7% (favorable peak +0.5%); position move -0.7%.
  decomp [first-order]: theta drag ~1% of premium / 3d · delta capture ~-7% · IV residual ~7% [inferred].
  convexity Γ·S = 2.74. exit TIMEOUT → realized -1%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE BE-2026-04-20-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 38 · V/OI 214.00 · spread +0.0%
  greeks Δ0.449 Γ0.0052 Θ-0.406 · IV 1.075 · mid 21.40
  overnight_score 6 · flow DIRECTIONAL · catalyst Partnership (0.95) · RSI 71
  headline "Oracle Expands Bloom Energy Deal to 2.8 GW to Power AI Cloud Infrastructure"
WHY
  underlying +1.2%/+5.3%/+8.8% (favorable peak +10.7%); position move +8.8%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~40% · IV residual ~-36% [inferred].
  convexity Γ·S = 1.14. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AFL-2026-04-21-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 16 · V/OI 4.00 · spread +0.1%
  greeks Δ0.732 Γ0.0526 Θ-0.065 · IV 0.251 · mid 4.17
  overnight_score 5 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 68
  headline "Aflac Incorporated to Release First Quarter Results and CFO Video Update on April 29, 2026"
WHY
  underlying -1.1%/-0.7%/-1.2% (favorable peak +0.0%); position move -1.2%.
  decomp [first-order]: theta drag ~5% of premium / 3d · delta capture ~-24% · IV residual ~28% [inferred].
  convexity Γ·S = 6.10. exit TIMEOUT → realized -1%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE CAT-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 29 · V/OI 6.00 · spread +0.0%
  greeks Δ0.479 Γ0.0039 Θ-0.723 · IV 0.447 · mid 35.20
  overnight_score 6 · flow DIRECTIONAL · catalyst Sector Rotation (0.85) · RSI 67
  headline "Wells Fargo Hikes Caterpillar Target to $960 as AI Data Center Power Needs Drive Industrial Supercycle"
WHY
  underlying +3.3%/+2.7%/+2.5% (favorable peak +4.5%); position move +2.5%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~27% · IV residual ~-22% [inferred].
  convexity Γ·S = 3.13. exit TIMEOUT → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE QURE-2026-04-16-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness n/a · DTE 28 · V/OI n/a · spread +0.1%
  greeks Δ0.413 Γ0.0599 Θ-0.046 · IV 1.379 · mid 1.73
  overnight_score 1 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 50
  headline "uniQure (QURE) Securities Fraud Class Action Lead Plaintiff Deadline Passes as Analysts Maintain $42 Consen…"
WHY
  underlying +4.6%/+7.3%/+3.8% (favorable peak +14.4%); position move +3.8%.
  decomp [first-order]: theta drag ~8% of premium / 3d · delta capture ~15% · IV residual ~-8% [inferred].
  convexity Γ·S = 1.01. exit TRAIL → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE TGT-2026-05-18-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.1% · DTE 30 · V/OI n/a · spread +0.0%
  greeks Δ0.335 Γ0.0239 Θ-0.090 · IV 0.428 · mid 3.10
  overnight_score 7 · flow DIRECTIONAL · catalyst Earnings Beat (0.85) · RSI 55
  headline "Target Q1 2026 Earnings: EPS and Revenues Exceed Analyst Expectations Amid Turnaround Momentum"
WHY
  underlying +3.1%/-0.9%/+2.2% (favorable peak +3.3%); position move +2.2%.
  decomp [first-order]: theta drag ~9% of premium / 3d · delta capture ~30% · IV residual ~-22% [inferred].
  convexity Γ·S = 2.95. exit TRAIL → realized -1%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE AAOI-2026-05-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.2% · DTE 34 · V/OI 2.75 · spread +0.1%
  greeks Δ0.405 Γ0.0054 Θ-0.416 · IV 1.320 · mid 13.05
  overnight_score 8 · flow DIRECTIONAL · catalyst Technical Breakout (0.70) · RSI 55
  headline "Applied Optoelectronics Stabilizes as Institutional Flow Targets Recovery to $215 Highs Post-ATM Offering"
WHY
  underlying -2.1%/-0.9%/-6.9% (favorable peak +7.4%); position move -6.9%.
  decomp [first-order]: theta drag ~10% of premium / 3d · delta capture ~-39% · IV residual ~48% [inferred].
  convexity Γ·S = 0.97. exit TIMEOUT → realized -0%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE ELF-2026-04-27-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 24 · V/OI 6.17 · spread +0.0%
  greeks Δ0.597 Γ0.0284 Θ-0.111 · IV 0.827 · mid 8.39
  overnight_score 4 · flow DIRECTIONAL · catalyst Technical Breakout (0.65) · RSI 41
  headline "e.l.f. Beauty Stock Is Down 15% in 2026. Can 45% Upside Support a Rebound?"
WHY
  underlying -1.1%/-4.1%/+0.4% (favorable peak +1.2%); position move +0.4%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~2% · IV residual ~2% [inferred].
  convexity Γ·S = 1.81. exit TIMEOUT → realized -0%.
TAKEAWAY: Chop: underlying never moved enough either way; theta bled it out over the hold.
```

```
CASE CR-2026-04-22-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 22 · V/OI 98.67 · spread +0.1%
  greeks Δ0.617 Γ0.0167 Θ-0.203 · IV 0.512 · mid 10.72
  overnight_score 2 · flow DIRECTIONAL · catalyst Macro (0.40) · RSI 46
  headline "US stock futures slide over 1% after Iran ceasefire talks fall through"
WHY
  underlying +0.4%/+0.3%/+1.9% (favorable peak +2.9%); position move +1.9%.
  decomp [first-order]: theta drag ~6% of premium / 3d · delta capture ~19% · IV residual ~-14% [inferred].
  convexity Γ·S = 2.99. exit TIMEOUT → realized -0%.
TAKEAWAY: TWO-LABEL TRAP: underlying moved our way but the option still lost — decay / insufficient delta ate the move.
```

```
CASE GOOGL-2026-05-13-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 12 · V/OI 5.17 · spread +0.0%
  greeks Δ0.331 Γ0.0160 Θ-0.338 · IV 0.303 · mid 5.04
  overnight_score 7 · flow DIRECTIONAL · catalyst Technical Breakout (0.90) · RSI 76
  headline "SpaceX and Google in Talks to Explore Data Centers in Orbit Amid $200B Anthropic Cloud Commitment"
WHY
  underlying -0.4%/-1.5%/-1.4% (favorable peak +1.5%); position move -1.4%.
  decomp [first-order]: theta drag ~20% of premium / 3d · delta capture ~-37% · IV residual ~57% [inferred].
  convexity Γ·S = 6.43. exit TRAIL → realized -0%.
TAKEAWAY: Directional miss — underlying went against the position.
```

```
CASE DAVE-2026-05-05-B  ·  BULLISH  ·  LOST  ·  [backtest_replay]
FEATURES (ex-ante)
  moneyness +0.0% · DTE 43 · V/OI 1.06 · spread +0.1%
  greeks Δ0.465 Γ0.0049 Θ-0.385 · IV 0.958 · mid 32.40
  overnight_score 5 · flow DIRECTIONAL · catalyst Earnings Beat (0.90) · RSI 56
  headline "Dave Inc. (DAVE) Beats Q1 Estimates and Raises Guidance, but Shares Slide on Convertible Note Dilution Fears"
WHY
  underlying -6.6%/-5.5%/-2.8% (favorable peak +0.6%); position move -2.8%.
  decomp [first-order]: theta drag ~4% of premium / 3d · delta capture ~-11% · IV residual ~14% [inferred].
  convexity Γ·S = 1.29. exit TIMEOUT → realized -0%.
TAKEAWAY: Directional miss — underlying went against the position.
```
