# Engine Wiki Schema

`docs/wiki/` is the engine's compiled-knowledge layer (LLM-wiki pattern: sources →
LLM-written notes → registry). **One claim per note. Edit-over-duplicate.** Adopted from
the `gammarips-trader` harness `wiki/_index/WIKI-SCHEMA.md` (2026-07-17 simplification
replan, Plan 3) with two engine-specific note types (`policy`, `architecture`) because
most engine claims are operating rules and data-contract facts, not cohort measurements.

The `docs/DECISIONS/`, `docs/research_reports/INTELLIGENCE_BRIEF.md`, and
`FINDINGS_LEDGER.md` files remain the canonical, detailed provenance. A wiki note is the
one-claim distilled version; it CITES the source doc, it does not replace it.

## Note types (by directory)
- `policy` (`wiki/policy/`) — a live operating/execution rule the engine runs today
  (the V7.1 "Tilted GIGO" policy surface).
- `architecture` (`wiki/architecture/`) — a durable pipeline / data-contract / service
  fact (how the funnel is wired, what a table means, a standing constraint).
- `finding` (`wiki/findings/`) — a claim tested on our own cohorts/ledgers.
- `literature` (`wiki/literature/`) — a claim from external research/practice, not
  tested on our data.

## Required header block (every note)
```
Status: active | superseded
Type: policy | architecture | finding | literature
Tag: policy-adopted | architecture-fact | proven-on-cohort | falsified-on-cohort |
     fragile-conditional | literature-established | untested-hypothesis
Exit-context: <the hold period + exit rule the evidence assumes; "n/a" for
               policy/architecture/concept notes that are exit-agnostic>
Source: <engine doc / DECISIONS file / study / paper>
Date: YYYY-MM-DD
```

**`Exit-context` is the load-bearing field for FINDINGS.** This program's central lesson
is that edges are exit-conditional (mom_60 is real on a 3-day hold and ZERO on same-day
GIGO). A finding cited without its exit context is meaningless. For `policy` and
`architecture` notes that are not about a measured edge, `Exit-context: n/a`.

## Tag semantics
- `policy-adopted` — an operating rule we run right now (often literature-anchored),
  distinct from a measured edge. The live V7.1 surface is almost all this.
- `architecture-fact` — a durable structural/data-contract fact (wiring, table meaning,
  standing constraint). Not an edge claim.
- `proven-on-cohort` — held up on our labeled data with real N; still era-bound (note the
  cohort + exit).
- `falsified-on-cohort` — tested on our data and rejected; anti-edge. Keep active; a
  falsified note is as valuable as a proven one.
- `fragile-conditional` — survived testing only under specific conditions; proposer-only;
  never load-bearing alone.
- `literature-established` — settled in published research; we deliberately did not
  re-test it on our small N.
- `untested-hypothesis` — plausible, not yet tested; never cite as support for a trade.

## Conventions
- Wikilinks: `[[note-slug]]` (slug = filename without `.md`), resolvable across all four
  directories.
- Plain, concrete prose. Numbers with their N and cohort. No hype.
- Every note is registered in `_index/REGISTRY.md` (one line + tag).
- Provenance rule: a note that distills a `docs/DECISIONS/` file MUST cite it by filename
  in `Source:` and MUST NOT alter the decision file. DECISIONS are read-only provenance.

## Firewall
Distillation reads engine research docs (FINDINGS_LEDGER, INTELLIGENCE_BRIEF,
docs/DECISIONS) and external literature. It MUST NOT copy in anything that would leak the
operator's private daily tournament pick or same-day engine state — the wiki is knowledge,
not a data side-channel.
