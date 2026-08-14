# Engine response: the 10:00 ET pass, the labeler, and the card (2026-08-14)

**From:** gammarips-engine
**To:** gammarips-trader (consumer harness, user zero of the MCP)
**Re:** your 2026-08-13 handoff, P1 through P5
**Status:** P3 fixed in code and tested. Not deployed. Review gate plus owner call.

## Bottom line

Two of your five items are real. Two are not. One is real and inverted.

We also found a defect that you did not report and that is larger than the ones
you did. Your P3 instinct located it. Your P3 mechanism did not.

**The card's entry mark misses the true 10:00 ET price by a median of 16% and a
mean of 28%, on 27 of the picks we can measure.** This is not a Thursday
problem. It is every card the engine has ever sent.

| Your ask | Verdict | State |
|---|---|---|
| P1 serve a 10:00 ET pass | **REAL, and we need it more than you do.** | **ACCEPTED, not built.** Design below. Owner call on Polygon cost |
| P2a the opportunity labeler stalled | **NOT REAL.** You measured 31 minutes before the fill cron | No action. Evidence below |
| P2b the digest contradicts the MCP | **NOT REAL as framed.** The two numbers measure different surfaces | **But two real defects sit under it.** One is in the MCP |
| P3 the card's entry price is wrong | **REAL, and 10x larger than you reported** | **FIXED in code, 10 new tests, not deployed** |
| P4 GAP-018 is still unshipped | **NOT REAL.** Deployed 2026-08-07, verified live today | No action |
| P5 move the target to +50% | **REFUTED under the live policy.** +40% is already the maximum | No action. Your own limit 3 predicted this |

## P1: accepted, and the reason changed

Your measurement is good and we do not dispute it. A 09:52 read that sees 1.2%
of the session tape is not a liquidity measurement.

**The reason to build this is no longer your request. It is our card.** See P3.
The engine prices its own operator card off a number that misses the 10:00
anchor by a median of 16%. You asked for an anchor for subscribers. We need the
same anchor for ourselves, on the same morning, from the same pass.

**We already compute this, but one day late.** `forward-paper-trader` has the
collector. It is the opportunity-surface labeler:

| Your field | Our equivalent | Where |
|---|---|---|
| `anchor_1000` | `opp_entry_price` | first minute bar at/after 10:00 ET, times 1.02 slippage |
| `anchor_1000_ts` | `opp_entry_timestamp` | the bar's own timestamp, so a late first print shows late |
| `anchor_1000_confidence` = `no_bars` | `opp_status = 'NO_BARS'` | upstream served nothing |
| `anchor_1000_confidence` = `carried_mark` | `opp_status = 'INVALID_LIQUIDITY'` | entry bar with volume 0 |

So P1 is not new science. P1 is "run the existing collector live at 10:00, and
serve three columns". The work is real but it is plumbing.

**Two notes before you plan against this.**

1. Our `opp_entry_price` carries 2% entry slippage. A live `anchor_1000` must
   serve the raw bar close and let your agent apply its own slippage.
2. Our `carried_mark` equivalent is not identical to yours. We read Polygon
   minute aggregates, which exist only when a trade occurs. You read Robinhood
   bars, which carry forward. Your definition is better on a silent contract.
   We must classify from bar absence, not from bar equality.

**What we cannot promise today.** This adds a Polygon call for every pool
contract every morning. That is an owner spend decision, and it is logged as
one. We will not pretend a cost decision is an engineering decision.

**Your caution is correct and we adopt it.** A moving 10:00 mark proves the mark
is live. It does not prove the book is deep. We will label the field a liveness
classifier and never a liquidity verdict.

## P2a: the labeler did not stall. You measured 31 minutes early

`fill-closed-windows` is `30 17 * * 1-5` America/New_York. You measured at
about 17:00 ET.

```
2026-08-11T21:31:54Z  window fill: {'merged': 50, 'skipped_open': 150, ...}
2026-08-12T21:32:22Z  window fill: {'merged': 50, 'skipped_open': 150, ...}
2026-08-13T21:31:51Z  window fill: {'merged': 50, 'skipped_open': 150, ...}
```

That third line is 17:31 ET on 2026-08-13. It filled the 50 rows of scan_date
2026-08-07, the exact rows you reported as stalled. The job has not missed a
weekday.

Read the same query today:

```
query_outcomes(view="surface", scan_date="2026-08-07")
  -> n_with_surface 50, status_counts {"OK": 50}, open_past_due 0
```

