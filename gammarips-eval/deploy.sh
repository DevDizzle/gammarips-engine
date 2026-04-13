#!/bin/bash
# Deploy gammarips-eval to Cloud Run
set -e

PROJECT="profitscout-fida8"
REGION="us-central1"
SERVICE="gammarips-eval"

echo "Deploying ${SERVICE} to Cloud Run..."

gcloud run deploy $SERVICE \
  --project=$PROJECT \
  --region=$REGION \
  --source=. \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --timeout=540 \
  --concurrency=8 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=${PROJECT},DATASET=profit_scout,EVAL_VERSION=v1.0.0,EVAL_MAX_SPEND_USD=2.0,JUDGE_MODEL=gemini-3-flash-preview"

URL=$(gcloud run services describe $SERVICE --project=$PROJECT --region=$REGION --format='value(status.url)')
echo "Deployed: ${URL}"
echo ""
echo "Smoke test:"
echo "  curl ${URL}/healthz"
echo "  curl -X POST ${URL}/eval/batch -H 'Content-Type: application/json' -d '{\"limit\": 10}'"
