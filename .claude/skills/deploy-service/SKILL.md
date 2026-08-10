---
name: deploy-service
description: Deploy a GammaRips Cloud Run service (forward-paper-trader, enrichment-trigger, signal-notifier, signal-judge, blog-generator, x-poster, win-tracker, and the rest). Use whenever the task is to deploy, ship, redeploy, roll back, or rotate secrets on any service in this repo. Carries the mandatory review gate, the secret-mount trap, and per-service facts.
---

# Deploying a GammaRips service

Every service deploys from its own directory with `bash deploy.sh`. The script is the
source of truth for flags, env vars, and secret mounts — read it before you run it.

## Gate first, always

1. **Invoke `gammarips-review` before any deploy.** Read-only auditor, and it is not
   self-waivable. It exists to catch lookahead bias, data leakage, and unsafe live paths
   before they reach capital.
2. If the change touches execution policy, the Definition of Done applies: 30-day
   out-of-sample on `forward-paper-trader` plus the review audit. See `CLAUDE.md`.
3. If the change alters public data exposure, that is also a `gammarips-review` trigger.
4. Policy changes need a `docs/DECISIONS/` note and a `docs/TRADING-STRATEGY.md` update
   in the same change, not after it.

## The secret-mount trap

`gcloud run deploy --set-secrets` **REPLACES the entire secret set**. Dropping a name
from that flag silently strips the mount on the next deploy; the service starts fine and
fails later at the first call that needs the secret.

Before deploying, diff the `--set-secrets` line against what the service actually mounts.
Never hand-edit that line down.

## Per-service facts

**`forward-paper-trader/`** — production paper trading, `profitscout-fida8`/`us-central1`,
1024Mi, timeout 600, max-instances 1, `--allow-unauthenticated`.
- Six routes: `POST /` (paper trading), `POST /cache_iv`, `POST /mark_to_market`,
  `POST /persist_minute_paths` (token-gated), `POST /label_life_surface`,
  `POST /label_enriched_pool`, `POST /fill_closed_windows` (token-gated, 2026-07-28).
- Secret mounts: `POLYGON_API_KEY`, `POOL_LIQ_REFRESH_TOKEN` (2026-07-07),
  `FILL_WINDOWS_TOKEN` (2026-07-28). **No FMP key, ever** — FMP was deliberately removed
  from this service 2026-04-08.
- Never add execution gates here. Signal-quality gates live in `enrichment-trigger` and
  `signal-notifier`.

**`enrichment-trigger/`** — vendors `libs/trace_logger` into the build context at deploy
time (`_trace_logger_vendor`, cleaned up via `trap ... EXIT`). Timeout 3600, max-instances 2.
Secrets: `POLYGON_API_KEY`, `GOOGLE_API_KEY`.

**`x-poster/`, `blog-generator/`** — additionally vendor `libs/gammarips_content`.
`blog-generator` defaults matter: verify `DRY_RUN` and the Firestore write path before a
live run. Both are behind the compliance canonicalizer in the shared lib.

**`signal-judge/`** — IAM-locked, invoked by `signal-notifier`. Not public.

**`agent-arena/`** — DEAD since 2026-05-04. Do not deploy. If touched, propose deletion.

## After deploying

Verify, do not assume:

```bash
# confirm the new revision is serving
gcloud run services describe <SERVICE> --project=profitscout-fida8 --region=us-central1 \
  --format='value(status.latestReadyRevisionName)'

# read logs
gcloud run services logs read <SERVICE> --project=profitscout-fida8 --region=us-central1 --limit=50

# scheduler state, if the service is cron-driven
gcloud scheduler jobs list --project=profitscout-fida8 --location=us-central1
```

Then dry-run the service's own entry point where one exists (e.g. blog-generator
`POST /generate {"slug":"...","dry_run":true}`) before trusting the next scheduled run.

## Rotations

`POLYGON_API_KEY` is mounted by several services. Rotating it means redeploying **every**
service that mounts it, not just the one you are working on. Grep `deploy.sh` across the
repo for the secret name to get the full list.
