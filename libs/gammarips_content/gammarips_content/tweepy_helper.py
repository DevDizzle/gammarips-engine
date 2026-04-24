"""
Tweepy wrapper for @gammarips publishing.

Handles:
- OAuth 1.0a client construction from env (matches x-poster deploy.sh secret mounts)
- Media upload (images) via v1.1 API, then linked to v2 create_tweet via media_ids
- Quote-retweet via v2 create_tweet(quote_tweet_id=...)
- Thread reply via v2 create_tweet(in_reply_to_tweet_id=...)
- DRY_RUN mode — logs the would-be-tweet and returns a fake tweet_id
"""
from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PostResult:
    tweet_id: str | None
    error: str | None = None
    dry_run: bool = False


def _load_creds_from_env() -> dict[str, str]:
    return {
        "consumer_key": os.getenv("X_API_KEY", "").strip(),
        "consumer_secret": os.getenv("X_API_SECRET", "").strip(),
        "access_token": os.getenv("X_ACCESS_TOKEN", "").strip(),
        "access_token_secret": os.getenv("X_ACCESS_SECRET", "").strip(),
    }


def _creds_present(creds: dict[str, str]) -> bool:
    return all(creds.values())


def build_client() -> Any | None:
    """Build a Tweepy v2 Client. Returns None if creds missing (DRY_RUN).

    We import tweepy lazily so unit tests can run without the dep.
    """
    creds = _load_creds_from_env()
    if not _creds_present(creds):
        logger.warning("X credentials missing — Tweepy client not built (DRY_RUN).")
        return None
    import tweepy  # noqa: WPS433

    return tweepy.Client(
        consumer_key=creds["consumer_key"],
        consumer_secret=creds["consumer_secret"],
        access_token=creds["access_token"],
        access_token_secret=creds["access_token_secret"],
    )


def build_v1_api() -> Any | None:
    """Build a Tweepy v1.1 API handle — needed only for media_upload."""
    creds = _load_creds_from_env()
    if not _creds_present(creds):
        return None
    import tweepy  # noqa: WPS433

    auth = tweepy.OAuth1UserHandler(
        creds["consumer_key"],
        creds["consumer_secret"],
        creds["access_token"],
        creds["access_token_secret"],
    )
    return tweepy.API(auth)


def upload_media(image_bytes: bytes, filename: str = "card.png") -> str | None:
    """Upload an image and return its media_id string. None on failure."""
    api = build_v1_api()
    if api is None:
        return None
    try:
        media = api.media_upload(filename=filename, file=io.BytesIO(image_bytes))
        return str(media.media_id_string)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Media upload failed: {exc}")
        return None


def post_tweet(
    text: str,
    image_bytes: bytes | None = None,
    quote_tweet_id: str | None = None,
    in_reply_to_tweet_id: str | None = None,
    dry_run: bool = False,
) -> PostResult:
    """Publish a tweet. Handles media, QRT, thread-reply. Honors DRY_RUN env.

    Priority order:
    1. DRY_RUN=true env var OR dry_run=True arg → log + return fake id
    2. Creds missing → return error
    3. Upload media if image_bytes provided → media_ids
    4. create_tweet with text + media_ids + quote_tweet_id + in_reply_to_tweet_id
    """
    dry_run_env = os.getenv("DRY_RUN", "false").lower() == "true"
    if dry_run or dry_run_env:
        logger.info(f"[DRY_RUN] would post: {text!r}, qrt={quote_tweet_id}, reply={in_reply_to_tweet_id}")
        return PostResult(tweet_id=f"dry_run_{abs(hash(text)) % 10**12}", dry_run=True)

    client = build_client()
    if client is None:
        return PostResult(tweet_id=None, error="missing_credentials")

    media_ids: list[str] = []
    if image_bytes:
        media_id = upload_media(image_bytes)
        if media_id:
            media_ids.append(media_id)
        else:
            logger.warning("Image upload failed — shipping text-only.")

    try:
        kwargs: dict[str, Any] = {"text": text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        if quote_tweet_id:
            kwargs["quote_tweet_id"] = quote_tweet_id
        if in_reply_to_tweet_id:
            kwargs["in_reply_to_tweet_id"] = in_reply_to_tweet_id
        resp = client.create_tweet(**kwargs)
        tweet_id = str(resp.data["id"]) if resp and resp.data else None
        logger.info(f"Posted tweet: id={tweet_id}")
        return PostResult(tweet_id=tweet_id)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"create_tweet failed: {exc}")
        return PostResult(tweet_id=None, error=str(exc))
