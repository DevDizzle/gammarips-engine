#!/bin/bash
# Deploy signal-notifier to Cloud Run
set -e

PROJECT_ID="profitscout-fida8"
REGION="us-central1"
SERVICE_NAME="signal-notifier"

echo "Deploying $SERVICE_NAME to Cloud Run in project $PROJECT_ID..."

gcloud run deploy $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --source=. \
  --clear-base-image \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=300 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --set-secrets="MAILGUN_API_KEY=MAILGUN_API_KEY:latest,MAILGUN_DOMAIN=MAILGUN_DOMAIN:latest" \
  --service-account="firebase-adminsdk-fbsvc@$PROJECT_ID.iam.gserviceaccount.com"

echo "Done!"