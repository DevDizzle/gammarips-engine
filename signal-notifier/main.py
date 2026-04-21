"""Signal Notifier — V5.3 Target 80

Reads `overnight_signals_enriched` for the target scan_date, applies the V5.3
filter stack, and sends at most one email with the single top-ranked signal.

Filters applied here (in addition to whatever enrichment already enforced):
  - ``volume_oi_ratio > 2.0``                 fresh flow, not stale OI
  - ``moneyness_pct BETWEEN 0.05 AND 0.15``   5-15% OTM sweet spot
  - ``vix3m_at_enrich`` present AND ``VIX <= VIX3M`` (no backwardation)
        Fail-closed: a NULL vix3m_at_enrich or a missing current VIX means we
        skip the email for the day entirely.
  - ``LIMIT 1`` ranked by directional UOA dollar volume

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
MONEYNESS_MAX = 0.15

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


def send_email(subject: str, html_content: str) -> bool:
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        logger.error("Mailgun credentials not set. Cannot send email.")
        return False

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": MAILGUN_SENDER,
        "to": [RECIPIENT_EMAIL],
        "subject": subject,
        "html": html_content,
    }

    try:
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()
        logger.info(f"Successfully sent email to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e} - Response: {getattr(response, 'text', '')}")
        return False


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

    return (
        f"*GammaRips — {entry_day.isoformat()}*\n"
        f"*{ticker} {direction}*\n"
        f"`{contract}`\n"
        f"Strike {strike} · DTE {dte} · Mid {mid_str} · V/OI {vol_oi_str} · {money_str}\n\n"
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

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 560px;">
      <h2 style="margin-bottom: 0;">GammaRips Signal — {entry_day}</h2>
      <p style="color: #666; margin-top: 4px;">V5.3 Target 80 · scan {target_date}</p>

      <div style="padding: 12px 16px; border: 2px solid {color}; border-radius: 6px; margin: 12px 0;">
        <div style="font-size: 22px;"><strong>{ticker}</strong>
          <span style="color: {color}; font-weight: 600;">&nbsp;{direction}</span>
        </div>
        <div style="font-size: 15px; margin-top: 4px;">
          <code>{contract}</code>
        </div>
        <div style="color: #555; margin-top: 6px;">
          Strike {strike} · DTE {dte} · Mid {mid_str} · V/OI {vol_oi_str} · {money_str}
        </div>
      </div>

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


def run_notifier(target_date: date | None = None):
    if not target_date:
        target_date = get_previous_trading_day(datetime.now(est).date())

    logger.info(f"Running V5.3 Signal Notifier for scan_date={target_date}")

    client = bigquery.Client(project=PROJECT_ID)

    # V5.3 filter stack. UOA dollar volume is direction-dependent: call_dollar_volume
    # for BULLISH, put_dollar_volume for BEARISH. Enrichment already gates on
    # spread <= 10%, overnight_score >= 1, and directional UOA > $500k — we
    # layer V5.3's additional quality filters on top and cap to LIMIT 1.
    #
    # The ORDER BY is deterministic: 5-key tiebreaker so `LIMIT 1` always
    # returns the same row given the same input (primary: directional UOA;
    # tiebreakers cascade to overnight_score, vol_oi ratio, tighter spread,
    # then alphabetical ticker). Single-key ORDER BY would non-deterministically
    # pick among rows with identical dollar volume. See exec-plan Phase 1.0.
    query = f"""
    SELECT
        ticker, scan_date, direction,
        recommended_contract, recommended_strike, recommended_expiration,
        recommended_dte, recommended_volume, recommended_oi,
        recommended_mid_price, recommended_spread_pct,
        overnight_score, premium_score,
        call_dollar_volume, put_dollar_volume, call_uoa_depth, put_uoa_depth,
        volume_oi_ratio, moneyness_pct, vix3m_at_enrich
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
      AND volume_oi_ratio IS NOT NULL
      AND volume_oi_ratio > {VOL_OI_MIN}
      AND moneyness_pct IS NOT NULL
      AND moneyness_pct BETWEEN {MONEYNESS_MIN} AND {MONEYNESS_MAX}
      AND vix3m_at_enrich IS NOT NULL
    ORDER BY
        CASE WHEN direction = 'BULLISH' THEN call_dollar_volume
             ELSE put_dollar_volume END DESC,
        overnight_score DESC,
        volume_oi_ratio DESC,
        recommended_spread_pct ASC,
        ticker ASC
    LIMIT 1
    """

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

    top = df.iloc[0]

    # Regime gate: skip the entire day if VIX > VIX3M (backwardation).
    vix3m = top.get("vix3m_at_enrich")
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

    # Happy path: write todays_pick doc BEFORE sending email. Fail-closed —
    # if the Firestore write raises, we do NOT send an email (the operator
    # would see email-without-webapp state and that's the exact drift we're
    # preventing with the single-source-of-truth contract).
    write_todays_pick_doc(target_date, has_pick=True, top=top, vix_now=vix_now)

    entry_day = get_next_trading_day(target_date)

    html_content = format_email_html(top, target_date, entry_day)
    subject = f"GammaRips {entry_day}: {top['ticker']} {top['direction']}"

    success = send_email(subject, html_content)

    # WhatsApp push is non-blocking and runs whether or not email succeeded —
    # it's an independent fan-out to a different channel, not a retry path.
    post_to_openclaw(format_whatsapp_message(top, target_date, entry_day, has_pick=True))

    if success:
        return True, f"Emailed top V5.3 signal: {top['ticker']} {top['direction']}."
    return False, "Failed to send email."


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
