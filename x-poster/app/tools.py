"""
Deterministic tools for x-poster agents.

All tools return JSON-serializable dicts. Return {"status": "empty"|"error"|"success", ...}
so agents can branch deterministically on missing data without prompt-parsing.
"""
from __future__ import annotations

import io
import logging
import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from google.cloud import bigquery

from gammarips_content import brand, compliance, firestore_helpers, tweepy_helper

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
DATASET = os.getenv("DATASET", "profit_scout")
LEDGER_TABLE = f"{PROJECT_ID}.{DATASET}.forward_paper_ledger"
ENRICHED_TABLE = f"{PROJECT_ID}.{DATASET}.overnight_signals_enriched"
GCS_BUCKET = os.getenv("GCS_BUCKET", "gammarips-x-media")
BRAND_REF_GCS = os.getenv("BRAND_REF_GCS", f"gs://{GCS_BUCKET}/brand_ref_card.png")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gemini-3-pro-image-preview")

ET = ZoneInfo("America/New_York")


def _jsonable(value):
    """Recursively coerce BigQuery/Firestore return values to JSON-safe types.

    BigQuery DATE → str (isoformat), TIMESTAMP/DATETIME → str (isoformat),
    bytes/Decimal → str. Dicts/lists are walked; primitives pass through.
    """
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    # google.cloud.bigquery returns Decimal for NUMERIC; Firestore returns
    # DatetimeWithNanoseconds which is a datetime subclass (handled above).
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:  # noqa: BLE001
            return str(value)
    return value


# Lazy singletons — ADK tools run in an agent runtime; build on first call.
_bq_client: bigquery.Client | None = None
_fs_client = None


def _bq() -> bigquery.Client:
    global _bq_client
    if _bq_client is None:
        _bq_client = bigquery.Client(project=PROJECT_ID)
    return _bq_client


def _fs():
    global _fs_client
    if _fs_client is None:
        _fs_client = firestore_helpers.get_client(PROJECT_ID)
    return _fs_client


# ---------------------------------------------------------------------------
# Read tools (planner)
# ---------------------------------------------------------------------------

def _normalize_percent(value):
    """Coerce a percentage-like value to display units (6.42 not 0.0642).

    Firestore `todays_pick` stores moneyness_pct as a fraction (0.0642) from
    upstream, but writer templates render it with `%` appended assuming display
    units. Normalize once at the tool boundary so all downstream logic gets
    a consistent representation.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return value
    # Values < 1 are fractional representations — convert to display percent.
    # Preserve explicit 0.0 (no OTM) and already-percent values (>= 1.0).
    if 0.0 < v < 1.0:
        return round(v * 100, 2)
    return v


def fetch_todays_pick(scan_date: str) -> dict:
    """Fetch today's V5.3 signal pick from Firestore `todays_pick/{scan_date}`.

    Normalizes `moneyness_pct` to display units (6.42 not 0.0642) so the writer
    template renders `6.42%` consistently regardless of upstream storage.

    Args:
        scan_date: Date in YYYY-MM-DD format (Eastern time).

    Returns:
        dict: {"status": "success", "data": {...pick fields...}}
              or {"status": "empty", "message": "No pick for YYYY-MM-DD"}
    """
    pick = firestore_helpers.fetch_todays_pick(_fs(), scan_date)
    if pick is None:
        return {"status": "empty", "message": f"No pick doc for {scan_date}"}
    data = _jsonable(pick)
    if isinstance(data, dict) and "moneyness_pct" in data:
        data["moneyness_pct"] = _normalize_percent(data["moneyness_pct"])
    return {"status": "success", "data": data}


def fetch_todays_report_summary(scan_date: str) -> dict:
    """Fetch today's overnight report summary from Firestore `overnight_reports/{scan_date}`.

    Args:
        scan_date: Date in YYYY-MM-DD format (Eastern time).

    Returns:
        dict: {"status": "success", "data": {"title": ..., "headline": ..., "top_bullets": [...]}}
              or {"status": "empty"}
    """
    report = firestore_helpers.fetch_todays_report(_fs(), scan_date)
    if report is None:
        return {"status": "empty", "message": f"No report for {scan_date}"}
    # Extract top bullets from markdown content — rough heuristic.
    content = report.get("content", "")
    bullets = [line for line in content.split("\n") if line.strip().startswith(("- ", "* "))][:2]
    return {
        "status": "success",
        "data": _jsonable({
            "title": report.get("title", ""),
            "headline": report.get("headline", ""),
            "top_bullets": bullets,
        }),
    }


def fetch_closing_trades(scan_date: str) -> dict:
    """Query `forward_paper_ledger` for trades that closed today.

    Args:
        scan_date: The EXIT date (YYYY-MM-DD). A trade entered 2026-04-21 and closed
            2026-04-24 is returned when scan_date='2026-04-24'.

    Returns:
        dict: {"status": "success", "data": {"wins": [...], "losses": [...]}}
              Each item: ticker, direction, entry_date, entry_price, realized_return_pct, exit_reason.
    """
    query = f"""
        SELECT
            scan_date AS entry_date,
            ticker, direction,
            entry_price, realized_return_pct, exit_reason
        FROM `{LEDGER_TABLE}`
        WHERE DATE(exit_timestamp) = @scan_date
          AND exit_reason IS NOT NULL
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("scan_date", "DATE", scan_date)]
            ),
        )
        rows = [dict(r) for r in job.result()]
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_closing_trades failed: {exc}")
        return {"status": "error", "message": str(exc)}

    wins = [r for r in rows if (r.get("realized_return_pct") or 0) > 0]
    losses = [r for r in rows if (r.get("realized_return_pct") or 0) <= 0]
    return {
        "status": "success",
        "data": _jsonable({"wins": wins, "losses": losses, "total": len(rows)}),
    }


