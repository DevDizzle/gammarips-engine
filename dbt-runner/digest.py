"""Daily freshness digest — the one artifact that answers "is everything firing?"

WHY THIS EXISTS (2026-08-07). The engine had no operator-visible health signal.
`dbt-source-freshness` ran daily but returned HTTP 200 unconditionally, so Cloud
Scheduler showed green no matter what and the report sat unread in a response
body; `underlying_daily_bars` went 37 days stale and `signal_performance`'s check
hard-errored for 10 days, both invisibly. That endpoint now goes red
(docs/DECISIONS/2026-08-07-freshness-canary-and-bars-loader.md) — but red is only
visible to someone who opens the console. This digest is the push half: one email,
every weekday morning, that the operator reads instead of going to look.

DESIGN RULE, non-negotiable: **a section that could not be checked must say so.**
Every section carries its own status, and `unknown` propagates to the subject
line. A green digest that is green because a check silently failed is strictly
worse than no digest — it converts "I don't know" into "I'm fine." That is the
exact failure mode this whole workstream exists to kill, so it must not be
reintroduced by the thing meant to prevent it.

READ-ONLY. Queries BigQuery and the Cloud Scheduler API, sends one email. It
writes nothing, anywhere.
"""

import logging
import os
from datetime import datetime, timedelta

import pytz
import requests
from google.cloud import bigquery

logger = logging.getLogger(__name__)

# Hardcoded, NOT os.environ with a fallback. A getenv-with-default here is the
# documented workstation footgun (memory `workstation-project-id-env-footgun`):
# the shell exports PROJECT_ID=profitscout-lx6bb, so any local run of this module
# would silently read the wrong project and report health for the wrong engine.
# Same convention as forward-paper-trader/main.py.
PROJECT_ID = "profitscout-fida8"
REGION = "us-central1"
EST = pytz.timezone("America/New_York")

MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", "").strip()
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "").strip()
MAILGUN_SENDER = f"GammaRips Engine <mailgun@{MAILGUN_DOMAIN}>"
RECIPIENT_EMAIL = os.environ.get("DIGEST_RECIPIENT", "eraphaelparra@gmail.com").strip()

OK, ATTENTION, UNKNOWN = "ok", "attention", "unknown"
_RANK = {OK: 0, ATTENTION: 1, UNKNOWN: 2}

# NOTE: an explicit KNOWN_PAUSED allowlist was written here and then deleted.
# It was unreachable in the direction it was meant to help and reachable only in
# the direction that hurts: a genuinely paused job already has state == "PAUSED"
# and is skipped before any name check, so the set could never suppress the
# crying-wolf it was written for — its ONLY live effect would have been to hide
# a job that had been re-enabled and was now failing. The state check alone is
# both sufficient and safer.

# (label, table, date column). The dbt freshness section already catches "this
# table STOPPED"; this grid catches the other failure — a HOLE in the middle,
# where collection resumed and nothing looks stale.
COVERAGE_TABLES = [
    ("scan",       "overnight_signals",           "scan_date"),
    ("enriched",   "overnight_signals_enriched",  "scan_date"),
    ("ledger",     "forward_paper_ledger",        "scan_date"),
    ("shadow",     "paper_shadow_topscore",       "scan_date"),
    ("outcomes",   "enriched_option_outcomes",    "entry_day"),
    ("minutepath", "option_minute_paths",         "entry_day"),
    ("iv",         "polygon_iv_history",          "as_of_date"),
    ("liquidity",  "pool_liquidity_snapshot",     "DATE(as_of)"),
    ("bars",       "underlying_daily_bars",       "date"),
]


def _worst(*statuses: str) -> str:
    return max(statuses, key=lambda s: _RANK.get(s, 2))


# ---------------------------------------------------------------- coverage ---

