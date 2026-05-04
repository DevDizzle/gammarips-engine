#!/bin/bash
# Deploy blog-generator to Cloud Run.
#
# Triggered by Cloud Scheduler jobs:
#   blog-generator-weekly         Mon 05:00 ET   POST /generate (empty body)
#   content-drafter-weekly-email  Sun 17:00 ET   POST /draft_email
#                                                {"theme":"weekly","dry_run":true}
#
# First deploy ships with DRY_RUN=true so Evan can inspect 1–2 generated posts
# in Firestore (as blog_posts/{slug} with status "dry_run"... except we write
# nothing to blog_posts in dry_run mode — the markdown is returned in the
# response body instead). Re-run deploy with DRY_RUN=false once validated.
#
# Newsletter env vars (added 2026-04-29 with /draft_email + /blast_email):
#   OPERATOR_EMAIL       — operator inbox for draft previews + blast dry-runs
#                          (default: evan@gammarips.com)
#   EMAIL_DRAFTS_BUCKET  — GCS bucket for newsletter HTML/text drafts
#                          (default: gammarips-content-drafts; must be pre-created
#                           with `gsutil mb -p profitscout-fida8 -l us-central1
#                           gs://gammarips-content-drafts`)
#   MAX_RECIPIENTS       — safety cap on /blast_email fan-out (default 1000)
#
# Mailgun secrets (same names as signal-notifier — no new GCP secrets needed):
#   MAILGUN_API_KEY  Secret Manager  MAILGUN_API_KEY:latest
#   MAILGUN_DOMAIN   Secret Manager  MAILGUN_DOMAIN:latest
set -e

# Stage shared gammarips_content lib into build context.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/_gammarips_content_vendor"
rm -rf "${VENDOR_DIR}"
cp -r "${SCRIPT_DIR}/../libs/gammarips_content/." "${VENDOR_DIR}"
trap 'rm -rf "${VENDOR_DIR}"' EXIT

DRY_RUN="${DRY_RUN:-false}"
OPERATOR_EMAIL="${OPERATOR_EMAIL:-evan@gammarips.com}"
EMAIL_DRAFTS_BUCKET="${EMAIL_DRAFTS_BUCKET:-gammarips-content-drafts}"
MAX_RECIPIENTS="${MAX_RECIPIENTS:-1000}"

# /weekly_intel — GA4 + GSC integration (set when SA + permissions land):
#   GA4_PROPERTY_ID  numeric GA4 property id (e.g. 312345678)
#   GSC_SITE_URL     'https://gammarips.com/' or 'sc-domain:gammarips.com'
# Both unset by default; the endpoint degrades to "not yet configured" until
# they're set.
GA4_PROPERTY_ID="${GA4_PROPERTY_ID:-}"
GSC_SITE_URL="${GSC_SITE_URL:-}"

# Runs as the project default compute SA — same as x-poster, has Vertex AI +
# logging + Firestore + GCS via project-level inheritance. The earlier
# firebase-adminsdk-fbsvc binding required per-role IAM grants for every
# capability the service touched (Vertex AI, logging, ...) which got tedious.
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
  --service-account="406581297632-compute@developer.gserviceaccount.com" \
  --set-env-vars="PROJECT_ID=profitscout-fida8,DATASET=profit_scout,N_TRADES_UNLOCK=30,DRY_RUN=${DRY_RUN},OPERATOR_EMAIL=${OPERATOR_EMAIL},EMAIL_DRAFTS_BUCKET=${EMAIL_DRAFTS_BUCKET},MAX_RECIPIENTS=${MAX_RECIPIENTS},GA4_PROPERTY_ID=${GA4_PROPERTY_ID},GSC_SITE_URL=${GSC_SITE_URL}" \
  --set-secrets="MAILGUN_API_KEY=MAILGUN_API_KEY:latest,MAILGUN_DOMAIN=MAILGUN_DOMAIN:latest"

