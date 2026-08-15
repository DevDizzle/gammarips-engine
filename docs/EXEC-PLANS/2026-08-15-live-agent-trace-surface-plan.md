# EXEC PLAN 2026-08-15: live agent, trace surface, video series, website

Status: ACTIVE for lane A (owner direction 2026-08-15, later the same day: "let
gammarips-trader do its work"). Lanes B and C's `/agent` trace page are QUEUED behind
the GTM organic push (`docs/GTM-ORGANIC-GROWTH-PLAN.md`: landing rewrite, guides,
video series). The live-video-stream idea is PARKED. Traces in BigQuery allow a render
later.

## What the owner decided (2026-08-15)

- The agent trades **real capital, $1,000, in the Robinhood agentic account**. His
  words: minimize execution risk, "the system has the skills, I do not"; and it is
  promo that builds the brand and drives subscribers.
- Traces are **saved to BigQuery by hook callbacks and served to a terminal-ish web
  page, slightly delayed**. Not a live video.
- YouTube is the **per-client how-to series**: Grok, Claude Code, Claude, Codex,
  ChatGPT.
- The website gets the landing rewrite (plan §A) plus the trace surface.
- Work is **delegated**: the `gammarips-trader` session builds the agent and the
  trade mechanics. This engine session builds the trace pipeline, the host, and the
  docs. A webapp session builds the pages.
- This reopens the 07-31 "autonomy ON HOLD" ruling for the agent. Record it in the
  trader repo and its memory.

## Owner calls, flagged once, now DECIDED unless he reopens them

1. **The agent never sees the tournament pick.** No Gmail on the host. It selects
   from the pool with the harness `/trade` screen and the Robinhood book, on public
   MCP primitives. "No pick, anywhere" holds.
2. **Public traces of a real-money account.** Copy frames it as the operator's own
   ring-fenced account and his own agent. Never a trade to follow. No P&L scoreboard
   on the page (webapp forbidden claims #2 and #6). Delay default **15 min**; the
   owner can set 15 to 60. Owner checks: Robinhood terms on publishing agent
   activity; a short legal read is prudent.
3. **Unattended real money.** Fail closed (`gammarips-trader/docs/RULES.md` §Halt).
   **Same-day flat in v1.** Exit arithmetic in code (`exit_eval.py`), not in the
   model. A watchdog pages the owner and sets PANIC.
4. **Sizing default:** one contract, cost <= settled cash, one entry per day, no
   averaging. `needs deposit` => stand down. The owner may change this.
5. **Rollout:** SHADOW (NO_ORDERS) -> `gammarips-review` PASS -> live orders ->
   public announce. The `/agent` page can be public during shadow with a SHADOW badge.

## Architecture

```
host: gammarips-agent-1 (GCE e2-small, Debian 12, on-demand, no video)      [lane B]
  agent uid: /home/agent/trader (private repo)   bin/agent-day.sh -> `claude -p` runs
             hooks -> client-side redaction -> logs/trace-spool.jsonl       [lane A]
  shipper uid: trace-shipper.service tails the spool -> POST /events (ID token)
ingest: Cloud Run agent-trace-ingest (IAM-only) -> validate -> server-side redaction
        (literal denylist in Secret Manager) -> BQ profit_scout.agent_trace_events
        + Firestore agent_sessions/{date}(/events)                          [lane B]
webapp: /agent terminal-ish viewer (Firestore, shows events with ts <= now - DELAY),
        homepage "Watch the agent work" card, disclosures #06               [lane C]
YouTube: how-to series per client, owner records; descriptions link the harness repo
        first, the site second (UTM per client), then /agent as proof      [lane B]
```

## Delegation matrix

| Lane | Owner | Deliverables |
|---|---|---|
| A. Agent + trade mechanics | `gammarips-trader` peer session | spikes S1/S2; un-archive and rebase `enter-position` and `monitor-position`; `scripts/exit_eval.py`; `bin/agent-day.sh` (ET clock, `claude -p ... --output-format stream-json`, caps, NO_ORDERS/PANIC); `bin/prompts/*.md`; hooks that emit the trace contract to the spool; `settings.vm.json` (order tools VM-only); `bin/watchdog.sh`; `docs/RULES.md` "Unattended mode"; `docs/DECISIONS/2026-08-15-autonomy-reopened.md`; trader memory updates |
| B. Trace pipeline + host + docs | engine session | `docs/DATA-CONTRACTS.md` § agent traces; `agent-trace-ingest/` service + BQ DDL + Firestore mirror + delay/visibility; `agent-host/` (VM, SA/IAM, secrets push, shipper unit, `deploy.sh`); MCP key mint for the agent; `docs/DECISIONS/2026-08-15-agent-trace-surface.md`; GTM plan Workstream E; `docs/GTM-VIDEO-SERIES.md`; briefs to lanes A and C; `NEXT_SESSION_PROMPT.md`; engine memory |
| C. Website | webapp session (copy via `gammarips-copywriter`, `/ship` from `~/workspace`) | PR-1 A1 + delete the 3 dead pick-era components; PR-2 `/agent` viewer + homepage card + disclosure component + disclosures #06 + copywriter clause, behind `NEXT_PUBLIC_AGENT_TRACE=1`; PR-3 A2 to A4; PR-4 video embeds as videos land |
| D. Owner | Evan | fund and enable options on the agentic account; per-order approval setting; RH terms check; YouTube channel; record videos (Gemini edit); decisions 1 to 5; approve the `gammarips-review` gate before live orders |

Interfaces: (1) the trace event contract, lane B writes it first, lane A emits it,
lane C renders it; (2) the Firestore doc shape, B writes and C reads; (3) the host
layout (`/home/agent/trader`, spool path, env file names) between A and B.

## Trace event contract (lane B, day 1; final text goes in `docs/DATA-CONTRACTS.md`)

BQ `profit_scout.agent_trace_events`, partition `DATE(ts)`, cluster `session_id`:

| Field | Type | Note |
|---|---|---|
| event_id | STRING | uuid, idempotency key |
| agent_id | STRING | `live-agent-v1` |
| session_id | STRING | Claude Code session id |
| run_id | STRING | one per `claude -p` invocation |
| run_kind | STRING | trade, midday, monitor, review, coach |
| seq | INT64 | monotonic per session |
| ts | TIMESTAMP | event time on the host |
| event_type | STRING | session_start, user_prompt, assistant_text, tool_use, tool_result, permission_denied, stop, session_end, error |
| tool_name | STRING | nullable |
| payload_json | STRING | redacted; tool_result capped at 4 KB |
| payload_chars | INT64 | pre-cap size |
| model | STRING | nullable |
| cost_usd | FLOAT64 | on stop rows |
| visibility | STRING | public, private |
| redaction_version | STRING | stamped on every row |
| host | STRING | hostname |
| ingested_at | TIMESTAMP | server time |

Firestore: `agent_sessions/{YYYY-MM-DD}` summary doc `{date, mode: shadow|live,
runs: [{run_kind, started_at, ended_at, cost_usd, decision_summary}], event_count,
last_event_ts, position: flat|open, disclosure_version}` plus subcollection
`events/{seq}` (public events only, same fields minus private). The webapp reads with
`ts <= now - DELAY`.

Redaction. Client side in the hook: `\b\d{9}\b`, emails, `gr_live_`, `sk-ant-`,
`ya29\.`, JWTs, `Bearer \S+`; account ids dropped, order UUIDs kept. Server side: a
literal denylist (account numbers, owner email) from Secret Manager
`AGENT_TRACE_REDACT_LITERALS`. `visibility=private` for `get_portfolio` results and
for anything the prompt marks private.

## Lane A brief (sent to the trader session by SendMessage)

- Spikes first. S1: `get_option_level_upgrade_info`, then `review_option_order` (review
  only, no place) on the agentic account. Can it trade options? Is per-order approval
  switchable off? S2: Robinhood OAuth persistence with no browser for 3 days on the
  host, or with copied credentials. Outcome: unattended OK, or a daily 09:40 ET
  re-auth ritual over an IAP port-forward.
- Runtime: `claude -p` per phase with `--permission-mode dontAsk --settings
  settings.vm.json --max-turns --max-budget-usd --output-format stream-json --verbose`.
  Schedule: 09:52 `/trade` -> enter-position (top-tier model); 11:45 second pass if
  flat (`--resume`); monitor tick every 10 min while `state/OPEN_POSITION` exists
  (small model, `exit_eval.py` verdict obeyed); 15:50 time-stop; 16:40 `/review`.
  NO_ORDERS = shadow rows with `"paper": true`. PANIC = no runs, and if a position is
  open, one closing tick then halt. Daily cost cap. Watchdog pages the owner on a
  stalled monitor or an auth error.
- Rules: no Gmail, no pick, same-day flat, sizing default, target rests GTC in the same
  minute, stop manual via ticks, exits at `high_fill_rate_sell_price`, limit only, one
  reprice.
- Hooks: emit contract rows to `logs/trace-spool.jsonl` (append only, redacted client
  side, `seq` monotonic per session). Never write to GCP directly.
- Guards: `settings.vm.json` denies `env`, `printenv`, `curl`, `wget`, `python -c`,
  `gcloud`, `git push`, `Read(~/.claude/**)`, `WebFetch`, `WebSearch`; a PreToolUse
  Bash block list; a path guard to the repo. Order tools are allowlisted ONLY in the VM
  copy. The laptop settings stay read-only.
- Docs and memory: RULES "Unattended mode"; a decision note; memory
  `agent-on-hold-owner-assist` -> reopened 2026-08-15; `owner-may-pause-trading` ->
  superseded.

## Lane B build (engine session)

- `agent-trace-ingest/`: FastAPI, `deploy.sh` per repo conventions, IAM-only (verify
  the live IAM policy, not the flag). `POST /events` (batch, idempotent on `event_id`),
  schema validation, server redaction, BQ streaming insert (the `TraceLogger`
  fire-and-forget shape or a sibling `AgentTraceLogger`), Firestore mirror,
  `GET /health`. BQ DDL as a one-shot in `scripts/`. Contract in `DATA-CONTRACTS.md`.
- `agent-host/`: `deploy.sh` (`--project=profitscout-fida8` on every call; SA
  `agent-host@` with `roles/run.invoker` on the ingest, `roles/aiplatform.user`,
  logging; NO Secret Manager; IAP-only ssh; on-demand e2-small, up 24/7, ~$15/mo),
  `setup.sh` (users `agent` and `shipper`, pinned `claude`, `DISABLE_AUTOUPDATER=1`,
  clone the private repo as root with the deploy key, then chown),
  `systemd/trace-shipper.service` (tail the spool -> POST with an ID token from
  metadata; the agent uid gets `IPAddressDeny=169.254.169.254/32`), `bin/push-secrets.sh`
  (root 0600: `GAMMARIPS_MCP_KEY`, deploy key, Anthropic key or Vertex env),
  `bin/status.sh`, `bin/panic.sh` (touch `state/PANIC` over IAP ssh). v1 Anthropic auth
  is `ANTHROPIC_API_KEY` in the agent env with deny rules and double redaction. An
  nginx gateway plus Vertex is v2 hardening.
- Docs: decision note; GTM plan Workstream E; `docs/GTM-VIDEO-SERIES.md`;
  `NEXT_SESSION_PROMPT.md` refresh; engine memory note.

## Lane C brief (webapp session)

- PR-1: `src/components/landing/harness-cta.tsx:20-21` -> `/trade` `/review`
  `/coach`; delete `todays-pick-card.tsx`, `next-pick-countdown.tsx`,
  `cohort-stats-row.tsx`.
- PR-2 `/agent`: `src/app/agent/page.tsx` (+ `/agent/[date]`) reads Firestore
  `agent_sessions`, `revalidate=60`, delay filter, terminal-ish console (dark, mono,
  tool calls collapsed, `assistant_text` as prose, denials shown), header badges
  "SHADOW" or "LIVE ACCOUNT" and "15 min delay", ET timestamps; empty state "No
  session yet today"; `src/components/compliance/disclosure-line.tsx`; homepage card
  after `<HarnessCta />` (`page.tsx:269`) behind `NEXT_PUBLIC_AGENT_TRACE`; footer and
  sitemap conditional; `hero.tsx:80-82` rewrite ("Not live data" becomes false);
  copywriter clause, owner-ruled: the `/agent` trace is real data by design, labeled
  the operator's own account and own agent, never illustrative, never a signal;
  `/disclosures` #06; metadata, canonical, `noindex` when unset. Copy in STE, no em
  dashes, no P&L totals.
- PR-3: A2 to A4 as in the plan of record. PR-4: per-video embeds in the hero and the
  guides.
- Verify: typecheck (only the 3 known `signals/page.tsx` errors), build, knip, local
  render with seeded Firestore docs, Lighthouse CLS 0, copywriter pass, `/ship`.

## Video series (`docs/GTM-VIDEO-SERIES.md`, owner records)

Template per episode (4 to 8 min): cold open in the client -> honesty beat -> free
connect (`claude mcp add ...` or the connector steps) -> the anonymous brief shows real
data -> the paid boundary said plainly -> the loop (`/trade` for Claude Code and Codex
via the harness; agent reasoning for ChatGPT, Claude, Grok) -> "it rejected most of the
pool" -> close: repo first, site second, `/agent` as proof. Order: Claude Code (spec
exists, HN artifact) -> Grok (receipt exists) -> Codex (needs harness `AGENTS.md`,
plan D2) -> ChatGPT and Claude after the connector-auth checks (B3/B4). Rails: the 8
compliance rails in `GTM-VIDEO-CLAUDE-OPTIONS-WORKFLOW.md`. UTM
`utm_source=youtube&utm_medium=video&utm_campaign=howto_<client>`. One 60 to 90 s Short
per episode. Each guide (B1 to B4) embeds its episode.

## Sequence

- Day 1: lane B writes the contract, the decision note, and the briefs; sends lane A
  its brief; the owner starts lane C. Lane A starts S1 and S2.
- Week 1: ingest + BQ + Firestore mirror deployed with a seed session; host up; lane A
  runtime in SHADOW on the host, real traces flowing; lane C PR-1 and PR-2 on seeded
  data.
- Week 2: SHADOW soak, 5 sessions; nightly leak grep on BQ (`gr_live_`, `sk-ant-`,
  account ids); cost check; `gammarips-review` on lane A skills and on ingest exposure;
  the Claude Code video recorded.
- Week 3: the owner flips NO_ORDERS off; 3 live sessions; then announce (X drafts,
  guide links, video descriptions). Landing PR-3 lands in parallel. Show HN gates are
  unchanged.

## Verification

- Contract: seed 5 fake events end to end (hook -> spool -> shipper -> ingest -> BQ row
  + Firestore doc -> `/agent` renders after the delay). A planted `gr_live_x` and a
  9-digit id never reach BQ or Firestore. Ingest rejects unauthenticated calls.
- Host: the agent uid cannot reach 169.254.169.254; the shipper can; `claude -p "reply
  ok"` works; a denied `env` shows as `permission_denied` in the trace.
- Lane A: SHADOW `/trade` -> would-be order row -> ticks obey `exit_eval.py` ->
  `/review`. PANIC closes and halts. The watchdog pages on a simulated stall.
- Webapp: as listed in lane C.
- Docs: `NEXT_SESSION_PROMPT.md`, DECISIONS notes (engine + trader), memory notes.
