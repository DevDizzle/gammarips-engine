#!/bin/bash
# Deploy signal-notifier to Cloud Run
set -e

PROJECT_ID="profitscout-fida8"
REGION="us-central1"
SERVICE_NAME="signal-notifier"

echo "Deploying $SERVICE_NAME to Cloud Run in project $PROJECT_ID..."

# Live-OI liquidity floor env knobs (2026-06-25, all reversible — defaults below
# match the in-code defaults; override here to retune without a code change):
#   OI_FLOOR=1000       contracts with live_oi < this are dropped (operator-set
#                       2026-06-25, strictest tier; in-code default is 200)
#   TOURNEY_MIN=8       fail-soft floor: never starve the tournament below this
#   LIQUIDITY_TILT=true kill switch — set false for bit-identical pre-2026-06-25
#                       behavior (no re-fetch, no drop, no tilt)
# Optional tuning (rarely needed): LIVE_OI_FETCH_TIMEOUT_S=8, LIVE_OI_MAX_WORKERS=16
# See docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md.
#
# POOL_LIQ_REFRESH_TOKEN (2026-07-07, review FIX-1): secret-mounted shared token
# for POST /refresh_pool_liquidity — the Cloud Scheduler job
# `pool-liquidity-refresh` sends it as X-Refresh-Token; force/scan_date knobs
# are refused without it. It MUST stay in this script's --set-secrets list:
# --set-secrets REPLACES the secret set, so dropping it here silently strips
# the mount on the next deploy (same landmine class as --allow-unauthenticated
# re-opening the service). See docs/DECISIONS/2026-07-07-pool-liquidity-snapshot.md.

gcloud run deploy $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --source=. \
  --clear-base-image \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=540 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --set-env-vars="SIGNAL_JUDGE_URL=https://signal-judge-406581297632.us-central1.run.app,OI_FLOOR=1000,TOURNEY_MIN=8,LIQUIDITY_TILT=true" \
  --set-secrets="MAILGUN_API_KEY=MAILGUN_API_KEY:latest,MAILGUN_DOMAIN=MAILGUN_DOMAIN:latest,FMP_API_KEY=FMP_API_KEY:latest,POLYGON_API_KEY=POLYGON_API_KEY:latest,POOL_LIQ_REFRESH_TOKEN=POOL_LIQ_REFRESH_TOKEN:latest" \
  --service-account="firebase-adminsdk-fbsvc@$PROJECT_ID.iam.gserviceaccount.com"

echo "Done!"