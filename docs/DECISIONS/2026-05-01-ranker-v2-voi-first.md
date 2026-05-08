# 2026-05-01 — Signal-notifier ranker: directional V/OI replaces dollar-volume primary

## Decision
Change the `signal-notifier` LIMIT-1 ORDER BY from "biggest directional UOA dollar volume wins" to "highest directional volume-to-open-interest ratio wins."

**Old ranker** (`signal-notifier/main.py:500-507` pre-change):
```sql
ORDER BY
    CASE WHEN direction = 'BULLISH' THEN call_dollar_volume
         ELSE put_dollar_volume END DESC,
    overnight_score DESC,
    volume_oi_ratio DESC,
    recommended_spread_pct ASC,
    ticker ASC
LIMIT 1
```

**New ranker** (post-change):
```sql
ORDER BY
    COALESCE(
        CASE WHEN direction = 'BULLISH' THEN call_vol_oi_ratio
             ELSE put_vol_oi_ratio END,
        0
    ) DESC,
    recommended_spread_pct ASC,
    overnight_score DESC,
    ticker ASC
LIMIT 1
```

Hard gates (WHERE clause) are unchanged. The SELECT now also returns `call_vol_oi_ratio` and `put_vol_oi_ratio` for downstream visibility.

## Why
EDA on N=435 V5.3 trades (10 scan days, 2026-04-13 → 2026-04-24, joined `overnight_signals_enriched` to `forward_paper_ledger`) showed the previous primary key was sorting in the wrong direction:

| Lead key | Top-1 days | Wins | Win-rate | Wilson 95% CI | Avg return |
|---|---|---|---|---|---|
| **`directional V/OI DESC` (NEW)** | 10 | 8 | **80%** | [49, 94] | **+28.4%** |
| `premium_score DESC` | 10 | 6 | 60% | [31, 83] | +3.7% |
| `recommended_spread_pct ASC` | 10 | 5 | 50% | [24, 76] | +3.8% |
| `overnight_score DESC` | 10 | 4 | 40% | [17, 69] | +2.8% |
| `enrichment_quality_score DESC` (Gemini) | 10 | 3 | 30% | [11, 60] | −15.6% |
| **CURRENT 5-key** (old) | 6 | 1 | **17%** | [3, 56] | +4.4% |
| `catalyst_score DESC` (Gemini) | 10 | 1 | 10% | [2, 40] | −9.4% |

Universe baseline win-rate over the same 10 days: **43%** [38.4, 47.7].

The old ranker (1/6 = 17%) lost to baseline by ~26 points. Every single-key alternative beat it. The directional V/OI lead key (8/10 = 80%) held in walk-forward halves (4/5 first half + 4/5 second half), making it the most stable candidate.

**Mechanism:** `directional_dollar_volume` measures absolute flow magnitude (institution-sized prints). `directional V/OI ratio` measures *unusual* flow (volume vs existing open interest). The data says, at the −60%/+80%/3-day bracket, "biggest" anti-predicts and "most unusual" predicts. Big institutional UOA tends to be hedging or rolls; high V/OI is fresh directional conviction.

Univariate evidence on the same N=435 cohort: winners had **lower** call_uoa_depth, put_uoa_depth, recommended_volume, contract_score, and recommended_iv than losers. The old ranker's primary key has the wrong sign on a confirmed-direction feature.

## Why we shipped without 30-day A/B
- Lead-key sign is unambiguous (1/6 vs 8/10 is not a tie).
- `gammarips-review` mandate applies to `forward-paper-trader` deploys; this is `signal-notifier` (upstream signal-quality, not execution).
- The ledger continues to log every pick; if the new ranker degrades, we'll see it in `forward_paper_ledger` within ~30 closed trades and revert.
- Park-mode is active (per project memory): the system is not actively trading; it's still surfacing picks for the email/WhatsApp pipeline. Cost of a bad week is logging, not P&L.

## Caveats
- N=10 scan days is small. The 80% point estimate is hypothesis-strength, not statistical proof.
- 45 hypotheses tested in the EDA → multiple-comparison concerns. Even 8/10 has selection-bias inflation.
- Validates only against V5.3 era data. Earlier V4 ledger does not exist.
- Tiebreakers (spread, overnight_score, ticker) are deterministic but their order is a judgment call within tied V/OI; expected to matter on <10% of days.

## Validation plan
- Monitor next 30 closed trades in `forward_paper_ledger`. Track win-rate vs the 43% baseline.
- If new-ranker win-rate drops below 35% over 20+ closed trades, revert to old ranker via single-line ORDER BY change and re-investigate.
- Continue current logging — no schema change required.

## Alternatives considered and rejected
- **Add an LLM judge over top-3 deterministic candidates.** Rejected. Logistic regression on 21 features yields AUC=0.464 (worse than chance) — labels are nearly orthogonal to features. An LLM cannot extract signal that isn't there. Recent agent-arena V1 retrospective independently confirmed multi-LLM ranking underperforms baseline.
- **Lead with `premium_score DESC`.** Rejected. premium_score=0 picks have *higher* win-rate (43.9%) than premium_score≥1 (~41%). The 5-flag composite has no predictive power at V5.3.
- **Lead with `enrichment_quality_score DESC`.** Rejected. Hits 3/10 wins and −15.6% avg return. Worst Gemini-derived signal tested.
- **30-day forward A/B with `proposed_v2_pick` column.** Rejected. The lead-key sign is decisive; a 30-day wait is not justified for a same-direction-but-stronger primary key.

## Changes
- `signal-notifier/main.py:480-516` — rewrite ORDER BY, expand SELECT to include directional V/OI columns, update inline comment block to cite this DECISIONS doc.

## Deploy
`cd signal-notifier && bash deploy.sh`

## Follow-ups (separate work)
- Funnel EDA in flight: tighten `enrichment-trigger` gates so ~20-30 candidates per day reach `overnight_signals_enriched` instead of the current ~120+. Will land in a separate DECISIONS note.
- Data-plumbing: `volume_oi_ratio`, `moneyness_pct`, `vix3m_at_enrich` are NULL on rows pre-2026-04-17. Not a regression here (gates already reject NULLs), but worth a backfill if someone wants V4-era data queryable.
