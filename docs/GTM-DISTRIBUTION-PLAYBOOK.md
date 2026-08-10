# GTM: Distribution playbook (the one-liner, Show HN, and where the link goes)

Status: LIVE (2026-08-08). Operationalizes `docs/DECISIONS/2026-08-06-growth-sequence-video-hn-ads.md`.
Companion: `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md` (the video), and the
30-day null result logged in `docs/GTM-MCP-DIRECTORY-PLAN.md`.

## The core insight this playbook exists to preserve

**Stop leading with the website. Lead with the command.**

The site converted 89 US sessions into zero subscribers in the 28 days to
2026-08-05. But the anonymous MCP tier is a ten-second trial with no card, no
key, and no signup:

    claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp

That is a fundamentally stronger funnel entry than "visit gammarips.com," and it
is what technical audiences respond to. The site is what someone reads AFTER the
tool has already done something for them.

**Corollary, and it is a hard one:** the harness loop itself CANNOT run on the
anonymous tier. `get_liquidity`, `get_signal`, `query_outcomes` and
`replay_contract` are all pro. Free to SEE the data, paid to RUN the loop. Never
blur this in any copy; the honest version converts better and cannot backfire.

## Why not just do SEO

Measured 2026-08-08 (memory `reports-are-the-seo-asset-not-ticker-pages`): real
external organic demand is ~2 impressions/day after stripping brand and `site:`
noise. We rank **7.7** for `llm stock options data last 7 days` and it drew **3
impressions in 90 days**. We are not losing the category; the category has not
started. SEO is demand *capture* and there is no demand yet to capture.

So: pre-position on the future vocabulary because it is cheap, acquire on the
CURRENT vocabulary (`options flow api`, `unusual whales alternative`, where a
buyer already has a wallet open), and get distribution from places where people
gather and can be SHOWN the idea.

## Surface list, ranked by whether a human meets it in context

| Surface | State | Action |
|---|---|---|
| Harness README | ✅ DONE 08-08 (PR #2) | Opens with the free one-liner + per-tool free/pro table. It previously opened with "Subscribe $39/mo" and never mentioned the free tier. |
| GitHub repo topics | ✅ DONE 08-08 | 7 topics added; was zero. |
| Show HN post + first comment | STAGED, not fired | See below. Gated on the video. |
| Video description + pinned comment | Waiting on the video | Repo link FIRST, site second. |
| X `@gammarips` bio + pinned post | TODO | Unpin the 03-14 post, pin the launch. |
| Reddit r/ClaudeAI, r/mcp, r/algotrading | AFTER HN | Read each sub's self-promo rules; they differ and they enforce. |
| Webapp harness CTA | ✅ live | `src/components/landing/harness-cta.tsx` |
| MCP directories | ❌ DO NOT REDO | 07-07 sprint = 30-day null result, zero external trials. Passive listings do not move this product. |

## Show HN plan

**Submit the REPO** `https://github.com/DevDizzle/gammarips-harness`, not
gammarips.com. HN clicks GitHub. A repo is something you clone; a marketing page
is something you bounce off. It is also the exact artifact the video demos, so
video viewers and HN readers land in one place.

**Recommended title:**
`Show HN: Open-source harness for trading options with an AI agent over MCP`

Alternates: `Show HN: Options-flow data for AI agents, with no pick endpoint on purpose`
· `Show HN: I gave my trading agent real options data instead of asking for picks`

**The text** (paste into the form's text field if it accepts one alongside a URL;
otherwise post it as your own first comment within a minute of submitting) is
kept verbatim in `~/workspace/HN-SUBMISSION.txt` and reproduced here so it
survives the scratch file:

> Hi HN. I run an overnight scan of ~5,200 US tickers for unusual options
> activity, curate it hard down to a small pool, and expose the whole thing to AI
> agents over MCP. This repo is the open-source harness I run against it.
>
> The design decision I would most like to be argued with about: there is no pick
> endpoint, deliberately. The MCP exposes primitives (the curated pool,
> per-contract liquidity, realized excursion distributions for historical setups,
> a queryable outcome database, exit-rule simulation, methodology playbooks) and
> your agent reasons over them to its own contract. Two agents with different
> objectives and risk should reach different answers. I think a pick-returning
> endpoint is both a worse product and a liability, but I know that is an odd
> position for something in this category.
>
> What is free and what is not, plainly:
>
> Free, no signup, about ten seconds. Connect any MCP client to the anonymous
> tier and you get the pool preview, the daily report, regime context, the market
> calendar, and the methodology playbooks:
>
>     claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp
>
> Paid ($39/mo) covers liquidity, enriched per-name detail, outcome history, and
> exit-rule simulation. The harness screen calls all four, so the daily loop will
> not run anonymously. The harness is free; the data is what costs money.
>
> The uncomfortable number, up front: the whole-pool composite under a fixed exit
> is negative. I publish that instead of hiding it. The pool is a candidate
> surface, not a set of winners, and whether anything works at all depends on how
> contracts are entered and exited. That is exactly why the harness pre-registers
> every pool name as a row before any outcome is known, and scores all of them
> after the close rather than only the ones it picked. Scoring just your own picks
> cannot tell you whether your screen works.
>
> Stack: Python on Cloud Run, BigQuery, Firestore, Polygon for options data. The
> MCP server is Streamable HTTP.
>
> I would genuinely rather be told where the methodology is wrong than be told it
> is neat. Everything is paper-traded and educational, and none of it is
> investment advice.

### Gates before firing

1. The video exists and is published (this is step 2 of the growth sequence).
2. A real trial checkout has confirmed GA4 `purchase` attaches to a session, not
   `(not set)`. Otherwise the spike is unmeasurable and the whole point is lost.
3. Webapp deployed so links preview with an image (done 08-08, PR #23).

**One shot per project.** Reposting burns goodwill. The cost of waiting a week is
zero; the cost of firing early is the channel.

### Mechanics and hard rules

- Account needs to exist beforehand; a day-old account posting a launch reads as
  exactly what it is. No karma minimum to submit.
- Tue to Thu, roughly 8-10am ET, on a day the owner can sit in the thread for 4+
  hours. Treat the timing as folklore; being present to answer matters more.
- **Never solicit upvotes.** Not in Slack, not in DMs. HN detects voting rings and
  bans for it. This is the fastest way to lose both the account and the launch.
- Do not repost if it sinks. There is a moderator second-chance pool; email
  hn@ycombinator.com once, politely.
- Do not get defensive. The people picking holes are doing the work for you.
- Nothing that reads as a returns promise goes in the thread. Our compliance
  posture is an ASSET there: "the composite is negative and I publish it" earns
  more credibility than any performance number could.

### The three questions to have answers ready for

1. "How is this not just Unusual Whales with extra steps?"
2. "Why should I pay for data when the composite is negative?"
3. "What stops the agent hallucinating a thesis over noisy data?"

## Measurement

This is the first traffic event with attribution actually working (webapp PR #21,
deployed 08-08). Watch GA4 realtime during the thread, and the
`begin_checkout` -> `purchase` funnel by source afterward. That CVR is the number
the ~09-01 ads decision is gated on.
