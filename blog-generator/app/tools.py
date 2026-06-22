"""
Deterministic tools for blog-generator agents.

All tools return JSON-serializable dicts. Return {"status": "success"|"empty"|"error"|"blocked", ...}
so agents can branch deterministically on missing data without prompt-parsing.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from google.cloud import bigquery, firestore, storage

from gammarips_content import compliance, firestore_helpers, voice_rules

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
DATASET = os.getenv("DATASET", "profit_scout")
LEDGER_TABLE = f"{PROJECT_ID}.{DATASET}.forward_paper_ledger"

# Minimum closed trades before any performance-claiming post can ship.
# Per DESIGN_SPEC.md §Constraints, also §6 of v5.3-surface-and-monetization doc.
N_TRADES_UNLOCK: int = int(os.getenv("N_TRADES_UNLOCK", "30"))

# Post types that REQUIRE live_context / ledger reads.
LIVE_CONTEXT_POST_TYPES: frozenset[str] = frozenset({
    "weekly_engine_recap",       # Wk 7
    "performance_post",          # Wk 10 (N=30 unlock)
    "post_mortem",               # Wk 11
    "video_demo",                # Wk 13 (optional ledger numbers)
})

ET = ZoneInfo("America/New_York")

# Word-count target range for a GammaRips blog post.
MIN_WORD_COUNT = 1200
MAX_WORD_COUNT = 1800

# Minimum structural requirements for a blog post.
MIN_H2_COUNT = 2
MIN_INTERNAL_LINKS = 1  # Planner pushes 2+; writer must ship at least 1.

# Exact disclaimer string that must appear in every blog post (blockquote-safe substring).
DISCLAIMER_REQUIRED_SUBSTR = voice_rules.DISCLAIMER_LONG


# Lazy singletons — ADK tools run in an agent runtime; build on first call.
_bq_client: bigquery.Client | None = None
_fs_client: firestore.Client | None = None


def _bq() -> bigquery.Client:
    global _bq_client
    if _bq_client is None:
        _bq_client = bigquery.Client(project=PROJECT_ID)
    return _bq_client


def _fs() -> firestore.Client:
    global _fs_client
    if _fs_client is None:
        _fs_client = firestore_helpers.get_client(PROJECT_ID)
    return _fs_client


def _today_et_iso() -> str:
    return datetime.now(ET).date().isoformat()


# ---------------------------------------------------------------------------
# Schedule tools (planner)
# ---------------------------------------------------------------------------

def fetch_next_schedule_slot() -> dict:
    """Return the next `pending` row from `blog_schedule/current`.

    The doc is a single Firestore document under `blog_schedule/current` with
    a `rows` array. We return the first row whose status == "pending".

    Returns:
        dict: {"status": "success", "data": {slug, week_num, title_candidate,
               persona, keywords, cta, type, cross_channel, status}}
              or {"status": "empty", "message": "..."}
              or {"status": "error", "message": "..."}
    """
    try:
        snap = _fs().collection("blog_schedule").document("current").get()
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_next_schedule_slot failed: {exc}")
        return {"status": "error", "message": str(exc)}

    if not snap.exists:
        return {
            "status": "empty",
            "message": "blog_schedule/current not found — run scripts/seed_schedule.py",
        }

    doc = snap.to_dict() or {}
    rows = doc.get("rows", []) or []
    for row in rows:
        if row.get("status") == "pending":
            return {"status": "success", "data": row}

    return {
        "status": "empty",
        "message": "no_pending_slots — schedule fully published, add more rows",
    }


def fetch_schedule_slot_by_slug(slug: str) -> dict:
    """Targeted fetch for a specific slug (manual retry flow).

    Returns the schedule row regardless of status (caller picks behavior).
    """
    if not slug:
        return {"status": "error", "message": "slug is required"}
    try:
        snap = _fs().collection("blog_schedule").document("current").get()
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_schedule_slot_by_slug failed: {exc}")
        return {"status": "error", "message": str(exc)}
    if not snap.exists:
        return {"status": "empty", "message": "blog_schedule/current not found"}
    rows = (snap.to_dict() or {}).get("rows", []) or []
    for row in rows:
        if row.get("slug") == slug:
            return {"status": "success", "data": row}
    return {"status": "empty", "message": f"slug {slug!r} not in schedule"}


# ---------------------------------------------------------------------------
# Prior-posts tools (planner)
# ---------------------------------------------------------------------------

def fetch_prior_posts(limit: int = 5) -> dict:
    """Return the last N published blog_posts for internal-link targets.

    Args:
        limit: Max posts to return. Default 5.

    Returns:
        dict: {"status": "success", "data": [{slug, title, keywords}, ...]}
              or {"status": "empty"} if no posts yet.
    """
    limit = max(1, min(int(limit or 5), 20))
    try:
        query = (
            _fs().collection("blog_posts")
            .where("status", "==", "published")
            .order_by("published_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        docs = list(query.stream())
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_prior_posts failed: {exc}")
        return {"status": "error", "message": str(exc)}

    if not docs:
        return {"status": "empty", "data": []}

    out = []
    for d in docs:
        data = d.to_dict() or {}
        out.append({
            "slug": data.get("slug", d.id),
            "title": data.get("title", ""),
            "keywords": data.get("keywords", []) or [],
        })
    return {"status": "success", "data": out}


# ---------------------------------------------------------------------------
# Live-context tool (writer, for performance-claiming post types)
# ---------------------------------------------------------------------------

def fetch_live_context(post_type: str, scan_date: str = "") -> dict:
    """Fetch live ledger context for posts that need it.

    Args:
        post_type: The schedule row's `type` — one of
                   weekly_engine_recap, performance_post, post_mortem, video_demo.
                   Other types return status="skipped" with no read.
        scan_date: YYYY-MM-DD (Eastern time). Defaults to today ET.

    Returns:
        dict with one of these statuses:
            "success" — returns {data: {closed_trade_count, wins, losses, net_return_pct}}
            "blocked" — closed_trade_count < N_TRADES_UNLOCK; post MUST NOT claim wins/P&L
            "skipped" — post_type does not need live context
            "error"   — BQ failure; caller should assume no numerics
    """
    if not post_type:
        return {"status": "error", "message": "post_type required"}
    if post_type not in LIVE_CONTEXT_POST_TYPES:
        return {
            "status": "skipped",
            "message": f"post_type {post_type!r} does not require live context",
        }

    date_iso = scan_date or _today_et_iso()
    # V6 only — prior cohorts are historical noise that would falsely trip the
    # 30-trade unlock gate. Drop INVALID_LIQUIDITY/SKIPPED non-trades.
    query = f"""
        SELECT
            COUNT(*) AS closed_trade_count,
            COUNTIF((peak_return IS NOT NULL) AND (peak_return > 0)) AS wins,
            COUNTIF((peak_return IS NOT NULL) AND (peak_return <= 0)) AS losses,
            SUM(IFNULL(peak_return, 0)) AS net_return_pct
        FROM `{LEDGER_TABLE}`
        WHERE exit_reason IS NOT NULL
          AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')
          AND policy_version = 'V7_1_TILTED_GIGO'
          AND DATE(exit_timestamp) <= @scan_date
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("scan_date", "DATE", date_iso),
                ]
            ),
        )
        row = next(iter(job.result()), None)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_live_context BQ failed: {exc}")
        return {"status": "error", "message": str(exc)}

    if row is None:
        return {
            "status": "blocked",
            "reason": "no_ledger_rows",
            "data": {"closed_trade_count": 0, "unlock_at": N_TRADES_UNLOCK},
        }

    n = int(row["closed_trade_count"] or 0)
    if n < N_TRADES_UNLOCK:
        return {
            "status": "blocked",
            "reason": f"closed_trade_count={n} < {N_TRADES_UNLOCK}",
            "data": {"closed_trade_count": n, "unlock_at": N_TRADES_UNLOCK},
        }

    return {
        "status": "success",
        "data": {
            "closed_trade_count": n,
            "wins": int(row["wins"] or 0),
            "losses": int(row["losses"] or 0),
            "net_return_pct": float(row["net_return_pct"] or 0.0),
            "as_of_date": date_iso,
        },
    }


