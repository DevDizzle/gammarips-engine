# MCP Chat Readiness Audit — GammaRips Pro ($39/mo @mention agent)

**Date:** 2026-04-20
**Auditor:** Claude (Opus 4.7) simulating Claude Haiku 4.5 @mention agent in WhatsApp group
**Endpoint tested:** `https://gammarips-mcp-406581297632.us-central1.run.app/rpc`
**Persona:** Part-time retail options trader, $10K account, just subscribed to Pro
**Scope:** 10 realistic questions + 1 refusal + 1 tool-chaining edge case

---

## 1. Executive summary

**Pro-tier ready? NO — fixable in 1–2 days.** The core moat tools (`get_todays_pick`, `get_open_position`, `get_win_rate_summary`, `get_signal_detail`, `get_daily_report`, `get_position_history`, `get_enriched_signal_schema`, `get_freemium_preview`) all return high-quality structured data that would produce a genuinely good paying-user experience. However two tools — `get_enriched_signals` with a `direction` filter and `web_search` — are broken, and three UX/system-prompt gaps would cause embarrassing chat turns on day one. None of these blockers are deep; they are one small server patch, one env var, and four concrete additions to the system prompt.

---

## 2. Grades table

| # | Question | Tool | Grade |
|---|---|---|---|
| 1 | What did GammaRips pick today? | `get_todays_pick` | WORKS |
| 2 | Why did you pick that one over OKLO? | `get_signal_detail` x2 | WORKS |
| 3 | What's the current status of my paper trade? | `get_open_position` | WORKS (with one phrasing nit) |
| 4 | How has GammaRips done over the last 30 days? | `get_win_rate_summary` | WORKS (needs framing) |
| 5 | Top bullish signals for today? | `get_enriched_signals(direction="bull")` | **BROKEN** (filter returns []) |
| 6 | What's in the daily report? | `get_daily_report` | WORKS |
| 7 | Walk me through the thesis for FIX. | `get_signal_detail` | WORKS |
| 8 | What fields do you have for signals? | `get_enriched_signal_schema` | WORKS |
| 9 | Last closed trade and how did it do? | `get_position_history(limit=1)` | WORKS |
| 10 | Skip day coming? What's the VIX telling you? | `web_search` + `get_todays_pick` | **BROKEN** (web_search env missing) |
| E1 | Refusal: should I size 2 or 3 contracts? | *(none)* | WORKS if system prompt present |
| E2 | Compare today's pick to last week's. | `get_todays_pick` x2 (chain) | AWKWARD (no `scan_date` history for `todays_pick`; see Open Issues) |

---

## 3. Detailed walkthroughs

### Q1. "What did GammaRips pick today?"
- **Tool:** `get_todays_pick` (canonical single-source-of-truth per tool description).
- **Raw:** `{"has_pick": true, "ticker": "FIX", "direction": "BULLISH", "recommended_contract": "O:FIX260515C01780000", "recommended_strike": 1780.0, "recommended_mid_price": 70.55, "overnight_score": 4, "vol_oi_ratio": 4.5, "moneyness_pct": 0.0785, "vix_now_at_decision": 17.48, "vix3m_at_enrich": 20.51, "policy_version": "V5_3_TARGET_80", "scan_date": "2026-04-17", "skip_reason": null, ...}`
- **Reply:** "Today's V5.3 pick is **FIX BULLISH** — `O:FIX260515C01780000`, $1780 call expiring May 15 at a $70.55 mid. It cleared the V5.3 gates with an overnight score of 4, vol/OI of 4.5, and ~7.9% OTM moneyness. VIX 17.48 is below the 20.51 VIX3M reading so the term-structure check is clean. Entry fires at 10:00 ET, −60/+80 bracket, exit 15:50 ET day-3. *Paper-trading performance, educational only. Not investment advice.*"
- **Grade:** **WORKS.** Clean, complete, nothing ambiguous.

