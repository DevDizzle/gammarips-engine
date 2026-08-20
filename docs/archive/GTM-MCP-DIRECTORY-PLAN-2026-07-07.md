> **CHANNEL DEAD — 30-day null result, DECIDED 2026-08-06**
> (`docs/DECISIONS/2026-08-06-growth-sequence-video-hn-ads.md`). Do not
> re-run the click-pack. Kept as the log of what was submitted.

# GTM: MCP Directory Listings Plan + Reevaluation Gate

**Created 2026-07-07 (go-live day). Owner-requested: get listed in the top MCP directories before any ad spend, with a hard timeline — if no paying subs by the gate date, reevaluate the business.**

## The one-line strategy
The buyer is someone already running an AI agent. They discover tools in MCP directories and registries, not on Google. Listings are free, permanent, and exactly-targeted — saturate them first, measure with `mcp_analytics`, and only then decide if paid acquisition can ever pencil at $39/mo.

## Assets (status at creation)
| Asset | Status |
|---|---|
| Remote Streamable HTTP endpoint | ✅ `https://gammarips-mcp-406581297632.us-central1.run.app/mcp` |
| Server card | ✅ `/.well-known/mcp/server-card.json` (good copy) |
| Anon tier (try-before-buy) | ✅ 8 keyless tools; pro tools return `subscription_required` + pricing URL |
| Tool annotations (`readOnlyHint`) | ✅ all tools (server.py:209) — verify per-tool `title` before Anthropic submission |
| Public GitHub repo | ✅ `DevDizzle/gammarips-mcp` — description + homepage fixed to data-vendor framing 07-07 |
| /developers docs page | ✅ live (keyless try-now leads) |
| Privacy policy URL | ✅ gammarips.com/privacy (verify it covers MCP data collection before Anthropic submission) |
| `server.json` manifest | ❌ TODO (required for official registry) |
| OAuth 2.1 | ❌ not built (bearer keys only) — gates the Anthropic Connectors Directory for *authenticated* use |
| Custom-domain endpoint (e.g. `mcp.gammarips.com`) | ❌ optional but better branding + needed for `com.gammarips/*` namespace via DNS |

## Tier 1 — do first (upstream + highest reach)
1. **Official MCP Registry** (`registry.modelcontextprotocol.io`) — THE upstream source; several directories propagate from it. Publish via `mcp-publisher` CLI + `server.json` (`remotes: [{type: streamable-http, url: …/mcp}]`). Namespace: `io.github.devdizzle/gammarips` (instant, GitHub-auth) or `com.gammarips/gammarips` (DNS TXT verification — better branding, needs owner DNS access). No human review — instant listing.
2. **Anthropic Claude Connectors Directory** — biggest reach (claude.ai + Desktop users). Requirements: tool annotations ✅, privacy policy, support contact, reviewer runbook + **test credentials with realistic data**. ⚠️ CATCH: claude.ai custom connectors support OAuth or keyless only — bearer-key headers don't attach in claude.ai web. Paying users on Claude Code/Cursor/Cline are fine today (headers supported). Decision at the Week-2 checkpoint: build OAuth 2.1 (the old Phase 2b) if we want authenticated claude.ai users, or submit later. Do NOT block the other listings on this.
3. **Smithery** — `smithery mcp publish <url> -n gammarips/gammarips`; supports hosted/remote servers.
4. **PulseMCP** — hand-reviewed daily; submit + claim listing.
5. **Glama** — likely auto-crawled (repo is public); claim the listing → move from anonymous-crawl to owner-verified tier.

## Tier 2 — same week, lower effort
mcp.so (community submit) · MCP.Directory · mcpserverfinder.com · Cursor directory (cursor.directory) · Cline marketplace (GitHub PR) · Docker MCP Catalog (Dockerfile exists). ✅ **ARD (Agentic Resource Discovery) — DONE 2026-07-07**: the "Agentic Resource Directory" the owner mentioned = the ARD spec (github.com/ards-project/ard-spec, v0.9 draft; Google/Microsoft/GitHub-backed). It's federated, not a submit-to directory — we now host `https://gammarips.com/.well-known/ai-catalog.json` (webapp PR #8) pointing at the MCP server card; ARD registries crawl it from there. `gammarips-review` passed. Maintenance note: the file pins the card's v3.0.0 tool list — re-sync it if tools or SERVER_VERSION change.

## Launch amplification (free, Week 1–2)
- **Show HN**: "GammaRips — anti-firehose options-flow data for AI agents (MCP)". Angle: the curation philosophy + the honest negative blind-buy baseline (radical transparency is the hook).
- **X thread** from @gammarips: the "stop asking AI for stock picks, give your agent real data" story + a real agent session screencap.
- **MCP community Discord** showcase channels; r/ClaudeAI-style posts (short, receipts-first per the Reddit rule — no long education posts).
- Blog/lab post targeting "options flow MCP" / "trading data for AI agents" queries (SEO compounding).

