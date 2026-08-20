# Google Ads Setup Prompt — GammaRips (agentic-trading data vendor)

> **Refreshed 2026-08-20** for the ~09-01 ads review. The `gtm/ads/` assets
> already exist (built 2026-07-09). The job is now to review and finalize
> them, not to produce them from scratch (see §0).

> **How to use this file.** Paste its contents (or its path) into a fresh Claude Code session running in `~/workspace/projects/gammarips-engine`. It reproduces the disciplined Google Ads process we ran for a sister product (TextTimeline) and adapts it to GammaRips. It references the TextTimeline ad assets as the concrete format template and encodes the reasoning behind every step. **Do not blindly copy TextTimeline — GammaRips is a different beast (see §1). Resolve the forks with the owner (Evan) before generating final assets.**

---

## 0. The goal / deliverables

The three paste-ready files and the launch brief already exist in `gtm/ads/` (built 2026-07-09, mirroring the TextTimeline templates):

- `gtm/ads/keywords.txt` — one keyword per line, match-type syntax included
- `gtm/ads/negative-keywords.txt` — one per line, pasteable into the campaign negative list
- `gtm/ads/rsa-ad-copy.txt` — Final URL, 15 headlines (≤30 ch), 4 descriptions (≤90 ch), display path (≤15 ch ×2), business name, 4–6 sitelinks (text ≤25 ch; 2 desc lines ≤35 ch; **unique text AND unique final URL each**), 8 callouts (≤25 ch)
- `gtm/ads/README.md` — the launch brief (objective, campaign type, bidding, budget, geo, kill metric)

**The job now: review and finalize these assets for the ~09-01 ads review, not produce them again.** Check them against the live site, the current pricing, and §3.

**Definition of done:** every asset within Google's char limits; every claim compliant with §3; the funnel fork (§1) confirmed with Evan; open items in `gtm/ads/README.md` resolved. A `gammarips-review` pass is optional and owner-invoked.

---

## 1. ⚠️ READ THIS FIRST — GammaRips is NOT TextTimeline

TextTimeline works on Google because its buyer *actively searches* a high-intent query ("print text messages for court") and buys a $19–$99 one-time deliverable. **None of that is true here.** Before writing a single keyword, internalize these four facts from this repo (`README.md`, `CLAUDE.md`, `docs/GTM-ORGANIC-GROWTH-PLAN.md`, `docs/TRADING-STRATEGY.md`):

1. **The paid product is `gammarips-mcp` — an MCP data vendor at ~$39/mo** for *bring-your-own-agent* traders. It sells **data + tool primitives + methodology, NOT a pick, NOT a return, NOT advice.** The free anon tier (8 keyless tools) + the free web UI (`gammarips.com`) are the top-of-funnel.
2. **The paid buyer is largely NOT on Google.** The MCP-directory channel is DEAD: a 30-day null result, DECIDED 2026-08-06 (`docs/archive/GTM-MCP-DIRECTORY-PLAN-2026-07-07.md`) — do not re-propose it. The plan of record is organic (`docs/GTM-ORGANIC-GROWTH-PLAN.md`: guides, video, Show HN); **Google Ads is an unproven, possibly-uneconomic secondary channel** reviewed ~09-01 on the measured organic CVR. The GTM gate is **Oct 5, 2026** — ad spend is explicitly to be revisited *with real CAC math only if ≥1 paying sub exists.*
3. **Finance is a Google Ads RESTRICTED category.** Options/derivatives content can trip the *Complex Speculative Financial Products* policy (certification + geo-restriction in some regions), the *Financial products and services* policy, and the *get-rich-quick* prohibition. Advertiser identity verification is required. See §3 — this is the single biggest execution risk.
4. **"Data, not advice / not a return" is an OWNER-LOCKED compliance rule** (CLAUDE.md, 2026-07-02), enforced by the rubric in `libs/gammarips_content/`. Ad copy that promises profit, returns, win rates, or "signals that make money" **violates both our own rule and Google policy.** Advertise the DATA and the TOOL. Never the outcome.