def fetch_runner_ups(scan_date: str, n: int) -> dict:
    """Query `overnight_signals_enriched` for top-N runner-up signals (excluding daily pick).

    Args:
        scan_date: Date in YYYY-MM-DD format.
        n: Number of runner-ups to return (2-5 typical).

    Returns:
        dict: {"status": "success", "data": [{ticker, direction, overnight_score, vol_oi_ratio, moneyness_pct}, ...]}
    """
    query = f"""
        SELECT
            ticker, direction, overnight_score, volume_oi_ratio AS vol_oi_ratio,
            recommended_spread_pct, is_premium_signal
        FROM `{ENRICHED_TABLE}`
        WHERE scan_date = @scan_date
        ORDER BY overnight_score DESC
        LIMIT @n
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("scan_date", "DATE", scan_date),
                    bigquery.ScalarQueryParameter("n", "INT64", max(n, 1)),
                ]
            ),
        )
        rows = [dict(r) for r in job.result()]
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_runner_ups failed: {exc}")
        return {"status": "error", "message": str(exc)}

    return {"status": "success", "data": _jsonable(rows)}


def fetch_original_tweet_id(original_scan_date: str) -> dict:
    """Look up the tweet_id of the original `signal` post for a past scan_date.

    Used by win/loss callback posts that want to quote-retweet the original call.

    Args:
        original_scan_date: Entry date (YYYY-MM-DD) of the trade being recapped.

    Returns:
        dict: {"status": "success", "tweet_id": "..."} or {"status": "empty"}
    """
    tweet_id = firestore_helpers.fetch_original_tweet_id(_fs(), original_scan_date)
    if tweet_id is None:
        return {"status": "empty", "message": f"No signal post logged for {original_scan_date}"}
    return {"status": "success", "tweet_id": tweet_id}


def fetch_weekly_ledger(week_ending: str) -> dict:
    """Query the past 5 trading days' closes for the Friday scorecard.

    Args:
        week_ending: Friday date in YYYY-MM-DD format.

    Returns:
        dict: {"status": "success", "data": {"trades": [...], "wins": N, "losses": N, "net_return_pct": X}}
    """
    end = datetime.strptime(week_ending, "%Y-%m-%d").date()
    # Look back 7 calendar days (covers Mon-Fri with buffer)
    start = end - timedelta(days=7)
    query = f"""
        SELECT
            ticker, direction, scan_date AS entry_date,
            DATE(exit_timestamp) AS exit_date,
            realized_return_pct, exit_reason
        FROM `{LEDGER_TABLE}`
        WHERE DATE(exit_timestamp) BETWEEN @start AND @end
          AND exit_reason IS NOT NULL
        ORDER BY exit_timestamp
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start", "DATE", start.isoformat()),
                    bigquery.ScalarQueryParameter("end", "DATE", end.isoformat()),
                ]
            ),
        )
        rows = [dict(r) for r in job.result()]
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_weekly_ledger failed: {exc}")
        return {"status": "error", "message": str(exc)}

    wins = sum(1 for r in rows if (r.get("realized_return_pct") or 0) > 0)
    losses = len(rows) - wins
    net = sum((r.get("realized_return_pct") or 0) for r in rows)
    return {
        "status": "success",
        "data": _jsonable(
            {"trades": rows, "wins": wins, "losses": losses, "net_return_pct": net}
        ),
    }


