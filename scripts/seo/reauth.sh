#!/bin/bash
# One-time ADC re-consent with the GA4 + Search Console read scopes.
# Plain `gcloud auth application-default login` omits these, so the SEO
# scripts 403 (see README step 3). Sign in as eraphaelparra@gmail.com —
# that account holds the GA4/GSC property access.
set -e
echo "Sign in as: eraphaelparra@gmail.com"
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
