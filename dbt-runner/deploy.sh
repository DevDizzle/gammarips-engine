#!/usr/bin/env bash
# Deploy the dbt-runner Cloud Run service.
#
# PRECONDITIONS (do NOT skip):
#   1. The dbt layer has had a green live `dbt build` at least once (operator OAuth).
#   2. Optional: ask the owner if they want a gammarips-review pass (it schedules a
#      live BQ build). The review is owner-invoked, never a gate.
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
  --set-env-vars=DBT_TARGET=prod \
  --set-secrets="MAILGUN_API_KEY=MAILGUN_API_KEY:latest,MAILGUN_DOMAIN=MAILGUN_DOMAIN:latest"

# MAILGUN_* (2026-08-07): the daily /digest health email. --set-secrets REPLACES
# the whole secret set, so never hand-trim this line. The runtime SA is the
# default compute SA, which also needs cloudscheduler.jobs.list for the job-health
# section; without it that section degrades to UNKNOWN rather than to a false OK.

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

  # source-freshness alarm at 07:00 ET. NOT optional since 2026-08-07: this is
  # the staleness canary, and /freshness now 500s on an error_after breach so a
  # red job means real staleness. Deliberately NO --max-retry-attempts (default
  # 0) — one red run per day, no retry storm.
  # --attempt-deadline is explicit: without it Scheduler defaults to 180s, and a
  # deadline-timeout red would be indistinguishable from a staleness red.
  gcloud scheduler jobs create http dbt-source-freshness \
    --project=profitscout-fida8 --location=us-central1 \
    --schedule="0 7 * * 1-5" --time-zone="America/New_York" \
    --uri="$RUN_URL/freshness" --http-method=POST \
    --oidc-service-account-email="$INVOKER" --oidc-token-audience="$RUN_URL" \
    --attempt-deadline=300s

  # daily operator health email at 07:15 ET — AFTER the freshness alarm at 07:00
  # so a red canary and the email that explains it land together.
  # Kept a SEPARATE job from dbt-source-freshness on purpose: the Scheduler red
  # status and the email are independent signals with independent failure modes,
  # and collapsing them would mean one broken channel blinds both.
  gcloud scheduler jobs create http freshness-digest \
    --project=profitscout-fida8 --location=us-central1 \
    --schedule="15 7 * * 1-5" --time-zone="America/New_York" \
    --uri="$RUN_URL/digest" --http-method=POST \
    --oidc-service-account-email="$INVOKER" --oidc-token-audience="$RUN_URL" \
    --message-body='{}' \
    --attempt-deadline=420s --max-retry-attempts=1
  # Deadline vs measured wall time: 31s warm, ~60s cold — 7-13x headroom. That
  # margin matters because a Scheduler timeout does NOT stop Cloud Run: the
  # request finishes and sends the email, then the retry sends it again.
  # Duplicate health emails are how a daily digest gets filtered to a folder and
  # stops being read, so retries are capped at 1.

  # One-time IAM for the job-health section (default compute SA):
  gcloud projects add-iam-policy-binding profitscout-fida8 \
    --member="serviceAccount:$(gcloud projects describe profitscout-fida8 \
        --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
    --role="roles/cloudscheduler.viewer"
NOTE
