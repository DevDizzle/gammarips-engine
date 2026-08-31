#!/usr/bin/env bash
# Relaunch-email runner. Fetches the Mailgun key from the deployed webapp
# service and hands it to relaunch_email.py. The key is never printed.
#
# Usage, from anywhere:
#   bash scripts/gtm/send_relaunch.sh                          # dry run
#   bash scripts/gtm/send_relaunch.sh --test evan@gammarips.com
#   bash scripts/gtm/send_relaunch.sh --send
#
# This replaces the long inline one-liner. That version started with "!" for
# the Claude prompt, and pasting it into bash made "!" the NOT operator, so
# "! cd x && ..." short-circuited and printed nothing at all (2026-08-31).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"

# Dry run needs no key. Only fetch one when we are actually sending.
if [[ "${1:-}" == "--send" || "${1:-}" == "--test" ]]; then
  echo "fetching Mailgun key from gammarips-webapp ..." >&2
  MAILGUN_API_KEY="$(
    gcloud run services describe gammarips-webapp \
      --project=profitscout-fida8 --region=us-central1 --format=json \
    | python3 -c "import json,sys; env=json.load(sys.stdin)['spec']['template']['spec']['containers'][0]['env']; print(next(e['value'] for e in env if e['name']=='MAILGUN_API_KEY'))"
  )"
  if [[ -z "${MAILGUN_API_KEY//[[:space:]]/}" ]]; then
    echo "ERROR: Mailgun key came back empty. Nothing sent." >&2
    exit 1
  fi
  export MAILGUN_API_KEY
  echo "key loaded (${#MAILGUN_API_KEY} chars)" >&2
fi

exec python scripts/gtm/relaunch_email.py "$@"
