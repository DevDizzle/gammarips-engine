# GTM — Organic Growth Plan: web rewrite, guides, backlinks

Owner decision 2026-08-13. This plan extends
`docs/DECISIONS/2026-08-06-growth-sequence-video-hn-ads.md`. The goal is
unchanged: 100 paid subscribers by 2026-12-31. Organic subscribers come
first. Paid ads wait for a measured baseline.

## The product statement (locked 2026-08-13)

**MCP + harness = agentic trading.**

- We sell hosted data over MCP ($39/mo). We give away the discipline
  loop: the open-source harness with its skills. The user brings their
  own agent.
- The product controls execution risk. The data answers three
  questions. Can I get in? Can I get out? What did this setup do
  before? The loop makes sure that the exit plan exists before the
  entry.
- Audience (owner, 2026-08-13): persons who operate an agent harness
  (Claude Code, Claude, ChatGPT, Grok, Codex, Cursor) and want to
  trade options. This market is small on purpose. The goal needs ~100
  subscribers, not thousands.
- No pick, anywhere. No profit claims. The webapp forbidden-claims
  list binds all public copy.

## Evidence base (measured 2026-08-13)

- Search Console, 90 days, brand and bots stripped: ZERO impressions
  on assistant names (claude, chatgpt, grok, gemini, copilot). The
  full AI-intent cluster is 8 impressions, 0 clicks. One page-1 seed:
  "mcp options order flow server" at position 10 on the pipeline blog
  post. The intent is 100% unserved, by us and by almost everyone.
- A public Grok share shows the funnel with no harness: free tier →
  the agent reasons to its own contract → the paywall error teaches
  the upgrade steps. Use the link as the receipt in guide B1.
- Robinhood has an OFFICIAL agentic-trading MCP (launched 2026-05-27,
  `agent.robinhood.com/mcp/trading`). Ring-fenced account,
  review-before-action, stocks-only beta, options pending. Clients:
  Claude, ChatGPT, Grok, Cursor. This intent wave is forming at this
  time. Memory: `robinhood-agentic-trading-mcp-official`.

## Sequence (amends 08-06 — the video and HN gates stay)

1. Workstream A landing rewrite: DONE, shipped 2026-08-15.
   Workstream B first guides: land these BEFORE Show HN, so HN
   traffic hits the new funnel.
2. The video. Spec unchanged: `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`.
3. Show HN per `docs/GTM-DISTRIBUTION-PLAYBOOK.md`. Gates unchanged:
   video live AND one real GA4-attributed checkout.
4. Workstream C backlink cadence: weekly, continues through all steps.
5. Ads review ~09-01 on measured CVR. Ads only on a nonzero organic
   baseline.

## Workstream A — landing page rewrite (repo: gammarips-webapp)

**DONE — shipped 2026-08-15.** A1 to A5 landed: command fix, new
hero, per-client connect tabs, page reorder, and the disclaimer-free
homepage meta description. That disclaimer scope is SETTLED (memory
`meta-description-disclaimer-scope-settled`).

## Client connect facts (verified 2026-08-15 from official docs)

These facts bind the guides (B), the connect tabs (A3), and the
videos (E). "Pro" = the client can send `Authorization: Bearer
gr_live_...`. Full table with sources: `docs/GTM-CLIENT-CONNECT-MATRIX.md`.
The table below is the 2026-08-15 pre-OAuth snapshot. The consequence
note after it carries the 2026-08-19 OAuth update.

| Client | Free tier | Pro tier today | How |
|---|---|---|---|
| Claude Code | yes | yes | `claude mcp add --transport http gammarips <url> --header "Authorization: Bearer <key>"` |
| Codex CLI | yes | yes | `~/.codex/config.toml` `[mcp_servers.gammarips]` `url` + `bearer_token_env_var` |
| Cursor | yes | yes | `.cursor/mcp.json` `url` + `headers` (`${env:VAR}`) |
| Gemini CLI | yes | yes | `gemini mcp add --transport http -H "Authorization: Bearer <key>" gammarips <url>` |
| Claude.ai / Desktop | yes (1 custom connector on Free) | beta only ("Request headers" in the connector dialog, slow rollout); community `mcp-remote` workaround | Customize > Connectors > Add custom connector |
| ChatGPT | yes (Plus/Pro/Business+, Developer mode, web only) | NO. ChatGPT cannot present API keys. Pro needs OAuth 2.1 on our server | Settings > Security and login > Developer mode > Plugins > + |
| Grok | yes (custom connector, any public URL) | UNVERIFIED in the consumer UI; Grok Build CLI supports `--header` (paid) | grok.com/connectors > New Connector > Custom |

Consequence (updated 2026-08-19): OAuth `/pro` is SHIPPED (D4). The
CLI clients keep the Bearer-key paid path. Chat clients (ChatGPT,
claude.ai, Grok) get the paid tier via OAuth sign-in on `/pro`. But
re-verify each client against the live `/pro` endpoint, with one
real sign-in per client, before any guide or video claims it. The
matrix (`docs/GTM-CLIENT-CONNECT-MATRIX.md`) tracks that
verification.

## Workstream B — how-to guides (blog section)

All guides: dated, written in STE, compliance pass, refresh
quarterly. Quote what an agent did. Never promise what an agent will
do. Each guide states its client's free/pro truth from the table
above in its first screen. Each guide embeds its video (E) when the
video exists. Titles carry the intent phrase "how to trade options
with <client>". Order below is the publish order.

