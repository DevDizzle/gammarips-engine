"""Bot exclusion for GA4 pulls. Read-only helper, no API calls of its own.

Why this exists
---------------
On 2026-08-31 a review of GA4 property 534472819 found that half of all
recorded sessions were one scraper, and much of the remainder was a second bot
population. Any number read off this property without filtering is fiction.
Two separate populations were identified, and they need different treatment.

Get the arithmetic right before quoting a share. The `country` DIMENSION is
event-scoped and its rows sum well above the deduplicated session total, so
dividing a country row by that total is meaningless. Doing exactly that
produced a wrong "82% of traffic is Singapore" on 2026-08-31. The correct
like-for-like comparison uses two deduplicated scalars: 60 days to 2026-08-31,
total 2,513 sessions, 1,255 surviving the Singapore exclusion, so 1,258
sessions (50.1%) were Singapore-only.

**Cluster A, the Singapore scraper. EXCLUDED by default.**
60 days to 2026-08-31: 1,258 of 2,513 sessions (50.1%), all `(direct) / (none)`,
1.00 users per session, 1.00 pageviews per session, 3.4s average duration
(0.0s on the 08-29 sweep). Three full-site sweeps (07-27: 699, 08-04: 390,
08-29: 293) over a ~10/day baseline. It targets the ticker pages: `/signals/*`
took 1,617 Singapore sessions against 46 US sessions.

Identified from the Firebase App Hosting edge log, which is the only log that
keeps the real client (Cloud Run's own request log shows the CDN, userAgent
"Google"). On 08-29 the agent was a bare
`Chrome/145.0.0.0 ... Macintosh` string with no bot token, spread over
**388 distinct IPs in 600 requests**, 95% inside `43.119.0.0/16`
(Alibaba Cloud Singapore Pte Ltd) and `47.82.0.0/16` (Alibaba Cloud LLC).
Rotating pool, spoofed consumer UA, executes JavaScript, which is why it fires
gtag when Googlebot / Applebot / OAI-SearchBot / Bytespider do not.

**Cluster B, the zero-pageview network. FLAGGED, never silently dropped.**
Sessions with ZERO `screenPageViews` but 20-26s duration and engagedSessions
almost equal to sessions. A session cannot be engaged for 20 seconds and view
no page. It is spread across ~25 countries (Vietnam 92 sessions / 0 pageviews,
Ukraine 27 / 0, Brazil 131 / 1, Mexico, Argentina, Bangladesh, Chile, Kenya,
Tunisia, ...) and it contaminates countries that also hold real users, France
and India among them. A country denylist would therefore throw away real
traffic to remove it, so this module refuses to guess. Rows matching the
signature are MARKED in the output and left in the totals for the reader to
judge.

Rule for anything built on this module: never emit a filtered number without
the raw number and the exclusion list beside it. A clean total that reconciles
perfectly against itself, with no note about what was removed, is the failure
mode this file exists to prevent.
"""

from __future__ import annotations

from google.analytics.data_v1beta.types import Filter, FilterExpression, FilterExpressionList

# Cluster A. Country is a coarse proxy for "the Alibaba Singapore scraper",
# and it is accurate here only because the property has effectively no real
# Singapore audience (46 US sessions vs 1,617 Singapore sessions on the ticker
# pages over the same 60 days). Re-check before assuming it still holds: if
# real Singapore users ever appear, this exclusion starts hiding them.
SCRAPER_COUNTRIES: tuple[str, ...] = ("Singapore",)

# Cluster B threshold. Below this many pageviews per session a row is marked
# as suspected automation. Real rows in this property run 1.0-1.4.
MIN_PAGEVIEWS_PER_SESSION = 0.5

EVIDENCE_DATE = "2026-08-31"


def exclude_countries(countries: tuple[str, ...] = SCRAPER_COUNTRIES) -> FilterExpression:
    """A FilterExpression that drops the named countries."""
    return FilterExpression(
        not_expression=FilterExpression(
            filter=Filter(
                field_name="country",
                in_list_filter=Filter.InListFilter(values=list(countries)),
            )
        )
    )


def combine(*expressions: FilterExpression | None) -> FilterExpression | None:
    """AND together the expressions that are not None."""
    present = [e for e in expressions if e is not None]
    if not present:
        return None
    if len(present) == 1:
        return present[0]
    return FilterExpression(
        and_group=FilterExpressionList(expressions=present)
    )


def looks_automated(sessions: int, pageviews: int) -> bool:
    """Cluster B signature: sessions that record (almost) no pageviews."""
    if sessions <= 0:
        return False
    return (pageviews / sessions) < MIN_PAGEVIEWS_PER_SESSION


def banner(days: int, raw_sessions: int, kept_sessions: int, applied: bool) -> str:
    """The header every GA4 pull prints. States what was removed, always."""
    if not applied:
        return (
            f"# RAW MODE. No bot exclusion applied. {raw_sessions} sessions in {days}d.\n"
            f"# About half of this property is one scraper, and a second bot\n"
            f"# population sits inside the remainder (evidence {EVIDENCE_DATE}).\n"
            f"# Do NOT quote these numbers as traffic."
        )
    removed = raw_sessions - kept_sessions
    pct = (removed / raw_sessions * 100) if raw_sessions else 0.0
    return (
        f"# Bot exclusion ON (evidence {EVIDENCE_DATE}): "
        f"country not in {list(SCRAPER_COUNTRIES)}\n"
        f"# sessions {days}d: raw {raw_sessions} -> kept {kept_sessions} "
        f"({removed} removed, {pct:.1f}%)\n"
        f"# Both figures are deduplicated session totals, so they are "
        f"comparable to each other.\n"
        f"# NEVER divide a country row by these. The country DIMENSION is "
        f"event-scoped and\n"
        f"# over-counts: its rows sum well above the total. That mismatch "
        f"produced a wrong\n"
        f"# 82% bot share on {EVIDENCE_DATE}; the like-for-like figure is the "
        f"{pct:.1f}% above.\n"
        f"# Rows marked BOT? show <{MIN_PAGEVIEWS_PER_SESSION} pageviews/session "
        f"and are KEPT in the\n"
        f"# totals above. They are a SECOND bot population. Judge them, do not "
        f"assume."
    )