# ---------------------------------------------------------------------------
# Rubric (reviewer-invoked via callback)
# ---------------------------------------------------------------------------

_YAML_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H2_RE = re.compile(r"^##\s+\S", re.MULTILINE)
_H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)
# Internal link = markdown link whose href starts with `/` (same-site) and points to
# /blog/, /how-it-works, /signals, /about, /scorecard, etc.
_INTERNAL_LINK_RE = re.compile(r"\[[^\]]+\]\((/[a-z0-9/_\-]+)\)")


def _strip_frontmatter(markdown: str) -> str:
    return _YAML_FRONTMATTER_RE.sub("", markdown, count=1)


def _word_count(text: str) -> int:
    # Word count excludes front matter + fenced code blocks + markdown link syntax.
    # Rough heuristic — good enough for the 1200-1800 gate.
    body = _strip_frontmatter(text)
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"[#>*_`\[\]()]", " ", body)
    return len([w for w in body.split() if w.strip()])


def score_blog_rubric(markdown: str, expected_cta: str | None = None) -> dict:
    """Deterministic blog-specific rubric scoring.

    Wraps gammarips_content.compliance.score_against_rubric(is_blog=True) and
    layers blog-only checks: word count (1200-1800), >=2 H2, disclaimer block,
    >=1 internal link.

    Args:
        markdown: Full blog markdown including YAML front matter.
        expected_cta: If provided, the front-matter `cta:` field must equal
            this value verbatim. Mismatch is a hard failure — the schedule
            slot is the source of truth, the writer cannot override.

    Returns:
        dict: {
          "passed": bool,
          "word_count": int,
          "h2_count": int,
          "h1_count": int,
          "disclaimer_present": bool,
          "internal_link_count": int,
          "cta_match": bool | None,  # null if expected_cta wasn't passed
          "failures": [str, ...],   // from base rubric + blog-specific
          "warnings": [str, ...],
        }
    """
    failures: list[str] = []
    warnings: list[str] = []

    if not isinstance(markdown, str) or not markdown.strip():
        return {
            "passed": False,
            "word_count": 0,
            "h2_count": 0,
            "h1_count": 0,
            "disclaimer_present": False,
            "internal_link_count": 0,
            "failures": ["empty_markdown"],
            "warnings": [],
        }

    # Base rubric (blog mode) — catches retired aliases + banned recommendation phrases.
    base = compliance.score_against_rubric(
        text=markdown, post_type="blog", is_blog=True
    )
    failures.extend(base.failures)
    warnings.extend(base.warnings)

    # Word count
    wc = _word_count(markdown)
    if wc < MIN_WORD_COUNT:
        failures.append(f"word_count_below_min: {wc} < {MIN_WORD_COUNT}")
    elif wc > MAX_WORD_COUNT:
        failures.append(f"word_count_above_max: {wc} > {MAX_WORD_COUNT}")

    # H2 count
    h2_count = len(_H2_RE.findall(markdown))
    if h2_count < MIN_H2_COUNT:
        failures.append(f"h2_count_below_min: {h2_count} < {MIN_H2_COUNT}")

    # H1 presence (exactly one recommended)
    h1_count = len(_H1_RE.findall(markdown))
    if h1_count != 1:
        warnings.append(f"h1_count_unusual: {h1_count} (expected 1)")

    # Disclaimer block present
    disclaimer_present = DISCLAIMER_REQUIRED_SUBSTR in markdown
    if not disclaimer_present:
        # Accept blockquote form too — the literal substring check is sufficient
        # because the blockquote prefix ("> ") doesn't break the sentence.
        # Recheck with line-joined form.
        flat = " ".join(
            line.lstrip("> ").strip() for line in markdown.splitlines()
        )
        disclaimer_present = DISCLAIMER_REQUIRED_SUBSTR in flat
    if not disclaimer_present:
        failures.append("disclaimer_missing")

    # Internal link density
    internal_links = _INTERNAL_LINK_RE.findall(markdown)
    internal_link_count = len(internal_links)
    if internal_link_count < MIN_INTERNAL_LINKS:
        failures.append(
            f"internal_link_count_below_min: {internal_link_count} < {MIN_INTERNAL_LINKS}"
        )

    # CTA match — the schedule slot is the source of truth. The writer cannot
    # override (e.g. drift from `webapp_visit` → `pro_trial`). Both the YAML
    # `cta:` field AND the closing paragraph must reflect the schedule pick.
    cta_match: bool | None = None
    if expected_cta:
        m = re.search(r'^cta:\s*"?([\w_]+)"?\s*$', markdown, flags=re.MULTILINE)
        actual_cta = m.group(1) if m else None
        cta_match = actual_cta == expected_cta
        if not cta_match:
            failures.append(
                f"cta_mismatch: front_matter={actual_cta!r} expected={expected_cta!r}"
            )
        # If schedule says webapp_visit, the body must NOT pitch a paid tier.
        if expected_cta == "webapp_visit":
            paid_pitch = re.search(
                r"\b(pro\s+trial|starter\s+trial|founder\s+pricing|paid\s+tier)\b",
                markdown,
                flags=re.IGNORECASE,
            )
            if paid_pitch:
                failures.append(
                    f"cta_paid_pitch_on_webapp_visit_post: matched {paid_pitch.group(0)!r}"
                )

    return {
        "passed": not failures,
        "word_count": wc,
        "h2_count": h2_count,
        "h1_count": h1_count,
        "disclaimer_present": disclaimer_present,
        "internal_link_count": internal_link_count,
        "cta_match": cta_match,
        "failures": failures,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Firestore writes (Publisher)
# ---------------------------------------------------------------------------

def _estimate_reading_time(markdown: str) -> int:
    wc = _word_count(markdown)
    # 225 wpm average reading speed → round up.
    return max(1, (wc + 224) // 225)


def _update_schedule_row_status(slug: str, new_status: str) -> None:
    """Update the row in blog_schedule/current matching `slug` to `new_status`.

    Uses a transaction to avoid clobbering concurrent writes.
    """
    doc_ref = _fs().collection("blog_schedule").document("current")

    @firestore.transactional
    def _update(tx: firestore.Transaction) -> None:
        snap = doc_ref.get(transaction=tx)
        if not snap.exists:
            return
        data = snap.to_dict() or {}
        rows = data.get("rows", []) or []
        changed = False
        for row in rows:
            if row.get("slug") == slug:
                row["status"] = new_status
                changed = True
                break
        if changed:
            tx.update(doc_ref, {"rows": rows})

    tx = _fs().transaction()
    try:
        _update(tx)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"_update_schedule_row_status({slug}, {new_status}) failed: {exc}")


def publish_to_firestore(
    slug: str,
    title: str,
    description: str,
    markdown: str,
    keywords: list[str],
    cta: str,
    reviewer_score: float,
    iterations: int,
) -> dict:
    """Write blog_posts/{slug} with status=published, bump schedule row to published.

    Returns:
        dict: {"status": "success", "slug": "...", "reading_time_min": N}
              or {"status": "error", "message": "..."}
    """
    if not slug:
        return {"status": "error", "message": "slug required"}
    try:
        reading_time = _estimate_reading_time(markdown)
        _fs().collection("blog_posts").document(slug).set({
            "slug": slug,
            "title": title,
            "description": description,
            "markdown": markdown,
            "keywords": list(keywords or []),
            "cta": cta,
            "reviewer_score": float(reviewer_score or 0.0),
            "iterations": int(iterations or 1),
            "status": "published",
            "reading_time_min": reading_time,
            "published_at": firestore.SERVER_TIMESTAMP,
        })
        _update_schedule_row_status(slug, "published")
        return {"status": "success", "slug": slug, "reading_time_min": reading_time}
    except Exception as exc:  # noqa: BLE001
        logger.error(f"publish_to_firestore failed: {exc}")
        return {"status": "error", "message": str(exc)}


def log_rejected(slug: str, notes: str) -> dict:
    """Write blog_posts/{slug} with status=rejected + reviewer notes.

    Called by Publisher when the loop exits without an APPROVE. Schedule row is
    NOT flipped — it stays pending so the next scheduled fire retries, or Evan
    can manually retry via POST /run with the slug.
    """
    if not slug:
        return {"status": "error", "message": "slug required"}
    try:
        _fs().collection("blog_posts").document(slug).set({
            "slug": slug,
            "status": "rejected",
            "reviewer_notes": notes or "",
            "rejected_at": firestore.SERVER_TIMESTAMP,
        }, merge=True)
        return {"status": "success", "slug": slug}
    except Exception as exc:  # noqa: BLE001
        logger.error(f"log_rejected failed: {exc}")
        return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# Utility (shared with fast_api_app)
# ---------------------------------------------------------------------------

def today_et_iso() -> str:
    """Today's date in America/New_York, as YYYY-MM-DD."""
    return _today_et_iso()


# ---------------------------------------------------------------------------
# Newsletter tools (POST /draft_email and POST /blast_email)
# ---------------------------------------------------------------------------

# Mailgun env (mirrors signal-notifier's wiring — same secret names).
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", "").strip()
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "").strip()
MAILGUN_SENDER = (
    f"GammaRips <newsletter@{MAILGUN_DOMAIN}>" if MAILGUN_DOMAIN else "GammaRips"
)

