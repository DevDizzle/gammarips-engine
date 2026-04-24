#!/usr/bin/env python
"""
Seed `blog_schedule/current` + `blog_config/voice_rules` in Firestore.

One-shot migration. Idempotent — re-running replaces the rows array but DOES
NOT flip existing published rows back to pending. To force-reset a slug's
status, edit the Firestore doc in console.

Source of truth for the schedule table:
    docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md §6 (13 rows)

Usage:
    cd blog-generator
    uv run python scripts/seed_schedule.py             # writes both docs
    uv run python scripts/seed_schedule.py --dry-run   # print, no write
    uv run python scripts/seed_schedule.py --voice-only   # only voice_rules
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure we can import gammarips_content when running from repo root.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "libs" / "gammarips_content") not in sys.path:
    sys.path.insert(0, str(_ROOT / "libs" / "gammarips_content"))

from gammarips_content import firestore_helpers, voice_rules  # noqa: E402


PROJECT_ID = os.getenv("PROJECT_ID", "profitscout-fida8")

# Schedule version — bump when the rows change.
SCHEDULE_VERSION = "2026-04-24"


# 13 rows from docs/EXEC-PLANS/2026-04-20-copy-seo-content-overhaul.md §6.
# type values map to app/tools.py LIVE_CONTEXT_POST_TYPES for gating.
# cta values: "webapp_visit" | "pro_trial" | "starter_trial"
BLOG_SCHEDULE_ROWS: list[dict] = [
    {
        "slug": "why-uoa-is-mostly-noise",
        "week_num": 1,
        "title_candidate": (
            "Why 'Unusual Options Activity' Is Mostly Noise "
            "(And the One Signal That Isn't)"
        ),
        "persona": ["A", "D"],
        "keywords": [
            "unusual options activity",
            "UOA",
            "volume open interest ratio",
        ],
        "cta": "webapp_visit",
        "type": "evergreen_explainer",
        "cross_channel": ["x_thread", "reddit_options", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "fix-vs-oklo-case-study",
        "week_num": 2,
        "title_candidate": (
            "Why Score Alone Doesn't Pick: The FIX-vs-OKLO 2026-04-17 Case Study"
        ),
        "persona": ["A", "D"],
        "keywords": ["options flow scanner", "stale open interest"],
        "cta": "webapp_visit",
        "type": "case_study",
        "cross_channel": ["x_thread", "reddit_options", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "vix-backwardation-gate",
        "week_num": 3,
        "title_candidate": (
            "VIX Backwardation Is the Easiest Day-Trading Gate You're Not Using"
        ),
        "persona": ["A"],
        "keywords": [
            "VIX VIX3M",
            "volatility term structure",
            "options risk regime",
        ],
        "cta": "webapp_visit",
        "type": "evergreen_explainer",
        "cross_channel": ["x_thread", "reddit_options"],
        "status": "pending",
    },
    {
        "slug": "one-trade-a-day-discipline",
        "week_num": 4,
        "title_candidate": "The Case for One Trade a Day: A Discipline Argument",
        "persona": ["A", "B"],
        "keywords": [
            "options swing trading",
            "one trade a day",
            "overtrading",
        ],
        "cta": "pro_trial",
        "type": "thought_leadership",
        "cross_channel": ["x_thread", "linkedin", "reddit_thetagang"],
        "status": "pending",
    },
    {
        "slug": "institutional-hedging-vs-directional",
        "week_num": 5,
        "title_candidate": (
            "How We Detect Institutional Hedging vs Directional Positioning"
        ),
        "persona": ["D"],
        "keywords": [
            "institutional options hedging",
            "dark pool flow",
            "call put ratio",
        ],
        "cta": "webapp_visit",
        "type": "methodology",
        "cross_channel": ["x_thread", "reddit_options", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "moneyness-5-15-otm",
        "week_num": 6,
        "title_candidate": (
            "Moneyness 5-15% OTM: Why We Skip Both ATM Gamma and Deep Lottery"
        ),
        "persona": ["A", "D"],
        "keywords": [
            "OTM options moneyness",
            "gamma exposure",
            "theta decay",
        ],
        "cta": "webapp_visit",
        "type": "evergreen_explainer",
        "cross_channel": ["x_thread", "reddit_thetagang"],
        "status": "pending",
    },
    {
        "slug": "whats-pushed-to-my-phone-at-9am",
        "week_num": 7,
        "title_candidate": (
            "What Gets Pushed to My Phone at 9:00 AM (Weekly Engine Recap)"
        ),
        "persona": ["A"],
        "keywords": ["options morning alerts", "9 AM options trade"],
        "cta": "pro_trial",
        "type": "weekly_engine_recap",
        "cross_channel": ["x_thread", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "19-per-month-signal-service",
        "week_num": 8,
        "title_candidate": (
            "A $19/mo Signal Service That Actually Skips Bad Days "
            "(And Why That Matters)"
        ),
        "persona": ["A", "B"],
        "keywords": [
            "options signal service review",
            "WhatsApp trading alerts",
        ],
        "cta": "starter_trial",
        "type": "positioning",
        "cross_channel": ["x_thread", "reddit_options"],
        "status": "pending",
    },
    {
        "slug": "whatsapp-group-tag-the-agent",
        "week_num": 9,
        "title_candidate": (
            "What Happens Inside the Private WhatsApp Group — Tag an AI Agent"
        ),
        "persona": ["A"],
        "keywords": [
            "AI trading assistant",
            "chatgpt options",
            "claude trading",
        ],
        "cta": "pro_trial",
        "type": "paid_differentiator",
        "cross_channel": ["x_thread", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "first-30-v53-trades",
        "week_num": 10,
        "title_candidate": (
            "The First 30 V5.3 Trades: What the Ledger Shows (Paper)"
        ),
        "persona": ["A", "B", "D"],
        "keywords": [
            "options trading track record",
            "paper trading performance",
        ],
        "cta": "pro_trial",
        "type": "performance_post",
        "cross_channel": ["x_thread", "reddit_options", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "engine-post-mortem-first-30-days",
        "week_num": 11,
        "title_candidate": (
            "What the Engine Got Wrong in the First 30 Days (Post-Mortem)"
        ),
        "persona": ["B", "D"],
        "keywords": ["options trading losses", "trade review"],
        "cta": "pro_trial",
        "type": "post_mortem",
        "cross_channel": ["x_thread", "reddit_options", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "systems-problem-not-pick-problem",
        "week_num": 12,
        "title_candidate": (
            "One Trade a Day Is a Systems Problem, Not a Pick Problem"
        ),
        "persona": ["A", "B"],
        "keywords": [
            "retail options trading systems",
            "trading routine",
        ],
        "cta": "pro_trial",
        "type": "thought_leadership",
        "cross_channel": ["x_thread", "linkedin"],
        "status": "pending",
    },
    {
        "slug": "gammarips-morning-90-seconds",
        "week_num": 13,
        "title_candidate": (
            "The GammaRips Morning: Mechanical Options Trading in 90 Seconds"
        ),
        "persona": ["A"],
        "keywords": [
            "options trading routine",
            "part time options trading",
        ],
        "cta": "pro_trial",
        "type": "video_demo",
        "cross_channel": ["x_thread_video", "linkedin", "reddit"],
        "status": "pending",
    },
]


def _seed_schedule(db) -> None:
    doc_ref = db.collection("blog_schedule").document("current")
    snap = doc_ref.get()
    if snap.exists:
        existing = snap.to_dict() or {}
        existing_rows = {r.get("slug"): r for r in existing.get("rows", []) or []}
        # Preserve status on slugs that already have a non-pending state.
        merged: list[dict] = []
        for row in BLOG_SCHEDULE_ROWS:
            prior = existing_rows.get(row["slug"])
            if prior and prior.get("status") not in (None, "pending"):
                row = {**row, "status": prior["status"]}
            merged.append(row)
        rows_to_write = merged
        print(
            f"[seed] blog_schedule/current exists — preserving non-pending statuses; "
            f"writing {len(rows_to_write)} rows."
        )
    else:
        rows_to_write = BLOG_SCHEDULE_ROWS
        print(f"[seed] blog_schedule/current not found — writing fresh {len(rows_to_write)} rows.")

    doc_ref.set({
        "version": SCHEDULE_VERSION,
        "rows": rows_to_write,
    })
    print(f"[seed] wrote blog_schedule/current (version={SCHEDULE_VERSION}).")


def _seed_voice_rules(db) -> None:
    doc_ref = db.collection("blog_config").document("voice_rules")
    rendered = voice_rules.render_for_prompt()
    doc_ref.set({
        "version": SCHEDULE_VERSION,
        "rendered": rendered,
        "retired_aliases": list(voice_rules.RETIRED_ALIASES),
        "banned_phrases": list(voice_rules.BANNED_RECOMMENDATION_PHRASES),
        "disclaimer_long": voice_rules.DISCLAIMER_LONG,
        "disclaimer_short": voice_rules.DISCLAIMER_SHORT,
    })
    print("[seed] wrote blog_config/voice_rules.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="Print payload, do not write.")
    parser.add_argument("--voice-only", action="store_true", help="Only seed voice_rules doc.")
    parser.add_argument("--schedule-only", action="store_true", help="Only seed blog_schedule doc.")
    args = parser.parse_args()

    if args.dry_run:
        payload = {
            "blog_schedule/current": {
                "version": SCHEDULE_VERSION,
                "rows": BLOG_SCHEDULE_ROWS,
            },
            "blog_config/voice_rules": {
                "version": SCHEDULE_VERSION,
                "rendered": voice_rules.render_for_prompt(),
                "retired_aliases": list(voice_rules.RETIRED_ALIASES),
                "banned_phrases": list(voice_rules.BANNED_RECOMMENDATION_PHRASES),
                "disclaimer_long": voice_rules.DISCLAIMER_LONG,
                "disclaimer_short": voice_rules.DISCLAIMER_SHORT,
            },
        }
        print(json.dumps(payload, indent=2))
        return

    db = firestore_helpers.get_client(PROJECT_ID)
    if not args.voice_only:
        _seed_schedule(db)
    if not args.schedule_only:
        _seed_voice_rules(db)
    print("[seed] done.")


if __name__ == "__main__":
    main()
