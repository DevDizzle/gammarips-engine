"""Signal Notifier — V5.3 Target 80

Reads `overnight_signals_enriched` for the target scan_date, applies the V5.3
filter stack, and sends at most one email with the single top-ranked signal.

Filters applied here (in addition to whatever enrichment already enforced):
  - ``volume_oi_ratio > 2.0``                 fresh flow, not stale OI
  - ``moneyness_pct BETWEEN 0.05 AND 0.10``   5-10% OTM (tightened 2026-05-06
        per H12 lit-audit; Aretz et al. 2023 RoF documents the deep-OTM EV
        cliff above ~10% on 9-DTE contracts).
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
    long single-leg through the print. Calendar source: FMP
    ``/v3/earning_calendar``. Fail-closed on calendar fetch failure AND on
    non-list payload (FMP quota-exhausted returns 200 + error dict).
    See docs/DECISIONS/2026-05-06-earnings-overlap-exclusion.md.
  - Pull top 10 ranked candidates, take the first that is NOT earnings-overlap.

If nothing passes, we send NOTHING — the user's inbox is the signal.

V5.3 delta from V5.2: the trader now exits on +80% option premium in addition
to the -60% stop and 3-day timeout. The signal stack here is unchanged — the
email must instruct the operator to arm BOTH the stop AND the target at entry.
"""

import logging
import os
from datetime import date, datetime, timedelta

import pandas as pd
import pandas_market_calendars as mcal
import pytz
import requests
from flask import Flask, jsonify, request
from google.cloud import bigquery, firestore

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

# Live cohort starts 2026-05-07 (first auto-cron entry day after the
# 2026-05-06 lit-audit deploy). Pre-2026-05-07 ledger rows were truncated
# 2026-05-06 — they were generated under pre-audit filters and don't form
# a clean baseline for the new cohort. See:
#   docs/DECISIONS/2026-05-06-paper-trader-reset-and-stats-surface.md
LIVE_COHORT_START_DATE = "2026-05-07"

# Public webapp base — used to build deep-links for emails / WhatsApp.
# Pinned here so the email surface never accidentally points at a staging
# host. Update in lockstep if the user-facing domain ever changes.
PUBLIC_WEBAPP_BASE = "https://gammarips.com"

# OpenClaw — non-blocking WhatsApp push. Activates the moment all three
# env vars are present. If any are missing the post is skipped silently.
OPENCLAW_GATEWAY_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "").strip()
OPENCLAW_HOOKS_TOKEN = os.environ.get("OPENCLAW_HOOKS_TOKEN", "").strip()
OPENCLAW_GROUP_JID = os.environ.get("OPENCLAW_GROUP_JID", "").strip()

nyse = mcal.get_calendar("NYSE")
est = pytz.timezone("America/New_York")

# V5.3 filter thresholds — canonical in CHEAT-SHEET.md
VOL_OI_MIN = 2.0
MONEYNESS_MIN = 0.05
# MONEYNESS_MAX tightened 0.15 -> 0.10 on 2026-05-06 per H12 (lit-audit).
# Aretz et al. 2023 RoF: ITM calls +7% / DOTM calls -27% systematic
# spread; at 9 DTE / 15% OTM, delta is 0.10-0.15 (lottery zone).
# Augustin et al. 2022 J. Fin. Markets: informed traders prefer slightly
# OTM, not deep-OTM, because B/A spreads scale inversely with price.
MONEYNESS_MAX = 0.10
OI_MIN = 20      # contract must have real open interest to be fillable
VOL_MIN = 100    # contract must have traded yesterday in size

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