# ---------------------------------------------------------------------------
# Rubric (planner or writer-invoked — optional; also enforced in reviewer callback)
# ---------------------------------------------------------------------------

def score_against_rubric(text: str, post_type: str) -> dict:
    """Deterministically score a candidate post against the compliance rubric.

    Args:
        text: Candidate tweet body.
        post_type: One of signal/standby/report/teaser/win/loss/scorecard.

    Returns:
        dict: {"passed": bool, "char_count": N, "char_budget": M, "failures": [...], "warnings": [...]}
    """
    result = compliance.score_against_rubric(text, post_type)
    return {
        "passed": result.passed,
        "char_count": result.char_count,
        "char_budget": result.char_budget,
        "failures": result.failures,
        "warnings": result.warnings,
    }


# ---------------------------------------------------------------------------
# Image generation (Nano Banana via Vertex AI) + PIL logo composite
# ---------------------------------------------------------------------------
#
# Strategy (Evan 2026-04-24): Let Nano Banana COOK an editorial image themed
# around the post's subject (ticker industry, daily report theme, etc.).
# DO NOT pass the og-image as a multimodal reference — it carries deprecated
# multi-agent debate visuals. Instead: brand guidelines flow via prompt only;
# the brand LOGO is composited deterministically via PIL bottom-right so the
# brand mark is pixel-perfect every time.

_logo_bytes: bytes | None = None
_logo_attempted: bool = False


def _load_logo() -> bytes | None:
    """Fetch the brand logo (gs://gammarips-x-media/brand_logo.jpg) once. Cache."""
    global _logo_bytes, _logo_attempted
    if _logo_attempted:
        return _logo_bytes
    _logo_attempted = True

    gcs_uri = os.getenv("LOGO_GCS", brand.LOGO_GCS)
    if not gcs_uri.startswith("gs://"):
        logger.warning(f"LOGO_GCS not a gs:// URI: {gcs_uri!r}")
        return None
    bucket_name, _, blob_name = gcs_uri[len("gs://"):].partition("/")
    if not bucket_name or not blob_name:
        logger.warning(f"LOGO_GCS malformed: {gcs_uri!r}")
        return None

    try:
        from google.cloud import storage
        client = storage.Client(project=PROJECT_ID)
        _logo_bytes = client.bucket(bucket_name).blob(blob_name).download_as_bytes()
        logger.info(f"Loaded brand logo: {len(_logo_bytes)} bytes from {gcs_uri}")
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Failed to load brand logo from {gcs_uri}: {exc}")
        _logo_bytes = None
    return _logo_bytes


def _composite_logo(
    image_bytes: bytes,
    logo_bytes: bytes,
    size_pct: float = 0.12,
    margin_px: int = 30,
) -> bytes:
    """Composite the brand logo onto bottom-right of the image.

    Returns PNG bytes. Logo is resized to size_pct of base image width with
    aspect preserved. The logo's own background (dark teal in our case) acts
    as a subtle badge on the dark editorial backdrop — works visually without
    needing a transparent PNG.
    """
    from io import BytesIO
    from PIL import Image

    base = Image.open(BytesIO(image_bytes)).convert("RGBA")
    logo = Image.open(BytesIO(logo_bytes)).convert("RGBA")

    new_w = max(1, int(base.width * size_pct))
    aspect = logo.height / logo.width
    new_h = max(1, int(new_w * aspect))
    logo = logo.resize((new_w, new_h), Image.LANCZOS)

    x = base.width - new_w - margin_px
    y = base.height - new_h - margin_px
    base.paste(logo, (x, y), logo)

    out = BytesIO()
    base.convert("RGB").save(out, format="PNG", optimize=True)
    return out.getvalue()


