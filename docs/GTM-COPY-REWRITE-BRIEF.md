# Copy rewrite brief — the funnel changed, so the story must change

**Written 2026-08-24, after the liquid-universe funnel shipped. This is a
positioning spec, not copy.** It tells the next session what is true, what may
be claimed, and what may never be claimed. The copy itself gets written in the
`gammarips-webapp` repo, through its `gammarips-copywriter` agent, and ships
with `/ship` from `~/workspace`.

## Why this is not optional

The current site describes a market-wide unusual-activity scan that surfaces the
best candidates. **Both halves are now false.**

- The scan no longer selects on unusual activity. It selects the 100 most liquid
  names and drops the $500K UOA floor
  (`docs/DECISIONS/2026-08-24-liquid-universe-funnel.md`).
- "Best candidates" implies a selection edge. Two pre-registered studies on
  2026-08-22 found none ([[selection-research-closed]],
  [[liquid-universe-uoa-null]]).

This is a factual correction, not a refresh.

## The shift, in one line

**Before:** we find the unusual flow and surface the best candidates.
**After:** we do not pick winners. We hand your agent a pool of contracts it can
actually trade.

## The word to change

The owner's framing was "the best chance at making a profit". Do not ship that
word. "Chance at profit" is a probability-of-return claim and it hits forbidden
claim 1, and it drifts toward 3.

We have no evidence that returns improve. The whole-pool composite under a fixed
exit is negative and we publish that. What we measured is **execution**, not
profit.

- Say: your agent can get in and out at the price it sees.
- Say: we remove the contracts you cannot trade.
- Do NOT say: better chance of profit, improves your returns,
  higher-probability setups, better opportunities, best candidates.

The distinction is the whole product. Execution quality is measured and
defensible. Profit probability is neither.

## The value proposition, three parts

Each part carries its own evidence. Copy must not blend them.

**1. Executability. The only measured improvement.**
The old funnel selected contracts that were HARDER to trade than random liquid
ones. It chased unusual volume, and unusual volume in a thin name is one large
print, not a market you can exit.

| | old funnel | liquid universe |
|---|---|---|
| no fill at 10:00 ET | 40.5% | 6.1% |
| tradeable by 10:00 ET | 17.9% | 63.1% |

Conditions that must travel with those numbers: 60 trading days ending
2026-08-14, minute-path tape, a real print in the [09:55, 10:15] window, study
Arms A and B. Source: `FINDINGS_LEDGER.md` §2026-08-22 (liquid-universe funnel).

**These are study numbers, not live results.** The funnel went live 2026-08-24
and has not been forward-validated. Copy may say the funnel was measured at
these rates on that window. Copy may NOT say "our pool fills 94% of the time" as
a live property. The study's own grading rule: promising, forward-validate,
never proven.

**2. The rule is stateable and reproducible.**
A buyer can restate the whole selection rule in one breath, which is rare in this
category and worth saying plainly:

3,532 optionable names -> traded 3M+ shares that session -> chain carries 25+
listed strikes -> top 100 by `z(chain dollar volume) + z(share volume)` ->
bullish names only -> one out-of-the-money call each, chosen on contract
liquidity.

Two honesty points that are strengths, not caveats.

**CORRECTED 2026-08-26 (claim-skeptic audit against the live pool).** The
paragraph below originally said the cap of 50 does not bind. That came from the
2026-08-24 partial-session dry run, and it is FALSE on full-session scans: on
scan_date 2026-08-25, 79 bullish names cleared the floor and `_edge_select_top_n`
(delta band, mom_60, liquidity demotion; `ENRICH_TOP_N=50`) cut them to 50. The
cap binds most days. Never ship "the cap does not bind" or "no hidden ranking".
The honest line: every bullish name in the top-100 is eligible, most days more
than 50 qualify, and a published deterministic point-in-time rank keeps 50,
using no outcome data. The second point stands: we surface the most liquid
NAMES, then choose a contract inside each. Not the most liquid contracts in the
market, which would be SPY and QQQ every day.

**3. The work, and the honest history.**
Every night we price full option chains across the liquid universe and reduce it
to a pool of roughly 40 to 50. We publish the opportunity surface (realized MFE
and MAE) and the outcome history, losers included. Prior whole-pool numbers were
flattered by rows nobody could trade, we found that ourselves, and we removed
them ([[ghost-rows-flatter-pool-composites]]). Say the uncomfortable true thing
first. That is the voice and it is also the differentiator.

## Who the buyer is

An agent-harness trader (Claude Code, Desktop, Codex, any MCP client). The agent
brings the discretion, which is where profit actually comes from: entry timing
and exit. We bring a clean, fillable, reproducible universe and the historical
surface to reason over. We are a data vendor. There is no pick, anywhere, and
the MCP has no pick-returning endpoint.

## Hard limits (from `gammarips-webapp/CLAUDE.md`, non-negotiable)

1. No expected return, win rate, or profit promise. Research cites N + window +
   conditions.
