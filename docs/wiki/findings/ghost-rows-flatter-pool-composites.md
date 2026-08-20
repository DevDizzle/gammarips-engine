Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: same-day V7.1 GIGO labels (10:00 entry / +40% TP / −30% stop / 15:45 flat)
Source: FINDINGS_LEDGER §2026-08-19 (tradeable subset)
Date: 2026-08-19

# Ghost rows flatter every whole-pool composite

Ghost rows (2 or fewer prints by 10:00 ET, 62.7% of the pool) exit at fabricated
near-flat marks. **16.8% of all closed V7.1 rows carry the EXACT no-move return of
−1.9608%** (= 1/1.02 − 1, the exit filling at the entry bar's own close because nothing
printed in between). On a ghost the bracket essentially never fires (the STOP fires on
8.8% of 0-2-print rows against 35.8% of tradeable rows), so the row records the absence
of a trade, not performance.

Consequence, measured on N=3,776 closed labels over 87 days (2026-04-10 to 2026-08-17):
the whole-pool composite reads **−4.67%** while the tradeable-only (11+ prints) truth is
**−9.59%**, and the gradient by print tier is monotonic in that direction. **Every
whole-pool performance number this program has published is optimistic by construction.**

`illiquid_exit` does not clean it: the production flag catches only 37% of ghosts and the
gradient survives deleting every flagged row. Filter on the tape (prints by 10:00), never
on the flag. Never quote a whole-pool composite without the tradeable split.
[[fixed-exit-composites-negative]] holds on both denominators;
[[execution-risk-is-exit-certainty]] carries the tradeability mapping.