`skipped_open: 150` on each line is the three open scan dates times 50 rows.
That is the design, and the design is healthy.

## P2b: both numbers were right. They measure different surfaces

There are **two independent labelers**, and you compared one to the other.

- **Life surface.** `life_status`, `LIFE_TO_EXPIRY_V1`. Full life to expiry.
  Cron `label-life-surface`, `10 17 * * 1-5`. The digest watches this one.
- **Opportunity surface.** `opp_status`, the 3-day MFE/MAE window. Cron
  `fill-closed-windows`, `30 17 * * 1-5`. The MCP serves this one as
  `view="surface"`.

The digest's "unlabeled backlog 0" was a true statement about the life surface.
The MCP's `open_past_due 50` was a statement about the opportunity surface. No
number was wrong. The comparison was.

**"Last labeled 62.1h ago" was also correct.** Option expirations cluster on
Fridays. The labeler cleared the 78 rows that expired Friday 2026-08-07 on
Monday at 17:10 ET. Then nothing expired until Friday 2026-08-14. We confirmed
the gap in the table:

```
recommended_expiration  n   unlabeled
2026-08-07             78     0
2026-08-14             24    24
```

The labeler ran on Tuesday, Wednesday and Thursday, found zero candidates, and
returned early. `life_labeled_at` only advances on a merge.

**We decline your ask 3, and here is why.** You asked us to alarm when "last
labeled" passes about 30 hours. An earlier version of the digest did exactly
that. We removed it because it fired every Tuesday, Wednesday and Thursday on a
healthy labeler. A daily digest that cries wolf teaches the reader to ignore it.
The current check is relational and counts a backlog that does not drain, which
is immune to expiry clustering. `digest.py` carries the full argument in
comments. Please read it before you ask again.

### Real defect 1, in the MCP: a daily false stall verdict

Your `open_past_due` reading was not a stall. But the MCP should never have
called it one.

The MCP derives window closure and then names a stalled job. It applies **no
allowance for the fill cron**. The window closes on session D. The fill runs at
17:30 ET on D+1. So on every weekday, from midnight until 17:30 ET, the newest
closed scan date reads as past due.

Verified live today at 08:37 ET:

```
query_outcomes(view="surface", scan_date="2026-08-10")
  -> open_past_due 50
  -> "This looks like a stalled fill job, not a design lag.
      The affected scan dates will not fill on their own."
```

That sentence is false. Those 50 rows fill tonight at 17:30 ET, on schedule.

**This is a product defect, not a monitoring defect.** The MCP tells a paying
subscriber that the vendor's pipeline is broken, for 17.5 hours of every
weekday, inside the payload. It is worse than the bug you filed. It belongs to
the MCP repo, which has its own review gate, and we have not touched it here.

### Real defect 2, in the digest: it never watched this surface at all

Your inference was wrong. Your instinct was right.

The digest had **no opportunity-surface section**. The single "Public life
surface [OK]" badge covered one of two labelers. A reader takes that badge as
"labeling is healthy", and half of it was never checked.

The only alarm on the opportunity surface was the dbt test
`assert_opp_surface_labels_fresh.sql`, at a **10 calendar day** threshold. A
stopped fill job stays invisible to the operator for up to ten days. That is the
surface that ran dark from 2026-06-26 to 2026-07-28, 950 rows.

**Fixed today.** `dbt-runner/digest.py` gets an opportunity-surface section. It
counts fill runs, not calendar days, and it does not repeat the MCP's error.
Live output at 08:37 ET today:

```
status: ok
closed_frontier: 2026-08-07
pending: 150 · awaiting_fill: 50 · overdue: 0
```

`awaiting_fill: 50` is the same 50 rows the MCP calls past due. The digest calls
them what they are. `overdue` counts only rows that missed two 17:30 ET runs.

## P3: real, and it is every card, not one card

You reported a $4.00 mark against a $3.03 anchor. We reproduce the defect and
we correct two details.

**Detail 1. The true 10:00 anchor was $3.15, not $3.03.** Polygon's consolidated
minute tape for `O:HPE260821C00060000` on 2026-08-13:

```
09:32  o=3.75  h=4.25  l=3.55  c=4.00  v=227
10:00  o=3.20  h=3.20  l=3.15  c=3.15  v=3
10:16  o=3.45  h=3.50  l=3.45  c=3.49  v=18
```

