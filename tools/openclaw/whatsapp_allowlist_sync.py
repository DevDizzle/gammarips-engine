"""Sync Firestore ``whatsapp_allowlist`` → OpenClaw ``groupAllowFrom``.

Reads every provisioned Pro subscriber's WhatsApp ``senderId`` (populated manually
when the user joins the group, or via a pairing hook if/when we wire one) and
emits a JSON patch that Evan can drop into ``~/.openclaw/config.json`` at
``channels.whatsapp.groupAllowFrom``.

Run manually for now:

    python whatsapp_allowlist_sync.py --project profitscout-fida8

Or dry-run to just print the pending adds without writing anything:

    python whatsapp_allowlist_sync.py --project profitscout-fida8 --dry-run

The paywall is enforced by OpenClaw's built-in group policy — if a number isn't
on ``groupAllowFrom``, the agent won't respond to @mentions from them. The
subscription webhook already writes the ``whatsapp_allowlist`` doc at
checkout.session.completed; the only manual step is pairing each subscriber's
Stripe record with their WhatsApp ``senderId`` (E.164 phone number).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from google.cloud import firestore


def fetch_allowlist(project_id: str) -> list[str]:
    """Return the list of E.164 numbers provisioned for Pro access.

    Filters out docs with missing ``senderId`` — those are subscribers who paid
    but haven't paired their WhatsApp number yet (user or Evan must populate).
    """
    db = firestore.Client(project=project_id)
    collection = db.collection("whatsapp_allowlist")
    docs = collection.where("status", "==", "provisioned").stream()

    senders: list[str] = []
    missing: list[str] = []
    for doc in docs:
        data = doc.to_dict() or {}
        sender = (data.get("senderId") or "").strip()
        email = data.get("email") or doc.id
        if sender:
            senders.append(sender)
        else:
            missing.append(email)

    if missing:
        print(
            f"[warn] {len(missing)} paid subs are missing senderId: {', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            "[warn] Pair them by editing whatsapp_allowlist/{uid}.senderId in Firestore",
            file=sys.stderr,
        )

    return sorted(set(senders))


def emit_config_patch(senders: list[str]) -> dict:
    """Produce the JSON patch for OpenClaw config."""
    return {
        "channels": {
            "whatsapp": {
                "groupPolicy": "allowlist",
                "groupAllowFrom": senders,
            }
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="profitscout-fida8", help="GCP project ID")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write the config patch JSON (default: stdout)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print and exit")
    args = parser.parse_args()

    senders = fetch_allowlist(args.project)
    print(f"[info] Provisioned + paired subscribers: {len(senders)}", file=sys.stderr)

    patch = emit_config_patch(senders)
    patch_json = json.dumps(patch, indent=2)

    if args.dry_run or args.out is None:
        print(patch_json)
        return 0

    args.out.write_text(patch_json)
    print(f"[info] Wrote config patch to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
