# Client connect matrix for the GammaRips MCP

Verified 2026-08-15 from official docs (sources at the end). Refresh before
each guide and each video. Target server: `https://mcp.gammarips.com/mcp`,
Streamable HTTP. Anonymous tier needs no auth. Pro tier needs
`Authorization: Bearer gr_live_<32 hex>`.

**OAuth status (2026-08-22): SHIPPED AND SHAPE-VERIFIED.** gammarips.com is
the authorization server, the MCP serves `https://mcp.gammarips.com/pro`
(auth required, OAuth 2.1 + PKCE, CIMD and DCR). The "OAuth" column is the
paid path for every chat client: add `/pro`, sign in, done.

**The 08-19 gate ("one real sign-in per client before any guide claims it")
is LIFTED for the server side.** It existed to stop us claiming a client
works when our own server might reject the shape that client sends. That
risk is now measured, not assumed: `gammarips-webapp/scripts/oauth/client-profiles.ts`
runs the full flow (register, authorize, consent, exchange, connect, call a
PRO tool) once per client profile against production. On 2026-08-22, 9 of 10
profiles reached a live pro tool. See "Shape verification" below.

What that evidence does NOT cover is a vendor's own UI wiring inside its
connector dialog. That is their code. Treat it exactly like the free-tier
steps in this table, which have always been sourced from vendor docs rather
than from our own clicks: write the documented step, and correct it if a real
user reports otherwise.

## Matrix

| Client | Add a remote server | Static Bearer | OAuth | No auth | Plan or tier | Platform | Confidence |
|---|---|---|---|---|---|---|---|
| Claude Code | `claude mcp add --transport http gammarips https://mcp.gammarips.com/mcp --header "Authorization: Bearer <key>"`; or `.mcp.json` `{"type":"http","url":...,"headers":{"Authorization":"Bearer ${GAMMARIPS_MCP_KEY}"}}` | yes (`-H`, repeatable; `${VAR}` expansion) | yes | yes | any install | CLI (macOS, Linux, Windows) | verified (doc + `claude` 2.1.233 help) |
| Codex CLI | `~/.codex/config.toml`: `[mcp_servers.gammarips]` `url = "https://mcp.gammarips.com/mcp"` `bearer_token_env_var = "GAMMARIPS_MCP_KEY"`; also `http_headers`, `env_http_headers`; CLI `codex mcp add gammarips --url <url> --bearer-token-env-var GAMMARIPS_MCP_KEY` | yes | yes (`codex mcp login`) | yes | not stated | CLI, IDE extension, ChatGPT desktop app share the file | config fields verified; `codex mcp add --url` verified only in GitHub's install guide |
| Cursor | `.cursor/mcp.json` or `~/.cursor/mcp.json`: `{"mcpServers":{"gammarips":{"url":"https://mcp.gammarips.com/mcp","headers":{"Authorization":"Bearer ${env:GAMMARIPS_MCP_KEY}"}}}}` | yes | yes | yes | not stated | Desktop IDE, Cursor CLI, Cursor Agents | verified |
| Gemini CLI | `gemini mcp add --transport http -H "Authorization: Bearer <key>" gammarips https://mcp.gammarips.com/mcp` (`-s user` for global); settings key is `httpUrl` (`url` means SSE) | yes | yes | yes | not stated | CLI | verified (doc + `gemini` 0.35.1 help) |
| Claude.ai web / Desktop | Customize > Connectors > Add custom connector > URL. Free plan gets one custom connector. | beta only: "Request headers" section, allowlisted names (`authorization`, `x-api-key`, ...), enter the full value `Bearer gr_live_...`; slow rollout, contact Anthropic for early access. Community workaround: `mcp-remote` stdio entry with `--header` (not Anthropic) | yes | yes | Free, Pro, Max, Team, Enterprise | web, Desktop, Cowork, mobile (cloud-side) | verified; beta rollout per account unknown |
| ChatGPT | Settings > Security and login > Developer mode ON; then Plugins > + > name, MCP URL ending `/mcp`, Authentication = OAuth, No Authentication, or Mixed | NO. Official: ChatGPT "cannot present custom API keys" | yes (OAuth 2.1 + PKCE, DCR or CIMD or static client id/secret) | yes | Pro, Plus, Business, Enterprise, Education, web only; Free and Go not listed | web | verified |
| Grok (grok.com) | grok.com/connectors > New Connector > Custom > URL > "complete any required authentication". Server must be public. | UNKNOWN in the consumer UI (no header field documented; one 05-12 bug report saw no prompt). Grok Build CLI: `grok mcp add --transport http <name> <url> --header "Authorization: Bearer ..."` (paid) | yes | inferred yes | official: "available to all Grok users"; third-party guides say a paid tier; unresolved | web, iOS, Android | steps verified; auth unknown; tier conflicting |