# Operator inbox — receives /draft_email previews and /blast_email dry runs.
OPERATOR_EMAIL = os.environ.get("OPERATOR_EMAIL", "evan@gammarips.com").strip()

# GCS bucket for draft email artifacts.
EMAIL_DRAFTS_BUCKET = os.environ.get(
    "EMAIL_DRAFTS_BUCKET", "gammarips-content-drafts"
).strip()

# Per-blast safety cap on real-recipient fan-out.
MAX_RECIPIENTS = int(os.environ.get("MAX_RECIPIENTS", "1000"))

_storage_client: storage.Client | None = None


def _gcs() -> storage.Client:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=PROJECT_ID)
    return _storage_client


def _parse_gs_uri(uri: str) -> tuple[str, str]:
    """Split `gs://bucket/key` into (bucket, key). Raises ValueError on bad input."""
    if not isinstance(uri, str) or not uri.startswith("gs://"):
        raise ValueError(f"not a gs:// uri: {uri!r}")
    rest = uri[len("gs://"):]
    bucket, _, key = rest.partition("/")
    if not bucket or not key:
        raise ValueError(f"malformed gs:// uri: {uri!r}")
    return bucket, key


def write_to_gcs(uri: str, content: str, content_type: str = "text/html") -> str:
    """Write `content` to `gs://bucket/key`. Returns the URI on success.

    Raises:
        ValueError on malformed URI.
        google.api_core.exceptions.NotFound if the bucket does not exist.
        google.api_core.exceptions.Forbidden on IAM error.
    """
    bucket_name, key = _parse_gs_uri(uri)
    blob = _gcs().bucket(bucket_name).blob(key)
    blob.upload_from_string(content, content_type=content_type)
    return uri


