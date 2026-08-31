# scripts/seo/ — read-only SEO/traffic data pulls

Thin CLIs the `gammarips-seo` subagent calls to analyze organic traffic.
Both are **read-only**: they only run reports, never mutate the GA4 or
Search Console properties.

| Script | Source API | What it pulls |
|---|---|---|
| `gsc_query.py` | Search Console API | top queries/pages by clicks, impressions, CTR, position |
| `gsc_inspect.py` | Search Console URL Inspection API | per-URL index verdict, coverage state, Google's chosen canonical vs ours |
| `ga4_query.py` | GA4 Data API | sessions/users/engagement by landing page or source-medium, **bot-filtered by default** |
| `bot_filter.py` | (no API) | the bot exclusion every GA4 pull applies, plus the evidence for it |

`gsc_query.py` answers "what ranks"; `gsc_inspect.py` answers "is it indexed
at all, and did Google honor our canonical" — the only programmatic way to
verify a GSC "issue fixed" validation actually held. Inspection quota is
2,000/day and 600/min per property, so it defaults to 25 URLs per run.

## Bot traffic — read this before quoting any GA4 number

This property is majority automated traffic. Two separate populations, found
2026-08-31:

- **The Singapore scraper.** 1,258 of 2,513 sessions over 60 days (50.1%).
  Headless Chrome on a rotating Alibaba Cloud Singapore IP pool (388 distinct
  IPs in 600 requests on 08-29), spoofed consumer user agent, no bot token. It
  executes JavaScript, so it fires gtag where Googlebot and Applebot do not. It
  sweeps the whole site every few weeks and targets `/signals/*`.
  `ga4_query.py` **excludes it by default**; pass `--raw` to see it.
- **The zero-pageview network.** Sessions with 0 pageviews but 20-26s duration
  and engaged=sessions, spread over ~25 countries including ones with real
  users (France, India). No country denylist can remove it without throwing
  away real traffic, so rows matching the signature are **marked `BOT?` and
  left in the totals**. Judge them; do not assume.

Two rules that cost a session to learn:

1. **Never divide a country row by the session total.** The `country`
   dimension is event-scoped and its rows sum well above the deduplicated
   total. That error produced a wrong "82% of traffic is Singapore". Compare
   deduplicated scalars only, which is what the script's header now does.
2. **The `BOT?` flag is per row, not per session.** A mixed row such as
   `(direct)/(none)` holds real visits and bots together and gets flagged
   whole, so the pass count understates real traffic. Use the named referral
   and organic rows as the floor.

The `country` report is deliberately never filtered — it is how you see the
bot traffic. Every other report filters and prints raw vs kept in its header.

## Auth — read this before debugging a 403

Auth is service-account impersonation. This is the only path that works:

```bash
export SEO_IMPERSONATE_SA=ga-admin@profitscout-fida8.iam.gserviceaccount.com
```

The `seo-auth` skill (`.claude/skills/seo-auth/`) is the runbook. It carries
the diagnostic table (three different 403s look identical), the one-time IAM
binding, the property grants, and the traps. Invoke it on any auth failure.

**The user-ADC path is DEAD.** Google blocked the shared gcloud client ID from
the Search Console and Analytics scopes (confirmed 2026-08-08). Do not run
`gcloud auth application-default login` with those scopes. `reauth.sh` is
decommissioned.

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

### 2. Set up impersonation
Follow Path A in the `seo-auth` skill: the token-creator IAM binding, the SA
grants on the Search Console and GA4 properties, and the
`SEO_IMPERSONATE_SA` export (persist it in `~/.bashrc`).

### 3. Tell the scripts where to look
```bash
export GA4_PROPERTY_ID=123456789          # numeric id, no 'properties/' prefix
export GSC_SITE_URL=sc-domain:gammarips.com   # or https://gammarips.com/
```

## Auth notes

- `SEO_IMPERSONATE_SA` must be set. If you leave it unset, the scripts run
  as your user ADC, which can no longer get the scopes (dead path above).
- Plain ADC (no extra scopes) as eraphaelparra@gmail.com still supplies the
  source credentials that impersonation builds on.

## Examples
```bash
PY=scripts/seo/.venv/bin/python
$PY scripts/seo/gsc_query.py --days 28 --dim query --limit 50
$PY scripts/seo/gsc_query.py --days 28 --dim page
$PY scripts/seo/gsc_inspect.py --url https://gammarips.com/signals/AAPL -v
$PY scripts/seo/gsc_inspect.py --sitemap --limit 25
$PY scripts/seo/ga4_query.py --days 28 --report landing
$PY scripts/seo/ga4_query.py --report source --channel "Organic Search"
$PY scripts/seo/ga4_query.py --days 60 --report country   # see the bots
$PY scripts/seo/ga4_query.py --days 60 --report source --raw  # no filtering
```

`gsc_inspect.py` exits non-zero when any URL fails or Google overrode our
canonical, so it drops straight into a check script.
