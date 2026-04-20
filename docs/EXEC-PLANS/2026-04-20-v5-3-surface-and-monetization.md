# EXEC-PLAN: V5.3 Surface Alignment + Monetization

**Author:** Evan + Claude (session 2026-04-20)
**Status:** **v2 — amended after gammarips-review audit 2026-04-20.** Pending Evan sign-off on Section 9 changes before Phase 1.0 starts.
**Scope:** Five workstreams that bring the non-trading surfaces (webapp, MCP, arena, GTM, payments) into lockstep with the V5.3 "Target 80" execution policy and unlock the $29/mo WhatsApp tier.

**Change log:**
- **v1 (2026-04-20):** initial draft
- **v2 (2026-04-20):** post-review amendments — Phase 2 push moved out of forward-paper-trader (BLOCKER), `todays_pick` writer pinned to signal-notifier (HIGH), drift tripwire added (HIGH), arena commentary gated to post-market (HIGH), real-money-vs-paper discipline rule proposed for TRADING-STRATEGY.md (HIGH), Secret Manager mandate added to all phases (LOW), sequencing within Week 1 spelled out (LOW).
- **v2.2 (2026-04-20, later):** **execution order swapped — Phase 3 (MCP refresh) ships BEFORE Phase 2 (WhatsApp paywall).** Rationale: Evan probed whether $29/mo was justifiable when the webapp reveals the same info simultaneously. Honest answer is the chat-with-agent feature (Phase 3 `get_todays_pick`, `get_open_position`, win-rate) is the real moat — push alone prices at $5–10/mo, push + agent-chat with live Polygon data prices at $29–49/mo.
- **v2.3 (2026-04-20, later still):** pricing + freemium gating research landed. **Pricing moves from intuition $29 to a two-tier $19 Starter / $39 Pro** (research showed $29 undersells by ~4x vs peers and sits at the low edge of the prosumer anchor zone). **Freemium gating strategy pinned** (Section 6.4): daily pick + signals + report stay fully free; arena full transcript, debrief pages, and full performance ledger get soft-gated; AI chat, live open-position tracker, personal watchlist, trade journal, alert rules, CSV export get hard-gated behind subscription. Phase 3 expanded to include paid-tier webapp features (AI chat wiring + live position page) as MVP; watchlist/journal/alerts deferred to post-launch iteration.
- **v2.4 (2026-04-20, end of day):** Evan clarified the chat UX — **AI chat lives only in the private WhatsApp group, not on the webapp**. Behavior: agent stays silent by default, responds only when `@mention`ed; other subscribers see every chat turn, which amortizes cost and builds community (one ask → everyone benefits). Consequences:
    - Phase 3b webapp `/chat` widget is **dropped entirely**.
    - Phase 3b webapp `/positions` is **deferred to post-launch iteration** — subscribers can just ask the agent "what's my open position?" via WhatsApp, which reads `get_open_position` from MCP. No duplicated webapp surface at launch.
    - **Phase 2 (OpenClaw wiring) is now the single launch blocker** for the paid tier. Phase 2 scope expands to include the @mention-aware chat agent, its system prompt, and compliance guardrails.
    - ✅ Phase 3a (MCP tool refresh) remains the prerequisite — the OpenClaw agent needs those tools via `mcporter`.
    - Revised execution order: 1.0 → 1 → 3a → 2 → 4 → (post-launch) 3b → 5.
- **v2.5 (2026-04-20, post-audit):** `gammarips-researcher` ledger diagnostic surfaced a wrong mental model in my original Phase 3a `get_open_position` tool.
    - Root cause: **`forward-paper-trader` is a batch simulator** that runs at 16:30 ET Mon–Fri and processes scan_date = today minus 4 trading days. Every ledger row is terminal by the time it's written — there's no "live open position" in the ledger by design.
    - Also found a bug I shipped: `get_position_history` SELECTed a nonexistent `exit_price` column; ledger encodes outcome via `realized_return_pct` + `underlying_exit_price`.
    - **Fix (already deployed, `gammarips-mcp-00022-xhs`):** `get_open_position` now returns a composite `{pending_pick, awaiting_simulation, most_recent_closed_trade, explanation}` sourced from Firestore `todays_pick` + a lookup of scan_dates still inside their 3-day hold window + the latest `entry_price IS NOT NULL AND exit_reason NOT IN ('INVALID_LIQUIDITY','SKIPPED')` ledger row. `get_position_history` drops `exit_price` and excludes `INVALID_LIQUIDITY` rows.
    - **Consequence for Phase 2 chat agent:** the system prompt must frame the chat answer in those three pieces. "What's my open position?" returns "next trade tomorrow at 10:00 ET is FIX BULLISH (or today's skip reason); last closed trade was WPM BULLISH TIMEOUT at +0.42%; 3 scan_dates in the 3-day hold window awaiting simulator reconciliation." NEVER claim a live unrealized P&L against a stale row.
    - **Still open (deferred, lower priority):** the ledger has a backlog of NULL-entry rows with `exit_reason = 'INVALID_LIQUIDITY'` where the option contract had no bars at 10:00 ET day-1. Auditor recommends the trader write a placeholder `exit_timestamp` + `realized_return_pct = 0` on those rows rather than leaving everything NULL. Needs a `gammarips-engineer` diff + DECISIONS/ note. Not launch-blocking — downstream queries already filter by `exit_reason NOT IN ('INVALID_LIQUIDITY','SKIPPED')`.

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