### Q2. "Why did you pick that one over OKLO?"
- **Tool:** `get_signal_detail` on FIX and OKLO, then compare. Correct choice because the user is asking about methodology contrast, not the canonical pick.
- **Raw (OKLO):** `{"thesis": "OKLO BULL $75C ... NSTM-3 ... NRC licensing ...", "overnight_score": 8, "recommended_spread_pct": 0.0083, "call_dollar_volume": 31932612, "flow_intent": "DIRECTIONAL", ...}` — OKLO actually scored 8 vs FIX's 4.
- **Reply:** "Both cleared the enrichment gate (score≥1, spread≤10%, directional UOA>$500K). OKLO has the higher overnight score (8 vs 4) and a much tighter spread (0.8% vs 9.8%) — but the V5.3 pick isn't chosen by raw score. `signal-notifier` takes the rank-1 signal that also passes the final gates: V/OI>2, 5–15% OTM moneyness, VIX≤VIX3M, LIMIT 1. OKLO's recommended contract is ~10.8% OTM and FIX's is 7.9% — both in-band — so the final tiebreak is the notifier's deterministic ordering. The methodology doc on gammarips.com has the full ranking logic. *Paper-trading performance, educational only. Not investment advice.*"
- **Grade:** **WORKS**, but note: the agent has to be honest that it doesn't have a single field that says "and FIX beat OKLO in the final tiebreak because X." Nothing in the tool response spells that out. The system prompt should discourage fabricating a tiebreak rationale and encourage pointing to methodology docs instead.

### Q3. "What's the current status of my paper trade?"
- **Tool:** `get_open_position`.
- **Raw:** `{"explanation": "Next trade: FIX BULLISH ... Last closed trade: WPM BULLISH on 2026-04-14 → TIMEOUT at 0.42%. Reminder: the paper-trader is a batch simulator. There is no live open position in the ledger by design.", "pending_pick": {...FIX...}, "awaiting_simulation": ["2026-04-17","2026-04-16","2026-04-15"], "most_recent_closed_trade": {...WPM...}}`
- **Reply:** "Three things to know. **Next trade:** FIX BULLISH, entering 10:00 ET tomorrow. **Awaiting simulation:** 3 scan_dates (Apr 15/16/17) are still inside their 3-day hold window — the batch simulator will reconcile them after day-3 exits. **Most recent closed trade:** WPM BULLISH on 2026-04-14 timed out at +0.42% (call-side). Reminder: the paper-trader is a batch simulator — there's no live unrealized P&L line. *Paper-trading performance, educational only. Not investment advice.*"
- **Grade:** **WORKS.** The tool's `explanation` string is genuinely good — the agent can almost parrot it. One phrasing nit: the user said "my paper trade," but the agent has to reframe as "the engine's paper trades" because there is no per-user ledger. System prompt should call this out explicitly.

### Q4. "How has GammaRips done over the last 30 days?"
- **Tool:** `get_win_rate_summary(days=30)`.
- **Raw:** `{"total_signals": 1026, "wins": 826, "win_rate": 80.51, "avg_return": 2.26, "bull_total": 641, "bull_wins": 544, "bull_win_rate": 84.87, "bear_total": 385, "bear_wins": 282, "bear_win_rate": 73.25, "max_return": 50.03, "min_return": -30.41, "best_performer": "CAR", "worst_performer": "GRCE"}`
- **Reply:** "Over the last 30 days, the engine's tracked signals hit an **80.5% win rate** (826/1026) with an average return of +2.26%. Bulls ran 84.9%, bears 73.3%. Best performer CAR (+50%), worst GRCE (−30%). **Important context:** this is the enriched-signals outcome table, which is different from the V5.3 paper-trader's realized bracket trades (one pick per day, −60/+80 bracket). For the live V5.3 trades ask for the position history. *Paper-trading performance, educational only. Not investment advice.*"
- **Grade:** **WORKS**, with caveat: the tool pulls from `signal_performance` (enriched-signal 3-day outcome tiers), not from `forward_paper_ledger`'s realized V5.3 bracket trades. That's a big distinction — 1026 signals in 30 days is ~34/day, clearly not the V5.3 one-per-day pick. A naive agent would quote "80% win rate" as if it were the V5.3 strategy, which is misleading. **System prompt must force this disambiguation.**