- B1. "How to trade options with Grok" — FIRST. Connector steps,
  free tier shown live, the pro truth (unverified in the consumer UI;
  Grok Build CLI with `--header` for paid), the Robinhood agentic
  pairing with the stocks-only caveat, and the live Grok share as the
  receipt:
  https://grok.com/share/c2hhcmQtMg_0325372b-f8fc-41a7-9184-e50a21398691
  Owner test before publish: does the Grok custom-connector dialog
  offer an API-key or header field on his account?
- B2. "How to trade options with Claude Code" — mirrors video E1 and
  the harness README. Full paid loop.
- B3. "How to trade options with Codex" — full paid loop via
  `config.toml` `bearer_token_env_var`; needs harness `AGENTS.md`
  (D2) first.
- B4. "How to trade options with Claude" (claude.ai / Desktop) —
  the 08-07 post `connect-claude-to-live-options-data-mcp` is the
  base. Retitle toward the intent phrase, add the loop, and state
  plainly: free tier now, pro when the "Request headers" beta
  reaches your account, or use Claude Code.
- B5. "How to trade options with ChatGPT" — Developer mode + Plugins
  steps; free tier first, then the paid path: OAuth sign-in on
  `/pro` (D4, shipped 08-19). Verify one real ChatGPT OAuth sign-in
  against the live `/pro` endpoint, then publish.
- B6. "How to trade options with Cursor" — short; full paid loop.
- B7. Pillar: "How agentic options trading actually works" — the hub
  page that links every guide, the Robinhood agentic account
  pairing, and the trace surface (`/agent`) once live. Targets the
  head term and serves the C5 newsletter pitch.
- B8. Refresh and retitle `wire-your-ai-agent-to-real-options-data-mcp`
  toward intent. It ranks for nothing with a brand-heavy title.
- B9. Mechanics: write Firestore `blog_posts/{slug}` rows with a
  script (`scripts/blog/publish_guide.py`, engine repo, reads a
  markdown file with front matter). Do NOT use blog-generator for
  these pages. Every guide passes `libs/gammarips_content`
  `score_against_rubric(is_blog=True)` and `/ship`.

## Workstream E — video series (owner records)

Spec: `docs/GTM-VIDEO-SERIES.md`. One episode per client, in this
order: E1 Claude Code (spec exists in
`GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`, the HN artifact), E2 Grok,
E3 Codex, E4 Claude, E5 ChatGPT, E6 Cursor. Each episode embeds in
its guide and links the repo first, the site second. Show HN fires
after E1 is live (gate unchanged).

## Workstream C — backlinks and authority

Hard rule: NO directory sprints. The 07-07 sprint was a 30-day null
result and the decision is recorded. Active placements only.

- C1. Show HN, per the playbook. The repo is the artifact.
- C2. GitHub: PRs to awesome-MCP lists, harness README cross-links.
  Repo topics were done 08-08.
- C3. Syndication: repost the pipeline-build story to dev.to and
  Medium with a canonical tag to our blog.
- C4. Community answers, weekly cadence: r/algotrading, r/options,
  HN threads, X (drafts via x-poster). Value first. Link the matching
  guide only when it answers the question. The owner posts from his
  own accounts. Outbound rule holds: draft, never send.
- C5. The Robinhood-agentic news wave: pitch 2-3 AI-trading
  newsletters or blogs with the "how agentic options trading actually
  works" angle.
- C6. Video description and pinned comment: repo link first, site
  second (playbook rule).

## Workstream D — product levers that feed the funnel

- D1. Audit the MCP `subscription_required` error text. Make sure it
  carries the account URL, the key format, and the header line. The
  error renders inside every assistant chat. It is a sales surface.
  Repo: gammarips-mcp, its own review gate.
- D2. Harness repo: add `AGENTS.md` for Codex. Add the "your fills
  close the loop" README section (shape approved 2026-08-13). Hand-
  sync the 4 drifted wiki notes. The regime-rail note waits on the
  owner call (public fail-closed vs private halve-and-continue).
  Never trust the archived sync script's `--apply` (memory
  `trader-harness-sync-apply-unsafe`).
- D3. Plugin packaging: PARKED. The repo is the canonical wrapper.
  Look at this again after the guides ship.
- D4. OAuth 2.1 on the MCP. **DONE — shipped 2026-08-19** (decided
  08-15, built and shipped 08-19: AS on gammarips.com, MCP `/pro`
  auth-required, `/mcp` anonymous, e2e 24/24). Decision note:
  gammarips-mcp `docs/DECISIONS/2026-08-15-oauth-pro-endpoint.md`.
  Next: the webapp copy PR (`/developers`, discovery files, connect
  tabs), then guides B4/B5 and videos E4/E5 after the per-client
  sign-in verification.
- D5. Connect tabs (A3) ship the four full-paid CLI clients as
  copy-paste steps and give the chat clients a free-tier step plus
  the honest pro line from the matrix. Never invent a step.

## Measures

- Weekly: Search Console cluster impressions and clicks. Strip brand,
  `site:`, and bot traffic first (house rule). GA4 signups by landing
  page.
- Before HN: one real attributed checkout. This is the only
  unverified item from the 08-08 deploy.
- Milestone: paying subscribers before 10-05 (memory
  `mcp-monetization-killswitch`).