def read_from_gcs(uri: str) -> str:
    """Read a UTF-8 text blob from `gs://bucket/key`."""
    bucket_name, key = _parse_gs_uri(uri)
    blob = _gcs().bucket(bucket_name).blob(key)
    return blob.download_as_text()


def gcs_object_exists(uri: str) -> bool:
    """Return True if the `gs://...` blob exists. Best-effort, swallows errors."""
    try:
        bucket_name, key = _parse_gs_uri(uri)
        return _gcs().bucket(bucket_name).blob(key).exists()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"gcs_object_exists({uri!r}) error: {exc}")
        return False


def send_email_via_mailgun(
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
) -> dict:
    """Single-recipient Mailgun send. Mirrors signal-notifier semantics.

    Per-recipient by design — never BCC, never `to: [a, b, c]`. Newsletter
    fan-out is done by the caller looping over recipients.

    Args:
        to: Single recipient email.
        subject: Email subject.
        html: HTML body.
        text: Optional plain-text alternative; recommended for deliverability.

    Returns:
        {"status": "success", "recipient": <email>, "mailgun_id": "..."}
        {"status": "error",   "recipient": <email>, "message": "..."}
    """
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        return {
            "status": "error",
            "recipient": to,
            "message": "MAILGUN_API_KEY/MAILGUN_DOMAIN not set",
        }
    if not to:
        return {"status": "error", "recipient": to, "message": "empty recipient"}

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": MAILGUN_SENDER,
        "to": [to],  # always single recipient
        "subject": subject,
        "html": html,
    }
    if text:
        data["text"] = text

    try:
        resp = requests.post(url, auth=auth, data=data, timeout=10)
        resp.raise_for_status()
        body = resp.json() if resp.content else {}
        return {
            "status": "success",
            "recipient": to,
            "mailgun_id": body.get("id", ""),
        }
    except Exception as exc:  # noqa: BLE001
        body_text = ""
        try:
            body_text = resp.text  # type: ignore[name-defined]
        except Exception:  # noqa: BLE001
            pass
        logger.error(f"Mailgun send to {to!r} failed: {exc} — body={body_text!r}")
        return {"status": "error", "recipient": to, "message": str(exc)}


