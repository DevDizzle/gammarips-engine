#!/usr/bin/env python3
"""Send one test `purchase` event to GA4 Measurement Protocol, then check Realtime.

The payload mirrors `src/app/api/stripe/webhook/route.ts` in the webapp so this
exercises the same path production uses.

READ THIS BEFORE TRUSTING A RESULT: `/mp/collect` returns **204 for every
payload**, valid or not, and `/debug/mp/collect` validates the schema without
ingesting. Neither is proof. Four months of dropped purchase events hid behind
exactly those two green lights. **GA4 Realtime is the only ground truth**, and
this script checks it for you.

The secret is read from Secret Manager and never printed.

Usage:
    python scripts/gtm/ga4_mp_verify.py            # send, then poll Realtime
    python scripts/gtm/ga4_mp_verify.py --check    # poll Realtime only
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import uuid

import requests

PROJECT = "profitscout-fida8"
SECRET_NAME = "GA_API_SECRET"
MEASUREMENT_ID = "G-ZF0DQVQEKJ"
PROPERTY_ID = "534472819"


def api_secret() -> str:
    """Latest secret version, stripped. Mounted/echoed values carry a newline,
    and a newline in a query string silently invalidates the credential."""
    proc = subprocess.run(
        [
            "gcloud", "secrets", "versions", "access", "latest",
            f"--secret={SECRET_NAME}", f"--project={PROJECT}",
        ],
        capture_output=True,
    )
    if proc.returncode != 0:
        tail = proc.stderr.decode().strip().splitlines()
        sys.exit(f"could not read {SECRET_NAME}: {tail[-1] if tail else '?'}")
    value = proc.stdout.decode().strip()
    if not value:
        sys.exit(f"{SECRET_NAME} is empty")
    print(f"read {SECRET_NAME} from Secret Manager ({len(value)} chars, hidden)")
    return value


def send(txn_id: str, client_id: str) -> None:
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "purchase",
                "params": {
                    "transaction_id": txn_id,
                    "value": 29.0,
                    "currency": "USD",
                    "engagement_time_msec": 1,
                    "items": [
                        {
                            "item_id": "mp_verification",
                            "item_name": "GammaRips Pro Subscription",
                            "price": 29.0,
                            "quantity": 1,
                        }
                    ],
                },
            }
        ],
    }
    r = requests.post(
        "https://www.google-analytics.com/mp/collect",
        params={"measurement_id": MEASUREMENT_ID, "api_secret": api_secret()},
        json=payload,
        timeout=30,
    )
    # Deliberately not treated as success. 204 means nothing here.
    print(f"POST /mp/collect -> HTTP {r.status_code} (this proves NOTHING)")
    print(f"transaction_id={txn_id}")


def realtime_purchases() -> int:
    """Purchase events GA4 Realtime has actually ingested in the last 30 min."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        Dimension,
        Filter,
        FilterExpression,
        Metric,
        RunRealtimeReportRequest,
    )

    # Plain user ADC cannot hold the Analytics scopes any more (Google blocked
    # the shared gcloud client id, 2026-08-08). Impersonate, same as scripts/seo.
    import os

    import google.auth
    from google.auth import impersonated_credentials

    scopes = ["https://www.googleapis.com/auth/analytics.readonly"]
    source, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds = impersonated_credentials.Credentials(
        source_credentials=source,
        target_principal=os.environ.get(
            "SEO_IMPERSONATE_SA",
            "ga-admin@profitscout-fida8.iam.gserviceaccount.com",
        ),
        target_scopes=scopes,
    )
    client = BetaAnalyticsDataClient(credentials=creds)
    resp = client.run_realtime_report(
        RunRealtimeReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount")],
            dimension_filter=FilterExpression(
                filter=Filter(
                    field_name="eventName",
                    string_filter=Filter.StringFilter(value="purchase"),
                )
            ),
        )
    )
    return sum(int(r.metric_values[0].value or 0) for r in resp.rows)


def poll(attempts: int = 10, delay: int = 15) -> bool:
    for i in range(1, attempts + 1):
        try:
            n = realtime_purchases()
        except Exception as exc:  # noqa: BLE001
            print(f"  [{i}/{attempts}] realtime query failed: {exc}")
            n = 0
        if n > 0:
            print(f"\nINGESTED. GA4 Realtime reports {n} purchase event(s).")
            return True
        print(f"  [{i}/{attempts}] no purchase event in Realtime yet ...")
        if i < attempts:
            time.sleep(delay)
    print("\nNOT INGESTED. Realtime never saw it. The secret or the wiring is wrong.")
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="poll Realtime only")
    a = ap.parse_args()
    if not a.check:
        send(f"mp-verify-{uuid.uuid4().hex[:10]}", f"{uuid.uuid4().int >> 96}.{int(time.time())}")
    sys.exit(0 if poll() else 1)


if __name__ == "__main__":
    main()