def write_todays_pick_doc(
    scan_date: date,
    has_pick: bool,
    top: pd.Series | None = None,
    vix_now: float | None = None,
    skip_reason: str | None = None,
) -> None:
    """Canonical writer for Firestore ``todays_pick/{scan_date}``.

    This is the single source of truth for "what did GammaRips pick today"
    across all downstream surfaces (webapp banner, MCP get_todays_pick,
    arena-verdict, GTM drafter, WhatsApp push). All readers MUST read this
    doc without re-applying filters — that is the drift-prevention invariant.

    Schema pinned in docs/EXEC-PLANS/2026-04-20-v5-3-surface-and-monetization.md
    Phase 1.0.

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
            "policy_version": "V5_3_TARGET_80",
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
            "policy_version": "V5_3_TARGET_80",
        }

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


def fetch_vix_close(scan_date: date) -> float | None:
    """Return the VIX close on or before ``scan_date`` via FRED VIXCLS.

    Returns None on any failure. Callers must fail closed (skip the day) when
    we cannot determine the current VIX regime.
    """
    try:
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
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
                v = float(vstr)
            except ValueError:
                continue
            if d <= scan_date and (best is None or d > best[0]):
                best = (d, v)
        return best[1] if best else None
    except Exception as e:
        logger.warning(f"VIX fetch failed: {e}")
        return None


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
    """Send the V5.3 signal email to every active paid subscriber.

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
) -> str:
    """Plain-text WhatsApp message — mirrors the email content, concise.

    On happy path: single pick + routine. On skip: one-line rationale so the
    group sees the engine is standing down (and doesn't wonder if it's broken).
    """
    stop_pct_str = f"{int(STOP_PCT_DISPLAY * 100)}%"
    target_pct_str = f"{int(TARGET_PCT_DISPLAY * 100)}%"

    if not has_pick:
        reason_lines = {
            "no_candidates_passed_gates": "Nothing cleared the V5.3 gates. Do nothing today.",
            "regime_fail_closed": "VIX or VIX3M missing — engine is standing down.",
            "vix_backwardation": "VIX > VIX3M (backwardation). Engine skipped today.",
            "earnings_overlap_all_candidates": "All top candidates report earnings during the hold window. Engine skipped today.",
            "earnings_calendar_unavailable": "Earnings calendar unavailable — engine is standing down (fail-closed).",
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
    return (
        f"*GammaRips — {entry_day.isoformat()}*\n"
        f"*{ticker} {direction}*\n"
        f"`{contract}`\n"
        f"Strike {strike} · DTE {dte} · Mid {mid_str} · V/OI {vol_oi_str} · {money_str}\n\n"
        f"Why we picked it: {signal_url}\n\n"
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


def format_email_html(row: pd.Series, target_date: date, entry_day: date) -> str:
    """V5.3 email: one signal, one routine. Mirrors CHEAT-SHEET.md."""
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
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 560px;">
      <h2 style="margin-bottom: 0;">GammaRips Signal — {entry_day}</h2>
      <p style="color: #666; margin-top: 4px;">V5.3 Target 80 · scan {target_date}</p>

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
    AND ``policy_version = 'V5_3_TARGET_80'`` AND closed (realized_return_pct
    not null). Pre-cohort rows were truncated 2026-05-06 — they were generated
    under pre-audit filters and don't form a clean baseline.

    Webapp reads this Firestore doc directly for the public live-stats panel.
    Failures NEVER raise — a stats-write blow-up must not affect the operator
    email path. Returns True on success, False on any failure.
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query = f"""
        SELECT
          COUNT(*) AS trades_closed,
          COUNTIF(realized_return_pct > 0) AS trades_won,
          COALESCE(SAFE_DIVIDE(COUNTIF(realized_return_pct > 0), COUNT(*)), 0) AS win_rate,
          COALESCE(SUM(entry_price * 100), 0) AS total_invested_usd,
          COALESCE(SUM(entry_price * 100 * realized_return_pct), 0) AS total_pl_usd,
          COALESCE(SAFE_DIVIDE(SUM(entry_price * 100 * realized_return_pct), SUM(entry_price * 100)), 0) AS roi_pct
        FROM `{PROJECT_ID}.profit_scout.forward_paper_ledger`
        WHERE DATE(entry_timestamp) >= "{LIVE_COHORT_START_DATE}"
          AND policy_version = "V5_3_TARGET_80"
          AND realized_return_pct IS NOT NULL
        """
        rows = list(client.query(query).result())
        r = rows[0] if rows else None

        stats = {
            "cohort_start": LIVE_COHORT_START_DATE,
            "policy_version": "V5_3_TARGET_80",
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


def run_notifier(target_date: date | None = None):
    if not target_date:
        target_date = get_previous_trading_day(datetime.now(est).date())

    logger.info(f"Running V5.3 Signal Notifier for scan_date={target_date}")

    # Refresh public cohort stats once per run. Independent of the day's
    # pick / skip outcome — the panel reflects ledger state, not today's
    # decision. Non-fatal: a stats blow-up never affects the email path.
    compute_and_write_cohort_stats()

    client = bigquery.Client(project=PROJECT_ID)

    # V5.3 filter stack. The ranker leads with DIRECTIONAL volume_oi_ratio
    # (call_vol_oi_ratio for BULLISH, put_vol_oi_ratio for BEARISH) — i.e.,
    # the strongest unusual-flow imbalance in the trade direction.
    #
    # Why this ORDER BY (changed 2026-05-01, see DECISIONS):
    # The previous primary key was directional dollar volume (biggest UOA wins).
    # EDA on N=435 V5.3 trades showed dollar volume NEGATIVELY correlates with
    # winning at the -60/+80/3-day bracket: bigger flows lose more often. Top-1
    # win-rate by ranker (10 V5.3 days): directional V/OI DESC = 8/10 (80%);
    # old dollar-volume primary = 1/6 (17%) — held in walk-forward halves
    # (4/5 + 4/5). Switching the primary key flips the sign on the lead signal.
    #
    # Tiebreakers: tighter spread (cleaner fills) -> overnight_score (composite
    # signal strength) -> ticker (alphabetical, deterministic). COALESCE keeps
    # rows with NULL directional V/OI participating instead of going first.
    query = f"""
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
      AND recommended_expiration IS NOT NULL
      AND volume_oi_ratio IS NOT NULL
      AND volume_oi_ratio > {VOL_OI_MIN}
      AND moneyness_pct IS NOT NULL
      AND moneyness_pct BETWEEN {MONEYNESS_MIN} AND {MONEYNESS_MAX}
      AND vix3m_at_enrich IS NOT NULL
      AND recommended_oi >= {OI_MIN}
      AND recommended_volume >= {VOL_MIN}
    ORDER BY
        COALESCE(
            CASE WHEN direction = 'BULLISH' THEN call_vol_oi_ratio
                 ELSE put_vol_oi_ratio END,
            0
        ) DESC,
        recommended_spread_pct ASC,
        overnight_score DESC,
        ticker ASC
    LIMIT 10
    """
    # LIMIT 10 (was LIMIT 1) — earnings-overlap exclusion (2026-05-06) walks
    # the ranked list and takes the first ticker NOT reporting in the hold
    # window. If rank-1 has earnings we fall to rank-2, etc. If all 10 are
    # earnings-overlap the day is skipped (skip_reason=earnings_overlap_all_candidates).

    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        logger.error(f"Failed to query BigQuery: {e}")
        return False, f"Error querying BQ: {e}"

    logger.info(f"Post-filter candidates: {len(df)} for {target_date}")

    if len(df) == 0:
        logger.info("No eligible V5.3 signal for this scan_date. No email sent.")
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

    top = None
    skipped_for_earnings: list[str] = []
    for _, candidate in df.iterrows():
        ticker = str(candidate["ticker"]).upper()
        if ticker in earnings_tickers:
            skipped_for_earnings.append(ticker)
            continue
        top = candidate
        break

    if top is None:
        logger.info(
            f"All {len(df)} top-ranked candidates report earnings in [{entry_day}, {exit_day}]. "
            f"Skipped tickers: {skipped_for_earnings}"
        )
        write_todays_pick_doc(target_date, has_pick=False, skip_reason="earnings_overlap_all_candidates")
        post_to_openclaw(format_whatsapp_message(
            None, target_date, None, has_pick=False, skip_reason="earnings_overlap_all_candidates"
        ))
        return True, "All top candidates have earnings overlap. Skipped."

    if skipped_for_earnings:
        logger.info(
            f"Earnings exclusion: skipped {len(skipped_for_earnings)} candidates "
            f"({skipped_for_earnings}); selected {top['ticker']} (rank {len(skipped_for_earnings) + 1})."
        )

    # Happy path: write todays_pick doc BEFORE sending email. Fail-closed —
    # if the Firestore write raises, we do NOT send an email (the operator
    # would see email-without-webapp state and that's the exact drift we're
    # preventing with the single-source-of-truth contract).
    write_todays_pick_doc(target_date, has_pick=True, top=top, vix_now=vix_now)

    html_content = format_email_html(top, target_date, entry_day)
    subject = f"GammaRips {entry_day}: {top['ticker']} {top['direction']}"

    success = send_email(subject, html_content)

    # WhatsApp push is non-blocking and runs whether or not email succeeded —
    # it's an independent fan-out to a different channel, not a retry path.
    post_to_openclaw(format_whatsapp_message(top, target_date, entry_day, has_pick=True))

    # Paid subscriber fan-out — additive, non-blocking. Operator notification
    # above is always primary; subscriber failures must never affect the
    # return code or the operator path.
    try:
        fan_out_count = fan_out_to_paid_subscribers(subject, html_content)
    except Exception as e:
        logger.error(f"Subscriber fan-out blew up (non-fatal): {e}")
        fan_out_count = 0

    if success:
        return True, (
            f"Emailed top V5.3 signal: {top['ticker']} {top['direction']} "
            f"(operator + {fan_out_count} subscribers)."
        )
    return False, "Failed to send operator email."


@app.route("/refresh_stats", methods=["POST"])
def refresh_stats():
    """Ad-hoc seed / recovery for ``cohort_stats/current``.

    Safe to curl any time. Does NOT send email or WhatsApp; only refreshes
    the public-stats Firestore doc. Used post-deploy to seed the empty-state
    doc and any time the operator wants to force a refresh outside the
    daily cron cadence.
    """
    ok = compute_and_write_cohort_stats()
    if ok:
        return jsonify({"status": "success", "message": "cohort_stats/current refreshed."}), 200
    return jsonify({"status": "error", "message": "cohort_stats refresh failed; check logs."}), 500


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
