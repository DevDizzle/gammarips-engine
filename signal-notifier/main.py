import os
import json
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta, date
import pytz
import pandas_market_calendars as mcal
from google.cloud import bigquery
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "profitscout-fida8"
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN", "").strip()
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY", "").strip()
MAILGUN_SENDER = f"GammaRips Engine <mailgun@{MAILGUN_DOMAIN}>"
RECIPIENT_EMAIL = "eraphaelparra@gmail.com"

nyse = mcal.get_calendar("NYSE")
est = pytz.timezone("America/New_York")

def get_previous_trading_day(base_date: date) -> date:
    start_date = base_date - timedelta(days=10)
    schedule = nyse.schedule(start_date=start_date, end_date=base_date)
    valid_dates = [d.date() for d in schedule.index if d.date() < base_date]
    return valid_dates[-1] if valid_dates else None

def send_email(subject, html_content):
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        logger.error("Mailgun credentials not set. Cannot send email.")
        return False
        
    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": MAILGUN_SENDER,
        "to": [RECIPIENT_EMAIL],
        "subject": subject,
        "html": html_content
    }
    
    try:
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()
        logger.info(f"Successfully sent email to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e} - Response: {getattr(response, 'text', '')}")
        return False

def format_email_html(df, target_date):
    html = f"<h2>GammaRips Sniper Signals for {target_date}</h2>"
    html += "<p>The following contracts met the strict execution criteria (Premium Score &ge; 2 and adequate liquidity):</p>"
    
    html += '<table border="1" style="border-collapse: collapse; padding: 5px; text-align: left;">'
    html += "<tr style='background-color: #f2f2f2;'><th>Ticker</th><th>Direction</th><th>Contract</th><th>DTE</th><th>Volume</th><th>OI</th><th>Premium Score</th></tr>"
    
    for _, row in df.iterrows():
        html += f"<tr>"
        html += f"<td style='padding: 5px;'><strong>{row['ticker']}</strong></td>"
        
        color = "green" if row['direction'] == "BULLISH" else "red"
        html += f"<td style='color: {color}; padding: 5px;'><strong>{row['direction']}</strong></td>"
        
        html += f"<td style='padding: 5px;'>{row['recommended_contract']}</td>"
        html += f"<td style='padding: 5px;'>{row['recommended_dte']}</td>"
        html += f"<td style='padding: 5px;'>{row['recommended_volume']}</td>"
        html += f"<td style='padding: 5px;'>{row['recommended_oi']}</td>"
        html += f"<td style='padding: 5px;'>{row['premium_score']}</td>"
        html += f"</tr>"
        
    html += "</table>"
    html += "<br><p><em>May the gamma be with you.</em></p>"
    return html

def run_notifier(target_date: date = None):
    if not target_date:
        # Default logic for target date (last scan date)
        target_date = get_previous_trading_day(datetime.now(est).date())
        
    logger.info(f"Running Signal Notifier for signals generated on {target_date}")
    
    client = bigquery.Client(project=PROJECT_ID)
    
    query = f"""
    SELECT 
        ticker, scan_date, direction, recommended_contract, recommended_strike, 
        recommended_expiration, recommended_dte, recommended_volume, recommended_oi, 
        premium_score
    FROM `{PROJECT_ID}.profit_scout.overnight_signals_enriched`
    WHERE DATE(scan_date) = "{target_date}"
      AND premium_score >= 2
      AND (
            (recommended_volume >= 100 AND recommended_oi >= 50)
            OR recommended_oi >= 250
      )
      AND recommended_strike IS NOT NULL
      AND recommended_expiration IS NOT NULL
    """
    
    try:
        df = client.query(query).to_dataframe()
    except Exception as e:
        logger.error(f"Failed to query BigQuery: {e}")
        return False, f"Error querying BQ: {e}"
        
    logger.info(f"Found {len(df)} eligible signals for {target_date}")
    
    if len(df) == 0:
        logger.info("No eligible signals found. Skipping email.")
        return True, "No eligible signals found. No email sent."
        
    # Deduplicate signals
    df = df.sort_values(by=["premium_score", "recommended_volume"], ascending=[False, False])
    # Convert scan_date to string for deduplication to work properly with BQ datetime objects
    df['scan_date_str'] = df['scan_date'].astype(str)
    df = df.drop_duplicates(subset=["ticker", "scan_date_str"])
    
    html_content = format_email_html(df, target_date)
    subject = f"GammaRips Sniper Alert: {len(df)} New Signals ({target_date})"
    
    success = send_email(subject, html_content)
    if success:
        return True, f"Successfully emailed {len(df)} signals."
    else:
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
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        logger.error(f"Error in signal-notifier endpoint: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