def get_closed_trade_count(table: str | None = None) -> int:
    """Count trades that actually closed in the live ledger.

    Filters: policy_version='V7_1_TILTED_GIGO' AND exit_reason valid (not
    INVALID_LIQUIDITY / SKIPPED). Other policy versions (V3, V4) are
    historical and not part of the public track record. Without this
    filter the count includes prior-cohort noise (ledger truncated 2026-06-04; V6 cohort
    starts fresh), which falsely trips the 30-trade unlock gate.

    Args:
        table: Fully-qualified table id; defaults to LEDGER_TABLE.

    Returns:
        int. Returns 0 on BQ failure.
    """
    table_id = table or LEDGER_TABLE
    sql = f"""
        SELECT COUNT(*) AS n FROM `{table_id}`
        WHERE exit_reason IS NOT NULL
          AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')
          AND policy_version = 'V7_1_TILTED_GIGO'
    """
    try:
        job = _bq().query(sql)
        row = next(iter(job.result()), None)
        return int(row["n"] or 0) if row else 0
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"get_closed_trade_count failed: {exc}")
        return 0


def get_recent_daily_reports(days: int = 7) -> list[dict]:
    """Fetch the past N days of `daily_reports/{date}` docs for newsletter
    summarization.

    Returns reverse-chronological list of {scan_date, title, headline,
    bullish_count, bearish_count, total_signals}. Empty list on failure.
    """
    from datetime import datetime, timedelta as _td
    end = datetime.now(ET).date()
    start = end - _td(days=max(days, 1))
    out: list[dict] = []
    try:
        col = _fs().collection("daily_reports")
        snaps = (
            col.where("scan_date", ">=", start.isoformat())
               .where("scan_date", "<=", end.isoformat())
               .stream()
        )
        for snap in snaps:
            d = snap.to_dict() or {}
            out.append({
                "scan_date": d.get("scan_date") or snap.id,
                "title": d.get("title", ""),
                "headline": d.get("headline", ""),
                "bullish_count": d.get("bullish_count"),
                "bearish_count": d.get("bearish_count"),
                "total_signals": d.get("total_signals"),
            })
        out.sort(key=lambda r: r.get("scan_date", ""), reverse=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"get_recent_daily_reports failed: {exc}")
        return []
    return out


def get_recent_v53_closes(days: int = 7) -> list[dict]:
    """Past N days of GammaRips closes from forward_paper_ledger.

    Pre-shaped for newsletter / blog summary: ticker, direction,
    entry_date, exit_date, return_pct (rounded), exit_reason. V6 only,
    valid exits only. Empty list on failure.
    """
    from datetime import datetime, timedelta as _td
    end = datetime.now(ET).date()
    start = end - _td(days=max(days, 1))
    sql = f"""
        SELECT
            ticker, direction,
            scan_date AS entry_date,
            DATE(exit_timestamp) AS exit_date,
            ROUND(realized_return_pct, 2) AS return_pct,
            exit_reason
        FROM `{LEDGER_TABLE}`
        WHERE DATE(exit_timestamp) BETWEEN @start AND @end
          AND exit_reason IS NOT NULL
          AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')
          AND policy_version = 'V7_1_TILTED_GIGO'
        ORDER BY exit_timestamp DESC
    """
    try:
        job = _bq().query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start", "DATE", start.isoformat()),
                    bigquery.ScalarQueryParameter("end", "DATE", end.isoformat()),
                ]
            ),
        )
        rows = []
        for r in job.result():
            d = dict(r)
            rd = d.get("return_pct")
            d["pct_signed"] = (
                f"{'+' if (rd or 0) >= 0 else ''}{int(round((rd or 0) * 100))}%"
                if rd is not None else None
            )
            for k, v in list(d.items()):
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            rows.append(d)
        return rows
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"get_recent_v53_closes failed: {exc}")
        return []


