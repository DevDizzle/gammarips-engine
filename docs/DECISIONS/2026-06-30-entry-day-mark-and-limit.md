# 2026-06-30 — Entry-day mark + fair-value limit (display, not selection)

## Status
Implemented in `signal-notifier/main.py` (Phase A): the Firestore doc fields **and**
the **email + WhatsApp render** (the paid delivery surface). `write_todays_pick_doc`
returns the entry-mark dict from one fetch; `_entry_display_strings` + the two
templates render the fresh Entry/Limit/do-not-chase/Target/Stop, falling back to the
overnight `Mid` line only when the mark is unavailable. **Webapp render is the one
remaining follow-on PR in `gammarips-webapp` (Phase B).** Not yet deployed — passed
`gammarips-review` (leakage/execution) once; re-verified after the render refactor.

## Problem
The webapp/email published `recommended_mid_price` — the **overnight scan-time**
option mark. On 2026-06-29 the FCEL $27C showed **$2.40** while the real entry-day
price was **$5.10** (the contract repriced over the weekend). That number is the
basis a subscriber would set an entry/limit against, so it was actively
misleading — independent of the (future) crowding/limit-order work.

Separately, the operator-display brackets `STOP_PCT_DISPLAY=0.60` /
`TARGET_PCT_DISPLAY=0.80` had **drifted** to the retired V6 3-day −60%/+80%
brackets; the live trader is V7.1 GIGO at **−30%/+40%** (`STOP_PCT=0.30` /
`TARGET_PCT=0.40`). They were dead (unused) but wrong.

## Decision
After the tournament has **already picked**, fetch a **fresh entry-day (~09:50 ET)
price** for the CHOSEN contract only and publish, on the `todays_pick` doc:
- `entry_mark`, `entry_mark_asof`, `entry_mark_source` (`last_trade|day_close|unavailable`), `entry_mark_stale`
- `limit_entry_price` = mark × (1 + `ENTRY_LIMIT_BUFFER`, def 2%), tick-rounded — a marketable fair-value BUY limit
- `do_not_chase_above` = mark × (1 + `ENTRY_CHASE_CAP`, def 8%), tick-rounded — hard "skip if it ran past this"
- `limit_good_til` = "10:15 ET"
- `display_target_price` / `display_stop_price` = mark × +40% / −30% (V7.1 GIGO), and `entry_bracket_basis="live_entry_day_mark"`

`recommended_mid_price` is retained for back-compat but is no longer the displayed entry.

## Why this is leakage-safe (the crux)
The entry-day-live snapshot fields (`last_trade`, `day` OHLC) are **forbidden from
SELECTION** by the C1 wall in `_fetch_live_oi` / `_FORBIDDEN_LIVE_KEYS`, because the
enrichment→tournament→judge pipeline is validated **point-in-time as of scan_date**.
This change uses those same fields **only after the pick is made**, inside
`write_todays_pick_doc(has_pick=True)`, for **display + deterministic limit/bracket
math**. It is a SEPARATE function (`_fetch_entry_mark`) so the OI selection wall
stays bit-identical, and the mark **never re-enters** enrichment/tournament/judge.
Display ≠ selection. (If we ever want fresh data to change *which name* is picked,
that is the 9:30–10:00 entry-window-tape research arc under the `ts ≤ 10:00` rule —
not this change.)

## Scope / non-goals
- **Trader mechanics UNCHANGED.** The paper trader still simulates the 10:00 entry
  and applies its own fill-based −30%/+40% bracket. This is subscriber-facing
  guidance, not a change to what the ledger records. So `TRADING-STRATEGY.md`
  execution policy is untouched.
- No new data vendor (reuses the existing Polygon snapshot). No NBBO on this plan,
  so the mark approximates fair value from the **last printed trade** — the
  buffer/cap are heuristics to revisit when a real quote feed lands.
- Measuring fill-rate / return-conditional-on-fill at the published limit is a
  later **trader** change (Phase C), not in this cut.

## Fail-soft
`_fetch_entry_mark` never raises (mirrors `_fetch_live_oi`). On any failure it
returns `source="unavailable"` and the limit/bracket fields are null — the webapp
shows "live mark unavailable, set your own limit" rather than reverting to the
stale overnight number. One extra ≤8s Polygon call runs before the email send;
it is best-effort and never blocks the pick.

## Env knobs
`ENTRY_MARK_TIMEOUT_S` (8), `ENTRY_LIMIT_BUFFER` (0.02), `ENTRY_CHASE_CAP` (0.08),
`ENTRY_MARK_STALE_SECS` (900).
