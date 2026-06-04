#!/bin/bash
# Deploy signal-judge to Cloud Run.
#
# Called inline from signal-notifier's 07:30 ET cron (Phase 3 wires this).
# DRY_RUN flipped false 2026-05-09 (signal_ranker_runs ledger writes enabled).
# Prompts bumped to scorer_v4 / picker_v3 2026-05-09 — trading-context preamble
# + ITM hard cap; see docs/DECISIONS/2026-05-09-moneyness-fix-and-trading-context-prompts.md.
# Prompts bumped to scorer_v5 / picker_v4 2026-05-12 — DTE band widened 7-30 → 7-45
# to match the relaxed signal-notifier hard gate; see
# docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md.
# Picker bumped to picker_v5 2026-06-03 — injects closed_trades_case_memory
# (case-memory harness: quant priors + curated forensic exemplars from
# case_memory/, which ships with --source=.). Advisory, fails open to "".
# See docs/DECISIONS/2026-06-03-picker-case-memory.md.
# COLLAPSED to judge_v6 2026-06-04 — Scorer+Picker -> one memory-aware call.
# JUDGE_PROMPT_VERSION=6 is mirrored into both scorer/picker columns of
# signal_ranker_runs (REQUIRED cols, DDL unchanged). Case-memory is now
# load-bearing (fail-closed if absent). The legacy SCORER_*/PICKER_* env vars
# are retained but inert. See docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md.
set -e

# Pre-deploy guard: the picker_v5 case-memory block must actually be present and
# non-empty in the build context, or the deploy ships a v5 service whose memory
# silently didn't make it. (Runtime also fails closed, but catch it here first.)
for f in case_memory/quant.md case_memory/exemplars.md; do
  if [ ! -s "$f" ]; then
    echo "FATAL: $f missing/empty — run scripts/ledger_and_tracking/build_case_memory.py" >&2
    exit 1
  fi
done
python3 -c "import json,sys; json.load(open('case_memory/build_manifest.json'))" \
  || { echo "FATAL: case_memory/build_manifest.json missing or invalid JSON" >&2; exit 1; }

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

gcloud run deploy signal-judge \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --source=. \
  --no-allow-unauthenticated \
  --memory=2Gi \
  --timeout=540 \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=2 \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,JUDGE_MODEL=gemini-3.1-pro-preview,JUDGE_PROMPT_VERSION=7,JUDGE_PROMPT_LABEL=tournament_v1,JUDGE_MAX_ATTEMPTS=3,TOURNEY_BATCH=10,GOOGLE_CLOUD_LOCATION=global,DRY_RUN=false"

# Grant the default compute SA invoker permission so signal-notifier (and
# operator-side smoke tests using ID tokens) can call /rank. Phase 3 also
# grants the Firebase Admin SA used by signal-notifier — service identity
# of any caller must be on this list explicitly (no --allow-unauthenticated).
gcloud run services add-iam-policy-binding signal-judge \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --member="serviceAccount:${DEFAULT_COMPUTE_SA}" \
  --role="roles/run.invoker"

gcloud run services add-iam-policy-binding signal-judge \
  --project=profitscout-fida8 \
  --region=us-central1 \
  --member="serviceAccount:firebase-adminsdk-fbsvc@profitscout-fida8.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
