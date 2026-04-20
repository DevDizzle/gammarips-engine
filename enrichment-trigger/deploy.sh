#!/bin/bash
# Deploy enrichment-trigger to Cloud Run
set -e

# Stage the shared trace_logger lib into the build context so the Dockerfile
# can COPY + pip install it. Cleaned up on exit regardless of success/failure.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_trace_logger_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/trace_logger/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

gcloud run deploy enrichment-trigger \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=3600 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,GCS_BUCKET=profit-scout-data,TRACE_LOGGING_ENABLED=true,MIN_ENRICHMENT_SCORE=1" \
  --set-secrets="POLYGON_API_KEY=POLYGON_API_KEY:latest,GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
