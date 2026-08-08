#!/bin/bash
# Interactive ADC re-consent with the GA4 + Search Console read scopes.
#
# THIS IS THE FALLBACK, NOT THE FIX. It re-consents *user* credentials, which
# expire and which Google is actively blocking for third-party scopes on the
# shared gcloud client ID. The permanent fix is service-account impersonation
# (SEO_IMPERSONATE_SA) — see the `seo-auth` skill, Path A.
#
# This script REQUIRES a real terminal: gcloud prompts on stdin for a
# verification code. Running it without a TTY (Claude Code's `!` prefix, CI, any
# backgrounded shell) crashes with `gcloud crashed (EOFError)`. That is not a
# gcloud bug and re-running it will not help.
set -e

if [ ! -t 0 ]; then
  cat >&2 <<'EOF'
ERROR: no TTY on stdin — gcloud cannot prompt for the verification code here.

This will crash with `gcloud crashed (EOFError)`. It is not a transient failure.

Do ONE of these instead:

  1. PERMANENT FIX (do this once, then never run this script again):
     set up service-account impersonation. See the `seo-auth` skill, Path A.
       export SEO_IMPERSONATE_SA=ga-admin@profitscout-fida8.iam.gserviceaccount.com

  2. Run this script in a real terminal window, not through `!` or a wrapper.

  3. Ask Claude to run the FIFO recipe in the `seo-auth` skill, Path B, which
     parks gcloud on a named pipe so the code can be delivered from chat.
EOF
  exit 2
fi

if [ -n "$SEO_IMPERSONATE_SA" ]; then
  echo "NOTE: SEO_IMPERSONATE_SA is set ($SEO_IMPERSONATE_SA)."
  echo "The scripts already impersonate a service account; you probably do not"
  echo "need this. If a pull is failing, check the diagnostic table in the"
  echo "seo-auth skill before re-consenting."
  echo
fi

echo "Sign in as: eraphaelparra@gmail.com"
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
