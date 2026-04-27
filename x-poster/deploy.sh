#!/bin/bash
# Deploy x-poster to Cloud Run.
#
# Triggered by 5 Cloud Scheduler jobs with different {"post_type": "..."} payloads:
#   x-poster-report-0830   weekday 08:30 ET
#   x-poster-signal-0905   weekday 09:05 ET
#   x-poster-teaser-1230   weekday 12:30 ET
#   x-poster-callback-1600 weekday 16:00 ET
#   x-poster-scorecard-fri-1700  Friday 17:00 ET
set -e

# Stage shared gammarips_content lib into build context.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_gammarips_content_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/gammarips_content/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

# LIVE: DRY_RUN=false posts real tweets. Flipped 2026-04-27 with Option B (PIL
# ticker overlay on signal/win/loss).
gcloud run deploy x-poster \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --allow-unauthenticated \
  --memory=2Gi \
  --timeout=540 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,GCS_BUCKET=gammarips-x-media,BRAND_REF_GCS=gs://gammarips-x-media/brand_ref_card.png,IMAGE_MODEL=gemini-3-pro-image-preview,BRAND_HANDLE=@gammarips,DRY_RUN=false" \
  --set-secrets="X_API_KEY=X_API_KEY:latest,X_API_SECRET=X_API_SECRET:latest,X_ACCESS_TOKEN=X_ACCESS_TOKEN:latest,X_ACCESS_SECRET=X_ACCESS_SECRET:latest"