def coverage_section(client: bigquery.Client, lookback_days: int = 12) -> dict:
    """Per-table daily row counts over recent weekdays, and any GAP.

    A gap = a weekday with zero rows for a table that has non-zero rows on a
    MORE RECENT day. Defining it that way makes the check immune to per-table
    write lag (the ledger writes scan_date D on the evening of D+1, the scanner
    writes D at 23:00 ET on D, and so on) without hardcoding nine different lag
    constants that would rot. Trailing zeros are simply "hasn't run yet"; the
    dbt freshness section is what catches a table that stopped for good.
    """
    try:
        parts = []
        for label, table, col in COVERAGE_TABLES:
            # DATE({col}) uniformly: overnight_signals_enriched.scan_date is
            # documented as ambiguously DATE-or-DATETIME across writer eras, and
            # a type mismatch would fail the whole UNION — pinning this section
            # to UNKNOWN permanently. Fail-safe, but a dark section is still a
            # dark section.
            parts.append(f"""
            SELECT '{label}' AS label, DATE({col}) AS d, COUNT(*) AS n
            FROM `{PROJECT_ID}.profit_scout.{table}`
            WHERE DATE({col}) >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY)
              AND DATE({col}) < CURRENT_DATE()
            GROUP BY d""")
        sql = "\nUNION ALL\n".join(parts)
        rows = list(client.query(sql).result())

        by_label: dict[str, dict] = {}
        for r in rows:
            by_label.setdefault(r["label"], {})[r["d"]] = int(r["n"])

        # Weekdays in range, newest first. NYSE holidays are NOT excluded — a
        # holiday shows as a zero for every table at once, which reads as an
        # obvious full-width blank rather than a per-table gap, and adding a
        # calendar dependency here would be a new failure mode for a cosmetic win.
        today = datetime.now(EST).date()
        days = []
        d = today - timedelta(days=1)
        while d > today - timedelta(days=lookback_days):
            if d.weekday() < 5:
                days.append(d)
            d -= timedelta(days=1)

        gaps, grid, silent = [], [], []
        for label, _, _ in COVERAGE_TABLES:
            counts = by_label.get(label, {})
            newest_with_data = max((dd for dd, n in counts.items() if n > 0), default=None)
            # A table with NO data anywhere in the window produces no gaps under
            # the relational rule — there is no newer data to make a hole a hole
            # — so it would read OK forever. "Stopped entirely" is supposed to be
            # the freshness section's job, but that only holds for tables that
            # HAVE a freshness declaration (pool_liquidity_snapshot did not), and
            # anything on error_after: 168h is blind for a week regardless.
            # Flagging here closes the class instead of the instance.
            if newest_with_data is None:
                silent.append(label)
            row = {"label": label, "cells": []}
            for dd in days:
                n = counts.get(dd, 0)
                is_gap = (n == 0 and newest_with_data is not None and dd < newest_with_data)
                row["cells"].append({"date": dd, "n": n, "gap": is_gap})
                if is_gap:
                    gaps.append(f"{label} {dd.isoformat()}")
            grid.append(row)

        # A whole day blank across EVERY table. Probably a market holiday — and
        # indistinguishable from a total collection outage without a calendar we
        # deliberately do not depend on. It must NOT be suppressed: six of these
        # nine tables are Polygon-derived, so one vendor outage, billing lapse or
        # region incident zeroes all nine at once, and because collection resumes
        # the next day `max(loaded_at)` is fresh again and the freshness section
        # never fires either. Suppressing would erase the one failure mode that
        # is otherwise BOTH permanent and invisible. So: report UNKNOWN and make
        # a human look. Same rule this module enforces everywhere else — "could
        # not determine" never renders as "fine" — applied to its own blind spot.
        # Cost: eyeballing ~9 holidays a year. Worth it.
        blank_days = sorted(
            dd.isoformat() for dd in days
            if all(by_label.get(lbl, {}).get(dd, 0) == 0 for lbl, _, _ in COVERAGE_TABLES)
        )
        gaps = [g for g in gaps if g.split()[-1] not in blank_days]

        status = ATTENTION if (gaps or silent) else OK
        if blank_days:
            status = UNKNOWN

        return {"status": status, "days": days, "grid": grid, "gaps": gaps,
                "blank_days": blank_days, "silent": silent}
    except Exception as e:  # noqa: BLE001
        logger.error(f"digest coverage section failed: {e}")
        return {"status": UNKNOWN, "error": str(e)[:400], "days": [], "grid": [],
                "gaps": [], "blank_days": [], "silent": []}


# --------------------------------------------------------------- scheduler ---

def scheduler_section() -> dict:
    """Cloud Scheduler job health.

    CAVEAT baked into the output: `lastAttemptTime` is NOT reliable — on
    2026-08-07 it reported blog-generator-weekly's last run as 07-27 while a post
    had demonstrably published on 08-03. So this flags ONLY an explicit non-zero
    last status code, and never infers a miss from a stale timestamp. Under-
    reporting beats crying wolf on a field that lies.
    """
    try:
        import google.auth
        import google.auth.transport.requests as gart

        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(gart.Request())
        url = (f"https://cloudscheduler.googleapis.com/v1/projects/{PROJECT_ID}"
               f"/locations/{REGION}/jobs?pageSize=500")
        jobs, token = [], None
        for _ in range(20):  # bounded: a stuck nextPageToken must not spin to timeout
            r = requests.get(url + (f"&pageToken={token}" if token else ""),
                             headers={"Authorization": f"Bearer {creds.token}"}, timeout=30)
            r.raise_for_status()
            body = r.json()
            jobs.extend(body.get("jobs", []))
            token = body.get("nextPageToken")
            if not token:
                break

        failing, never_run = [], []
        for j in jobs:
            name = j.get("name", "").split("/")[-1]
            state = j.get("state")
            # Skip ONLY deliberately-paused jobs. The earlier filter was
            # `state != "ENABLED"`, which also skipped UPDATE_FAILED and
            # DISABLED — and Cloud Scheduler documents DISABLED as "disabled by
            # the system due to error". That silently ignored the jobs in the
            # WORST condition and returned OK.
            if state == "PAUSED":
                continue
            if state in ("UPDATE_FAILED", "DISABLED"):
                failing.append({"name": name, "code": state,
                                "message": "job is in a system-error state"})
                continue
            # lastAttemptTime FIRST. A job that has never fired reports
            # status.code = -1 (not a gRPC code; the API's "no result yet"),
            # which is indistinguishable from a failure if you read the code
            # alone — a newly-created job would be reported as broken on its
            # first morning. Never-attempted is informational, not a failure.
            if not j.get("lastAttemptTime"):
                never_run.append(name)
                continue
            code = (j.get("status") or {}).get("code")
            if code not in (None, 0):
                failing.append({"name": name, "code": code,
                                "message": (j.get("status") or {}).get("message", "")[:200]})

        return {"status": ATTENTION if failing else OK, "failing": failing,
                "never_run": never_run,
                # Count what was actually CHECKED, not what is enabled — a
                # denominator that disagrees with the check is how a reader
                # concludes more was verified than was.
                "checked_total": sum(1 for j in jobs if j.get("state") != "PAUSED")}
    except Exception as e:  # noqa: BLE001
        logger.error(f"digest scheduler section failed: {e}")
        # Key MUST match the success path — the renderer reads `checked_total`,
        # and a mismatch is a latent KeyError the moment anyone surfaces this
        # count outside the UNKNOWN branch. A render_html crash means no email,
        # which is the one failure this artifact cannot report on itself.
        return {"status": UNKNOWN, "error": str(e)[:400],
                "failing": [], "never_run": [], "checked_total": 0}


