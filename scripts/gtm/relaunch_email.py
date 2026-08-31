#!/usr/bin/env python3
"""Relaunch email to the dormant Firestore `users` list. Dry run by default.

Usage:
  python scripts/gtm/relaunch_email.py                 # dry run: count + CSV, no send
  python scripts/gtm/relaunch_email.py --test you@x    # send ONE copy to you
  python scripts/gtm/relaunch_email.py --send          # send to the list (needs MAILGUN_API_KEY)

The subject and body live in ~/workspace/GAMMARIPS-RELAUNCH-EMAIL.txt below the
dashed "Subject:" line. The script refuses to send if the compliance rubric
fails. The owner sends: nothing leaves without --send or --test.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "profitscout-fida8"  # explicit: the shell PROJECT_ID footgun points elsewhere
DOMAIN = os.environ.get("MAILGUN_DOMAIN", "mg.gammarips.com")
FROM = "Evan Parra <evan@gammarips.com>"
TAG = "relaunch-2026-08"
DRAFT = Path.home() / "workspace" / "GAMMARIPS-RELAUNCH-EMAIL.txt"
OUT_CSV = Path.home() / "workspace" / "GAMMARIPS-RELAUNCH-RECIPIENTS.csv"
EXCLUDE_DOMAINS = {"evanparra.ai", "profitscout.app"}
LIB = Path(__file__).resolve().parents[2] / "libs" / "gammarips_content"


def load_draft() -> tuple[str, str]:
    text = DRAFT.read_text()
    m = re.search(r"^Subject: (.+)$\n-+\n(.*)\Z", text, re.M | re.S)
    if not m:
        sys.exit(f"cannot parse subject/body from {DRAFT}")
    return m.group(1).strip(), m.group(2).strip() + "\n"


def compliance_ok(body: str) -> bool:
    sys.path.insert(0, str(LIB))
    try:
        from gammarips_content.compliance import (
            rubric_to_reviewer_notes,
            score_against_rubric,
        )
    except Exception as e:  # pragma: no cover
        print(f"compliance lib unavailable ({e}); refusing to send", file=sys.stderr)
        return False
    res = score_against_rubric(body, post_type="email", is_blog=True)
    print(rubric_to_reviewer_notes(res))
    return bool(res.passed)


def recipients() -> list[dict]:
    from google.cloud import firestore

    db = firestore.Client(project=PROJECT)
    now = datetime.now(timezone.utc)
    seen: set[str] = set()
    rows: list[dict] = []
    for u in db.collection("users").stream():
        d = u.to_dict() or {}
        email = (d.get("email") or "").strip().lower()
        if not email or "@" not in email:
            continue
        local, dom = email.split("@", 1)
        if email.endswith(".com.com") or "test" in local or dom in EXCLUDE_DOMAINS:
            continue
        if email in seen:
            continue
        pu = d.get("proUntil")
        if pu is not None and hasattr(pu, "timestamp") and pu > now:
            continue  # already Pro today
        seen.add(email)
        ca = d.get("createdAt")
        rows.append({
            "email": email,
            "uid": u.id,
            "plan": d.get("plan") or "",
            "created": ca.date().isoformat() if hasattr(ca, "date") else "",
        })
    return rows


def send(to: list[str], subject: str, body: str) -> tuple[int, int]:
    import requests

    key = os.environ.get("MAILGUN_API_KEY", "").strip()
    if not key:
        sys.exit("MAILGUN_API_KEY is not set")
    sent = failed = 0
    for i in range(0, len(to), 500):  # Mailgun batch cap is 1000, keep margin
        chunk = to[i:i + 500]
        r = requests.post(
            f"https://api.mailgun.net/v3/{DOMAIN}/messages",
            auth=("api", key),
            data={
                "from": FROM,
                "to": chunk,
                "subject": subject,
                "text": body,
                "o:tag": TAG,
                # Click tracking OFF (2026-08-31). Mailgun rewrites every URL in
                # the body, which broke the one thing the email exists for: the
                # `claude mcp add ... https://mcp.gammarips.com/mcp` line became
                # an http:// email.mg.gammarips.com/c/<token> redirect that no
                # MCP client can use. Open tracking needs an HTML part to hold
                # the pixel and this message is text/plain, so it never worked
                # either. Delivery and bounce stats still come from o:tag.
                # Attribution is the utm_source on the site links instead.
                "o:tracking": "no",
                "o:tracking-clicks": "no",
                "h:Reply-To": "evan@gammarips.com",
                "h:List-Unsubscribe": "<mailto:evan@gammarips.com?subject=unsubscribe>",
                "recipient-variables": "{" + ",".join(f'"{e}":{{}}' for e in chunk) + "}",
            },
            timeout=60,
        )
        if r.ok:
            sent += len(chunk)
        else:
            failed += len(chunk)
            print(f"batch failed: {r.status_code} {r.text[:200]}", file=sys.stderr)
    return sent, failed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true", help="send to the list")
    ap.add_argument("--test", metavar="EMAIL", help="send one copy to EMAIL only")
    ap.add_argument("--limit", type=int, default=0, help="cap recipients (testing)")
    a = ap.parse_args()

    subject, body = load_draft()
    if not compliance_ok(body):
        sys.exit("compliance rubric FAILED, fix the draft first")

    if a.test:
        s, f = send([a.test], subject, body)
        print(f"sent {s} test message to {a.test} (failed {f})")
        return

    rows = recipients()
    if a.limit:
        rows = rows[: a.limit]
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["email", "uid", "plan", "created"])
        w.writeheader()
        w.writerows(rows)
    print(f"recipients: {len(rows)} (written to {OUT_CSV})")
    if not a.send:
        print("dry run. Add --send to deliver, or --test EMAIL for one copy.")
        return
    s, f = send([r["email"] for r in rows], subject, body)
    print(f"sent {s}, failed {f}")


if __name__ == "__main__":
    main()