### Q5. "Top bullish signals for today?"
- **Tool:** `get_enriched_signals(direction="bull")` — but this returns `[]`.
- **Raw:** `"[]"` with both lowercase and uppercase `direction`.
- **Root cause:** `src/tools/overnight_signals.py` lines 70–71 and 147–148 do `LOWER(direction) = LOWER(@direction)`, but stored values are `"BULLISH"`/`"BEARISH"` while the schema `enum` is `"bull"`/`"bear"`. Lowercased comparison yields `"bull" = "bullish"` → always false.
- **Workaround used by simulated agent:** `get_freemium_preview(limit=5)` returns the top 5 enriched bullish-leaning signals cleanly (OKLO, WDC, CLS, DAL, LUV) with headlines, scores, and dollar volume.
- **Reply (using workaround):** "Top 5 enriched signals for 2026-04-17 (all bullish): **OKLO** (score 8, $31.9M bull flow, NRC licensing), **WDC** (7, $43.7M, pre-earnings), **CLS** (7, $17.4M, Apr 27 earnings), **DAL** (7, $11.5M, oil rout tailwind), **LUV** (7, $3.1M, same macro). These cleared the enrichment gate; only one is promoted to the daily V5.3 pick via the notifier's final filter (V/OI>2, 5–15% OTM, VIX≤VIX3M). *Paper-trading performance, educational only.*"
- **Grade:** **BROKEN.** The direct-named tool for this question is broken. The workaround works but isn't what a Haiku-4.5 agent would naturally pick from a cold read of tool descriptions.

### Q6. "What's in the daily report?"
- **Tool:** `get_daily_report` (default = latest).
- **Raw:** Full markdown `content` (~3KB) titled "The Peace Pivot & AI Power Plays — Overnight Edge Report, 2026-04-20" plus `bullish_count: 54`, `bearish_count: 14`, `total_signals: 68`, `seoMetadata`, `headline`.
- **Reply:** "Today's report is **'The Peace Pivot & AI Power Plays'** — 68 signals, heavy 79% bullish skew. Key themes: (1) nuclear/AI power names (OKLO, BE) getting re-rated as AI infrastructure, (2) geopolitical de-escalation crushing energy/defense premiums (CVX, VLO, LMT bearish) while boosting travel (DAL, LUV), (3) pre-earnings front-running in CLS, WDC, LLY. Top contract recs: OKLO $74C May 22, LLY $942.5C May 1, VLO $210P May 29. Full report text available on request. *Paper-trading performance, educational only.*"
- **Grade:** **WORKS.** Clean, rich, great summarization target.

### Q7. "Walk me through the thesis for FIX."
- **Tool:** `get_signal_detail(ticker="FIX")`.
- **Raw:** Full enriched row — thesis string, news_summary, flow_intent_reasoning, technicals (RSI 66, MACD+, above SMA50/200, golden cross), contract details, greeks, IV 0.69, 7.9% OTM, +2.77% price change, catalyst="Technical Breakout" score 0.85.
- **Reply:** "**FIX thesis:** Institutional positioning for the Apr 23 Q1 earnings, leveraging a $12B backlog and AI data-center revenue (45% of mix). Entry on the recovery from $1,600 support, $1,800 target. **Flow reasoning:** $11.6M bullish 3 days ahead of earnings, following a Stifel PT hike to $1,819. **Technicals:** RSI 66, above SMA50/200, golden cross, MACD expanding. **Contract:** $1780C May 15, 7.9% OTM, delta 0.38, IV 0.69. **Risk:** 40x P/E — sell-the-news risk if guidance only meets. *Paper-trading performance, educational only.*"
- **Grade:** **WORKS.** The enriched row has everything needed for a solid chat answer.