# ------------------------------------------------------------- life surface ---

def life_surface_section(client: bigquery.Client) -> dict:
    """Public full-life cohort health — the surface that silently froze for a
    month in 2026-07.

    Watches BOTH halves of that failure, which are different:
    - `PARTIAL_NO_EXPIRY` climbing = the bars cache stopped feeding a labeler
      that is still running (the 726-row incident). Symptom of a broken input.
    - `life_labeled_at` going stale = the labeler itself stopped. Nothing
      strands, counts simply FREEZE, and a count-only check reads OK while the
      public cohort is frozen exactly as before. Symptom of a broken worker.
    Watching only the first would have caught history and missed the next one.
    """
    try:
        # The "labeler stopped" signal is RELATIONAL, not a time threshold: a
        # backlog of expired-but-unlabeled rows that is not draining. An earlier
        # version alarmed on MAX(life_labeled_at) age > 96h, which was an
        # unmeasured write-lag constant — the exact thing the coverage section
        # deliberately refuses to hardcode. It was also wrong: life_labeled_at
        # only advances when a merge happens, and run_label_life_surface returns
        # early with candidates=0 when nothing newly expired. Option expirations
        # cluster on Fridays, so a Tue/Wed/Thu with no prior expiries advances
        # nothing while the labeler runs perfectly — a false ATTENTION, which on
        # a daily digest is how the reader learns to ignore it.
        # The backlog is ~0 whenever the labeler runs and grows monotonically
        # once it stops, immune to expiry clustering, with no constant to rot.
        # The queue predicates mirror run_label_life_surface's exactly, so rows
        # it would never pick up (NULL contract/strike) cannot register as a
        # phantom backlog that never clears.
        #
        # The cutoff counts TRADING SESSIONS, not calendar days (fixed
        # 2026-08-10). It was `CURRENT_DATE() - 2 DAY`, which reintroduced the
        # very false ATTENTION the paragraph above exists to prevent, one rung
        # down: run_label_life_surface queues on `recommended_expiration <
        # today ET` and only runs weekdays 17:10 ET, so Friday's expiries first
        # become eligible on Saturday and get their first run Monday 17:10 —
        # but by Monday 07:15 they are already "2 calendar days" expired. Option
        # expirations cluster on Fridays, so EVERY Monday digest reported the
        # whole Friday cluster as a stopped labeler (2026-08-10: 78 rows, all
        # expiring 2026-08-07, labeler perfectly healthy).
        # The unit is LABELER RUNS, not calendar days and not market sessions:
        # a row is counted only after TWO 17:10 runs have had a chance at it,
        # which is what the old rule meant on a Tue/Wed/Thu and got wrong across
        # a weekend. Verified against every weekday — a row expiring Mon first
        # counts Thu, Tue->Fri, Wed->Mon, Thu->Tue, Fri->Wed, all at exactly two
        # missed runs. The cutoff is monotone non-decreasing over the week, so a
        # counted row never drops back out and a growing backlog cannot read as
        # a recovering one.
        # WEEKDAY ARITHMETIC IS EXACT HERE — do NOT "fix" it toward an NYSE
        # market calendar. label-life-surface is `10 17 * * 1-5` on Cloud
        # Scheduler (forward-paper-trader/deploy.sh), which has no holiday
        # awareness: it fires on market holidays, its queue is calendar-based
        # (`recommended_expiration < @today`), and its bars input is T-1, so a
        # holiday run labels normally. A market-calendar "correction" would push
        # the cutoff OLDER in a holiday week (Wed after a Monday holiday: Fri
        # instead of Mon), excluding the Friday cluster for an extra day. That
        # is a real detection hole introduced by a well-meaning fix.
        # THE ACTUAL RESIDUAL, since the holiday one does not exist: this is
        # correct only while (a) the digest reads BEFORE the day's 17:10 run and
        # (b) the labeler stays on a weekday cron. If freshness-digest moves past
        # 17:10 ET the check quietly requires three missed runs (slower, safe).
        # If label-life-surface ever moves to a 7-day cron the CASE becomes wrong
        # in the UNSAFE direction — it would demand two weekday runs while three
        # or four had actually elapsed. Re-derive the offsets if either moves.
        sql = f"""
        WITH labeled AS (
          SELECT life_status, life_labeled_at
          FROM `{PROJECT_ID}.profit_scout.enriched_option_outcomes`
          WHERE life_sim_version = 'LIFE_TO_EXPIRY_V1'
        ), backlog AS (
          SELECT COUNT(*) AS n
          FROM `{PROJECT_ID}.profit_scout.enriched_option_outcomes`
          WHERE life_status IS NULL
            AND recommended_expiration IS NOT NULL
            AND recommended_strike IS NOT NULL
            AND recommended_contract IS NOT NULL
            -- Two labeler runs back. Weekday cron, NOT a market calendar; see
            -- the comment above before changing these offsets.
            -- ET, not UTC, to match run_label_life_surface's `today_et`; at
            -- 07:15 ET the two dates agree, so this is a latent-bug fix only.
            AND recommended_expiration < DATE_SUB(
                  CURRENT_DATE('America/New_York'),
                  INTERVAL CASE EXTRACT(DAYOFWEEK FROM CURRENT_DATE('America/New_York'))
                             WHEN 1 THEN 3   -- Sun -> Thu
                             WHEN 2 THEN 4   -- Mon -> Thu
                             WHEN 3 THEN 4   -- Tue -> Fri
                             ELSE 2          -- Wed..Sat -> two weekdays back
                           END DAY)
        )
        SELECT l.life_status, COUNT(*) n, MAX(l.life_labeled_at) AS last_labeled,
               (SELECT n FROM backlog) AS backlog
        FROM labeled l
        GROUP BY l.life_status
        """
        rows = list(client.query(sql).result())
        counts = {r["life_status"]: int(r["n"]) for r in rows}
        stamps = [r["last_labeled"] for r in rows if r["last_labeled"]]
        last_labeled = max(stamps) if stamps else None

        backlog = int(rows[0]["backlog"]) if rows else 0
        stranded = counts.get("PARTIAL_NO_EXPIRY", 0)
        split_adj = counts.get("PARTIAL_SPLIT_ADJUSTED", 0)
        age_h = None
        if last_labeled is not None:
            age_h = (datetime.now(pytz.utc) - last_labeled).total_seconds() / 3600

        notes = []
        if stranded > 50:
            notes.append(f"PARTIAL_NO_EXPIRY={stranded} (>50): the bars cache has likely "
                         "stopped feeding the labeler — check underlying_daily_bars.")
        # >50 rather than >0: LIFE_DAILY_LIMIT caps a run at 600, so a monthly-opex
        # expiry cluster can legitimately leave a small remainder that the next
        # run clears. Sustained growth past that means the labeler is not running.
        if backlog > 50:
            # "labeler runs", not "days": the cutoff is 4 calendar days back on a
            # Mon/Tue and 2 on a Wed/Thu/Fri, so a day count would be wrong in the
            # email on three weekdays out of five — in exactly the unit whose
            # misuse produced the 2026-08-10 false positive.
            notes.append(f"{backlog} expired rows still unlabeled after 2+ labeler "
                         "runs: the labeler itself may have stopped — counts freeze "
                         "without stranding anything, so the cohort silently stops "
                         "growing.")
        if split_adj > 100:
            notes.append(f"PARTIAL_SPLIT_ADJUSTED={split_adj} (>100): unexpected growth "
                         "suggests a split-guard or unit problem, not ordinary splits.")

        return {
            # No rows at all means the cohort could not be read — UNKNOWN, never OK.
            "status": ATTENTION if notes else (OK if rows else UNKNOWN),
            "counts": counts, "stranded": stranded, "backlog": backlog,
            "last_labeled": last_labeled.isoformat() if last_labeled else None,
            # Age is INFORMATIONAL only — it does not drive status. See the query
            # comment: it is a legitimately lumpy metric, not a health signal.
            "age_hours": round(age_h, 1) if age_h is not None else None,
            "notes": notes,
        }
    except Exception as e:  # noqa: BLE001
        logger.error(f"digest life section failed: {e}")
        return {"status": UNKNOWN, "error": str(e)[:400], "counts": {},
                "stranded": None, "backlog": None, "notes": []}