def generate_image(image_prompt: str, post_type: str) -> dict:
    """Generate an editorial image via Nano Banana, then composite the brand logo.

    Args:
        image_prompt: Writer's composed THEME-driven prompt (e.g. "Editorial
            image evoking $NVDA's semiconductor industry — silicon, fabrication,
            data centers. Dark palette."). NO text/logo guidance — that's
            handled by the deterministic logo composite step.
        post_type: Logged for observability + future post-type-specific tweaks.

    Returns:
        dict: {"status": "success", "image_bytes": <PNG bytes>, "image_url": None,
               "logo_composited": bool}
              or {"status": "error", "message": "...", "image_bytes": None}.
              Image generation is non-blocking for publish — caller falls back
              to text-only on error.
    """
    try:
        from google import genai
    except ImportError as exc:
        return {"status": "error", "message": f"google-genai import: {exc}", "image_bytes": None}

    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

        brand_preamble = brand.render_for_image_prompt()
        full_prompt = (
            f"{brand_preamble}\n\n"
            f"--- THEME-DRIVEN EDITORIAL IMAGE (post_type={post_type}) ---\n"
            f"{image_prompt}\n\n"
            f"Composition rules:\n"
            f"- 1200x675 horizontal landscape\n"
            f"- Editorial financial-news style. Bloomberg meets modern SaaS.\n"
            f"- Dominant palette: dark navy/slate backgrounds (#1a1f2e, #242a3d) "
            f"with brand-color accents (lime green #a4e600, gold #ffcc00, bear red #cc3333 if relevant).\n"
            f"- ABSOLUTELY NO TEXT, words, numbers, tickers, logos, wordmarks, or "
            f"watermarks in the image. The logo is composited separately. The "
            f"tweet copy carries the data.\n"
            f"- Avoid cliches: stock photo handshakes, generic city skylines, "
            f"computer screens with code, 'to the moon' rocket imagery, lit-up "
            f"trading terminals, generic 'business meeting' shots, hype graphics.\n"
            f"- Aim for: editorial, disciplined, sector-evocative, single focal "
            f"point with intentional negative space."
        )

        response = client.models.generate_content(model=IMAGE_MODEL, contents=full_prompt)

        for part in (response.candidates[0].content.parts if response.candidates else []):
            if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                raw_bytes = part.inline_data.data
                logo = _load_logo()
                if logo is not None:
                    try:
                        final_bytes = _composite_logo(raw_bytes, logo)
                        return {
                            "status": "success",
                            "image_bytes": final_bytes,
                            "image_url": None,
                            "logo_composited": True,
                        }
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(f"Logo composite failed, returning raw: {exc}")
                        return {
                            "status": "success",
                            "image_bytes": raw_bytes,
                            "image_url": None,
                            "logo_composited": False,
                        }
                return {
                    "status": "success",
                    "image_bytes": raw_bytes,
                    "image_url": None,
                    "logo_composited": False,
                }

        return {"status": "error", "message": "No inline_data in response", "image_bytes": None}
    except Exception as exc:  # noqa: BLE001
        logger.error(f"generate_image failed: {exc}")
        return {"status": "error", "message": str(exc), "image_bytes": None}


# ---------------------------------------------------------------------------
# Publishing + logging
# ---------------------------------------------------------------------------

def publish_to_x(
    text: str,
    image_bytes: bytes | None,
    quote_tweet_id: str | None = None,
    in_reply_to_tweet_id: str | None = None,
) -> dict:
    """Publish a tweet via Tweepy. Handles media + QRT + thread-reply.

    Honors DRY_RUN env var — returns a fake tweet_id without hitting X.

    Returns:
        dict: {"status": "success"|"error", "tweet_id": "..." | None, "error": "...", "dry_run": bool}
    """
    result = tweepy_helper.post_tweet(
        text=text,
        image_bytes=image_bytes,
        quote_tweet_id=quote_tweet_id,
        in_reply_to_tweet_id=in_reply_to_tweet_id,
    )
    return {
        "status": "success" if result.tweet_id else "error",
        "tweet_id": result.tweet_id,
        "error": result.error,
        "dry_run": result.dry_run,
    }


def log_post(
    scan_date: str,
    post_type: str,
    text: str,
    tweet_id: str | None = None,
    image_url: str | None = None,
    iterations: int = 1,
    error: str | None = None,
    dry_run: bool = False,
    thread_tweet_index: int | None = None,
) -> dict:
    """Log a published (or rejected) post to Firestore `x_posts/{doc_id}`.

    Returns:
        dict: {"status": "success"} — logging is fire-and-forget.
    """
    try:
        firestore_helpers.log_x_post(
            _fs(), scan_date=scan_date, post_type=post_type, text=text,
            tweet_id=tweet_id, image_url=image_url, iterations=iterations,
            error=error, dry_run=dry_run, thread_tweet_index=thread_tweet_index,
        )
        return {"status": "success"}
    except Exception as exc:  # noqa: BLE001
        logger.error(f"log_post failed: {exc}")
        return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# Utility for planners / entry handler
# ---------------------------------------------------------------------------

def today_et_iso() -> str:
    """Today's date in America/New_York, as YYYY-MM-DD."""
    return datetime.now(ET).date().isoformat()
