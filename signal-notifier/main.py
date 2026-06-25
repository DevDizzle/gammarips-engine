"""Signal Notifier — bracket tournament (canonical 2026-06-04, was V5.4 ranker).

Reads `overnight_signals_enriched`, builds the FULL candidate pool (selection
gates removed 2026-06-04), calls the signal-judge bracket tournament to pick one
ticker, and sends ONE email with that pick to operator + paid subscribers (same
content). On any judge error (timeout, 5xx, out-of-set), fails CLOSED — no email.

What the STRICT path filters (2026-06-04 bracket-tournament):
  - SAFETY rails ONLY in the SELECT: a tradeable contract must exist
        (recommended_strike / recommended_expiration NOT NULL) and regime data
        must be present (vix3m_at_enrich NOT NULL).
  - ``VIX <= VIX3M`` (no backwardation) — checked downstream before the judge.
        Fail-closed: a NULL vix3m_at_enrich or a missing current VIX means we
        skip the email for the day entirely.
  - Earnings-overlap exclusion (see below) — the last hard filter.

  INTENTIONALLY NOT GATED on the strict path: moneyness, OI, vol, DTE,
  volume_oi_ratio, active-days. The tournament ranges across the full pool and
  weighs these features itself (they are all in the SELECT). ``spread <= 8%``
  still runs UPSTREAM in enrichment-trigger; the V/OI gate was removed 2026-06-02
  and the rest were removed 2026-06-04. The FALLBACK path (bypasses the
  tournament, takes df.iloc[0]) re-applies a moneyness band as its only bound.
  See DECISIONS/2026-06-04-bracket-tournament.md.

  - **Earnings-overlap exclusion** (added 2026-05-06): exclude any ticker
    whose scheduled earnings date falls inside ``[scan_date, exit_day]``
    where ``exit_day = entry_day + 2 trading days``. Window includes
    scan_date so AMC-scan_date prints (signal generated under known-imminent
    earnings positioning) are caught alongside BMO-entry_day (the CDW case)
    and any in-hold-window report. Literature-anchored (De Silva/Smith/So
    2026 RoF; Cao/Han 2013 JFE) — retail loses 5-9% per earnings event on
    long single-leg through the print. Fail-closed on calendar fetch failure.
    See docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md.

The picker (2026-06-04 tournament_v1): a randomized bracket tournament over the
full enriched pool — 3 independent brackets, batches of ≤10, top-2 advance,
3-run consensus selects the pick (3/3=high, 2/3=medium, 1/3=low). Dead-simple
prompt + the daily report + per-contract JSON; no memory, no rubric, no weights.
This replaced the V5.4 Scorer→Picker pair / judge_v6. Hosted at signal-judge
Cloud Run service. signal-judge uptime is the SLO — no SQL fallback. See
docs/DECISIONS/2026-06-04-bracket-tournament.md.

Trader execution mechanics (forward-paper-trader, separate service): entry
10:00 ET day-1, stop -60%, target +80%, 3-day hold, exit 15:50 ET day-3.
Unchanged across V5.3 → V5.4 → tournament — only the picker has changed.
"""

import logging
import os
import time
from datetime import date, datetime, timedelta

import pandas as pd
import pandas_market_calendars as mcal
import pytz
import requests
from flask import Flask, jsonify, request
from google.cloud import bigquery, firestore
from pandas.tseries.offsets import BDay

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", "").strip()
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "").strip()
MAILGUN_SENDER = f"GammaRips Engine <mailgun@{MAILGUN_DOMAIN}>"
RECIPIENT_EMAIL = "eraphaelparra@gmail.com"

# Earnings-overlap exclusion (2026-05-06). FMP earning_calendar is the only
# call this service makes to FMP; mounted via deploy.sh as a Secret Manager
# binding. Missing key fails closed (no email).
FMP_API_KEY = os.environ.get("FMP_API_KEY", "").strip()

# Active-days liquidity gate (2026-05-19). Polygon daily aggs on the
# recommended_contract are used to compute active_days_20d transiently per
# finalist. Missing key -> compute_active_days_20d returns ("polygon_error")
# -> caller fails closed per-candidate. See:
#   docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "").strip()

# Live cohort starts 2026-05-13 — the first actual V5.4 fill (OKTA scan
# 2026-05-12 → entry 2026-05-13). V5.4 was *promoted* 2026-05-08 but the
# V5.4-only trader code didn't land until 2026-05-15 and the first row it
# wrote was OKTA with entry_timestamp=2026-05-13. Anchoring the public cohort
# to the policy-promotion date (5/8) over-states the cohort age and creates
# the impression that fewer trades have fired than expected. Anchored instead
# to the first executed trade so the "cohort age" displayed publicly matches
# the trade record. See:
#   docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md
#   docs/DECISIONS/2026-05-19-cohort-start-and-position-sizing.md
LIVE_COHORT_START_DATE = "2026-06-23"  # V7.1 Tilted GIGO cohort: first ENTRY is the first momentum-tilt-enriched pick (scan 06-22 -> entry 06-23). Ledger TRUNCATED 2026-06-22; the prior V7_INTRADAY cohort + the 06-22 TTWO pick (pre-tilt, enriched before the 06-19 tilt deploy) are EXCLUDED by this floor. See docs/DECISIONS/2026-06-22-v7-1-tilted-gigo-cohort-reset.md.

# Fixed-dollar position sizing for the public cohort_stats panel.
# The ledger records actual per-contract premium + percent return; the public
# display layer applies a normalized $500/trade position size so the cohort
# ROI is comparable across trades regardless of contract premium. Without
# this, a 1-contract $0.40 option winning +80% (HTZ on 2026-05-19) shows
# only ~$32 P&L next to a 1-contract $4.67 option losing -2% (OKTA on
# 2026-05-13) at $9 — the dollar-weighted ROI under-represents wins on
# low-premium contracts. n_contracts = max(1, ROUND($500 / (entry_price*100))).
# See docs/DECISIONS/2026-05-19-cohort-start-and-position-sizing.md.
POSITION_SIZE_USD = 500.0

# Public webapp base — used to build deep-links for emails / WhatsApp.
# Pinned here so the email surface never accidentally points at a staging
# host. Update in lockstep if the user-facing domain ever changes.
PUBLIC_WEBAPP_BASE = "https://gammarips.com"

# OpenClaw — non-blocking WhatsApp push. Activates the moment all three
# env vars are present. If any are missing the post is skipped silently.
OPENCLAW_GATEWAY_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "").strip()
OPENCLAW_HOOKS_TOKEN = os.environ.get("OPENCLAW_HOOKS_TOKEN", "").strip()
OPENCLAW_GROUP_JID = os.environ.get("OPENCLAW_GROUP_JID", "").strip()

# V5.4 signal-judge — sole live picker (promoted 2026-05-08). If the env var
# is missing or the call fails for any reason, this service fails closed: no
# pick is published, no email is sent, no `todays_pick` doc is written with
# `has_pick=True`. There is no V5.3 fallback path.
SIGNAL_JUDGE_URL = os.environ.get("SIGNAL_JUDGE_URL", "").strip().rstrip("/")

nyse = mcal.get_calendar("NYSE")
est = pytz.timezone("America/New_York")

# V5.3 filter thresholds — canonical in CHEAT-SHEET.md
VOL_OI_MIN = 2.0
MONEYNESS_MIN = 0.05
# MONEYNESS_MAX history:
#   0.15 -> 0.10 on 2026-05-06 (H12 lit-audit; Aretz 2023 / Augustin 2022 deep-OTM cliff).
#   0.10 -> 0.13 on 2026-06-02 (owner-directed; see DECISIONS/2026-06-02-moneyness-cap-widen-to-13).
# Mechanism correction: the Aretz/Augustin deep-OTM EV cliff is a HOLD-TO-EXPIRY
# phenomenon (VRP/theta bled over the option's life). We hold MAX 3 days on a
# +80/-60 bracket of a 7-45 DTE option conditioned on directional UOA flow —
# theta is negligible over 3 days and we never ride to expiry, so that literature
# is about a different trade. Realized-option-PnL backtest (N=1,375 fills,
# backtesting_and_research/moneyness_band_study.py) showed the 10-13% increment
# at +8.9% mean (90% CI [+0.014,+0.163], flat cost) while the toxic (0.14,0.15]
# bin was -15% (excluded). STRICT path only — the FALLBACK cap stays pinned at
# 0.10 (see below). Thin/single-regime evidence; reversible — revert to 0.10 if
# the 10-13% pick cohort underperforms on the live ledger.
MONEYNESS_MAX = 0.13
# Contract OI/vol selection floors (OI_MIN=10 / VOL_MIN=50) were REMOVED with
# the 2026-06-04 bracket-tournament — scan-time OI/vol is a one-day-stale
# snapshot and the sweep that earns the score only becomes OI the next morning,
# after our 10:00 entry. The tournament now weighs liquidity rather than
# pre-filtering on it. Underlying liquidity is still enforced upstream by
# enrichment-trigger (directional UOA > $500K). See
# docs/DECISIONS/2026-06-04-bracket-tournament.md.

# DTE band added 2026-05-11 (7-30 originally). Anchored to scorer_v4.md:18 /
# picker_v3.md:69: short-DTE is the structural sweet spot for the +80%/3-day
# bracket — short enough for gamma to dominate theta, long enough to survive
# a flat session. 40+ DTE contracts (like the 2026-05-11 VAL incident) have
# too little gamma to print +80% on a 3-day move and should never reach the
# ranker.
#
# Upper bound widened 30 -> 45 on 2026-05-12 (Scenario C, picker starvation
# fix; see docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md). Gamma is
# still meaningfully positive at 31-45 DTE on near-the-money strikes (delta
# 0.45-0.55 inside the 5-10% moneyness band); the original 30-day cap was a
# defensive default, not literature-backed. Projected funnel impact (22-day
# sample): median candidates 1 -> 2; % days with >=3 candidates 22.7% ->
# 50%. Tighten back to 30 if research shows EV at 31-45 DTE materially
# underperforms 7-30 DTE on N>=15 V5.4 closes.
DTE_MIN = 7
DTE_MAX = 45

# Active-days liquidity gate (added 2026-05-19, ACTIVE_DAYS_MIN=5) was REMOVED
# with the 2026-06-04 bracket-tournament — same rationale as the OI/vol floors
# (scan-time liquidity is a stale snapshot; the tournament weighs it instead of
# pre-filtering). compute_active_days_20d() is retained for reference/audit but
# is no longer called. See docs/DECISIONS/2026-06-04-bracket-tournament.md.

# Daily-cadence fallback (2026-06-01, see
# docs/DECISIONS/2026-06-01-daily-cadence-fallback.md). The fallback fires when
# the strict pool is empty (rare post-2026-06-04, since the strict path is now
# ungated). It BYPASSES the tournament and takes df.iloc[0] directly, so it is
# the one path that still applies a moneyness band — the band is the only thing
# keeping the bypassed pick from being deep-ITM/deep-OTM. The fallback band is
# interpolated into the SELECT (see _build_candidate_query, fallback=True):
# floor relaxed to ATM, cap pinned at FALLBACK_MONEYNESS_MAX. Fallback picks are
# tagged policy_gate="FALLBACK" end-to-end so their EV is measurable separately
# from STRICT picks and the fallback can be killed with data if it loses.
FALLBACK_MONEYNESS_MIN = 0.0   # ATM allowed (strict floor 0.05); ITM still excluded
# Pinned at 0.10 (NOT coupled to MONEYNESS_MAX). The fallback fires only on
# zero-strict-candidate days — the worst place for deeper-OTM names — so it stays
# tight even though the strict tournament ranges across the full moneyness pool.
FALLBACK_MONEYNESS_MAX = 0.10   # pinned; no deep-OTM on bypassed fallback picks
POLICY_GATE_STRICT = "STRICT"
POLICY_GATE_FALLBACK = "FALLBACK"