## Shape verification (2026-08-22)

`gammarips-webapp/scripts/oauth/client-profiles.ts`, run against
`AS_URL=https://gammarips.com` + `MCP_URL=https://mcp.gammarips.com`.
Each row is a full flow ending in a real `query_outcomes` call on `/pro`.

| Profile | Shape under test | Result |
|---|---|---|
| Claude Code | client-ID metadata document + ephemeral loopback port | PASS |
| claude.ai / Desktop | hosted web callback, public client (PKCE only) | PASS |
| ChatGPT | hosted web callback, dynamic registration | PASS |
| ChatGPT | static client id + secret, HTTP Basic at the token endpoint | PASS |
| ChatGPT | static client id + secret, secret in the form body | PASS |
| Cursor | private-use scheme (RFC 8252 section 7.1) | PASS |
| Codex CLI | fixed loopback port | PASS |
| Gemini CLI | ephemeral loopback port | PASS |
| Grok / generic | hosted web callback (Grok does not publish its URL) | PASS |
| Native client | loopback on literal `127.0.0.1` | FAIL, known |

Every pass also confirms `state` round-trips, RFC 9207 `iss` is present, the
code lands on the client's own callback host, `aud` is the `/pro` resource,
and the `tier` claim is `pro`.

The one failure is the documented App Hosting residual: the edge rewrites the
literal token `127.0.0.1` in a query parameter, so that redirect 400s on prod
and passes on localhost. Owner-assessed as low impact and NOT a blocker
(`gammarips-mcp/docs/DECISIONS/2026-08-15-oauth-pro-endpoint.md`). No shipped
chat client is affected. Re-run the probe after any change to the AS.

## Copy rules that follow

- **There are two ways in, and both are real.** Clients that can send an
  Authorization header use an API key on `/mcp`. Clients that cannot add
  `/pro` and sign in. Never write that a client "cannot reach the paid
  tools" again.
- The paid loop is no longer a CLI-only story. Claude.ai, ChatGPT and Grok
  reach the same 9 tools through OAuth.
- Never write a step you did not verify. Vendor-documented UI steps count as
  verified, exactly as they always have for the free tier; our own protocol
  claims must trace to a probe or e2e run. Mark unknowns as unknown.
- Grok still does not document its callback or its auth field. Our generic
  hosted-callback shape passes, so the honest line is that Grok works if its
  dialog completes the sign-in, and we say so without inventing its UI.
- The trailing-newline trap is real for every client that takes a KEY: a
  pasted key with a newline fails with a whitespace error. Say "no spaces, no
  newline" once in every guide. It does not apply to the OAuth path, which is
  the point of recommending OAuth to non-technical users.
- Prefer `localhost` over `127.0.0.1` whenever developer copy names a loopback
  host.

## Sources (fetched 2026-08-15)

- Claude Code: https://code.claude.com/docs/en/mcp
- Codex: https://learn.chatgpt.com/docs/extend/mcp?surface=cli ;
  https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md
- Cursor: https://cursor.com/docs/mcp.md
- Gemini CLI: https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md
- Claude.ai / Desktop: https://claude.com/docs/connectors/custom/remote-mcp ;
  https://claude.com/docs/connectors/building/authentication ;
  https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp
- ChatGPT: https://developers.openai.com/api/docs/guides/developer-mode ;
  https://developers.openai.com/plugins/build/auth ;
  https://developers.openai.com/plugins/deploy/connect-chatgpt
- Grok: https://docs.x.ai/grok/connectors ;
  https://docs.x.ai/grok/connectors/custom-mcp-tunneling ;
  https://x.ai/news/grok-connectors ; https://docs.x.ai/build/features/mcp-servers ;
  https://github.com/makeplane/plane/issues/9055
