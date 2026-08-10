"""Regenerate the overnight scan universe file from Polygon.

Universe definition: active US exchange-listed common stocks (Polygon type=CS,
matching the hand-curated original: no ETFs, no ADRs) that have at least one
listed call expiring inside ~75 days. Replaces the static list that froze on
2026-02-13 and silently excluded every later listing (FINDINGS_LEDGER.md
2026-08-05).

Hard-won API facts (verified 2026-08-05, do not "simplify" these away):
- Polygon next_url cursor pagination SILENTLY SKIPS ROWS on both
  /v3/reference/tickers and /v3/reference/options/contracts (RDDT was dropped
  by both bulk walks while point lookups and gte-windows return it). So bulk
  enumeration uses explicit keyset pagination (ticker.gte=<last seen>,
  inclusive, dedup) and never trusts next_url.
- Unfiltered limit=1000 pages of /v3/reference/options/contracts time out
  server-side; optionability is therefore checked per-name (limit=1 probe),
  which is also what makes membership decisions point-verified.
- No name is removed on bulk evidence alone: current-universe names missing
  from the enumeration get a point lookup before they may be dropped, and
  probe errors fail OPEN (keep the name; a stale extra costs one chain fetch,
  a wrongly dropped name is invisible forever).

Consumed by overnight-scanner's POST /refresh_universe (weekly Cloud Scheduler)
and by scripts/universe/refresh_universe.py (manual CLI). Full run is ~9 min
(~7K rate-limited Polygon requests) — the service timeout must stay above that.
"""

import concurrent.futures
import datetime
import logging
import threading
import time

import requests
from google.cloud import storage

from src.enrichment.core import config

logger = logging.getLogger(__name__)

BACKUP_PREFIX = "universe-backups/"
TICKERS_URL = "https://api.polygon.io/v3/reference/tickers"
CONTRACTS_URL = "https://api.polygon.io/v3/reference/options/contracts"
PAGE_LIMIT = 1000
REQS_PER_SEC = 15  # stay under the 20 req/s plan cap
EXPIRY_HORIZON_DAYS = 75  # monthlies + quarterly cycle: every optionable name lists inside this
MIN_UNIVERSE_SIZE = 3000
MAX_SHRINK_PCT = 0.15
MAX_GROWTH_PCT = 0.15
# Probes fail OPEN per-name, but systematic probe failure must abort the write:
# a degraded contracts endpoint would otherwise balloon the universe with
# non-optionable names while every size guard passes (review 2026-08-05).
MAX_PROBE_ERROR_RATE = 0.03
PROBE_WORKERS = 8

_rate_lock = threading.Lock()
_last_request = [0.0]


class _ProbeStats:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.errors = 0
        self.total = 0

    def wrap(self, fn):
        """Run a probe; on error count it and fail OPEN (keep the name)."""
        with self.lock:
            self.total += 1
        try:
            return fn()
        except Exception as e:
            with self.lock:
                self.errors += 1
                if self.errors <= 5:
                    logger.warning("Universe refresh: probe error (fail-open): %s", e)
            return True


def _throttled_get(session: requests.Session, url: str, params: dict | None) -> requests.Response:
    """GET with a global rate limit and retry/backoff. Raises after 4 failures."""
    last_exc: Exception | None = None
    for attempt in range(4):
        with _rate_lock:
            wait = _last_request[0] + 1.0 / REQS_PER_SEC - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            _last_request[0] = time.monotonic()
        try:
            resp = session.get(url, params=params, timeout=60)
        except requests.RequestException as e:
            last_exc = e
            time.sleep(2**attempt)
            continue
        if resp.status_code == 429 or resp.status_code >= 500:
            last_exc = RuntimeError(f"HTTP {resp.status_code}")
            time.sleep(2**attempt)
            continue
        resp.raise_for_status()
        return resp
    raise last_exc  # type: ignore[misc]


def _enumerate_common_stocks(session: requests.Session) -> set[str]:
    """Keyset-paginate all active type=CS tickers (never trusts next_url)."""
    tickers: set[str] = set()
    cursor = ""
    while True:
        params = {
            "market": "stocks", "active": "true", "type": "CS",
            "sort": "ticker", "order": "asc", "limit": PAGE_LIMIT,
        }
        if cursor:
            params["ticker.gte"] = cursor
        rows = _throttled_get(session, TICKERS_URL, params).json().get("results") or []
        page = [t for t in ((r.get("ticker") or "").strip().upper() for r in rows) if t]
        before = len(tickers)
        tickers.update(page)
        # Termination: a page adding nothing new means we've re-fetched the tail.
        if not page or (len(tickers) == before and cursor) or page[-1] == cursor:
            break
        cursor = page[-1]
    logger.info("Universe refresh: %d active CS tickers (keyset walk)", len(tickers))
    return tickers


def _is_active_common_stock(session: requests.Session, ticker: str) -> bool:
    """Point lookup: is this ticker an active type=CS? (Raises on error; the
    caller's _ProbeStats.wrap applies fail-open and counts the error.)"""
    rows = _throttled_get(session, TICKERS_URL, {"ticker": ticker}).json().get("results") or []
    return any(r.get("ticker", "").upper() == ticker and r.get("active") and r.get("type") == "CS"
               for r in rows)


