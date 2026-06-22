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
    """Fetch today's V5.4 signal pick from Firestore `todays_pick/{scan_date}`.

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


def fetch_closing_trades(scan_date: str, restrict_tickers: str = "") -> dict:
    """Query `forward_paper_ledger` for V7 trades that closed today.

    Returns each row pre-shaped for the WIN/LOSS writer template: derived
    `exit_price` (entry_price * (1 + realized_return_pct)), `pct_signed`
    string ("+80%" / "-60%"), and human-readable `exit_reason_display`.

    Args:
        scan_date: The EXIT date (YYYY-MM-DD).
        restrict_tickers: Comma-separated tickers to restrict the result to
            (typically the tickers we've publicly posted on X in the past
            lookback window — gathered via fetch_recently_posted_tickers).
            Empty string means "no filter, return all closes".

    Returns:
        dict: {"status": "success", "data": {"wins": [...], "losses": [...]}}
    """
    tickers = [t.strip().upper() for t in (restrict_tickers or "").split(",") if t.strip()]
    query = f"""
        SELECT
            scan_date AS entry_date,
            ticker, direction,
            ROUND(entry_price, 2) AS entry_price,
            ROUND(realized_return_pct, 2) AS realized_return_pct,
            exit_reason
        FROM `{LEDGER_TABLE}`
        WHERE DATE(exit_timestamp) = @scan_date
          AND exit_reason IS NOT NULL
          AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')
          AND policy_version = 'V7_1_TILTED_GIGO'
          AND (ARRAY_LENGTH(@tickers) = 0 OR ticker IN UNNEST(@tickers))
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("scan_date", "DATE", scan_date),
                    bigquery.ArrayQueryParameter("tickers", "STRING", tickers),
                ]
            ),
        )
        rows = [dict(r) for r in job.result()]
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_closing_trades failed: {exc}")
        return {"status": "error", "message": str(exc)}

    _exit_reason_display = {
        "TARGET": "target hit",
        "STOP": "stop hit",
        "TIMEOUT": "same-day close",  # V7: flat at 15:45 ET, no target/stop hit
    }
    enriched: list[dict] = []
    for r in rows:
        ep = r.get("entry_price")
        ret = r.get("realized_return_pct")
        exit_price = round(ep * (1.0 + ret), 2) if (ep is not None and ret is not None) else None
        pct_signed = (
            f"{'+' if ret >= 0 else ''}{int(round(ret * 100))}%"
            if ret is not None else None
        )
        enriched.append({
            **r,
            "exit_price": exit_price,
            "pct_signed": pct_signed,
            "exit_reason_display": _exit_reason_display.get(
                r.get("exit_reason") or "", r.get("exit_reason") or ""
            ),
        })

    wins = [r for r in enriched if (r.get("realized_return_pct") or 0) > 0]
    losses = [r for r in enriched if (r.get("realized_return_pct") or 0) <= 0]
    return {
        "status": "success",
        "data": _jsonable({"wins": wins, "losses": losses, "total": len(enriched)}),
    }


