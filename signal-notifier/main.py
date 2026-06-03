"""Signal Notifier — V5.4 Agent Ranker (canonical 2026-05-08).

Reads `overnight_signals_enriched`, applies the hard gate stack to build the
candidate pool, calls the V5.4 signal-ranker to pick one ticker, and sends
ONE email with that pick to operator + paid subscribers (same content). On
any V5.4 error (timeout, 5xx, picker out-of-set), fails CLOSED — no email.

Gate stack (run UPSTREAM of the V5.4 picker):
  - ``volume_oi_ratio > 2.0`` — REMOVED 2026-06-02. Realized option-PnL
        backtest (N=1,375) showed it dropped ~55-63% of real winners for
        precision lift <= 0; it was the main cause of picker-slate starvation
        (~2 candidates/day). See DECISIONS/2026-06-02-voi-gate-relaxation-proposal.md.
  - ``moneyness_pct BETWEEN 0.05 AND 0.13``   5-13% OTM (cap widened 0.10->0.13
        on 2026-06-02; the H12 deep-OTM-cliff lit is hold-to-expiry, not our
        3-day bracket. See DECISIONS/2026-06-02-moneyness-cap-widen-to-13.md.
        FALLBACK path keeps the 0.10 cap.).
  - ``vix3m_at_enrich`` present AND ``VIX <= VIX3M`` (no backwardation)
        Fail-closed: a NULL vix3m_at_enrich or a missing current VIX means we
        skip the email for the day entirely.
  - **Earnings-overlap exclusion** (added 2026-05-06): exclude any ticker
    whose scheduled earnings date falls inside ``[scan_date, exit_day]``
    where ``exit_day = entry_day + 2 trading days``. Window includes
    scan_date so AMC-scan_date prints (signal generated under known-imminent
    earnings positioning) are caught alongside BMO-entry_day (the CDW case)
    and any in-hold-window report. Literature-anchored (De Silva/Smith/So
    2026 RoF; Cao/Han 2013 JFE) — retail loses 5-9% per earnings event on
    long single-leg through the print. Fail-closed on calendar fetch failure.
    See docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md.

The picker (V5.4): Scorer fanout (`gemini-3.5-flash`, scorer_v3 with
HEDGING flow_conviction ≤4 hard cap) + Picker (`gemini-3.1-pro-preview`,
picker_v2, enum confidence). Composite weights 60/25/15 flow/regime/narrative
(weighted sum). Hosted at signal-ranker Cloud Run service. signal-ranker
uptime is the SLO — no V5.3 SQL fallback. See docs/DECISIONS/
2026-05-08-v5-3-retired-v5-4-promoted.md.

Trader execution mechanics (forward-paper-trader, separate service): entry
10:00 ET day-1, stop -60%, target +80%, 3-day hold, exit 15:50 ET day-3.
Unchanged across V5.3 → V5.4 — the picker change is what V5.4 introduced.
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
LIVE_COHORT_START_DATE = "2026-05-13"

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

# V5.4 signal-ranker — sole live picker (promoted 2026-05-08). If the env var
# is missing or the call fails for any reason, this service fails closed: no
# pick is published, no email is sent, no `todays_pick` doc is written with
# `has_pick=True`. There is no V5.3 fallback path.
SIGNAL_RANKER_URL = os.environ.get("SIGNAL_RANKER_URL", "").strip().rstrip("/")

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
# Liquidity floors relaxed 2026-05-12 (Scenario C, picker starvation fix; see
# docs/DECISIONS/2026-05-12-v5-4-pipeline-alignment.md). Pre-relaxation values
# (OI_MIN=20, VOL_MIN=100) were chosen as defensive defaults at the 2026-04-30
# liquidity-floor launch; researcher funnel analysis on the 22 V5.4-era scan
# dates showed they were the dominant cause of zero-candidate days. Halving
# both floors keeps the "contract is actually fillable" intent while opening
# the candidate pool. Underlying liquidity is already enforced upstream by
# enrichment-trigger (directional UOA > $500K), so a 10/50 contract still
# sits inside a real flow envelope. Revisit at N=15 closed V5.4 trades only
# if win rate diverges materially by OI/volume decile.
OI_MIN = 10      # contract must have real open interest to be fillable
VOL_MIN = 50     # contract must have traded yesterday in size

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

# Active-days liquidity gate (added 2026-05-19). Each finalist's
# recommended_contract must have printed volume on at least ACTIVE_DAYS_MIN of
# the 20 trading days preceding scan_date. Picked deliberately at 5: lifts
# entry-day fillability 50% -> 71% (~95% of the gain from >=8) with zero V5.4
# dry days in the 25-day backtest. Tuning requires a new DECISIONS doc — do
# not loosen via env var or hot-path edit. See:
#   docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md
ACTIVE_DAYS_MIN = 5

# Daily-cadence fallback (2026-06-01, see
# docs/DECISIONS/2026-06-01-daily-cadence-fallback.md). When the strict
# conviction gates (V/OI > 2, 5-10% OTM band) leave ZERO candidates, we no
# longer skip the day — we surface the single best *fillable* candidate so the
# cohort gets a trade on every tradeable day. The fallback RELAXES only the two
# pure-conviction gates (unusual-volume V/OI, the tight OTM band) and KEEPS
# every tradeability / literature-settled gate intact: OI/vol floors, the
# regime (VIX<=VIX3M) gate, the earnings-overlap exclusion, and the active-days
# liquidity gate all still run on the fallback pool. The 2026-05-26 skip day is
# the motivating case: 24 score-7/8 names were thrown away; HUBS (OI 733, vol
# 215) was perfectly fillable and only failed V/OI (0.3). Fallback picks are
# tagged policy_gate="FALLBACK" end-to-end so their EV is measurable separately
# from STRICT picks and the fallback can be killed with data if it loses.
FALLBACK_MONEYNESS_MIN = 0.0   # ATM allowed (strict floor 0.05); ITM still excluded
# DECOUPLED from MONEYNESS_MAX on 2026-06-02. Previously `= MONEYNESS_MAX`, which
# would silently widen the fallback cap whenever the strict cap moved. Fallback
# fires only on zero-strict-candidate (lowest-conviction) days — the worst place
# for deeper-OTM names — so it stays pinned at 0.10 even though STRICT is now 0.13.
FALLBACK_MONEYNESS_MAX = 0.10   # pinned; do NOT inherit MONEYNESS_MAX — no deep-OTM on fallback days
# V/OI floor is dropped entirely for the fallback (unusual-flow conviction is
# precisely what we relax). OI_MIN / VOL_MIN / DTE band are UNCHANGED — a
# fallback pick must still be fillable, and the active-days gate downstream is
# the resting-liquidity backstop that keeps thin OI=3 names (CDNS) out.
POLICY_GATE_STRICT = "STRICT"
POLICY_GATE_FALLBACK = "FALLBACK"

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
            "policy_version": "V5_4_AGENT_RANKER",
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
            "vol_oi_ratio": _num("volume_oi_ratio"),
            "moneyness_pct": _num("moneyness_pct"),
            "call_dollar_volume": _num("call_dollar_volume"),
            "put_dollar_volume": _num("put_dollar_volume"),
            "vix3m_at_enrich": _num("vix3m_at_enrich"),
            "vix_now_at_decision": float(vix_now) if vix_now is not None else None,
            "vix_source": _LAST_VIX_SOURCE,
            "policy_version": "V5_4_AGENT_RANKER",
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
VIX_FALLBACK_TOLERANCE = 1.5  # two non-FRED sources must agree within this (vol pts)
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

    Primary source FRED VIXCLS (single-source-trusted). On FRED failure, fall
    back to free public sources (Stooq, Yahoo) — but because the regime gate is
    one-sided (``vix_now > vix3m`` => skip), a single fallback source biased LOW
    could MASK a backwardation regime. So a fallback value is trusted only when
    BOTH Stooq and Yahoo corroborate within ``VIX_FALLBACK_TOLERANCE`` vol pts;
    otherwise we fail-closed (return None), exactly as if FRED were down.
    Consequence: a FRED-outage day on which only one backup answers now SKIPS
    (the 2026-06-03 Yahoo-only DAVE pick would have skipped under this rule).
    Records the winning source in ``_LAST_VIX_SOURCE`` for pick provenance.

    Hardened per gammarips-review of the 2026-06-03 live-VIX fallback.
    """
    global _LAST_VIX_SOURCE
    # FRED's fredgraph.csv intermittently 504s / read-times-out — retry with
    # linear backoff before giving up.
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS"
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

    # FRED down: require TWO independent public sources to corroborate before
    # trusting a fallback value for the gate (guards against a single low-biased
    # source masking backwardation).
    stooq = _fetch_vix_from_stooq(scan_date)
    yahoo = _fetch_vix_from_yahoo(scan_date)
    got = [(n, v) for n, v in (("Stooq", stooq), ("Yahoo", yahoo)) if v is not None]
    if len(got) < 2:
        have = ", ".join(f"{n}={v:.2f}" for n, v in got) or "none"
        logger.warning(
            f"VIX: FRED down and fallback uncorroborated (have: {have}); fail-closed "
            f"(need 2 sources within {VIX_FALLBACK_TOLERANCE} vol pts)."
        )
        return None
    spread = abs(got[0][1] - got[1][1])
    if spread > VIX_FALLBACK_TOLERANCE:
        logger.warning(
            f"VIX: fallback sources disagree ({got[0][0]}={got[0][1]:.2f}, "
            f"{got[1][0]}={got[1][1]:.2f}, spread {spread:.2f} > "
            f"{VIX_FALLBACK_TOLERANCE}); fail-closed."
        )
        return None
    val = round((got[0][1] + got[1][1]) / 2, 2)
    _LAST_VIX_SOURCE = f"{got[0][0]}+{got[1][0]}"
    logger.warning(
        f"VIX: FRED unavailable; corroborated fallback = {val:.2f} "
        f"({got[0][0]}={got[0][1]:.2f}, {got[1][0]}={got[1][1]:.2f})."
    )
    return val


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
    stop_pct_str = f"{int(STOP_PCT_DISPLAY * 100)}%"
    target_pct_str = f"{int(TARGET_PCT_DISPLAY * 100)}%"

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
        f"*Routine*\n"
        f"10:00 ET — buy 1 contract at market\n"
        f"Arm GTC −{stop_pct_str} stop AND +{target_pct_str} target\n"
        f"15:50 ET day-3 — close if neither has filled\n\n"
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
# signal-ranker /rank is BLOCKING — its return is THE pick. On any error
# (timeout, 5xx, picker out-of-set), signal-notifier fails CLOSED: no email,
# empty-state todays_pick doc, WhatsApp standby. signal-ranker uptime is the
# product SLO. No V5.3 SQL fallback exists post-promotion.
#
# The V5.4 ticker lands in Firestore todays_pick/{scan_date} (canonical doc
# for webapp banner, MCP get_todays_pick, x-poster signal, gamma-bot, blog
# newsletter). forward-paper-trader simulates every enriched signal and
# tags rows policy_version='V5_4_AGENT_RANKER'; the "official pick" is
# identified by ticker JOIN to todays_pick.


