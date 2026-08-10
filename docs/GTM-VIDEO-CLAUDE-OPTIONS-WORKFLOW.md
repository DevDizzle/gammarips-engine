# GTM: "How to Trade Options Using Claude" video

Status: DRAFT v1 (2026-08-06). Owner records; this doc is the outline, script
skeleton, and compliance rails. Companion to `docs/GTM-MCP-DIRECTORY-PLAN.md`.
Destination: YouTube (primary) + iframe embed on the webapp `landing/video-led`
branch (already READY, waiting on this video) + X pin.

## Why this video, in one paragraph

"How to trade options using Claude" and its query cluster (Claude MCP trading,
AI agent options trading, connect Claude to market data) have real search intent
and almost no supply. The video demos the exact monetized product (MCP access,
$39/mo Agent Access) end to end, feeds the organic CVR baseline the ads decision
is gated on, and builds the agentic-trading category we claim as our hero angle.

## Compliance rails (non-negotiable, from webapp forbidden-claims list)

Every scene must pass these. The webapp `gammarips-copywriter` agent reviews the
final script before recording; any on-site copy for the embed goes through `/ship`.

1. No stated or implied expected return, win rate, or profit promise. Research
   numbers only with N + window + conditions, framed as research.
2. No picks. Never show or imply "the trade to take." The agent on screen reaches
   its OWN conclusion and the narration says so explicitly. The operator's private
   tournament pick never appears (it is not in the MCP; keep it that way on screen).
3. No timing advantage, no "edge" as guarantee, nothing insider-flavored.
4. State the uncomfortable truth: the whole pool under one fixed mechanical exit
   is NEGATIVE. That honesty IS the differentiator and the reason agent-side
   reasoning matters. Never a selected-positive blended ROI.
5. Paper-trading / educational / not-investment-advice disclosure: verbal in the
   intro, on-screen lower-third during any performance-adjacent segment, and in
   the video description.
6. No aggregate live-cohort performance marketing (under 30 closed trades).
7. No em dashes in any public-facing text: title, description, on-screen text,
   thumbnail. (Workspace hard rule.)
8. Facts that must be right: 9 MCP tools, endpoint `https://mcp.gammarips.com/mcp`,
   free web UI, Agent Access $39/mo with 7-day trial.

## Format

- Main video: 8 to 12 minutes, screen recording of a real Claude session with the
  GammaRips MCP connected, owner voiceover. Dry, receipts-forward, zero hype.
- Cut a 60 to 90 second vertical Short from Act 3 (the agent reasoning beat).
- Thumbnail: terminal/Claude UI screenshot, plain claim ("I gave Claude my
  options data. Here is what it did."), no rockets, no money imagery.

## Script skeleton

### Act 1: Hook + honest framing (0:00 to 1:00)
- Cold open on a live Claude session already mid-analysis. 5 seconds.
- Hook line (draft): "This is Claude reading last night's unusual options
  activity and deciding, on its own, whether anything is worth trading today."
- Immediately the honesty beat: "First, what this is not. Nobody here is
  selling you picks or a win rate. This is a data pipeline and an AI agent that
  reasons over it. Paper-trading data, educational, not investment advice."
- One-line product frame: free website for humans, MCP server for agents.

### Act 2: Setup (1:00 to 3:00)
- What MCP is in one sentence (a standard port for plugging tools into Claude).
- Live: connect the server. Show both paths on screen:
  - Claude Code: `claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp`
  - claude.ai custom connector (Settings > Connectors) for non-CLI users.
- Show the 9 tools appearing. Name a few: get_pool, get_liquidity,
  replay_contract, query_outcomes, get_playbook.
- Note the free/pro split honestly: 5 tools free, 4 pro, trial exists.

### Act 3: The workflow, agent-driven (3:00 to 8:00) THE CORE
Narrate what the ENGINE did overnight (scan 5,230+ tickers, score, curate to a
small bullish pool, two safety rails), then hand the wheel to Claude. Show a
real prompt that models correct use, for example:

    "Pull today's pool and the regime context. For anything that interests
    you, check liquidity and replay how similar contracts actually moved.
    Then tell me if YOU would trade any of these, at what terms, and what
    would make you walk away. Assume I will disagree with you."

- Let the agent visibly call: get_market_calendar_status, get_regime_context,
  get_pool, get_liquidity on 1 or 2 names, replay_contract, query_outcomes,
  get_playbook.
- Critical beat: the agent declines some or most of the pool, sets its own
  entry/exit logic, maybe concludes "nothing today." Keep that take. The
  narration underlines it: "Different agent, different prompt, different
  conclusion. That is the point. This is data, not a signal to follow."
- Honesty beat #2 (lower-third disclosure on screen): "If you traded the whole
  pool mechanically under one fixed exit, you would lose money. We publish
  that. The opportunity surface is real; capturing it depends on how each
  contract is traded, which is exactly the part the agent owns."

### Act 4: Close (8:00 to end)
- Recap in two sentences. What the engine curates, what the agent decides.
- CTA, in this order: the website is free (pool, research Lab, methodology);
  if you want your agent plugged in, Agent Access is $39/mo with a 7-day trial.
- Verbal + on-screen disclosure repeat. End card: gammarips.com.

## SEO packaging (draft, copywriter pass required)

- Title candidates (no em dashes):
  1. "How to Trade Options Using Claude (Full AI Agent Workflow)"
  2. "I Connected Claude to Live Options Flow Data. Here Is the Full Workflow."
- Description skeleton: what happens in the video, tool list, endpoint, free
  site link with UTM (`utm_source=youtube&utm_medium=video&utm_campaign=claude_workflow`),
  disclosures paragraph, timestamped chapters matching the four acts.
- Chapters double as the Short cut points.

## Production checklist

- [ ] Script final pass through webapp `gammarips-copywriter` (compliance + voice)
- [ ] Fresh demo account + demo API key for recording; REVOKE the key after the
      shoot (it will be on video). Never the owner's real key.
- [ ] Record on a day with a real pool; a "nothing today" outcome is acceptable
      and on-message if it happens.
- [ ] Blur/skip anything showing the private tournament pick or operator email.
- [ ] UTM links in description; confirm GA4 picks up `utm_source=youtube`.
- [ ] After publish: iframe swap on `landing/video-led`, then `/ship` from
      workspace root; X unpin 03-14 post, pin this.
- [ ] Measure: YouTube CTR/retention, GA4 youtube-source sessions, begin_checkout
      from youtube source. This traffic is the organic CVR baseline the ads
      decision (memory `owner-goal-100-paid-subs-eoy2026`) is waiting on.