### Q8. "What fields do you have for signals?"
- **Tool:** `get_enriched_signal_schema`.
- **Raw:** 81 columns returned with `column_name`, `data_type`, `is_nullable` — e.g. `thesis STRING`, `rsi_14 FLOAT64`, `call_dollar_volume FLOAT64`, `recommended_contract STRING`, `vix3m_at_enrich FLOAT64`, etc.
- **Reply:** "The enriched-signals table has 81 columns across five buckets: **flow** (call/put dollar volume, UOA depth, vol/OI ratios), **contract** (strike, DTE, IV, delta/gamma/theta/vega, mid price, spread%), **technicals** (RSI14, MACD, SMA50/200, ATR14, EMA21, golden_cross, 52w high/low), **narrative** (thesis, news_summary, key_headline, catalyst_type, flow_intent), and **outcome tracking** (next_day_pct, day2/3_close, peak_return_3d, is_win). Use `get_signal_detail(ticker=...)` to pull any of these for a specific name. *Paper-trading performance, educational only.*"
- **Grade:** **WORKS.** Excellent introspection tool; this is a great paying-user differentiator.

### Q9. "What was the last closed trade and how did it do?"
- **Tool:** `get_position_history(days=30, limit=1)`.
- **Raw:** `[{"scan_date": "2026-04-14", "ticker": "WPM", "direction": "BULLISH", "recommended_contract": "O:WPM260424C00144000", "entry_price": 6.75, "target_price": 12.15, "stop_price": 2.70, "realized_return_pct": 0.4247, "exit_reason": "TIMEOUT", "underlying_return": 0.0376, "spy_return_over_window": 0.0193, ...}]`
- **Reply:** "Last closed trade: **WPM BULLISH** (scan_date Apr 14), $144 call Apr 24 expiry. Entry $6.75, target $12.15, stop $2.70. Exited **TIMEOUT** at 15:50 ET day-3 for a realized +0.42% on the option. Underlying moved +3.76%; SPY returned +1.93% over the same window. *Paper-trading performance, educational only.*"
- **Grade:** **WORKS.** Ledger row is rich: includes SPY benchmark return and underlying return for contextual framing. Paying-tier-worthy.

### Q10. "Is there a skip day coming? What's the VIX telling you?"
- **Tool chosen:** `get_todays_pick` (for current VIX snapshot) + `web_search` (to compare to VIX futures curve). The pick response includes `vix_now_at_decision: 17.48` and `vix3m_at_enrich: 20.51`.
- **Raw web_search:** `"Error: GOOGLE_API_KEY or GOOGLE_CSE_ID not configured in environment."`
- **Reply (degraded):** "At today's V5.3 decision, spot VIX was **17.48** and VIX3M was **20.51** — term structure is in contango (VIX < VIX3M), so the signal-notifier's VIX gate passed. If that inverts (VIX > VIX3M = backwardation), the notifier fail-closes and the engine skips — the `skip_reason` field on `get_todays_pick` will say `vix_backwardation` on those days. I can't pull live VIX/VIX3M quotes right now (web search is offline); gammarips.com shows the latest gate status. *Paper-trading performance, educational only.*"
- **Grade:** **BROKEN** — the most natural second tool (`web_search`) is unconfigured. The simulated agent can still answer partially from the canonical pick fields, but "forward-looking skip risk" needs live market data. This is a real hole for a Pro-tier user.

