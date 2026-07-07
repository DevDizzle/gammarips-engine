"""Pool-liquidity interval snapshot (MCP Priority-1A, 2026-07-07).

Every ~10 minutes during regular trading hours (plus one pre-open pass), a
Cloud Scheduler job POSTs /refresh_pool_liquidity on this service. The handler
re-fetches the Polygon option snapshot for EVERY contract in the current
enriched pool (scan_date = previous trading day) and appends one row per
contract to `profit_scout.pool_liquidity_snapshot`, keyed (contract, as_of).

This is the same upstream fetch the ~09:45 ET live-OI floor already makes
(see _fetch_live_oi in main.py) — extended from OI-only to the full liquidity
read (OI, session volume, last trade, day OHLC, IV/greeks, underlying price)
and persisted so the MCP's `get_contract_snapshot` / `get_pool_liquidity`
tools can serve a whole shortlist from ONE cached read instead of N upstream
fetches at the busiest minute of the day.

LEAKAGE WALL (read this before touching anything):
  * Everything this module fetches is ENTRY-DAY-LIVE (the 10:00+ tape). It is
    TELEMETRY, keyed by an explicit `as_of` timestamp — it must NEVER be
    joined into `overnight_signals_enriched`, `enriched_features_v1`, or any
    as-of <= scan_date feature surface, and it must never reach the
    tournament/judge selection path. This module is called ONLY from its own
    /refresh_pool_liquidity endpoint; run_notifier() does not import it.
  * The selection path keeps its own C1-walled fetch (_fetch_live_oi extracts
    OI+volume only). Do not "deduplicate" the two fetches — the wall is the
    point.

Quote fields (bid/ask/mid/spread_pct) exist in the table schema but are
written NULL: the current Polygon plan serves NO options quotes
(docs/DECISIONS/2026-06-05-engine-quote-outage-and-gate.md). They are
placeholders for the RM-001b quote-feed purchase; the MCP omits them from
responses while NULL. Populate _quote_fields() if/when the feed lands.

Write path: `insert_rows_json` against a pre-created table with an EXPLICIT
schema (scripts/ledger_and_tracking/create_pool_liquidity_snapshot.py). No
load jobs, no autodetect — see the 2026-07-02 enrichment outage.
"""

import logging
import os
import time as _time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import requests
from google.cloud import bigquery

logger = logging.getLogger(__name__)

_ET = ZoneInfo("America/New_York")

PROJECT_ID = "profitscout-fida8"
TABLE_ID = f"{PROJECT_ID}.profit_scout.pool_liquidity_snapshot"

FETCH_TIMEOUT_S = int(os.environ.get("POOL_LIQ_FETCH_TIMEOUT_S", "8"))
MAX_WORKERS = int(os.environ.get("POOL_LIQ_MAX_WORKERS", "16"))
# Spam guard: refuse to run again within this many seconds of the last
# successful run (max-instances=1 makes a module global effective). The cron
# cadence is 600s; 120s leaves room for a manual force-run without letting an
# unauthenticated caller spin the Polygon meter.
MIN_INTERVAL_S = int(os.environ.get("POOL_LIQ_MIN_INTERVAL_S", "120"))

# Honest provenance: this Polygon plan serves delayed (15-min) options data
# and no NBBO quotes. If the data plan changes, update both constants AND the
# decision note.
SOURCE_LABEL = "polygon option snapshot (delayed plan; no NBBO quotes)"
IS_DELAYED = True

_last_run_monotonic: float | None = None


def _ns_to_iso(ns) -> str | None:
    """Polygon sip/last_updated nanoseconds -> ISO8601 UTC (BQ TIMESTAMP-safe)."""
    if not ns:
        return None
    try:
        return datetime.fromtimestamp(int(ns) / 1e9, tz=UTC).isoformat()
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def _f(v) -> float | None:
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _i(v) -> int | None:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _get_json(url: str, api_key: str, timeout: int = FETCH_TIMEOUT_S) -> dict | None:
    """One GET, bearer-header key (never in the URL — requests exceptions embed
    the full URL), fail-soft to None."""
    try:
        resp = requests.get(
            url, headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout
        )
        if resp.status_code != 200:
            logger.warning(f"pool-liq GET {url.split('?')[0]} HTTP {resp.status_code}")
            return None
        body = resp.json()
        return body if isinstance(body, dict) else None
    except Exception as e:  # noqa: BLE001
        logger.warning(f"pool-liq GET failed: {e}")
        return None