### The funnel fork you MUST resolve with Evan before generating assets
Because the paid buyer isn't on Google, "run ads for agentic trading" almost certainly should **not** mean "sell $39/mo MCP subscriptions directly off Search." The realistic options — get Evan to pick (recommend A, and keep C tiny):

- **A) Top-of-funnel to the FREE surface (recommended).** Buy cheaper, higher-volume *adjacent* intent ("unusual options activity scanner", "options order flow data", "options flow API") → land on the **free web UI or free anon MCP tier** → convert to $39/mo later via product, email, and directories. Matches the documented "free UI = top of funnel" model; keeps CAC sane; ads amplify SEO rather than fight the wrong channel.
- **B) Direct-to-paid MCP (skeptical).** Buy the emerging, near-zero-volume "agentic/MCP trading data" category → land on `/pricing` or `/developers`. High intent but almost no search volume today; likely a handful of clicks. Only worth a *tiny* exact-match ad group as a category-staking experiment.
- **C) Brand/defense.** `gammarips` brand terms — cheap, optional.

**Evan resolved this fork on 2026-07-09: MCP-direct (B) primary, with brand defense** (`gtm/ads/README.md`). Confirm it still stands at the ~09-01 review before you change any asset. Do not silently flip to A.

---

## 2. The proven methodology (what we did on TextTimeline) — and how each step maps here

Open the whole TextTimeline ads folder and read all three files as the **format template**:

- `~/workspace/projects/texttimeline/gtm/ads/keywords.txt`
- `~/workspace/projects/texttimeline/gtm/ads/negative-keywords.txt`
- `~/workspace/projects/texttimeline/gtm/ads/rsa-ad-copy.txt`

Reasoning/spec for the whole campaign (read for the *why*, not to copy the family-law specifics):
- `~/workspace/projects/texttimeline/docs/EXEC-PLANS/active/016-consumer-relaunch-and-serp-offensive.md` → **Appendix A** (full ads spec: bidding, geo, negatives rationale, budget math, policy notes)
- `~/workspace/projects/texttimeline/NEXT_SESSION_PROMPT.md` → the **2026-07-09 handoff block** (the launch decisions + why)

