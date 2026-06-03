# scripts/seo/ — read-only SEO/traffic data pulls

Thin CLIs the `gammarips-seo` subagent calls to analyze organic traffic.
Both are **read-only**: they only run reports, never mutate the GA4 or
Search Console properties.

| Script | Source API | What it pulls |
|---|---|---|
| `gsc_query.py` | Search Console API | top queries/pages by clicks, impressions, CTR, position |
| `ga4_query.py` | GA4 Data API | sessions/users/engagement by landing page or source-medium |

## One-time setup

### 1. Install deps (self-contained venv via uv)
The system python is externally-managed, so deps live in a local venv:
```bash
uv venv scripts/seo/.venv --python 3.12
uv pip install --python scripts/seo/.venv/bin/python \
  google-api-python-client google-analytics-data google-auth
```
The venv is git-ignored. Always run the scripts with its python:
`scripts/seo/.venv/bin/python`.

### 2. Grant your Google account access
We auth via Application Default Credentials as **eraphaelparra@gmail.com**.
Grant that account:

- **GA4** → Admin → Property Access Management → add the email as **Viewer**
- **Search Console** → Settings → Users and permissions → add the email as **Full** or **Restricted** user

### 3. Re-consent ADC with the analytics + search-console scopes
A plain `gcloud auth application-default login` does NOT carry the GA4 /
Search Console read scopes, so the API calls will 403 even with property
access. Re-run login with the scopes explicitly (one time):

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
```

### 4. Tell the scripts where to look
```bash
export GA4_PROPERTY_ID=123456789          # numeric id, no 'properties/' prefix
export GSC_SITE_URL=sc-domain:gammarips.com   # or https://gammarips.com/
```

## Auth notes

- Locally, ADC resolves to your user account — that's why we grant
  **eraphaelparra@gmail.com** on the properties directly.
- `SEO_IMPERSONATE_SA` is still supported if you ever want to run these as
  a service account (e.g. from Cloud Run); leave it unset to run as you.

## Examples
```bash
PY=scripts/seo/.venv/bin/python
$PY scripts/seo/gsc_query.py --days 28 --dim query --limit 50
$PY scripts/seo/gsc_query.py --days 28 --dim page
$PY scripts/seo/ga4_query.py --days 28 --report landing
$PY scripts/seo/ga4_query.py --report source --channel "Organic Search"
```
