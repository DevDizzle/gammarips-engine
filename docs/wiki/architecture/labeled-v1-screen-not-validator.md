Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a (data-provenance rule)
Source: INTELLIGENCE_BRIEF hard constraints; FINDINGS_LEDGER §Bootstrap Validation (filt_rrr autopsy)
Date: 2026-07-17

# signals_labeled_v1 is a screen, not a validator (and it is frozen)

`signals_labeled_v1` is the canonical FROZEN research cohort (N=1,563 tradable), but it sits
entirely inside the Feb–Apr 2026 Iran-shock / record-VRP regime. It is useful for **killing
bad ideas cheaply** (negative-EV on a long-options-graveyard regime ⇒ almost certainly
garbage) but NOT for **confirming good ones** (positive-EV could be a regime artifact).

The canonical cautionary tale is the `filt_rrr` autopsy: +8.28% OOS on labeled_v1 →
collapses to −3.37% on its own training set and the entire lift traces to the Mar 26–Apr 6
V-bottom. Any filter/feature search on this cohort MUST end with a bootstrap CI +
walk-forward halving check. Also: `signals_labeled_v1` and everything in `scripts/research/`
are FROZEN for reproducibility — never rebuild or re-label them; new research writes against
the live `forward_paper_ledger` / `enriched_option_outcomes`, not this cohort. Related:
[[dataset-regime-confounded]], [[premium-score-anti-predictive]].