### E1. Refusal: "Should I size 2 or 3 contracts on today's pick given my $10K account?"
- **Tool chosen:** None. Out-of-scope per Phase 2 guardrails (personalized advice triggers the Lowe-exclusion boundary).
- **Reply:** "I can walk you through the engine's methodology and current data, but I'm not your advisor and can't give personalized sizing guidance. Ask your broker, a licensed CFP, or see the sizing examples in the public methodology on gammarips.com. *Paper-trading performance, educational only. Not investment advice.*"
- **Grade:** **WORKS if the system prompt includes the Section 2 refusal template.** No tool call is even necessary — the system prompt's refusal template handles it directly. The canned refusal text from the Phase 2 doc is already well-tuned.

### E2. Tool-chaining: "Compare today's pick to last week's pick."
- **Tool-selection reasoning:** Needs (a) today's pick from Firestore `todays_pick/{scan_date=today}` via `get_todays_pick()`, plus (b) last week's pick. There is **no `scan_date` history** surfaced for `todays_pick` — the tool returns only one pick per `scan_date`, and you'd need to call `get_todays_pick(scan_date="2026-04-10")` (a week ago). If the scan_date the user means is "last week's WPM trade" (which actually executed), the honest chain is: `get_position_history(days=7, limit=10)` to find last week's closed trades → compare each against today's pending pick.
- **Raw tool response:** (simulated chain — would require two sequential calls)
- **Reply (simulated):** "Today's pick is FIX BULLISH, score 4, 7.9% OTM, May 15 expiry. Last closed trade a week ago was WPM BULLISH (scan_date Apr 14) → TIMEOUT +0.42%. Different sectors (engineering services vs. precious metals royalty), both bullish, both earnings-adjacent. I can pull deeper context on either. *Paper-trading performance, educational only.*"
- **Grade:** **AWKWARD.** The chain works but the phrase "last week's pick" is ambiguous — there is no `list_recent_picks` tool to enumerate all historical `todays_pick` entries. Agent has to probe: "did you mean the last pick that actually closed (WPM), or the pick on a specific date?" A small `list_todays_picks(days=N)` tool or having `get_position_history` also surface the un-closed picks would remove this ambiguity.

---

## 4. Tool reliability findings

| Tool | Status | Notes |
|---|---|---|
| `get_todays_pick` | OK | Full payload, skip_reason=null semantics clean. |
| `get_open_position` | OK | Three-piece explanation string is chat-ready. |
| `get_win_rate_summary` | OK | 80.5% on 1026 signals — but agent must disambiguate this is the enriched-signals outcome table, not V5.3 bracket trades. |
| `get_signal_detail` | OK | Rich payload, works for both FIX and OKLO. |
| `get_enriched_signals` | **BUG** | `direction` filter silently returns `[]` for both `"bull"` and `"BULL"`. Root cause: `LOWER("bull") != LOWER("BULLISH")`. Both the enum definition (`["bull","bear"]`) and the `LOWER=LOWER` WHERE clause need to align. Either change the enum to `["BULLISH","BEARISH"]`, or change the SQL to `LIKE LOWER(@direction)||'%'`. See `src/tools/overnight_signals.py:70-71, 147-148`. |
| `get_freemium_preview` | OK | Great fallback for top-N; directionless but fine. |
| `get_position_history` | OK | Good realized-trade payload with SPY benchmark. |
| `get_daily_report` | OK | Markdown + counts + SEO metadata; rich summarization target. |
| `get_report_list` | not tested | |
| `get_available_dates` | OK | 30 scan dates, signal counts per date. Useful for E2. |
| `get_enriched_signal_schema` | OK | 81 columns, clean introspection. |
| `web_search` | **BUG** | Returns `"Error: GOOGLE_API_KEY or GOOGLE_CSE_ID not configured in environment."` Cloud Run deploy needs those two env vars set from Secret Manager. |
| `get_overnight_signals` | not tested | (Raw scanner, unlikely to be needed for Pro chat.) |
| `get_signal_performance` | not tested | (Historical outcomes; useful for "how did Apr 14's signals do?") |

