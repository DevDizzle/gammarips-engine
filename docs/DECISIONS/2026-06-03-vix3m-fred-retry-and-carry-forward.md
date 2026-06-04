# 2026-06-03 — VIX3M FRED retry + bounded carry-forward (regime-data resilience)

**Status:** implemented, gammarips-review SAFE-TO-DEPLOY, pending deploy
**Services:** `enrichment-trigger` (VIX3M + VIX fetch), `signal-notifier` (regime-gate VIX fetch)
**Decision owner:** Evan
**Related:** [[2026-06-01-daily-cadence-fallback]], [[2026-05-08-v5-3-retired-v5-4-promoted]]

## Incident

**scan_date 2026-06-02 produced no trade.** Not the trader, not the gates, not the
2026-06-02 V/OI/moneyness commit (`ec995e7`) — a transient **FRED outage**.

The 2026-06-03 09:30 ET enrichment run hit FRED `fredgraph.csv?id=VXVCLS` (VIX3M) and
`?id=VIXCLS` (VIX). Both **read-timed-out** at the 15s ceiling:

```
WARNING:main:VIX:   FRED fetch failed: ...Read timed out (read timeout=15). Storing NULL.
WARNING:main:VIX3M: FRED fetch failed: ...Read timed out (read timeout=15). Storing NULL.
```

`fetch_vix3m_for_scan_date` caught the failure and stored `NULL`. The in-process
`_VIX3M_CACHE` then served that `NULL` to **all 101 enriched rows**. Both the STRICT and
FALLBACK candidate queries in `signal-notifier` require `vix3m_at_enrich IS NOT NULL`, so
the entire slate was wiped — `Post-filter candidates: 0` in both modes → honest skip, no
email. With VIX3M present there were **32 strict-moneyness candidates** that day; the slate
was healthy, only the regime column was missing.

Root weakness: **a single transient FRED fetch poisons a whole scan_date** (one timeout →
cached NULL → every row NULL → both gate paths empty). The system fail-closed correctly
(no bad fill), but lost a tradeable day to a 15-second external blip.

## Decision

Harden the FRED regime-data path so a transient outage no longer wipes a day, while keeping
the fail-closed contract intact for genuine prolonged outages.

1. **Retry + longer timeout.** New `_fetch_fred_csv(url, retries=3, timeout=30)` in
   `enrichment-trigger` (linear backoff 2s/4s). Used by both `fetch_vix3m_for_scan_date`
   and `fetch_vix_for_scan_date`. `signal-notifier.fetch_vix_close` gets the same 3×/30s
   retry inline. The exact incident (one 15s timeout) is now absorbed by ≤3 attempts.

2. **Bounded carry-forward (VIX3M only).** If `VXVCLS` still fails after retries, enrichment
   reads the most recent non-null `vix3m_at_enrich` **strictly before** `scan_date` from
   `overnight_signals_enriched` and carries it forward — but **only if ≤7 calendar days old**
   (`VIX3M_CARRY_FORWARD_MAX_AGE_DAYS`). Past that bound, store NULL and fail-closed as before.

### Why this is safe

- **No lookahead.** The carry-forward query filters `DATE(scan_date) < "{scan_date}"`
  (strict `<`), so it can never pull the current or a future date's value. The read runs
  before the dedup `DELETE`/write of the current day's rows; the strict `<` makes any
  same-date row ineligible regardless.
- **Regime contract preserved.** VIX3M is a 3-month forward-vol measure — slow-moving — so a
  ≤7-day-old close (≈5 trading days) is a sound proxy. Past the bound we still fail-closed.
- **VIX leg never carried forward.** `signal-notifier` still fetches a **fresh** same-day VIX
  for the `VIX ≤ VIX3M` comparison, so a genuine same-day vol spike still trips backwardation
  and skips — carry-forward cannot mask it. Only the slow 3M leg is reused.

### Live-VIX fallback (added same day, owner-directed)

The FRED outage on 2026-06-03 was **prolonged** — down for both the VIX3M and the live-VIX
legs through every retry, from Cloud Run egress, for hours. VIX3M carry-forward repaired the
slate query, but `signal-notifier.fetch_vix_close` still returned None → `regime_fail_closed`,
blocking the day even though the regime was independently confirmed calm (VIX ≈16 ≪ VIX3M).

