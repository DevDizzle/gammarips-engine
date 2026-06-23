# dbt-runner

Cloud Run service that runs the GammaRips dbt project (`../dbt`) on a schedule —
the production refresh path for the `profitscout_dbt` semantic layer.

**Status: DRAFT, NOT DEPLOYED.** Pending (1) a first green live `dbt build` and
(2) a `gammarips-review` pass. See `docs/DECISIONS/2026-06-23-dbt-layer-rebuild.md`.

## What it does
- `POST /` → `dbt deps && dbt build` (materializes models + runs tests, DAG order).
- `POST /freshness` → `dbt source freshness`.
- `GET /healthz` → liveness.

It is **read-only over production**: writes only to `profitscout_dbt`, never to a
source table, never to trading execution. BigQuery auth is the Cloud Run default
compute SA via ADC (the dbt `prod` target uses `method: oauth` — no key, no secret).

## How the dbt project gets in
`deploy.sh` vendors `../dbt` into `./dbt` (gitignored) so the Cloud Run source
build has it in context, then removes it. Same pattern as the trace_logger vendor.

## Deploy (only after the preconditions)
```bash
cd dbt-runner && bash deploy.sh
```
Then create the Cloud Scheduler jobs (commands printed at the end of `deploy.sh`):
a daily build at 06:30 ET and an optional source-freshness check at 07:00 ET, both
invoking the service with OIDC.
