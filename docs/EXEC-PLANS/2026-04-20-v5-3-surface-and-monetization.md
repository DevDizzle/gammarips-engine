# EXEC-PLAN: V5.3 Surface Alignment + Monetization

**Author:** Evan + Claude (session 2026-04-20)
**Status:** **v2 — amended after gammarips-review audit 2026-04-20.** Pending Evan sign-off on Section 9 changes before Phase 1.0 starts.
**Scope:** Five workstreams that bring the non-trading surfaces (webapp, MCP, arena, GTM, payments) into lockstep with the V5.3 "Target 80" execution policy and unlock the $29/mo WhatsApp tier.

**Change log:**
- **v1 (2026-04-20):** initial draft
- **v2 (2026-04-20):** post-review amendments — Phase 2 push moved out of forward-paper-trader (BLOCKER), `todays_pick` writer pinned to signal-notifier (HIGH), drift tripwire added (HIGH), arena commentary gated to post-market (HIGH), real-money-vs-paper discipline rule proposed for TRADING-STRATEGY.md (HIGH), Secret Manager mandate added to all phases (LOW), sequencing within Week 1 spelled out (LOW).

---

## Executive Summary

The engine is on V5.3 Target 80. The **surfaces around it are not.** Today's state, per session reconnaissance:

| Surface | State | Gap |
|---|---|---|
| Webapp (`/home/user/gammarips-webapp`) | Still renders V3 "premium" flags and exposes recommended_contract without gating | Needs V5.3 vocabulary; paywall decision |
| MCP server (`/home/user/gammarips-mcp`) | Hardcoded `score >= 6` gate (V3 artifact), no "today's pick" tool, no open-position tool, currently unauthenticated | 2 tools broken, 5 tools missing for $29/mo chat UX |
| Agent arena | Write-only: 0% agreement with signal-notifier over 21 days; ~$150-250/mo LLM cost; no downstream consumer | Keep for freemium engagement, reshape to cut cost — or kill |
| GTM / content | One-way X posts from `signal_performance`; no Reddit pipeline; no draft-to-email flow | Build draft-and-email content service |
| Payments / WhatsApp | Stripe exists; OpenClaw ready; no wiring between forward-paper-trader and WhatsApp | Wire entry/exit → WhatsApp; Firestore subscription check |

Monetization thesis (from user, 2026-04-20):
> "Paywall is just access to our WhatsApp group where we ping the entry and exit … essentially our forward-paper-trader logic being sent to private WhatsApp group so paid users can follow along. Everything else is just freemium content so we gain reputation and drive traffic."

That is, **freemium = max useful transparency**, **paid = mechanical push notifications** so the user doesn't have to check the webapp. This framing drives the plan.

---

## 1. Why FIX was picked on 2026-04-17 (background context)

User asked why the notifier surfaced FIX (score 4) over OKLO (score 8) / WDC (score 7) / CLS (score 7). BQ evidence:

| Ticker | Score | vol_oi | moneyness | spread | V5.3 gate |
|---|---|---|---|---|---|
| OKLO | 8 | **1.5** | 10.8% | 0.8% | **FAIL** (vol_oi < 2.0 — flow was stale OI rolls) |
| WDC | 7 | **NULL** | 9.4% | 0.7% | **FAIL** (missing data) |
| CLS | 7 | 506 | **4.8%** | 9.8% | **FAIL** (moneyness < 5%) |
| LLY | 6 | 35 | **1.7%** | 0.0% | **FAIL** (way too ATM) |
| DAL | 7 | 5.37 | 11.5% | 8.7% | PASS |
| **FIX** | **4** | 4.5 | 7.8% | 9.8% | **PASS** |

Score is **orthogonal** to V5.3 ranking. Gates do the work: V/OI>2 rejects stale OI, 5–15% OTM rejects ATM gamma plays, VIX≤VIX3M rejects backwardation days. Among survivors, **rank is directional dollar volume** — FIX edged DAL by $60K ($11.57M vs $11.51M call DV). A photo finish.

This matters for the plan because it tells us what the webapp should **teach**: "score tells you how interesting a ticker is; the V5.3 gates tell you whether it's *tradeable today*." The webapp's V3 habit of sorting/filtering/badging by score is therefore correct as a *browsing* affordance — it just shouldn't masquerade as "premium = what to trade."

---

## 2. Target architecture

