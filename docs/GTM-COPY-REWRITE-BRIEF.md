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

Two honesty points that are strengths, not caveats. The cap of 50 currently does
not bind, so the pool is simply every bullish name in the top-100 liquid
universe: there is no hidden ranking deciding membership. And we surface the most
liquid NAMES, then choose a contract inside each. Not the most liquid contracts
in the market, which would be SPY and QQQ every day.

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

**3. MCP (`gammarips-mcp`).** Tool descriptions and the `get_playbook` text.
Read that repo's `CLAUDE.md` + `SECURITY.md` before touching it.

**4. Poster prompts.** `x-poster/` and `blog-generator/` prompt templates in this
repo, both vendoring `libs/gammarips_content`.

The honest replacement for the HN opener follows the same shape as the site:
name the universe, name the liquidity rule, say plainly that there is no edge
claim and that the value is contracts the agent can actually fill.

## Process

1. Read `../gammarips-webapp/CLAUDE.md` first. Its rules do not auto-load from
   this repo.
2. Branch. Pushing to `main` auto-deploys production.
3. Copy goes through the `gammarips-copywriter` agent.
4. Gate public surfaces with `/ship` from `~/workspace`. That gate is never
   self-waived.
5. Engine and webapp are separate repos. Separate commits, separate pushes.