# ----------------------------------------------------- opportunity surface ---

def opp_surface_section(client: bigquery.Client) -> dict:
    """Opportunity-surface (3-day MFE/MAE) fill health — the OTHER labeler.

    Why this exists (2026-08-14). The digest watched `life_status` only, so the
    single "Public life surface [OK]" badge covered one of two independent
    labelers and a reader took it as "labeling is healthy". The opportunity
    surface — the one the paid MCP serves as view="surface" — had NO row here at
    all. Its only alarm was the dbt test `assert_opp_surface_labels_fresh.sql`
    at a 10-CALENDAR-DAY threshold, so a stopped fill job stayed invisible to
    the operator for up to ten days. That is the exact surface that silently ran
    dark 2026-06-26 -> 2026-07-28, 950 rows (FINDINGS_LEDGER 2026-07-28).

    THE ALLOWANCE IS THE WHOLE POINT. `fill-closed-windows` is `30 17 * * 1-5`
    ET and this digest reads at 07:15 ET, BEFORE that day's run. So a window
    that closed yesterday has had ZERO fill attempts when this query runs, and
    calling it overdue is a guaranteed daily false alarm. That is not
    hypothetical: the MCP's `open_past_due` derives closure with no fill-run
    allowance and therefore tells a paying subscriber "This looks like a stalled
    fill job" every weekday from midnight until 17:30 ET (verified live
    2026-08-14 08:37 ET against scan_date 2026-08-10, whose fill ran on
    schedule that evening). Do not copy that predicate. Count FILL RUNS.

    Sessions, not calendar days, and the calendar is the table's own DISTINCT
    entry_day values — same no-new-dependency idiom the MCP uses. A holed or
    stale calendar undercounts elapsed sessions and would route to the
    reassuring branch, so an unusable calendar reports UNKNOWN, never OK.
    """
    try:
        sql = f"""
        WITH sessions AS (
          SELECT DISTINCT entry_day AS d
          FROM `{PROJECT_ID}.profit_scout.enriched_option_outcomes`
          WHERE entry_day IS NOT NULL
            AND entry_day >= DATE_SUB(CURRENT_DATE('America/New_York'), INTERVAL 120 DAY)
        ), cal AS (
          SELECT MAX(d) AS max_session, MAX(DATE_DIFF(d, prev_d, DAY)) AS max_gap
          FROM (SELECT d, LAG(d) OVER (ORDER BY d) AS prev_d FROM sessions)
        ), scoped AS (
          SELECT
            o.scan_date,
            o.opp_status,
            (o.opp_status IS NULL OR o.opp_status = 'WINDOW_OPEN') AS pending,
            IFNULL(o.opp_window_days, 3) - 1 AS need,
            (SELECT COUNT(*) FROM sessions s
              WHERE s.d > o.entry_day
                AND s.d < CURRENT_DATE('America/New_York')) AS elapsed
          FROM `{PROJECT_ID}.profit_scout.enriched_option_outcomes` o
          WHERE o.entry_day IS NOT NULL
            AND o.entry_day >= DATE_SUB(CURRENT_DATE('America/New_York'), INTERVAL 120 DAY)
            -- MIRROR the filler's queue exactly (_rows_needing_window_fill).
            -- A row it can never pick up would otherwise read as overdue
            -- forever, which is the phantom-backlog failure the life section
            -- documents at length. Same reason, same fix.
            AND o.recommended_strike IS NOT NULL
            AND o.recommended_expiration IS NOT NULL
            AND o.recommended_contract IS NOT NULL
        )
        SELECT
          COUNTIF(pending) AS pending_rows,
          -- window closed, but the fill cron has not had its turn yet: EXPECTED.
          COUNTIF(pending AND elapsed >= need) AS closed_awaiting_fill,
          -- two 17:30 ET runs have had a shot and did not fill it: STALLED.
          COUNTIF(pending AND elapsed >= need + 2) AS overdue_rows,
          COUNT(DISTINCT IF(pending AND elapsed >= need + 2, scan_date, NULL)) AS overdue_dates,
          MIN(IF(pending AND elapsed >= need + 2, scan_date, NULL)) AS oldest_overdue,
          MAX(IF(NOT pending, scan_date, NULL)) AS closed_frontier,
          -- Resolved-as-unusable, NOT filled. These rows are non-pending
          -- forever: the MERGE guard lets a terminal status overwrite a
          -- WINDOW_OPEN target and the filler never re-selects them. They are
          -- invisible to `overdue` by construction, so COUNT them rather than
          -- let the section read a clean OK over a growing dark set.
          COUNTIF(NOT pending AND opp_status != 'OK') AS terminal_unusable,
          (SELECT max_session FROM cal) AS max_session,
          IFNULL(
            (SELECT max_session FROM cal)
              < DATE_SUB(CURRENT_DATE('America/New_York'), INTERVAL 5 DAY)
            OR IFNULL((SELECT max_gap FROM cal), 0) > 4,
            TRUE
          ) AS calendar_unusable
        FROM scoped
        """
        row = next(iter(client.query(sql).result()), None)
        if row is None:
            return {"status": UNKNOWN, "error": "no rows returned", "notes": []}

        if row["calendar_unusable"]:
            return {
                "status": UNKNOWN,
                "error": (f"session calendar unusable (ends {row['max_session']}) — "
                          "cannot decide whether pending windows are overdue"),
                "notes": [],
            }

        overdue = int(row["overdue_rows"] or 0)
        notes = []
        if overdue > 0:
            notes.append(
                f"{overdue} row(s) across {row['overdue_dates']} scan date(s), oldest "
                f"{row['oldest_overdue']}, are still unfilled after 2+ fill-closed-windows "
                "runs — the opportunity-surface fill job has likely stopped. The paid MCP "
                "serves this surface as view=\"surface\"."
            )
            # The cron only scans scan_date BETWEEN today-10d AND today, so a row
            # that goes overdue by more than that is permanently out of its reach.
            # Without this line the note keeps saying "the job has likely stopped"
            # after the job recovers, and the reader retries the wrong fix.
            notes.append(
                "Rows older than the cron's 10-day scan_date lookback will NOT "
                "self-heal once it recovers — they need a manual backfill "
                "(scripts/ledger_and_tracking/backfill_opportunity_surface.py)."
            )
        return {
            "status": ATTENTION if notes else OK,
            "pending": int(row["pending_rows"] or 0),
            "awaiting_fill": int(row["closed_awaiting_fill"] or 0),
            "overdue": overdue,
            "terminal_unusable": int(row["terminal_unusable"] or 0),
            "closed_frontier": str(row["closed_frontier"]) if row["closed_frontier"] else None,
            "notes": notes,
        }
    except Exception as e:  # noqa: BLE001
        logger.error(f"digest opp surface section failed: {e}")
        return {"status": UNKNOWN, "error": str(e)[:400], "notes": []}