def _has_near_term_calls(session: requests.Session, ticker: str, horizon: str) -> bool:
    """Point probe: does this underlying list a call inside the horizon?
    (Raises on error; the caller's _ProbeStats.wrap applies fail-open.)"""
    params = {
        "underlying_ticker": ticker, "expired": "false", "contract_type": "call",
        "expiration_date.lte": horizon, "limit": 1,
    }
    return bool(_throttled_get(session, CONTRACTS_URL, params).json().get("results") or [])


def run_refresh(api_key: str | None = None, dry_run: bool = False, allow_shrink: bool = False,
                allow_growth: bool = False, project: str | None = None) -> dict:
    """Derive the current universe, diff against the live file, and (unless
    dry_run) back it up and overwrite it. Returns a summary dict; raises
    ValueError when a safety guard aborts the write."""
    # .strip() is load-bearing: the Secret Manager mount delivers the key with a
    # trailing newline, which is an invalid HTTP header value.
    api_key = (api_key or config.POLYGON_API_KEY or "").strip()
    if not api_key:
        raise ValueError("POLYGON_API_KEY not configured")
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {api_key}"

    gcs = storage.Client(project=project or config.PROJECT_ID)
    bucket = gcs.bucket(config.GCS_BUCKET_NAME)
    blob = bucket.blob(config.OVERNIGHT_UNIVERSE_FILE)
    blob.reload()
    old_updated = blob.updated.date().isoformat()
    old = {t.strip().upper() for t in blob.download_as_text().splitlines() if t.strip()}
    logger.info("Universe refresh: current file %d tickers, last modified %s", len(old), old_updated)

    stats = _ProbeStats()
    enumerated = _enumerate_common_stocks(session)
    # Removal-verification net: current names the bulk walk missed get a point lookup.
    leftovers = sorted(old - enumerated)
    recovered = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=PROBE_WORKERS) as pool:
        for t, ok in zip(leftovers, pool.map(
                lambda t: stats.wrap(lambda: _is_active_common_stock(session, t)), leftovers)):
            if ok:
                recovered.add(t)
    logger.info("Universe refresh: %d leftovers point-checked, %d still active CS",
                len(leftovers), len(recovered))
    candidates = sorted(enumerated | recovered)

    horizon = (datetime.date.today() + datetime.timedelta(days=EXPIRY_HORIZON_DAYS)).isoformat()
    new: set[str] = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=PROBE_WORKERS) as pool:
        for t, ok in zip(candidates, pool.map(
                lambda t: stats.wrap(lambda: _has_near_term_calls(session, t, horizon)), candidates)):
            if ok:
                new.add(t)
    logger.info("Universe refresh: %d candidates -> %d optionable common stocks "
                "(%d/%d probes failed open)", len(candidates), len(new), stats.errors, stats.total)

    summary = {
        "old_count": len(old), "new_count": len(new),
        "added": len(new - old), "removed": len(old - new),
        "added_sample": sorted(new - old)[:25], "removed_sample": sorted(old - new)[:25],
        "probe_errors": stats.errors, "probes_total": stats.total,
        "dry_run": dry_run, "uploaded": False,
    }

    if stats.total and stats.errors / stats.total > MAX_PROBE_ERROR_RATE:
        raise ValueError(f"universe refresh aborted: {stats.errors}/{stats.total} probes failed "
                         f"open (> {MAX_PROBE_ERROR_RATE:.0%}) — derived set untrustworthy")
    if len(new) < MIN_UNIVERSE_SIZE:
        raise ValueError(f"universe refresh aborted: derived {len(new)} < floor {MIN_UNIVERSE_SIZE}")
    if len(new) < len(old) * (1 - MAX_SHRINK_PCT) and not allow_shrink:
        raise ValueError(f"universe refresh aborted: shrink {len(old)} -> {len(new)} "
                         f"exceeds {MAX_SHRINK_PCT:.0%}")
    if len(new) > len(old) * (1 + MAX_GROWTH_PCT) and not allow_growth:
        raise ValueError(f"universe refresh aborted: growth {len(old)} -> {len(new)} "
                         f"exceeds {MAX_GROWTH_PCT:.0%}")
    if dry_run:
        return summary

    # Generation-pinned compare-and-swap: back up exactly the generation we read
    # and refuse the write if anyone updated the file since (412 -> 500 upstream).
    backup_name = f"{BACKUP_PREFIX}{config.OVERNIGHT_UNIVERSE_FILE.removesuffix('.txt')}-{old_updated}.txt"
    bucket.copy_blob(blob, bucket, backup_name, source_generation=blob.generation)
    blob.upload_from_string("\n".join(sorted(new)) + "\n", content_type="text/plain",
                            if_generation_match=blob.generation)
    logger.info("Universe refresh: uploaded %d tickers (backup %s)", len(new), backup_name)
    summary["uploaded"] = True
    summary["backup"] = backup_name
    return summary
