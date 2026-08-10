# GTM: "How to Trade Options Using Claude" video

Status: **DRAFT v2 (2026-08-08) — CONCEPT CHANGED BY OWNER.** v1 specced an 8-12
minute walkthrough of a Claude session with the MCP attached. v2 is a
**zero-to-contracts install demo**: clone the open-source harness, run the one-line
MCP connect, run `/trade`, and produce contract candidates out of the curated data.
Nothing is pre-set-up on screen. Owner records; this doc is the outline, script
skeleton, and compliance rails. Companion: `docs/GTM-DISTRIBUTION-PLAYBOOK.md`.
Destination: YouTube (primary) + iframe embed on the webapp `landing/video-led`
branch (READY, waiting on this video) + X pin + the Show HN thread.

## Why THIS video, in one paragraph

The thing on screen is the same artifact we submit to HN
(`github.com/DevDizzle/gammarips-harness`), so the video and the launch point at
one destination and a viewer can replicate exactly what they just watched. Going
from an empty directory to contract candidates is the only way to show that the
data is real and the workflow is not a mock. It also demos the monetized product
($39/mo Agent Access) honestly end to end, and it feeds the organic CVR baseline
the ads decision is gated on.

## The one structural rule for v2

**Start from nothing.** No pre-cloned repo, no pre-connected server, no warmed
context. The whole point is that the viewer sees the distance from `git clone` to
a contract candidate and knows it is short. If a step is slow, cut it in the edit,
never fake it in the recording.

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

- Main video: **6 to 10 minutes**, one continuous screen recording from an empty
  directory to contract candidates, owner voiceover. Dry, receipts-forward, no hype.
- Cut a **60 to 90 second vertical Short** from the connect + first output beat.
  That Short is the highest-leverage asset: it is the whole promise in a minute.
- Thumbnail: terminal mid-run, plain claim ("From `git clone` to contract
  candidates"), no rockets, no money imagery.
- Editing: owner is coordinating the cut with Gemini. Keep the raw recording;
  the honest beats below must survive the edit, especially the "nothing today"
  possibility and the paid-tier boundary.

## Script skeleton

### Act 1: Hook + honest framing (0:00 to 0:45)
- Cold open on an EMPTY terminal in an empty directory. That is the hook: nothing
  is set up.
- Hook line (draft): "In the next few minutes I am going to go from an empty folder
  to a set of options contracts my agent picked out of last night's flow. Nothing
  is pre-installed."
- Immediately the honesty beat: "First, what this is not. Nobody is selling you
  picks or a win rate. This is a data pipeline and an AI agent that reasons over
  it. Paper-trading data, educational, not investment advice."
- One-line product frame: free website for humans, MCP server for agents, harness
  is open source.

### Act 2: From nothing to connected (0:45 to 2:30)
- `git clone https://github.com/DevDizzle/gammarips-harness.git` on screen. Real.
- What MCP is, in one sentence (a standard port for plugging tools into an agent).
- The free connect, typed live:
  `claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp`
- Show the tools appearing. Ask for a morning brief on the ANONYMOUS tier so the
  viewer sees real data before any mention of paying. This beat is why the video
  converts: value lands before the ask.
- Then the honest boundary, said plainly: the harness loop needs the paid tools
  (`get_liquidity`, `get_signal`, `query_outcomes`, `replay_contract`), so
  export the demo key. "The harness is free. The data is what costs money."
  **Do not imply the loop runs anonymously. It does not.**

### Act 3: `/trade`, agent-driven (2:30 to 7:00) THE CORE
Narrate what the ENGINE did overnight (scan 5,230+ tickers, score, curate to a
small bullish pool, two safety rails), then run `/trade` and get out of the way.

- Let the agent visibly work: screen the pool, grade tradeability BEFORE thesis,
  check liquidity, replay how similar contracts actually moved, then reason to
  contract candidates with its own entry and exit terms.
- Critical beat, non-negotiable: the agent declines most of the pool, and the
  narration says why that is the product. "It rejected almost everything. That is
  the job. And a different agent with a different objective would land somewhere
  else, which is exactly why there is no pick endpoint to call."
- **If the honest outcome that day is "nothing today," KEEP IT and ship it.** A
  no-trade day is the single most credible thing this video can show, and it is
  on-message. Do not re-record for a prettier outcome.
- Honesty beat #2 (lower-third disclosure on screen): "If you traded the whole
  pool mechanically under one fixed exit, you would lose money. We publish that.
  The opportunity surface is real; capturing it depends on how each contract is
  traded, which is the part the agent owns."

### Act 4: Close (7:00 to end)
- Recap in two sentences: engine curates, agent decides, you disagree with it.
- CTA in this order: clone the harness (free, link in description), browse the
  site free, and Agent Access is $39/mo with a 7-day trial if you want the paid
  tools the loop needs.
- Verbal + on-screen disclosure repeat. End card: the GitHub repo AND
  gammarips.com, repo first.

## SEO packaging (draft, copywriter pass required)

- Title candidates (no em dashes), now install-shaped to match the v2 concept:
  1. "From git clone to options contracts: an AI agent on real options flow"
  2. "How to Trade Options Using Claude (Full AI Agent Workflow)"
  3. "I gave Claude last night's options flow. Watch it pick the contracts."
- Description skeleton: what happens in the video, tool list, endpoint, free
  site link with UTM (`utm_source=youtube&utm_medium=video&utm_campaign=claude_workflow`),
  disclosures paragraph, timestamped chapters matching the four acts.
- Chapters double as the Short cut points.

## Production checklist

- [ ] Script final pass through webapp `gammarips-copywriter` (compliance + voice)
- [ ] Fresh demo account + demo API key for recording; REVOKE the key after the
      shoot (it will be on video). Never the owner's real key.
- [ ] Record on a day with a real pool; a "nothing today" outcome is acceptable,
      on-message, and SHOULD be shipped rather than re-recorded.
- [ ] Start from a genuinely empty directory. No pre-cloned repo, no warmed
      context, no pre-connected server. The distance is the message.
- [ ] Keep the raw file for the Gemini edit. The beats that must survive the cut:
      the anonymous-tier data landing before any ask, the paid-boundary sentence,
      the agent rejecting most of the pool, and the negative-composite disclosure.
- [ ] Blur/skip anything showing the private tournament pick or operator email.
- [ ] UTM links in description; confirm GA4 picks up `utm_source=youtube`.
- [ ] After publish: iframe swap on `landing/video-led`, then `/ship` from
      workspace root; X unpin 03-14 post, pin this.
- [ ] Measure: YouTube CTR/retention, GA4 youtube-source sessions, begin_checkout
      from youtube source. This traffic is the organic CVR baseline the ads
      decision (memory `owner-goal-100-paid-subs-eoy2026`) is waiting on.