# Edge-rank pool cap (2026-06-11, see docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md).
# The 2026-06-04 tournament runs over the FULL enriched pool (~94 signals/day),
# costing ~39 model calls/pick (3 brackets x ~13). That is not affordable. We now
# DETERMINISTICALLY pre-rank the strict pool by the 4 levers the 1,375-trade
# realized-option-PnL study proved separate winners from losers, and feed only the
# top TOURNEY_POOL_CAP into the tournament. At cap=12 the bracket collapses to
# ~3 calls/bracket -> ~9 calls/pick (~77% fewer); set cap=10 for a single-batch
# ~92% cut. This is a SOFT cap, NOT a gate: a strong bearish/high-RR name can still
# rank into the top-K and reach the LLM — we are not categorically banning any
# direction (bearish -7.7% is regime-conditional; see the decision note). Every
# input (direction, recommended_delta, risk_reward_ratio, atr_normalized_move) is
# point-in-time at scan_date — leakage-safe, unlike the stale-OI gates retired
# 2026-06-04. FALLBACK is unaffected (it bypasses the tournament via df.iloc[0]).
TOURNEY_POOL_CAP = int(os.environ.get("TOURNEY_POOL_CAP", "12"))
# BULLISH-only hard gate (2026-06-11, owner-directed). The edge levers below are
# defined on CALL deltas (|delta| 0.35-0.46 band, advertised RR) — bearish puts
# carry the opposite delta sign and a different contract structure, so the lever
# does NOT transfer. We are NOT chasing a regime call here; we are restricting to
# the trade family the edge actually describes. This OVERRIDES the soft-cap regime
# caveat (bearish -7.7% is regime-conditional) by explicit owner decision. Env
# toggle so re-enabling bearish later is a config flip, not a code change.
BULLISH_ONLY = os.environ.get("BULLISH_ONLY", "true").strip().lower() in ("1", "true", "yes")
# Tradeable delta band from the funnel study: |delta| 0.20-0.46. The real lever is
# the UPPER bound (exclude deep-ITM 0.46+, which collapses to +0.1%); the far-OTM
# lottery floor is already handled by RR<1.4, so the lower bound is a loose 0.20
# (a 0.35 floor was too tight — it gave zero delta-credit to good 0.20-0.35 names).
# Confirmed Q19 delta-as-trap-escape lever.
EDGE_DELTA_LO = 0.20
EDGE_DELTA_HI = 0.46
# Advertised risk/reward: RR < 1.4 -> +2-3%; the high-RR (far-OTM lottery) bucket
# is the single worst thing in the data (-7.7%). Penalize, don't ban.
EDGE_RR_MAX = 1.4

# Live-OI liquidity floor (2026-06-25, see
# docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md). At ~09:45 ET pick time we
# re-fetch LIVE open interest per candidate from Polygon's option snapshot and drop
# contracts whose live OI is below OI_FLOOR. The tournament kept selecting dead
# contracts (e.g. BBWI live OI ~617, today-vol 2) because the enriched row carries
# a one-day-stale scan-time OI snapshot. The threshold is set on FILL-RATE
# tradeability (an ~OI=200 fill-rate cliff in the backtest), NOT on PnL — thin
# contracts show a spurious "0% PnL" stale-print artifact, so PnL can't set the
# floor. This explicitly REVERSES the 2026-06-04 OI-strip (which removed the
# STALE scan-time OI from the judge); re-introducing OI is safe here because it is
# (a) FRESH (re-fetched at pick time, not the scan snapshot) and (b) OI-ONLY —
# every other live snapshot field (IV, greeks, day OHLC, last trade/quote) is
# DISCARDED immediately after the fetch (entry-day-live leakage, the 10:00+ window).
#   * OI_FLOOR: contracts with live_oi < OI_FLOOR are dropped (200 = fill cliff).
#   * TOURNEY_MIN: fail-soft floor — if fewer than this survive, keep the top
#     live_oi names up to TOURNEY_MIN so the tournament never starves to zero.
#   * LIQUIDITY_TILT: kill switch (same shape as enrichment-trigger MOMENTUM_TILT).
#     When false, behavior is bit-identical to today (no re-fetch, no drop, no tilt).
OI_FLOOR = int(os.environ.get("OI_FLOOR", "200"))
TOURNEY_MIN = int(os.environ.get("TOURNEY_MIN", "8"))
LIQUIDITY_TILT = os.environ.get("LIQUIDITY_TILT", "true").strip().lower() in ("1", "true", "yes")

# Per-candidate Polygon option-snapshot timeout (seconds). Matches the
# compute_active_days_20d single-attempt / 8s fail-soft pattern. The whole
# re-fetch is parallelized across a ThreadPoolExecutor, so worst-case
# wall-clock is ~one timeout (not 50 * 8s) — see _refresh_live_oi_batch.
LIVE_OI_FETCH_TIMEOUT_S = int(os.environ.get("LIVE_OI_FETCH_TIMEOUT_S", "8"))
LIVE_OI_MAX_WORKERS = int(os.environ.get("LIVE_OI_MAX_WORKERS", "16"))

# Entry-day-live snapshot fields that MUST NEVER reach the /rank payload (C1/C3
# leakage guard, 2026-06-25). The Polygon option snapshot returns IV, greeks, day
# OHLC, last trade and last quote alongside open_interest — all of those reflect
# the LIVE entry-day (10:00+) tape and would leak the future. Only live_oi is
# extracted and surfaced; everything here is discarded at fetch time and asserted
# absent again just before the payload is built.
_FORBIDDEN_LIVE_KEYS = {
    "live_iv", "live_delta", "live_gamma", "live_theta", "live_vega",
    "last_trade", "last_trade_price", "last_quote",
    "day_close", "day_open", "day_high", "day_low", "day_vwap",
}

# V5.3 execution knobs — must mirror forward-paper-trader/main.py.
# Displayed in the operator email so the routine matches what the simulator
# actually models. If these diverge from the trader, update both.
STOP_PCT_DISPLAY = 0.60   # -60% on option premium
TARGET_PCT_DISPLAY = 0.80  # +80% on option premium


def get_previous_trading_day(base_date: date) -> date:
    start_date = base_date - timedelta(days=10)
    schedule = nyse.schedule(start_date=start_date, end_date=base_date)
    valid_dates = [d.date() for d in schedule.index if d.date() < base_date]
    return valid_dates[-1] if valid_dates else None


def is_trading_day(d: date) -> bool:
    """True if `d` is an NYSE trading session (handles weekends + holidays)."""
    schedule = nyse.schedule(start_date=d, end_date=d)
    return len(schedule.index) > 0


def get_next_trading_day(base_date: date) -> date:
    schedule = nyse.schedule(start_date=base_date, end_date=base_date + timedelta(days=10))
    valid_dates = [d.date() for d in schedule.index if d.date() > base_date]
    return valid_dates[0] if valid_dates else base_date + timedelta(days=1)


def get_hold_window_end(entry_day: date) -> date:
    """Return ``entry_day + 2 trading days`` — the V5.3 exit_day (15:50 ET).

    The earnings-overlap exclusion uses ``[entry_day, get_hold_window_end(entry_day)]``
    inclusive as the window any reporting ticker must NOT touch. V5.3 holds
    through entry_day, entry+1, exits 15:50 ET on entry+2.
    """
    schedule = nyse.schedule(start_date=entry_day, end_date=entry_day + timedelta(days=20))
    valid_dates = [d.date() for d in schedule.index if d.date() > entry_day]
    if len(valid_dates) >= 2:
        return valid_dates[1]
    return entry_day + timedelta(days=4)


def fetch_earnings_calendar(start_date: date, end_date: date) -> set[str] | None:
    """Return uppercase tickers with scheduled earnings in ``[start_date, end_date]``.

    Source: FMP ``/stable/earnings-calendar``. Returns None on any failure —
    callers MUST fail-closed (skip the day) because we cannot tell "no earnings"
    apart from "calendar unreachable." The no-long-options-through-earnings rule
    is hard (literature-settled, see DECISIONS/2026-05-06-earnings-overlap-exclusion).

    Note: the legacy ``/api/v3/earning_calendar`` endpoint was retired on
    2025-08-31 and now returns 403 for all keys. ``/stable/earnings-calendar``
    is the current path; same key, same ``from``/``to`` params, same
    ``{symbol, date, ...}`` response shape.
    """
    if not FMP_API_KEY:
        logger.error("FMP_API_KEY not set; cannot check earnings calendar.")
        return None
    try:
        url = "https://financialmodelingprep.com/stable/earnings-calendar"
        # apikey goes in the header, not the query string — the URL ends up in
        # error logs verbatim, and a query-param key leaks the secret on every
        # 4xx/5xx (FMP confirmed 2026-05-07: header auth is supported on /stable).
        params = {
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        }
        resp = requests.get(
            url, params=params, headers={"apikey": FMP_API_KEY}, timeout=15
        )
        resp.raise_for_status()
        events = resp.json()
        # FMP free-tier quota-exhausted returns HTTP 200 with a dict body like
        # {"Error Message": "Limit Reach..."}. We must NOT silently treat that
        # as "zero earnings reporting" — that's a fail-OPEN that lets earnings-
        # overlap trades through. A list payload is the only valid happy path;
        # anything else fails closed.
        if not isinstance(events, list):
            logger.error(
                f"FMP returned non-list payload (likely quota or auth error): "
                f"{str(events)[:200]}"
            )
            return None
        tickers = {
            str(e.get("symbol", "")).upper()
            for e in events
            if isinstance(e, dict) and e.get("symbol")
        }
        logger.info(
            f"Earnings calendar [{start_date} -> {end_date}]: "
            f"{len(tickers)} tickers reporting."
        )
        return tickers
    except Exception as e:
        logger.error(f"Earnings calendar fetch failed: {e}")
        return None


def compute_active_days_20d(
    recommended_contract: str, scan_date: date
) -> tuple[int | None, str]:
    """Count trading days with vol>0 over the 20 sessions preceding scan_date.

    Returns ``(active_days_20d, status)`` where ``status`` is one of:
      * ``"ok"`` — Polygon returned a valid (possibly empty) ``results`` list
        AND we were able to compute a count. Returned int is in [0, 20].
      * ``"polygon_empty"`` — Polygon returned 200 with ``results=[]`` or
        ``resultsCount=0``. Treated as "contract never printed in the
        window" — count is None, caller MUST fail closed.
      * ``"polygon_error"`` — any other failure (missing key, exception,
        timeout, non-200, malformed JSON). Count is None, caller MUST fail
        closed.

    Single attempt — the caller handles fail-closed; retries belong in the
    Polygon session, not here. 8s timeout. See decision doc for threshold
    rationale and backtest:
      docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md
    """
    if not POLYGON_API_KEY:
        logger.error(
            "POLYGON_API_KEY not set; cannot compute active_days_20d for "
            f"{recommended_contract}"
        )
        return None, "polygon_error"

    # 35 calendar days back from scan_date is enough to span 20 trading days
    # even across long weekends / holidays. End at scan_date - 1 calendar day
    # so we never accidentally include scan_date itself.
    start_d = scan_date - timedelta(days=35)
    end_d = scan_date - timedelta(days=1)
    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{recommended_contract}"
        f"/range/1/day/{start_d.isoformat()}/{end_d.isoformat()}"
        f"?adjusted=true&sort=asc&limit=120&apiKey={POLYGON_API_KEY}"
    )

    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            logger.warning(
                f"Polygon daily aggs {recommended_contract} HTTP "
                f"{resp.status_code}: {resp.text[:200]}"
            )
            return None, "polygon_error"
        body = resp.json()
    except Exception as e:
        logger.warning(
            f"Polygon daily aggs {recommended_contract} fetch failed: {e}"
        )
        return None, "polygon_error"

    if not isinstance(body, dict):
        logger.warning(
            f"Polygon daily aggs {recommended_contract} non-dict body: "
            f"{str(body)[:200]}"
        )
        return None, "polygon_error"

    results = body.get("results") or []
    if not results:
        # Distinguish "never traded" from "API down" — same fail-closed
        # outcome, different skip reason in postmortem.
        return None, "polygon_empty"

    # Build the 20 most recent US business days strictly before scan_date.
    # BDay is the same primitive the researcher's backtest used; pandas
    # business-day arithmetic is good enough here (option markets follow NYSE
    # but the trailing 20-session count is robust to the rare federal holiday
    # mismatch — at worst we mis-bucket by 1 session, which doesn't move the
    # gate at threshold 5).
    sd_ts = pd.Timestamp(scan_date)
    sessions = pd.bdate_range(end=sd_ts - BDay(1), periods=20)
    session_dates = {ts.date() for ts in sessions}

    # Map Polygon results to {date: volume}. `t` is ms epoch at bar start (UTC).
    # Polygon returns at most one bar per US trading day; we treat each bar's
    # UTC date as its trading-day index.
    by_date: dict[date, int] = {}
    for bar in results:
        t_ms = bar.get("t")
        if t_ms is None:
            continue
        v = bar.get("v", 0) or 0
        try:
            d = datetime.utcfromtimestamp(t_ms / 1000.0).date()
        except (OverflowError, OSError, ValueError):
            continue
        if d >= scan_date:
            continue
        by_date[d] = int(v)

    # Zero-fill missing trading days, then count days with vol > 0.
    active = sum(1 for d in session_dates if by_date.get(d, 0) > 0)
    return active, "ok"


