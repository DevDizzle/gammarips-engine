"""Firestore + GCS + PRAW glue for reddit-poster."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from google.cloud import firestore, storage

PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")
GCS_DRAFTS_BUCKET = os.getenv("GCS_DRAFTS_BUCKET", "gammarips-reddit-drafts")
DEFAULT_SUBREDDITS = tuple(
    s.strip()
    for s in os.getenv("DEFAULT_SUBREDDITS", "options,thetagang,algotrading").split(",")
    if s.strip()
)
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

_fs_client: firestore.Client | None = None
_gcs_client: storage.Client | None = None


def fs() -> firestore.Client:
    global _fs_client
    if _fs_client is None:
        _fs_client = firestore.Client(project=PROJECT_ID)
    return _fs_client


def gcs() -> storage.Client:
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = storage.Client(project=PROJECT_ID)
    return _gcs_client


# --- Data reads -----------------------------------------------------------

def fetch_todays_pick(scan_date: str) -> dict | None:
    snap = fs().collection("todays_pick").document(scan_date).get()
    if not snap.exists:
        return None
    return snap.to_dict()


def fetch_recent_close(now_utc: datetime | None = None) -> dict | None:
    """Return the most-recent signal_performance doc closed in the last 24h.
    If multiple closed in the window, pick the highest peak_return.

    Enriches the returned dict with the running V5.4 cohort tally
    (`wins_so_far`, `closed_so_far`) so the receipt template can render
    "cohort so far: 1/1 wins". Source: `cohort_stats/current` Firestore doc
    written by signal-notifier on every run.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=24)
    docs = (
        fs()
        .collection("signal_performance")
        .where("closed_at", ">=", cutoff)
        .stream()
    )
    rows: list[dict] = []
    for d in docs:
        data = d.to_dict() or {}
        if not data.get("outcome"):
            continue
        rows.append(data)
    if not rows:
        return None
    rows.sort(key=lambda r: float(r.get("peak_return") or 0), reverse=True)
    perf = rows[0]

    cohort_snap = fs().collection("cohort_stats").document("current").get()
    if cohort_snap.exists:
        cohort = cohort_snap.to_dict() or {}
        perf["wins_so_far"] = cohort.get("trades_won")
        perf["closed_so_far"] = cohort.get("trades_closed")
    return perf


# --- Subreddit selection (round-robin) ------------------------------------

def pick_subreddit(post_type: str, override: str | None = None) -> str:
    """Round-robin across DEFAULT_SUBREDDITS via Firestore state.
    For pnl_receipt, mirror the subreddit the originating trade_idea posted to
    (read from reddit_post_state/today_idea_sub).
    """
    if override:
        return override.lstrip("r/").lstrip("/")

    state = fs().collection("reddit_post_state")

    if post_type == "pnl_receipt":
        snap = state.document("today_idea_sub").get()
        if snap.exists:
            sub = (snap.to_dict() or {}).get("subreddit")
            if sub:
                return sub

    last_snap = state.document("last_subreddit").get()
    last = (last_snap.to_dict() or {}).get("subreddit") if last_snap.exists else None
    subs = list(DEFAULT_SUBREDDITS) or ["options"]
    if last in subs:
        idx = (subs.index(last) + 1) % len(subs)
    else:
        idx = 0
    return subs[idx]


def record_subreddit_state(post_type: str, subreddit: str) -> None:
    state = fs().collection("reddit_post_state")
    state.document("last_subreddit").set(
        {"subreddit": subreddit, "updated_at": datetime.now(timezone.utc)}
    )
    if post_type == "trade_idea":
        state.document("today_idea_sub").set(
            {"subreddit": subreddit, "updated_at": datetime.now(timezone.utc)}
        )


# --- Idempotency ----------------------------------------------------------

def reddit_post_doc_id(scan_date: str, post_type: str, subreddit: str) -> str:
    return f"{scan_date}_{post_type}_{subreddit}"


def already_posted(scan_date: str, post_type: str, subreddit: str) -> bool:
    snap = (
        fs()
        .collection("reddit_posts")
        .document(reddit_post_doc_id(scan_date, post_type, subreddit))
        .get()
    )
    if not snap.exists:
        return False
    return (snap.to_dict() or {}).get("status") == "posted"


def mark_pending(scan_date: str, post_type: str, subreddit: str, body: str, title: str) -> None:
    fs().collection("reddit_posts").document(
        reddit_post_doc_id(scan_date, post_type, subreddit)
    ).set(
        {
            "scan_date": scan_date,
            "post_type": post_type,
            "subreddit": subreddit,
            "title": title,
            "body": body,
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
    )


def mark_posted(
    scan_date: str,
    post_type: str,
    subreddit: str,
    reddit_url: str,
    reddit_id: str,
) -> None:
    fs().collection("reddit_posts").document(
        reddit_post_doc_id(scan_date, post_type, subreddit)
    ).set(
        {
            "status": "posted",
            "reddit_url": reddit_url,
            "reddit_id": reddit_id,
            "posted_at": datetime.now(timezone.utc),
        },
        merge=True,
    )


def mark_skipped(
    scan_date: str, post_type: str, subreddit: str, reason: str
) -> None:
    fs().collection("reddit_posts").document(
        reddit_post_doc_id(scan_date, post_type, subreddit)
    ).set(
        {"status": "skipped", "reason": reason, "updated_at": datetime.now(timezone.utc)},
        merge=True,
    )


# --- GCS draft writes (DRY_RUN) -------------------------------------------

def write_draft(scan_date: str, post_type: str, subreddit: str, title: str, body: str) -> str:
    blob_name = f"{scan_date}/{post_type}_{subreddit}.md"
    bucket = gcs().bucket(GCS_DRAFTS_BUCKET)
    blob = bucket.blob(blob_name)
    content = f"# {title}\n\n{body}\n"
    blob.upload_from_string(content, content_type="text/markdown")
    return f"gs://{GCS_DRAFTS_BUCKET}/{blob_name}"


# --- PRAW client factory --------------------------------------------------

def reddit_client() -> Any:
    """Build a PRAW client from env vars. Returns None if creds missing.
    Caller is responsible for handling None (DRY_RUN should never call this).
    """
    try:
        import praw
    except ImportError:
        return None
    cid = os.getenv("REDDIT_CLIENT_ID")
    csec = os.getenv("REDDIT_CLIENT_SECRET")
    user = os.getenv("REDDIT_USERNAME")
    pwd = os.getenv("REDDIT_PASSWORD")
    if not all([cid, csec, user, pwd]):
        return None
    user_agent = os.getenv("REDDIT_USER_AGENT", f"gammarips-poster/0.1 by u/{user}")
    return praw.Reddit(
        client_id=cid,
        client_secret=csec,
        username=user,
        password=pwd,
        user_agent=user_agent,
    )


def submit_post(client: Any, subreddit: str, title: str, body: str) -> dict:
    """Submit a self-post. Returns {reddit_id, reddit_url} or raises."""
    submission = client.subreddit(subreddit).submit(title=title, selftext=body)
    return {
        "reddit_id": submission.id,
        "reddit_url": f"https://reddit.com{submission.permalink}",
    }


def today_et_iso() -> str:
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo("America/New_York")).date().isoformat()
