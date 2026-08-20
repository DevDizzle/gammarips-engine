Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: V7.1 GIGO bracket vs PM-entry/overnight variants; ENTRY-KNOWABLE tradeable tier
Source: FINDINGS_LEDGER §2026-08-19 (PM entry)
Date: 2026-08-19

# Overnight holds break the stop: PM entry / "morning pop" REFUTED

The hypothesis (enter in the afternoon, catch the next-morning pop) fails twice over on
the enriched-pool minute tape (4,292 legs, 87 days):

- **The morning pop does not exist where you can trade.** The whole-set morning mean
  (+8.19%) is two penny options; the median morning move is exactly 0.00%. On liquid
  contracts both the overnight gap (−4.4%) and the first half-hour (−3.6%) are NEGATIVE.
  Same thin-tape mirage the 2026-06-22 entry study found ([[entry-1000-et]]).
- **The overnight hold removes the stop.** Options do not trade overnight, so the stop
  cannot execute in the gap. On the entry-knowable tradeable tier the live arm's p05 is
  −31.4% (the −30% stop IS the floor) while every overnight arm prints p05 near −53%.
  The tail deepens by about 22 percentage points.

Every liquid-tier PM variant is negative (ENTRY-KNOWABLE n=168: PM → day-2 15:45 reads
−8.25% [−17.0, −0.2]). The cleanest signal is the control arm, which keeps the 10:00
entry and changes ONLY the hold: −4.87% [−8.7, −1.4], CI excludes zero. **The damage is
the overnight hold, not the entry time.** This independently re-confirms the same-day
exit ([[v7-gigo-same-day-exit]]) on a substrate and a question that lever's own study
never touched. Do not move the entry to the afternoon. Do not hold overnight.
