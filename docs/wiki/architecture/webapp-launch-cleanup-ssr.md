Status: retired
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-22-launch-cleanup.md
Date: 2026-07-17

# Webapp launch cleanup + SSR crawlability (webapp-only, engine untouched)

The 2026-04-22 launch-cleanup fixed the `gammarips-webapp` for its paid-tier launch:
end-to-end Stripe payment flow, a cluster of accumulated console env overrides, SSR
crawlability, and copy-alignment gaps. Explicit scope note: **engine services were
untouched** and no execution policy changed.

Retired here because it is a webapp-repo decision (the webapp is a separate Next.js repo)
and its specific state — the V5.3-era paid tier — has since been superseded by the
free-UI / paid-MCP model ([[v5-3-monetization-retired]]). Represented in the engine wiki for
provenance completeness; the current webapp plan is the 2026-07-17 replan's Plan 4.
