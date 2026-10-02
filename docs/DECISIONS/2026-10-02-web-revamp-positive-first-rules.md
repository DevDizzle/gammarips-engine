# 2026-10-02: Web revamp rules: positive first, real results with N

**Status:** DECIDED. Owner call 2026-10-02. He approved the numbers table and
each rule change one by one. Do not re-open unless the owner asks.

## Decision

gammarips.com sells subscriptions. Each marketing page leads with the value and
the numbers that show it. The research caveats stay on /methodology and /lab.

The owner approved these changes to the webapp `CLAUDE.md` and to
`.claude/agents/gammarips-copywriter.md`:

- **Voice.** Confident, positive, receipts-forward. The old rule "say the
  uncomfortable true thing before the flattering one" is deleted.
- **Positioning.** Better-quality contracts every night, the exit lab, and the
  user's AI builds the trade plan, in Claude, ChatGPT, Cursor, and Codex. "Data,
  not advice" stays in the disclaimer and the FAQ. It is not a headline.
- **Forbidden claims.**
  1. Real results can appear with N, window, and the disclaimer. A touch is
     "hit +50% within 3 trading days", never profit kept. No return or win-rate
     promise for the user's own trades.
  2. No pick, no signal to follow, no trade to copy. Substance unchanged.
  3. No guarantee, no "insider", no timing-advantage claim. Unchanged.
  4. Complete cohorts only. The whole-pool fixed-exit composite moves to
     /methodology. It is not a marketing duty.
  5. The disclaimer goes in each page section that shows a performance number,
     the homepage hero included. The 2026-08-08 meta-description ruling stays.
  6. The 30-trade floor for live-record marketing is deleted. The live record
     shows from trade 1.
- **Unchanged.** Do not claim the pool returns more than other contracts. This
  is the same rule as the MCP start-here.

## The approved numbers

The homepage first screen uses the first three. Every site number comes from
this table.

| Number | Meaning | Source | N | Window |
|---|---|---|---|---|
| 11 of 14, +$2,263 | Real-money trades that closed at a profit, net realized P&L | gammarips-trader `scripts/tally.py --account LIVE` (account 820865996) | 14 | entries 2026-09-14 to 2026-10-02 |
| 34.5% (about 1 in 3) | Pool contracts that hit +50% within 3 trading days | BigQuery, the MCP `query_outcomes(view="harvest")` query | 1,150 | scan dates 2026-08-24 to 2026-09-28 |
| 4,664 vs 906 | Median open interest of the pool contract, after vs before the liquidity rule | BigQuery `overnight_signals_enriched`, BULLISH, `recommended_oi` | 1,300 vs 3,501 | 2026-08-24 to 2026-10-01 vs the 60 scan days 2026-05-27 to 2026-08-21 |
| 52.8% / 15.9% | Hit +25% / +100% within 3 trading days | as the +50% row | 1,150 | as the +50% row |
| 1,039 vs 232 | Median session volume, after vs before | as the open-interest row, `recommended_volume` | 1,300 vs 3,501 | as the open-interest row |
| 1,635 vs 29 | Open interest of the thinnest 10% | as the open-interest row, p10 | 1,300 vs 3,501 | as the open-interest row |
| 40.5% to 6.1% | No print at the 10:00 ET entry. A study, not a live number | `FINDINGS_LEDGER.md` §2026-08-22 | 3,190 vs 545 legs | 60 sessions ending 2026-08-14 |

Context for the exit lab: 74.1% of the same 1,150 contracts also touched −30%
in the window. Most contracts touch both sides, so the exit plan decides the
result. The live record also has these facts: 10 of 14 trades closed at the
agent's pre-set target, and 8 of 14 were NVDA calls.

The MCP text said "893 / 233 / 86" for the pre-rule baseline. That window was
not recorded and the numbers do not reproduce. The owner chose the reproducible
906 / 232 / 29. The MCP text changes to match.

## Why

The owner, 2026-10-02: "We want to optimize this for selling subscriptions, not
some morally superior bullshit." Also: "We have had great success trading. Look
at our record." The goal is 100 paid subscribers by the end of 2026. An agent
reads our text literally, so a negative headline becomes its answer.

## Records not used on the site

- The agent paper book, 2026-08-25 to 2026-09-15: 14 trades, 10 wins, of record
  +$2,061 to +$2,145 (modelled).
- The owner's manual trades, 2026-07-31 to 2026-08-14 (the manual account): 12
  scored of 15, 5 wins, −$1,412. They come before the agent and before the
  liquidity rule.