## Timeline (weeks start Monday; today = Tue 2026-07-07)
- **Week 0 (Jul 7–12):** `server.json` + registry publish; Smithery; Glama claim; PulseMCP + mcp.so + Tier-2 submissions. Fix any per-tool `title` gaps. Owner: decide DNS namespace (`com.gammarips`) or ship with `io.github.*`.
- **Week 1 (Jul 13–19):** Show HN + X launch + Discord/communities. Verify listings render correctly (install snippets, copy). Start weekly metering readout from `mcp_analytics`.
- **Week 2 checkpoint — Mon Jul 20:** leading indicators: distinct callers, anon tool calls/day, `/developers` sessions, `subscription_required` hits (= paywall touches), keys generated, trials started. Decide OAuth 2.1 build (for Anthropic directory) based on demand signal.
- **Week 6 checkpoint — Mon Aug 17:** if **zero trial starts** by now, do NOT wait for the October gate — the funnel has a structural hole; diagnose/reevaluate early. Otherwise iterate (pricing page copy, onboarding friction, new anon-tier teaser tools).
- **🔴 THE GATE — Mon Oct 5, 2026 (90 days):** if **zero PAYING subscribers** (defined: completed the 7-day trial + first successful real-card charge; owner/founder accounts excluded), **reevaluate the business**. Options on the table at that point: price/packaging change, OAuth + Anthropic directory push, B2B data licensing, API-not-MCP pivot, or wind down to operator-only tooling. If ≥1 paying sub: continue, revisit ad spend with real CAC math.

## Execution status (2026-07-07 sprint — deadline 07-10)
**DONE (same day):**
- ✅ Blog launch post LIVE: gammarips.com/blog/wire-your-ai-agent-to-real-options-data-mcp (generator draft was factually wrong — invented tools, fake links, "real-time institutional" claims; hand-corrected to the real tool surface, gammarips-review SHIP)
- ✅ `server.json` registry-validated; PR #11 on gammarips-mcp (server.json + Cursor/Cline README snippets + 400×400 logo)
- ✅ Cline Marketplace: cline/mcp-marketplace#1969
- ✅ Docker MCP Catalog: docker/mcp-registry#4296
- ✅ mcp.so: chatmcp/mcpso#3057
- ✅ GitHub repo description/homepage fixed to data-vendor framing
- ✅ **Open Plugins wrapper (07-07)**: cursor.directory switched to plugin-only submissions (Open Plugins standard, auto-detect from repo). gammarips-mcp PR #15 adds `.cursor-plugin/plugin.json` (inline remote streamable-HTTP server, keyless anon default) + a bundled `skills/gammarips-options-flow/SKILL.md` teaching the data-not-advice workflow (gammarips-review: SHIP). Owner: merge #15, then cursor.directory → Submit a Plugin → paste the repo URL. Strategic note: the plugin format is the "bundle skills with the MCP" vehicle — same repo now installs the server + methodology skill in one click across Open Plugins hosts (Cursor, Claude Code, …); future skills (exit-lab companion, tournament-pattern) slot into `skills/`.

**OWNER CLICK-PACK (≈15 min total):**
1. **Official registry auth** — github.com/login/device, enter the device code Claude gives you (15-min expiry; publish fires automatically on authorize). Self-serve fallback anytime: `cd ~/gammarips-mcp-serverjson && ~/.local/bin/mcp-publisher login github && ~/.local/bin/mcp-publisher publish` (binary installed 07-07; server.json is registry-validated).
2. **Merge PR #11** — github.com/DevDizzle/gammarips-mcp/pull/11 (metadata only, zero runtime).
3. **Smithery** — smithery.ai → sign in with GitHub → Add/claim server → endpoint `https://gammarips-mcp-406581297632.us-central1.run.app/mcp` (Streamable HTTP, remote).
4. **PulseMCP** — pulsemcp.com/submit → name "GammaRips Options Intelligence", URL github.com/DevDizzle/gammarips-mcp, endpoint above, description: "Anti-firehose options-flow data for AI agents: curated daily pool, point-in-time features, realized MFE/MAE outcomes. Free anon tier; no pick endpoint. Not advice."
5. **Glama** — glama.ai → sign in with GitHub → claim the crawled DevDizzle/gammarips-mcp listing.
6. **cursor.directory** — MCP section → submit with the same endpoint + description.

## Measurement (all already wired)
- `profitscout-fida8.mcp_analytics.run_googleapis_com_stderr` — per-call tool/tier/decision (parse `MCP_TOOL_CALL` JSON from textPayload).
- GA4 (`G-ZF0DQVQEKJ`) — /developers, /pricing funnels.
- Stripe dashboard — trials, conversions, churn.
- Firestore `mcp_api_keys` — keys minted (excluding founder).

## Standing rules for all listing copy
Data-not-advice framing. NO performance/ROI claims (pool composite is negative; publish the honest baseline instead). NO IV-beating claim, NEVER ITM%/floor-mean as marketing. `gammarips-review` before any new public data exposure.