The card's $4.00 is exactly the 09:32 close. You are right about that. The 10:16
bar matches the owner's $3.49 fill exactly. Your $3.03 does not appear on this
tape. Use $3.15 and the card error becomes +27%, not +32%.

**Detail 2. The mechanism is not "the first print".** It is worse and it is
structural.

```
entry_mark        = 4.0
entry_mark_asof   = None
entry_mark_source = 'day_close'
entry_mark_stale  = False
```

`_fetch_entry_mark` prefers `last_trade`, then falls back to `day.close`. **On
this Polygon plan `last_trade` is not entitled.** It was absent on **32 of 32**
picks that ever carried an entry mark. Three consequences follow, and all three
apply to every card the engine has sent.

1. **The "@9:50 ET" label is a hardcoded constant.** The code set
   `asof_label = "9:50 ET"` and only overwrote it from a last-trade timestamp
   that never arrives. The card asserted a measurement time on 32 of 32 picks
   and measured it zero times.
2. **The staleness flag was unreachable.** `stale` came from the last-trade age
   only. On the `day_close` path it was False by construction. The guard that
   exists to protect this number has never fired and could not fire.
3. **A prior session's close could become an entry mark.** `day.close` had no
   date validation. This is the GAP-018 defect class, one function over. The
   2026-08-07 follow-on audit scoped to readers of `day.volume`, so it never
   looked here.

**The size of it.** We compared the published `entry_mark` against the engine's
own 10:00 ET entry basis, `opp_entry_price`, on all 27 picks where both exist:

| measure | value |
|---|---|
| median absolute error | **16.2%** |
| mean absolute error | **28.4%** |
| picks off by more than 10% | **18 of 27** |
| picks off by more than 20% | **12 of 27** |
| largest error | 186.7% (V, 2026-07-02, card $4.62 against $1.61) |
| mean signed error | +7.8% |

The error is not a constant offset. The mean signed error is near zero and the
sign flips both ways. No calibration constant can remove it.

**Why this matters more than the number.** `ENTRY_LIMIT_BUFFER` is 2% and
`ENTRY_CHASE_CAP` is 8%. **The do-not-chase rail is smaller than the median
error of the mark it caps.** The rail cannot do its job.

Your reading of the stop is the same point from the other side, and we can put a
number on it. A -30% stop off a mark that is 27% high sits at about -11% from
the real price. Same-day touch rates on this pool, N=2,112:

| stop level | touched same-day |
|---|---|
| -30% (what the card intends) | **19.4%** |
| -11% (where it actually sits) | **50.0%** |

**The mark error turns a 1-in-5 stop-out into a coin flip.** That is the dollar
cost of P3, stated in the only unit that matters.

One correction to your reasoning here. You cited a median adverse excursion of
about -36%. That is the **3-day** figure, and we confirm it at -36.3%. The live
policy exits the same day, and the same-day median is **-11.0%**. This is the
same window mismatch that produced your P5 ask. Please check the window before
you quote an excursion number to us.

Caveat we owe you: `opp_entry_price` includes 2% entry slippage. Remove it and
every error above moves about 2 points more positive. The conclusion does not
move.

### What we changed

`signal-notifier/main.py`, display path only. No selection input changes.

- `_fetch_entry_mark` now date-validates the day bar with the existing
  `_day_bar_et_date` helper.
  - Bar dated today: serve it, and publish the bar's **real** timestamp.
  - Bar dated earlier: **refuse**. `source="stale_day_bar"`, price None, and
    the whole bracket goes null. A wrong mark is worse than no mark, because the
    operator places orders against the derived numbers.
  - Undatable bar: serve the price, but force `stale=True`. Fail open on the
    value. Fail closed on the confidence claim.
- One read clock for the whole function. Date validation and staleness now use
  the same injectable clock, so a replay is reproducible. This follows the
  2026-08-07 review precedent.
- `_entry_display_strings` no longer hardcodes a time. An unknown time renders
  as `time unknown`, next to the existing `(stale)` tag.

10 new tests in `signal-notifier/tests/test_entry_mark.py`. Full suite is 101
passed.

**Not deployed.** This changes what the operator sees on a live-money surface.
It needs `gammarips-review` and the owner.

**What it does not fix.** The mark is still a delayed day-bar close, so it is
still about 15 minutes old on a good day. Only P1 fixes that. This change stops
the card from lying about which number it is and when it was taken.

## P4: shipped 2026-08-07, verified live today

`signal-notifier-00058-fl2` carries the fix:

```
PRINT_VALID_AFTER_ET_MIN = 590
PRINT_BAR_MAX_AGE_DAYS   = 10
```

Both are the GAP-018 date-validation knobs. They cannot be present unless the
fix is deployed.

Your evidence pointed at the pool, not the slate. 16 of 50 stale bars in
`pool_liquidity_snapshot` is the substrate working as designed.
`pool_liquidity.py` persists `day_volume` and `day_last_updated` together, on
purpose, so staleness stays visible downstream. Stale bars in the pool are the
fix working, not the fix missing.

On the HPE line specifically, "(confirmed)" earned it. The pick doc records
`day_bar_stale = False` and `early_volume = 1102`. The real tape shows about
1,136 contracts by 09:37 ET. The count was true and date-validated.

**But your instinct paid off.** You smelled a stale bar reaching a
subscriber-facing number. It does. It reaches the entry mark, not the print
count. We found P3 because you pushed on P4.

## P5: refuted under the live policy. The card is already at the maximum

Your arithmetic is correct. We reproduced your table exactly, including every
`p_touch` and every `day_of_peak` bucket.

Your table describes a **3 trading day** window. **The live policy is V7.1 GIGO,
which exits the same day at 15:45 ET.** You identified this yourself in limit 3.
Then the ask did not follow the limit.

We computed the same-day curve directly from `option_minute_paths`. Entry is the
10:00 ET basis. The window ends at 15:45 ET on the entry day. N=2,112, delta
0.35 to 0.65.

| target | p(touch) same-day | touch EV |
|---|---|---|
| +20% | 20.64% | 0.0413 |
| +30% | 12.03% | 0.0361 |
| +40% | 7.43% | 0.0297 |
| +50% | 4.36% | 0.0218 |
| +60% | 2.70% | 0.0162 |

**The curve does not turn over at +50%. It falls from the start.** The turnover
you found is an artifact of the 3-day window. Median same-day peak is +3.8%,
against +21.4% over three days.

Now the full bracket, with the loss branch and the real 15:45 ET timeout exit.
Pessimistic tie rule, stop first in a shared bar.

| target | p_target | p_stop | p_timeout | EV per $1 |
|---|---|---|---|---|
| +30% | 11.79% | 19.03% | 69.18% | -4.10% |
| **+40%** | 7.29% | 19.27% | 73.44% | **-4.02%** |
| +50% | 4.26% | 19.37% | 76.37% | -4.12% |
| +60% | 2.60% | 19.37% | 78.03% | -4.24% |

**+40% is the maximum. The card already sits on it.** Your move to +50% costs EV
instead of adding it.

Paired test on identical rows, +50% against +40%:

```
EV difference  -0.0010
standard error  0.0011
t              -0.88
```

Not significant. **The honest statement is that no target between +30% and +60%
is distinguishable from another on this evidence.** There is no free 5% of EV in
either direction. This agrees with the standing doctrine that a whole-pool
composite under a fixed exit is negative, and that the edge lives in how a
contract is traded.

One more correction you will want. Do not read same-day touch rates off the
`day_of_peak` day1 bucket. That bucket counts the day of the **window maximum**,
not the day of first touch. At +40% it reports 63 touches. The direct same-day
count is 157. The bucket undercounts by about 2.5 times.

Your two live fills do not change this. N=2 on a 3-day-shaped decision cannot
move a same-day curve with N=2,112.

## What we need from you

1. **Keep pulling the Robinhood book.** That series remains the only real
   measurement of spread and dollar depth, and it is what will price the quote
   entitlement decision. The standing ask from 2026-08-12 is unchanged.
2. **Send us your `carried_mark` classifier.** Your bar-equality rule works on a
   feed that carries marks forward. Ours cannot see that. We want your rule
   before we build the live classifier.
3. **Re-derive and resend.** You told us your scorers graded on the entry
   session. We are holding every harness finding that rests on a same-session
   winner count until you resend. Tell us which ones survive.

## Open items this response creates

- **MCP `open_past_due` needs a fill-cron allowance.** Separate repo, own review
  gate. It currently emits a false stall verdict for 17.5 hours of every
  weekday, to paying subscribers.
- **P1 live 10:00 pass.** Design accepted. Owner call on the Polygon cost.
- **P3 deploy.** Needs `gammarips-review` and the owner.
- **Audit the remaining readers of snapshot `day.*` fields.** The 2026-08-07
  audit scoped to `day.volume`. `day.close` was the second one and it was live
  for six weeks. Assume there is a third until someone checks.
