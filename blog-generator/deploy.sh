#!/bin/bash
# Deploy blog-generator to Cloud Run.
#
# Triggered by one Cloud Scheduler job:
#   blog-generator-weekly   Monday 05:00 ET   POST /run (empty body)
#
# First deploy ships with DRY_RUN=true so Evan can inspect 1–2 generated posts
# in Firestore (as blog_posts/{slug} with status "dry_run"... except we write
# nothing to blog_posts in dry_run mode — the markdown is returned in the
# response body instead). Re-run deploy with DRY_RUN=false once validated.
set -e

# Stage shared gammarips_content lib into build context.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_gammarips_content_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/gammarips_content/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

DRY_RUN="${DRY_RUN:-true}"

gcloud run deploy blog-generator \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --allow-unauthenticated \
  --memory=2Gi \
  --timeout=900 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,N_TRADES_UNLOCK=30,DRY_RUN=${DRY_RUN}"
