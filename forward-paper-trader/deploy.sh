#!/bin/bash
# Deploy forward-paper-trader to Cloud Run
set -e

PROJECT_ID="profitscout-fida8"
REGION="us-central1"
SERVICE_NAME="forward-paper-trader"

echo "Deploying $SERVICE_NAME to Cloud Run in project $PROJECT_ID..."

# POOL_LIQ_REFRESH_TOKEN (2026-07-07): shared refresh token for the
# POST /persist_minute_paths research endpoint (X-Refresh-Token header; same
# secret the notifier's /refresh_pool_liquidity uses). MUST stay in
# --set-secrets — the flag REPLACES the secret set, so dropping it silently
# strips the mount on the next deploy.
# FILL_WINDOWS_TOKEN (2026-07-28): per-endpoint token gating the
# POST /fill_closed_windows daily opp-window filler (X-Refresh-Token header).
# Same REPLACES-the-set caveat applies.

gcloud run deploy $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --source=. \
  --clear-base-image \
  --allow-unauthenticated \
  --memory=1024Mi \
  --timeout=600 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,FILL_WINDOWS_MAX_ROWS=200" \
  --set-secrets="POLYGON_API_KEY=POLYGON_API_KEY:latest,POOL_LIQ_REFRESH_TOKEN=POOL_LIQ_REFRESH_TOKEN:latest,FILL_WINDOWS_TOKEN=FILL_WINDOWS_TOKEN:latest" \
  --service-account="firebase-adminsdk-fbsvc@$PROJECT_ID.iam.gserviceaccount.com"

cat <<'NOTE'

Done!

Scheduler job for POST /load_underlying_bars (2026-08-07) — create ONCE, and
keep this codified: an uncodified job is unauditable, and this one going
missing (or losing its header) recreates the exact 37-day stale-bars outage it
exists to prevent.

  RUN_URL=$(gcloud run services describe forward-paper-trader \
      --project=profitscout-fida8 --region=us-central1 --format='value(status.url)')
  TOKEN=$(gcloud secrets versions access latest --secret=POOL_LIQ_REFRESH_TOKEN \
      --project=profitscout-fida8 | tr -d '\n')   # mounts carry a trailing newline

  # 17:05 ET — five minutes BEFORE label-life-surface (17:10), which needs the
  # settlement marks this loads. attempt-deadline covers a 5-session window
  # (~5 Polygon calls + 5 DELETE+load pairs) well inside Cloud Run's 600s.
  # max-retry-attempts=1: the endpoint 500s only when the NEWEST session failed,
  # and a full retry re-runs the whole window, so one retry then go red.
  gcloud scheduler jobs create http load-underlying-bars \
    --project=profitscout-fida8 --location=us-central1 \
    --schedule="5 17 * * 1-5" --time-zone="America/New_York" \
    --uri="$RUN_URL/load_underlying_bars" --http-method=POST \
    --headers="Content-Type=application/json,X-Refresh-Token=$TOKEN" \
    --message-body='{}' \
    --attempt-deadline=300s --max-retry-attempts=1

The EXISTING label-life-surface job, recorded here because it was never
codified and it consumes what the job above produces. 17:10 ET, five minutes
after. It runs a LIFE_DAILY_LIMIT-row loop (600) at roughly 0.5s/row plus
staged MERGEs, so the deadline must leave room under Cloud Run's --timeout=600.
Since 2026-08-07 it can also abort on a Polygon splits-enumeration failure
(fail-closed by design), which is a legitimate 500 and should go red.

  gcloud scheduler jobs create http label-life-surface \
    --project=profitscout-fida8 --location=us-central1 \
    --schedule="10 17 * * 1-5" --time-zone="America/New_York" \
    --uri="$RUN_URL/label_life_surface" --http-method=POST \
    --headers="Content-Type=application/json,X-Refresh-Token=$TOKEN" \
    --message-body='{}' \
    --attempt-deadline=600s

NEVER paste `gcloud scheduler jobs describe` output for either job anywhere:
--headers puts the shared token in argv and in the describe output.
NOTE