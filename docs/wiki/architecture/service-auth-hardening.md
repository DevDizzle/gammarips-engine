Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-07-02-service-auth-hardening.md
Date: 2026-07-17

# Cloud Run services are systemically --allow-unauthenticated (remediation not yet executed)

Nearly every Cloud Run service in `profitscout-fida8/us-central1` is deployed
`--allow-unauthenticated` (IAM `allUsers` → `run.invoker`), does NO app-level auth, and
several answer GET as well as POST with attacker-chosen params. Anyone who learns a URL can
drive them. The worst exposure: a forced `/label_enriched_pool` (forward-paper-trader) or
`/pool_outcomes` (win-tracker) call could poison the paid substrate; enrichment-trigger and
the report/eval services are LLM $-cost surfaces (the $38/day incident).

Remediation is OIDC-then-lock per service (drop `allUsers`, require the caller's service
account). Two gotchas: **`deploy.sh` re-opens the door** (it passes
`--allow-unauthenticated`), so the flag must be removed there too; and the `gammarips-mcp`
surface stays public by design (it is the product; it has its own key auth). Idempotent,
recompute-from-BQ-truth writers ([[public-tracks-pool-not-pick]]) blunt the poison risk but
do not replace auth. Status: FINDING + plan, NOT yet executed.
