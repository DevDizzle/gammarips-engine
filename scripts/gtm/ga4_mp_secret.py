#!/usr/bin/env python3
"""Manage the GA4 Measurement Protocol API secret for the GammaRips web stream.

Background (2026-08-29 diagnosis, `~/workspace/GAMMARIPS-GA4-ATTRIBUTION-FIX.txt`):
no `purchase` event has ever reached GA4 property 534472819. Client-side gtag
events land; every server-side Measurement Protocol call is silently dropped.
The measurement id and the webhook are both correct. The stored `GA_API_SECRET`
is not valid for stream G-ZF0DQVQEKJ, proven by re-sending a test event with
live credentials: debug validator clean, /mp/collect 204, absent from Realtime.
A 204 and a clean debug response are NOT ingestion proof. Realtime is.

This script mints a replacement secret through the GA4 Admin API and writes it
straight into Secret Manager. **The secret value is never printed.** It goes
from the API response into Secret Manager and nowhere else.

Auth: service-account impersonation, same as scripts/seo/. Needs the
analytics.edit scope and Editor on the GA4 property.

    export SEO_IMPERSONATE_SA=ga-admin@profitscout-fida8.iam.gserviceaccount.com

Usage:
    python scripts/gtm/ga4_mp_secret.py --list
    python scripts/gtm/ga4_mp_secret.py --create --write-secret
    python scripts/gtm/ga4_mp_secret.py --acknowledge   # owner-authorized only
    python scripts/gtm/ga4_mp_secret.py --delete <secret_id>
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

import google.auth
import requests
from google.auth import impersonated_credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/analytics.edit"]
PROPERTY = os.environ.get("GA4_PROPERTY_ID", "534472819")
STREAM = os.environ.get("GA4_STREAM_ID", "14531024465")  # G-ZF0DQVQEKJ
GCP_PROJECT = "profitscout-fida8"
SECRET_NAME = "GA_API_SECRET"
BASE = "https://analyticsadmin.googleapis.com/v1beta"
PARENT = f"properties/{PROPERTY}/dataStreams/{STREAM}"


def token() -> str:
    source, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    target = os.environ.get(
        "SEO_IMPERSONATE_SA", "ga-admin@profitscout-fida8.iam.gserviceaccount.com"
    )
    creds = impersonated_credentials.Credentials(
        source_credentials=source,
        target_principal=target,
        target_scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds.token


def _headers() -> dict:
    return {"Authorization": f"Bearer {token()}"}


def list_secrets() -> list[dict]:
    r = requests.get(
        f"{BASE}/{PARENT}/measurementProtocolSecrets", headers=_headers(), timeout=30
    )
    r.raise_for_status()
    return r.json().get("measurementProtocolSecrets", [])


def show(secrets: list[dict]) -> None:
    """Print metadata only. Never the value."""
    print(f"stream {PARENT}")
    print(f"existing Measurement Protocol secrets: {len(secrets)}")
    for s in secrets:
        value = s.get("secretValue") or ""
        print(
            f"  id={s['name'].rsplit('/', 1)[-1]}  "
            f"display={s.get('displayName','')!r}  "
            f"value=<{len(value)} chars, hidden>"
        )


# The exact string the Admin API requires. It is a legal representation by the
# property owner, so this is never sent without the owner saying so. Evan
# authorized it explicitly on 2026-08-31 after being shown this wording, which
# is why the acknowledgement is a separate opt-in flag and not part of --create.
ACK_TEXT = (
    "I acknowledge that I have the necessary privacy disclosures and rights "
    "from my end users for the collection and processing of their data, "
    "including the association of such data with the visitation information "
    "Google Analytics collects from my site and/or app property."
)


def acknowledge() -> None:
    """Attest the User Data Collection Acknowledgement on the property.

    Without this, `measurementProtocolSecrets.create` returns
    FAILED_PRECONDITION and NO secret can exist on any stream. That was the
    real root cause of four months of dropped purchase events: the property
    was never attested, so the value stored in Secret Manager on 2026-02-02
    could not have been a valid Measurement Protocol secret.
    """
    r = requests.post(
        f"{BASE}/properties/{PROPERTY}:acknowledgeUserDataCollection",
        headers=_headers(),
        json={"acknowledgement": ACK_TEXT},
        timeout=30,
    )
    if r.status_code != 200:
        err = {}
        try:
            err = r.json().get("error", {})
        except Exception:
            pass
        sys.exit(
            f"acknowledge failed HTTP {r.status_code}: "
            f"{err.get('status','')} {err.get('message', r.text[:200])}"
        )
    print(f"User Data Collection Acknowledgement attested on properties/{PROPERTY}")


def create(display_name: str) -> str:
    r = requests.post(
        f"{BASE}/{PARENT}/measurementProtocolSecrets",
        headers=_headers(),
        json={"displayName": display_name},
        timeout=30,
    )
    if r.status_code != 200:
        # Error bodies carry no secret, so they are safe to surface. A success
        # body DOES carry one and is never printed.
        try:
            err = r.json().get("error", {})
            detail = f"{err.get('status','')}: {err.get('message','')}"
            for d in err.get("details", []):
                for v in d.get("fieldViolations", []):
                    detail += f"\n  field={v.get('field')} -> {v.get('description')}"
        except Exception:
            detail = r.text[:300]
        sys.exit(f"create failed HTTP {r.status_code}\n{detail}")
    body = r.json()
    print(f"created id={body['name'].rsplit('/', 1)[-1]} display={display_name!r}")
    return body["secretValue"]


def write_to_secret_manager(value: str) -> None:
    """Pipe the value straight to gcloud on stdin. Never on the command line."""
    proc = subprocess.run(
        [
            "gcloud",
            "secrets",
            "versions",
            "add",
            SECRET_NAME,
            f"--project={GCP_PROJECT}",
            "--data-file=-",
        ],
        input=value.encode(),
        capture_output=True,
    )
    if proc.returncode != 0:
        # stderr can echo input on some failures; print only the last line.
        tail = proc.stderr.decode().strip().splitlines()
        print(f"secret-manager write FAILED: {tail[-1] if tail else '?'}", file=sys.stderr)
        raise SystemExit(1)
    print(f"wrote a new version of {SECRET_NAME} in {GCP_PROJECT}")


def delete(secret_id: str) -> None:
    r = requests.delete(
        f"{BASE}/{PARENT}/measurementProtocolSecrets/{secret_id}",
        headers=_headers(),
        timeout=30,
    )
    r.raise_for_status()
    print(f"deleted {secret_id}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--create", action="store_true")
    ap.add_argument(
        "--display-name",
        default="gammarips-webapp-server",
        help="label shown in the GA4 admin UI",
    )
    ap.add_argument(
        "--write-secret",
        action="store_true",
        help=f"write the new value to Secret Manager {SECRET_NAME} (required with --create)",
    )
    ap.add_argument("--delete", metavar="SECRET_ID")
    ap.add_argument(
        "--acknowledge",
        action="store_true",
        help="attest the User Data Collection Acknowledgement (owner-authorized only)",
    )
    a = ap.parse_args()

    if a.delete:
        delete(a.delete)
        return
    if a.acknowledge:
        acknowledge()
        if not a.create:
            return
    if a.create:
        if not a.write_secret:
            sys.exit(
                "refusing to create without --write-secret: the value would have "
                "nowhere safe to go and this script never prints it."
            )
        value = create(a.display_name)
        write_to_secret_manager(value)
        print("\nNEXT: the value is in Secret Manager only. It was never printed.")
        print("Redeploy the webapp so it picks up the new version, then verify in")
        print("GA4 Realtime. A 204 from /mp/collect is NOT proof.")
        return
    show(list_secrets())


if __name__ == "__main__":
    main()
