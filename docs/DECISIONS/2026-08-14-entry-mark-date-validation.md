# 2026-08-14 — The entry mark was a delayed day close under a hardcoded "9:50 ET" label

**Status: FIXED in code, `gammarips-review` FAIL then re-review, NOT YET DEPLOYED.**
Display path only. No selection input changes. Supersedes the `entry_mark_source`
enum pinned in `docs/DECISIONS/2026-06-30-entry-day-mark-and-limit.md`.

## Problem

`last_trade` is **not entitled** on the current Polygon plan.
`signal-notifier/main.py::_fetch_entry_mark` prefers `last_trade` and falls back
to `day.close`. Measured across every pick that ever carried an entry mark:

| field | value | rows |
|---|---|---|
| `entry_mark_source` | `day_close` | **32 of 32** |
| `entry_mark_asof` | None | **32 of 32** |
| `entry_mark_stale` | False | **32 of 32** |

Three defects follow, and all three applied to every card the engine has sent
since 2026-06-30.

1. **The card's time label was a constant.** `_entry_display_strings` set
   `asof_label = "9:50 ET"` and only overwrote it from a last-trade timestamp
   that never arrives. The card asserted a measurement time on 32 of 32 picks
   and measured it zero times.
2. **The staleness flag was unreachable.** `stale` came from the last-trade age
   only. On the `day_close` path it was False by construction. The guard that
   exists to protect this number could not fire.
3. **A prior session's close could become an entry mark.** `day.close` had no
   date validation. This is the GAP-018 defect class one function over. The
   2026-08-07 follow-on audit scoped to readers of `day.volume`, so it never
   looked here.

### Size

Compared against the engine's own 10:00 ET entry basis (`opp_entry_price`) on
all 27 picks where both exist:

| measure | value |
|---|---|
| median absolute error | **16.2%** |
| mean absolute error | **28.4%** |
| off by more than 10% | 18 of 27 |
| off by more than 20% | 12 of 27 |
| largest | 186.7% (V, 2026-07-02, card $4.62 against $1.61) |
| mean signed error | +7.8% |

The error is unbiased, so no calibration constant removes it. `opp_entry_price`
carries 2% entry slippage, so each figure moves about 2 points more positive
without it. The conclusion does not move.

**Why it costs money.** `ENTRY_CHASE_CAP` is 8%, which is smaller than the
median error of the mark it caps, so the do-not-chase rail cannot do its job. A
-30% stop off a 27%-high mark sits at about -11% from the real price. Same-day
touch rates on this pool, N=2,112: **-30% is touched 19.4%** of the time,
**-11% is touched 50.0%**. The mark error turns a 1-in-5 stop-out into a coin
flip.

Worked example, the 2026-08-13 HPE card. Published mark $4.00, which is exactly
the 09:32 minute-bar close. True 10:00 close $3.15. Operator filled at $3.49 at
10:16, matching the tape. Prior session close $2.09.

## Fix

`_fetch_entry_mark` now date-validates with the existing `_day_bar_et_date`.

| snapshot state | result |
|---|---|
| day bar dated TODAY | serve, publish the bar's REAL `last_updated` as `asof` |
| day bar dated EARLIER | **REFUSE**. `source="stale_day_bar"`, price None, `stale=True` |
| day bar outside the age bound | UNDATABLE. Serve, force `stale=True` |
| no parseable `last_updated` | UNDATABLE. Serve, force `stale=True` |
| last trade dated EARLIER | **REFUSE**. `source="stale_last_trade"`, `stale=True` |

**Fail direction is asymmetric on purpose.** A wrong mark is worse than no mark,
because `limit_entry_price`, `do_not_chase_above`, `display_target_price` and
`display_stop_price` are all derived from it, and the operator places orders
against them. So a prior-session price is refused rather than served.

**The age bound is not decoration** (`gammarips-review` BLOCKING B2). It mirrors
`_validate_day_bar_volume`'s `PRINT_BAR_MAX_AGE_DAYS`. Without it a vendor units
change (ns to ms) parses every bar to 1970, every date reads older than the read
date, and the function refuses **100% of marks, silently and forever**. A
refusal is not a safe default when it is universal. An out-of-range date is
therefore UNDATABLE, never "prior session".

**One read clock.** Date validation and staleness both use the injectable
`read_dt_et`, so a replay is reproducible. Follows the 2026-08-07 precedent.

### The refusal must be visible (`gammarips-review` BLOCKING B1)

