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

1. Workstreams A + B: landing rewrite and the first guides. Land
   these BEFORE Show HN, so HN traffic hits the new funnel.
2. The video. Spec unchanged: `docs/GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`.
3. Show HN per `docs/GTM-DISTRIBUTION-PLAYBOOK.md`. Gates unchanged:
   video live AND one real GA4-attributed checkout.
4. Workstream C backlink cadence: weekly, continues through all steps.
5. Ads review ~09-01 on measured CVR. Ads only on a nonzero organic
   baseline.

## Workstream A — landing page rewrite (repo: gammarips-webapp)

Rails: branch first (main auto-deploys production). All copy goes
through `gammarips-copywriter`. Ship with `/ship` from `~/workspace`.
Write all new copy in STE.

- A1. Fix the dead commands in
  `src/components/landing/harness-cta.tsx:21`. The block teaches four
  retired command names. The real loop is `/trade`, `/review`,
  `/coach`. Keep the block in lockstep with the harness README.
- A2. New hero block: the plain equation "MCP + harness = agentic
  trading" and the three-layer product statement. Keep the video
  iframe slot for the step-2 swap.
- A3. New per-client connect component with tabs: Claude Code,
  Claude, ChatGPT, Grok. Each tab shows the free ten-second connect
  first, then the pro steps for that client.
- A4. Reorder the page: hero → connect tabs → harness steps → today's
  pool + the honesty section → pricing CTA → Lab → blog → FAQ.
  Activation above the fold. Proof after.
- A5. Keep the homepage meta description disclaimer-free. That scope
  is SETTLED (memory `meta-description-disclaimer-scope-settled`).
- Known and unrelated: 3 pre-existing tsc errors in
  `src/app/signals/page.tsx` reproduce on clean main.

## Client connect facts (verified 2026-08-15 from official docs)

These facts bind the guides (B), the connect tabs (A3), and the
videos (E). "Pro" = the client can send `Authorization: Bearer
gr_live_...`. Full table with sources: `docs/GTM-CLIENT-CONNECT-MATRIX.md`.

| Client | Free tier | Pro tier today | How |
|---|---|---|---|
| Claude Code | yes | yes | `claude mcp add --transport http gammarips <url> --header "Authorization: Bearer <key>"` |
| Codex CLI | yes | yes | `~/.codex/config.toml` `[mcp_servers.gammarips]` `url` + `bearer_token_env_var` |
| Cursor | yes | yes | `.cursor/mcp.json` `url` + `headers` (`${env:VAR}`) |
| Gemini CLI | yes | yes | `gemini mcp add --transport http -H "Authorization: Bearer <key>" gammarips <url>` |
| Claude.ai / Desktop | yes (1 custom connector on Free) | beta only ("Request headers" in the connector dialog, slow rollout); community `mcp-remote` workaround | Customize > Connectors > Add custom connector |
| ChatGPT | yes (Plus/Pro/Business+, Developer mode, web only) | NO. ChatGPT cannot present API keys. Pro needs OAuth 2.1 on our server | Settings > Security and login > Developer mode > Plugins > + |
| Grok | yes (custom connector, any public URL) | UNVERIFIED in the consumer UI; Grok Build CLI supports `--header` (paid) | grok.com/connectors > New Connector > Custom |

Consequence: the paid loop is a CLI story today (Claude Code, Codex,
Cursor, Gemini CLI). Chat clients get the free tier and an honest
"pro needs X" line. The one product lever that changes this is
OAuth 2.1 on the MCP (D4). Do not write copy that says ChatGPT or
Grok can run the paid loop.

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
- B5. "How to trade options with ChatGPT" — free tier only, said in
  the first screen; Developer mode + Plugins steps; the honest line
  "ChatGPT cannot send our key; the paid tools need OAuth, which is
  on the roadmap (D4)". Publish after D4 is decided so the line is
  right.
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
- D4. OAuth 2.1 on the MCP (MCP-V3-SPEC Phase 2b). **DECIDED 2026-08-15:
  build it in anticipation, sequenced THIRD** (owner, later the same
  day): first the landing page, then the YouTube content, then OAuth,
  and OAuth must be live BEFORE the live-money trading agent debuts in
  public. It is the one
  lever that unlocks the PAID tier inside ChatGPT and claude.ai without
  a beta. Measured first: 30 days of logs show 0 ChatGPT and 0 claude.ai
  paywall hits, 3 from Grok; the build is a forecast bet on the
  Robinhood agentic wave (Claude, ChatGPT, Grok, Cursor), not a demand
  response. Shape: the authorization server lives on gammarips.com
  (Firebase login + consent, DCR, PKCE, JWT access tokens, rotating
  refresh); the MCP adds a `/pro` endpoint that requires auth and keeps
  `/mcp` anonymous. Repos: gammarips-webapp + gammarips-mcp, each with
  its own gate. Decision note: gammarips-mcp
  `docs/DECISIONS/2026-08-15-oauth-pro-endpoint.md`. Also add a client
  class to the `MCP_TOOL_CALL` meter so the weekly denial-by-client
  read is one query.
  **BUILT 2026-08-19** (owner pulled it forward: "we need OAuth so we
  can run an agent headless in a VM"). Webapp branch
  `oauth/authorization-server` (AS: `/.well-known/oauth-authorization-server`,
  `/oauth/{authorize,consent,token,register,revoke,jwks}`, CIMD + DCR,
  PKCE, RS256 tokens with `tier`, rotating refresh, `client_credentials`
  machine clients on `/account`). MCP branch `oauth/pro-endpoint`
  (`/pro`, JWT verification, discovery docs, meter `client_class`).
  e2e with the real MCP SDK client: 24/24. **SHIPPED the same day:** PR #26
  merged, MCP `gammarips-mcp-00044-2fq`; the JWKS key wiring (`912d3def`)
  was the last rollout. Next: the webapp copy PR (`/developers`, discovery
  files, connect tabs), then guides B4/B5 and videos E4/E5 can show a
  person paying inside the chat client.
- D5. Connect tabs (A3) ship the four full-paid CLI clients as
  copy-paste steps and give the chat clients a free-tier step plus
  the honest pro line from the matrix. Never invent a step.

## Measures

- Weekly: Search Console cluster impressions and clicks. Strip brand,
  `site:`, and bot traffic first (house rule). GA4 signups by landing
  page.
- Before HN: one real attributed checkout. This is the only
  unverified item from the 08-08 deploy.
- Milestones: first external trials before the 08-17 checkpoint,
  paying subscribers before 10-05 (memory
  `mcp-monetization-killswitch`).