def _fetch_underlying_price(ticker: str, api_key: str) -> tuple[float | None, str | None]:
    """Best available underlying price on this plan, honestly labeled.

    Chain: today's developing daily agg close (delayed ~15min) -> previous
    close. Callers first try the option snapshot's own underlying_asset.price
    (free, sometimes present) before paying these calls.
    """
    # ET date, not UTC — an evening force-run after 20:00 ET would otherwise
    # query tomorrow's (empty) agg and silently degrade to prev_close.
    today = datetime.now(_ET).date().isoformat()
    body = _get_json(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{today}/{today}",
        api_key,
    )
    results = (body or {}).get("results") or []
    if results and results[0].get("c") is not None:
        px = _f(results[0].get("c"))
        if px:
            return px, "day_agg_delayed"
    body = _get_json(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev", api_key)
    results = (body or {}).get("results") or []
    if results and results[0].get("c") is not None:
        px = _f(results[0].get("c"))
        if px:
            return px, "prev_close"
    return None, None


def _fetch_contract_row(
    underlying: str, contract: str, api_key: str
) -> dict:
    """Full liquidity snapshot for one contract -> a pool_liquidity_snapshot
    row dict (without the batch keys as_of/scan_date/is_preopen, added by the
    caller). Never raises. fetch_status: ok | polygon_empty | polygon_error."""
    row: dict = {
        "contract": contract,
        "underlying": underlying,
        "fetch_status": "polygon_error",
        "source": SOURCE_LABEL,
        "is_delayed": IS_DELAYED,
    }
    body = _get_json(
        f"https://api.polygon.io/v3/snapshot/options/{underlying}/{contract}", api_key
    )
    if body is None:
        return row
    res = body.get("results")
    if not isinstance(res, dict) or not res:
        row["fetch_status"] = "polygon_empty"
        return row

    day = res.get("day") if isinstance(res.get("day"), dict) else {}
    lt = res.get("last_trade") if isinstance(res.get("last_trade"), dict) else {}
    greeks = res.get("greeks") if isinstance(res.get("greeks"), dict) else {}

    row.update(
        {
            "fetch_status": "ok",
            "open_interest": _i(res.get("open_interest")),
            "day_volume": _i(day.get("volume")),
            "last_trade_price": _f(lt.get("price")),
            "last_trade_ts": _ns_to_iso(lt.get("sip_timestamp")),
            "day_open": _f(day.get("open")),
            "day_high": _f(day.get("high")),
            "day_low": _f(day.get("low")),
            "day_close": _f(day.get("close")),
            "day_last_updated": _ns_to_iso(day.get("last_updated")),
            "implied_volatility": _f(res.get("implied_volatility")),
            "delta": _f(greeks.get("delta")),
            "gamma": _f(greeks.get("gamma")),
            "theta": _f(greeks.get("theta")),
            "vega": _f(greeks.get("vega")),
            # RM-001b placeholders — stay NULL until the quote-feed purchase.
            "bid": None,
            "ask": None,
            "mid": None,
            "spread_pct": None,
        }
    )
    und_px = _f((res.get("underlying_asset") or {}).get("price"))
    if und_px:
        row["underlying_price"] = und_px
        row["underlying_price_source"] = "option_snapshot"
    return row


def _fetch_pool_contracts(scan_date: date) -> list[tuple[str, str]]:
    """(ticker, recommended_contract) for every enriched-pool row on scan_date."""
    client = bigquery.Client(project=PROJECT_ID)
    q = f"""
    SELECT DISTINCT ticker, recommended_contract
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = @sd AND recommended_contract IS NOT NULL
    """
    job = client.query(
        q,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("sd", "DATE", scan_date)]
        ),
    )
    return [(str(r.ticker), str(r.recommended_contract)) for r in job.result()]


