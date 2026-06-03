"""Read-only Google Search Console pull for organic-click analysis.

Returns top queries / pages by clicks, impressions, CTR, and average
position over a trailing window. **Read-only** — never submits sitemaps,
deletes URLs, or mutates the property. The output shape is stable so the
SEO subagent can diff it week over week.

Auth: Application Default Credentials, as eraphaelparra@gmail.com. That
account must be added as a *user* on the Search Console property, and ADC
must be re-consented with the webmasters.readonly scope (see README).
Optionally run as a service account via SEO_IMPERSONATE_SA.

Run with:
    python scripts/seo/gsc_query.py --days 28 --dim query --limit 50
    python scripts/seo/gsc_query.py --days 28 --dim page
    SEO_IMPERSONATE_SA=406581297632-compute@developer.gserviceaccount.com \
        python scripts/seo/gsc_query.py --dim query
"""

import argparse
import datetime as dt
import os
import sys

import google.auth
from google.auth import impersonated_credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_SITE = os.environ.get("GSC_SITE_URL", "sc-domain:gammarips.com")


def get_credentials():
    creds, _ = google.auth.default(scopes=SCOPES)
    target = os.environ.get("SEO_IMPERSONATE_SA")
    if target:
        creds = impersonated_credentials.Credentials(
            source_credentials=creds,
            target_principal=target,
            target_scopes=SCOPES,
        )
    return creds


def run(site: str, days: int, dim: str, limit: int) -> None:
    # GSC data lags ~2-3 days; offset the window end to avoid empty tail rows.
    end = dt.date.today() - dt.timedelta(days=3)
    start = end - dt.timedelta(days=days)

    service = build("searchconsole", "v1", credentials=get_credentials())
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": [dim],
        "rowLimit": limit,
        "dataState": "final",
    }
    resp = (
        service.searchanalytics()
        .query(siteUrl=site, body=body)
        .execute()
    )
    rows = resp.get("rows", [])

    print(f"# GSC {dim} | {site} | {start} .. {end} | {len(rows)} rows")
    print(f"{'clicks':>7} {'impr':>8} {'ctr%':>6} {'pos':>6}  {dim}")
    for r in rows:
        key = r["keys"][0]
        print(
            f"{int(r['clicks']):>7} {int(r['impressions']):>8} "
            f"{r['ctr'] * 100:>6.2f} {r['position']:>6.1f}  {key}"
        )

    if not rows:
        print(
            "\n(no rows — check the SA has access to this property and the "
            "GSC_SITE_URL prefix is correct, e.g. 'sc-domain:gammarips.com' "
            "vs 'https://gammarips.com/')",
            file=sys.stderr,
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only Search Console pull.")
    ap.add_argument("--site", default=DEFAULT_SITE, help="GSC property URL")
    ap.add_argument("--days", type=int, default=28, help="trailing window")
    ap.add_argument(
        "--dim", default="query", choices=["query", "page", "country", "device"]
    )
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()
    run(args.site, args.days, args.dim, args.limit)


if __name__ == "__main__":
    main()
