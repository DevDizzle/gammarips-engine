# 2026-05-06 — H11 + H12: spread and moneyness tightening (lit-audit recalibrations)

## Decision
Tighten two existing V5.3 signal-quality thresholds to their literature-supported bands:

- **H11:** `recommended_spread_pct <= 0.10` → `<= 0.08` at `enrichment-trigger`
- **H12:** `moneyness_pct BETWEEN 0.05 AND 0.15` → `BETWEEN 0.05 AND 0.10` at `signal-notifier`

Both are *exclusion-style* tightenings (kicking out parameter regions where the literature explicitly documents EV decay), same epistemic class as the earnings-overlap exclusion adopted earlier today. No labeled_v1 backtesting required per the methodological note in `INTELLIGENCE_BRIEF.md` "Hard constraints" — the literature has decades and millions of trades; we have 1,563 rows in one regime.

Surfaced by the parallel three-agent literature audit run on 2026-05-06 (full table in `docs/research_reports/INTELLIGENCE_BRIEF.md`). Both flagged as the highest-confidence quick-win recalibrations.

## H11 — Spread tightening (10% → 8%)

**Why:** A 10% relative quoted spread implies an **effective round-trip cost of ~5-6% of mid** (Muravyev & Pearson 2020, *Review of Financial Studies* — "Options Trading Costs Are Lower than You Think"). On a +80%/-60% bracket, that is ~7% of the option premium *move* lost to friction. More importantly, contracts with relative spreads >10% are usually thin-OI / single-MM listings where adverse selection and fill quality both deteriorate (Mayhew 2002, *Journal of Finance*). And the options-flow signal predictability **collapses when the options market is the less liquid venue** (Cremers & Weinbaum 2010, *JFQA*) — i.e., a 10% spread is itself a signal that the underlying flow read is in the wrong informational regime.

8% is the empirically defensible band for retail execution on 5-10% OTM 9-DTE single-name contracts. Tighter would be conservative (5-7%) but risks emptying the daily candidate pool too aggressively given the universe size.

## H12 — Moneyness upper-bound tightening (15% → 10%)

**Why:** The literature explicitly contradicts the "deeper-OTM = more whale leverage" thesis that motivated the 5-15% V5.3 band. Augustin, Brenner, Grass, Orłowski & Subrahmanyam (2022, *J. Financial Markets*) — informed traders ahead of corporate news prefer *slightly* OTM, not deep-OTM, because bid-ask spreads scale inversely with price and DOTM frictions destroy realized edge. Aretz, Lin & Poon (2023, *Review of Finance*) document a structural ITM calls +7% / DOTM calls −27% systematic-vol return spread: deep-OTM long-call returns are negative on average across the cross-section.

At 9 DTE and 15% OTM, the focal contract has delta ~0.10–0.15 — that is statistically retail/lottery space, not informed-flow territory. Tightening to 10% upper bound moves the band into the informed-flow zone (delta ~0.20–0.40) without invalidating the "leverage edge" intuition that made the V5.3 band attractive in the first place.

5% lower bound stays unchanged — Augustin et al. confirms the "slightly OTM" preference, and 0–5% (near-ATM) is a different trade structure (more delta, less vega; the same-priced ATM contract sees less of the IV positioning that the UOA scanner depends on).

## Implementation
- **`enrichment-trigger/main.py:216`** — `recommended_spread_pct <= 0.10` → `<= 0.08`. Comment block added documenting the literature reference. Log line updated.
- **`signal-notifier/main.py`** — `MONEYNESS_MAX = 0.15` → `MONEYNESS_MAX = 0.10`. Comment block added documenting the literature reference. Module docstring updated.
- **No execution-policy change.** Entry 10:00 ET, −60% stop, +80% target, 3-day hold, 15:50 ET exit are all unchanged. The trader is not touched; `policy_version` tagging is unchanged pending the V5.x naming question (separate decision).
- **No backfill, no historical relabeling.** Forward-only. Existing `forward_paper_ledger` rows stay tagged `V5_3_TARGET_80`.

## Expected impact on candidate volume
Both tightenings narrow the post-filter cohort. Order-of-magnitude estimates from the V5.3 lit-audit notes:
- Spread 10→8%: estimated ~15-25% reduction in daily candidate count.
- Moneyness 15→10%: estimated ~30-40% reduction in daily candidate count (deep-OTM is a meaningful share of UOA flow).
- Combined (multiplicative if independent, less if correlated): ~40-60% reduction.

This is acceptable. The user explicitly prefers fewer-but-better picks (`feedback_simplicity.md`) and the existing `LIMIT 1` selection means we always emit at most one signal per day; reducing the candidate pool from ~10 to ~4-6 per day still leaves ample selection room. Days where the post-filter pool is empty fail-closed via the existing `no_candidates_passed_gates` skip_reason.

## Validation posture
This is theory-driven exclusion, not a hypothesis under test. Per the lit-audit methodology codified in `INTELLIGENCE_BRIEF.md`, the post-deploy ledger evidence validates *implementation correctness* (the right thresholds are being enforced), not *EV lift* (which the literature has already established).

Watch for:
- Post-deploy candidate-count distribution (Cloud Run logs `Found {N} signals` line at enrichment-trigger). If N=0 frequency spikes >2× pre-deploy, escalate to widen the bands or revisit the joint-distribution assumption.
- Skip-day rate at signal-notifier `no_candidates_passed_gates`. Should rise modestly; flag if >50% of trading days.
- First-week ledger rows: confirm all `recommended_spread_pct <= 0.08` and `moneyness_pct <= 0.10`. Drift here would indicate the SQL change didn't propagate.

## Review posture
H11 + H12 are numerical edits to existing gate parameters. No new code paths, no new external dependencies, no new fail-closed behaviors, no trader changes. The earlier `gammarips-review` audit on the earnings filter (2026-05-06) already validated the gate-stack architecture; H11 + H12 ride the same pattern. A formal re-audit is on a per-deploy discretionary basis — not strictly required but will be invoked.

## Files changed
- `enrichment-trigger/main.py` — spread threshold 0.10 → 0.08; comment + log update.
- `signal-notifier/main.py` — `MONEYNESS_MAX` 0.15 → 0.10; comment + module docstring update.
- `CHEAT-SHEET.md` — gate values updated.
- `docs/TRADING-STRATEGY.md` — gate values updated with citation breadcrumbs.
- `docs/research_reports/INTELLIGENCE_BRIEF.md` — H11 / H12 status moved from "pending" to "deployed" (separate edit).
