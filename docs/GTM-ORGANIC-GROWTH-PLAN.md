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

## Workstream B — how-to guides (blog section)

All guides: dated, written in STE, compliance pass, refresh
quarterly. Quote what an agent did. Never promise what an agent will
do.

- B1. "How to trade options with Grok" — FIRST. Connector steps, the
  Bearer header, free vs pro, the Robinhood agentic pairing with the
  stocks-only caveat, and the live Grok share as the receipt:
  https://grok.com/share/c2hhcmQtMg_0325372b-f8fc-41a7-9184-e50a21398691
- B2. "How to trade options with Claude Code" — mirrors the video and
  the harness README.
- B3. "How to trade options with ChatGPT" — make sure of the current
  ChatGPT MCP connector scope before you write it.
- B4. "How to trade options with Claude" (claude.ai / Desktop) —
  BLOCKED on one check: can a custom connector send a Bearer-header
  key? If no, the guide says plainly that Claude Desktop gets the
  free tier only.
- B5. Refresh and retitle the post
  `wire-your-ai-agent-to-real-options-data-mcp` toward intent. It
  ranks for nothing with a brand-heavy title.
- B6. Mechanics decision at build time: write Firestore
  `blog_posts/{slug}` rows with a script, or add a static guides
  route. Do NOT use blog-generator for these pages.

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

## Measures

- Weekly: Search Console cluster impressions and clicks. Strip brand,
  `site:`, and bot traffic first (house rule). GA4 signups by landing
  page.
- Before HN: one real attributed checkout. This is the only
  unverified item from the 08-08 deploy.
- Milestones: first external trials before the 08-17 checkpoint,
  paying subscribers before 10-05 (memory
  `mcp-monetization-killswitch`).
