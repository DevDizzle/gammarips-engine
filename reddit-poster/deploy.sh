#!/bin/bash
# Deploy reddit-poster to Cloud Run.
#
# Single endpoint: POST /post with {"post_type":"trade_idea"|"pnl_receipt"}.
# DRY_RUN=true on first deploy — writes drafts to gs://gammarips-reddit-drafts/
# instead of submitting to Reddit. Flip to false once Evan reviews 1-2 drafts.
#
# Pre-deploy one-time setup (Evan, by hand):
#   1. Create Reddit "script" app at https://www.reddit.com/prefs/apps
#   2. Put 4 secrets into Secret Manager:
#        REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
#      gcloud secrets create REDDIT_CLIENT_ID --project=profitscout-fida8 --replication-policy=automatic
#      printf "%s" "$REDDIT_CLIENT_ID_VALUE" | gcloud secrets versions add REDDIT_CLIENT_ID --data-file=- --project=profitscout-fida8
#      (repeat for the other 3)
#   3. Create the GCS drafts bucket (one-time):
#      gsutil mb -p profitscout-fida8 -l us-central1 gs://gammarips-reddit-drafts
set -e

# Stage shared gammarips_content lib into build context.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_gammarips_content_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/gammarips_content/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

DRY_RUN="${DRY_RUN:-true}"
DEFAULT_SUBREDDITS="${DEFAULT_SUBREDDITS:-options,thetagang,algotrading}"
GCS_DRAFTS_BUCKET="${GCS_DRAFTS_BUCKET:-gammarips-reddit-drafts}"

gcloud run deploy reddit-poster \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=300 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --service-account="406581297632-compute@developer.gserviceaccount.com" \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DRY_RUN=${DRY_RUN},DEFAULT_SUBREDDITS=${DEFAULT_SUBREDDITS},GCS_DRAFTS_BUCKET=${GCS_DRAFTS_BUCKET}" \
  --set-secrets="REDDIT_CLIENT_ID=REDDIT_CLIENT_ID:latest,REDDIT_CLIENT_SECRET=REDDIT_CLIENT_SECRET:latest,REDDIT_USERNAME=REDDIT_USERNAME:latest,REDDIT_PASSWORD=REDDIT_PASSWORD:latest"

# ---------------------------------------------------------------------------
# Cloud Scheduler — DOCUMENTATION ONLY. DO NOT auto-run from this script.
# Wait until Evan confirms post types + cadence + subreddits, then run by hand.
# ---------------------------------------------------------------------------
#
# Suggested cadence (subject to Evan's confirmation):
#
#   reddit-poster-trade-idea-0930   weekday 09:30 ET   POST /post {"post_type":"trade_idea"}
#   reddit-poster-pnl-receipt-1600  weekday 16:00 ET   POST /post {"post_type":"pnl_receipt"}
#
# gcloud scheduler jobs create http reddit-poster-trade-idea-0930 \
#   --project=profitscout-fida8 \
#   --location=us-central1 \
#   --schedule="30 9 * * MON-FRI" \
#   --time-zone="America/New_York" \
#   --uri="https://reddit-poster-406581297632.us-central1.run.app/post" \
#   --http-method=POST \
#   --headers="Content-Type=application/json" \
#   --message-body='{"post_type":"trade_idea"}' \
#   --attempt-deadline=300s
#
# gcloud scheduler jobs create http reddit-poster-pnl-receipt-1600 \
#   --project=profitscout-fida8 \
#   --location=us-central1 \
#   --schedule="0 16 * * MON-FRI" \
#   --time-zone="America/New_York" \
#   --uri="https://reddit-poster-406581297632.us-central1.run.app/post" \
#   --http-method=POST \
#   --headers="Content-Type=application/json" \
#   --message-body='{"post_type":"pnl_receipt"}' \
#   --attempt-deadline=300s