2. No picks, signals to take, or trades to follow.
3. No timing advantage, no "edge" as a guarantee.
4. The whole-pool composite under a fixed exit is NEGATIVE and we publish it. No
   selected-positive blended ROI.
5. Performance-adjacent surfaces carry the paper-trading and educational
   markers. Homepage meta description stays disclaimer-free: SETTLED, do not
   re-raise.
6. No aggregate live-cohort performance marketing until 30 closed trades.

Add for this rewrite: **do not describe the scan as unusual-activity-driven.**
Flow still orders the pool but no longer decides membership.

## Surfaces to audit — four repos, not one

Anything describing the scan, the funnel, "unusual activity", or how the pool is
built.

**1. Webapp (`gammarips-webapp`).** Homepage, /methodology, /about, /pool,
/reports templates, blog copy that explains the funnel.

**2. Harness (`gammarips-harness`) — HIGHEST URGENCY.**
`docs/HN-SUBMISSION.txt` line 60 opens with "I run an overnight scan of ~5,200
US tickers for unusual options activity, curate it hard down to a small pool".
Every clause of that is now wrong: the universe is 3,532 names, the scan does
not select on unusual activity, and "curate it hard" is the selection-edge story
two studies just killed. **Show HN is scheduled for the week of 08-25, so this
text ships before most of the rewrite.** Fix it first, in the same pass as the
webapp homepage. Also check `README.md` and the plugin description in PR #3
(the plugin name is immutable, the description is not).

**3. MCP (`gammarips-mcp`).** Wider than tool text. Four surfaces, and the
first one is public:
- `README.md` line 7 carries the same dead sentence as the HN text: "scans the
  US options market for unusual institutional activity and curates it hard".
- `skills/gammarips-options-flow/SKILL.md` (the bundled skill description, so it
  ships inside the plugin) and `CURSOR-DIRECTORY-UPDATE.txt` (the directory
  listing).
- Tool descriptions and the `get_playbook` text.
- The playbook files under `content/playbooks/` (see the section below).
Read that repo's `CLAUDE.md` + `SECURITY.md` before touching it.

**4. Poster prompts.** `x-poster/` and `blog-generator/` prompt templates in this
repo, both vendoring `libs/gammarips_content`.

The honest replacement for the HN opener follows the same shape as the site:
name the universe, name the liquidity rule, say plainly that there is no edge
claim and that the value is contracts the agent can actually fill.

## PRIORITY: the MCP ships a moneyness claim it contradicts itself on

Raised by the `gammarips-trader` session on 2026-08-25. I verified it in the MCP
repo. It is a live defect, not a cohort-bound one, and it outranks the
possessive-frame edits below.

`content/playbooks/moneyness-10-15-otm.md` ships the claim "10-15% OTM was the
best moneyness bucket", and `content/playbooks/methodology.md` line 34 tags it
**proven-on-cohort**. Three things are wrong with that.

1. **The MCP contradicts itself.** `src/tools/education.py` line 98 already
   says "the old 5-15% OTM moneyness gate was retired under V6, moneyness is no
   longer a hard selection filter". `content/playbooks/changelog.md` line 62
   says the legacy moneyness gate was retired because it "removed real winners".
   A subscriber can read both surfaces in one session.
2. **This engine has no such note.** There is no
   `docs/wiki/findings/moneyness-10-15-otm.md` here. Our registry carries
   [[moneyness-band-10-13-otm]] and marks the older audit SUPERSEDED. The
   shipped playbook is the only place the 10-15 claim still lives as current.
3. **It was falsified on a larger cohort, with an owner directive.** The trader
   harness re-derived it on 2026-07-17 at n=1,806 labeled rows. The bucket won
   41% against the whole pool's 42%, and the split halves flip sign (+6.3% then
   -9.8%). Owner directive the same day: moneyness is descriptive context only,
   it never filters and never ranks.

The claim has therefore shipped for about five weeks after the measurement that
killed it. Blast radius is currently zero external users, and Show HN ships the
week of 2026-08-25, so fix it before that and not after.

The fix is a retag and a rewrite of the note, not a cohort bound. Do not re-test
it. [[selection-research-closed]] bans the re-test and that ban includes us.

**Do NOT replace 10-15 with 10-13.** Raised by the trader session and it is the
trap next to this one. Our live [[moneyness-band-10-13-otm]] note is real, but it
describes the enrichment FALLBACK path, not a claim about which band a subscriber
should trade. Swapping the number keeps the shape of the defect and ships a
moneyness gate with a fresh figure on it. The MCP's own text already settles this
without any outside evidence: `education.py` says moneyness is no longer a hard
selection filter, and `changelog.md` says the gate was retired for removing real
winners. So the copy rule is band-agnostic. **Moneyness is descriptive context in
the MCP. It never presents as a filter or a rank, at any band.** The trader
harness carries the same rule as an owner directive dated 2026-07-17, scoped to
its own screen. Whether that directive also binds this engine's fallback path is
an open owner question and NOT a copy decision. Do not resolve it in the copy.

