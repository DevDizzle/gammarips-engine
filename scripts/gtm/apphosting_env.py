#!/usr/bin/env python3
"""Inspect and edit the Firebase App Hosting backend's console env vars.

These are the `overrideEnv` entries on the backend resource. They are what the
Firebase Console "Environment variables" screen writes, and they MERGE with
`apphosting.yaml` at build time. Two things make them dangerous:

1. **An entry with an empty value breaks every deploy.** The preparer emits an
   env entry with neither `value:` nor `secret:` and the build rejects the whole
   config with `fah/invalid-apphosting-yaml: either 'value' or 'secret' field is
   required`. The error names `apphosting_preprocessed`, so it reads as a repo
   problem and is not one. `RECONCILE_CRON_SECRET` did this on 2026-08-31 and
   killed every build regardless of commit.
2. **Every plain value is printed in the Cloud Build log in cleartext**,
   including the Stripe LIVE secret key. Anyone with build-log access reads
   them. The fix is to declare the var in `apphosting.yaml` under `env:` as
   `variable:` + `secret:` (RUNTIME only) and DELETE the console row.

This script never prints a value. `--list` shows lengths, `--compare` shows
sha256 prefixes.

Usage:
    python scripts/gtm/apphosting_env.py --list
    python scripts/gtm/apphosting_env.py --compare RECONCILE_CRON_SECRET
    python scripts/gtm/apphosting_env.py --delete RECONCILE_CRON_SECRET
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys

import google.auth
import requests
from google.auth.transport.requests import Request

PROJECT = "profitscout-fida8"
LOCATION = "us-central1"
BACKEND = "gammarips-webapp"
BASE = "https://firebaseapphosting.googleapis.com/v1beta"
URL = f"{BASE}/projects/{PROJECT}/locations/{LOCATION}/backends/{BACKEND}"


def _headers() -> dict:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(Request())
    return {"Authorization": f"Bearer {creds.token}"}


def get_backend() -> dict:
    r = requests.get(URL, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw.strip()).hexdigest()[:16]


def list_env() -> None:
    b = get_backend()
    entries = b.get("overrideEnv", [])
    print(f"backend {BACKEND}: {len(entries)} console env vars")
    print(f"{'variable':40s} {'kind':12s} {'len':>5s}  note")
    for e in entries:
        name = e.get("variable", "")
        if "secret" in e:
            print(f"{name:40s} {'secret-ref':12s} {'-':>5s}  {e['secret']}")
            continue
        v = e.get("value")
        n = 0 if v is None else len(v)
        note = "EMPTY -> BREAKS EVERY DEPLOY" if n == 0 else "plaintext in build logs"
        print(f"{name:40s} {'value':12s} {n:>5d}  {note}")


def compare(name: str) -> None:
    """Does Secret Manager hold the same value as the console row?"""
    b = get_backend()
    hit = [e for e in b.get("overrideEnv", []) if e.get("variable") == name]
    if not hit:
        sys.exit(f"{name} is not a console env var on this backend")
    console = (hit[0].get("value") or "").encode()
    proc = subprocess.run(
        [
            "gcloud", "secrets", "versions", "access", "latest",
            f"--secret={name}", f"--project={PROJECT}",
        ],
        capture_output=True,
    )
    print(f"{name}:")
    print(f"  console        len={len(console.strip())} sha256={_digest(console)}")
    if proc.returncode != 0:
        print("  secret manager NOT FOUND — create it before deleting the console row")
        return
    sm = proc.stdout
    print(f"  secret manager len={len(sm.strip())} sha256={_digest(sm)}")
    if not console.strip():
        # e3b0c442... is sha256 of the empty string. An empty console row holds
        # nothing to preserve AND is the thing that breaks every deploy, so
        # "mismatch" here is not a warning, it is the reason to delete.
        print(
            "  console row is EMPTY. Nothing to preserve, and an empty row breaks\n"
            "  every deploy. Delete it once apphosting.yaml sources the value."
        )
    elif _digest(console) == _digest(sm):
        print("  MATCH — safe to move to apphosting.yaml and delete the console row")
    else:
        print("  MISMATCH — do NOT delete the console row until this is resolved")


def delete(name: str) -> None:
    b = get_backend()
    entries = b.get("overrideEnv", [])
    if not any(e.get("variable") == name for e in entries):
        sys.exit(f"{name} is not present; nothing to do")
    kept = [e for e in entries if e.get("variable") != name]
    # PATCH replaces the whole list, so every other entry is sent back
    # unchanged. Values pass through this process to the API and are never
    # printed or written to disk.
    body = {"overrideEnv": kept}
    r = requests.patch(
        URL,
        headers=_headers(),
        params={"updateMask": "overrideEnv"},
        json=body,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        try:
            msg = r.json().get("error", {}).get("message", "")
        except Exception:
            msg = r.text[:300]
        sys.exit(f"patch failed HTTP {r.status_code}: {msg}")
    print(f"removed {name}. console env vars: {len(entries)} -> {len(kept)}")
    print("App Hosting reconciles the backend; the next build uses the new config.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--compare", metavar="VAR")
    ap.add_argument("--delete", metavar="VAR")
    a = ap.parse_args()
    if a.compare:
        compare(a.compare)
    elif a.delete:
        delete(a.delete)
    else:
        list_env()


if __name__ == "__main__":
    main()