```
                                 ┌────────────────────────┐
                                 │  overnight-scanner      │
                                 │  → overnight_signals BQ │
                                 └───────────┬────────────┘
                                             │  05:30 ET
                                 ┌───────────▼────────────┐
                                 │  enrichment-trigger     │
                                 │  gates: score≥1, sprd≤10%│
                                 │       UOA>$500K         │
                                 │  → overnight_signals_enriched BQ
                                 │  → Firestore overnight_signals/_summaries
                                 │  → Firestore daily_reports (via report-gen 08:15)
                                 └───────────┬────────────┘
                                             │
                         ┌───────────────────┼─────────────────────┐
                         ▼                   ▼                     ▼
              ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐
              │  signal-notifier  │  │  agent-arena      │  │  webapp (free) │
              │  (deterministic   │  │  (freemium content│  │  reads Firestore│
              │   V5.3 pick       │  │   5 LLMs debate)  │  │  shows all data │
              │   09:00 ET email) │  │  06:00 ET         │  │                │
              └────────┬─────────┘  └──────────────────┘  └────────────────┘
                       │
                       ▼
              ┌──────────────────┐         ┌─────────────────────────────┐
              │ forward-paper-    │────────▶│ WhatsApp webhook (paid tier) │
              │ trader            │  entry  │  via OpenClaw                │
              │ 10:00 ET day-1    │  exit   │                              │
              │ writes ledger     │         │  subscribers from Stripe     │
              └──────────────────┘         │  → Firestore users/{uid}     │
                                           └─────────────────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ MCP server       │
              │ (paid chat agent │
              │  or anyone free) │
              └──────────────────┘
```

Key invariants:
- **One gate logic, one source of truth.** The filter-and-rank logic lives in `signal-notifier/main.py`. MCP's `get_todays_pick` must mirror it exactly — not reimplement gates inline.
- **Webapp is fully free.** No blur, no gate. Trust-building surface.
- **Paywall is push-only.** The value is "I don't have to check at 9:00 AM; the ping tells me what to do at 10:00."

---

## 3. Phased plan

Priority order confirmed by user: webapp → paywall → MCP → arena → GTM.

### Phase 1.0 — Pre-work: `todays_pick` schema + writer (0.5 day, BLOCKS Phase 1)