def refresh(scan_date: date, is_preopen: bool, force: bool = False) -> dict:
    """Fetch + persist one liquidity snapshot pass over the scan_date pool.

    Returns a summary dict (never raises): {status, scan_date, as_of,
    contracts, ok, empty, error, inserted}.
    """
    global _last_run_monotonic
    now_mono = _time.monotonic()
    if (
        not force
        and _last_run_monotonic is not None
        and now_mono - _last_run_monotonic < MIN_INTERVAL_S
    ):
        return {
            "status": "skipped",
            "reason": f"ran {int(now_mono - _last_run_monotonic)}s ago (< {MIN_INTERVAL_S}s)",
        }

    api_key = (os.environ.get("POLYGON_API_KEY") or "").strip()
    if not api_key:
        logger.error("POLYGON_API_KEY not set; pool-liquidity refresh cannot run.")
        return {"status": "error", "reason": "POLYGON_API_KEY not set"}

    try:
        pool = _fetch_pool_contracts(scan_date)
    except Exception as e:  # noqa: BLE001
        logger.error(f"pool-liquidity: pool query failed: {e}")
        return {"status": "error", "reason": f"pool query failed: {e}"}
    if not pool:
        return {"status": "skipped", "reason": f"no enriched pool for scan_date={scan_date}"}

    as_of = datetime.now(UTC)
    as_of_iso = as_of.isoformat()

    rows: list[dict] = []
    workers = max(1, min(MAX_WORKERS, len(pool)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {
            ex.submit(_fetch_contract_row, u, c, api_key): (u, c) for (u, c) in pool
        }
        for fut in as_completed(futs):
            u, c = futs[fut]
            try:
                rows.append(fut.result())
            except Exception as e:  # noqa: BLE001
                logger.warning(f"pool-liquidity future raised for {c}: {e}")
                rows.append(
                    {
                        "contract": c,
                        "underlying": u,
                        "fetch_status": "polygon_error",
                        "source": SOURCE_LABEL,
                        "is_delayed": IS_DELAYED,
                    }
                )

    # Underlying-price fallback, ONE fetch per unique underlying that the
    # option snapshot didn't price (TF-18: live moneyness needs this).
    need_px = sorted({r["underlying"] for r in rows if not r.get("underlying_price")})
    px_memo: dict[str, tuple[float | None, str | None]] = {}
    if need_px:
        with ThreadPoolExecutor(max_workers=max(1, min(MAX_WORKERS, len(need_px)))) as ex:
            futs = {
                ex.submit(_fetch_underlying_price, t, api_key): t for t in need_px
            }
            for fut in as_completed(futs):
                t = futs[fut]
                try:
                    px_memo[t] = fut.result()
                except Exception:  # noqa: BLE001
                    px_memo[t] = (None, None)
        for r in rows:
            if not r.get("underlying_price"):
                px, src = px_memo.get(r["underlying"], (None, None))
                if px:
                    r["underlying_price"] = px
                    r["underlying_price_source"] = src

    for r in rows:
        r["as_of"] = as_of_iso
        r["scan_date"] = scan_date.isoformat()
        r["is_preopen"] = is_preopen

    n_ok = sum(1 for r in rows if r["fetch_status"] == "ok")
    n_empty = sum(1 for r in rows if r["fetch_status"] == "polygon_empty")
    n_err = len(rows) - n_ok - n_empty

    try:
        client = bigquery.Client(project=PROJECT_ID)
        errors = client.insert_rows_json(TABLE_ID, rows)
        if errors:
            logger.error(f"pool-liquidity insert errors (first 3): {errors[:3]}")
            return {
                "status": "error",
                "reason": f"BQ insert errors on {len(errors)} rows",
                "scan_date": scan_date.isoformat(),
            }
    except Exception as e:  # noqa: BLE001
        logger.error(f"pool-liquidity BQ insert failed: {e}")
        return {"status": "error", "reason": f"BQ insert failed: {e}"}

    _last_run_monotonic = now_mono
    logger.info(
        f"pool-liquidity: wrote {len(rows)} rows (ok={n_ok} empty={n_empty} "
        f"err={n_err}) scan_date={scan_date} as_of={as_of_iso} preopen={is_preopen}"
    )
    return {
        "status": "success",
        "scan_date": scan_date.isoformat(),
        "as_of": as_of_iso,
        "contracts": len(rows),
        "ok": n_ok,
        "empty": n_empty,
        "error": n_err,
        "inserted": len(rows),
    }
