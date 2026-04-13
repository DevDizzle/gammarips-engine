#!/bin/bash
# Deploy overnight-report-generator to Cloud Run
set -e

# Stage shared trace_logger lib into build context.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_trace_logger_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/trace_logger/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

gcloud run deploy overnight-report-generator \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=540 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,TRACE_LOGGING_ENABLED=true" \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