### Phase 1.0 — Pre-work: `todays_pick` schema + deterministic notifier SQL + writer (0.5 day, BLOCKS Phase 1)

**v2.1 addition — deterministic tiebreaker in `signal-notifier/main.py`.** The current `ORDER BY CASE WHEN direction='BULLISH' THEN call_dollar_volume ELSE put_dollar_volume END DESC` with `LIMIT 1` is **non-deterministic on ties** — if two rows have identical dollar volume to the cent, BigQuery picks arbitrarily. Replace with a fully-deterministic 5-key sort:

```sql
ORDER BY
  CASE WHEN direction = 'BULLISH' THEN call_dollar_volume
       ELSE put_dollar_volume END DESC,     -- primary: directional UOA
  overnight_score DESC,                      -- higher scanner confidence
  volume_oi_ratio DESC,                      -- fresher flow
  recommended_spread_pct ASC,                -- tighter execution
  ticker ASC                                 -- alphabetical — last-resort deterministic
LIMIT 1
```

This lands together with the `todays_pick` writer in the same `signal-notifier` diff so the doc always reflects a deterministic pick.


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

**Phase 1.0 Definition of Done (status as of 2026-04-20):**
- ✅ Schema doc frozen in this section before any reader code written.
- ✅ Writer landed in `signal-notifier/main.py` (`write_todays_pick_doc()` + `get_next_trading_day()` helper). Deployed as revision `signal-notifier-00007-pv9` 2026-04-20.
- ✅ Empty-state cases covered: `no_candidates_passed_gates`, `regime_fail_closed`, `vix_backwardation` — each writes a `has_pick: false` doc atomically before returning.
- ✅ Deterministic 5-key `ORDER BY` added; `overnight_score` selected in the query to feed the tiebreaker.
- ✅ Integration-verified: manual trigger for `scan_date=2026-04-17` produces `todays_pick/2026-04-17 = {has_pick: true, ticker: "FIX", direction: "BULLISH", effective_at: 2026-04-20T14:00:00Z, policy_version: "V5_3_TARGET_80"}` matching the pinned schema.
- 🟡 Formal unit test deferred — signal-notifier has no existing test harness; the live integration verify above is the de-facto check. Adding a shape test is Phase 7 (CI hardening) scope.
- 🟡 Drift tripwire **deferred to Phase 3.0.** Rationale: drift is only possible once a second, independent reader exists (MCP `get_todays_pick` in Phase 3). In Phase 1.0 the Firestore doc and the operator email are produced atomically from the same service call — no drift is constructible. The tripwire becomes valuable at the moment MCP lands.

**G-Stack review (Phase 1.0):** ✅ Applied during plan v2 audit. Writer diff preserves gate logic (query unchanged on filter clauses; only ORDER BY extended and SELECT widened by one column). Fail-closed Firestore-write-before-email invariant upheld.

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

### Phase 2 — WhatsApp paywall + @mention chat agent (v2.4, now the launch blocker)

