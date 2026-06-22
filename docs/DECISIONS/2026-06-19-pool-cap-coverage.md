# 2026-06-19 — Pool-cap coverage: 25 is the floor (FINDING; flip PENDING)

## Question
What `TOURNEY_POOL_CAP` / `ENRICH_TOP_N` (currently 50) is "sufficient" — how small can the
candidate pool shrink before the tournament starts losing the names that would have won?

## Method
Read-only coverage / ceiling backtest on `enriched_option_outcomes` (deduped) + the frozen
1,375-trade set, evaluated on OPTION PnL, using the **current momentum-inclusive edge-rank**
to order candidates. Point-in-time (mom_60 anchored ≤ scan_date); outcomes used only for
evaluation, never ranking. Bootstrap 95% CIs. This is a **ceiling / necessary-condition** test —
"is the eventual best-PnL name still IN the top-N pool" — it does NOT measure whether the LLM
*picks* better at smaller N (that needs a forward A/B).

## Result
Best-name capture vs the full uncapped pool, by edge-rank top-N:

| N | best-name capture | ceiling-EV shortfall vs full (CI) |
|---|---|---|
| 10 | 56% | −10.0pp [−14.9, −5.8] |
| 15 | 80% | −5.3pp [−9.2, −2.0] |
| 20 | 89% | −3.4pp [−6.5, −0.8] |
| **25** | **93.5%** | **−2.1pp [−5.0, +0.0]** ← only N (besides 50) whose CI touches zero |
| 50 | 100% | 0 |

- **N=10 drops the winner 43% of days** and forfeits ~10pp of achievable ceiling — too small.
- By **N=25** the ceiling shortfall is statistically indistinguishable from the full pool.
- **50 is overkill:** only **4 of 46 days** ever had >50 candidates, so the cap rarely binds.
- Pool-mean quality does NOT rise much as you shrink — edge-rank's value is keeping the
  CEILING intact while shrinking, not lifting the average.

## Decision (PENDING owner timing)
**Recommended target: cut `TOURNEY_POOL_CAP` and `ENRICH_TOP_N` from 50 → 25.** It ~halves the
grounded-enrichment LLM calls (the old cost driver) + tournament calls with no demonstrated
ceiling loss, and makes the momentum tilt more decisive (25 of ~150).

**Not yet shipped — timing is the open question:**
- **Clean (recommended):** hold 50 until the 2026-06-19 momentum tilt earns a clean N≥15 read,
  THEN flip to 25 — so the cohort attributes cleanly to one change at a time.
- **Cost-first:** flip to 25 now, accepting the cohort then reflects both changes.

## Caveats / governance
- **Ceiling test only** — proves the winner is PRESENT at N=25, NOT that the LLM picks better at
  25. Pair the eventual cut with a short forward A/B (25 vs 50) before treating 25 as settled.
- Short window (46 days; only 30 have pools >25); the N=25 CI *just* touches zero — reasoned
  floor, not a precision estimate.
- The cap is an **env knob**, instantly reversible. Flipping it is execution policy → on ship,
  add the deploy revision here + `gammarips-review`.
- Memory: `project_pool_cap_coverage`. Sibling: `docs/DECISIONS/2026-06-19-momentum-60d-edge-tilt.md`.