**Surprising shapes noted:**
- `get_open_position.explanation` is a pre-assembled prose string — very agent-friendly; prefer quoting it over re-assembling from the structured fields.
- `get_win_rate_summary` has no `scan_date` scoping; it's an aggregate across the enriched table's outcome columns. Agent must name the source explicitly to avoid conflating it with V5.3 ledger trades.
- `get_todays_pick` returns `decided_at` **and** `effective_at` — agents may confuse these. `effective_at` is entry time (10:00 ET next day); `decided_at` is when the Firestore doc was written.

---

## 5. System-prompt recommendations (concrete additions to §2 of `2026-04-20-v5-3-surface-and-monetization.md`)

The existing prompt is good on scope/refusal. Add these four patterns:

### 5.1. Add a "two performance numbers exist" discipline rule

> "When a user asks about win rate or performance, there are TWO answer paths. The `get_win_rate_summary` tool aggregates from the **enriched-signals outcome table** (all signals that cleared enrichment, ~30/day, tracked against 3-day forward returns, 80%+ win rate). The `get_position_history` tool returns the **V5.3 paper-trader realized bracket trades** (one per day, −60%/+80% option bracket, 3-day hold, exited at the bracket or at 15:50 ET day-3). These are different universes. Always name which one you're quoting. Never average them. If the user says 'how has the engine done,' ask whether they mean enriched-signal outcomes or V5.3 paper trades — or quote both with labels."

### 5.2. Add a "batch simulator, no live P&L" reminder anchored to `get_open_position`

> "The V5.3 paper-trader is a batch simulator. There is no live unrealized P&L row in the ledger. When reporting position state, use the three-piece framing returned by `get_open_position`: (1) pending pick from `todays_pick` (next trade to enter), (2) `awaiting_simulation` scan_dates (inside 3-day hold, not yet reconciled), (3) `most_recent_closed_trade` (last row with real entry+exit). NEVER invent an unrealized P&L by looking up the current Polygon quote on the pending pick — that would imply the engine is already in the position when it is not."

### 5.3. Add an "impersonal-framing" reminder for every response

> "If the user asks 'my trade,' 'my position,' 'should I,' or uses any first-person possessive pronoun about a trade — always reframe as 'the engine's trade,' 'the V5.3 paper-trader's position,' or 'the engine's upcoming pick.' There is no per-user ledger; everyone in the group sees the same paper trades. If the user's question cannot be answered without personalizing, decline with the refusal template."

### 5.4. Add "tool-selection examples" section with these three

> **Example: 'What did GammaRips pick today?'** → `get_todays_pick()` only. Do not call `get_enriched_signals` — the canonical pick is already narrowed.
>
> **Example: 'How's the engine doing?'** → `get_win_rate_summary(days=30)` AND `get_position_history(days=30, limit=10)`. Report both; label the difference (enriched-outcome vs V5.3 realized).
>
> **Example: 'What's my status?' / 'What trade am I in?'** → `get_open_position()` only. Parrot the `explanation` field, do not re-assemble. Always remind it's a batch simulator.
>
> **Example: 'Top bullish signals today.'** → `get_freemium_preview(limit=5)` for now (the `get_enriched_signals` direction filter is broken; avoid it until fixed).

### 5.5. Discourage fabrication of methodology internals

> "When the user asks 'why X over Y' for two tickers that both cleared enrichment, you will NOT have a field that spells out the final tiebreak used by `signal-notifier` (V/OI>2, 5–15% OTM, VIX≤VIX3M, LIMIT 1 ordering). Do not invent one. Explain the published gate criteria and point the user at the public methodology docs on gammarips.com. State plainly: 'the ranking is deterministic from the code; I don't have a single field that encodes the final tiebreak in this tool response.'"

---

## 6. Open issues blocking Pro launch (prioritized)

### P0 — ship-stoppers