def fetch_report_md(scan_date: date) -> str:
    """Pull today's overnight report markdown from Firestore daily_reports.

    Returns empty string on miss or error — signal-ranker handles empty
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


def call_signal_ranker(
    top_10_df: pd.DataFrame,
    scan_date: date,
    entry_day: date,
    report_md: str,
    ledger_summary: dict,
) -> dict | None:
    """POST top-10 candidates to signal-ranker /rank.

    Returns the parsed RankResponse dict on success, None on any failure
    (timeout, 5xx, malformed JSON, missing required fields). Caller MUST
    treat None as "fail-closed today" — no V5.3 fallback exists post-2026-05-08.
    """
    if not SIGNAL_RANKER_URL:
        logger.info("SIGNAL_RANKER_URL not set; V5.4 shadow path disabled")
        return None
    if top_10_df is None or len(top_10_df) == 0:
        logger.info("Empty candidate set; skipping V5.4 call")
        return None

    candidates = [
        _candidate_for_ranker(row, idx)
        for idx, (_, row) in enumerate(top_10_df.iterrows(), start=1)
    ]
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
        token = id_token_lib.fetch_id_token(auth_req, SIGNAL_RANKER_URL)
        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.post(
            f"{SIGNAL_RANKER_URL}/rank",
            json=payload,
            headers=headers,
            # 300s — signal-ranker is min_instances=0 so cold start can add
            # 30-60s on top of the ~30-45s Scorer fanout + Picker call. Cloud
            # Run service-to-service calls without warm pools regularly take
            # 60-120s on the first request after idle. Trader's own timeout
            # is 540s so we have plenty of headroom.
            timeout=300,
        )
        if resp.status_code != 200:
            logger.error(
                f"signal-ranker /rank returned {resp.status_code}: "
                f"{resp.text[:400]}"
            )
            return None
        body = resp.json()
        if not isinstance(body, dict) or "pick" not in body or "confidence" not in body:
            logger.error(f"signal-ranker malformed response: {str(body)[:400]}")
            return None
        return body
    except Exception as e:
        logger.error(f"signal-ranker call failed: {e}")
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

    stop_pct_str = f"{int(STOP_PCT_DISPLAY * 100)}%"
    target_pct_str = f"{int(TARGET_PCT_DISPLAY * 100)}%"

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
      <h3 style="margin-bottom: 4px;">Today's Routine</h3>
      <table style="border-collapse: collapse; width: 100%;">
        <tr><td style="padding: 4px 8px;">10:00 AM ET <em>day 1</em></td>
            <td>Buy 1 contract at market. Arm
                <strong>-{stop_pct_str}</strong> GTC stop-limit
                <strong>AND</strong>
                <strong>+{target_pct_str}</strong> GTC limit sell on Robinhood.</td></tr>
        <tr><td style="padding: 4px 8px;">Through day 3</td>
            <td>Phone in pocket. Both exit orders armed. No monitoring.</td></tr>
        <tr><td style="padding: 4px 8px;">If either fills</td>
            <td>Cancel the other order — Robinhood doesn't auto-OCO options.</td></tr>
        <tr><td style="padding: 4px 8px;">3:50 PM ET <em>day 3</em></td>
            <td>If still open, cancel both pending orders, market sell. Done.</td></tr>
      </table>

      <p style="color: #888; font-size: 12px; margin-top: 16px;">
        Entry: 10:00 ET day-1 &middot; Stop: -{stop_pct_str} option premium &middot;
        Target: +{target_pct_str} option premium &middot; Hold: 3 trading days &middot;
        Exit: 15:50 ET day-3.
        Missed entry → skip. Missed exit → GTC stop and target still armed;
        close next morning open.
      </p>
    </div>
    """
    return html