**While in `methodology.md`, reframe [[bullish-direction-asymmetry]].** The
funnel is bullish-only, so the pool no longer contains the bearish arm the claim
is built on and the comparison cannot be re-run in-pool at all. It is not
refuted and it is not a selector. State it as the REASON the funnel is
bullish-only. Today it sits next to that funnel and reads as an active edge
claim the funnel has already acted on.

## What the studies do NOT kill: the 3-day harvest curve

Raised by the `gammarips-trader` session on 2026-08-25. It is correct and it
widens this brief.

The two studies are **same-day and comparative**. The harvest curve is **3-day
and absolute**. They do not cancel. P(touch +20% in 3 days) = 51% stays true as
a measured property of the contracts. What the studies kill is the **causal
reading**: that pool MEMBERSHIP produces that rate. Study 2 found the pool
indistinguishable from matched random on the same tape, so the pop belongs to
liquid optionable calls, not to our selection.

Two of our own surfaces state it causally today:
- `gammarips-mcp/content/playbooks/three-day-harvest-curve.md`: "the pool's pop
  is real".
- `gammarips-mcp/content/playbooks/fixed-exit-composites-negative.md`: "the same
  pool's opportunity surface is real".
Also audit `content/playbooks/exit-lab.md`, `content/playbooks/methodology.md`,
`src/tools/education.py`, `src/tools/substrate.py`, and this repo's
`docs/wiki/findings/three-day-harvest-curve.md` plus its `REGISTRY.md` line.

Do not delete the numbers. Two edits to each:
1. Bound the cohort. Every one of these was measured on the pre-2026-08-25 UOA
   pool. `src/tools/education.py` already says "Measured on the Apr-Jun 2026
   pool", which is the model to copy. The others do not.
2. Drop the possessive causal frame. Say the contracts move like this, not that
   the pool makes them move like this. Cite
   [[selection-research-closed]] next to the curve.

This is the same cohort break the trader harness fixed in its own `edge.py` on
2026-08-25. Numbers from the old pool and the new pool are not one population.

**A related audit in the same pass.** The trader session asked whether
`exit-lab.md` and `methodology.md` assert selection as a proven profitability
lever. They do not, and `exit-lab.md` already carries the sentence the rest of
the rewrite should copy: "selection curates *which* fairly-priced contracts you
see. It does not find direction the market missed."

But `content/playbooks/methodology.md` tags three selection-flavored notes
**proven-on-cohort**: [[bullish-direction-asymmetry]] (marked "3-day era"),
[[delta-band-0-20-0-46]] ("the only feature separating winners from losers"),
and [[moneyness-10-15-otm]]. The studies do not refute these, because they
tested the pool against random and never a feature within the pool. Do not
delete them and do not re-test them, because [[selection-research-closed]] bans
new feature searches. Bound their cohort to the pre-2026-08-25 UOA pool, the
same edit as the harvest curve.

## Keep the exit horizon on every number

Raised by the trader session on 2026-08-25, and I audited our side. The engine
exits same-day under V7.1. That harness holds up to 3 sessions. A subscriber's
agent picks its own hold. So a number without its exit horizon is not merely
imprecise, it is unusable, and the same number can be current for one reader and
stale for another.

We mostly do this well. 25 of the 32 files in `gammarips-mcp/content/playbooks/`
carry an `Exit-context:` header. Six of the seven without one are process or
architecture docs with no single horizon, which is correct.

**The exception is `exit-lab.md`, and it is the one that matters.** It is the
playbook entirely about exits, it has no `Exit-context:` header, and its numbered
list mixes three horizons: a 3-trading-day harvest curve (N=2,029), a
peak-to-expiry figure (N=1,303, p90 ≈ +445%), and a retained-at-expiration
giveback. Each is labeled inline, so nothing there is false. But the reader has
to track the horizon per bullet on the one page where confusing them is most
expensive. Give it a header and state the horizon in each numbered item.

A refinement from the trader session that makes this cheaper than it looks. Some
items carry a horizon-free APPLICATION and a horizon-bearing STATISTIC, and only
the statistic needs the label. `exit-lab.md` divides that way. Item 1 ("selection
curates which fairly-priced contracts you see, it does not find direction the
market missed") is a principle that holds under any hold period and needs no
horizon at all. Items 2 to 6 each carry numbers on three different horizons, so
they need per-item labels and a single file header cannot cover them. Split them
that way rather than stamping all six.

Note the axis. This is NOT the cohort bound. A number can sit on the right
population and still describe a hold the reader does not have.

## Process

1. Read `../gammarips-webapp/CLAUDE.md` first. Its rules do not auto-load from
   this repo.
2. Branch. Pushing to `main` auto-deploys production.
3. Copy goes through the `gammarips-copywriter` agent.
4. Gate public surfaces with `/ship` from `~/workspace`. That gate is never
   self-waived.
5. Engine and webapp are separate repos. Separate commits, separate pushes.
