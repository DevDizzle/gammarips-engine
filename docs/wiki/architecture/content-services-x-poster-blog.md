Status: active
Type: architecture
Tag: architecture-fact
Exit-context: n/a
Source: docs/DECISIONS/2026-04-24-x-poster-launch.md
Date: 2026-07-17

# x-poster + blog-generator ADK services + shared content lib

The distribution layer is two ADK multi-agent services plus a shared library, stood up
2026-04-24 (no execution-policy change):
- **`x-poster/`** — @gammarips X publisher (Planner→Writer→Reviewer→EscalationChecker loop +
  Publisher), post types behind `POST /post`, `DRY_RUN=true` default.
- **`blog-generator/`** — same ADK shape, writes Firestore `blog_posts/{slug}` for the
  webapp `/blog`, weekly Mon cron.
- **`libs/gammarips_content/`** — shared brand constants + compliance rubric/canonicalizer +
  tweepy/firestore/MCP helpers, vendored into both at deploy time.

X posting was removed from `win-tracker` at the same time (it now writes only
`signal_performance`). These services turn overnight signals + closed trades + the morning
report into published content; the content STRATEGY (receipts not picks) is
[[content-receipts-not-claims]] and the current @gammarips posture is
[[x-poster-revamp-agentic]].