# ------------------------------------------------------------------- render ---

_CSS = (
    "font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;"
    "font-size:14px;color:#111;line-height:1.5"
)
_BADGE = {
    OK: ("#0a7", "#e8f8f2", "OK"),
    ATTENTION: ("#b00", "#fdecec", "ATTENTION"),
    UNKNOWN: ("#a60", "#fff6e5", "UNKNOWN"),
}


def _badge(status: str) -> str:
    fg, bg, label = _BADGE.get(status, _BADGE[UNKNOWN])
    return (f'<span style="background:{bg};color:{fg};border:1px solid {fg};'
            f'border-radius:3px;padding:1px 6px;font-size:11px;font-weight:600">{label}</span>')


def render_html(fresh: dict, cov: dict, sched: dict, life: dict, opp: dict,
                overall: str) -> str:
    out = [f'<div style="{_CSS}">']
    now = datetime.now(EST).strftime("%A %Y-%m-%d %H:%M ET")
    out.append(f'<h2 style="margin:0 0 2px">Engine health {_badge(overall)}</h2>')
    out.append(f'<div style="color:#666;font-size:12px;margin-bottom:16px">{now}</div>')

    if overall == UNKNOWN:
        out.append('<div style="background:#fff6e5;border-left:3px solid #a60;'
                   'padding:8px 12px;margin-bottom:16px"><b>At least one check could '
                   'not run.</b> Treat the sections marked UNKNOWN as unverified, not '
                   'as passing.</div>')

    # --- freshness
    out.append(f'<h3 style="margin:18px 0 6px">Table freshness {_badge(fresh["status"])}</h3>')
    if fresh["status"] == UNKNOWN:
        out.append(f'<div style="color:#a60">Check failed: {fresh.get("error","")}</div>')
    else:
        bad = fresh.get("not_fresh") or {}
        if bad:
            # The badge and this list are computed from DIFFERENT thresholds and
            # used to contradict each other on screen (2026-08-10: header OK
            # over ten WARN rows, which cost a consumer 15 minutes deciding
            # whether the pool-trust rule had fired). The badge is dbt's exit
            # code — only an `error_after` breach is non-zero — while the list
            # is every source past `warn_after`. Both are right; neither said
            # so. Print the severity on each row and, when they disagree, say
            # why in one line, HERE, where the wrong conclusion gets drawn.
            errs = {k: v for k, v in bad.items() if v == "ERROR"}
            warns = {k: v for k, v in bad.items() if v != "ERROR"}
            if errs and fresh["status"] != UNKNOWN:
                out.append('<div style="color:#b00;margin:4px 0"><b>Past error_after '
                           f'({len(errs)}):</b> these are what make this section red.</div>')
            out.append("<ul style='margin:4px 0'>" + "".join(
                f'<li><b>{k}</b>: <span style="color:{"#b00" if v == "ERROR" else "#a60"}">'
                f"{v}</span></li>"
                for k, v in sorted(errs.items()) + sorted(warns.items())) + "</ul>")
            # Guard on the BADGE, not merely on the absence of errors. ATTENTION
            # is driven by `rc != 0`, and dbt can exit non-zero for reasons other
            # than an error_after breach while still parsing sources — that would
            # print "which is why this section is still OK" under a red badge,
            # i.e. this fix's own contradiction, inverted.
            if warns and not errs and fresh["status"] == OK:
                out.append('<div style="color:#666;font-size:12px;margin:-2px 0 0">'
                           f'The {len(warns)} WARN row(s) above are past <code>warn_after</code> '
                           'but inside <code>error_after</code>, which is why this section is '
                           'still OK. Every weekday-written source reads ~60h old at Monday '
                           '07:00 ET, so a Monday warn is expected. Only an '
                           '<code>error_after</code> breach turns it red.</div>')
        else:
            out.append(f'<div>All {len(fresh.get("sources", {}))} sources fresh.</div>')

    # --- coverage
    out.append(f'<h3 style="margin:18px 0 6px">Collection coverage {_badge(cov["status"])}</h3>')
    if cov["status"] == UNKNOWN:
        out.append(f'<div style="color:#a60">Check failed: {cov.get("error","")}</div>')
    elif cov["grid"]:
        if cov.get("blank_days"):
            out.append('<div style="background:#fff6e5;border-left:3px solid #a60;'
                       'padding:8px 12px;margin-bottom:8px"><b>Zero rows across ALL '
                       f'{len(COVERAGE_TABLES)} tables on {", ".join(cov["blank_days"])}.'
                       '</b> That is either a market holiday or a total collection '
                       'outage, and this check cannot tell them apart. If it was a '
                       'trading day, nothing collected that day and freshness will not '
                       'catch it — verify manually.</div>')
        if cov.get("silent"):
            out.append('<div style="color:#b00;margin-bottom:6px"><b>No data at all in '
                       'the window:</b> ' + ", ".join(cov["silent"])
                       + " — this table may have stopped entirely.</div>")
        if cov["gaps"]:
            out.append('<div style="color:#b00;margin-bottom:6px"><b>Gaps:</b> '
                       + ", ".join(cov["gaps"]) + "</div>")
        out.append('<table style="border-collapse:collapse;font-size:12px">')
        out.append('<tr><th style="text-align:left;padding:2px 8px"></th>' + "".join(
            f'<th style="padding:2px 6px;color:#666;font-weight:500">{d.strftime("%m-%d")}</th>'
            for d in cov["days"]) + "</tr>")
        for row in cov["grid"]:
            cells = []
            for c in row["cells"]:
                style = "padding:2px 6px;text-align:right"
                if c["gap"]:
                    style += ";background:#fdecec;color:#b00;font-weight:700"
                elif c["n"] == 0:
                    style += ";color:#bbb"
                cells.append(f'<td style="{style}">{c["n"] or "-"}</td>')
            out.append(f'<tr><td style="padding:2px 8px;color:#444">{row["label"]}</td>'
                       + "".join(cells) + "</tr>")
        out.append("</table>")
        out.append('<div style="color:#888;font-size:11px;margin-top:4px">'
                   'Trailing zeros are normal (per-table write lag); a highlighted cell '
                   'is a hole with newer data after it.</div>')

    # --- scheduler
    out.append(f'<h3 style="margin:18px 0 6px">Scheduled jobs {_badge(sched["status"])}</h3>')
    if sched["status"] == UNKNOWN:
        out.append(f'<div style="color:#a60">Check failed: {sched.get("error","")}</div>')
    else:
        if sched["failing"]:
            out.append("<ul style='margin:4px 0'>" + "".join(
                f'<li style="color:#b00"><b>{j["name"]}</b> — code {j["code"]} {j["message"]}</li>'
                for j in sched["failing"]) + "</ul>")
        else:
            out.append(f'<div>{sched["checked_total"]} jobs checked, none in a system-error '
                       'state or reporting a failed last attempt.</div>')
        if sched["never_run"]:
            out.append('<div style="color:#666;font-size:12px">Never attempted: '
                       + ", ".join(sched["never_run"]) + "</div>")
        out.append('<div style="color:#888;font-size:11px;margin-top:4px">'
                   'Only explicit failure codes are reported. lastAttemptTime is '
                   'unreliable and is deliberately not used to infer a missed run.</div>')

    # --- life surface
    out.append(f'<h3 style="margin:18px 0 6px">Public life surface {_badge(life["status"])}</h3>')
    if life["status"] == UNKNOWN:
        out.append(f'<div style="color:#a60">Check failed: {life.get("error","")}</div>')
    else:
        out.append("<div>" + " &middot; ".join(
            f"{k} <b>{v}</b>" for k, v in sorted(life["counts"].items(),
                                                 key=lambda kv: -kv[1])) + "</div>")
        if life.get("age_hours") is not None:
            out.append(f'<div style="color:#666;font-size:12px">last labeled '
                       f'{life["age_hours"]}h ago &middot; unlabeled backlog '
                       f'{life.get("backlog")}</div>')
        for n in life.get("notes", []):
            out.append(f'<div style="color:#b00;font-size:12px">{n}</div>')

    # --- opportunity surface (the OTHER labeler; see opp_surface_section)
    out.append(f'<h3 style="margin:18px 0 6px">Opportunity surface (3-day MFE/MAE) '
               f'{_badge(opp["status"])}</h3>')
    if opp["status"] == UNKNOWN:
        out.append(f'<div style="color:#a60">Check failed: {opp.get("error","")}</div>')
    else:
        out.append(f'<div>closed through <b>{opp.get("closed_frontier")}</b> &middot; '
                   f'pending <b>{opp.get("pending")}</b> &middot; overdue '
                   f'<b>{opp.get("overdue")}</b></div>')
        out.append('<div style="color:#666;font-size:12px">'
                   f'{opp.get("awaiting_fill")} row(s) have a closed window still '
                   'awaiting tonight&rsquo;s 17:30 ET fill — that is the design lag, '
                   'not a stall. Overdue counts only rows that have already missed '
                   'two fill runs.</div>')
        # Disclose the set this check is structurally blind to, rather than let
        # an OK badge cover it. These rows are resolved-as-unusable, never
        # filled, and the filler will not revisit them.
        out.append('<div style="color:#888;font-size:11px">'
                   f'{opp.get("terminal_unusable")} row(s) resolved to a terminal '
                   'non-OK status (NO_BARS / NO_POST_ENTRY_BARS / ERROR). They '
                   'are counted as closed, never as overdue, and the fill job '
                   'will not retry them.</div>')
        for n in opp.get("notes", []):
            out.append(f'<div style="color:#b00;font-size:12px">{n}</div>')

    # The digest cannot report its own non-delivery: if dbt hangs or the service
    # is down, no email exists to carry the bad news, and the only remaining
    # signal is the console-red job this artifact exists to replace. There is no
    # cheap dead-man's-switch, so the expectation is written where it will be
    # read — absence IS the alarm.
    out.append('<div style="color:#888;font-size:11px;margin-top:22px;border-top:'
               '1px solid #eee;padding-top:8px">'
               '<b>This email arrives every weekday by ~07:20 ET. If it does not '
               'arrive, treat that as an alarm</b> — it cannot report its own '
               'failure to send.<br>Read-only digest from dbt-runner. '
               'Detail: <code>POST /freshness</code>. '
               'Doctrine: docs/DECISIONS/2026-08-07-freshness-canary-and-bars-loader.md</div>')
    out.append("</div>")
    return "".join(out)