def fetch_watchlist(scan_date: str, n: int, exclude_ticker: str = "") -> dict:
    """Query `overnight_signals_enriched` for top-N high-dollar-volume setups.

    Used for the public X "watchlist" post — drives discovery via popular
    names without leaking the paid V5.4 daily pick. Ranks by total option
    dollar volume (call+put) which biases toward broad-attention tickers
    (CAT, MS, MELI, BE…) rather than small-cap unusual-activity names.

    Args:
        scan_date: YYYY-MM-DD.
        n: Top-N to return (typically 3).
        exclude_ticker: Daily-pick ticker to omit so the watchlist never
            duplicates the paid email.

    Returns:
        dict: {"status": "success", "data": [{ticker, direction, score,
              dollar_vol_m, vol_oi_ratio}, ...]}
              Empty list = "no qualifying setups today" — publisher skips.
    """
    query = f"""
        WITH effective AS (
            SELECT MAX(scan_date) AS d
            FROM `{ENRICHED_TABLE}`
            WHERE scan_date <= @scan_date
        )
        SELECT
            ticker,
            direction,
            ROUND(overnight_score, 1) AS score,
            ROUND((COALESCE(call_dollar_volume, 0) + COALESCE(put_dollar_volume, 0)) / 1e6, 2) AS dollar_vol_m,
            ROUND(volume_oi_ratio, 2) AS vol_oi_ratio
        FROM `{ENRICHED_TABLE}`
        WHERE scan_date = (SELECT d FROM effective)
          AND (@exclude_ticker = '' OR ticker != @exclude_ticker)
        ORDER BY (COALESCE(call_dollar_volume, 0) + COALESCE(put_dollar_volume, 0)) DESC
        LIMIT @n
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("scan_date", "DATE", scan_date),
                    bigquery.ScalarQueryParameter("n", "INT64", max(n, 1)),
                    bigquery.ScalarQueryParameter("exclude_ticker", "STRING", exclude_ticker or ""),
                ]
            ),
        )
        rows = [dict(r) for r in job.result()]
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_watchlist failed: {exc}")
        return {"status": "error", "message": str(exc)}

    return {"status": "success", "data": _jsonable(rows)}


def fetch_recently_posted_tickers(scan_date: str, lookback_days: int = 5) -> dict:
    """Scan recent x_posts (watchlist + signal types) for tickers we publicly named.

    Callbacks should ONLY post about tickers the X audience has seen us
    name — otherwise we'd surface paper-trade outcomes for tickers no
    follower has context for.

    Args:
        scan_date: Today's date (YYYY-MM-DD); look back from here.
        lookback_days: Calendar days to walk back. Under V7 (same-day exit) the
            close and its originating signal post are the SAME day, so today is
            always in range; 5 is kept as a harmless safety margin (the QRT
            lookup sorts newest-first, so it still pairs to today's signal).

    Returns:
        dict: {"status": "success", "tickers": ["BE", "STX", ...]} unique upper-case.
    """
    import re
    from datetime import datetime, timedelta

    end = datetime.strptime(scan_date, "%Y-%m-%d").date()
    start = end - timedelta(days=lookback_days)
    cashtag_re = re.compile(r"\$([A-Z]{1,5})\b")

    found: set[str] = set()
    try:
        col = _fs().collection("x_posts")
        # Doc IDs are `{date}_{post_type}` — Firestore string range works lexically.
        docs = (
            col.where("scan_date", ">=", start.isoformat())
               .where("scan_date", "<=", end.isoformat())
               .stream()
        )
        for d in docs:
            data = d.to_dict() or {}
            if data.get("post_type") not in ("watchlist", "signal"):
                continue
            if data.get("dry_run"):
                continue
            for m in cashtag_re.finditer(data.get("text") or ""):
                found.add(m.group(1).upper())
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_recently_posted_tickers failed: {exc}")
        return {"status": "error", "message": str(exc), "tickers": []}

    return {"status": "success", "tickers": sorted(found)}


def find_originating_post_for_ticker(ticker: str, lookback_days: int = 5) -> dict:
    """Find the most recent x_post that publicly mentioned `ticker` for QRT.

    Used by win-callback to QRT the originating watchlist or signal post.
    Walks back lookback_days, returns the first non-dry-run match.

    Returns:
        dict: {"status": "success", "tweet_id": "..."} or {"status": "empty"}
    """
    import re
    from datetime import datetime, timedelta

    cashtag_re = re.compile(rf"\$\b{re.escape(ticker.upper().lstrip('$'))}\b")
    end = datetime.now(ET).date()
    start = end - timedelta(days=lookback_days)
    try:
        docs = (
            _fs().collection("x_posts")
                 .where("scan_date", ">=", start.isoformat())
                 .where("scan_date", "<=", end.isoformat())
                 .stream()
        )
        candidates: list[tuple[str, str]] = []  # (scan_date, tweet_id)
        for d in docs:
            data = d.to_dict() or {}
            if data.get("post_type") not in ("watchlist", "signal"):
                continue
            tid = data.get("tweet_id")
            if not tid or str(tid).startswith("dry_run_") or data.get("dry_run"):
                continue
            if cashtag_re.search(data.get("text") or ""):
                candidates.append((data.get("scan_date") or "", tid))
        if not candidates:
            return {"status": "empty"}
        candidates.sort(reverse=True)  # newest first
        return {"status": "success", "tweet_id": candidates[0][1]}
    except Exception as exc:  # noqa: BLE001
        logger.error(f"find_originating_post_for_ticker failed: {exc}")
        return {"status": "error", "message": str(exc)}


def fetch_runner_ups(scan_date: str, n: int, exclude_ticker: str = "") -> dict:
    """Query `overnight_signals_enriched` for top-N runner-up signals.

    Args:
        scan_date: Date in YYYY-MM-DD format.
        n: Number of runner-ups to return (2-5 typical).
        exclude_ticker: Ticker to omit (typically today's daily pick — the teaser
            should show OTHER signals, not duplicate the SIGNAL post). Empty
            string means no exclusion.

    Returns:
        dict: {"status": "success", "data": [...]} with 0..n entries.
              Empty list is a valid result and means "no runner-ups today" —
              callers should treat as a skip signal for the teaser publish.
    """
    fetch_n = max(n, 1)
    query = f"""
        WITH effective AS (
            SELECT MAX(scan_date) AS d
            FROM `{ENRICHED_TABLE}`
            WHERE scan_date <= @scan_date
        )
        SELECT
            ticker, direction, overnight_score, volume_oi_ratio AS vol_oi_ratio,
            recommended_spread_pct, is_premium_signal
        FROM `{ENRICHED_TABLE}`
        WHERE scan_date = (SELECT d FROM effective)
          AND (@exclude_ticker = '' OR ticker != @exclude_ticker)
        ORDER BY overnight_score DESC
        LIMIT @n
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("scan_date", "DATE", scan_date),
                    bigquery.ScalarQueryParameter("n", "INT64", fetch_n),
                    bigquery.ScalarQueryParameter("exclude_ticker", "STRING", exclude_ticker or ""),
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


def fetch_weekly_ledger(week_ending: str, restrict_tickers: str = "") -> dict:
    """Query the past 5 trading days. V7 closes for the Friday scorecard.

    The scorecard reflects the PUBLIC track record — only trades on tickers
    the X audience has seen us name should appear. Pass `restrict_tickers`
    populated from `fetch_recently_posted_tickers(scan_date, lookback=10)`.

    Filters: V7_1_TILTED_GIGO only, drops INVALID_LIQUIDITY/SKIPPED. Each
    row pre-shaped for the writer template (pct_signed, outcome_emoji,
    direction_short).

    Args:
        week_ending: Friday date in YYYY-MM-DD format.
        restrict_tickers: Comma-separated tickers to restrict to. Empty = all
            V5.4 closes (use only for internal/admin scorecards — public X
            scorecards must restrict).

    Returns:
        dict: {"status": "success", "data": {"trades": [...], "wins": N,
              "losses": N, "net_return_pct": X (display %, sum of trade %s)}}
    """
    end = datetime.strptime(week_ending, "%Y-%m-%d").date()
    start = end - timedelta(days=7)
    tickers = [t.strip().upper() for t in (restrict_tickers or "").split(",") if t.strip()]
    query = f"""
        SELECT
            ticker, direction, scan_date AS entry_date,
            DATE(exit_timestamp) AS exit_date,
            ROUND(realized_return_pct, 2) AS realized_return_pct,
            exit_reason
        FROM `{LEDGER_TABLE}`
        WHERE DATE(exit_timestamp) BETWEEN @start AND @end
          AND exit_reason IS NOT NULL
          AND exit_reason NOT IN ('INVALID_LIQUIDITY', 'SKIPPED')
          AND policy_version = 'V7_1_TILTED_GIGO'
          AND (ARRAY_LENGTH(@tickers) = 0 OR ticker IN UNNEST(@tickers))
        ORDER BY exit_timestamp
    """
    try:
        job = _bq().query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start", "DATE", start.isoformat()),
                    bigquery.ScalarQueryParameter("end", "DATE", end.isoformat()),
                    bigquery.ArrayQueryParameter("tickers", "STRING", tickers),
                ]
            ),
        )
        rows = [dict(r) for r in job.result()]
    except Exception as exc:  # noqa: BLE001
        logger.error(f"fetch_weekly_ledger failed: {exc}")
        return {"status": "error", "message": str(exc)}

    enriched: list[dict] = []
    for r in rows:
        ret = r.get("realized_return_pct")
        if ret is None:
            continue
        is_win = ret > 0
        pct_int = int(round(ret * 100))
        enriched.append({
            **r,
            "outcome_emoji": "✅" if is_win else "❌",
            "direction_short": "BULL" if (r.get("direction") or "").upper().startswith("BULL") else "BEAR",
            "pct_signed": f"{'+' if pct_int >= 0 else ''}{pct_int}%",
        })

    wins = sum(1 for r in enriched if (r.get("realized_return_pct") or 0) > 0)
    losses = len(enriched) - wins
    net_pct_display = round(
        sum((r.get("realized_return_pct") or 0) for r in enriched) * 100, 1
    )
    return {
        "status": "success",
        "data": _jsonable(
            {"trades": enriched, "wins": wins, "losses": losses,
             "net_return_pct": net_pct_display}
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


# Path inside the deployed image (Dockerfile copies ./assets to /code/assets).
# Resolved relative to this file so local `make playground` and Cloud Run both
# find the bundled font.
_FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets",
                          "SpaceGrotesk-VariableFont_wght.ttf")

# Fallback if the bundled TTF is missing — DejaVu Sans Bold is in slim images
# only sometimes, so the function is defensive: it returns the input unchanged
# rather than crashing the publish pipeline.
_DEJAVU_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _composite_ticker_overlay(
    image_bytes: bytes,
    ticker: str,
    direction: str,
    ticker_pt: int = 180,
    direction_pt: int = 60,
    margin_px: int = 60,
) -> bytes:
    """Composite a large `$TICKER` + direction badge on the upper-left of the image.

    For signal/win/loss posts only — gives feed-scroll readability without
    relying on the AI image to render text. Drop-shadow ensures legibility on
    any backdrop. Returns PNG bytes; never raises (returns input on failure).

    Color contract: BULLISH → brand lime-green #a4e600, BEARISH → bear red
    #cc3333. Direction defaults to neutral off-white if anything else.
    """
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont

    try:
        base = Image.open(BytesIO(image_bytes)).convert("RGBA")

        font_path = _FONT_PATH if os.path.exists(_FONT_PATH) else _DEJAVU_FALLBACK
        if not os.path.exists(font_path):
            logger.warning("ticker overlay: no font available, returning input")
            return image_bytes

        ticker_font = ImageFont.truetype(font_path, size=ticker_pt)
        direction_font = ImageFont.truetype(font_path, size=direction_pt)
        # Set Bold weight on the variable font when supported.
        for f in (ticker_font, direction_font):
            try:
                f.set_variation_by_name("Bold")
            except Exception:  # noqa: BLE001
                pass

        dir_upper = (direction or "").upper().strip()
        if dir_upper.startswith("BULL"):
            accent = (164, 230, 0, 255)   # #a4e600
        elif dir_upper.startswith("BEAR"):
            accent = (204, 51, 51, 255)   # #cc3333
        else:
            accent = (232, 236, 247, 255)  # #e8ecf7 (foreground)

        ticker_text = f"${ticker.upper().lstrip('$')}"
        direction_text = dir_upper

        # Draw onto a transparent overlay so the shadow blends correctly.
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Drop shadow (offset 4px, semi-opaque black).
        shadow_offset = 4
        shadow_color = (0, 0, 0, 200)
        draw.text(
            (margin_px + shadow_offset, margin_px + shadow_offset),
            ticker_text, font=ticker_font, fill=shadow_color,
        )
        draw.text(
            (margin_px, margin_px),
            ticker_text, font=ticker_font, fill=(255, 255, 255, 255),
        )

        # Direction badge sits below the ticker, accent color, with shadow.
        # Use textbbox to space it consistently regardless of font metrics.
        ticker_bbox = draw.textbbox((margin_px, margin_px), ticker_text, font=ticker_font)
        dir_y = ticker_bbox[3] + 8  # 8px gap under ticker baseline-box
        draw.text(
            (margin_px + shadow_offset, dir_y + shadow_offset),
            direction_text, font=direction_font, fill=shadow_color,
        )
        draw.text(
            (margin_px, dir_y),
            direction_text, font=direction_font, fill=accent,
        )

        composed = Image.alpha_composite(base, overlay)
        out = BytesIO()
        composed.convert("RGB").save(out, format="PNG", optimize=True)
        return out.getvalue()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"ticker overlay failed, returning unmodified image: {exc}")
        return image_bytes


