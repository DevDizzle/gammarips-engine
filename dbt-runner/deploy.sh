#!/usr/bin/env bash
# Deploy the dbt-runner Cloud Run service.
#
# PRECONDITIONS (do NOT skip):
#   1. The dbt layer has had a green live `dbt build` at least once (operator OAuth).
#   2. gammarips-review has passed on this service (it schedules a live BQ build).
#
# Vendors the dbt/ project into ./dbt (gitignored) so `gcloud run deploy --source=.`
# from this directory has the project in its build context, then cleans it up.
set -euo pipefail

cd "$(dirname "$0")"

PROJECT=profitscout-fida8
REGION=us-central1
SERVICE=dbt-runner

echo "==> Vendoring dbt project…"
rm -rf ./dbt
cp -r ../dbt ./dbt
# prod profile target uses method: oauth -> Cloud Run compute SA ADC (no secret).
cp ../dbt/profiles.yml.example ./dbt/profiles.yml
# drop local-only artifacts
rm -rf ./dbt/target ./dbt/dbt_packages ./dbt/logs

echo "==> Deploying $SERVICE to Cloud Run ($PROJECT/$REGION)…"
gcloud run deploy "$SERVICE" \
  --source=. \
  --project="$PROJECT" \
  --region="$REGION" \
  --no-allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=1800 \
  --set-env-vars=DBT_TARGET=prod

echo "==> Cleaning up vendored copy…"
rm -rf ./dbt

cat <<'NOTE'

Deployed. To schedule the daily build (run once, after deploy):

  RUN_URL=$(gcloud run services describe dbt-runner --project=profitscout-fida8 \
      --region=us-central1 --format='value(status.url)')
  INVOKER=$(gcloud projects describe profitscout-fida8 --format='value(projectNumber)')-compute@developer.gserviceaccount.com

  # daily build at 06:30 ET (after enrichment, before the trader)
  gcloud scheduler jobs create http dbt-daily-build \
    --project=profitscout-fida8 --location=us-central1 \
    --schedule="30 6 * * 1-5" --time-zone="America/New_York" \
    --uri="$RUN_URL/" --http-method=POST \
    --oidc-service-account-email="$INVOKER" --oidc-token-audience="$RUN_URL" \
    --attempt-deadline=1800s --max-retry-attempts=2

  # optional: source-freshness alarm at 07:00 ET
  gcloud scheduler jobs create http dbt-source-freshness \
    --project=profitscout-fida8 --location=us-central1 \
    --schedule="0 7 * * 1-5" --time-zone="America/New_York" \
    --uri="$RUN_URL/freshness" --http-method=POST \
    --oidc-service-account-email="$INVOKER" --oidc-token-audience="$RUN_URL"
NOTE