def get_latest_blog_post() -> dict | None:
    """Return the most-recent published blog post, or None if no posts yet.

    Used by the newsletter writer to compose the "What we wrote" section.
    Returns the same shape as `fetch_prior_posts` rows but with `markdown`
    + `description` included so the writer can excerpt the intro.
    """
    try:
        query = (
            _fs().collection("blog_posts")
            .where("status", "==", "published")
            .order_by("published_at", direction=firestore.Query.DESCENDING)
            .limit(1)
        )
        docs = list(query.stream())
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"get_latest_blog_post failed: {exc}")
        return None
    if not docs:
        return None
    data = docs[0].to_dict() or {}
    return {
        "slug": data.get("slug", docs[0].id),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "markdown": data.get("markdown", ""),
        "keywords": data.get("keywords", []) or [],
        "published_at": data.get("published_at"),
        "reading_time_min": data.get("reading_time_min"),
    }


def read_email_audience(audience: str = "all") -> list[dict]:
    """Return the list of email recipients for a given audience filter.

    Audiences (mirrors the `users` collection schema — 211 docs as of
    2026-04-29):

    - "all"  : !isAnonymous AND email IS NOT NULL
    - "free" : "all" minus active paid (plan != 'pro' OR subscriptionStatus != 'active')
    - "paid" : plan == 'pro' AND subscriptionStatus == 'active' AND
               stripeSubscriptionId IS NOT NULL

    Deduped by email address (lowercased). Some addresses (e.g.
    admin@evanparra.ai, admin@profitscout.app) exist under multiple uids
    in the users collection; without dedup the same address gets the
    blast twice. The retained row is the FIRST matching uid in the
    Firestore stream order — `displayName` and `uid` reflect that row.

    Returns: list of {email, displayName, uid}. Empty list on error.
    """
    audience = (audience or "all").strip().lower()
    if audience not in {"all", "free", "paid"}:
        logger.error(f"read_email_audience: unknown audience {audience!r}")
        return []

    try:
        col = _fs().collection("users")

        def _dedupe_by_email(rows: list[dict]) -> list[dict]:
            """First-wins dedup on lowercased email. Mailgun call dedup."""
            seen: set[str] = set()
            out: list[dict] = []
            for r in rows:
                key = (r.get("email") or "").strip().lower()
                if not key or key in seen:
                    continue
                seen.add(key)
                out.append(r)
            return out

        if audience == "paid":
            # Strict-tuple paid filter — same as signal-notifier.
            query = (
                col.where("plan", "==", "pro")
                .where("subscriptionStatus", "==", "active")
            )
            paid_rows: list[dict] = []
            for doc in query.stream():
                d = doc.to_dict() or {}
                email = d.get("email")
                stripe_sub_id = d.get("stripeSubscriptionId")
                if email and stripe_sub_id and not d.get("isAnonymous", False):
                    paid_rows.append({
                        "email": email,
                        "displayName": d.get("displayName", "") or "",
                        "uid": d.get("uid", doc.id),
                    })
            return _dedupe_by_email(paid_rows)

        # "all" and "free" both start from the non-anonymous + has-email cohort.
        # Firestore can't do "field != X" cleanly across all SDKs, so we filter
        # on isAnonymous == False and post-filter for email presence.
        query = col.where("isAnonymous", "==", False)
        all_users: list[dict] = []
        for doc in query.stream():
            d = doc.to_dict() or {}
            email = d.get("email")
            if not email:
                continue
            all_users.append({
                "email": email,
                "displayName": d.get("displayName", "") or "",
                "uid": d.get("uid", doc.id),
                "_plan": d.get("plan", "") or "",
                "_sub_status": d.get("subscriptionStatus", "") or "",
                "_stripe_sub_id": d.get("stripeSubscriptionId", "") or "",
            })

        if audience == "all":
            return _dedupe_by_email([
                {"email": u["email"], "displayName": u["displayName"], "uid": u["uid"]}
                for u in all_users
            ])

        # audience == "free": NOT (plan == 'pro' AND subscriptionStatus == 'active')
        free_rows: list[dict] = []
        for u in all_users:
            is_active_paid = (
                u["_plan"] == "pro"
                and u["_sub_status"] == "active"
                and bool(u["_stripe_sub_id"])
            )
            if not is_active_paid:
                free_rows.append({
                    "email": u["email"],
                    "displayName": u["displayName"],
                    "uid": u["uid"],
                })
        return _dedupe_by_email(free_rows)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"read_email_audience({audience!r}) failed: {exc}")
        return []


# ---------------------------------------------------------------------------
# /blast_latest helpers — auto-discover, kill-switch, idempotency
# ---------------------------------------------------------------------------

EMAIL_DRAFTS_BUCKET_NAME = os.environ.get("EMAIL_DRAFTS_BUCKET", "gammarips-content-drafts")
_DRAFT_NAME_RE = re.compile(r"email/(\d{4}-\d{2}-\d{2})_newsletter\.html$")


