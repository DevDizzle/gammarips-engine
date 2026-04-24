"""
Firestore helpers shared by x-poster and blog-generator.

Thin wrappers — keep business logic in each service; this module owns
schema-level concerns (doc IDs, timestamp fields, idempotency checks).
"""
from __future__ import annotations

import logging
import os
from typing import Any

from google.cloud import firestore

logger = logging.getLogger(__name__)

_DEFAULT_PROJECT = os.getenv("PROJECT_ID", "profitscout-fida8")


def get_client(project: str | None = None) -> firestore.Client:
    """Singleton-free getter — callers should cache the returned client themselves."""
    return firestore.Client(project=project or _DEFAULT_PROJECT)


# --- x-poster schema ---

def x_post_doc_id(scan_date: str, post_type: str, thread_tweet_index: int | None = None) -> str:
    """Canonical doc id for Firestore x_posts/ collection.

    Scorecard thread tweets get suffixed: `2026-04-24_scorecard_0`, `_1`, `_2`.
    Everything else is `{date}_{type}`.
    """
    if thread_tweet_index is not None:
        return f"{scan_date}_{post_type}_{thread_tweet_index}"
    return f"{scan_date}_{post_type}"


def fetch_original_tweet_id(db: firestore.Client, original_scan_date: str) -> str | None:
    """Look up the tweet_id of the original signal post for a given scan_date.

    Used by win/loss callback posts that QRT the original.
    """
    doc_id = x_post_doc_id(original_scan_date, "signal")
    snap = db.collection("x_posts").document(doc_id).get()
    if not snap.exists:
        return None
    return snap.to_dict().get("tweet_id")


def already_posted(db: firestore.Client, scan_date: str, post_type: str) -> bool:
    """Idempotency check — has this scan_date+post_type already published?"""
    snap = db.collection("x_posts").document(x_post_doc_id(scan_date, post_type)).get()
    return snap.exists


def log_x_post(
    db: firestore.Client,
    scan_date: str,
    post_type: str,
    text: str,
    tweet_id: str | None,
    image_url: str | None = None,
    iterations: int = 1,
    error: str | None = None,
    dry_run: bool = False,
    thread_tweet_index: int | None = None,
) -> None:
    """Write to x_posts/{doc_id}. Uses server timestamp."""
    doc_id = x_post_doc_id(scan_date, post_type, thread_tweet_index)
    db.collection("x_posts").document(doc_id).set({
        "scan_date": scan_date,
        "post_type": post_type,
        "text": text,
        "tweet_id": tweet_id,
        "image_url": image_url,
        "iterations": iterations,
        "error": error,
        "dry_run": dry_run,
        "posted_at": firestore.SERVER_TIMESTAMP,
        **({"thread_tweet_index": thread_tweet_index} if thread_tweet_index is not None else {}),
    })


# --- Signal / report readers (read-only, shared by planner agents) ---

def fetch_todays_pick(db: firestore.Client, scan_date: str) -> dict[str, Any] | None:
    snap = db.collection("todays_pick").document(scan_date).get()
    return snap.to_dict() if snap.exists else None


def fetch_todays_report(db: firestore.Client, scan_date: str) -> dict[str, Any] | None:
    snap = db.collection("overnight_reports").document(scan_date).get()
    return snap.to_dict() if snap.exists else None
