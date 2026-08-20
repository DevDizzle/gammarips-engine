# 2026-08-20 — Score floor accepted at 1, PRINT_FLOOR_MIN=25 shipped, cohort reset to 2026-08-21

**Status:** DEPLOYED 2026-08-20 — `signal-notifier-00062-wvm` serving 100%,
env `PRINT_FLOOR_MIN=25` verified, all secret mounts intact, clean boot. Two
owner calls, made together in the 2026-08-20 session.

## Call 1: accept `MIN_ENRICHMENT_SCORE=1` and scrub the `>= 4` claim

**The `overnight_score >= 4` floor never ran a single day.** Timeline, verified
from git and the live Cloud Run env:

- 2026-04-20 (`3c5cc94`, V5.3 Target 80 cutover): the code default AND the
  deploy.sh env pin were both set to 1, deliberately.
- 2026-06-05 (decision `2026-06-05-engine-quote-outage-and-gate.md`): the owner
  shipped "the `score >= 4` floor". The deploy changed only the code default
  (1 → 4, committed `398339b` on 06-08). The deploy.sh pin
  `MIN_ENRICHMENT_SCORE=1` was not touched, and the env var wins over the
  default. Production enriched at `>= 1` before, during, and after.
- 2026-08-20: live env verified `MIN_ENRICHMENT_SCORE=1`.

**Why accept 1 instead of deploying 4:**

- The floor is measured cosmetic. Among BULLISH + UOA>$500K (median 142
  qualified/day), removing `score >= 4` changes the top-50 pool on 1 of 20 days,
  6 slots total (FINDINGS_LEDGER §2026-07-28 entry-day contract tradeability
  study). The UOA bar,
  the BULLISH gate, and the top-50 edge-rank cap do the filtering.
  `overnight_score` AUC against outcomes is ~0.51.
- Every research result on the enriched substrate was measured on the floor=1
  reality, so accepting 1 changes nothing and re-labels nothing. Deploying 4
  would change production to match a claim whose evidence base was 33 days, one
  regime, on the retired 3-day-bracket labels (76% timeout exits), pre-ghost-audit.
- V6 doctrine is "feed the tournament a broad pool, let it discriminate."
  Floor=1 is that doctrine.

**Consequence:** the `>= 4` claim is scrubbed from every surface: engine docs
and wiki, the MCP tool docstrings and playbooks (`education.py`,
`overnight_signals.py`, `content/playbooks/`), and the webapp methodology page
and landing FAQ (branch + PR, merges through that repo's own gates). The code
default in `enrichment-trigger/main.py` is set to 1 so the env pin and the
default agree; no enrichment-trigger redeploy is needed (behavior is unchanged).

## Call 2: ship `PRINT_FLOOR_MIN=25` on signal-notifier

Adopted 2026-08-19 (header of `2026-08-19-pool-liquidity-floor-and-cap-20.md`;
that note's enrichment admission-floor design was NOT adopted). Deployed
2026-08-20.

**Evidence (31 measured days of `pool_liquidity_snapshot`):** raising the
known-prints floor from 1 to 25 cuts the slate ghost rate 36.7% → 9.4% and
raises the tradeable share 25.4% → 62.6%. ~3% of days fall below `TOURNEY_MIN`,
which under `FAILSOFT_RESTORE_MODE=none` is a legitimate `no_liquid_candidates`
no-pick day, not a failure.

**Why it matters:** ghosts exit at the fabricated −1.9608% no-move mark
([[ghost-rows-flatter-pool-composites]]) and cannot be exited cleanly when the
stop fires (stop slippage median −3.1%, thin names −10.3% —
`docs/EXECUTION-RISK-GUIDELINES.md`). The operator trades the pick with real
money.

**Rollback lever:** env `PRINT_FLOOR_MIN=1`, redeploy. `PRINT_FLOOR_ENABLED=false`
remains the full kill switch.

## Cohort reset → 2026-08-21

A material selection change resets the cohort
([[cohort-reset-on-filter-change]], standing practice since 2026-05-06,
re-confirmed 08-12). First entry day under the new floor is 2026-08-21. Fifth
reset in eight weeks; the 08-12 caution about incremental selection churn
stands — this ghost-scrub is intended as the last selection change before the
pre-registered pool-vs-benchmark test runs.

Mirrors moved in the same change: `signal-notifier/main.py`,
`libs/gammarips_content/gammarips_content/cohort.py` (pin test green). The MCP
repo's mirror (`data.py` + prose) moves in that repo's own commit. x-poster and
blog-generator need a redeploy to pick up the vendored lib — tracked in
`NEXT_SESSION_PROMPT.md` (blog-generator's Mon 05:00 ET cron is the exposure).
No truncation: prior rows stay in `forward_paper_ledger`, excluded by the date
filter.

## Verification

- Post-deploy: env shows `PRINT_FLOOR_MIN=25`, new revision serving, logs clean.
- Next 09:52 ET run (2026-08-21): expect a thinner slate. Grep
  `Fail-soft restore SUPPRESSED` / `EMPTY SLATE` / `no_liquid_candidates`.
  A no-pick day is correct behavior.
