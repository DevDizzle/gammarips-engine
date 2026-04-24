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

from google.cloud import bigquery, firestore

from gammarips_content import compliance, firestore_helpers, voice_rules

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
DATASET = os.getenv("DATASET", "profit_scout")
LEDGER_TABLE = f"{PROJECT_ID}.{DATASET}.forward_paper_ledger"

# Minimum closed V5.3 trades before any performance-claiming post can ship.
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
    query = f"""
        SELECT
            COUNT(*) AS closed_trade_count,
            COUNTIF((peak_return IS NOT NULL) AND (peak_return > 0)) AS wins,
            COUNTIF((peak_return IS NOT NULL) AND (peak_return <= 0)) AS losses,
            SUM(IFNULL(peak_return, 0)) AS net_return_pct
        FROM `{LEDGER_TABLE}`
        WHERE exit_reason IS NOT NULL
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


def score_blog_rubric(markdown: str) -> dict:
    """Deterministic blog-specific rubric scoring.

    Wraps gammarips_content.compliance.score_against_rubric(is_blog=True) and
    layers blog-only checks: word count (1200-1800), >=2 H2, disclaimer block,
    >=1 internal link.

    Returns:
        dict: {
          "passed": bool,
          "word_count": int,
          "h2_count": int,
          "h1_count": int,
          "disclaimer_present": bool,
          "internal_link_count": int,
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

    return {
        "passed": not failures,
        "word_count": wc,
        "h2_count": h2_count,
        "h1_count": h1_count,
        "disclaimer_present": disclaimer_present,
        "internal_link_count": internal_link_count,
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
