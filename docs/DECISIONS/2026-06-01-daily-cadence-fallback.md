# 2026-06-01 — Daily-cadence fallback (surface a trade every tradeable day)

**Status:** implemented, pending `gammarips-review` + deploy
**Services:** `signal-notifier` (selection), `forward-paper-trader` (tag propagation)
**Decision owner:** Evan
**Related:** [[2026-05-12-v5-4-pipeline-alignment]], [[2026-05-19-active-days-liquidity-gate]], [[2026-05-08-v5-3-retired-v5-4-promoted]]

## Problem

The cohort is producing ~6 trades across ~13 trading days (5/13–6/1) against an operator target of ≥10/month. The bottleneck is **not** the trader or the one-pick-per-day cap (~21/month ceiling) — it is the upstream conviction funnel emptying on too many days. The 22-day V5.4 sample shows median 1 candidate/day and frequent zero-candidate skips even in a risk-on tape.

**Motivating case — scan_date 2026-05-26 (skipped `no_candidates_passed_gates`):** the enriched pool held **24 candidates scoring 7–8**, all rejected by the strict conviction gates (unusual-volume `V/OI > 2`, the tight 5–10% OTM band) and the contract liquidity floors. A run of those names were perfectly fillable (ADBE BEARISH: OI 109, vol 322, 2% OTM put; RBLX, CTSH, DHI similar). We stood down on a day that had real, tradeable signal — just not *unusual-volume* signal.

## Decision

When the strict stack leaves **zero** candidates, do not skip. Re-query with the two **pure-conviction** gates relaxed and surface the single best *fillable* candidate.

| Gate | Strict | Fallback | Rationale |
|---|---|---|---|
| `volume_oi_ratio > 2` | required | **dropped** | "Unusual volume" is a conviction signal, not a fillability signal. Relaxing it is the whole point — we accept a liquid name without a volume spike. |
| `moneyness_pct` | `[0.05, 0.10]` | `[0.0, 0.10]` | Allow ATM (more liquid, higher delta — safer for a fallback). ITM still excluded; 10% OTM cap kept (no deep-OTM lottery). |
| `recommended_oi ≥ 10` | kept | **kept** | Tradeability. Excludes thin OI=3 mirages (CDNS) that would fill at fictional prices → INVALID_LIQUIDITY. |
| `recommended_volume ≥ 50` | kept | **kept** | Tradeability. |
| DTE `[7, 45]` | kept | **kept** | Bracket gamma profile. |
| Regime `VIX ≤ VIX3M` | kept | **kept** | Literature-settled; runs on the fallback pool. |
| Earnings-overlap exclusion | kept | **kept** | Hard rule (De Silva 2026; Cao-Han 2013); runs on the fallback pool. |
| `active_days_20d ≥ 5` | kept | **kept** | Resting-liquidity backstop; runs on the fallback pool. This is what makes a fallback pick genuinely fillable despite lacking the volume spike. |

**Fallback ranking:** `(1) overnight_score DESC, (2) recommended_oi DESC, (3) spread ASC, (4) ticker ASC` — best composite signal among the most fillable.

**Ranker bypassed on fallback days.** The fallback pool is already "best fillable candidate" by construction, and routing ~1 low-conviction name through the Scorer/Picker only re-introduces a mass-leakage skip that would defeat the cadence guarantee. The deterministic top row is taken directly, written `confidence=LOW` with a templated justification, email subject suffixed `[FALLBACK]`. STRICT days are unchanged (full V5.4 ranker path).

**Honest skip preserved.** If the fallback pool is *also* empty, or a kept tradeability gate (regime/earnings/liquidity) empties it, the day still skips `no_candidates_passed_gates`. "Daily" is not absolute — a genuinely barren or backwardation day still stands down.

## Why this is safe to ship at N=6

- It is **additive and reversible** — STRICT behavior is byte-identical; the fallback only fires on days that would otherwise be skips (no trade lost, only trades gained).
- It relaxes **conviction**, never **tradeability** — the gates that prevent fake fills and earnings IV-crush are all retained.
- Fallback picks are **tagged `policy_gate=FALLBACK`** end-to-end (`todays_pick` → `forward_paper_ledger`). This is the kill switch: if fallback trades prove EV-negative in ledger analysis, they are identifiable and the fallback is retired with data, not opinion.

## Measurement / revisit trigger

At **N≥10 closed FALLBACK trades**, compare FALLBACK vs STRICT realized EV on the ledger (`GROUP BY policy_gate`). If FALLBACK EV is materially negative while STRICT is not, retire the fallback or tighten its liquidity floor (pillar: a fallback lacking volume-spike conviction may warrant a *higher* resting-OI bar than the strict OI≥10). Until then, the fallback runs to buy cadence and accelerate the path to N≥30.

**Cohort-labeling note for the analyst (gammarips-review, 2026-06-01):** `forward_paper_ledger.policy_gate` will hold **three** distinct values over time — `ENRICHMENT_ONLY_NO_TRADER_GATE` (legacy ranker picks written before this change, plus all skip rows), `STRICT` (ranker picks after this change), and `FALLBACK`. For the EV comparison, treat `ENRICHMENT_ONLY_NO_TRADER_GATE` **and** `STRICT` together as the non-fallback baseline (i.e. `policy_gate != 'FALLBACK'` among executed rows), or filter `entry_timestamp >= <deploy_date>`. Do not read pre-deploy STRICT history as missing just because its tag string differs.

## What this does NOT change

- Trader execution mechanics (entry 10:00 ET, −60% stop / +80% target, trail, 3-day hold). Unchanged.
- The STRICT V5.4 ranker path. Unchanged.
- The +80% target debate (see session 2026-06-01): a quick-scalp target would have halved cohort return by clipping the HTZ tail. Deferred until N≥15 gives a real distribution of +30%-touching trades to calibrate a trailing floor. This decision is cadence-only.
