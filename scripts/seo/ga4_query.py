"""Read-only GA4 Data API pull for traffic-pattern analysis.

Returns sessions / engagement broken down by landing page or by
source-medium over a trailing window. **Read-only** — the Data API
cannot mutate the property; this script only ever runs reports.

Auth: Application Default Credentials, as eraphaelparra@gmail.com. That
account must be added as a *Viewer* on the GA4 property, and ADC must be
re-consented with the analytics.readonly scope (see README).
Optionally run as a service account via SEO_IMPERSONATE_SA.

Set the property id once:
    export GA4_PROPERTY_ID=123456789   # the numeric id, no 'properties/'

Run with:
    python scripts/seo/ga4_query.py --days 28 --report landing
    python scripts/seo/ga4_query.py --days 28 --report source
    python scripts/seo/ga4_query.py --report source --channel "Organic Search"
"""

import argparse
import os
import sys

import google.auth
from google.auth import impersonated_credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    OrderBy,
    RunReportRequest,
)

import bot_filter

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

# Live GammaRips GA4 property (ProfitScout/Firebase account). Override with
# GA4_PROPERTY_ID if it ever changes. The id=506898594 "GammaRips" property
# is an empty duplicate — do not use it.
DEFAULT_PROPERTY = "534472819"

REPORTS = {
    "landing": ["landingPagePlusQueryString"],
    "source": ["sessionSource", "sessionMedium"],
    "channel": ["sessionDefaultChannelGroup"],
    "country": ["country"],
}
# screenPageViews is load-bearing: it is what separates the cluster-B
# zero-pageview bot sessions from real ones. Do not drop it.
METRICS = [
    "sessions",
    "totalUsers",
    "engagedSessions",
    "userEngagementDuration",
    "screenPageViews",
]


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


def _total_sessions(client, prop: str, days: int, dim_filter) -> int:
    """One scalar: total sessions in the window, with or without a filter."""
    req = RunReportRequest(
        property=f"properties/{prop}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        metrics=[Metric(name="sessions")],
    )
    if dim_filter is not None:
        req.dimension_filter = dim_filter
    resp = client.run_report(req)
    return int(resp.rows[0].metric_values[0].value or 0) if resp.rows else 0


def run(
    prop: str,
    days: int,
    report: str,
    channel: str | None,
    limit: int,
    raw: bool,
) -> None:
    dims = REPORTS[report]

    channel_filter = None
    if channel:
        channel_filter = FilterExpression(
            filter=Filter(
                field_name="sessionDefaultChannelGroup",
                string_filter=Filter.StringFilter(value=channel),
            )
        )

    # Bot exclusion is ON unless --raw. The country report keeps every row so
    # the excluded traffic stays visible; every other report drops it.
    bot_expr = None
    if not raw and report != "country":
        bot_expr = bot_filter.exclude_countries()

    dim_filter = bot_filter.combine(channel_filter, bot_expr)

    req = RunReportRequest(
        property=f"properties/{prop}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in METRICS],
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)
        ],
        limit=limit,
    )
    if dim_filter is not None:
        req.dimension_filter = dim_filter

    client = BetaAnalyticsDataClient(credentials=get_credentials())
    resp = client.run_report(req)

    # Raw vs kept, so the header can never claim a clean number on its own.
    raw_total = _total_sessions(client, prop, days, channel_filter)
    kept_total = (
        raw_total
        if bot_expr is None
        else _total_sessions(client, prop, days, dim_filter)
    )

    label = " + ".join(dims)
    chan = f" | channel={channel}" if channel else ""
    print(f"# GA4 {report} ({label}) | prop {prop} | last {days}d{chan}")
    print(bot_filter.banner(days, raw_total, kept_total, applied=bot_expr is not None))
    if report == "country" and not raw:
        print(
            "# NOTE: the country report is never filtered — it is how you see "
            "the bot traffic."
        )
    print(
        f"{'sessions':>9} {'users':>8} {'engaged':>8} {'views':>7} "
        f"{'avg_eng_s':>10}  {label}"
    )
    clean_sessions = 0
    flagged_sessions = 0
    for row in resp.rows:
        key = " / ".join(d.value for d in row.dimension_values)
        sessions = int(row.metric_values[0].value or 0)
        users = int(row.metric_values[1].value or 0)
        engaged = int(row.metric_values[2].value or 0)
        eng_dur = float(row.metric_values[3].value or 0)
        views = int(row.metric_values[4].value or 0)
        avg_eng = eng_dur / sessions if sessions else 0.0
        automated = bot_filter.looks_automated(sessions, views)
        if automated:
            flagged_sessions += sessions
        else:
            clean_sessions += sessions
        mark = "  BOT?" if automated else ""
        print(
            f"{sessions:>9} {users:>8} {engaged:>8} {views:>7} "
            f"{avg_eng:>10.1f}  {key}{mark}"
        )

    if resp.rows:
        print(
            f"# rows shown: {clean_sessions} sessions pass the pageview test, "
            f"{flagged_sessions} are marked BOT?."
        )
        print(
            "# The flag is per ROW, not per session. A mixed row such as "
            "(direct)/(none) holds\n"
            "# real visits AND cluster-B bots, so it gets flagged whole and "
            "the pass count\n"
            "# UNDERSTATES real traffic. Read the named referral and organic "
            "rows for a floor."
        )
        print(
            "# Row sums are event-scoped and will not tie to the deduplicated "
            "totals in the header."
        )

    if not resp.rows:
        print(
            "\n(no rows — check GA4_PROPERTY_ID is the numeric id and the SA "
            "has Viewer on the property)",
            file=sys.stderr,
        )


def main() -> None:
    ap = argparse.ArgumentParser(description="Read-only GA4 Data API pull.")
    ap.add_argument(
        "--property",
        default=os.environ.get("GA4_PROPERTY_ID", DEFAULT_PROPERTY),
        help="numeric GA4 property id (default: live GammaRips property)",
    )
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--report", default="landing", choices=list(REPORTS))
    ap.add_argument(
        "--channel", default=None, help='filter by channel, e.g. "Organic Search"'
    )
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument(
        "--raw",
        action="store_true",
        help="disable bot exclusion. Output is then unusable as a traffic number.",
    )
    args = ap.parse_args()

    if not args.property:
        ap.error("GA4 property id required: pass --property or set GA4_PROPERTY_ID")
    run(args.property, args.days, args.report, args.channel, args.limit, args.raw)


if __name__ == "__main__":
    main()