1. **`get_enriched_signals` direction filter is broken.** Returns `[]` for both `"bull"` and `"BULL"` because the enum (`bull`/`bear`) does not match stored values (`BULLISH`/`BEARISH`). A paying user asking "top bullish signals today" via the named tool will get silent empty results. **Fix:** in `src/tools/overnight_signals.py` lines 70–71 and 147–148, change `WHERE LOWER(direction) = LOWER(@direction)` to `WHERE LOWER(direction) LIKE LOWER(@direction) || '%'`. 1-line change, ~15 min including deploy.

2. **`web_search` returns env error.** Missing `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` on the Cloud Run service. Any "is the VIX spiking right now?" or "any news on FIX this morning?" question will fail. **Fix:** add both secrets to Secret Manager and mount them on the MCP Cloud Run service. 10 min.

### P1 — UX awkwardness that will burn a paying user in week 1

3. **No `list_todays_picks(days=N)` tool.** "Compare today's pick to last week's" is a natural Pro-tier question and currently requires the agent to either call `get_todays_pick` with a guessed historical `scan_date` or fall back to `get_position_history` (which only shows *closed* trades, missing recent unreconciled picks). **Fix:** add a `list_todays_picks(days=N)` tool that enumerates Firestore `todays_pick/*` and returns `[{scan_date, ticker, direction, skip_reason}, ...]`. Gives the agent a clean "recent picks" enumeration. ~30 min.

4. **`get_win_rate_summary` and `get_position_history` cover different universes with no disambiguation in the tool description.** The agent will conflate the 80% enriched-outcome win rate with the V5.3 realized win rate (which, based on the single WPM TIMEOUT sample, is probably much lower right now). **Fix:** update each tool's `description` field in `get_tools_list()` to explicitly say which table it reads and what universe of trades it represents. Also add the disambiguation to the system prompt (§5.1 above).

5. **`get_todays_pick` can return a stale/yesterday's pick when the current day's signal-notifier hasn't written yet.** The `scan_date` in the response (2026-04-17 while today is 2026-04-20) may confuse users asking "what's today's pick" before the notifier fires. **Fix:** have the tool explicitly return `scan_date_is_stale: true/false` based on `scan_date < today`, or have the agent system prompt parse `scan_date` and phrase the answer as "based on the most recent scan (Apr 17), tonight's/tomorrow's trade is..." Low-cost system-prompt-only fix is acceptable.

### P2 — nice-to-haves for launch + 1

6. `get_open_position.pending_pick.effective_at` vs `decided_at` confusion (agent may surface the wrong timestamp as "entry time"). Add a `entry_time_et: "10:00 ET"` convenience field or spell it out in the explanation string.

7. `get_position_history` does not include open/unreconciled bracket trades. If a beta user in the group asks "walk me through every trade the engine has made since I subscribed," and they subscribed 2 days ago, the answer will appear empty (no closed trades in window) even though the engine placed two picks. A `get_all_active_and_recent_trades(days=N)` convenience endpoint would help. Alternatively a system-prompt instruction to chain `get_open_position` + `get_position_history` and present both.

8. `web_search` scoping: once env vars are fixed, decide whether the agent is allowed to answer general-market questions ("how did SPY do today?") or only GammaRips-internal questions. A scope fence in the system prompt would prevent paying users from treating the chat as a general Bloomberg terminal.

---

## 7. Final verdict

The MCP server is **close to Pro-tier ready**, but launching today would produce at least one embarrassing silent-empty result (Q5) and one "I can't look that up right now" answer (Q10) within the first hour of real WhatsApp traffic. All four P0/P1 fixes are small and scoped:

- P0-1: SQL WHERE clause, 1-line
- P0-2: two Secret Manager env vars
- P1-3: one new `list_todays_picks` tool, ~30 LOC
- P1-4: tool description edits + system prompt additions

**Recommended action:** block Phase 2 launch until P0-1 and P0-2 are fixed + system-prompt §5.1–5.4 additions are committed to the agent config. P1 items can ship in the first post-launch patch (week 1 of live Pro tier).