def compute_and_write_cohort_stats() -> bool:
    """Refresh ``cohort_stats/current`` from forward_paper_ledger.

    Cohort definition: ``DATE(entry_timestamp) >= LIVE_COHORT_START_DATE``
    AND ``policy_version = 'V5_4_AGENT_RANKER'`` AND closed
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
            AND policy_version = "V5_4_AGENT_RANKER"
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
            "policy_version": "V5_4_AGENT_RANKER",
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
    ``policy_version = 'V5_4_AGENT_RANKER'`` AND closed), so the table rows and
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
            AND policy_version = "V5_4_AGENT_RANKER"
            AND realized_return_pct IS NOT NULL
            AND entry_price IS NOT NULL
            AND entry_price > 0
        )
        SELECT *,
          ROUND(n_contracts * entry_price * 100, 2) AS capital_usd,
          ROUND(n_contracts * entry_price * 100 * realized_return_pct, 2) AS pl_usd
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
                "exit_date": r["exit_date"],
                "hold_days": int(r["hold_days"]) if r["hold_days"] is not None else None,
                "exit_reason": r["exit_reason"],
                "return_pct": float(r["realized_return_pct"]),
                "capital_usd": float(r["capital_usd"]),
                "pl_usd": float(r["pl_usd"]),
                "policy_gate": r["policy_gate"],
                "policy_version": "V5_4_AGENT_RANKER",
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
    """Build the enriched-candidate SELECT for the strict or fallback gate.

    STRICT (default), as of 2026-06-02, is the 5-10% OTM band only (the
    unusual-volume V/OI > 2 gate was REMOVED — see the conviction_where comment
    and DECISIONS/2026-06-02). As of the same date STRICT and FALLBACK share the
    SAME ranking — composite ``overnight_score`` DESC, then resting
    ``recommended_oi`` DESC (fillability), then spread — so both pick the best
    fillable high-signal candidate. FALLBACK (daily-cadence, 2026-06-01)
    additionally lowers the moneyness floor to ATM. Both modes keep the OI/vol
    floors and the DTE band; the downstream regime, earnings, and active-days
    gates run identically on whichever pool this returns.
    See docs/DECISIONS/2026-06-01-daily-cadence-fallback.md.

    STRICT ORDER BY: re-ranked 2026-06-02 to ``overnight_score`` DESC primary,
    SUPERSEDING the 2026-05-01 directional-V/OI-DESC primary. Rationale in the
    order_by comment below: the 2026-05-01 EDA (N=435 V5.3) only established
    V/OI-DESC over a dollar-volume primary, and the 2026-06-02 realized-PnL
    analysis (N=1,375) shows V/OI carries no selection value — so it should not
    rank the pool the picker draws from. The scorer re-scores survivors by
    composite, making overnight_score the aligned pre-LIMIT sort.
    """
    if fallback:
        # Drop the V/OI floor; widen the moneyness floor to ATM. Rank by
        # composite score, then resting open interest (fillability), then spread.
        conviction_where = f"""
      AND moneyness_pct IS NOT NULL
      AND moneyness_pct BETWEEN {FALLBACK_MONEYNESS_MIN} AND {FALLBACK_MONEYNESS_MAX}"""
        order_by = """
        overnight_score DESC,
        recommended_oi DESC,
        recommended_spread_pct ASC,
        ticker ASC"""
    else:
        # V/OI > 2 conviction gate REMOVED 2026-06-02 (owner-directed; see
        # docs/DECISIONS/2026-06-02-voi-gate-relaxation-proposal.md). Realized
        # option-PnL backtest (N=1,375 fills) showed V/OI>2 drops ~55-63% of
        # real +80%/+25% winners for precision lift statistically <= 0
        # (90% CI [-0.061, -0.001]). It was strangling the picker's slate to a
        # median of ~2 candidates/day. The moneyness band and ALL tradeability
        # gates (OI/vol/DTE/regime/earnings/active-days) are unchanged.
        conviction_where = f"""
      AND moneyness_pct IS NOT NULL
      AND moneyness_pct BETWEEN {MONEYNESS_MIN} AND {MONEYNESS_MAX}"""
        # ORDER BY re-ranked 2026-06-02 to match FALLBACK: composite
        # ``overnight_score`` first, then resting ``recommended_oi`` (fillability),
        # then spread. This SUPERSEDES the 2026-05-01 directional-V/OI-DESC primary
        # — that EDA (N=435 V5.3) only beat a dollar-volume primary, and the
        # 2026-06-02 realized-PnL work (N=1,375) shows V/OI has no selection value,
        # so ranking the picker's pre-LIMIT pool by it is backwards. The LIMIT 10
        # only binds on high-inventory days; the scorer re-scores the survivors by
        # composite anyway, so overnight_score is the aligned pre-filter.
        order_by = """
        overnight_score DESC,
        recommended_oi DESC,
        recommended_spread_pct ASC,
        ticker ASC"""

    # LIMIT 10 — the earnings-overlap exclusion (2026-05-06) walks the ranked
    # list and takes the first ticker NOT reporting in the hold window; if all
    # 10 overlap the day is skipped.
    return f"""
    SELECT
        ticker, scan_date, direction,
        recommended_contract, recommended_strike, recommended_expiration,
        recommended_dte, recommended_volume, recommended_oi,
        recommended_mid_price, recommended_spread_pct,
        overnight_score, premium_score,
        call_dollar_volume, put_dollar_volume, call_uoa_depth, put_uoa_depth,
        volume_oi_ratio, call_vol_oi_ratio, put_vol_oi_ratio,
        moneyness_pct, vix3m_at_enrich
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL{conviction_where}
      AND vix3m_at_enrich IS NOT NULL
      AND recommended_oi >= {OI_MIN}
      AND recommended_volume >= {VOL_MIN}
      AND recommended_dte BETWEEN {DTE_MIN} AND {DTE_MAX}
    ORDER BY{order_by}
    LIMIT 10
    """


def run_notifier(target_date: date | None = None):
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

    # Earnings-overlap exclusion: build the candidate pool V5.4 will rank.
    # The hard gates (moneyness 5-13%, OI/vol floors, spread ≤8%, regime
    # VIX≤VIX3M; V/OI removed 2026-06-02) ran upstream in the SELECT that produced
    # df. Earnings overlap is the last hard filter — anything that touches an
    # earnings print in [scan_date, exit_day] is removed before V5.4 sees it.
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

    # Active-days liquidity gate (added 2026-05-19, per
    # docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md). Each surviving
    # finalist's recommended_contract must have printed volume on at least
    # ACTIVE_DAYS_MIN of the 20 trading days preceding scan_date. Two distinct
    # rejection reasons:
    #   * thin_contract_liquidity     — Polygon answered, count < threshold
    #   * liquidity_check_unavailable — Polygon errored or returned empty;
    #                                   fail-closed at the candidate level
    # The KBR Jun-18 27.5P 2026-05-14 INVALID_LIQUIDITY incident is the
    # motivating case (4 active days, scan-day vol=323 was a single block).
    pre_liquidity_n = len(df)
    keep_mask: list[bool] = []
    active_days_per_row: list[int | None] = []
    liquidity_rejections: list[dict] = []
    for _, cand in df.iterrows():
        ticker = str(cand.get("ticker", ""))
        contract = str(cand.get("recommended_contract", "") or "")
        if not contract:
            # Defensive — the SELECT already requires strike + expiration,
            # but a NULL recommended_contract slipping through should not
            # crash the loop. Fail-closed on the candidate.
            logger.info(
                f"Active-days gate: {ticker} has no recommended_contract; "
                f"removing from pool (liquidity_check_unavailable)."
            )
            keep_mask.append(False)
            active_days_per_row.append(None)
            liquidity_rejections.append({
                "ticker": ticker,
                "contract": contract,
                "active_days_20d": None,
                "reason": "liquidity_check_unavailable",
            })
            continue
        active, status = compute_active_days_20d(contract, target_date)
        if status != "ok":
            logger.info(
                f"Active-days gate: {ticker} {contract} status={status} "
                f"-> liquidity_check_unavailable (removed)."
            )
            keep_mask.append(False)
            active_days_per_row.append(None)
            liquidity_rejections.append({
                "ticker": ticker,
                "contract": contract,
                "active_days_20d": None,
                "reason": "liquidity_check_unavailable",
            })
            continue
        if active < ACTIVE_DAYS_MIN:
            logger.info(
                f"Active-days gate: {ticker} {contract} "
                f"active_days_20d={active} < {ACTIVE_DAYS_MIN} "
                f"-> thin_contract_liquidity (removed)."
            )
            keep_mask.append(False)
            active_days_per_row.append(active)
            liquidity_rejections.append({
                "ticker": ticker,
                "contract": contract,
                "active_days_20d": active,
                "reason": "thin_contract_liquidity",
            })
            continue
        keep_mask.append(True)
        active_days_per_row.append(active)

    # Attach the computed value as a column so the ranker payload carries it
    # forward as ranker context (signal-ranker ignores unknown keys; this is
    # purely additive). NaN-safe — None becomes NaN under pandas, which the
    # _candidate_for_ranker helper drops on isna check.
    df = df.assign(active_days_20d=active_days_per_row)
    df = df[keep_mask].reset_index(drop=True)

    if liquidity_rejections:
        logger.info(
            f"Active-days liquidity gate: removed {len(liquidity_rejections)} "
            f"of {pre_liquidity_n} candidates; {len(df)} candidates passed to V5.4. "
            f"Rejections: {liquidity_rejections}"
        )

    if len(df) == 0:
        # The pool emptied here even though it was non-empty before this gate
        # (we only entered this block if earnings filtering left rows). Use the
        # existing day-level skip reason — thin_contract_liquidity is per
        # candidate, not per day, per the decision doc.
        logger.info(
            "All remaining candidates failed the active-days liquidity gate. "
            "No email sent."
        )
        write_todays_pick_doc(
            target_date, has_pick=False, skip_reason="no_candidates_passed_gates"
        )
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False,
            skip_reason="no_candidates_passed_gates",
        ))
        return True, "No eligible signal after active-days liquidity gate."

    # Pick selection. On STRICT days the V5.4 Scorer/Picker LLM pair ranks the
    # pool. On FALLBACK days we bypass the ranker entirely: the pool is already
    # "best fillable candidate" by construction (ORDER BY score, OI), and ranking
    # ~1 low-conviction name only re-introduces a mass-leakage skip that would
    # defeat the daily-cadence guarantee. The regime, earnings, and active-days
    # gates above have already run on the fallback pool, so what survives here is
    # tradeable. See docs/DECISIONS/2026-06-01-daily-cadence-fallback.md.
    if gate_mode == POLICY_GATE_FALLBACK:
        top = df.iloc[0]
        v5_4_meta = {
            "runner_up": str(df.iloc[1]["ticker"]) if len(df) > 1 else None,
            "justification": (
                "Fallback pick — no signal cleared the strict conviction gates "
                "(unusual-volume V/OI > 2 or the 5-10% OTM band). Selected the "
                "best fillable candidate by composite score and resting open "
                "interest; the regime, earnings, and liquidity gates all passed. "
                "Low conviction by construction — tagged FALLBACK in the ledger."
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
        # V5.4 IS the picker — no V5.3 SQL "rank-1" fallback. signal-ranker uptime
        # is the SLO. On any error: fail-closed (no email, empty-state todays_pick).
        # Decision lock: docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md.
        v5_4_response: dict | None = None
        try:
            report_md = fetch_report_md(target_date)
            ledger_summary = compute_14d_ledger_summary(target_date)
            v5_4_response = call_signal_ranker(
                df, target_date, entry_day, report_md, ledger_summary
            )
        except Exception as e:
            logger.error(f"V5.4 path raised: {e}")
            v5_4_response = None

        if v5_4_response is None:
            logger.error("V5.4 signal-ranker unavailable. Fail-closed: no email, no WhatsApp pick.")
            write_todays_pick_doc(target_date, has_pick=False, skip_reason="v5_4_unavailable")
            post_to_openclaw(format_whatsapp_message(
                None, target_date, None, has_pick=False, skip_reason="v5_4_unavailable"
            ))
            return True, "V5.4 signal-ranker unavailable. Fail-closed."

        # Mass-leakage skip. signal-ranker sets skip=True when every top-5 candidate
        # scored 1/1/1 (per scorer_v4.md:29 leakage rule) — picking the "least bad"
        # of identically-floored candidates would ship a coin flip. Treat it like
        # any other fail-closed reason: no email, empty-state todays_pick, alert
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
            # Picker out-of-set — signal-ranker should have caught this and
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