def generate_image(
    image_prompt: str,
    post_type: str,
    ticker: str | None = None,
    direction: str | None = None,
) -> dict:
    """Generate an editorial image via Nano Banana, then composite the brand logo.

    For post_type ∈ {signal, win, loss}, additionally composites a large
    `$TICKER` + direction PIL overlay on the upper-left for feed-scroll
    readability. Other post_types stay editorial-clean.

    Args:
        image_prompt: Writer's composed THEME-driven prompt (e.g. "Editorial
            image evoking $NVDA's semiconductor industry — silicon, fabrication,
            data centers. Dark palette."). NO text/logo guidance — that's
            handled by the deterministic logo composite step.
        post_type: Logged for observability + future post-type-specific tweaks.
        ticker: Cashtag (without `$`) for the optional ticker overlay. Required
            when post_type ∈ {signal, win, loss}; ignored otherwise.
        direction: BULLISH or BEARISH for the direction badge color + label.

    Returns:
        dict: {"status": "success", "image_bytes": <PNG bytes>, "image_url": None,
               "logo_composited": bool, "ticker_overlay": bool}
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

                # Step 1: composite brand logo (every post type).
                logo = _load_logo()
                logo_composited = False
                if logo is not None:
                    try:
                        raw_bytes = _composite_logo(raw_bytes, logo)
                        logo_composited = True
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(f"Logo composite failed: {exc}")

                # Step 2: composite ticker overlay (signal/win/loss only).
                # post_type "callback" also triggers — the scheduler payload is
                # always "callback" and the writer routes internally to win/loss.
                overlay_applied = False
                if post_type in ("signal", "win", "loss", "callback") and ticker:
                    try:
                        raw_bytes = _composite_ticker_overlay(
                            raw_bytes, ticker=ticker, direction=direction or "",
                        )
                        overlay_applied = True
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(f"Ticker overlay failed: {exc}")

                return {
                    "status": "success",
                    "image_bytes": raw_bytes,
                    "image_url": None,
                    "logo_composited": logo_composited,
                    "ticker_overlay": overlay_applied,
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