# ---------------------------------------------------------------------------
# Cloud Scheduler — DOCUMENTATION ONLY. DO NOT auto-run from this script.
# Run by hand once after the first deploy that includes /draft_email.
# ---------------------------------------------------------------------------
#
# Pre-req: the GCS bucket must exist (one-time):
#   gsutil mb -p profitscout-fida8 -l us-central1 gs://gammarips-content-drafts
#
# Weekly newsletter draft (operator-preview-only — never blasts):
#
# gcloud scheduler jobs create http content-drafter-weekly-email \
#   --project=profitscout-fida8 \
#   --location=us-central1 \
#   --schedule="0 17 * * SUN" \
#   --time-zone="America/New_York" \
#   --uri="https://blog-generator-406581297632.us-central1.run.app/draft_email" \
#   --http-method=POST \
#   --headers="Content-Type=application/json" \
#   --message-body='{"theme":"weekly","dry_run":true}' \
#   --attempt-deadline=900s
#
# /blast_email remains a manual fallback. The auto path is /blast_latest:
#
#   gcloud scheduler jobs create http content-blast-mon-0530 \
#     --project=profitscout-fida8 \
#     --location=us-central1 \
#     --schedule="30 5 * * 1" \
#     --time-zone="America/New_York" \
#     --uri="https://blog-generator-406581297632.us-central1.run.app/blast_latest" \
#     --http-method=POST \
#     --headers="Content-Type=application/json" \
#     --message-body='{"audience":"all","dry_run":false}' \
#     --attempt-deadline=900s
#
# Sequence:
#   Sun 17:00 ET  — content-drafter-weekly-email   /draft_email   (preview to operator)
#   Mon 05:30 ET  — content-blast-mon-0530         /blast_latest  (auto-blast unless killed)
#
# Operator kill workflow (between Sun preview and Mon blast — ~12.5h window):
#
#   gcloud firestore documents set blast_killswitch/<DATE> \
#     --data='{"aborted": true, "reason": "..."}' \
#     --project=profitscout-fida8
#
# /blast_latest is idempotent: re-runs honor blast_history/<DATE> and skip
# if a prior fan-out already completed. Manual fallback:
#
#   curl -X POST https://blog-generator-406581297632.us-central1.run.app/blast_email \
#     -H "Content-Type: application/json" \
#     -d '{"gcs_uri":"gs://gammarips-content-drafts/email/2026-05-03_newsletter.html",
#          "audience":"all", "dry_run":true}'
#
# ---------------------------------------------------------------------------
# /weekly_intel — Mon 07:00 ET intel report (GA4 + GSC + ledger + blasts)
# ---------------------------------------------------------------------------
#
# gcloud scheduler jobs create http weekly-intel-mon-0700 \
#   --project=profitscout-fida8 \
#   --location=us-central1 \
#   --schedule="0 7 * * 1" \
#   --time-zone="America/New_York" \
#   --uri="https://blog-generator-406581297632.us-central1.run.app/weekly_intel" \
#   --http-method=POST \
#   --headers="Content-Type=application/json" \
#   --message-body='{"days":7,"ledger_days":30,"dry_run":false}' \
#   --attempt-deadline=900s
#
# Pre-reqs (operator one-time setup):
#   1. Create SA: gcloud iam service-accounts create gammarips-analytics-reader
#   2. GA4: in https://analytics.google.com → Admin → Property → Access Mgmt,
#      add gammarips-analytics-reader@profitscout-fida8.iam.gserviceaccount.com
#      as Viewer on the GammaRips GA4 property. Copy the numeric property ID.
#   3. GSC: in https://search.google.com/search-console → Settings → Users
#      and permissions, add the same SA email as Restricted user on the
#      verified gammarips.com property. Copy the verified site URL.
#   4. Re-deploy with env vars:
#        GA4_PROPERTY_ID=<numeric>  GSC_SITE_URL=<https://...>  bash deploy.sh
#   5. Default compute SA at 406581297632-compute@developer.gserviceaccount.com
#      runs the Cloud Run service; ADC picks up the GA4/GSC permissions because
#      we're granting them to gammarips-analytics-reader and impersonating —
#      OR (simpler) bind 406581297632-compute@... directly to GA4 + GSC.
#      Recommended: bind the default compute SA directly to keep Cloud Run
#      auth-flow trivial. The dedicated SA name is documentation only.