def find_latest_email_draft() -> tuple[str, str] | None:
    """Return (gcs_uri, draft_date_iso) for the most recent newsletter draft.

    Lists `gs://{EMAIL_DRAFTS_BUCKET}/email/*_newsletter.html` and picks the
    lexicographically-greatest filename — works because dates are ISO. Returns
    None if no draft exists.
    """
    try:
        client = _gcs()
        bucket = client.bucket(EMAIL_DRAFTS_BUCKET_NAME)
        latest: tuple[str, str] | None = None
        for blob in client.list_blobs(bucket, prefix="email/"):
            m = _DRAFT_NAME_RE.search(blob.name or "")
            if not m:
                continue
            date_iso = m.group(1)
            uri = f"gs://{EMAIL_DRAFTS_BUCKET_NAME}/{blob.name}"
            if latest is None or date_iso > latest[1]:
                latest = (uri, date_iso)
        return latest
    except Exception as exc:  # noqa: BLE001
        logger.error(f"find_latest_email_draft failed: {exc}")
        return None


def is_blast_killswitch_set(date_iso: str) -> bool:
    """True if `blast_killswitch/{date_iso}` exists with `aborted=true`.

    Operator workflow: after receiving the Sun 17:00 ET draft preview, set the
    kill switch with:
      gcloud firestore documents set blast_killswitch/<date> \
        --data='{"aborted": true, "reason": "..."}' --project=profitscout-fida8
    """
    try:
        snap = _fs().collection("blast_killswitch").document(date_iso).get()
        return bool(snap.exists and (snap.to_dict() or {}).get("aborted") is True)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"is_blast_killswitch_set({date_iso!r}) failed (fail-open): {exc}")
        return False


def get_blast_history(date_iso: str) -> dict | None:
    try:
        snap = _fs().collection("blast_history").document(date_iso).get()
        return snap.to_dict() if snap.exists else None
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"get_blast_history({date_iso!r}) failed: {exc}")
        return None


def mark_blast_started(date_iso: str, gcs_uri: str, audience: str) -> bool:
    """Atomic-create `blast_history/{date_iso}` with status='in_progress'.

    Returns True on first create (caller proceeds), False if doc already
    exists (caller should skip — already blasted or in-progress).
    """
    try:
        ref = _fs().collection("blast_history").document(date_iso)
        ref.create({
            "date_iso": date_iso,
            "gcs_uri": gcs_uri,
            "audience": audience,
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat() + "Z",
        })
        return True
    except Exception as exc:  # noqa: BLE001
        # google.api_core.exceptions.AlreadyExists is the expected idempotent
        # path. Anything else (transient FS error) we log and treat as "skip"
        # to avoid double-blasting under partial failure.
        logger.info(f"mark_blast_started({date_iso!r}) not created (likely exists): {exc}")
        return False


def mark_blast_completed(
    date_iso: str,
    sent: int,
    failed: int,
    audience_count: int,
    status: str = "completed",
) -> None:
    try:
        ref = _fs().collection("blast_history").document(date_iso)
        ref.set({
            "status": status,
            "sent": sent,
            "failed": failed,
            "audience_count": audience_count,
            "completed_at": datetime.utcnow().isoformat() + "Z",
        }, merge=True)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"mark_blast_completed({date_iso!r}) failed: {exc}")


# ---------------------------------------------------------------------------
# /weekly_intel tools — GA4 + GSC + ledger summary for the Mon 07:00 cron
# ---------------------------------------------------------------------------
#
# GA4 + GSC integrations are STUBS until the operator finishes the manual
# setup: create gammarips-analytics-reader@profitscout-fida8 service account,
# grant GA4 property Viewer + GSC property Restricted user, set env vars
# GA4_PROPERTY_ID and GSC_SITE_URL on the Cloud Run service.
#
# Once configured, the stubs are replaced by:
#   - GA4: google.analytics.data_v1beta.BetaAnalyticsDataClient
#   - GSC: googleapiclient.discovery.build('searchconsole', 'v1', ...)
# ADC picks up the SA credentials automatically on Cloud Run.


def fetch_ga4_traffic_summary(days: int = 7) -> dict:
    """Pull GA4 last-N-day rollup. Returns {status, sessions, top_pages,
    top_sources, top_countries}. Returns {status: 'unavailable', reason} if
    GA4_PROPERTY_ID is unset OR the GA4 client lib is unavailable.
    """
    property_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    if not property_id:
        return {"status": "unavailable", "reason": "GA4_PROPERTY_ID env var unset"}
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Metric, RunReportRequest,
        )
    except ImportError as exc:
        return {
            "status": "unavailable",
            "reason": f"google-analytics-data lib not installed: {exc}",
        }
    try:
        client = BetaAnalyticsDataClient()
        date_range = [DateRange(start_date=f"{days}daysAgo", end_date="today")]
        # Total sessions + engaged sessions.
        totals = client.run_report(RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[Metric(name="sessions"), Metric(name="engagedSessions"),
                     Metric(name="averageSessionDuration"), Metric(name="bounceRate")],
            date_ranges=date_range,
        ))
        # Top pages.
        pages = client.run_report(RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews"), Metric(name="engagedSessions")],
            date_ranges=date_range,
            limit=10,
        ))
        # Top sources.
        sources = client.run_report(RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="sessionSource"), Dimension(name="sessionMedium")],
            metrics=[Metric(name="sessions")],
            date_ranges=date_range,
            limit=10,
        ))
        return {
            "status": "ok",
            "totals": _ga4_rows(totals)[0] if _ga4_rows(totals) else {},
            "top_pages": _ga4_rows(pages),
            "top_sources": _ga4_rows(sources),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"fetch_ga4_traffic_summary failed: {exc}")
        return {"status": "error", "reason": str(exc)}