Owner directed shipping a live-VIX fallback rather than skipping. `fetch_vix_close` now tries
FRED VIXCLS (3× retry) → **Stooq** ^VIX CSV → **Yahoo** ^VIX chart JSON, returning the first
usable close on/before scan_date; None only if all three fail (still fail-closed). This
reverses the earlier "carry-forward only, no alt vendor" choice (2026-06-03 AAC question) once
it was clear carry-forward does not cover the live-VIX leg. Stooq/Yahoo are unauthenticated
public sources; no key, no plan entitlement (Polygon's plan is not entitled to I:VIX).

**Validation:** triggered `signal-notifier` for scan_date 2026-06-02 with FRED down — Yahoo
fallback returned VIX 15.77, regime passed (15.77 ≤ 18.66), pick **DAVE BEARISH** emitted.

**Review + hardening (2026-06-03, post-deploy).** The live-VIX fallback was first shipped
single-source (first usable of Stooq→Yahoo wins) to unblock the DAVE pick. `gammarips-review`
then returned **CHANGES REQUIRED** (safe to keep serving, no rollback). Hardened accordingly:

- **Two-source corroboration (was the HIGH finding).** The regime gate is one-sided
  (`vix_now > vix3m` => skip), so a single fallback source biased LOW could mask a backwardation.
  A fallback value is now trusted only when BOTH Stooq and Yahoo agree within
  `VIX_FALLBACK_TOLERANCE = 1.5` vol pts (uses their mean); if only one answers, or they
  disagree, fetch_vix_close fail-closes (returns None → `regime_fail_closed`). **Availability
  cost, accepted:** a FRED-outage day on which only one backup is reachable now SKIPS — the
  2026-06-03 Yahoo-only DAVE pick would NOT have fired under this rule. FRED itself stays
  single-source-trusted.
- **Plausibility bound** `1.0 < v < 200.0` on every parsed value (FRED + both fallbacks).
- **Stooq parse** now requires the full 6-column schema (was `< 5`).
- **`d < today` (ET) guard** so a live/partial current-session bar can never feed the gate.
- **Provenance:** `todays_pick` now carries `vix_source` ("FRED" / "Stooq+Yahoo") for audit.

Remaining follow-up: consider persisting `vix_at_enrich` so the regime read has one provenance
(deferred). Note: the 2026-06-02 slate's `vix3m_at_enrich` was repaired via a one-off manual
`UPDATE ... SET vix3m_at_enrich = 18.66` (carry-forward value), not a recurring path.

### Provenance follow-up (recommended by review)

Carried-forward VIX3M is written into `vix3m_at_enrich` indistinguishably from a fresh read.
Consider adding a `vix3m_carried_forward_age_days` column so carry-forward fire-days can be
segmented in postmortem (did they underperform?). Deferred — carry-forward is expected to be
rare.

## Today's skipped trade (2026-06-02)

**Let it skip** (owner decision). FRED was still 504-ing at review time, blocking a clean
re-run; no bad fill occurred and the N=6 cohort is unaffected. The fix prevents recurrence;
no retroactive backfill attempted.

## Scope

Reliability/availability hardening of the regime-data fetch — **not** an execution-policy or
gate-threshold change. The gate logic (`VIX ≤ VIX3M`, NULL ⇒ skip) is byte-for-byte preserved.
Full 30-day forward-paper DoD does not apply (no new strategy/gate/bracket). Cleared by
`gammarips-review` (SAFE TO DEPLOY).

---

## Follow-up 2026-06-04 — live-VIX fallback simplified (two-source rule removed)

The 2026-06-03 hardening shipped a *second* guard alongside the VIX3M carry-forward: on FRED
failure, the **live** VIX leg fell back to Stooq + Yahoo but trusted the value only if **both**
corroborated within 1.5 vol-pts (`VIX_FALLBACK_TOLERANCE`). Rationale at the time: a single
low-biased source could mask backwardation on the one-sided `vix_now > vix3m → skip` gate.

That rule was too strict and re-wiped a day. Scan **2026-06-03** (entry **2026-06-04**): FRED
VIXCLS was still timing out, VIX3M carry-forward worked (18.66), 4 candidates were queued — but
the live leg got only **Yahoo=16.06** (Stooq returned nothing), so the two-source requirement
rejected a perfectly good reading and fail-closed. 16.06 ≪ 18.66 was plainly contango.

**Fix:** drop the corroboration requirement. On FRED failure use the best public source that
answers; when both answer take the **MAX** — the conservative direction for this gate (a
low-biased source cannot manufacture a false trade; at worst MAX causes a false *skip*). A single
source is sufficient. Only a total source blackout fail-closes. `VIX_FALLBACK_TOLERANCE` removed.

Deployed `signal-notifier-00033-sjr`; notifier re-run for scan 2026-06-03 emitted **BBWI BULLISH**
(`vix_source=Yahoo`, vix_now=16.06) before the 10:00 ET entry. Same scope as above —
availability hardening, gate logic byte-for-byte preserved. Cleared by `gammarips-review` (GO):
all fallback bars still pass `_vix_date_ok` (`d ≤ scan_date AND d < today`), no lookahead.
