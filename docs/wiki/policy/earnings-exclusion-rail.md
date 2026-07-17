Status: active
Type: policy
Tag: policy-adopted
Exit-context: any hold that spans a scheduled earnings print
Source: docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md; De Silva/Smith/So (2026); Cao & Han (2013)
Date: 2026-07-17

# Safety rail 1 — no earnings in the hold/exclusion window

`signal-notifier` hard-excludes any candidate whose scheduled earnings date falls inside
the hold/exclusion window `[scan_date, entry_day + 2 trading days]`. It walks the top-10
ranked candidates and takes the first non-overlapping ticker; if all 10 overlap, it skips
the day. Fail-closed on calendar-fetch failure or a non-list payload.

This is a **literature-anchored EXCLUSION rule, not a selection gate** — IV inflates into
earnings and crushes immediately after, so a long single-leg option loses even when the
direction is right (De Silva/Smith/So 2026: −5–9%/event, −10–14% on high-vol names; see
[[earnings-iv-crush]]). It is deliberately NOT backtested on our small N — the literature
settled it at scale we cannot match. Trigger: the 2026-05-06 CDW pick, dead on arrival on
an earnings gap. It is one of exactly two safety rails kept in the notifier
([[regime-rail-vix-term]] is the other); everything else was removed
([[selection-gates-removed]]).
