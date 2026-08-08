"""Read-only Google Search Console URL Inspection pull.

Answers the question the Search Analytics API cannot: *is this URL actually
indexed, and which URL does Google think is canonical?* That is the only
programmatic way to verify a "Page indexing issue fixed" validation held,
and to catch a canonical the site declares but Google overrides.

For each URL it reports the index verdict, coverage state, Google's chosen
canonical vs the one the page declares, and the last crawl time — and flags
CANONICAL MISMATCH (google != user) plus any non-PASS verdict.

**Read-only** — inspection never submits, reindexes, or mutates anything.

Quota: 2,000 inspections/day and 600/minute per property. --limit defaults
to 25 so a careless run cannot burn the daily budget.

Auth: same as gsc_query.py — ADC as eraphaelparra@gmail.com, re-consented
with the webmasters.readonly scope (`scripts/seo/reauth.sh`).

Run with:
    python scripts/seo/gsc_inspect.py --url https://gammarips.com/signals/AAPL
    python scripts/seo/gsc_inspect.py --sitemap --limit 25
    python scripts/seo/gsc_inspect.py --file urls.txt --limit 50
"""

import argparse
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

import google.auth
from google.auth import impersonated_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_SITE = os.environ.get("GSC_SITE_URL", "sc-domain:gammarips.com")
DEFAULT_SITEMAP = os.environ.get("GSC_SITEMAP_URL", "https://gammarips.com/sitemap.xml")

# Inspection is 600/min; 0.2s between calls keeps us an order of magnitude under.
THROTTLE_SECONDS = 0.2


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


def urls_from_sitemap(sitemap_url: str) -> list[str]:
    with urllib.request.urlopen(sitemap_url, timeout=60) as resp:
        root = ET.fromstring(resp.read())
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text.strip() for loc in root.findall(".//sm:url/sm:loc", ns) if loc.text]


def inspect(service, site: str, url: str) -> dict:
    resp = (
        service.urlInspection()
        .index()
        .inspect(body={"inspectionUrl": url, "siteUrl": site})
        .execute()
    )
    return resp.get("inspectionResult", {}).get("indexStatusResult", {})


def run(site: str, urls: list[str], verbose: bool) -> int:
    service = build("searchconsole", "v1", credentials=get_credentials())

    print(f"# GSC URL inspection | {site} | {len(urls)} urls")
    print(f"{'verdict':<8} {'coverageState':<44} url")
    print("-" * 110)

    problems: list[tuple[str, str]] = []
    for i, url in enumerate(urls):
        if i:
            time.sleep(THROTTLE_SECONDS)
        try:
            r = inspect(service, site, url)
        except HttpError as e:
            print(f"{'ERROR':<8} {str(e.status_code):<44} {url}")
            problems.append((url, f"api error {e.status_code}"))
            continue

        verdict = r.get("verdict", "?")
        coverage = r.get("coverageState", "?")
        user_canon = r.get("userCanonical") or ""
        goog_canon = r.get("googleCanonical") or ""

        print(f"{verdict:<8} {coverage:<44} {url}")

        if verbose:
            print(
                f"         crawled={r.get('lastCrawlTime', '-')} "
                f"robots={r.get('robotsTxtState', '-')} "
                f"indexing={r.get('indexingState', '-')}"
            )
            if user_canon or goog_canon:
                print(f"         user_canonical={user_canon or '-'}")
                print(f"         google_canonical={goog_canon or '-'}")

        if user_canon and goog_canon and user_canon != goog_canon:
            print(f"         !! CANONICAL MISMATCH: google chose {goog_canon}")
            problems.append((url, f"canonical mismatch -> {goog_canon}"))
        elif verdict != "PASS":
            problems.append((url, f"{verdict}: {coverage}"))

    print("-" * 110)
    if problems:
        print(f"\n{len(problems)} of {len(urls)} URLs need attention:")
        for url, why in problems:
            print(f"  {url}\n      {why}")
    else:
        print(f"\nAll {len(urls)} URLs PASS with the declared canonical honored.")
    return len(problems)


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only GSC URL Inspection pull.")
    ap.add_argument("--site", default=DEFAULT_SITE, help="GSC property URL")
    ap.add_argument("--url", action="append", default=[], help="URL to inspect (repeatable)")
    ap.add_argument("--file", help="file of URLs, one per line (# comments ok)")
    ap.add_argument("--sitemap", nargs="?", const=DEFAULT_SITEMAP, help="pull URLs from a sitemap")
    ap.add_argument("--limit", type=int, default=25, help="max URLs to inspect (quota guard)")
    ap.add_argument("-v", "--verbose", action="store_true", help="show canonicals + crawl detail")
    args = ap.parse_args()

    urls = list(args.url)
    if args.file:
        with open(args.file) as fh:
            urls += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if args.sitemap:
        urls += urls_from_sitemap(args.sitemap)

    if not urls:
        ap.error("no URLs — pass --url, --file, or --sitemap")

    seen: set[str] = set()
    deduped = [u for u in urls if not (u in seen or seen.add(u))]
    if len(deduped) > args.limit:
        print(
            f"# {len(deduped)} URLs supplied, inspecting the first {args.limit} "
            f"(raise with --limit; quota is 2000/day)",
            file=sys.stderr,
        )
        deduped = deduped[: args.limit]

    sys.exit(1 if run(args.site, deduped, args.verbose) else 0)


if __name__ == "__main__":
    main()