| # | Step (TextTimeline) | The reasoning | How it changes for GammaRips |
|---|---|---|---|
| 1 | **Objective = Website traffic, NOT Sales** | A cold account on a small budget can't feed Smart Bidding's ~15–30-conversion learning phase; buy clean clicks and measure the rate yourself. | **Same.** Still Website traffic + click bidding. Financial + $39/mo + tiny volume makes conversion-bidding even less feasible. Set up conversion tracking (trial start / signup) for *measurement*, not bidding. |
| 2 | **Search only; uncheck Search Partners + Display** | Partners/Display leak budget to junk placements. | **Same, non-negotiable.** |
| 3 | **Bidding: Maximize Clicks WITH a max-CPC cap** (never open-ended) | Legal CPCs run high; the cap prevents Smart Bidding from bidding you into the expensive auction. | **Same**, but re-estimate the cap from Keyword Planner for *finance/data* terms — likely different. Finance CPCs can be brutal; set a hard cap. |
| 4 | **Match type: Phrase, never Broad** (Exact only if starving) | Broad + click-bid + small budget = concept-matched waste. Phrase gives reach with word-order control; negatives filter the rest. | **Same default (Phrase).** For the tiny "agentic/MCP trading" category (fork B), use **Exact** — the terms are specific and you want zero waste. |
| 5 | **Keyword curation: keep buyer-intent, cut informational-broad & wrong-universe** — and note *more phrase keywords ≠ more traffic* (variants already covered) | Google pads suggestion lists to make you spend; adding near-duplicate phrase keywords just fragments reporting. | **Critical here.** The audience is technical (devs/quants running agents in Cursor/Claude Code/Cline). Buyer-intent themes: `unusual options activity`, `options order flow`, `options flow data/scanner`, `options flow API`, `options data for AI agents`, `MCP server finance/trading`, `agentic trading tools`. **Cut hard:** "how to make money", "best options to buy", "options signals", "day trading course", "get rich" — those are the *retail-gambler* universe, not our data-vendor buyer, and they're policy landmines. |
| 6 | **Strong negative list day one; scrub Search Terms report day 3–4 and day 10** | Negatives are the steering wheel; on a small budget you spend real money before the first scrub. | **Same cadence.** Different negatives (see §4). Scrub is *more* urgent at any daily budget above ~$12. |
| 7 | **RSA: fill all 15 headlines / 4 descriptions / 4–6 sitelinks (unique text + unique URL) / 8 callouts** | Ad strength "Poor" → fill it out; sitelinks/callouts are the biggest strength lifts; Google rejects duplicate sitelink text OR url. | **Same mechanics.** Copy must obey §3 (data-not-advice). Sitelinks → distinct real pages (`/`, `/developers`, `/pricing`, a docs/methodology page, a "free tier" page). Verify each URL resolves before saving. |
| 8 | **Final URL = the most keyword-matched page** (a dedicated landing page beats the generic homepage) | Keyword-to-page match lifts Quality Score and conversion. | **Depends on the fork.** A → free web UI or a purpose-built "options flow for your agent" landing page; B → `/developers` or `/pricing`. If no well-matched page exists, flag it — a landing-page mismatch wastes the whole budget faster than any keyword problem. |
| 9 | **Budget/runway math + explicit kill metric up front** | Know your CPC → clicks → visitors, and the number that kills the test. | **Same.** Tie the kill metric to the **Oct 5, 2026 GTM gate** and real CAC at $39/mo. Model: at $X CPC and a realistic free→paid rate, what does one $39/mo sub cost? If CAC ≫ LTV on paper, that itself is the finding — say so before spending. |

---

## 3. ⚠️ Financial-services ad policy — the big risk (verify LIVE)

Google's financial-ad policies change; **do not trust this from memory — WebSearch/WebFetch the current pages** ("Google Ads financial products and services policy", "Complex speculative financial products", "get-rich-quick", "Advertiser identity verification / business operations verification") and confirm before launch. Known shape:

- **Complex speculative financial products** (CFDs, rolling spot forex, spread betting — and options/derivatives can be read in): often **restricted, certification-required, and geo-limited.** Confirm whether an options-*flow-data* vendor (we don't broker or advise) is in or out of scope. Our data-vendor framing is the argument for "out of scope," but Google may still gate it — be ready to certify or geo-restrict.
- **Advertiser identity / business verification:** required; complete same-day when prompted or ads pause.
- **Prohibited: get-rich-quick.** No "make money", "guaranteed", "double your account", "profit in 3 days", "win rate", "beat the market". This aligns exactly with our owner-locked rule.
- **The safe posture (also the true one): advertise the DATA and the TOOL, never the outcome.** e.g. "Anti-firehose options-flow data for your trading agent" / "Point-in-time features + realized MFE/MAE outcome surfaces via MCP" / "Curated daily pool, not a firehose" / "Free anon tier, no pick endpoint, not advice." Mirror the vetted vendor copy (archived directory plan `docs/archive/GTM-MCP-DIRECTORY-PLAN-2026-07-07.md`, PulseMCP line) and the compliance rubric in `libs/gammarips_content/`.
- A `gammarips-review` pass on the ad assets is **optional and owner-invoked**. Append/repeat the `Not advice.` framing where natural.

---

## 4. Starter kit (a starting point to validate with Evan — NOT final)

**Candidate structure (fork A primary):**
- **AG1 — options-flow data intent** (Phrase): `"unusual options activity"`, `"options order flow"`, `"options flow scanner"`, `"options flow data"`, `"unusual options activity scanner"`. → free web UI / free-tier landing.
- **AG2 — data-for-agents / API intent** (Phrase + Exact): `"options flow api"`, `"options data api"`, `"options data for ai agents"`, `[mcp server for trading]`, `[mcp options data]`, `[agentic trading data]`. → `/developers`.
- **AG3 — brand** (Exact/Phrase): `[gammarips]`, `"gamma rips"`. → home.
- (Optional tiny **AG4 — category-staking**, Exact, fork B): `[agentic trading]`, `[ai trading agent tools]`, `[mcp finance server]`. Expect near-zero volume; it's a listening post.

**Candidate negatives (adapt from TextTimeline's ethics/junk discipline; the finance list is different):**
- *Get-rich-quick / retail-gambler intent (policy + wrong buyer):* free money, get rich, guaranteed, double, 10x, robinhood, wsb, meme stock, day trading course, signals group, alerts group, discord signals, telegram signals, "make money", pump.
- *Advice/broker intent we don't serve:* financial advisor, broker, brokerage, buy now, best stock to buy, stock picks, hot stocks, "should i buy".
- *Wrong-product / job / education:* course, class, tutorial, jobs, salary, internship, definition, meaning, "what is options trading".
- *Free-only (if selling paid):* — but here the free tier IS the funnel, so **do NOT negative "free"** in fork A.
- **Do NOT negative:** options flow, unusual options, MCP, agent, API, data, quant — that's the ICP.

**Copy rules for `rsa-ad-copy.txt`:**
- Headlines/descriptions describe **data, curation, methodology, and the agent workflow** — never returns. Good: "Options Flow Data for Agents", "Anti-Firehose. One Curated Pool.", "Point-in-Time, Leakage-Safe", "Realized MFE/MAE Surfaces", "Free Anon Tier — No Pick Endpoint", "Built for Cursor, Claude & Cline", "Not Advice. Just the Data.", "MCP Access for BYO-Agent Traders". Bad (do not use): anything with profit/return/win/guaranteed.
- Business name: `GammaRips`. Display path: e.g. `options-flow` / `for-agents`.

---

## 5. What to gather before finalizing (ask Evan; check the repo first)

1. **The funnel fork (§1)** — which surface do ads sell? (Recommend A.)
2. **Landing URL(s)** that actually exist and match the intent — is there a `/developers`, `/pricing`, a free-tier explainer, an "options flow for your agent" page? (GA4 `G-ZF0DQVQEKJ` tracks `/developers` + `/pricing` funnels — confirm they're ad-ready.)
3. **Daily budget + total probe size**, and the **max-CPC cap** (pull finance-term bids from Keyword Planner first; if the money terms show top-of-page bids that make $39/mo CAC impossible, **STOP and report that as the finding** — don't spend).
4. **Geo** (US only? sensitive-category personalized ads OFF regardless).
5. **Regulatory posture confirmation** — we're a *data/software vendor, not an adviser/broker* — so Google's adviser certification likely doesn't apply, but confirm the complex-speculative-products gate for options data (§3).
6. **Conversion event** to import for *measurement* (trial start / signup / `subscription_required` paywall touch via `mcp_analytics` + GA4).

---

## 6. Governance
- Honor this repo's rules exactly as a TextTimeline session honors `.claude/rules/` — `data-not-advice` framing and leakage-safety are non-negotiable. `gammarips-review` is optional and owner-invoked (2026-08-19).
- Keep `gtm/ads/` as the source of truth for what's in the account; if Evan edits in the UI, reconcile back to the files.
- End the working turn with a clear status and the open decisions listed for Evan.

---

### TL;DR for the session
Read the TextTimeline `gtm/ads/` folder for the *format*, read this repo's README/CLAUDE/GTM-ORGANIC-GROWTH-PLAN for the *reality*, confirm the funnel fork with Evan (the 07-09 call was MCP-direct primary, see `gtm/ads/README.md`), verify live financial-ad policy, advertise **the data not the outcome**, and review/finalize the existing `gtm/ads/` files + launch brief. A `gammarips-review` pass is optional and owner-invoked.