def write_todays_pick_doc(
    scan_date: date,
    has_pick: bool,
    top: pd.Series | None = None,
    vix_now: float | None = None,
    skip_reason: str | None = None,
    v5_4_meta: dict | None = None,
    policy_gate: str = "STRICT",
) -> None:
    """Canonical writer for Firestore ``todays_pick/{scan_date}``.

    This is the single source of truth for "what did GammaRips pick today"
    across all downstream surfaces (webapp banner, MCP get_todays_pick,
    x-poster signal post, gamma-bot, blog newsletter). All readers MUST read
    this doc without re-applying filters — that is the drift-prevention
    invariant.

    Schema pinned in docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md
    Phase 1.0; extended 2026-05-08 (V5.4 promotion) to carry the agent-ranker
    justification + confidence + run_id alongside the picked-ticker data.
    See docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md.

    Dual-write contract (Evan 2026-04-28): we write the doc under BOTH the
    scan_date key AND the entry_day key. Readers like x-poster fire on the
    entry day and look up "today's pick" — they don't know the scan_date.
    Writing under both keys keeps webapp/MCP backwards-compatible without
    forcing every reader to do calendar arithmetic.
    """
    db = firestore.Client(project=PROJECT_ID)
    doc_ref = db.collection("todays_pick").document(scan_date.isoformat())

    if not has_pick:
        doc_data = {
            "scan_date": scan_date.isoformat(),
            "decided_at": firestore.SERVER_TIMESTAMP,
            "effective_at": None,
            "has_pick": False,
            "skip_reason": skip_reason,
            "policy_version": "V7_1_TILTED_GIGO",
        }
    else:
        assert top is not None, "write_todays_pick_doc(has_pick=True) requires `top`"
        entry_day = get_next_trading_day(scan_date)
        entry_dt_et = est.localize(datetime.combine(entry_day, datetime.strptime("10:00", "%H:%M").time()))
        effective_at = entry_dt_et.astimezone(pytz.UTC)

        def _num(key: str) -> float | None:
            v = top.get(key)
            return float(v) if v is not None and not pd.isna(v) else None

        def _int(key: str) -> int | None:
            v = top.get(key)
            return int(v) if v is not None and not pd.isna(v) else None

        def _str(key: str) -> str | None:
            v = top.get(key)
            return str(v) if v is not None and not pd.isna(v) else None

        doc_data = {
            "scan_date": scan_date.isoformat(),
            "decided_at": firestore.SERVER_TIMESTAMP,
            "effective_at": effective_at.isoformat(),
            "has_pick": True,
            "skip_reason": None,
            "ticker": _str("ticker"),
            "direction": _str("direction"),
            "recommended_contract": _str("recommended_contract"),
            "recommended_strike": _num("recommended_strike"),
            "recommended_expiration": _str("recommended_expiration"),
            "recommended_mid_price": _num("recommended_mid_price"),
            "recommended_dte": _int("recommended_dte"),
            "overnight_score": _int("overnight_score") if "overnight_score" in top else None,
            # live_oi: fresh pick-time open interest (2026-06-25 liquidity floor).
            # Firestore is schemaless so this is C5-safe (it never touches the
            # forward_paper_ledger load job). None on liquidity-tilt-off / failed
            # refresh / FALLBACK days (the col only exists post-_liquidity_refresh).
            "live_oi": _int("live_oi") if "live_oi" in top else None,
            "vol_oi_ratio": _num("volume_oi_ratio"),
            "moneyness_pct": _num("moneyness_pct"),
            "call_dollar_volume": _num("call_dollar_volume"),
            "put_dollar_volume": _num("put_dollar_volume"),
            "vix3m_at_enrich": _num("vix3m_at_enrich"),
            "vix_now_at_decision": float(vix_now) if vix_now is not None else None,
            "vix_source": _LAST_VIX_SOURCE,
            "policy_version": "V7_1_TILTED_GIGO",
            # STRICT (ranker pick) or FALLBACK (daily-cadence deterministic
            # pick). Propagated to forward_paper_ledger.policy_gate so fallback
            # EV is separable. See DECISIONS/2026-06-01-daily-cadence-fallback.md.
            "policy_gate": policy_gate,
        }
        # V5.4 ranker provenance — present on every has_pick=True doc post-promotion.
        if v5_4_meta:
            doc_data.update({
                "v5_4_runner_up": v5_4_meta.get("runner_up"),
                "v5_4_justification": v5_4_meta.get("justification"),
                "v5_4_confidence": v5_4_meta.get("confidence"),
                "v5_4_run_id": v5_4_meta.get("run_id"),
                "v5_4_scorer_prompt_version": v5_4_meta.get("scorer_prompt_version"),
                "v5_4_picker_prompt_version": v5_4_meta.get("picker_prompt_version"),
                "v5_4_scorer_model": v5_4_meta.get("scorer_model"),
                "v5_4_picker_model": v5_4_meta.get("picker_model"),
            })

    doc_ref.set(doc_data)
    logger.info(
        f"Wrote todays_pick/{scan_date.isoformat()} has_pick={has_pick}"
        + (f" skip_reason={skip_reason}" if not has_pick else f" ticker={doc_data.get('ticker')}")
    )

    # Dual-write under entry_day so readers that fire on the entry day
    # (x-poster signal cron, etc.) can look up todays_pick/{today}.
    entry_day_iso = (
        get_next_trading_day(scan_date).isoformat()
        if has_pick or skip_reason is not None
        else None
    )
    if entry_day_iso and entry_day_iso != scan_date.isoformat():
        db.collection("todays_pick").document(entry_day_iso).set(doc_data)
        logger.info(f"Mirrored todays_pick/{entry_day_iso} (entry day)")


# VIX sanity + fallback-corroboration policy --------------------------------
VIX_PLAUSIBLE_MIN = 1.0     # below this is a parse/garbage artifact, not a real VIX
VIX_PLAUSIBLE_MAX = 200.0   # 2020's intraday peak was ~85; 200 is a generous garbage bound
# Source that produced the VIX used in the most recent fetch_vix_close call
# ("FRED" / "Stooq+Yahoo"). Read by write_todays_pick_doc so every pick is
# auditable to its regime-data source after logs age out. The notifier is a
# once-daily single-request job, so this module-global is safe.
_LAST_VIX_SOURCE = "unknown"


def _plausible_vix(v: float | None) -> float | None:
    """Return v only if it is in a sane VIX range, else None (garbage guard)."""
    if v is None:
        return None
    return v if VIX_PLAUSIBLE_MIN < v < VIX_PLAUSIBLE_MAX else None


def _vix_date_ok(d: date, scan_date: date) -> bool:
    """Accept a bar dated on/before scan_date AND strictly before today (ET).

    The second clause stops a live/partial CURRENT-session bar (which Stooq and
    Yahoo can carry intraday) from feeding the regime gate. In normal cron use
    scan_date is the prior trading day, so ``d <= scan_date`` already implies
    this; the guard only bites if fetch_vix_close is ever called with
    scan_date == today.
    """
    return d <= scan_date and d < datetime.now(est).date()


def _fetch_vix_from_stooq(scan_date: date) -> float | None:
    """Fallback VIX source: Stooq daily CSV (Date,Open,High,Low,Close,Volume)."""
    try:
        resp = requests.get(
            "https://stooq.com/q/d/l/?s=%5Evix&i=d",
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        best: tuple[date, float] | None = None
        for ln in resp.text.strip().splitlines()[1:]:
            parts = ln.split(",")
            if len(parts) < 6:  # real schema is 6 cols; a short/garbled row is not data
                continue
            try:
                d = datetime.strptime(parts[0].strip(), "%Y-%m-%d").date()
                v = _plausible_vix(float(parts[4].strip()))
            except ValueError:
                continue
            if v is not None and _vix_date_ok(d, scan_date) and (best is None or d > best[0]):
                best = (d, v)
        return best[1] if best else None
    except Exception as e:
        logger.warning(f"VIX Stooq fallback failed: {e}")
        return None


def _fetch_vix_from_yahoo(scan_date: date) -> float | None:
    """Fallback VIX source: Yahoo Finance ^VIX daily chart JSON."""
    try:
        resp = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=1mo",
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        result = resp.json()["chart"]["result"][0]
        ts = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]
        best: tuple[date, float] | None = None
        for t, c in zip(ts, closes):
            v = _plausible_vix(float(c)) if c is not None else None
            if v is None:
                continue
            d = datetime.utcfromtimestamp(t).date()
            if _vix_date_ok(d, scan_date) and (best is None or d > best[0]):
                best = (d, v)
        return best[1] if best else None
    except Exception as e:
        logger.warning(f"VIX Yahoo fallback failed: {e}")
        return None


def fetch_vix_close(scan_date: date) -> float | None:
    """Return the VIX close on or before ``scan_date``.

    Primary source FRED VIXCLS. On FRED failure, fall back to free public
    sources (Stooq, Yahoo) and use the best one that answers. The regime gate
    is one-sided (``vix_now > vix3m`` => skip), so when sources disagree we take
    the MAX: that's the conservative read (a low-biased source can't mask
    backwardation) and it works with a single source — we no longer wipe a whole
    FRED-outage day just because only one backup responded.
    Records the winning source in ``_LAST_VIX_SOURCE`` for pick provenance.
    """
    global _LAST_VIX_SOURCE
    # Bound the request with cosd (start date). Without it FRED serializes VIXCLS
    # back to 1990, and that full dump exceeds the 30s timeout every morning —
    # the chronic "FRED outage" of 2026-06-02..04 was this, not a real outage. A
    # 45-day window spans any holiday gap + FRED's publish lag at ~30 rows. We
    # still retry with linear backoff for genuine transient 504s.
    cosd = (scan_date - timedelta(days=45)).isoformat()
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd={cosd}"
    fred_val: float | None = None
    try:
        resp = None
        for attempt in range(1, 4):
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                break
            except Exception as e:
                logger.warning(f"VIX fetch attempt {attempt}/3 failed: {e}")
                if attempt < 3:
                    time.sleep(2 * attempt)
                else:
                    raise
        lines = resp.text.strip().splitlines()[1:]
        best: tuple[date, float] | None = None
        for ln in lines:
            parts = ln.split(",")
            if len(parts) < 2:
                continue
            dstr, vstr = parts[0].strip(), parts[1].strip()
            if not dstr or vstr in ("", "."):
                continue
            try:
                d = datetime.strptime(dstr, "%Y-%m-%d").date()
                v = _plausible_vix(float(vstr))
            except ValueError:
                continue
            if v is not None and _vix_date_ok(d, scan_date) and (best is None or d > best[0]):
                best = (d, v)
        fred_val = best[1] if best else None
    except Exception as e:
        logger.warning(f"VIX FRED fetch failed: {e}")

    if fred_val is not None:
        _LAST_VIX_SOURCE = "FRED"
        return fred_val

    # FRED down: use the best public source that answers. When sources differ
    # we take the MAX — the conservative read for a one-sided gate (a low-biased
    # source can't mask backwardation). A single source is enough.
    got = [(n, v) for n, v in (
        ("Stooq", _fetch_vix_from_stooq(scan_date)),
        ("Yahoo", _fetch_vix_from_yahoo(scan_date)),
    ) if v is not None]
    if not got:
        logger.warning("VIX: FRED down and no public fallback answered; fail-closed.")
        return None
    name, val = max(got, key=lambda nv: nv[1])
    _LAST_VIX_SOURCE = name
    logger.warning(
        f"VIX: FRED unavailable; using {name}={val:.2f} "
        f"(max of {', '.join(f'{n}={v:.2f}' for n, v in got)})."
    )
    return val


