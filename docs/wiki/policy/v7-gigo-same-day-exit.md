Status: active
Type: policy
Tag: policy-adopted
Exit-context: THIS NOTE DEFINES the live exit — same-day GIGO bracket
Source: docs/DECISIONS/2026-06-17-v7-intraday-bracket.md; CLAUDE.md "Current policy"
Date: 2026-07-17

# V7 GIGO exit — same-day get-in-get-out bracket

The live exit (V7, 2026-06-17) is a same-day intraday OCO bracket:
- **Entry: 10:00 ET** on day-1 (see [[entry-1000-et]]).
- **Take-profit: +40%** on option premium (limit).
- **Stop: −30%** on option premium.
- **Time-exit: flat at 15:45 ET the same day**, no trail, no overnight hold.
- On ambiguous intrabar order, resolve **TIMEOUT(15:45) > STOP > TARGET** (conservative).

This SUPERSEDES the V6 exit (−60% stop / +80% target / 3-day hold), which is DEAD. The
lever proven in the exit-velocity sweep was the **same-day exit itself, not the target
magnitude** (~+2.4–2.8%/trade across all H1 targets); same-day frees capital ~2.5× faster
(~3× return-per-capital-day) and halves the disaster tail (−34% vs −61%). The per-trade EV
improvement was NOT significant at the day level (single regime, ~33 days) — the case
rests on velocity + tail reduction. See [[exit-velocity-same-day-lever]].

Consequence for research: any edge cited to justify a live trade must be proven under this
same-day exit-context. Multi-day-hold findings (e.g. [[momentum-60d-enrichment-tilt]]) do
NOT transfer.