def _ga4_rows(report) -> list[dict]:
    """Convert a GA4 run_report response to a list of {dim..., metric...} dicts."""
    dims = [d.name for d in report.dimension_headers]
    mets = [m.name for m in report.metric_headers]
    out: list[dict] = []
    for row in report.rows:
        d: dict = {}
        for i, name in enumerate(dims):
            d[name] = row.dimension_values[i].value
        for i, name in enumerate(mets):
            d[name] = row.metric_values[i].value
        out.append(d)
    return out


def fetch_gsc_search_summary(days: int = 7) -> dict:
    """Pull Google Search Console last-N-day rollup. Returns top queries +
    top pages + totals. Returns {status: 'unavailable'} if GSC_SITE_URL unset.
    """
    site_url = os.environ.get("GSC_SITE_URL", "").strip()
    if not site_url:
        return {"status": "unavailable", "reason": "GSC_SITE_URL env var unset"}
    try:
        from googleapiclient.discovery import build
    except ImportError as exc:
        return {
            "status": "unavailable",
            "reason": f"google-api-python-client not installed: {exc}",
        }
    try:
        from datetime import timedelta as _td
        end = datetime.now(ET).date()
        start = end - _td(days=days)
        service = build("searchconsole", "v1", cache_discovery=False)

        def _run(dimensions: list[str], row_limit: int = 25) -> list[dict]:
            req = {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": dimensions,
                "rowLimit": row_limit,
            }
            resp = service.searchanalytics().query(siteUrl=site_url, body=req).execute()
            rows = []
            for r in resp.get("rows", []) or []:
                d = dict(zip(dimensions, r.get("keys", [])))
                d.update({
                    "clicks": r.get("clicks", 0),
                    "impressions": r.get("impressions", 0),
                    "ctr": round((r.get("ctr") or 0) * 100, 2),
                    "position": round(r.get("position") or 0, 2),
                })
                rows.append(d)
            return rows

        return {
            "status": "ok",
            "top_queries": _run(["query"], 25),
            "top_pages": _run(["page"], 25),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"fetch_gsc_search_summary failed: {exc}")
        return {"status": "error", "reason": str(exc)}


def fetch_recent_blast_history(weeks: int = 4) -> list[dict]:
    """Last N weeks of newsletter blast history. Reverse-chronological."""
    from datetime import timedelta as _td
    cutoff = (datetime.now(ET).date() - _td(days=weeks * 7)).isoformat()
    out: list[dict] = []
    try:
        col = _fs().collection("blast_history")
        for snap in col.stream():
            d = snap.to_dict() or {}
            date_iso = d.get("date_iso") or snap.id
            if date_iso < cutoff:
                continue
            out.append({
                "date_iso": date_iso,
                "audience": d.get("audience"),
                "audience_count": d.get("audience_count"),
                "sent": d.get("sent"),
                "failed": d.get("failed"),
                "status": d.get("status"),
            })
        out.sort(key=lambda r: r.get("date_iso", ""), reverse=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"fetch_recent_blast_history failed: {exc}")
    return out


def fetch_ledger_intel_summary(days: int = 30) -> dict:
    """Last N days of Engine ledger health: closes, win rate, peak return."""
    from datetime import timedelta as _td
    end = datetime.now(ET).date()
    start = end - _td(days=days)
    sql = f"""
        SELECT
            COUNT(*) AS closes,
            SUM(CASE WHEN realized_return_pct > 0 THEN 1 ELSE 0 END) AS winners,
            SUM(CASE WHEN realized_return_pct <= 0 THEN 1 ELSE 0 END) AS losers,
            ROUND(AVG(realized_return_pct), 4) AS avg_return,
            ROUND(MAX(realized_return_pct), 4) AS best_return,
            ROUND(MIN(realized_return_pct), 4) AS worst_return,
            COUNTIF(direction = 'BULLISH') AS bullish_closes,
            COUNTIF(direction = 'BEARISH') AS bearish_closes
        FROM `{LEDGER_TABLE}`
        WHERE DATE(exit_timestamp) BETWEEN @start AND @end
          AND exit_reason IS NOT NULL
          AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')
          AND policy_version = 'V7_1_TILTED_GIGO'
    """
    try:
        job = _bq().query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start", "DATE", start.isoformat()),
                    bigquery.ScalarQueryParameter("end", "DATE", end.isoformat()),
                ]
            ),
        )
        row = next(iter(job.result()), None)
        if row is None:
            return {"closes": 0}
        d = dict(row)
        for k, v in list(d.items()):
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        return d
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"fetch_ledger_intel_summary failed: {exc}")
        return {"closes": 0, "error": str(exc)}