def claim_email_send(scan_date: date) -> bool:
    """Atomically claim the right to send the daily pick on TODAY (ET run-day).

    Cloud Scheduler retries the notifier on attempt-deadline overrun, and
    ``run_notifier`` routinely takes 3+ minutes (signal-judge cold start + the
    bracket tournament). Without a guard, a retry re-runs the whole pipeline and
    double-sends the email + WhatsApp + subscriber fan-out (observed 2026-06-11;
    see docs/DECISIONS/2026-06-11-notifier-duplicate-send-guard.md). This
    transactional claim makes the outbound send fire at most once per CALENDAR
    SEND-DAY no matter how many times the endpoint is triggered.

    KEY = the ET run-day, NOT ``scan_date``. The guard's job is "send at most
    once this morning" — keying on the wall-clock day dedups same-morning
    Scheduler retries (its only purpose; there is exactly one notifier run per
    morning) while NEVER colliding across days. Keying on scan_date was wrong:
    across a market holiday the SAME scan_date is the "previous trading day" for
    two consecutive mornings, so a claim written on the first morning silenced
    the legitimate send on the next (observed 2026-06-22 — Friday's Juneteenth
    pre-guard run claimed scan_date=2026-06-18, suppressing Monday's real send of
    the same scan_date). ``scan_date`` is retained in the doc body for audit.

    Returns True if THIS caller acquired the claim (proceed to send), False if a
    prior/concurrent run already claimed it (skip all outbound). Fail-OPEN: if
    Firestore raises we return True so a real outage never silences the signal —
    a rare duplicate is the lesser harm than a missed pick.

    OPERATOR: to force a deliberate resend, delete ``email_sends/{TODAY_ET}``
    (the send-day doc id), not ``email_sends/{scan_date}``.
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        run_day = datetime.now(est).date()
        claim_ref = db.collection("email_sends").document(run_day.isoformat())

        @firestore.transactional
        def _claim(txn) -> bool:
            snap = claim_ref.get(transaction=txn)
            if snap.exists:
                return False
            txn.set(claim_ref, {
                "run_day": run_day.isoformat(),
                "scan_date": scan_date.isoformat(),
                "claimed_at": firestore.SERVER_TIMESTAMP,
            })
            return True

        return _claim(db.transaction())
    except Exception as e:
        logger.error(f"claim_email_send failed (fail-open, will send): {e}")
        return True


def send_email(subject: str, html_content: str, to: str | None = None) -> bool:
    """Send a single Mailgun email. Defaults to operator (RECIPIENT_EMAIL).

    Pass ``to`` to fan out to a paid subscriber. One recipient per call so
    failures are isolated and Mailgun logs are clean per-recipient.
    """
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        logger.error("Mailgun credentials not set. Cannot send email.")
        return False

    recipient = to or RECIPIENT_EMAIL
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": MAILGUN_SENDER,
        "to": [recipient],
        "subject": subject,
        "html": html_content,
    }

    response = None
    try:
        response = requests.post(url, auth=auth, data=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully sent email to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e} - Response: {getattr(response, 'text', '')}")
        return False


def fetch_paid_subscriber_emails() -> list[str]:
    """Query Firestore ``users`` for active paid subscribers.

    Strict-tuple filter: ``plan == 'pro'`` AND ``subscriptionStatus == 'active'``
    AND ``stripeSubscriptionId`` non-null AND ``email`` non-null. Defense in
    depth — never relies on the ``isSubscribed`` flag alone, which historically
    defaulted to ``true`` on every signup before the 2026-04-29 fix.

    Returns empty on any error so subscriber fan-out is best-effort and never
    blocks the operator email path.
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        query = (
            db.collection("users")
            .where("plan", "==", "pro")
            .where("subscriptionStatus", "==", "active")
        )
        emails: list[str] = []
        for doc in query.stream():
            data = doc.to_dict() or {}
            email = data.get("email")
            stripe_sub_id = data.get("stripeSubscriptionId")
            if email and stripe_sub_id:
                emails.append(email)
        logger.info(f"Paid subscribers eligible for fan-out: {len(emails)}")
        return emails
    except Exception as e:
        logger.warning(f"Failed to fetch paid subscribers (fan-out will be skipped): {e}")
        return []


def fan_out_to_paid_subscribers(subject: str, html_content: str) -> int:
    """Send the daily V5.4 signal email to every active paid subscriber.

    Per-recipient send so one failure doesn't block the batch. Never raises —
    a fan-out blow-up must not affect the operator notification or return
    code. Returns the count successfully delivered.
    """
    emails = fetch_paid_subscriber_emails()
    if not emails:
        logger.info("No paid subscribers — fan-out skipped.")
        return 0

    sent = 0
    for email in emails:
        try:
            if send_email(subject, html_content, to=email):
                sent += 1
        except Exception as e:
            logger.error(f"Subscriber fan-out raised for {email}: {e}")
    logger.info(f"Paid subscriber fan-out: {sent}/{len(emails)} delivered")
    return sent


def format_whatsapp_message(
    row: pd.Series | None,
    target_date: date,
    entry_day: date | None,
    has_pick: bool,
    skip_reason: str | None = None,
    v5_4_meta: dict | None = None,
) -> str:
    """Plain-text WhatsApp message — mirrors the email content, concise.

    On happy path: single pick + routine. On skip: one-line rationale so the
    group sees the engine is standing down (and doesn't wonder if it's broken).
    """
    if not has_pick:
        reason_lines = {
            "no_candidates_passed_gates": "Nothing cleared the gates. Do nothing today.",
            "regime_fail_closed": "VIX or VIX3M missing — engine is standing down.",
            "vix_backwardation": "VIX > VIX3M (backwardation). Engine skipped today.",
            "earnings_overlap_all_candidates": "All top candidates report earnings during the hold window. Engine skipped today.",
            "earnings_calendar_unavailable": "Earnings calendar unavailable — engine is standing down (fail-closed).",
            "v5_4_unavailable": "Agent ranker unavailable — engine is standing down (fail-closed).",
            "v5_4_out_of_set": "Agent ranker returned an off-list pick — engine is standing down (fail-closed).",
            "v5_4_mass_leakage": "Agent ranker detected leaked inputs across all candidates — engine is standing down (fail-closed).",
        }
        reason = reason_lines.get(skip_reason or "", f"No pick today ({skip_reason}).")
        return (
            f"*GammaRips — {target_date.isoformat()}*\n"
            f"No trade today.\n"
            f"{reason}\n\n"
            f"_Paper-trading, educational only. Not investment advice._"
        )

    assert row is not None and entry_day is not None
    ticker = row["ticker"]
    direction = row["direction"]
    contract = row.get("recommended_contract", "")
    strike = row.get("recommended_strike")
    dte = row.get("recommended_dte")
    mid = row.get("recommended_mid_price")
    vol_oi = row.get("volume_oi_ratio")
    money = row.get("moneyness_pct")

    try:
        vol_oi_str = f"{float(vol_oi):.2f}" if vol_oi is not None else "n/a"
    except (TypeError, ValueError):
        vol_oi_str = "n/a"
    try:
        money_str = f"{float(money) * 100:.1f}% OTM" if money is not None else "n/a"
    except (TypeError, ValueError):
        money_str = "n/a"
    try:
        mid_str = f"${float(mid):.2f}" if mid is not None else "—"
    except (TypeError, ValueError):
        mid_str = "—"

    signal_url = f"{PUBLIC_WEBAPP_BASE}/signals/{ticker}"
    # V5.4 Picker justification — trim to one short line for WhatsApp.
    why_line = ""
    if v5_4_meta:
        j = (v5_4_meta.get("justification") or "").strip()
        if j:
            why_line = f"_Why:_ {j[:180]}{'…' if len(j) > 180 else ''}\n\n"
    return (
        f"*GammaRips — {entry_day.isoformat()}*\n"
        f"*{ticker} {direction}*\n"
        f"`{contract}`\n"
        f"Strike {strike} · DTE {dte} · Mid {mid_str} · V/OI {vol_oi_str} · {money_str}\n\n"
        f"{why_line}"
        f"Full rationale: {signal_url}\n\n"
        f"_Paper-trading, educational only. Not investment advice._"
    )


