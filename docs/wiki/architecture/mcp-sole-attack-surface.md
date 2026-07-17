Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-27-mcp-hardening-x-poster-live-email-only.md
Date: 2026-07-17

# gammarips-mcp is the SOLE attack surface for paid-agent interactions

Every paid bring-your-own-agent interaction routes through the `gammarips-mcp` server, which
is the ONLY way that agent touches the world — so the prompt-injection blast radius is
bounded by whatever the MCP exposes (safe_error / clamp / rate-limit / schema-whitelist
hardening). This is deliberate: it was built as the single, sandboxed surface for the paid
bot.

Corollaries: the MCP exposes data + tool primitives each agent reasons over to its OWN
contract, **never a pick-returning endpoint** ([[public-tracks-pool-not-pick]]); the MCP
stays intentionally public (its own key auth), unlike the other Cloud Run services which
should be locked ([[service-auth-hardening]]). The MCP is a SEPARATE repo and is the
monetized product.
