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
# Early-print slate floor knobs (2026-07-28 tournament liquidity upgrade —
# requires the 09:52 ET cron; at 09:45 the delayed feed shows nothing):
#   PRINT_FLOOR_ENABLED=true  kill switch — false = bit-identical pre-2026-07-28
#                             single-tier OI-floor behavior
#   PRINT_FLOOR_MIN=1         a contract must show >= this many KNOWN prints at
#                             the ~09:52 read to stay (None = unknown = kept)
# See docs/DECISIONS/2026-07-28-tournament-liquidity-upgrade.md.
#
# Fail-soft restore mode (2026-08-12). A candidate that fails a liquidity floor
# must never become the pick. The old always-on restore fed the rejects to a
# judge that could not see they were rejects (ALC 08-11, MDB 08-12).
#   FAILSOFT_RESTORE_MODE=none  DEFAULT. Never restore. When zero candidates
#                               clear, the slate is empty and the notifier
#                               fails closed with no_liquid_candidates.
#                               TOURNEY_MIN becomes a soft target only.
#   ...=empty_only              restore up to TOURNEY_MIN only when zero cleared
#   ...=always                  pre-2026-08-12 behavior. This is the defect.
#                               Rollback lever only.
# An unrecognized value logs an error and falls back to "none" (fails SAFE).
#   LIVE_FETCH_MIN_OK_FRAC=0.5  EVIDENCE gate on the stand-down. A total
#                       Polygon failure does NOT raise, so a run can
#                       complete with live_oi=None everywhere and let the
#                       OI floor sweep the slate on stale frozen OI. Below
#                       this fraction the run is DEGRADED: floors skipped,
#                       pool passed through, no stand-down. Raise it to be
#                       stricter, lower it only with a reason.
# See docs/DECISIONS/2026-08-12-failsoft-restore-never-picks.md.
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
  --set-env-vars="SIGNAL_JUDGE_URL=https://signal-judge-406581297632.us-central1.run.app,OI_FLOOR=1000,TOURNEY_MIN=8,LIQUIDITY_TILT=true,PRINT_FLOOR_ENABLED=true,PRINT_FLOOR_MIN=1,PRINT_VALID_AFTER_ET_MIN=590,PRINT_BAR_MAX_AGE_DAYS=10,FAILSOFT_RESTORE_MODE=none,LIVE_FETCH_MIN_OK_FRAC=0.5" \
  --set-secrets="MAILGUN_API_KEY=MAILGUN_API_KEY:latest,MAILGUN_DOMAIN=MAILGUN_DOMAIN:latest,FMP_API_KEY=FMP_API_KEY:latest,POLYGON_API_KEY=POLYGON_API_KEY:latest,POOL_LIQ_REFRESH_TOKEN=POOL_LIQ_REFRESH_TOKEN:latest" \
  --service-account="firebase-adminsdk-fbsvc@$PROJECT_ID.iam.gserviceaccount.com"

echo "Done!"