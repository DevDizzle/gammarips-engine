# GTM: "How to trade options with <client>" video series

Status: PLAN (2026-08-15). Owner records, Gemini edits. Companion to
`docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md` (episode E1, the full spec) and
`docs/GTM-CLIENT-CONNECT-MATRIX.md` (the facts each episode must state).
Destination: YouTube (the channel is the series), one embed per guide (plan
Workstream B), X pin for E1, the Show HN thread for E1.

## Why a series

Search Console shows zero impressions on assistant names today. The intent
"how to trade options with <client>" is unserved. One episode per client
matches one guide per client, so each intent gets a page and a video that
point at the same repo and the same site. Six short videos beat one long
one: each ranks on its own phrase, and each Short is its own hook.

## Episode order and the pro truth each one must say

| # | Client | Paid loop on screen? | The one honest line |
|---|---|---|---|
| E1 | Claude Code | yes, full `/trade` via the harness | "The harness is free. The data is what costs money." |
| E2 | Grok | free tier only unless the owner's UI test finds a header field | "Grok reads the free tier today. The paid tools need a key that Grok's connector dialog does not take yet." (or the verified line) |
| E3 | Codex | yes, via `config.toml` `bearer_token_env_var` and the harness `AGENTS.md` | same as E1 |
| E4 | Claude (claude.ai / Desktop) | yes, via OAuth sign-in on `/pro`, once that flow is verified in this client | "Add /pro as a connector, sign in once, and the paid tools work in the chat." (use the verified flow) |
| E5 | ChatGPT | yes, via OAuth sign-in on `/pro`, once that flow is verified in this client | "Sign in with OAuth and the paid tools work inside ChatGPT." (use the verified flow) |
| E6 | Cursor | yes | same as E1 |

OAuth `/pro` shipped 2026-08-19 (plan D4). Record E5 after one real
ChatGPT OAuth sign-in is verified against the live `/pro` endpoint.
The same verification rule applies to E4 for claude.ai.
E2 waits on the owner's five-minute UI test.

## Episode template (4 to 8 min, one take where possible)

1. Cold open in the client, nothing connected. Say the client's name in
   the first sentence (the title phrase).
2. Honesty beat, 20 seconds: no picks, no win rate, paper-trading data,
   educational, not investment advice, the whole pool under one fixed
   exit is negative and we publish that.
3. Free connect, typed live: the exact steps from the matrix. Then ask
   for the morning brief on the anonymous tier. Real data lands before
   any mention of paying.
4. The paid boundary, said plainly, with the client's honest line from
   the table.
5. The loop. CLI clients: `/trade` in the harness (Claude Code, Codex)
   or the same steps by hand (Cursor). Chat clients: ask the agent to
   grade tradeability, check liquidity, replay similar setups, and
   reason to its own candidates or to none.
6. The critical beat: the agent declines most of the pool. "That is the
   job. Your agent will land somewhere else. That is why there is no
   pick endpoint."
7. Close: repo first, site second, `/agent` as proof once it is live,
   Agent Access $39/mo with a 7-day trial for the CLI clients only.
   Verbal and on-screen disclosure repeat.

Cut a 60 to 90 second vertical Short from steps 3 and 6 for each episode.

## Rails (the eight from the E1 spec, restated once)

1. No expected return, win rate, or profit promise. 2. No picks; the
agent reaches its own conclusion and the narration says so; the operator's
private selection never appears. 3. No timing advantage or "edge" as a
guarantee. 4. State the negative whole-pool composite. 5. Paper-trading /
educational / not-investment-advice: verbal in the intro, lower-third in
any performance-adjacent segment, in the description. 6. No aggregate
live-cohort performance marketing under 30 closed trades. 7. No em dashes
in title, description, on-screen text, thumbnail. 8. Facts that must be
right: 9 MCP tools, `https://mcp.gammarips.com/mcp`, free web UI, Agent
Access $39/mo with a 7-day trial, and the client's connect facts from the
matrix.

## Packaging per episode

- Title: "How to Trade Options with <Client> (AI agent + real options
  flow)". No em dashes.
- Description order: harness repo link first, site link second with
  `utm_source=youtube&utm_medium=video&utm_campaign=howto_<client>`, the
  matching guide URL, tool list and endpoint, the disclosure paragraph,
  chapters (the seven template steps).
- Pinned comment: the free connect command or steps for that client.
- Thumbnail: the client's screen mid-run, plain claim, no money imagery.
- Fresh demo API key for any episode that shows the paid tier; revoke
  after the shoot. Never the owner's real key. Blur or skip anything that
  shows the private selection or the operator email.

## Production checklist per episode

- [ ] Facts re-checked against `GTM-CLIENT-CONNECT-MATRIX.md` that week.
- [ ] Script pass through the webapp `gammarips-copywriter` agent.
- [ ] Recorded on a day with a real pool. "Nothing today" ships.
- [ ] Demo key minted, then revoked after the shoot.
- [ ] Description and pinned comment through `/ship` (public copy).
- [ ] Guide updated with the embed the same day. GA4 `utm_source=youtube`
      confirmed on the first click.
- [ ] Measure: retention, CTR, GA4 youtube-source sessions, `begin_checkout`
      from youtube by campaign. This is the organic CVR baseline the ads
      review (~09-01) waits on.