# --------------------------------------------------------------------- send ---

def send_email(subject: str, html: str) -> bool:
    """Single Mailgun send to the operator. Mirrors signal-notifier's helper."""
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        logger.error("Mailgun credentials not set — cannot send digest.")
        return False
    try:
        r = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={"from": MAILGUN_SENDER, "to": [RECIPIENT_EMAIL],
                  "subject": subject, "html": html},
            timeout=15,
        )
        r.raise_for_status()
        logger.info(f"digest sent to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:  # noqa: BLE001
        # Never echo response text: it can contain credentials.
        logger.error(f"digest send failed: {type(e).__name__}")
        return False


def build_and_send(freshness: dict, send: bool = True) -> dict:
    """Assemble every section, render, and (optionally) email.

    `freshness` is the already-computed /freshness payload — passed in rather
    than recomputed so the digest and the canary can never disagree about what
    they saw.
    """
    client = None
    try:
        client = bigquery.Client(project=PROJECT_ID)
    except Exception as e:  # noqa: BLE001
        logger.error(f"digest: BigQuery client failed: {e}")

    fresh = {"status": UNKNOWN, "error": "freshness payload missing"}
    if freshness:
        bad = freshness.get("not_fresh") or {}
        fresh = {
            "status": UNKNOWN if freshness.get("rc") is None else (
                ATTENTION if freshness.get("rc") != 0 else OK),
            "sources": freshness.get("sources", {}),
            "not_fresh": bad,
            "error": (freshness.get("stderr") or "")[:400] if freshness.get("rc") else "",
        }
        # rc != 0 with no parsed sources means dbt died before the DAG ran — that
        # is "could not check", not "a table is stale". The distinction decides
        # whether the reader hunts a stale table or a broken runner.
        if freshness.get("rc") not in (0, None) and not freshness.get("sources"):
            fresh["status"] = UNKNOWN

    if client is None:
        cov = {"status": UNKNOWN, "error": "BigQuery client unavailable",
               "days": [], "grid": [], "gaps": [], "holidays": []}
        life = {"status": UNKNOWN, "error": "BigQuery client unavailable", "counts": {}}
        opp = {"status": UNKNOWN, "error": "BigQuery client unavailable", "notes": []}
    else:
        cov = coverage_section(client)
        life = life_surface_section(client)
        opp = opp_surface_section(client)
    sched = scheduler_section()

    overall = _worst(fresh["status"], cov["status"], sched["status"],
                     life["status"], opp["status"])
    html = render_html(fresh, cov, sched, life, opp, overall)
    tag = {OK: "OK", ATTENTION: "ATTENTION", UNKNOWN: "UNKNOWN"}.get(overall, "UNKNOWN")
    date_str = datetime.now(EST).strftime("%a %m-%d")
    subject = f"[GammaRips] Engine health {tag} — {date_str}"

    sent = send_email(subject, html) if send else None
    return {
        "overall": overall, "subject": subject, "sent": sent,
        "sections": {"freshness": fresh["status"], "coverage": cov["status"],
                     "scheduler": sched["status"], "life_surface": life["status"],
                     "opp_surface": opp["status"]},
        "gaps": cov["gaps"], "failing_jobs": [j["name"] for j in sched["failing"]],
        "not_fresh": fresh.get("not_fresh", {}),
        "html": html,
    }