> **v2 amendment (audit #5, #11):** Before any reader (webapp banner, MCP tool, GTM drafter) touches Firestore `todays_pick/{scan_date}`, the **writer** must exist in `signal-notifier/main.py` and the schema must be pinned in this plan. This is the single source of truth for "what did GammaRips pick today."

**Schema (Firestore `todays_pick/{scan_date}`):**
```json
{
  "scan_date": "2026-04-17",           // underlying scanner date
  "decided_at": "2026-04-20T13:00:05Z",// when signal-notifier ran
  "effective_at": "2026-04-21T14:00:00Z", // 10:00 ET day+1 (when the trade is meant to be entered)
  "has_pick": true,
  "skip_reason": null,                 // one of: "no_candidates", "regime_fail_closed", "vix_backwardation", null
  "ticker": "FIX",
  "direction": "BULLISH",
  "recommended_contract": "FIX $580C 2026-05-22",
  "recommended_strike": 580,
  "recommended_expiration": "2026-05-22",
  "recommended_mid_price": 1.57,
  "recommended_dte": 32,
  "vol_oi_ratio": 4.5,
  "moneyness_pct": 0.078,
  "call_dollar_volume": 11570000,
  "put_dollar_volume": 2480000,
  "vix3m_at_enrich": 20.51,
  "vix_now_at_decision": 18.92,
  "policy_version": "V5_3_TARGET_80"
}
```

**Empty-state doc (no pick for the day):**
```json
{
  "scan_date": "2026-04-17",
  "decided_at": "2026-04-20T13:00:05Z",
  "effective_at": null,
  "has_pick": false,
  "skip_reason": "no_candidates_passed_gates"   // or "regime_fail_closed", "vix_backwardation"
}
```

**Writer invariant:** `signal-notifier/main.py` writes the doc **exactly once per scan_date**, before the email send. If the email fails, the doc still stands (it is the source of truth, not the email). If the doc write fails, the service returns 500 so the scheduler retries.

**Drift tripwire (audit #4):**
- New Cloud Scheduler job `drift-check-daily`, cron `15 9 * * 1-5` ET (15 min after notifier).
- Reads three sources: (a) most recent `signal-notifier` email from Mailgun events API, (b) Firestore `todays_pick/{today}`, (c) `mcp.get_todays_pick()` result.
- If any field (ticker, direction, contract) differs, write a Firestore `alerts/drift_{timestamp}` doc and email operator.

**Phase 1.0 Definition of Done:**
- Schema doc exists (this section) and is frozen before any reader code is written.
- `signal-notifier/main.py` has a writer with a unit test that asserts doc shape against the schema.
- Empty-state cases covered (no candidates, regime fail).
- Drift tripwire scheduler + alert collection deployed.

**G-Stack review (Phase 1.0):** **REQUIRED.** Writer touches signal-notifier; doc shape affects every downstream surface. Audit the writer diff for gate-logic preservation.

---

### Phase 1 — Webapp V5.3 alignment (2–3 days, surgical, depends on 1.0)

**Goal:** Free users see a coherent V5.3 story — what the engine thinks is interesting today, what the V5.3 gates picked, and why other high-score tickers did or didn't make it.

> **v2 amendment (audit #3, #9):** Webapp banner shows today's pick at the same moment the operator email goes out (~09:00 ET). Paying users do NOT get timing advantage — they pay for **convenience** (no webapp check, pre-staged WhatsApp push to their phone). Strategy doc update required.

**Specific edits** (file:line refs from webapp Explore report):

| Change | File | Purpose |
|---|---|---|
| Add `TodaysPickCard` component above Top Signals | `src/app/page.tsx` (~line 194) | Renders the single V5.3 pick (or "No pick today — VIX/filter reason") |
| Query today's pick from Firestore | `src/lib/firebase-admin.ts` (new fn) | `getTodaysPick()` filters `overnight_signals` by V5.3 gates, LIMIT 1 by dir UOA |
| Rename `is_premium_signal` badge → "Engine interest" subtle chip | `src/app/signals/[ticker]/signal-client.tsx:27–53, 105–166` | Kill "Premium Signal" framing. Keep the 5 flags as a technical detail panel. |
| Remove "Premium Only" filter toggle | `src/components/overnight/signals-table.tsx:18–64` | Replaced by direction + score filters |
| Change home-page top-signals sort | `src/app/page.tsx:35–37` | Sort by `overnight_score` DESC but ADD a "passes V5.3 gates" chip derived client-side from vol_oi/moneyness/vix fields |
| Add "Why [ticker] was today's pick" callout | `src/app/page.tsx` (new) | Explains gates: "vol_oi=4.5 ✓, moneyness=7.8% ✓, dir dollar vol $11.57M" |
| Remove type defs for `mean_reversion_risk`, `enrichment_quality_score` | `src/lib/firebase-admin.ts:197, 172`; `src/lib/types/overnight-edge.ts` | Ghost fields — never rendered |

**Paywall question resolved:** Per user's "freemium = max useful", **do not blur** the webapp. The paywall is convenience (push), not information access. This simplifies Phase 1 significantly.

**Strategy doc update (must land BEFORE Phase 1 ships — audit #3):**
Add section to `docs/TRADING-STRATEGY.md`:
> **Publication timing:** Today's pick is revealed publicly on the webapp and via WhatsApp push simultaneously at **09:00 ET day-0** (same moment the operator email fires). Paid users receive a WhatsApp notification so they do not have to check the webapp; they do **not** receive earlier access to the ticker. Simulated entry at 10:00 ET day-1 in `forward-paper-trader` models realistic operator slippage; real-money execution is the operator's responsibility and discretionary.

**Cache invariant (audit #9):**
- Home page uses Next.js `revalidate: 60` on the `todays_pick` fetch, OR on-demand revalidation triggered by a Firebase Function listening on the `todays_pick/{scan_date}` write.
- `getTodaysPick()` filters `scan_date == canonical_scan_date(today_et)` and returns `no_pick_available_yet` for any doc where `decided_at` is in a prior calendar day or missing.

**Definition of Done (Phase 1):**
- Home page renders today's V5.3 pick (or skip-reason) from Firestore `todays_pick/{scan_date}` — no SQL or inline filter on the reader side.
- "No pick available yet" state rendered cleanly between 16:30 ET (previous day close) and 09:00 ET (next decision).
- No "Premium" language remains in UI. Internal field names may stay; only display changes.
- `mean_reversion_risk` / `enrichment_quality_score` removed from TypeScript types.
- Deploy via Firebase App Hosting CI/CD by pushing to `DevDizzle/gammarips-webapp`.
- `docs/TRADING-STRATEGY.md` already updated with the Publication Timing section BEFORE this phase's PR merges.

**G-Stack review (Phase 1):** Not required for the webapp diff itself. But the `docs/TRADING-STRATEGY.md` update IS reviewed (via DECISIONS/ note) because it pins policy.

---

### Phase 2 — WhatsApp paywall (3–5 days, touches trading surface)

> ⚠️ **v2 amendment (BLOCKERS #1, #2):** Audit flagged that `forward-paper-trader/main.py` is a **batch simulator that runs 16:30 ET Mon–Fri**, not a live-at-10:00-ET service. Wiring the push inside the trader means the ping fires hours late — a product-killing defect. The push must come from the service that fires **at the decision time** for each event.
>
> Also: no synchronous Firestore query or outbound HTTP in the trader. `.claude/rules/forward-paper-trader.md` now gets a new rule prohibiting this.

**Goal:** Paying $29/mo subscribers get a WhatsApp ping at:
- **Entry-setup time (09:00 ET day-1)** — immediately after signal-notifier decides the day's pick. "Today's trade at 10:00 ET: BUY FIX $580C 05/22. Arm stop -60%, target +80%."
- **Exit time (day-3)** — from a separate 15:50 ET cron that reads the ledger's pending exits and fires one last "Close FIX now" push.

Intraday target/stop fills are NOT pushed at the moment of fill because the trader simulates them post-hoc; subscribers already armed their GTC orders at entry and will be notified by their broker, not by us. This is honest — the paywall value is the daily entry timing, not intraday event streaming.

**Architecture (v2, audit-cleared):**

```
Stripe checkout → webapp Stripe webhook → Firestore users/{uid}.subscription = {tier: "paid", expires_at: TS, whatsapp_e164: "+1..."}

09:00 ET signal-notifier/main.py (ALREADY computes today's pick):
  ▶ WRITE Firestore todays_pick/{scan_date} = {ticker, direction, contract, strike, expiration,
       mid_price, vol_oi, moneyness_pct, vix3m, effective_at: scan_date+1 10:00 ET}
  ▶ PUBLISH Pub/Sub topic `gammarips-pick-decided` with {scan_date, ticker, direction}
  ▶ (existing) send operator email

whatsapp-notifier (NEW Cloud Run service, subscribes to gammarips-pick-decided):
  ▶ reads todays_pick/{scan_date}
  ▶ loads Firestore users where subscription.tier == "paid" AND expires_at > now()
  ▶ POSTs to OpenClaw per subscriber
  ▶ all failure modes local — does NOT block notifier or trader

15:50 ET NEW scheduler: exit-reminder (can live in whatsapp-notifier):
  ▶ query forward_paper_ledger for trades where exit_timestamp IS NULL AND scan_date = today - 3 trading days
  ▶ fire one "close now" push per open position
  ▶ forward-paper-trader itself then runs at 16:30 ET and writes the real ledger row

forward-paper-trader/main.py: UNCHANGED in this phase. No new imports, no Firestore users query,
  no HTTP calls, no POLICY_VERSION touch.
```

**Specific edits:**

| Change | File | Purpose |
|---|---|---|
| Stripe webhook handler | `/home/user/gammarips-webapp/src/app/api/stripe/webhook/route.ts` (already exists) | Extend to write `subscription` field on success + cancellation |
| **todays_pick writer** | `signal-notifier/main.py` | After the existing SELECT that finds the LIMIT-1 pick, write the Firestore doc `todays_pick/{scan_date}` **before** sending the operator email. Fail-closed: if doc write fails, skip email too. |
| **Pub/Sub publish** | `signal-notifier/main.py` | Publish `gammarips-pick-decided` with `{scan_date, ticker}` after doc write. |
| **New service** | `/home/user/gammarips-engine/whatsapp-notifier/` | Cloud Run, Pub/Sub-triggered; reads Firestore `todays_pick` + `users`; POSTs OpenClaw; logs every attempt to `libs/trace_logger`. |
| **Exit-reminder cron** | `whatsapp-notifier/main.py` (second endpoint `/exit_reminder`) | Reads `forward_paper_ledger` for open positions on day-3; sends reminder push at 15:50 ET. |
| **New scheduler jobs** | gcloud scheduler | (a) `whatsapp-notifier-entry` subscribing to Pub/Sub — no cron needed; (b) `whatsapp-notifier-exit-reminder` cron `50 15 * * 1-5` ET. |
| **Forbid in-trader HTTP** | `.claude/rules/forward-paper-trader.md` | Add rule: "NEVER add synchronous outbound HTTP or user-notification calls to this service. All subscriber messaging goes through `whatsapp-notifier` via Pub/Sub." |
| **Compliance disclaimer** | `whatsapp-notifier` | "Paper-trading performance only. Educational. Not investment advice." Appended to every push. |
| **Secrets** | Secret Manager | `OPENCLAW_API_KEY`, `STRIPE_WEBHOOK_SECRET` mounted from Secret Manager — never env-var plaintext. |

**Legal / compliance risks to clear BEFORE shipping:**
1. **Are we selling "trading signals"?** Gray zone. Safer framing: we share our paper-trading ledger for educational purposes. Subscriber pays for **delivery convenience** — a push that reaches your phone before the 10:00 ET entry moment, so you don't have to sit at a screen. They pay for attention relief, not timing advantage (all data is public on the webapp at 09:00 ET simultaneously). Confirm framing with counsel.
2. **WhatsApp Business API rules.** OpenClaw uses a private group. Ensure bulk-message rules are respected; avoid WhatsApp's spam classifiers.
3. **Stripe + SaaS vs. financial-services handling.** Stripe's Acceptable Use for "investment and financial products" may require additional disclosures.
4. **Real-money-vs-paper discipline (NEW, v2, audit finding #6):** Because `forward-paper-trader` runs the ledger regardless, and subscribers may discretionarily skip real-money trades, the paper-vs-real divergence must be tracked. `docs/TRADING-STRATEGY.md` will get a new section (Phase 2 pre-deploy) requiring: *"For the 30-day OOS validation window, operator logs every real-money skip to Firestore `real_money_skips/{scan_date}` with a reason. If the skip rate exceeds 20%, paper results become an unreliable proxy for real-world performance and we must pause marketing claims built on paper returns."*

**Definition of Done (Phase 2):**
- Paying subscriber receives a WhatsApp entry push **within 10 seconds of 09:00:05 ET** (signal-notifier decision time), NOT tied to the trader's 16:30 ET batch run.
- Exit reminder push fires at 15:50 ET on day-3 and covers every open position in `forward_paper_ledger` where `exit_timestamp IS NULL`.
- Unsubscribe: Stripe cancellation writes `subscription.tier = "free"` to Firestore within 60 seconds; next push skips the user.
- **Non-blocking invariant:** OpenClaw or Firestore failure in `whatsapp-notifier` must NOT block or retry signal-notifier. Pub/Sub dead-letter queue absorbs failed notifier runs; on-call alerts if DLQ > 0 for 10 min.
- **Secrets invariant:** all new credentials via Secret Manager only. No keys in source, .env, or plaintext env vars.
- **Trader untouched:** `forward-paper-trader/main.py` has zero diff in this phase. `POLICY_VERSION`, `POLICY_GATE`, `LEDGER_TABLE`, and the ledger schema `record = {...}` are unchanged. Verified via `git diff forward-paper-trader/` before deploy.
- **Trader latency invariant:** Cloud Run p50/p95 of `forward-paper-trader` `/` endpoint unchanged within 5% over 5 business days pre- and post-Phase-2 deploy. (Phase 2 shouldn't affect it at all, but verifying means we caught any accidental import or blocking call.)

**G-Stack review (Phase 2):** **REQUIRED.** Audit surfaces:
- `signal-notifier/main.py` diff for `todays_pick` writer + Pub/Sub publish (gate logic must not change — only side effects added).
- `whatsapp-notifier/main.py` (new service) — audit for retry/backoff, circuit breaker, timeout budgets, failure isolation from notifier.
- Confirm `.claude/rules/forward-paper-trader.md` update is in place BEFORE any whatsapp-notifier work begins.

---

### Phase 3 — MCP refresh (2–3 days)

**Goal:** MCP tools are V5.3-correct and support both (a) the eventual paid chat-agent UX and (b) any public agent that queries GammaRips data.

From MCP Explore report — fix/add matrix:

**FIX (3 existing tools):**
1. `get_enriched_signals` — change `overnight_score >= 6` → `>= 1` (stale V3 gate)
2. `get_signal_performance` — add `LOWER(direction)` normalization
3. `get_overnight_signals` — replace hardcoded field names with BQ schema introspection

**ADD (5 new tools):**
1. `get_todays_pick()` — mirrors signal-notifier's gate + rank logic exactly. **Must not reimplement gates inline;** import the shared function or reference the same SQL template.
2. `get_open_position()` — queries `forward_paper_ledger` for `exit_timestamp IS NULL`; fetches current Polygon price; returns unrealized P&L + days-to-timeout
3. `get_position_history(days=30)` — realized P&L summary from `forward_paper_ledger`
4. `get_freemium_preview(limit=5)` — top-5 enriched signals for public browsing
5. `get_enriched_signal_schema()` — returns BQ column list so chat agents can reason over what's available

**Deployment/auth:**
- Currently deployed to Cloud Run, unauthenticated, public SSE endpoint
- Add Firestore-backed API key check (`taas_users` collection already designed per MCP_AUTH.md)
- Free public access keeps 3 tools: `get_daily_report`, `get_report_list`, `get_freemium_preview`
- Paid/API-key gated: everything else, especially `get_open_position`

**Definition of Done (Phase 3):**
- All 3 fixes deployed; old `score >= 6` gate eliminated everywhere
- 5 new tools pass an integration test from a real chat agent ("What's today's pick?" → returns correct ticker or "no pick today")
- Auth middleware enforces Firestore-backed API key for protected tools

**G-Stack review (Phase 3):** **REQUIRED.** `get_todays_pick` must mirror signal-notifier gates exactly. Any drift = data mismatch between email, WhatsApp push, webapp banner, and chatbot answer. gammarips-review must audit the SQL.

---

### Phase 4 — Arena decision (0 or 1–2 days)

Agent Arena's role under V5.3 is the most ambiguous workstream.

**Findings:**
- Zero downstream execution consumer
- 0% agreement with signal-notifier over 21 trading days (they optimize different objectives)
- LLM cost $150–250/mo
- Webapp currently renders arena as "spectacle / education"

**Two options:**

**Option A — Reshape as freemium content (recommended, given user's freemium strategy):**
- Keep arena running but **decouple** from critical-path scheduler (already done — it no longer races with enrichment)
- Reduce to 2 agents (Claude + Grok) → ~60% cost savings
- Change the debate question from "which single trade?" to "how risky is today's V5.3 pick?" — arena becomes a **risk-commentary layer** on top of the notifier's deterministic pick
- Publish highlights to webapp + X ("Claude agrees, Grok dissents — here's why")

**Option B — Kill:**
- Remove service, scheduler, and downstream tables after 90-day archive
- Saves ~$200/mo + ~$40/mo Cloud Run
- Rollback cost is a few engineering days if we ever want it back (git history preserved)

**Recommendation:** Option A. User's freemium thesis specifically calls out engagement ("thrill of picking winners"). Arena transparency into AI disagreement is exactly that content. But only if we can cut cost and change the question to something non-redundant with notifier.

> **v2 amendment (audit #6):** Arena risk commentary is **published only AFTER 15:50 ET day-3 close**, never pre-entry. Showing "Claude says this is high risk" on the webapp banner at 09:00 ET could cause operators to discretionarily skip real-money trades — creating a paper-vs-real divergence that silently biases any future performance claim. Arena output is **retrospective commentary** for closed trades only.

**Definition of Done (Phase 4):**
- Arena cost drops to ≤$60/mo (2 agents, 2 rounds, or equivalent).
- Arena output appears on the webapp's **closed-trades** pages ("Here's what the AIs said about this trade back on 2026-04-17") — never on the live daily-pick banner.
- If kill: all `agent_arena_*` tables archived for 90 days then deleted; scheduler job removed; `docs/DECISIONS/` note records the reasoning.
- Arena schedule moved OUT of 06:00 ET slot (set for Phase 4 to be decided; could run post-market at 16:30 ET Mon–Fri to debate each day's closed V5.3 pick).

**G-Stack review (Phase 4):** Required if we ever wire arena back into gate logic. Not required for Option A's retrospective commentary — but any change to timing (pre-entry vs post-close) needs a DECISIONS note.

---

### Phase 5 — GTM content pipeline (3–5 days)

**Goal:** Automate the *drafting* of X + Reddit posts about GammaRips' daily output. **Operator posts manually** after reviewing the drafts in their inbox. This avoids Reddit shadowban risk (user confirmed manual posting).

**Inputs to content generation:**
- Today's daily report (`daily_reports/{today}`)
- Today's V5.3 pick from `todays_pick/{scan_date}` (SAME Firestore doc the webapp reads — single source of truth, audit #4)
- Arena risk commentary (retrospective, from Phase 4 if kept)
- **Realized-only** `signal_performance` rows: `WHERE exit_timestamp IS NOT NULL AND DATE(exit_timestamp) < CURRENT_DATE()` — audit #8 bars unrealized / intraday-open P&L from appearing in track-record posts.

**Architecture:**

```
New service: gtm-content-drafter (Cloud Run, scheduled 09:30 ET)
  → reads daily_reports, overnight_signals_enriched, signal_performance
  → calls Gemini to draft:
       - X post (≤280 chars): today's pick + thesis + relevant gate stat
       - Reddit post (r/options, r/thetagang, r/wallstreetbets): longer form,
         leads with educational hook ("how to filter stale OI rolls"),
         ends with "we paper-traded FIX today based on these gates"
       - Track-record thread (weekly): realized P&L since V5.3 cutover
  → emails drafts to eraphaelparra@gmail.com via Mailgun
  → operator copy-pastes after review
```

**Specific edits:**

| Change | File | Purpose |
|---|---|---|
| New service dir | `gtm-content-drafter/main.py`, `Dockerfile`, `deploy.sh`, `requirements.txt` | Cloud Run drafter |
| Scheduler job | `gcloud scheduler jobs create` | `30 9 * * 1-5` ET — runs after signal-notifier fires at 9:00 |
| Existing X poster (from `signal_performance`) | Identify and audit — currently posts auto | Decide: keep auto-post for closed-trade highlights OR pipe through drafter for approval |
| Reddit subreddit target list | In drafter config | r/options, r/thetagang, r/wallstreetbets (karma-aware) |

**Existing X posting status — unknown.** User mentioned "we are just posting to X from signal_performance." Need to locate the service that does this — could be `win-tracker` or a cron in another service. Task: audit + decide whether to keep auto-X or route through drafter.

**Track-record publication guardrail:** User said "we don't have enough track record currently for marketing asset, it will come." Therefore **do not publish track-record content until a sample-size threshold is met** (suggestion: 30 closed V5.3 trades OR 60 calendar days, whichever later).

**Definition of Done (Phase 5):**
- Operator receives a single email at 09:30 ET each trading day with X + Reddit drafts ready to copy-paste.
- **Pick-accuracy validator (audit #7):** before the email fires, a post-LLM check asserts the draft's mentioned ticker + direction exactly equals the Firestore `todays_pick/{scan_date}` doc. On mismatch, hold the draft and alert. Never publish a hallucinated ticker.
- **Realized-only filter** applied to `signal_performance` SQL; documented in the drafter's source.
- Weekly track-record email sent Sundays only if N≥30 closed V5.3 trades (user confirmed: "we don't have enough track record currently").
- **Secrets invariant:** Mailgun + Gemini API keys mounted from Secret Manager.

**G-Stack review (Phase 5):** Not required (content only, no execution). But the validator is the insurance against drafts falsely claiming a picked ticker.

---

## 4. Cross-cutting concerns

### 4.1. "Source of truth for the V5.3 pick"

Five surfaces now answer "what did GammaRips pick today?":
1. `signal-notifier` email (existing — authoritative)
2. Webapp banner (Phase 1)
3. WhatsApp push (Phase 2)
4. MCP `get_todays_pick` (Phase 3)
5. GTM drafts (Phase 5)

**All five must give the same answer.** To enforce this, Phase 1 should extract the gate+rank SQL into a shared template or library function, not duplicate the filters in each surface:

- Option A: move the V5.3 filter SQL into a shared string constant in `libs/v53_gates/query.py`, imported by signal-notifier, MCP, and (for reporting) forward-paper-trader
- Option B: after enrichment completes, compute the V5.3 pick once and write it to Firestore `todays_pick/{scan_date}` — all five surfaces then just read that doc

**Recommendation:** Option B. Removes SQL duplication, gives the webapp a trivial read pattern, and makes the pick append-only auditable (you can see exactly what was picked on each date without re-running the filter).

### 4.2. Legal / compliance track

These need a dated DECISION record + a disclaimer policy before Phase 2 ships:
- Subscriber agreement copy (paper-trading, educational, not advice)
- Risk disclosure on webapp footer + every WhatsApp push
- Stripe Acceptable Use confirmation for financial-adjacent content
- Cancellation + refund policy

**Owner:** Evan + counsel. Blocker for Phase 2.

### 4.3. Observability

Every push, every MCP call, every draft should be traceable:
- `libs/trace_logger` already exists — extend to cover WhatsApp push attempts (success/fail, latency)
- Add Firestore `content_drafts` collection for GTM drafts (so you can see later what was recommended vs. what you actually posted)

---

## 5. Timeline

Assuming user is the sole developer and Claude assists:

```
Week 1 (Apr 21–25):  Phase 1 (webapp V5.3 alignment) + Phase 3 fixes to existing MCP tools
Week 2 (Apr 28–May 2): Phase 2 (paywall/WhatsApp) draft + compliance track kickoff
Week 3 (May 5–9):    Phase 3 new MCP tools; Phase 4 arena reshape
Week 4 (May 12–16):  Phase 5 GTM drafter + X/Reddit pipeline
Week 5+:             Soft launch with 5–10 beta subscribers; iterate
```

Track record milestone for marketing claims: end of May (≥30 closed V5.3 trades).

---

## 6. G-Stack review summary (v2)

Per CLAUDE.md's governance: any change that touches execution or gate logic requires `gammarips-review` pre-deploy audit.

| Phase | gammarips-review required? | Reason |
|---|---|---|
| 1.0 — Firestore `todays_pick` writer | **YES** | Writer lives in signal-notifier; gate logic must not drift |
| 1 — Webapp | No (but `docs/TRADING-STRATEGY.md` update reviewed via DECISIONS) | Display-only |
| 2 — WhatsApp paywall | **YES** | Adds to signal-notifier + new whatsapp-notifier service; rule file touched |
| 3 — MCP refresh | **YES** | `get_todays_pick` must read the same Firestore doc, not reimplement gates |
| 4 — Arena reshape | No (Option A, post-close commentary only) | No gate logic change |
| 5 — GTM drafter | No | Content only; validator asserts no drift from `todays_pick` |

**Audit sign-off record:** initial audit complete 2026-04-20 (see `docs/DECISIONS/2026-04-20-v5-3-surface-and-monetization.md`). Re-review required on Phase 2 + Phase 3 specifically, with the completed code diffs, before deploy.

---

## 7. Open questions for Evan before execution

1. **Audit sign-off:** confirm the v2 amendments (Phase 1.0 writer, in-trader push banned, arena gated to post-close, strategy doc publication-timing section, realized-only GTM filter) align with your intent before Phase 1.0 work starts.
2. **X auto-posting:** is the current X poster in `win-tracker` or elsewhere? Keep it auto (for closed-trade highlights only) or route through GTM drafter for operator approval?
3. **Arena post-close reshape:** change the debate to run at 16:30 ET Mon–Fri, retrospectively commenting on the day's V5.3 trade (entry, current status, thesis)? Or kill entirely?
4. **Beta subscribers:** do you have 3–5 people willing to pay $29 to test the WhatsApp push for 30 days before general launch?
5. **Compliance counsel:** is there a lawyer on retainer, or one we need to engage before Phase 2 ships? The real-money-vs-paper discipline language needs legal sign-off.
6. **OpenClaw contract:** what's the exact send-message API surface? (Shapes the `whatsapp-notifier` spec.)
7. **Real-money-skip logging:** are you ok with the operator-discipline rule requiring you to log every skip to `real_money_skips/{scan_date}`? It's a small ongoing cost but it protects any future marketing claim.

---

## 8. Next actions for Claude (upon approval)

1. Create `docs/DECISIONS/2026-04-20-v5-3-surface-and-monetization.md` as the accountable decision record capturing this plan + audit findings + v2 amendments.
2. Ask Evan to sign off on Section 7 questions.
3. On sign-off, execute Phase 1.0 (schema + signal-notifier writer + drift tripwire).
4. Re-invoke `gammarips-review` on the actual code diff for Phase 1.0 before deploy.
5. Proceed phase-by-phase per the timeline in Section 5.
