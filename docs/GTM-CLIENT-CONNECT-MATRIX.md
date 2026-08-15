# Client connect matrix for the GammaRips MCP

Verified 2026-08-15 from official docs (sources at the end). Refresh before
each guide and each video. Target server: `https://mcp.gammarips.com/mcp`,
Streamable HTTP. Anonymous tier needs no auth. Pro tier needs
`Authorization: Bearer gr_live_<32 hex>`.

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

## Copy rules that follow

- The paid loop is a CLI story today: Claude Code, Codex, Cursor,
  Gemini CLI. Say so.
- Chat clients (Claude.ai, ChatGPT, Grok) get the free tier now.
  Give the honest pro line: Claude.ai = beta header or use Claude
  Code; ChatGPT = needs OAuth on our server (roadmap D4); Grok =
  test in the UI before you promise anything.
- Never write a step you did not verify. Mark unknowns as unknown.
- The trailing-newline trap is real for every client: a pasted key
  with a newline fails with a whitespace error. Say "no spaces, no
  newline" once in every guide.

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
