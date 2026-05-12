#!/bin/bash
# Deploy signal-ranker to Cloud Run.
#
# Called inline from signal-notifier's 07:30 ET cron (Phase 3 wires this).
# DRY_RUN flipped false 2026-05-09 (signal_ranker_runs ledger writes enabled).
# Prompts bumped to scorer_v4 / picker_v3 2026-05-09 — trading-context preamble
# + ITM hard cap; see docs/DECISIONS/2026-05-09-moneyness-fix-and-trading-context-prompts.md.
# Prompts bumped to scorer_v5 / picker_v4 2026-05-12 — DTE band widened 7-30 → 7-45
# to match the relaxed signal-notifier hard gate; see
# docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md.
set -e

# Stage shared gammarips_content lib into build context (mirrors x-poster).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_gammarips_content_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/gammarips_content/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

# IAM-invoker only (no --allow-unauthenticated). signal-notifier and the
# operator (smoke-test scripts) authenticate via service-account ID tokens.
# Audit 2026-05-08 item 4: an unauthenticated /rank endpoint with attacker-
# controlled report_md + candidates is a non-trivial injection surface even
# in DRY_RUN. Closing it before any further deploy.
PROJECT_NUM="406581297632"
DEFAULT_COMPUTE_SA="${PROJECT_NUM}-compute@developer.gserviceaccount.com"

gcloud run deploy signal-ranker \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --no-allow-unauthenticated \
  --memory=2Gi \
  --timeout=540 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,SCORER_MODEL=gemini-3-flash-preview,PICKER_MODEL=gemini-3.1-pro-preview,SCORER_PROMPT_VERSION=5,PICKER_PROMPT_VERSION=4,DRY_RUN=false,MIN_SCORER_SUCCESS_FRAC=0.5"

# Grant the default compute SA invoker permission so signal-notifier (and
# operator-side smoke tests using ID tokens) can call /rank. Phase 3 also
# grants the Firebase Admin SA used by signal-notifier — service identity
# of any caller must be on this list explicitly (no --allow-unauthenticated).
gcloud run services add-iam-policy-binding signal-ranker \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --member="serviceAccount:${DEFAULT_COMPUTE_SA}" \
  --role="roles/run.invoker"

gcloud run services add-iam-policy-binding signal-ranker \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --member="serviceAccount:firebase-adminsdk-fbsvc@profitscout-fida8.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