> ⚠️ **v2 amendment (BLOCKERS #1, #2):** Audit flagged that `forward-paper-trader/main.py` is a **batch simulator that runs 16:30 ET Mon–Fri**, not a live-at-10:00-ET service. Wiring the push inside the trader means the ping fires hours late — a product-killing defect. The push must come from the service that fires **at the decision time** for each event.
>
> Also: no synchronous Firestore query or outbound HTTP in the trader. `.claude/rules/forward-paper-trader.md` now gets a new rule prohibiting this.

**Goal:** Paying $29/mo subscribers get a WhatsApp ping at:
- **Entry-setup time (09:00 ET day-1)** — immediately after signal-notifier decides the day's pick. "Today's trade at 10:00 ET: BUY FIX $580C 05/22. Arm stop -60%, target +80%."
- **Exit time (day-3)** — from a separate 15:50 ET cron that reads the ledger's pending exits and fires one last "Close FIX now" push.

Intraday target/stop fills are NOT pushed at the moment of fill because the trader simulates them post-hoc; subscribers already armed their GTC orders at entry and will be notified by their broker, not by us. This is honest — the paywall value is the daily entry timing, not intraday event streaming.

**Architecture (v2.1 — OpenClaw provided a webhook endpoint; simpler than v2's Pub/Sub approach):**

OpenClaw exposes `POST http://<gateway>:18789/hooks/agent` with `Authorization: Bearer <HOOKS_TOKEN>` and a JSON body containing `{message, name: "GammaRips", deliver: true, channel: "whatsapp", to: <GROUP_JID>}`. That single endpoint handles group routing for us, so we don't need a Pub/Sub + separate consumer service. Instead, each scheduled event POSTs directly, fire-and-forget.

```
Stripe checkout → webapp Stripe webhook → Firestore users/{uid}.subscription = {tier: "paid", expires_at: TS, whatsapp_e164: "+1..."}
  (only needed once we want per-user messaging or paywall inside the OpenClaw agent;
   for v1 of Phase 2 we use a single shared private WhatsApp group, which is naturally
   gated by who we invite — Stripe just controls who gets the invite.)

09:00 ET signal-notifier/main.py:
  ▶ WRITE Firestore todays_pick/{scan_date}
  ▶ (existing) send operator email
  ▶ NEW: POST OpenClaw /hooks/agent with today's entry message
       (5s timeout, wrapped in try/except, logs failure — MUST NOT block email or raise)

09:15 ET arena-verdict service (NEW, Phase 4 Option C):
  ▶ READ Firestore todays_pick/{scan_date}
  ▶ run 3-agent debate (Claude + Grok + Gemini)
  ▶ UPDATE todays_pick/{scan_date} with arena_verdict + vote_count + reasoning
  ▶ POST OpenClaw /hooks/agent with verdict update ("🟢 TAKE 4/5" etc.)

15:50 ET exit-reminder (NEW tiny Cloud Run + scheduler):
  ▶ QUERY forward_paper_ledger where exit_timestamp IS NULL AND scan_date <= today - 3 trading days
  ▶ for each open position: POST OpenClaw /hooks/agent with "close FIX now"

forward-paper-trader/main.py: UNCHANGED in this phase. No new imports, no Firestore query,
  no outbound HTTP, no POLICY_VERSION touch. Audit rule #2 holds.
```

**Secrets:** `OPENCLAW_HOOKS_TOKEN`, `OPENCLAW_GATEWAY_URL`, `OPENCLAW_GROUP_JID` mounted from Secret Manager. Never in env plaintext.

**Paywall mechanism (v2.1 — simpler than per-user messaging):**
For the v1 launch, the paywall IS the WhatsApp group invitation. Stripe subscription success triggers a webhook that appends the user's phone number to Firestore `whatsapp_allowlist/{phone_e164}`. Evan (or an OpenClaw automation) reads that allowlist and invites those numbers to the private group. Cancellation sets `active: false`. No per-message gating needed for Phase 2 push — the group itself is gated.

**Phase 3 paywall (upgraded mechanism, informed by OpenClaw research):**
When we ship the chat experience (paid users ask questions in the group and Claude answers via MCP), per-message gating becomes needed. The right pattern is a small **OpenClaw plugin** (`openclaw/plugin-sdk`, docs at `/home/user/openclaw/docs/tools/plugin.md`) that inspects every inbound `senderId` (phone_e164) against `whatsapp_allowlist`:
- If sender is paid + active: let the agent run with MCP tools
- If sender is unknown / unpaid: short-circuit reply with a paywall note + Stripe checkout link
This is a ~100-line TypeScript plugin living in Evan's OpenClaw install, NOT a separate Cloud Run service. Keeps auth logic close to the channel it enforces.

**Specific edits:**

| Change | File | Purpose |
|---|---|---|
| Stripe webhook handler | `/home/user/gammarips-webapp/src/app/api/stripe/webhook/route.ts` (already exists) | On success, append user's WhatsApp number to Firestore `whatsapp_allowlist/{phone_e164}`. On cancellation, set `active: false`. |
| **todays_pick writer** | `signal-notifier/main.py` (Phase 1.0 — already scheduled) | Writes `todays_pick/{scan_date}` Firestore doc before email send |
| **OpenClaw entry POST** | `signal-notifier/main.py` (Phase 2) | After Firestore write + before/after email: non-blocking POST to `$OPENCLAW_GATEWAY_URL/hooks/agent` with Bearer auth. Timeout 5s. try/except wrapper. Log success/failure via `libs/trace_logger`. Never raises. |
| **OpenClaw exit-reminder cron (new service)** | `exit-reminder/main.py` (tiny new Cloud Run, Python/Flask) | Single endpoint; queries `forward_paper_ledger` for open positions; POSTs one OpenClaw message per position. Deploys via `deploy.sh` + Cloud Scheduler `50 15 * * 1-5` ET. |
| **OpenClaw arena-verdict POST** | `agent-arena/main.py` → modified to Option C (Phase 4) | After verdict decided, POST to same OpenClaw endpoint with verdict update |
| **Forbid in-trader HTTP** | `.claude/rules/forward-paper-trader.md` | Add rule: "NEVER add synchronous outbound HTTP or user-notification calls to this service. Paper-trader is the ledger of record, nothing else. All subscriber messaging fires from `signal-notifier`, `agent-arena`, and `exit-reminder` only." |
| **Compliance disclaimer** | OpenClaw message template in each caller | Every push includes: *"Paper-trading performance, educational only. Not investment advice."* Appended to message string. |
| **Secrets** | Secret Manager | `OPENCLAW_HOOKS_TOKEN`, `OPENCLAW_GATEWAY_URL`, `OPENCLAW_GROUP_JID`, `STRIPE_WEBHOOK_SECRET` — never env-var plaintext. |

**Phase 2 addition (v2.4) — @mention-triggered agent in the WhatsApp group:**

This is the main paid differentiator. Lives entirely inside OpenClaw; the webapp has no chat surface. Design:

| Aspect | Decision |
|---|---|
| **Trigger** | Agent responds only when the message contains an `@mention` of its configured handle (e.g. `@GammaRips`). Silent otherwise — human-to-human chat flows undisturbed. |
| **Identity gate** | OpenClaw plugin (`openclaw/plugin-sdk`, ~100 LOC) checks `senderId` (phone_e164) against Firestore `whatsapp_allowlist`. If not active-paid, short-circuit with a paywall note + Stripe checkout link instead of invoking the agent. |
| **MCP tool access** | Agent uses the bundled `mcporter` skill to call our Cloud Run MCP at `https://gammarips-mcp-406581297632.us-central1.run.app/sse`. Phase 3a tools (`get_todays_pick`, `get_open_position`, `get_position_history`, `get_win_rate_summary`, `get_signal_detail`, `get_enriched_signal_schema`, `get_freemium_preview`, `get_daily_report`, `web_search`) are all available. |
| **Model** | Claude Haiku 4.5 with Anthropic prompt caching on system prompt + MCP tool descriptions (see §4 above for model-cost lever). |
| **Visibility** | All chat turns are visible to every member of the paid group. This is by design — one user's question + agent answer benefits the whole community and amortizes the per-message cost. |
| **Context window** | Stateless per-turn — agent does NOT maintain conversational memory across messages in v1. If a user asks a follow-up, they must re-include needed context. Revisit after first month of usage data. |

**Compliance guardrails on the agent's system prompt (v2.4 requirement):**

To stay inside the SEC *Lowe* publisher exclusion, the @mention-triggered agent must produce **impersonal content** — explanations of the engine's output, the methodology, and public data — not personalized investment advice. The system prompt explicitly instructs:

```
You are GammaMolt, the AI concierge for GammaRips. Paid members ask you about
GammaRips' daily V5.3 pick, the engine's methodology, historical paper-trading
performance, and flow data. You have MCP tools to read the canonical pick, live
open paper positions, realized trade history, and the enriched signals table.

You DO answer:
  - "What did GammaRips pick today and why did it clear the V5.3 gates?"
  - "What's the status of the engine's trades right now?" — report the next trade (from Firestore `todays_pick`), how many scan_dates are still inside their 3-day hold window awaiting simulation, and the most recent closed trade's outcome. The paper-trader is a batch simulator — there is no live unrealized P&L; never fabricate one.
  - "How has the engine done over the last 30 days?"
  - "Walk me through the enriched data for FIX / any ticker."
  - "What's in the daily report?"

You DO NOT answer:
  - Anything that depends on the user's personal account, capital, tax, or risk
    tolerance ("should I size 2 contracts?", "is this safe for my IRA?").
  - Personalized trade recommendations ("take this one", "skip that one").
  - Any instruction that implies fiduciary or advisory role.

When asked an out-of-scope question, respond:
  "I can walk you through the engine's methodology and current data, but I'm
   not your advisor and can't give personalized trade guidance. Ask your
   broker, a licensed CFP, or use the public gammarips.com methodology docs."

Every response ends with: "Paper-trading performance, educational only.
Not investment advice."
```

Log every agent response to Firestore `chat_log/{group_id}/{turn_id}` with `senderId`, `prompt`, `response`, `mcp_tools_called`, `model`, `timestamp`. Audit trail for both compliance and product-iteration signal.

**Legal / disclaimer hygiene (v2.1 — no counsel at this scale, per Evan):**

Legal basis: *SEC v. Lowe (1985)* + Investment Advisers Act §202(a)(11)(D) "publisher exclusion" protects bona fide publishers/newsletters as long as the content is (a) same for all subscribers (impersonal), (b) published on a regular schedule, (c) not customized to any subscriber's financial situation, and (d) the publisher does not take custody of subscriber funds. Our WhatsApp push and webapp meet all four. Counsel is not needed at pre-scale.

Checklist (must all be true before Phase 2 ships):
1. **Uniform content.** Every paid subscriber gets the identical push. No personalization beyond a `$user_name` greeting.
2. **Scheduled, not event-responsive.** Push fires from notifier + exit-reminder cron. Never in response to "should I take this?" from a user — that would be personalized advice, which is outside the publisher exclusion.
3. **Disclaimer on every push and every webapp page:** `"Paper-trading performance, educational content only. Not investment advice. You trade your own account; GammaRips does not manage your money. Past performance is not a guarantee of future results."`
4. **No fund custody.** Stripe collects subscription only. GammaRips never receives customer trading capital. (Phase 2 DoD confirms.)
5. **Stripe Acceptable Use review:** read [stripe.com/legal/restricted-businesses](https://stripe.com/legal/restricted-businesses) once before launch; "educational trading content" is accepted; "signal services" are accepted with proper disclosures. Not "investment advisers."
6. **WhatsApp Business API rules:** OpenClaw is a private group (opt-in via Stripe-confirmed phone number). Bulk messaging rules respected.
7. **Honest marketing:** only publish paper-trading stats; label them "paper-traded" every time; never imply real-money results we don't have data for.

Escalate to counsel ONLY if any of: (a) >500 paid subs and a state-level RIA challenge appears, (b) cease-and-desist from any regulator, (c) we want to start publishing real-money track record as marketing, (d) we start managing subscriber funds (we won't).

**Real-money-skip logging — deferred:** the original v2 plan proposed logging operator real-money skips during the 30-day OOS window. Evan confirmed no real-money trades to log at launch. This moves to Phase 5 as an optional Firestore collection `operator_trades/{scan_date}` with a single "Took it? Y/N + reason" control on the webapp, to be enabled WHEN we want to publish real-money track record (per the plan's existing track-record milestone: ≥30 closed V5.3 trades OR 60 days).

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

### Phase 3 — MCP refresh + paid-tier webapp MVP (5–7 days, now ships BEFORE Phase 2)

**Goal:** the MCP tools are V5.3-correct and support the paid chat-agent UX. **Scope expanded in v2.3** to include the paid-tier webapp features that make $39/mo defensible — the AI chat and the live open-position tracker. Watchlist, trade journal, alert rules, CSV export are deferred to post-launch iteration.

This phase is now the longest and most important. The paywall does not launch (Phase 2) until this is in place and tested end-to-end with at least one beta user.

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

**OpenClaw MCP integration path (v2.1 — from OpenClaw research):**
OpenClaw is a multi-channel AI gateway (MIT TS/Node, self-hosted, Baileys-based WhatsApp) running `pi-agent-core` as its agent loop. It does **not** implement a native MCP host/client — instead, it bundles the `mcporter` skill (`/home/user/openclaw/skills/mcporter/SKILL.md`) which is a CLI that shells out to any MCP server over HTTP/stdio. Our Cloud Run MCP at `https://gammarips-mcp-406581297632.us-central1.run.app/sse` is reachable via `mcporter call gammarips.<tool> arg=value`.

To wire it up (Phase 3 deployment):
1. Enable `mcporter` skill in OpenClaw config
2. Register our SSE endpoint so `mcporter` knows about `gammarips.*` tools
3. Ensure the API-key auth on our MCP is pluggable into `mcporter`'s call format (header-based Bearer)
4. Confirm the tool latency is acceptable for an in-group chat interaction (target <5s per tool call)

**Model cost lever (v2.2 — Evan's call):** the chat agent must NOT be routed to a flagship model for every user message at $29/mo, or per-user economics break. OpenClaw supports multiple providers — the right default for this use case is a **cheap-but-tool-capable** model:

| Option | In/Out $/M | Fit |
|---|---|---|
| **Claude Haiku 4.5** | 0.25 / 1.25 | Best tool-use reliability in its tier; strong for MCP Q&A with structured responses. Default recommendation. |
| **Gemini 2.5 Flash** | 0.075 / 0.30 | Very cheap with native thinking; already in use by GammaRips for enrichment + report generation, so Evan has ops experience. Solid alternative. |
| **DeepSeek V3 (via HF)** | ~0 (free tier) | Acceptable tool use; latency and rate-limit risk at scale. |
| **Claude Sonnet 4.6 / Opus 4.7** | ≥3.0 / ≥15.0 | Overkill for Q&A about a single daily pick; reserve for rare escalation. |

Also supported: OpenClaw's **setup-token** path reuses Evan's existing Claude Pro/Code subscription as an alternative to pay-per-token API. Useful for dev/test; at real scale, a dedicated API key with OpenClaw's built-in prompt caching (`short`=5min, `long`=1h) is more predictable. Per-user monthly cost target: ≤$2 at 50 questions/mo → leaves $27 of $29 as gross margin.

Decision: default to **Haiku 4.5 via Anthropic API** with prompt caching on the system prompt + MCP tool descriptions. Revisit after first month of real usage data.

**v2.4 amendment — chat is WhatsApp-only, not webapp.** The former Phase 3b `/chat` widget is DROPPED. The former `/positions` webapp page is DEMOTED to post-launch iteration. The paid moat lives entirely in OpenClaw (spec in Phase 2 above).

**Remaining Phase 3b scope (soft-gating UX; not launch-blocking):**
- Arena page (`/arena`) — `backdrop-filter: blur(6px)` on round-by-round transcript past 2 read-throughs/day (localStorage counter). Overlay CTA "Unlock full debate (Pro) →". Headline verdict stays free for funnel.
- Debrief pages (`/signals/[ticker]/debrief`) — time-delay gate: paid users see immediately, free users see after 48h.

**Post-launch iteration (Phase 3c, ships after paid tier is live and we have real usage signal):**
- Webapp `/positions` live tracker (richer second surface for open positions; v1 is "ask the agent in WhatsApp").
- Personal watchlist page.
- Trade journal (user-entered real-money fills vs paper).
- Alert rules per ticker.
- CSV export.
- Email digest tier differentiation (daily for paid vs weekly for free).

**Definition of Done (Phase 3a — MCP tools only, completed 2026-04-20):**
- ✅ `get_enriched_signals` description corrected (stale "score >= 6" claim removed).
- ✅ `get_win_rate_summary` direction casing normalized via `UPPER()`.
- ✅ 5 new MCP tools deployed (`get_todays_pick`, `get_freemium_preview`, `get_open_position`, `get_position_history`, `get_enriched_signal_schema`).
- ✅ Live verified via `/rpc` JSON-RPC smoke tests; `get_todays_pick` returns FIX BULLISH + full payload; all tools reachable by name.
- Deployment: `gammarips-mcp-00021-9tp` with `POLYGON_API_KEY` mounted.

**Definition of Done (Phase 3b — soft-gating, ships with or shortly after Phase 2):**
- Arena full-transcript blur + unlock CTA in production; read-through counter works cross-session via localStorage.
- Debrief pages: paid users see immediately, free users see after 48h (Firestore `signal_debriefs/{scan_date}_{ticker}.published_at` vs `users/{uid}.subscription.tier`).
- No regression on acquisition funnel (free users still reach daily pick + report + signals list without friction).

**G-Stack review (Phase 3):** **REQUIRED.** `get_todays_pick` must mirror signal-notifier gates exactly. Any drift = data mismatch between email, WhatsApp push, webapp banner, and chatbot answer. gammarips-review must audit the SQL.

---

### Phase 4 — Arena decision (0 or 1–2 days)

Agent Arena's role under V5.3 is the most ambiguous workstream.

**Findings:**
- Zero downstream execution consumer
- 0% agreement with signal-notifier over 21 trading days (they optimize different objectives)
- LLM cost $150–250/mo
- Webapp currently renders arena as "spectacle / education"

**Three options (v2.1 — adds Option C per Evan's direction 2026-04-20):**

**Option C — Verdict debate on today's deterministic pick (RECOMMENDED, Evan-selected):**
- Runs **09:15 ET** Mon–Fri — after `signal-notifier` writes `todays_pick` at 09:00, before the 10:00 ET entry window.
- Input: `todays_pick/{scan_date}` (the one V5.3 pick). Skip the day if `has_pick == false`.
- Question: "Given the enriched signal data for today's pick (thesis, technicals, catalyst, VIX regime), should operator take this trade at 10:00 ET? Answer: TAKE / CAUTION / SKIP with one paragraph of reasoning."
- Reduce to **3 agents** (Claude = Risk Manager, Grok = Momentum, Gemini = Contrarian). Drops LLM cost to ~$60/mo and runtime to <20s.
- **One round** (each agent votes independently). No attack/defend/final — that cycle is redundant for a single-ticker Y/N decision.
- Output: extends `todays_pick/{scan_date}` with `arena_verdict`, `arena_vote_count`, `arena_top_reasoning`, `arena_debate_ref`. (The full transcript still goes to `arena_debates/*` for the webapp "read the whole debate" affordance.)
- **Cloud Scheduler:** new job `agent-arena-verdict` on `15 9 * * 1-5` ET. Delete the existing 06:00 ET arena-trigger (the 06:00 cron becomes useless since arena now needs the `todays_pick` doc).
- Webapp + WhatsApp push render the verdict prominently.

**Option A — Post-close retrospective commentary (from v2, deprecated by Option C):**
- Same arena but runs at 16:30 ET Mon–Fri commenting on closed/in-progress trades. Avoids any pre-entry biasing. Lower product value (no real-time decision support). Retained as a fallback if Option C creates unacceptable paper-vs-real divergence during the OOS window.

**Option B — Kill:**
- Remove service, scheduler, and downstream tables after 90-day archive. Saves ~$200/mo + Cloud Run. Rebuild cost is a few engineer days if needed.

**Recommendation:** Option C. Rationale: the original audit finding #6 correctly identified that a pre-entry arena CAN bias real-money skips and cause paper-vs-real divergence. Evan is comfortable accepting that divergence IF we are transparent: the paper ledger stays full-coverage (takes every V5.3 pick regardless of arena verdict), and any future marketing claim makes the distinction explicit (`"paper: full-coverage +X%" vs "arena-filtered: took only TAKE-votes, +Y%"`). Option C preserves engagement, re-aligns arena with V5.3 product, and reduces cost.

**Paper-vs-real divergence transparency rule (v2.1 requirement for Option C):**
- `forward-paper-trader` keeps its existing policy: takes every V5.3 pick regardless of arena verdict. This is the **control.** No change to `POLICY_VERSION` or `POLICY_GATE`.
- New column added to `forward_paper_ledger` schema: `arena_verdict` (nullable: "TAKE" / "CAUTION" / "SKIP" / NULL for days arena didn't run). Written by the trader as metadata only — does NOT affect the decision to paper-trade. (Non-breaking schema change; existing consumers ignore it.)
- Any marketing output that cites paper performance MUST label it "paper (full-coverage)". If we later publish arena-filtered performance as a marketing claim, a separate column view is added (`is_arena_take_only`) — via SQL filter, not a second ledger.

**Definition of Done (Phase 4 — Option C):**
- Arena cost drops to ≤$60/mo (3 agents, 1 round).
- `todays_pick/{scan_date}` is extended (not replaced) with `arena_verdict`, `arena_vote_count`, `arena_top_reasoning`, `arena_debate_ref`.
- Scheduler job `agent-arena-verdict` cron `15 9 * * 1-5` ET. Old `agent-arena-trigger` (06:00 ET) is deleted.
- Webapp banner shows verdict label + vote breakdown + "read the debate" link.
- Paper ledger gains nullable `arena_verdict` metadata column. `forward-paper-trader` decision logic unchanged (takes every V5.3 pick — paper is the control).
- Marketing/track-record surfaces that publish performance always label the filter used ("paper, full-coverage" vs "arena-filtered").
- If we choose to kill instead: all `agent_arena_*` tables archived 90 days then deleted, scheduler removed, DECISIONS note written.

**G-Stack review (Phase 4):**
- **Required** for Option C: arena verdict becomes a USER-FACING verdict on whether to trade. Audit must confirm: (a) paper ledger decision is NOT affected by arena, (b) arena output is clearly labeled as opinion not execution, (c) no new LLM call path is on the paper-trader's critical path, (d) the schema column `arena_verdict` is metadata-only.
- Not required for Option A retrospective or Option B kill.

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

### 4.4. Pricing (v2.3)

Decided after competitive research across ~25 comparable products (Unusual Whales $48, Cheddar Standard $45, Cheddar Pro $99, OptionStrat Live $40, Benzinga Basic $37, FinChat Plus $29, Koyfin Plus $39, Discord signal groups $50–200, etc.). Key findings:

- **No direct competitor under $100/mo bundles what we're proposing** (curated daily pick + phone push + private community + AI chat agent). Feature-count-equivalent mix would cost ~$128 across three providers.
- **Prosumer price anchor** is **$39–49** (where users in this space have already been trained to say yes). $29 sits at the bottom edge of that zone and signals "hobbyist Substack" more than "serious research tool."
- **Industry norm is Free / Core / Pro** three-tier, ~$19 / $39 / $79.
- **7-day free trial** is the industry standard for this price point.

Adopted structure:

| Tier | Price | What's included | Target persona |
|---|---|---|---|
| **Free** | $0 | Full gammarips.com: today's V5.3 pick, full signals list, daily report, per-ticker deep dive, arena headline verdict + preview, win-rate summary stat | Browsers, newsletter readers, funnel top |
| **Starter** | **$19/mo** | Everything in Free + WhatsApp push of entry/exit + private WhatsApp group (no AI chat) | Price-sensitive retail who wants convenience |
| **Pro** | **$39/mo** | Everything in Starter **+ @mention-able AI chat agent inside the WhatsApp group** (ask about today's pick, your open position with live Polygon prices, 30-day win rate, historical ledger queries). Agent only replies when tagged — group chat stays human-first. Post-launch iteration adds webapp `/positions`, personal watchlist, trade journal. | Active retail with $5k–50k account — the core persona |
| **Pro Annual** | **$399/yr** | Same as Pro, priced at ~$33/mo effective | Committed subscribers |

**Launch tactics (from research):**
- **Founder pricing:** first 500 Pro subscribers lock in **$29/mo for life** (captures Evan's original intuition as a founder perk, rewards early believers, signals urgency without compromising future ARPU).
- **7-day free trial** on Pro. Free trial on Starter optional (maybe skip — low friction anyway).
- **No price raises in the first 6 months** of paid launch. Moving $29 → $39 later would churn early cohorts; starting at $39 with $29 founder lock-in is the cleaner path.
- **Grandfathering policy:** any future price increase applies only to new subscribers; active subs keep their price point.

**The AI chat is the moat that earns the $39 anchor.** Starter is a ladder rung — it catches users who object to $39 but want the push, and funnels them toward Pro on the next billing cycle when they realize they want the chat. Do NOT ship Starter on day one if the chat agent isn't live (Phase 3) — shipping only Starter at $19 locks in the wrong anchor.

---

### 4.5. Freemium gating (v2.3)

Content/feature-level decisions, informed by the Explore-agent report 2026-04-20. Rule of thumb: **gate features, not information.** Information is acquisition; features are paid.

**Keep fully free (acquisition surface):**
- Today's V5.3 pick (ticker, direction, contract, strike, DTE, mid, gate-evidence chips) — this is the publisher-exclusion-protected content and the funnel-top trust signal.
- Full daily report text (editorial narrative, themes, counts).
- Full signals list (`/signals`) with all bullish/bearish signals browsable.
- Full per-ticker deep dive (`/signals/[ticker]`) with thesis, engine flags, flow breakdown, recommended contract, technicals, news.
- FAQ, methodology docs, all disclaimers.
- Past daily-pick archive (date, ticker, result summary) — public track record is marketing.
- Win-rate hero stat ("Last 30 days: 6/10 hits, +X% avg, paper trading") — summary only.
- Arena headline verdict (TAKE / CAUTION / SKIP + vote count + first sentence of each agent's reasoning). Builds engagement.

**Soft-gate (preview / blur / time-delay):**
- **Arena full debate transcript** — blur past 2–3 read-throughs per day via localStorage counter, overlay CTA "Unlock full debate (Pro) →"
- **Per-trade debrief pages** — paid users see immediately after close; free users see 48h later.
- **Full performance ledger** — summary stat free; row-level entry/exit times + per-trade P&L = Pro.

**Hard-gate (requires subscription; WhatsApp group invite or webapp login):**
- **@mention-able AI chat agent INSIDE the private WhatsApp group** — the Pro moat. No webapp chat surface. Group is shared among all paid subscribers; one question benefits everyone.
- **Live open-position tracker** — v1 is "ask the agent in WhatsApp, it calls `get_open_position`" (no new UI). v2 post-launch adds a webapp `/positions` page as a richer second surface.
- **Personal watchlist** — save tickers, get notified when they appear in the next scan.
- **Trade journal** — log your own real-money entries/exits vs paper-trader.
- **Alert rules per ticker** — "notify me when AAPL appears with score > 6."
- **CSV export** — full historical ledger / signals / debates.
- **Daily email digest** (free tier limited to weekly).

**What NOT to gate (legal / trust floor):**
Ticker + direction of the daily pick, recommended contract spec, disclaimers, methodology, FAQ, past-pick archive with dates and outcomes. Gating these breaks SEC *Lowe* publisher exclusion and also kills the "see everything, trust us" thesis.

**Psychological posture:** soft blur + read-through counter > hard paywall. Contextual CTAs ("See your open position live →") > generic "Upgrade now" buttons. Social proof on the paywall ("X paying subscribers"). Avoid aggressive / spammy copy.

---

## 5. Timeline (v2.4 — chat is WhatsApp-only, Phase 2 is the launch blocker)

Assuming Evan is the sole developer and Claude assists. Execution order is **1.0 → 1 → 3a → 2 → 4 → (post-launch) 3b → 5**.

```
✅ Week 1 (Apr 20):  Phase 1.0 DONE (notifier todays_pick writer + tiebreaker).
                     Phase 1 DONE (webapp TODAY'S PICK banner + V3 premium UI removed).
                     Phase 3a DONE (MCP: 5 new tools + 2 fixes, live at gammarips-mcp-00021-9tp).

Week 2 (Apr 21–25):  Evan prerequisites for Phase 2 — create private WhatsApp group with
                     OpenClaw's linked number, get GROUP_JID, enable hooks config, mount
                     OPENCLAW_GATEWAY_URL / OPENCLAW_HOOKS_TOKEN / OPENCLAW_GROUP_JID
                     to Secret Manager. No code work blocks on Claude side.

Week 3 (Apr 28–May 2): Phase 2 start — OpenClaw direct-POST wiring from signal-notifier
                       (09:00 ET entry message) + new exit-reminder service (15:50 ET
                       day-3). OpenClaw paywall plugin (senderId vs whatsapp_allowlist).
                       mcporter skill registered against our MCP.

Week 4 (May 5–9):    Phase 2 cont. — @mention agent system prompt + compliance guardrails.
                       Stripe tier SKUs: Starter $19, Pro $39, Pro Annual $399, Founder
                       $29 lifetime lock for first 500. Stripe webhook → Firestore
                       whatsapp_allowlist. End-to-end beta with Evan + 1-2 friends.
                       Phase 3b soft-gating (arena blur, debrief delay) ships in parallel.

Week 5 (May 12–16):  Phase 4 arena Option C (pre-entry verdict debate at 09:15 ET, 3 agents,
                       extends todays_pick doc with arena_verdict field). Soft-launch Pro
                       tier publicly at $39/mo with 7-day free trial.

Week 6+:             Phase 5 GTM drafter; Phase 3c iteration (webapp /positions, watchlist,
                     journal, alerts, CSV, email digest tier); iterate on pricing + gating
                     from real usage signal.
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

## 7. Open questions for Evan before execution (v2.1 — updated 2026-04-20 after Evan sign-off)

**Resolved this session:**
- ✅ v2 audit amendments approved
- ✅ Compliance counsel NOT required at this scale — replaced with disclaimer hygiene checklist (Section 6.2)
- ✅ Arena repurpose: Option C (09:15 ET pre-entry verdict debate on today's V5.3 pick)
- ✅ Real-money-skip logging: deferred to Phase 5 (only needed when publishing real-money track record)
- ✅ Stripe subs: set up when we're ready to open paid tier; Phase 2 waits on this

**Resolved 2026-04-20 (later in session):**
- ✅ X poster located: `win-tracker/main.py:351-408` — Tweepy-based, fires on strong wins only. Keep as-is; new GTM drafter (Phase 5) adds auto-X posts for daily report summary, top-signals teaser, and arena verdict using same 4 X API creds.
- ✅ OpenClaw API contract received: `POST /hooks/agent` with Bearer, JSON body `{message, name, deliver: true, channel: "whatsapp", to: <GROUP_JID>}`. Architecture simplified — no Pub/Sub, no `whatsapp-notifier` service. Direct POST from `signal-notifier`, `agent-arena`, and new tiny `exit-reminder` service.
- ✅ Push vs pull decision: **Push** (Option A) — real-time delivery matters for V5.3's 09:00 → 10:00 ET window.
- ✅ OpenClaw stack understood (investigated install at `/home/user/openclaw`, v2026.2.9): MIT TypeScript gateway, Baileys WhatsApp + native group routing, `pi-agent-core` agent loop, first-class Claude (API key or setup-token), MCP integration via bundled `mcporter` skill (CLI shell-out). Phase 3 chat paywall will be a small OpenClaw plugin keyed on `senderId` vs Firestore `whatsapp_allowlist`, not a separate Cloud Run service.

**Still open:**
1. **Group creation (Evan action):** create the private WhatsApp group, add OpenClaw's linked number, get the GROUP_JID from OpenClaw, enable hooks config (`{"hooks": {"enabled": true, "token": "<secret>", "path": "/hooks"}}`) and share the `HOOKS_TOKEN` + `GATEWAY_URL` + `GROUP_JID` via Google Secret Manager (never in chat/plaintext).
2. **Beta subscribers:** who are the first 3–5 testers of the WhatsApp push when Phase 2 is ready? Not blocking 1.0 or 1.
3. **Disclaimer copy finalization:** confirm the disclaimer text in Section 6.2 step 3.

---

## 8. Next actions for Claude (upon approval)

1. Create `docs/DECISIONS/2026-04-20-v5-3-surface-and-monetization.md` as the accountable decision record capturing this plan + audit findings + v2 amendments.
2. Ask Evan to sign off on Section 7 questions.
3. On sign-off, execute Phase 1.0 (schema + signal-notifier writer + drift tripwire).
4. Re-invoke `gammarips-review` on the actual code diff for Phase 1.0 before deploy.
5. Proceed phase-by-phase per the timeline in Section 5.