def post_to_openclaw(message: str) -> None:
    """Fire-and-forget WhatsApp push to OpenClaw. NEVER raises.

    Activates when ``OPENCLAW_GATEWAY_URL``, ``OPENCLAW_HOOKS_TOKEN``, and
    ``OPENCLAW_GROUP_JID`` are all set. If any are missing or the POST fails,
    we log and move on — the email path is the fallback.
    """
    if not (OPENCLAW_GATEWAY_URL and OPENCLAW_HOOKS_TOKEN and OPENCLAW_GROUP_JID):
        logger.info("OpenClaw not configured (missing env); skipping WhatsApp push.")
        return

    try:
        url = f"{OPENCLAW_GATEWAY_URL.rstrip('/')}/hooks/agent"
        payload = {
            "chat_jid": OPENCLAW_GROUP_JID,
            "text": message,
        }
        headers = {
            "Authorization": f"Bearer {OPENCLAW_HOOKS_TOKEN}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        if resp.status_code >= 400:
            logger.warning(
                f"OpenClaw push returned {resp.status_code}: {resp.text[:200]}"
            )
        else:
            logger.info(f"OpenClaw push OK ({resp.status_code}).")
    except Exception as e:  # noqa: BLE001 — intentional broad catch
        logger.warning(f"OpenClaw push failed (non-fatal): {e}")


# =====================================================================
# V5.4 picker — canonical (2026-05-08 V5.3 retirement)
# =====================================================================
#
# signal-judge /rank is BLOCKING — its return is THE pick. On any error
# (timeout, 5xx, picker out-of-set), signal-notifier fails CLOSED: no email,
# empty-state todays_pick doc, WhatsApp standby. signal-judge uptime is the
# product SLO. No V5.3 SQL fallback exists post-promotion.
#
# The V5.4 ticker lands in Firestore todays_pick/{scan_date} (canonical doc
# for webapp banner, MCP get_todays_pick, x-poster signal, gamma-bot, blog
# newsletter). forward-paper-trader simulates every enriched signal and
# tags rows policy_version='V7_1_TILTED_GIGO'; the "official pick" is
# identified by ticker JOIN to todays_pick.


def fetch_report_md(scan_date: date) -> str:
    """Pull today's overnight report markdown from Firestore daily_reports.

    Returns empty string on miss or error — signal-judge handles empty
    report_md gracefully (regime_alignment will lean neutral).
    """
    try:
        db = firestore.Client(project=PROJECT_ID)
        doc = db.collection("daily_reports").document(scan_date.isoformat()).get()
        if not doc.exists:
            return ""
        d = doc.to_dict() or {}
        parts = []
        if d.get("title"):
            parts.append(f"# {d['title']}")
        if d.get("headline"):
            parts.append(d["headline"])
        if d.get("content"):
            parts.append(d["content"])
        return "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"fetch_report_md failed for {scan_date}: {e}")
        return ""


def compute_14d_ledger_summary(scan_date: date, window_days: int = 14) -> dict:
    """14d ledger summary by direction × policy_version. Picker context."""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        start = scan_date - timedelta(days=window_days)
        q = f"""
        SELECT policy_version, direction,
               COUNT(*) AS n,
               COUNTIF(realized_return_pct > 0) AS wins,
               COUNTIF(realized_return_pct < 0) AS losses,
               ROUND(AVG(realized_return_pct), 4) AS avg_pct
        FROM `{PROJECT_ID}.profit_scout.forward_paper_ledger`
        WHERE scan_date >= '{start.isoformat()}'
          AND scan_date < '{scan_date.isoformat()}'
          AND COALESCE(is_skipped, FALSE) = FALSE
          AND realized_return_pct IS NOT NULL
        GROUP BY policy_version, direction
        """
        rows = list(client.query(q).result())
        total = 0
        by_dir, by_pol = {}, {}
        for r in rows:
            d = dict(r)
            n = int(d["n"])
            total += n
            by_dir.setdefault(d["direction"], {"n": 0, "wins": 0, "losses": 0})
            by_dir[d["direction"]]["n"] += n
            by_dir[d["direction"]]["wins"] += int(d["wins"])
            by_dir[d["direction"]]["losses"] += int(d["losses"])
            by_pol.setdefault(d["policy_version"], {"n": 0, "wins": 0, "losses": 0})
            by_pol[d["policy_version"]]["n"] += n
            by_pol[d["policy_version"]]["wins"] += int(d["wins"])
            by_pol[d["policy_version"]]["losses"] += int(d["losses"])
        return {
            "window_days": window_days,
            "closed_trades": total,
            "by_direction": by_dir,
            "by_policy": by_pol,
            "notes": (
                f"{total} closed in last {window_days}d. "
                f"by_direction={by_dir}. by_policy={by_pol}."
            ),
        }
    except Exception as e:
        logger.warning(f"compute_14d_ledger_summary failed: {e}")
        return {
            "window_days": window_days, "closed_trades": 0,
            "by_direction": {}, "by_policy": {},
            "notes": "ledger summary unavailable",
        }


def _candidate_for_ranker(row: pd.Series, static_rank: int) -> dict:
    """Convert a top-10 enriched row to a JSON-safe candidate dict for /rank."""
    c: dict = {}
    for k, v in row.items():
        if pd.isna(v):
            continue
        if isinstance(v, (date, datetime)):
            c[k] = (v.date() if isinstance(v, datetime) else v).isoformat()
        else:
            c[k] = v
    c["static_rank"] = static_rank
    return c


def _edge_score(row: pd.Series) -> float:
    """Deterministic edge score from the 1,375-trade realized-option-PnL study.
    Higher = more aligned with what actually separated winners from losers. Used
    ONLY to order the strict pool for the top-K cap — it never selects the pick
    (the tournament does) and it never drops a candidate categorically. All inputs
    are point-in-time at scan_date (leakage-safe). See
    docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md.

      direction  BULLISH +4.1% vs BEARISH -7.7%  -> biggest single separator
      |delta|    0.35-0.46 +6.6% vs deep ITM +0.1% (confirmed Q19 trap-escape)
      RR         < 1.4 +2-3% vs > 1.4 far-OTM lottery -7.7%
      ATR move   already-moved-hard +4.1% vs quiet -3.3% (monotonic, capped)
    """
    score = 0.0
    if str(row.get("direction", "")).upper() == "BULLISH":
        score += 2.0
    delta = row.get("recommended_delta")
    if delta is not None and not pd.isna(delta):
        if EDGE_DELTA_LO <= abs(float(delta)) <= EDGE_DELTA_HI:
            score += 1.5
    rr = row.get("risk_reward_ratio")
    if rr is not None and not pd.isna(rr) and float(rr) < EDGE_RR_MAX:
        score += 1.0
    atr_move = row.get("atr_normalized_move")
    if atr_move is not None and not pd.isna(atr_move):
        score += 0.5 * min(float(atr_move), 2.5)  # reward magnitude, cap runaway
    return score


def _edge_rank_and_cap(df: pd.DataFrame, k: int) -> pd.DataFrame:
    """Order the strict pool by deterministic edge score (desc), tie-broken by
    overnight_score (desc), and keep the top ``k``. SOFT cap — a strong bearish or
    high-RR name can still survive into the top-K and reach the tournament. Returns
    the full df unchanged when it already fits within k. The tournament still makes
    the actual pick across whatever survives. See
    docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md."""
    if df is None or len(df) <= k:
        return df
    scored = df.assign(_edge_score=df.apply(_edge_score, axis=1))
    scored = scored.sort_values(
        ["_edge_score", "overnight_score"], ascending=[False, False]
    ).head(k).drop(columns=["_edge_score"]).reset_index(drop=True)
    logger.info(
        f"Edge-rank cap: {len(df)} -> {len(scored)} candidates into tournament "
        f"(cap={k}); survivors: {list(scored['ticker'])}"
    )
    return scored


def _fetch_live_oi(underlying: str, contract: str) -> tuple[int | None, int | None, str]:
    """Re-fetch LIVE open interest for one option contract at pick time.

    Returns ``(live_oi, today_volume, status)`` where:
      * ``live_oi``      — ``results.open_interest`` (int) or None.
      * ``today_volume`` — ``results.day.volume`` (int) or None. INTERNAL ONLY:
        the caller pops this out before building the /rank payload — it is never
        surfaced to the judge.
      * ``status``       — "ok" | "polygon_empty" | "polygon_error".

    C1 (LEAKAGE, non-negotiable): the v3/snapshot/options response also carries
    ``implied_volatility``, ``greeks`` (delta/gamma/theta/vega), ``day`` OHLC,
    ``last_trade`` and ``last_quote`` — all entry-day-LIVE (10:00+ window). This
    function extracts ONLY open_interest and day.volume and lets the rest of the
    response go out of scope here. NOTHING else crosses the function boundary.

    Single attempt, 8s timeout, fail-soft — never raises (mirrors
    compute_active_days_20d). On any failure the caller keeps the candidate with
    its frozen scan-time OI (C4: a fetch failure for a contract = "no live OI",
    NOT a drop).
    """
    if not POLYGON_API_KEY:
        logger.error(
            f"POLYGON_API_KEY not set; cannot re-fetch live OI for {contract}"
        )
        return None, None, "polygon_error"
    url = (
        f"https://api.polygon.io/v3/snapshot/options/{underlying}/{contract}"
        f"?apiKey={POLYGON_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=LIVE_OI_FETCH_TIMEOUT_S)
        if resp.status_code != 200:
            logger.warning(
                f"Polygon option snapshot {contract} HTTP {resp.status_code}: "
                f"{resp.text[:200]}"
            )
            return None, None, "polygon_error"
        body = resp.json()
    except Exception as e:
        logger.warning(f"Polygon option snapshot {contract} fetch failed: {e}")
        return None, None, "polygon_error"

    if not isinstance(body, dict):
        logger.warning(f"Polygon option snapshot {contract} non-dict body: {str(body)[:200]}")
        return None, None, "polygon_error"
    res = body.get("results")
    if not isinstance(res, dict) or not res:
        # 200 with no results = contract not found / no snapshot. Fail-soft.
        return None, None, "polygon_empty"

    # --- C1: extract ONLY open_interest + day.volume; discard everything else ---
    # `res.get("greeks")`, `res.get("implied_volatility")`, `res.get("day")` OHLC,
    # `res.get("last_trade")`, `res.get("last_quote")` are all entry-day-live and
    # are DELIBERATELY NOT read. `oi` and `vol` below are the only two scalars
    # that survive past this point.
    oi_raw = res.get("open_interest")
    day = res.get("day") if isinstance(res.get("day"), dict) else {}
    vol_raw = day.get("volume")
    try:
        live_oi = int(oi_raw) if oi_raw is not None else None
    except (TypeError, ValueError):
        live_oi = None
    try:
        today_volume = int(vol_raw) if vol_raw is not None else None
    except (TypeError, ValueError):
        today_volume = None
    return live_oi, today_volume, "ok"


def _refresh_live_oi_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Re-fetch live OI for every candidate in parallel and attach two transient
    columns: ``live_oi`` and ``_today_volume`` (internal). Returns a COPY of df.

    C4 (per-candidate fail-soft): each future is individually try/excepted. A
    timeout / error for one contract = ``live_oi=None`` for that row — it is KEPT
    (the floor falls back to frozen ``recommended_oi``), never dropped here.

    Worst-case wall-clock: with up to ~50 candidates fanned across
    LIVE_OI_MAX_WORKERS (default 16) threads at LIVE_OI_FETCH_TIMEOUT_S (8s) each,
    the bound is ceil(50/16) * 8s ~= 24s (plus negligible HTTP setup). Even at
    workers=1 the absolute worst case is ~50 * 8s = 400s, still inside the
    notifier's 540s request timeout AND well before the trader cron reads
    todays_pick — but the default 16-worker pool keeps it to ~half a minute.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    out = df.copy()
    out["live_oi"] = None
    out["_today_volume"] = None

    # Build the work list: (index, underlying, contract). Skip rows with no
    # contract symbol — those keep live_oi=None and fall back to frozen OI.
    work: list[tuple] = []
    for idx, row in out.iterrows():
        contract = row.get("recommended_contract")
        underlying = row.get("ticker")
        if (contract is None or pd.isna(contract)
                or underlying is None or pd.isna(underlying)):
            continue
        work.append((idx, str(underlying), str(contract)))

    if not work:
        return out

    n_ok = n_empty = n_err = 0
    workers = max(1, min(LIVE_OI_MAX_WORKERS, len(work)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fut_to_idx = {
            pool.submit(_fetch_live_oi, u, c): idx for (idx, u, c) in work
        }
        for fut in as_completed(fut_to_idx):
            idx = fut_to_idx[fut]
            try:
                live_oi, today_volume, status = fut.result()
            except Exception as e:
                # C4: a per-future blow-up = "no live OI for this contract".
                logger.warning(f"live-OI future raised for row {idx}: {e}")
                continue
            if status == "ok":
                n_ok += 1
            elif status == "polygon_empty":
                n_empty += 1
            else:
                n_err += 1
            if live_oi is not None:
                out.at[idx, "live_oi"] = live_oi
            if today_volume is not None:
                out.at[idx, "_today_volume"] = today_volume

    logger.info(
        f"Live-OI refresh: {len(work)} contracts queried "
        f"(ok={n_ok} empty={n_empty} err={n_err}); "
        f"with-live-oi={int(out['live_oi'].notna().sum())}"
    )
    return out


def _effective_oi(row: pd.Series) -> float:
    """Live OI if present, else the frozen scan-time recommended_oi, else 0."""
    lo = row.get("live_oi")
    if lo is not None and not pd.isna(lo):
        try:
            return float(lo)
        except (TypeError, ValueError):
            pass
    ro = row.get("recommended_oi")
    if ro is not None and not pd.isna(ro):
        try:
            return float(ro)
        except (TypeError, ValueError):
            pass
    return 0.0


def _liquidity_refresh_and_rank(candidates_df: pd.DataFrame) -> pd.DataFrame:
    """Deterministic live-OI liquidity floor + soft tilt, run on the edge-capped
    strict pool just before the tournament. See
    docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md.

    Steps:
      1. Re-fetch LIVE OI per candidate (C1: OI-only; entry-day-live fields
         discarded at fetch time).
      2. DROP candidates with live_oi < OI_FLOOR (fill-rate cliff, not PnL).
      3. FAIL-SOFT FLOOR: if fewer than TOURNEY_MIN survive, restore the
         top-effective-OI names up to TOURNEY_MIN so the tournament never starves
         to zero (which would spuriously surface no_candidates_passed_gates).
      4. SOFT TILT: order survivors by effective OI desc (fillability).

    C4 (total fail-soft): the whole body is wrapped — ANY exception returns the
    INPUT df unchanged (frozen-OI / edge-rank order), never empty, never raising
    into the live pick. The LIQUIDITY_TILT kill switch short-circuits to identical
    pre-2026-06-25 behavior.

    `live_oi` is the only NEW key that surfaces to /rank (C1). `_today_volume` is
    internal — it is popped before the payload is built (see call_signal_ranker).
    """
    if not LIQUIDITY_TILT:
        return candidates_df
    if candidates_df is None or len(candidates_df) == 0:
        return candidates_df
    try:
        refreshed = _refresh_live_oi_batch(candidates_df)

        # Effective OI per row (live where available, frozen otherwise).
        eff = refreshed.apply(_effective_oi, axis=1)
        survivors = refreshed[eff >= OI_FLOOR].copy()

        n_total = len(refreshed)
        n_pass = len(survivors)

        if n_pass < TOURNEY_MIN:
            # Fail-soft floor: never starve the tournament. Take the top-OI names
            # up to TOURNEY_MIN regardless of the floor so a thin day still ranks.
            ordered_all = refreshed.assign(_eff_oi=eff).sort_values(
                "_eff_oi", ascending=False
            )
            keep_n = min(TOURNEY_MIN, n_total)
            survivors = ordered_all.head(keep_n).drop(columns=["_eff_oi"]).copy()
            logger.info(
                f"Live-OI floor: only {n_pass}/{n_total} cleared OI_FLOOR={OI_FLOOR}; "
                f"fail-soft restored top-{keep_n} by effective OI "
                f"(survivors: {list(survivors['ticker'])})"
            )
        else:
            # Soft tilt: order the passing pool by effective OI desc (fillability).
            survivors = survivors.assign(
                _eff_oi=survivors.apply(_effective_oi, axis=1)
            ).sort_values("_eff_oi", ascending=False).drop(columns=["_eff_oi"])
            logger.info(
                f"Live-OI floor: {n_pass}/{n_total} cleared OI_FLOOR={OI_FLOOR}; "
                f"tilted by effective OI (survivors: {list(survivors['ticker'])})"
            )

        return survivors.reset_index(drop=True)
    except Exception as e:
        # C4: never raise into the live pick. Fall back to the input df untouched
        # (edge-rank order, frozen OI). Worst case = today's exact behavior.
        logger.error(
            f"Live-OI liquidity refresh failed ({e}); falling back to "
            f"edge-rank pool unchanged (fail-soft)."
        )
        return candidates_df


def call_signal_ranker(
    top_10_df: pd.DataFrame,
    scan_date: date,
    entry_day: date,
    report_md: str,
    ledger_summary: dict,
) -> dict | None:
    """POST the edge-capped candidate pool to signal-judge /rank.

    Returns the parsed RankResponse dict on success, None on any failure
    (timeout, 5xx, malformed JSON, missing required fields). Caller MUST
    treat None as "fail-closed today" — no V5.3 fallback exists post-2026-05-08.
    """
    if not SIGNAL_JUDGE_URL:
        logger.info("SIGNAL_JUDGE_URL not set; V5.4 shadow path disabled")
        return None
    if top_10_df is None or len(top_10_df) == 0:
        logger.info("Empty candidate set; skipping V5.4 call")
        return None

    candidates = [
        _candidate_for_ranker(row, idx)
        for idx, (_, row) in enumerate(top_10_df.iterrows(), start=1)
    ]
    # C1: `_today_volume` is an INTERNAL liquidity-floor input (today's live
    # option volume). It must NEVER reach the judge — pop it out of every
    # candidate before the payload is built. `live_oi` (the only new permitted
    # live key) stays. `_candidate_for_ranker` copies all df columns verbatim, so
    # this is where the internal column is stripped from the wire format.
    for cand in candidates:
        cand.pop("_today_volume", None)

    # C3 leakage guard (2026-06-25): the live-OI snapshot also carries entry-day
    # IV / greeks / day OHLC / last trade / last quote. Those are discarded at
    # fetch time (_fetch_live_oi, C1) and must never appear on a candidate. Assert
    # it explicitly here, immediately before the payload is serialized, so any
    # future regression that re-attaches a live field fails CLOSED (the notifier
    # raises -> the V5.4 path catches it -> fail-closed, no pick) instead of
    # silently leaking the future into the tournament.
    for cand in candidates:
        leaked = _FORBIDDEN_LIVE_KEYS & set(cand.keys())
        assert not leaked, f"entry-day-live leak into /rank payload: {leaked}"

    payload = {
        "scan_date": scan_date.isoformat(),
        "entry_day": entry_day.isoformat(),
        "candidates": candidates,
        "report_md": report_md,
        "ledger_summary": ledger_summary,
    }

    try:
        # Mint ID token for the IAM-protected /rank endpoint. Cloud Run SA
        # creds support fetch_id_token directly (operator smoke tests need
        # the gcloud workaround; runtime does not).
        import google.auth.transport.requests
        from google.oauth2 import id_token as id_token_lib
        auth_req = google.auth.transport.requests.Request()
        token = id_token_lib.fetch_id_token(auth_req, SIGNAL_JUDGE_URL)
        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.post(
            f"{SIGNAL_JUDGE_URL}/rank",
            json=payload,
            headers=headers,
            # 480s — the bracket tournament makes ~39 model calls (3 brackets x
            # ~13), so it runs longer than the old single call; plus signal-judge
            # is min_instances=0 so cold start can add
            # 30-60s on top of the ~30-45s Scorer fanout + Picker call. Cloud
            # Run service-to-service calls without warm pools regularly take
            # 60-120s on the first request after idle. Trader's own timeout
            # is 540s so we have plenty of headroom.
            timeout=480,
        )
        if resp.status_code != 200:
            logger.error(
                f"signal-judge /rank returned {resp.status_code}: "
                f"{resp.text[:400]}"
            )
            return None
        body = resp.json()
        if not isinstance(body, dict) or "pick" not in body or "confidence" not in body:
            logger.error(f"signal-judge malformed response: {str(body)[:400]}")
            return None
        return body
    except Exception as e:
        logger.error(f"signal-judge call failed: {e}")
        return None


def format_email_html(
    row: pd.Series,
    target_date: date,
    entry_day: date,
    v5_4_meta: dict | None = None,
) -> str:
    """V5.4 email: one signal, one routine + agent-ranker justification.

    Mirrors CHEAT-SHEET.md trader mechanics. v5_4_meta carries the Picker's
    justification + confidence (rendered as a 'Why we picked it' block). One
    template for operator + paid subscribers — no separate operator-only
    shadow block post-promotion (2026-05-08).
    """
    ticker = row["ticker"]
    direction = row["direction"]
    contract = row.get("recommended_contract", "")
    dte = row.get("recommended_dte")
    vol = row.get("recommended_volume")
    oi = row.get("recommended_oi")
    vol_oi = row.get("volume_oi_ratio")
    money = row.get("moneyness_pct")
    strike = row.get("recommended_strike")
    mid = row.get("recommended_mid_price")
    color = "#0a8f3c" if direction == "BULLISH" else "#c62828"

    try:
        vol_oi_str = f"{float(vol_oi):.2f}" if vol_oi is not None else "n/a"
    except (TypeError, ValueError):
        vol_oi_str = "n/a"
    try:
        money_str = f"{float(money)*100:.1f}% OTM" if money is not None else "n/a"
    except (TypeError, ValueError):
        money_str = "n/a"
    try:
        mid_str = f"${float(mid):.2f}" if mid is not None else "—"
    except (TypeError, ValueError):
        mid_str = "—"

    signal_url = f"{PUBLIC_WEBAPP_BASE}/signals/{ticker}"

    # V5.4 justification block. Shows the Picker's reasoning + confidence
    # right under the contract card. Operator + paid subs see the same block.
    v5_4_block = ""
    if v5_4_meta:
        justification = (v5_4_meta.get("justification") or "").strip()
        confidence = (v5_4_meta.get("confidence") or "").strip()
        runner_up = (v5_4_meta.get("runner_up") or "").strip()
        if justification:
            conf_chip = (
                f'<span style="display:inline-block;padding:1px 8px;'
                f'border-radius:10px;font-size:11px;font-weight:600;'
                f'background:#e8f0fe;color:#1a73e8;letter-spacing:0.3px;">'
                f'{confidence.upper()}</span>'
            ) if confidence else ""
            runner_up_line = (
                f'<div style="color:#888;font-size:12px;margin-top:6px;">'
                f'Runner-up: {runner_up}</div>'
            ) if runner_up else ""
            v5_4_block = f"""
      <div style="margin: 12px 0; padding: 12px 14px; background-color: #f7f7f9; border-left: 3px solid #1a73e8; font-size: 14px;">
        <div style="font-size: 11px; color: #888; letter-spacing: 0.5px; margin-bottom: 6px;">
          WHY WE PICKED IT &nbsp;{conf_chip}
        </div>
        <p style="margin: 0; color: #333; line-height: 1.5;">{justification}</p>
        {runner_up_line}
      </div>
            """

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 560px;">
      <h2 style="margin-bottom: 0;">GammaRips Signal — {entry_day}</h2>
      <p style="color: #666; margin-top: 4px;">Agent ranker · scan {target_date}</p>

      <a href="{signal_url}" style="text-decoration: none; color: inherit;">
        <div style="padding: 12px 16px; border: 2px solid {color}; border-radius: 6px; margin: 12px 0; cursor: pointer;">
          <div style="font-size: 22px;"><strong>{ticker}</strong>
            <span style="color: {color}; font-weight: 600;">&nbsp;{direction}</span>
          </div>
          <div style="font-size: 15px; margin-top: 4px;">
            <code>{contract}</code>
          </div>
          <div style="color: #555; margin-top: 6px;">
            Strike {strike} · DTE {dte} · Mid {mid_str} · V/OI {vol_oi_str} · {money_str}
          </div>
          <div style="color: #1a73e8; margin-top: 8px; font-size: 13px;">
            Read the full rationale →
          </div>
        </div>
      </a>
{v5_4_block}
    </div>
    """
    return html


def compute_and_write_cohort_stats() -> bool:
    """Refresh ``cohort_stats/current`` from forward_paper_ledger.

    Cohort definition: ``DATE(entry_timestamp) >= LIVE_COHORT_START_DATE``
    AND ``policy_version = 'V7_1_TILTED_GIGO'`` AND closed
    (realized_return_pct not null). Pre-cohort rows were TRUNCATED 2026-05-08
    when V5.3 was retired; the ledger restarts fresh under V5.4.

    Webapp reads this Firestore doc directly for the public live-stats panel.
    Failures NEVER raise — a stats-write blow-up must not affect the operator
    email path. Returns True on success, False on any failure.
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        # Fixed-dollar sizing: n_contracts = max(1, ROUND(POSITION_SIZE_USD /
        # (entry_price * 100))). Computed in-SQL so changing position size is a
        # one-place update and the ledger keeps per-contract granularity. See
        # docs/DECISIONS/2026-05-19-cohort-start-and-position-sizing.md.
        query = f"""
        WITH sized AS (
          SELECT
            realized_return_pct,
            entry_price,
            GREATEST(1, CAST(ROUND({POSITION_SIZE_USD} / (entry_price * 100)) AS INT64)) AS n_contracts
          FROM `{PROJECT_ID}.profit_scout.forward_paper_ledger`
          WHERE DATE(entry_timestamp) >= "{LIVE_COHORT_START_DATE}"
            AND policy_version = "V7_1_TILTED_GIGO"
            AND realized_return_pct IS NOT NULL
            AND entry_price IS NOT NULL
            AND entry_price > 0
        )
        SELECT
          COUNT(*) AS trades_closed,
          COUNTIF(realized_return_pct > 0) AS trades_won,
          COALESCE(SAFE_DIVIDE(COUNTIF(realized_return_pct > 0), COUNT(*)), 0) AS win_rate,
          COALESCE(SUM(n_contracts * entry_price * 100), 0) AS total_invested_usd,
          COALESCE(SUM(n_contracts * entry_price * 100 * realized_return_pct), 0) AS total_pl_usd,
          COALESCE(SAFE_DIVIDE(
            SUM(n_contracts * entry_price * 100 * realized_return_pct),
            SUM(n_contracts * entry_price * 100)
          ), 0) AS roi_pct
        FROM sized
        """
        rows = list(client.query(query).result())
        r = rows[0] if rows else None

        stats = {
            "cohort_start": LIVE_COHORT_START_DATE,
            "policy_version": "V7_1_TILTED_GIGO",
            "position_size_usd": POSITION_SIZE_USD,
            "as_of": firestore.SERVER_TIMESTAMP,
            "trades_closed": int(r["trades_closed"]) if r else 0,
            "trades_won": int(r["trades_won"]) if r else 0,
            "win_rate": float(r["win_rate"]) if r else 0.0,
            "total_invested_usd": float(r["total_invested_usd"]) if r else 0.0,
            "total_pl_usd": float(r["total_pl_usd"]) if r else 0.0,
            "roi_pct": float(r["roi_pct"]) if r else 0.0,
        }

        db = firestore.Client(project=PROJECT_ID)
        db.collection("cohort_stats").document("current").set(stats)
        logger.info(
            f"cohort_stats/current updated: {stats['trades_closed']} closed, "
            f"win_rate={stats['win_rate']:.2%}, roi={stats['roi_pct']:.2%}, "
            f"invested=${stats['total_invested_usd']:.2f}, pl=${stats['total_pl_usd']:.2f}"
        )
        return True
    except Exception as e:  # noqa: BLE001 — intentional broad catch
        logger.warning(f"cohort_stats write failed (non-fatal): {e}")
        return False


def _parse_occ_contract(occ: str | None) -> dict:
    """Parse an OCC option symbol into {option_type, strike, expiration}.

    Example: ``O:CIEN260605P00525000`` -> PUT, 525.0, 2026-06-05. The tail is a
    fixed 6-digit date + 1 type char + 8-digit (strike*1000) suffix; the root is
    variable-length and ignored here. Best-effort: returns Nones on any failure.
    """
    out = {"option_type": None, "strike": None, "expiration": None}
    try:
        s = (occ or "").split(":", 1)[-1]  # drop the 'O:' prefix if present
        if len(s) < 15:
            return out
        tail = s[-15:]               # YYMMDD + C/P + 8-digit strike
        yymmdd, cp, strike_raw = tail[0:6], tail[6].upper(), tail[7:15]
        out["expiration"] = f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"
        out["option_type"] = "CALL" if cp == "C" else "PUT" if cp == "P" else None
        out["strike"] = int(strike_raw) / 1000.0
    except Exception:
        return {"option_type": None, "strike": None, "expiration": None}
    return out


def compute_and_write_ledger_trades() -> bool:
    """Sync closed V5.4 cohort trades to Firestore ``ledger_trades/{scan_date}_{ticker}``.

    Powers the public scorecard per-trade ledger table. Uses the SAME cohort
    definition and fixed-dollar sizing as ``compute_and_write_cohort_stats``
    (``DATE(entry_timestamp) >= LIVE_COHORT_START_DATE`` AND
    ``policy_version = 'V7_1_TILTED_GIGO'`` AND closed), so the table rows and
    the aggregate tiles can never disagree. Idempotent (merge by doc id).
    Non-fatal: never raises into the email path. Returns True on success.
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query = f"""
        WITH sized AS (
          SELECT
            CAST(DATE(scan_date) AS STRING) AS scan_date,
            ticker, direction, recommended_contract, recommended_dte, policy_gate,
            CAST(DATE(entry_timestamp) AS STRING) AS entry_date,
            entry_price,
            CAST(DATE(exit_timestamp) AS STRING) AS exit_date,
            DATE_DIFF(DATE(exit_timestamp), DATE(entry_timestamp), DAY) AS hold_days,
            exit_reason, realized_return_pct,
            GREATEST(1, CAST(ROUND({POSITION_SIZE_USD} / (entry_price * 100)) AS INT64)) AS n_contracts
          FROM `{PROJECT_ID}.profit_scout.forward_paper_ledger`
          WHERE DATE(entry_timestamp) >= "{LIVE_COHORT_START_DATE}"
            AND policy_version = "V7_1_TILTED_GIGO"
            AND realized_return_pct IS NOT NULL
            AND entry_price IS NOT NULL
            AND entry_price > 0
        )
        SELECT *,
          ROUND(n_contracts * entry_price * 100, 2) AS capital_usd,
          ROUND(n_contracts * entry_price * 100 * realized_return_pct, 2) AS pl_usd,
          ROUND(n_contracts * entry_price * 100 * (1 + realized_return_pct), 2) AS exit_value_usd
        FROM sized
        ORDER BY entry_date
        """
        rows = list(client.query(query).result())

        db = firestore.Client(project=PROJECT_ID)
        batch = db.batch()
        n = 0
        for r in rows:
            parsed = _parse_occ_contract(r["recommended_contract"])
            doc = {
                "scan_date": r["scan_date"],
                "ticker": r["ticker"],
                "direction": r["direction"],
                "recommended_contract": r["recommended_contract"],
                "option_type": parsed["option_type"],
                "strike": parsed["strike"],
                "expiration": parsed["expiration"],
                "dte": int(r["recommended_dte"]) if r["recommended_dte"] is not None else None,
                "entry_date": r["entry_date"],
                "entry_price": float(r["entry_price"]),
                "n_contracts": int(r["n_contracts"]),
                "exit_date": r["exit_date"],
                "hold_days": int(r["hold_days"]) if r["hold_days"] is not None else None,
                "exit_reason": r["exit_reason"],
                "return_pct": float(r["realized_return_pct"]),
                "capital_usd": float(r["capital_usd"]),       # "Invested" column
                "exit_value_usd": float(r["exit_value_usd"]),  # "Exit Value" column
                "pl_usd": float(r["pl_usd"]),                  # "Profit" column
                "policy_gate": r["policy_gate"],
                "policy_version": "V7_1_TILTED_GIGO",
                "as_of": firestore.SERVER_TIMESTAMP,
            }
            batch.set(db.collection("ledger_trades").document(f"{r['scan_date']}_{r['ticker']}"), doc, merge=True)
            n += 1
            if n % 400 == 0:
                batch.commit()
                batch = db.batch()
        batch.commit()
        logger.info(f"ledger_trades synced: {n} V5.4 trades")
        return True
    except Exception as e:  # noqa: BLE001 — intentional broad catch
        logger.warning(f"ledger_trades sync failed (non-fatal): {e}")
        return False


def _build_candidate_query(target_date: date, fallback: bool = False) -> str:
    """Build the enriched-candidate SELECT for the strict or fallback pool.

    STRICT (default), as of the 2026-06-04 bracket-tournament, is INTENTIONALLY
    UNGATED on selection: NO moneyness band, NO OI/vol floor, NO DTE band, NO
    V/OI, NO active-days. The only WHERE predicates are SAFETY rails — a
    tradeable contract must exist (strike/expiration NOT NULL) and regime data
    must be present (vix3m_at_enrich NOT NULL). The tournament in signal-judge
    picks across the full pool (downstream regime + earnings exclusions still
    apply in run_notifier; spread<=8% still runs upstream in enrichment-trigger).
    See docs/DECISIONS/2026-06-04-bracket-tournament.md.

    FALLBACK (daily-cadence, 2026-06-01) is a SEPARATE path that BYPASSES the
    tournament (run_notifier takes df.iloc[0]). Because nothing downstream bounds
    it, FALLBACK re-applies a moneyness band here (ATM floor, 0.10 cap) so the
    bypassed pick can't be deep-ITM/deep-OTM.
    See docs/DECISIONS/2026-06-01-daily-cadence-fallback.md.

    ORDER BY (both modes): composite ``overnight_score`` DESC, then resting
    ``recommended_oi`` DESC (fillability), then spread. For FALLBACK this is the
    selection (iloc[0]); for STRICT it only orders the pool the tournament reads.
    """
    if fallback:
        # FALLBACK still bounds moneyness. The fallback pick BYPASSES the
        # tournament (run_notifier takes df.iloc[0]), so the band is the only
        # thing keeping the bypassed pick from being deep-ITM/deep-OTM — it MUST
        # be interpolated into the WHERE clause. Floor relaxed to ATM, cap pinned
        # at FALLBACK_MONEYNESS_MAX (0.10). Rank by composite score, then resting
        # open interest (fillability), then spread.
        moneyness_where = f"""
      AND moneyness_pct IS NOT NULL
      AND moneyness_pct BETWEEN {FALLBACK_MONEYNESS_MIN} AND {FALLBACK_MONEYNESS_MAX}"""
        order_by = """
        overnight_score DESC,
        recommended_oi DESC,
        recommended_spread_pct ASC,
        ticker ASC"""
    else:
        # 2026-06-04 bracket-tournament: the STRICT path is INTENTIONALLY
        # UNGATED on moneyness/OI/vol/DTE/V-OI/active-days — every enriched
        # signal reaches the tournament in signal-judge, which weighs moneyness
        # (it's in the SELECT below) rather than us pre-filtering it. So the
        # strict moneyness band is empty here. See
        # docs/DECISIONS/2026-06-04-bracket-tournament.md.
        moneyness_where = ""
        order_by = """
        overnight_score DESC,
        recommended_oi DESC,
        recommended_spread_pct ASC,
        ticker ASC"""

    # BULLISH-only hard gate (2026-06-11, owner-directed). Applies to BOTH paths
    # so no bearish name can reach email via strict OR fallback. The edge levers
    # are call-delta-defined and don't transfer to puts; env-toggleable. See
    # docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md.
    direction_where = "\n      AND direction = 'BULLISH'" if BULLISH_ONLY else ""

    # 2026-06-04 bracket-tournament: STRICT filters ONLY strike/expiration/vix3m
    # NOT NULL here, then regime + earnings downstream in run_notifier. The
    # moneyness, OI, vol, DTE, V/OI, and active-days SELECTION gates are
    # intentionally NOT applied on the strict path — the tournament in signal-judge
    # picks across the full pool. (spread<=8% still runs upstream in
    # enrichment-trigger.) The rich feature columns (technicals, narrative, greeks)
    # plus moneyness_pct are selected so the judge gets the full structured JSON and
    # can weigh moneyness itself. Leakage cols (next_day*/day2_*/day3_*/peak_return/
    # is_win/outcome_tier) are DELIBERATELY NOT selected. ``moneyness_where`` is the
    # FALLBACK-only band (empty on strict). See
    # docs/DECISIONS/2026-06-04-bracket-tournament.md.
    return f"""
    SELECT
        ticker, scan_date, direction, underlying_price, price_change_pct,
        recommended_contract, recommended_strike, recommended_expiration,
        recommended_dte, recommended_volume, recommended_oi,
        recommended_mid_price, recommended_spread_pct,
        recommended_delta, recommended_gamma, recommended_theta, recommended_iv,
        overnight_score, premium_score,
        call_dollar_volume, put_dollar_volume, call_uoa_depth, put_uoa_depth,
        call_active_strikes, put_active_strikes,
        volume_oi_ratio, call_vol_oi_ratio, put_vol_oi_ratio,
        moneyness_pct, vix3m_at_enrich,
        flow_intent, flow_intent_reasoning,
        rsi_14, macd, sma_50, sma_200, atr_normalized_move,
        golden_cross, above_sma_50, above_sma_200,
        support, resistance, high_52w, low_52w,
        thesis, news_summary, key_headline, catalyst_type, catalyst_score,
        mean_reversion_risk, move_overdone, reversal_probability, risk_reward_ratio,
        premium_bull_flow, premium_bear_flow, premium_high_rr, premium_high_atr, premium_hedge
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND vix3m_at_enrich IS NOT NULL{direction_where}{moneyness_where}
    ORDER BY{order_by}
    LIMIT 200
    """


def run_notifier(target_date: date | None = None):
    # Market-holiday stand-down. The notifier fires on the intended ENTRY day
    # (the run day). On a closed-market day we send NOTHING (no email, no
    # WhatsApp, no tournament spend) and write a clean skip doc so the webapp
    # shows a "markets closed" state.
    #
    # DOC-KEYING: the webapp's getLatestTodaysPick() does
    # orderBy('scan_date','desc').limit(1) — it returns the doc with the highest
    # scan_date FIELD. Keying the skip doc to run_day (the holiday) would write
    # an ORPHAN: the next real run keys its doc to get_previous_trading_day(next
    # session) = the last session BEFORE the holiday (a smaller scan_date), so it
    # never overwrites the holiday doc, and the orphan stays max → "markets
    # closed" sticks on the next trading day, hiding the real pick.
    # FIX: key the skip doc to get_previous_trading_day(run_day) — the same
    # scan_date / doc id the next real run will use — so the next run cleanly
    # overwrites the placeholder. No orphan.
    # See 2026-06-19 Juneteenth: email + trade fired on a closed market.
    run_day = datetime.now(est).date()
    if not is_trading_day(run_day):
        skip_scan_date = get_previous_trading_day(run_day)
        logger.info(f"{run_day} is not an NYSE trading day (market holiday/closed). Standing down: no email, no tournament. Writing market_holiday skip doc keyed to {skip_scan_date}.")
        write_todays_pick_doc(skip_scan_date, has_pick=False, skip_reason="market_holiday")
        return True, "market_holiday"

    if not target_date:
        target_date = get_previous_trading_day(datetime.now(est).date())

    logger.info(f"Running V5.4 Signal Notifier for scan_date={target_date}")

    # Refresh public cohort stats + per-trade ledger once per run. Independent
    # of the day's pick / skip outcome — they reflect ledger state, not today's
    # decision. Non-fatal: a stats blow-up never affects the email path.
    compute_and_write_cohort_stats()
    compute_and_write_ledger_trades()

    client = bigquery.Client(project=PROJECT_ID)

    # Strict conviction gate first (V5.3 stack). On a zero-candidate day we no
    # longer skip — we run the daily-cadence fallback (drop V/OI floor, allow
    # ATM) to surface the best fillable candidate. gate_mode is threaded into
    # todays_pick (policy_gate) and onward to the ledger so fallback EV is
    # measurable separately. See docs/DECISIONS/2026-06-01-daily-cadence-fallback.md.
    gate_mode = POLICY_GATE_STRICT
    try:
        df = client.query(_build_candidate_query(target_date, fallback=False)).to_dataframe()
    except Exception as e:
        logger.error(f"Failed to query BigQuery: {e}")
        return False, f"Error querying BQ: {e}"

    if len(df) == 0:
        logger.info(
            "Strict conviction gates left 0 candidates — running daily-cadence "
            "fallback (relax V/OI + moneyness floor; tradeability gates intact)."
        )
        gate_mode = POLICY_GATE_FALLBACK
        try:
            df = client.query(_build_candidate_query(target_date, fallback=True)).to_dataframe()
        except Exception as e:
            logger.error(f"Fallback BigQuery query failed: {e}")
            return False, f"Error querying BQ (fallback): {e}"

    logger.info(f"Post-filter candidates: {len(df)} for {target_date} (gate_mode={gate_mode})")

    if len(df) == 0:
        # Genuinely barren scan_date — neither the strict nor the fallback pool
        # had a fillable candidate. This is an honest skip, not starvation.
        logger.info("No eligible candidates (strict or fallback). No email sent.")
        # Fail-closed: write the empty-state todays_pick doc so every downstream
        # reader (webapp banner, MCP, GTM) learns the skip reason atomically.
        write_todays_pick_doc(target_date, has_pick=False, skip_reason="no_candidates_passed_gates")
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False, skip_reason="no_candidates_passed_gates"
        ))
        return True, "No eligible signal."

    # Regime gate uses the top candidate's vix3m_at_enrich. VIX3M is a
    # market-wide indicator written once per scan_date by enrichment-trigger,
    # so it is the same across every row in df. Picking row[0] is correct
    # even if the earnings filter below ultimately selects a different row.
    regime_top = df.iloc[0]
    vix3m = regime_top.get("vix3m_at_enrich")
    vix_now = fetch_vix_close(target_date)
    if vix3m is None or vix_now is None:
        logger.info(
            f"Regime gate fail-closed: vix3m_at_enrich={vix3m}, vix_now={vix_now}. "
            f"No email sent."
        )
        write_todays_pick_doc(target_date, has_pick=False, skip_reason="regime_fail_closed")
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False, skip_reason="regime_fail_closed"
        ))
        return True, "Regime gate fail-closed (missing VIX or VIX3M)."
    if vix_now > float(vix3m):
        logger.info(
            f"Regime gate: VIX {vix_now:.2f} > VIX3M {float(vix3m):.2f} "
            f"(backwardation). Skipping email."
        )
        write_todays_pick_doc(target_date, has_pick=False, skip_reason="vix_backwardation")
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False, skip_reason="vix_backwardation"
        ))
        return True, f"Backwardation regime (VIX {vix_now:.2f} > VIX3M {float(vix3m):.2f}). Skipped."

    # Earnings-overlap exclusion (2026-05-06). Fail-closed if the calendar is
    # unreachable: we cannot distinguish "no earnings" from "API down."
    # Window starts at scan_date (target_date), not entry_day, to catch
    # AMC-scan_date contamination — a ticker that reports after-hours on the
    # scan day generated its UOA flow under known-imminent-earnings positioning,
    # then prints before our 10:00 entry_day open. CDW (BMO entry_day) was
    # caught by entry_day; AMC scan_date is the symmetric case.
    entry_day = get_next_trading_day(target_date)
    exit_day = get_hold_window_end(entry_day)
    earnings_tickers = fetch_earnings_calendar(target_date, exit_day)
    if earnings_tickers is None:
        logger.info("Earnings calendar fetch failed — fail-closed. No email sent.")
        write_todays_pick_doc(target_date, has_pick=False, skip_reason="earnings_calendar_unavailable")
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False, skip_reason="earnings_calendar_unavailable"
        ))
        return True, "Earnings calendar unavailable (fail-closed)."

    # Earnings-overlap exclusion: build the candidate pool the tournament will
    # rank. As of 2026-06-04 the SELECT that produced df is INTENTIONALLY UNGATED
    # on selection (no moneyness/OI/vol/DTE/V-OI) — it applied only the
    # strike/expiration/vix3m NOT NULL safety rails (and the FALLBACK-only
    # moneyness band). Regime (VIX≤VIX3M) is checked separately below; spread≤8%
    # runs upstream in enrichment-trigger. Earnings overlap is the last hard
    # filter — anything that touches an earnings print in [scan_date, exit_day]
    # is removed before the tournament sees it.
    skipped_for_earnings: list[str] = [
        str(c["ticker"]).upper() for _, c in df.iterrows()
        if str(c["ticker"]).upper() in earnings_tickers
    ]
    df = df[~df["ticker"].str.upper().isin(earnings_tickers)].reset_index(drop=True)

    if len(df) == 0:
        logger.info(
            f"All top-ranked candidates report earnings in [{target_date}, {exit_day}]. "
            f"Skipped tickers: {skipped_for_earnings}"
        )
        write_todays_pick_doc(target_date, has_pick=False, skip_reason="earnings_overlap_all_candidates")
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False, skip_reason="earnings_overlap_all_candidates"
        ))
        return True, "All top candidates have earnings overlap. Skipped."

    if skipped_for_earnings:
        logger.info(
            f"Earnings exclusion: removed {len(skipped_for_earnings)} candidates "
            f"({skipped_for_earnings}). {len(df)} candidates passed to V5.4."
        )

    # 2026-06-04 bracket-tournament: the active-days liquidity gate is REMOVED
    # (was added 2026-05-19; KBR Jun-18 27.5P INVALID_LIQUIDITY was the motivating
    # case). All signals get a chance — the early/illiquid sweeps (OI builds AFTER
    # our 10:00 entry, so scan-time OI is a stale snapshot) are exactly what we
    # want the tournament to weigh, not filter out. This also drops the ~N
    # per-candidate Polygon calls (latency). The old `df.assign(active_days_20d=
    # None)` no-op was removed: it never reached the /rank payload anyway
    # (_candidate_for_ranker drops None-valued columns). See
    # docs/DECISIONS/2026-06-04-bracket-tournament.md.

    if len(df) == 0:
        # The pool emptied here even though it was non-empty before this gate
        # (we only entered this block if earnings filtering left rows). Use the
        # existing day-level skip reason — thin_contract_liquidity is per
        # candidate, not per day, per the decision doc.
        logger.info(
            "All remaining candidates were filtered out. No email sent."
        )
        write_todays_pick_doc(
            target_date, has_pick=False, skip_reason="no_candidates_passed_gates"
        )
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False,
            skip_reason="no_candidates_passed_gates",
        ))
        return True, "No eligible signal after regime/earnings filters."

    # Pick selection. On STRICT days the signal-judge bracket tournament ranks
    # the FULL pool. On FALLBACK days we bypass the tournament entirely: the pool
    # is already "best fillable candidate within the fallback moneyness band" by
    # construction (ORDER BY score, OI), and ranking ~1 low-conviction name only
    # re-introduces a mass-leakage skip that would defeat the daily-cadence
    # guarantee. The regime and earnings filters above have already run on the
    # fallback pool. See docs/DECISIONS/2026-06-01-daily-cadence-fallback.md.
    if gate_mode == POLICY_GATE_FALLBACK:
        top = df.iloc[0]
        v5_4_meta = {
            "runner_up": str(df.iloc[1]["ticker"]) if len(df) > 1 else None,
            "justification": (
                "Fallback pick — the strict pool was empty. Selected the best "
                "candidate by composite score and resting open interest, bounded "
                "by the fallback moneyness band (ATM floor, 0.10 cap); the regime "
                "and earnings filters passed. Low conviction by construction — "
                "tagged FALLBACK in the ledger."
            ),
            "confidence": "LOW",
            "run_id": None,
            "scorer_prompt_version": None,
            "picker_prompt_version": None,
            "scorer_model": None,
            "picker_model": None,
        }
        logger.info(
            f"FALLBACK pick (ranker bypassed): {top['ticker']} {top['direction']} "
            f"score={top.get('overnight_score')} oi={top.get('recommended_oi')}"
        )
    else:
        # V5.4 IS the picker — no V5.3 SQL "rank-1" fallback. signal-judge uptime
        # is the SLO. On any error: fail-closed (no email, empty-state todays_pick).
        # Decision lock: docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md.
        v5_4_response: dict | None = None
        try:
            report_md = fetch_report_md(target_date)
            ledger_summary = compute_14d_ledger_summary(target_date)
            # Edge-rank cap: deterministically narrow the strict pool to the top
            # TOURNEY_POOL_CAP edge-aligned candidates BEFORE the tournament. Cuts
            # ~39 model calls/pick to ~9 (cap=12). Soft cap — bearish/high-RR names
            # can still survive. See docs/DECISIONS/2026-06-11-edge-rank-pool-cap.md.
            df = _edge_rank_and_cap(df, TOURNEY_POOL_CAP)
            # Live-OI liquidity floor (2026-06-25): re-fetch live OI at pick time,
            # drop dead contracts below OI_FLOOR (fill-rate cliff, not PnL), and
            # soft-tilt by fillability. Fail-soft on every axis — never empties the
            # pool, never raises (returns df unchanged on any error / when
            # LIQUIDITY_TILT=false). live_oi is injected here and surfaces to the
            # judge; _today_volume is internal and popped before the /rank payload.
            # See docs/DECISIONS/2026-06-25-live-oi-liquidity-floor.md.
            df = _liquidity_refresh_and_rank(df)
            v5_4_response = call_signal_ranker(
                df, target_date, entry_day, report_md, ledger_summary
            )
        except Exception as e:
            logger.error(f"V5.4 path raised: {e}")
            v5_4_response = None

        if v5_4_response is None:
            logger.error("V5.4 signal-judge unavailable. Fail-closed: no email, no WhatsApp pick.")
            write_todays_pick_doc(target_date, has_pick=False, skip_reason="v5_4_unavailable")
            post_to_openclaw(format_whatsapp_message(
                None, target_date, None, has_pick=False, skip_reason="v5_4_unavailable"
            ))
            return True, "V5.4 signal-judge unavailable. Fail-closed."

        # Mass-leakage skip. signal-judge sets skip=True when every candidate
        # verdict is flagged leakage (judge_v6 §2; deterministic all-leakage check
        # in run_pipeline) — picking the "least bad" of identically-poisoned
        # candidates would ship a coin flip. Treat it like any other fail-closed
        # reason: no email, empty-state todays_pick, alert
        # the WhatsApp channel that the engine stood down.
        if v5_4_response.get("skip"):
            skip_reason_raw = v5_4_response.get("skip_reason") or "mass_leakage"
            skip_reason_full = f"v5_4_{skip_reason_raw}"
            logger.error(
                f"V5.4 ranker returned skip={skip_reason_full}. Fail-closed: no email."
            )
            write_todays_pick_doc(target_date, has_pick=False, skip_reason=skip_reason_full)
            post_to_openclaw(format_whatsapp_message(
                None, target_date, None, has_pick=False, skip_reason=skip_reason_full
            ))
            return True, f"V5.4 skip ({skip_reason_full}). Fail-closed."

        # V5.4 chose a ticker — find its enriched row in df for contract details.
        pick_ticker = v5_4_response.get("pick")
        picked_rows = df[df["ticker"] == pick_ticker]
        if picked_rows.empty:
            # Picker out-of-set — signal-judge should have caught this and
            # returned 500. If it slipped through, fail-closed (don't fabricate a
            # pick from a ticker not in df).
            logger.error(
                f"V5.4 picked {pick_ticker} but it's not in the candidate df. "
                f"Out-of-set bug. Fail-closed."
            )
            write_todays_pick_doc(target_date, has_pick=False, skip_reason="v5_4_out_of_set")
            post_to_openclaw(format_whatsapp_message(
                None, target_date, None, has_pick=False, skip_reason="v5_4_out_of_set"
            ))
            return True, f"V5.4 returned out-of-set ticker {pick_ticker}. Fail-closed."

        top = picked_rows.iloc[0]
        v5_4_meta = {
            "runner_up": v5_4_response.get("runner_up"),
            "justification": v5_4_response.get("justification"),
            "confidence": v5_4_response.get("confidence"),
            "run_id": v5_4_response.get("run_id"),
            "scorer_prompt_version": v5_4_response.get("scorer_prompt_version"),
            "picker_prompt_version": v5_4_response.get("picker_prompt_version"),
            "scorer_model": v5_4_response.get("scorer_model"),
            "picker_model": v5_4_response.get("picker_model"),
        }

    # Happy path: write todays_pick doc BEFORE sending email. Fail-closed —
    # if the Firestore write raises, we do NOT send an email (the operator
    # would see email-without-webapp state and that's the exact drift we're
    # preventing with the single-source-of-truth contract).
    write_todays_pick_doc(
        target_date, has_pick=True, top=top, vix_now=vix_now, v5_4_meta=v5_4_meta,
        policy_gate=gate_mode,
    )

    # Single email path — operator + paid subscribers see the SAME html with
    # V5.4 justification embedded under the contract card. No operator-only
    # shadow block (retired with V5.3 promotion 2026-05-08). Fallback picks are
    # marked in the subject so the recipient knows it's a low-conviction day.
    html_content = format_email_html(top, target_date, entry_day, v5_4_meta=v5_4_meta)
    subject = f"GammaRips {entry_day}: {top['ticker']} {top['direction']}"
    if gate_mode == POLICY_GATE_FALLBACK:
        subject += " [FALLBACK]"

    # Idempotency guard: a Scheduler retry (or any double-trigger) must not
    # re-send. Claim the send transactionally (keyed on the ET run-day); if this
    # morning's send was already claimed, suppress all outbound (email + WhatsApp
    # + sub fan-out) and report success so Scheduler stops retrying. todays_pick
    # was already (idempotently) written above, so the webapp stays correct.
    if not claim_email_send(target_date):
        logger.warning(
            f"Duplicate trigger today (scan_date={target_date}) — pick already "
            f"sent this morning. Suppressing email/WhatsApp/fan-out (Scheduler "
            f"retry guard, keyed on ET run-day)."
        )
        return True, f"Duplicate trigger suppressed (already sent today; scan_date={target_date})."

    success = send_email(subject, html_content)

    # WhatsApp push is non-blocking and runs whether or not email succeeded —
    # it's an independent fan-out to a different channel, not a retry path.
    post_to_openclaw(format_whatsapp_message(
        top, target_date, entry_day, has_pick=True, v5_4_meta=v5_4_meta,
    ))

    # Paid subscriber fan-out — additive, non-blocking. Subscribers receive
    # the same html_content as operator post-promotion (V5.4 is the product).
    try:
        fan_out_count = fan_out_to_paid_subscribers(subject, html_content)
    except Exception as e:
        logger.error(f"Subscriber fan-out blew up (non-fatal): {e}")
        fan_out_count = 0

    if success:
        return True, (
            f"Emailed V5.4 pick: {top['ticker']} {top['direction']} "
            f"(confidence={v5_4_meta.get('confidence')}, "
            f"runner_up={v5_4_meta.get('runner_up')}; "
            f"operator + {fan_out_count} subscribers)."
        )
    return False, "Failed to send operator email."


@app.route("/refresh_stats", methods=["POST"])
def refresh_stats():
    """Ad-hoc seed / recovery for ``cohort_stats/current``.

    Safe to curl any time. Does NOT send email or WhatsApp; only refreshes
    the public-stats Firestore doc + per-trade ledger_trades. Used post-deploy
    to seed the empty-state doc and any time the operator wants to force a
    refresh outside the daily cron cadence.
    """
    ok = compute_and_write_cohort_stats()
    ledger_ok = compute_and_write_ledger_trades()
    if ok and ledger_ok:
        return jsonify({"status": "success", "message": "cohort_stats/current + ledger_trades refreshed."}), 200
    return jsonify({"status": "error", "message": "stats/ledger refresh failed; check logs."}), 500


@app.route("/", methods=["GET", "POST"])
def trigger_notifier():
    try:
        req_data = request.get_json(silent=True)
        target_date_str = req_data.get("target_date") if req_data else None

        if target_date_str:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        else:
            target_date = get_previous_trading_day(datetime.now(est).date())

        success, msg = run_notifier(target_date)
        if success:
            return jsonify({"status": "success", "message": msg}), 200
        return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        logger.error(f"Error in signal-notifier endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