The first version of this fix was **blocked**, and correctly. With no usable
mark `_entry_display_strings` returns None and both render paths fall to an ELSE
branch that prints `Mid {recommended_mid_price}` — the **overnight scan-time**
mark. That is the exact number this feature was built to escape (the FCEL
2026-06-29 card showed $2.40 against a real $5.10). The refusal added to protect
the operator would have rendered a normal-looking pre-2026-06-30 card, so a
refusal day would have been **indistinguishable from a healthy one**, and the
displayed number would have been worse than the one it replaced.

New `_entry_mark_refusal_note()` returns one line, shared by the email and the
plain-text render so they cannot drift:

```
OVERNIGHT scan mark — live entry mark REFUSED (Polygon served a PRIOR-SESSION
day bar). No limit, target or stop is published. Set your own from the live book.
```

An unrecognized `entry_mark_source` still produces a caveat. A future enum value
can never render as a silent clean fallback.

`limit_good_til` and `entry_bracket_basis` no longer assert a live basis over a
row of nulls. They become None and `"none_refused"`.

## Contract change

`entry_mark_source` on the Firestore `todays_pick` doc gains two values:

```
last_trade | day_close | stale_day_bar | stale_last_trade | unavailable
```

Consumers audited by `gammarips-review`. **No consumer breaks.** No engine
reader. `gammarips-mcp` has zero consumers (pick tools removed in V3).
`forward-paper-trader` reads no mark field, so no execution path is affected.
`x-poster` and `reddit-poster` read the whole doc but reference no price field.

**Follow-up, separate repo, separate commit:** `gammarips-webapp`
`src/lib/firebase-admin.ts:294` declares the old three-value union over an
unchecked cast, so an unknown value cannot throw, but the comment at `:290-291`
prescribes the dangerous behavior ("render falls back to recommended_mid_price").
Fix the union and that comment together.

## What this does NOT fix

The mark is still a **delayed day-bar close**, so it is still about 15 minutes
old on a good day. This change stops the card from lying about which number it
is and when it was taken. Only a live 10:00 ET pass fixes the staleness itself,
and that is the trader's P1, accepted and not built. See
`docs/research_reports/handoffs/2026-08-14-trader-handoff-response.md`.

`src/enrichment/core/clients/polygon_client.py:90` is a **third** reader of the
same shape (`trade.get("price") or day.get("close")`, no date validation). It
feeds `recommended_mid_price`, which is the number the refusal branch falls back
to. Still open. Do not close that item with this change.

## Known residual, accepted (`gammarips-review` second pass, finding 4)

The UNDATABLE branch merges two populations, and they are not equally innocent:

- `last_updated` **absent** — incidental, never seen in 49,285 real reads.
- `last_updated` **present but out of range** — positive evidence of a vendor
  semantics change.

Both serve the price. So under a real ns-to-ms change every card would serve an
unvalidated `day.close` with a `(stale)` tag **and a full bracket derived from
it**, which inverts this function's own rule that a wrong mark is worse than no
mark.

Accepted for now, for three reasons. The B1 caveat makes the alternative
(universal refusal) honest rather than silent. The six-week status quo was
strictly worse than either option. The trigger is low-probability.

**The cheap improvement, if it ever fires:** split the two cases and refuse only
the out-of-range one. Watch for the WARNING `outside [10d, 0d] of read`. If it
fires broadly, treat it as a Polygon timestamp-unit change and read this section
before touching anything.

## Definition of Done

Not an execution-policy change. `docs/TRADING-STRATEGY.md` has no entry-mark
content, nothing here touches selection, entry, stop, target or exit, and the
trader reads no mark field. So no 30-day forward-validation gate applies. This
note exists because the published Firestore contract changed.

## Tests

`signal-notifier/tests/test_entry_mark.py` — 21 cases. Today's bar served with
its real timestamp, prior-session close refused, undatable bar served but
flagged, the 1970 unit-change case, a future-dated bar, staleness now reachable
on the `day_close` path, prior-session last trade refused, the refusal note for
every enum value including an unknown one, and the card label never returning
the constant.

```
.venv/bin/python -m pytest signal-notifier/tests signal-judge/tests/unit -q
110 passed
  test_entry_mark.py  21
  test_print_floor.py 46
  signal-judge/unit   43
```

## Rollback

No new env var. Revert the commit. The pre-fix behavior is a bit-identical
`day.close` passthrough with `asof=None` and `stale=False`.
