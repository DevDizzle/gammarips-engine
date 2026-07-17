Status: active
Type: policy
Tag: policy-adopted
Exit-context: n/a (delivery display, not selection or execution)
Source: docs/DECISIONS/2026-06-30-entry-day-mark-and-limit.md
Date: 2026-07-17

# Published pick shows a FRESH entry-day mark + fair-value limit (display, not selection)

After the tournament has ALREADY picked, `signal-notifier` fetches a fresh entry-day
(~09:50 ET) price for the CHOSEN contract only and publishes on `todays_pick`:
`entry_mark` (+ asof/source/stale), `limit_entry_price` = mark × (1 + `ENTRY_LIMIT_BUFFER`,
def 2%), `do_not_chase_above` = mark × (1 + `ENTRY_CHASE_CAP`, def 8%), `limit_good_til`
"10:15 ET". This is DISPLAY only — it does not change selection or the trader.

Trigger: the webapp/email had published `recommended_mid_price` (the overnight scan-time
mark); on 2026-06-29 FCEL $27C showed $2.40 while the real entry-day price was $5.10 (weekend
reprice) — an actively misleading entry basis. The operator-display brackets
(`STOP_PCT_DISPLAY`/`TARGET_PCT_DISPLAY`) had also drifted to the retired V6 −60/+80; they
were corrected to the live V7.1 GIGO −30/+40 ([[v7-gigo-same-day-exit]]).
