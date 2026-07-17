Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: 3-day +80/−60 bracket era; N=1,375 fills. SUPERSEDED as live policy by same-day GIGO.
Source: INTELLIGENCE_BRIEF 2026-06-02 (H18); backtesting_and_research/exit_design_study.py
Date: 2026-07-17

# The −60% premium stop earned its keep over a 3-day bracket (H18)

H18 (drop the −60% premium stop for a laissez-faire/underlying stop) was TESTED and NOT
SUPPORTED. Re-replaying all 1,375 fills under 4 exit policies: removing the −60% hard stop =
paired mean delta **−0.001 (90% CI [−0.004,+0.003])** — ZERO EV change, just a fatter left
tail (min −0.60 → −0.97). The "premium stop wicks out and bleeds EV" premise is a
HOLD-TO-EXPIRY artifact; over a short bracket the option is down 60% only when the underlying
genuinely failed, so the stop ≈ a time-exit. TIME_ONLY had higher MEAN (+4.5%) but was a
right-tail mirage (lower median, WR 37.5%, −97% losers).

Note the exit-context: this is 3-day-era evidence. The LIVE policy is a same-day −30% stop
([[v7-gigo-same-day-exit]]), chosen because same-day is the real lever
([[exit-velocity-same-day-lever]]) and −30% beats −40% on the tail. The durable takeaway is
mechanistic: a fixed-% premium stop on a SHORT hold behaves like a time-exit, not an EV leak.
