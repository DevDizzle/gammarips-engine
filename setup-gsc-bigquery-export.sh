#!/usr/bin/env bash
# ONE-TIME setup for Google Search Console -> BigQuery Bulk Data Export.
#
# What this does: grants Google's OWN Search Console export service account
# permission to write exported performance data into your BigQuery project.
# It does NOT touch your data, and it does NOT use your personal Gmail auth
# (it runs as your gcloud owner login). Safe + reversible.
#
# The SA below is Google-managed and only ever writes Search Console exports.
# Roles follow Google's documented setup:
#   - bigquery.jobUser   -> lets it run the load jobs
#   - bigquery.dataEditor -> lets it create/write the searchconsole tables
#
# Run:   bash setup-gsc-bigquery-export.sh
set -euo pipefail

PROJECT="profitscout-fida8"
SA="search-console-data-export@system.gserviceaccount.com"

echo "Granting BigQuery Job User to ${SA} ..."
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA}" \
  --role="roles/bigquery.jobUser" \
  --condition=None --quiet >/dev/null

echo "Granting BigQuery Data Editor to ${SA} ..."
gcloud projects add-iam-policy-binding "${PROJECT}" \
  --member="serviceAccount:${SA}" \
  --role="roles/bigquery.dataEditor" \
  --condition=None --quiet >/dev/null

echo
echo "Bindings now on ${SA}:"
gcloud projects get-iam-policy "${PROJECT}" \
  --flatten="bindings[].members" \
  --filter="bindings.members:${SA}" \
  --format="table(bindings.role)"

echo
echo "DONE. Now finish in the Search Console UI (see the form values Claude gave you)."
