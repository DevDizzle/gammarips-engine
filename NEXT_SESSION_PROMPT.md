# Next Session Prompt

**2026-06-04 session — SCORER→PICKER COLLAPSED into one memory-aware judge (`judge_v6`). IMPLEMENTED + unit-tested (32 pass) + LIVE gemini smoke passed. NOT yet deployed; pending `gammarips-review` leakage audit (the one non-negotiable; owner waived the rest of the G-Stack ceremony).**

Owner-directed simplification. A multi-agent workflow (16 agents) evaluated the 2-stage ranker: across 13 V5.4-era slates the single judge agreed 9/13 with the logged baseline and was structurally sounder 4-to-1 on the divergences (every divergence was the judge REJECTING a two-label-trap the 2-stage fell into — OKTA→BX, KBR→MCO, EQIX-LEAP→RDDT, CIEN-theta-cliff→GE). The Scorer's top-5 cut was a no-op on ~80% of days (slates ≤5); structural rules were triple-encoded (gates + scorer + picker). Decision: `docs/DECISIONS/2026-06-04-scorer-picker-collapse-to-single-judge.md`.

**What shipped (code, branch `gate-changes-2026-06-02`, NOT committed yet):**
- `signal-judge/prompts/judge_v6.md` — single-call rubric: trusts upstream gates (no re-litigating ITM/earnings/spread), anti-anchoring ("score each candidate as if it were the only one"), absolute leakage discipline + mass-leakage skip, per-candidate verdict array, deterministic composite/tiebreak.
- `app/schemas.py` — `PerCandidateVerdict` + `JudgeOutput` (composite weights 60/25/15 unchanged). `ScorerOutput`/`PickerOutput` kept for typecheck/replay. `RankResponse.scorer_outputs` re-typed.
- `app/agent.py` — removed Scorer fanout + ADK Picker; added `run_judge` (leakage-assert all → ONE structured call → `JUDGE_MAX_ATTEMPTS=3` bounded retry, replacing the lost `MIN_SCORER_SUCCESS_FRAC` partial-failure tolerance); rewired `run_pipeline` (deterministic mass-leakage decision; off-list/poisoned pick fails closed). `root_agent` now a degenerate judge for ADK discovery.
- `app/tools.py` — `persist_run` writes one row per verdict, **mirrors the judge into both scorer/picker REQUIRED columns** (`*_prompt_version=6`, `*_model=gemini-3.1-pro-preview`) → **BQ DDL UNCHANGED**, cohort separable. New `JUDGE_*` constants.
- `deploy.sh` env → `JUDGE_*` (legacy `SCORER_*`/`PICKER_*` retained-but-inert). Case-memory now **load-bearing** (`run_pipeline` fails closed if absent).
- **Wire contract preserved → ZERO signal-notifier changes** (verified: `call_signal_ranker` only guards on `pick`+`confidence`; v5_4_meta fields all present).
- Docs: TRADING-STRATEGY (lines 4 + 47), CLAUDE.md + GEMINI.MD policy line, this file. Live smoke harness at `.scratch/smoke_judge_v6.py` (reads `.scratch/replay_slates.json`).

**OPEN / NEXT:**
- (a) **`gammarips-review` leakage audit** of the diff — DONE, verdict SHIP (serial pre-pass assert, deterministic skip, fail-closed all confirmed).
- (b) Service+dir+code renamed `signal-ranker` → `signal-judge` (2026-06-04). Deploy: `cd signal-judge && bash deploy.sh`. Then live smoke + verify a `signal_ranker_runs` row writes with version=6. **BQ table `signal_ranker_runs` + Firestore `v5_4_*` keys deliberately KEPT (migration/webapp landmines, no payoff).**
- (c) Commit (working tree has the diff; `.scratch/` is untracked — don't commit it).
- (d) The V5.5 relabel below is INDEPENDENT and still open — judge_v6 emits the same provenance fields, so it doesn't conflict.
- Optional follow-ups (from the eval's gaps): poisoned-slate fixture for mass-leakage, fat-day (N>5) anti-anchoring A/B, optional `ALTER` for first-class `judge_prompt_version` column.

Memory: `feedback_dont_gate_owner_innovation`, `feedback_simplicity`, `project_picker_memory_harness`.

---

**2026-06-03 session — PICKER CASE-MEMORY HARNESS built + wired + DEPLOYED + verified live (`signal-ranker` rev `00011-pw9`, `picker_v5`). Owner-directed; owner WAIVED the N≥15/30-day-OOS/DoD ceremony for this (it's advisory/non-gating). Leakage was NOT waived — audited by `gammarips-review` = SHIP-WITH-FIXES, all fixed.**

Owner's idea: give the LLM Picker a *curated, causally-labeled memory* of past option winners/losers ("cleaner than RAG") so it reasons by analogy. Two deep-research workflows (the first over-constrained by my own prompt — it banned post-entry "why" tokens and reduced to a moneyness-CI test, killing the idea; the second, correctly framed, delivered it). **Key reframe that unlocked it:** leakage protects only TODAY's live pick — explaining a CLOSED past trade with full hindsight is allowed and is the whole point.

**What shipped:**
- `scripts/ledger_and_tracking/build_case_memory.py` (read-only) joins `realized_label.pkl` (FILLED option outcome + underlying path) ⨝ `overnight_signals_enriched` (greeks/IV/catalyst/flow) on `(recommended_contract, scan_date)`, overlays the 6 matched live `forward_paper_ledger` closes → emits `signal-ranker/case_memory/{bull.md (846), bear.md (529), exemplars.md (~50 curated, the injection block), case_index.parquet, build_manifest.json}`. `quant.md` (12 priors Q1–Q12) is hand-authored, NOT regenerated.
- **Outcome keyed on `realized_ret>0` (option PnL), NOT `is_win` (stock direction) — they disagree 44.2%.** That "two-label trap" (stock moved your way, option still lost — short-DTE theta cliff) is the central lesson. WHY is **deterministic option physics** (theta drag / delta capture / inferred IV residual), no LLM-authored cause.
- Wired into the Picker the house way: fenced `{case_memory_block}` in `_build_picker_instruction` (agent.py), renderer `tools.render_case_memory_for_picker()` (cached, ~46.7KB), `picker_v5.md` (v4 + §1a "how to use case memory"), `Dockerfile` ships `case_memory/`, `PICKER_PROMPT_VERSION=5`. **NOT ADK MemoryService** (that's session-recall RAG — wrong tool).
- Review fixes: (1) **fail CLOSED** if v5 ships w/o memory (no silent v4 degrade), `RankResponse.case_memory_bytes`; (2) `deploy.sh` preflight assert; (3) decision note `docs/DECISIONS/2026-06-03-picker-case-memory.md` naming the accepted+bounded **same-ticker outcome-import** vector.
- Verified: smoke test `case_memory_bytes=46673` live, clean pick, no guard trip; 25/25 unit tests pass. Picker latency ~39s now (bigger context, fine vs 540s timeout).

**DONE 2026-06-03/04:** docs updated (TRADING-STRATEGY, CHEAT-SHEET, DECISIONS note, this file) + **COMMITTED** `f5bd0df` on branch `gate-changes-2026-06-02` (working tree clean; `uv.lock` + `case_memory/*.parquet` gitignored). Prompt alignment DONE (picker_v5 §1a). **LEDGER DECISION MADE: TAG, do NOT truncate** — keep the 13 V5.4 rows as the pre-memory baseline; new rows get `policy_version='V5_5_CASE_MEMORY'`; webapp filters to V5.5 for a clean public view. (Truncate rejected: would wipe the only live track record + the 6 live case-memory exemplars + the A/B baseline for "did memory help".)

**OPEN / NEXT — V5.5 relabel (NOT started; only the site map below was pulled). Take a step at a time.**
Note: **V5.5 is already LIVE behaviorally** (picker_v5, `signal-ranker` rev `00011-pw9`); this is cohort-LABELING only, not a behavior change.

**(a) WRITE sites — change the emitted tag `'V5_4_AGENT_RANKER'` → `'V5_5_CASE_MEMORY'` for NEW rows:**
- `forward-paper-trader/main.py:66` — `POLICY_VERSION = "V5_4_AGENT_RANKER"` constant (used at 238, 462, 1041). **Single constant — change here.**
- `signal-notifier/main.py:430, 471, 1220, 1327` — literal `"policy_version": "V5_4_AGENT_RANKER"` writes (todays_pick + ledger). Consider hoisting to a module constant while here.

**(b) READ-FILTER sites — CRITICAL coupling. These filter `policy_version = "V5_4_AGENT_RANKER"`; if left as-is they will MISS the new V5.5 rows:**
- `signal-notifier/main.py:1198, 1291` — feed the picker's 14d ledger summary / stats. **Recommend: filter to BOTH `IN ('V5_4_AGENT_RANKER','V5_5_CASE_MEMORY')`** so the rolling 14d window + track record stay continuous across the relabel (the column still segments cohorts for analysis). The summary builder at 918-949 GROUPs BY policy_version (no filter) — already fine, will show both split out.
- Downstream consumers that filter V5_4 and would silently drop V5.5 — **decide per surface**: `win-tracker/main.py:165`, `blog-generator/app/tools.py:217,674,741,1189`, `x-poster/app/tools.py:173,439`. For public-facing stats (x-poster/blog/webapp) owner wants a clean **V5.5** view → those can filter V5_5-only OR both; pick deliberately. win-tracker = performance tracking → both.

**(c) Deploy + review:** relabel touches `forward-paper-trader` (rule: ALWAYS `gammarips-review` before deploy) + `signal-notifier` (+ optionally win-tracker/blog/x-poster). Sequence: edit → `gammarips-review` → deploy the touched services. No trader-mechanics change (label only).

**(d) Webapp** — separate repo `/home/user/gammarips-webapp` (Next.js, auto-deploys). Show "V5.5" label + filter public stats to the V5.5 cohort. Do AFTER engine side. It reads `todays_pick` (has `v5_4_*` provenance fields — note the field-name prefix is `v5_4_*` even post-relabel unless we also rename those, which the webapp reads — check before renaming Firestore keys).

**Optional later:** flash-narrative prose pass over the deterministic case WHY (A/B for readability); Phase-2 graph from `case_index.parquet`.

**Housekeeping:** smoke test wrote one stray audit row to `signal_ranker_runs` (`run_id v5_4_2026-05-28_eaaa64c9`) — harmless, deletable.

Memory: `project_picker_memory_harness`, `feedback_dont_gate_owner_innovation`.

---

**2026-06-02 session — THREE signal-quality changes SHIPPED to `signal-notifier` + deep-research triage. Owner-directed; overrode the N≥15 lock for gate-*removals/selection* (NOT trader mechanics).** Operator was frustrated with a thin picker slate (~2 candidates/day) and weak picks (CIEN BEARISH entered 05-29, underlying +8%). Goal: *more good options for the picker.*

**NEW: first leak-free realized-option-PnL backtest infrastructure (reusable, the new arbiter).** Backfilled full 3-day option **minute** bars for all labeled candidates from live Polygon (`backtesting_and_research/fetch_hold_window_bars.py`; the cache previously held only entry-day bars, which had made an earlier replay 99% day-1 truncations), replayed the exact +80/−60/trail bracket → `realized_label.pkl` (**1,375 fills**). Analysis scripts: `realized_option_label.py`, `gate_recall.py`, `gate_validity_checks.py`, `moneyness_band_study.py`, `exit_design_study.py`. **Lesson reinforced all session: literature/AI is for framing; our realized option bars are the arbiter.**

**SHIPPED to `signal-notifier` (rev `00028-pm7`), all live for the 2026-06-02+ 07:30 cron:**
1. **`V/OI > 2` gate REMOVED.** Realized PnL: dropped ~55–63% of real winners for precision lift statistically ≤ 0 (90% CI [−0.061,−0.001]); not fillability-confounded (gap +0.057); stable across chrono halves. Folklore conviction gate. `gammarips-review` = SAFE. Decision: `docs/DECISIONS/2026-06-02-voi-gate-relaxation-proposal.md`.
2. **STRICT `ORDER BY` re-ranked** from directional-V/OI-DESC → `overnight_score DESC, recommended_oi DESC, spread ASC, ticker` (now identical to FALLBACK). V/OI is a poor *filter* and a poor *ranker*; supersedes the 2026-05-01 V/OI-DESC primary.
3. **Moneyness cap WIDENED `0.10 → 0.13`** (STRICT only; **`FALLBACK_MONEYNESS_MAX` decoupled + pinned at 0.10** — was `= MONEYNESS_MAX`, a real footgun). Realized PnL: 10-13% increment +8.9% (90% CI [+.014,+.163]); current 5-10% band was breakeven; (0.14,0.15] bin toxic (−15%, excluded → cap at 0.13 not 0.15). **Mechanism correction, NOT a literature reversal:** the H12 deep-OTM-cliff lit (Aretz/Augustin) is HOLD-TO-EXPIRY; our 3-day bracket on UOA flow isn't that trade. `gammarips-review` = SAFE (correctness). Decision: `docs/DECISIONS/2026-06-02-moneyness-cap-widen-to-13.md`. Floor unchanged (0.05). **Thin evidence (N=87, one regime), can't cost-validate in paper — reversible, monitor closely.**

Every tradeability gate kept (OI≥10, vol≥50, DTE 7-45, regime, earnings, active-days). **No trader-mechanics change.** Also re-ran the notifier once for scan 06-01 (no real subscribers) → DINO BULLISH (same pick; 06-01 wasn't V/OI-bound — slate was 123→5 via SQL gates → 2 via downstream Python gates).

**Deep-research (external Gemini Deep Research) triaged against our data → `INTELLIGENCE_BRIEF.md` H18–H21:**
- **H18 (kill the −60% premium stop — the report's #1 lever, = our old H13): TESTED → FALSIFIED.** `exit_design_study.py`: removing the hard stop = paired mean delta **−0.001** (CI [−0.004,+0.003]), zero EV change, just fatter left tail (−0.60 → −0.97). The "wick-out" is a HTE artifact — over 3 days the option is down 60% only when the underlying genuinely failed. **Keep the −60% stop.** Trail earns its keep (TARGET_ONLY −0.012 worse). TIME_ONLY higher *mean* but right-tail mirage (lower median/win%, fatter losers). Memory: `project_exit_design_backtest`.
- **H19 (restrict DTE 7-45 → 21-45): untested** — would shrink the slate; stratify our PnL before adopting.
- **H20 (sweep/ISO detection): PARKED — blocked on data tier.** Taxonomy exists (Polygon id 219 ISO, 228/230 single-leg ISO, 232-247 multi-leg) but `/v3/trades` returns **403 on our Polygon plan**. Needs an Options-Advanced (trades-feed) upgrade — spend + vendor decision. **Defer until EV proven at N≥15–30**; highest-value future signal-quality lever. Probe: `backtesting_and_research/probe_sweep_feasibility.py`.
- **H21 (exit by Day-2 if stalled): untested.**
- **REJECTED:** "VOI > 1.25 predictive" (contradicts our measured V/OI null); "anchor moneyness to 5%" (contradicts our 10-13% data; same HTE lottery argument we discounted).

**Monitoring the new changes (no tag fields added — measure by JOIN):** slate size should climb; INVALID_LIQUIDITY rate should hold (fillability gates kept); the 10-13% moneyness cohort = `forward_paper_ledger` rows `scan_date ≥ 2026-06-02` ⨝ `overnight_signals_enriched` on (ticker, scan_date) WHERE `moneyness_pct` ∈ (0.10, 0.13]. **All three changes are one-line reverts** (`MONEYNESS_MAX`→0.10; re-add 2 V/OI lines; restore old ORDER BY). Memories: `project_option_pnl_relabel_blocked`, `project_moneyness_band_study`, `project_exit_design_backtest`.

**⚠️ Not committed to git.** This session's working-tree changes (`signal-notifier/main.py`, `CLAUDE.md`, `CHEAT-SHEET.md`, `docs/TRADING-STRATEGY.md`, `docs/research_reports/INTELLIGENCE_BRIEF.md`, two new `docs/DECISIONS/2026-06-02-*.md`, and `backtesting_and_research/*.py` + `realized_label.pkl`) were **deployed but NOT committed** — same pattern as prior sessions. Commit when convenient (branch off `master`).

---

**2026-06-01 (later session) — Per-signal SEO metadata SHIPPED; organic-content gap identified.** Ran `gammarips-seo` to find organic-click opportunities. Key correction: the agent worked blind to the webapp source and assumed weak titles — the **webapp is a SEPARATE repo** (`/home/user/gammarips-webapp`, Next.js, auto-deploys live) and its `/signals` + `/how-it-works` titles are **already optimized** (keyword-rich, canonical, SSR'd ticker table). The ONE real gap: per-ticker pages (`/signals/{ticker}`) read `signal.seoMetadata` from Firestore but nothing populated it → all fell back to thin `"{TICKER} Signal"`. **Fix shipped:** `overnight-report-generator` now generates per-signal SEO via an **isolated** Gemini call (`generate_per_signal_seo`, `SEO_PROMPT_VERSION="signal_seo_v1"`) — separate from the report-markdown call so `report_md`/the V5.4 ranker is byte-for-byte unaffected — with a deterministic per-ticker fallback, writing `seoMetadata` onto the top-10 candidates' `overnight_signals/{report_date}_{ticker}` docs via `.update()` (Stage 5, non-blocking, skip-on-miss). `gammarips-review` = **SHIP**. Deployed `overnight-report-generator 00017-h6c`; verified by force-run on 2026-05-29 (10 docs) and backfilled today 2026-06-01 (10 docs). Going forward the 08:15 ET report cron populates it daily. Memory: `project_webapp_separate_repo_and_seo`.

**Blog/EEAT pipeline FIXED end-to-end (Part A + B shipped).** Foundational content was entirely missing — `blog_posts` empty, no webapp `/blog` route — despite `blog-generator` being "live." **Root cause (Part A):** the Publisher couldn't resolve a slug. The planner embeds `schedule_slot` *nested* in `post_outline` (a JSON string under output_key), but Publisher read top-level `state["schedule_slot"]` (never set) and `outline["slug"]` (wrong nesting) → `slug=""` → `publish_to_firestore("")` returned `error` → endpoint returned **200** (masking it) → nothing written. **Fix:** parse the writer's YAML front matter (authoritative — has slug/title/description/keywords/cta; schedule row lacks `description`) as the primary metadata source + strip it from the stored body; loud-fail on empty slug; `/generate` now returns **500** on `error`/`rejected` so failures surface + Scheduler retries. Deployed `blog-generator 00021-285`; real `/generate` published `blog_posts/why-uoa-is-mostly-noise` (status=published, clean body, 7-min read); schedule now 1 published / **12 pending**. **Part B (webapp `gammarips-webapp` repo):** the Firestore reader was stale — targeted a non-existent `blogPosts` camelCase collection with wrong fields. Reconciled `BlogPost` + `getBlogPostsAdmin`/`getBlogPostAdmin` to the real `blog_posts` schema; built `/blog` (index) + `/blog/[slug]` (Article + BreadcrumbList schema, canonical, OG, ISR 300s); added `/blog` to sitemap. **Blog is LIVE with 12 foundational posts** at gammarips.com/blog (+ `/blog/[slug]`). Drained all pending via `/generate`; all passed the compliance rubric at score 10.0. Three more deploy-time bugs caught by verification + fixed: (1) `blog-generator` slug regression on a post whose front matter wasn't position-0 → added a **deterministic schedule fallback** (`f1beea1`, redeployed `00022-qf9`); (2) doubled `<title>` (`| GammaRips | GammaRips`) — root layout already templates the suffix → dropped it (`a0164c29`); (3) `/blog` index 308-redirected to `/signals` because the `/:ticker([a-zA-Z]{1,5})` catch-all swallowed 4-letter "blog" → excluded it in `next.config.ts` (`89e6293d`). Sitemap includes all post URLs. **One post HELD, not a bug:** `19-per-month-signal-service` is `status=rejected` (compliance rubric hard-fails the retired alias "premium signal", which the writer reintroduced across all 3 revision passes) — leave it; the topic is also stale (founder pricing is $29/mo, not $19), so it needs an editorial/title decision before retry. **Re-run `gammarips-seo` ~90 days out (early Sept 2026), not 30** — at ~10 organic clicks/28d a 30-day delta is noise; the blog needs weeks to crawl+index. The weekly Mon 05:00 cron now publishes reliably going forward (it was silently failing on empty-slug before today). **No trader-mechanics change this thread.**

---

**2026-06-01 session — Daily-cadence fallback SHIPPED + verified; lock-in/Alpaca decisions made (design-only, no trader-mechanics change).** Two threads this session:

**(A) Daily-cadence fallback — DEPLOYED to prod.** Problem: cadence is the bottleneck (~6 trades in ~13 trading days vs ≥10/mo target); the strict conviction funnel empties on too many days even in a rip (scan 2026-05-26 skipped with 24 score-7/8 names in the pool). Fix: when the strict stack leaves **zero** candidates, `signal-notifier` no longer skips — it re-queries with **only conviction gates relaxed** (drops `volume_oi_ratio > 2`; moneyness floor `0.05 → 0.0`) and surfaces the single **best fillable** candidate (`ORDER BY overnight_score DESC, recommended_oi DESC, spread ASC, ticker`). **Every tradeability/literature gate stays** (OI≥10, vol≥50, DTE 7-45, regime VIX≤VIX3M, earnings-overlap, active_days_20d≥5 — all run on the fallback pool). On fallback days the **V5.4 ranker is BYPASSED** (deterministic top row, `confidence=LOW`, email subject `[FALLBACK]`). Strict days unchanged. Tagged `policy_gate=FALLBACK` in `todays_pick` → propagated to `forward_paper_ledger.policy_gate` so fallback EV is separable. Verified on real data: scan 05-26 (was a skip) → surfaces ADBE BEARISH (OI 109, vol 322); scan 05-27 strict → PAAS unchanged. `gammarips-review` verdict **GO**. Deployed: `signal-notifier 00025-xxg`, `forward-paper-trader 00036-8jt` (both booted clean). Decision: [`docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`](docs/DECISIONS/2026-06-01-daily-cadence-fallback.md). **Revisit trigger: N≥10 closed FALLBACK trades** → compare FALLBACK vs STRICT EV (`GROUP BY policy_gate`; treat legacy `ENRICHMENT_ONLY_NO_TRADER_GATE` + `STRICT` as one non-fallback baseline); kill or tighten the fallback if it loses. **NOT a V5.3 fallback** — this is conviction-relaxation within V5.4, not a strategy fallback; does not violate the "no V5.3 fallback" rule.

**(B) Lock-in gains ("issue #2") — DECISION: leave it alone until N≥15.** Operator wanted to lock gains after the PAAS give-back (peaked +31%, timed out flat). Resolved with data: a **ratcheting** trail provably does NOT kill the +80% winners (HTZ ran $0.40→$0.74 and filled the +80% target *on the way up*; a trailing stop only fires on a drop, so it never threatens a trade that reaches target). BUT the current −25%-off-peak trail is too loose to lock much (on PAAS's $3.00 peak it sits at ~break-even), and with only **2 trades** ever reaching the +30% zone you cannot calibrate arm/trail levels. So: **keep clean +80/−60, no trail change now**; revisit the ratchet at N≥15 with a real peak distribution. (A +25% scalp target was rejected earlier — it would have ~halved cohort return by clipping the HTZ tail.)

**(C) Alpaca platform constraints (verified for the eventual agent) — design-only, nothing built.** Alpaca **options** support market / limit / **stop / stop-limit**; they do **NOT** support trailing-stop, bracket, OCO, or OTO (all equity-only). Consequences for the future agent: (1) lock-in must be **agent-coded** (a ratcheting native *stop*, not a trailing-stop order type); (2) **no OCO** → cannot rest the −60% stop AND +80% limit simultaneously on one contract — the agent holds ONE resting protective stop and fires the target via a poll loop. Capital/velocity: Alpaca accounts are **margin/limited-margin by default and float settlement**, so unsettled proceeds recycle immediately (same as Robinhood Instant) — velocity is NOT a blocker (confirm options-proceeds behavior via paper test). Real capital need is **overlap** (daily entry × 3-day hold = ~3 concurrent positions = ~$1.5–2k working capital), inherent to the strategy, not a settlement problem. 3-day holds are NOT day trades, so the $25k PDT floor doesn't bind. The agent ("Gemini Spark" — operator's term; clarify the specific runtime/framework next time) stays **DEFERRED** per the unchanged 3-part go-live trigger (N≥30 + EV≥0 + 15 manual matches). Next step when signal is good: draft the agent exit state-machine spec (poll loop, one-resting-order constraint, target-fire logic) so paper-sim == live-execution. **No code for this thread this session.**

**⚠️ Not committed to git.** This session's working-tree changes (`signal-notifier/main.py`, `forward-paper-trader/main.py`, `docs/TRADING-STRATEGY.md`, new `docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`) were **deployed but NOT committed** — same pattern as prior sessions' uncommitted state. Commit when convenient (branch off `master`).

---

**2026-05-28 session — Gemini model migration SHIPPED + verified.** Migrated every text-generation Gemini call `gemini-3-flash-preview` → `gemini-3.5-flash` across the engine. Voluntary quality upgrade — `profitscout-fida8` calls the old model daily so it keeps access past the 2026-06-15 deprecation regardless (NOT a forced migration). **Deployed + verified on 3.5-flash:** `overnight-report-generator` (00016-txd, trace ok), `gammarips-eval` (00006-t8p, judge logs ok + `config.yaml` bug fixed), `x-poster` (00036-kj6, dry-run APPROVE; DRY_RUN restored false), `enrichment-trigger` (00038-6xf — verified by its live 05:30 ET cron: 79 ok grounded calls on 3.5-flash), `signal-ranker` (00010-bmt — verified via `/rank` smoke: `scorer_model=gemini-3.5-flash`). **Untouched (deliberate):** Picker (`gemini-3.1-pro-preview`), x-poster image model (`gemini-3-pro-image-preview`), VAPO (`gemini-2.5-pro`), agent-arena (dead). **Behavioral:** Scorer `temperature=0.2` dropped (response_schema enforces structure); enrichment sampling knobs incl `seed=42` dropped; report temp dropped; **eval judges keep temp=0.0**. `thinking_level` NOT set — deployed `google-genai==1.22.0` rejects the field (caught live by smoke test, a green build hid it); thinking stays at 3.x server default. **Cohort:** segmented by `v5_4_scorer_model` — the 3 pre-migration closed trades (`gemini-3-flash-preview`) are NOT pooled with new-model trades for the 15/30-trade EV gates. `gammarips-review` PASSED. Decision: [`docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md`](docs/DECISIONS/2026-05-27-gemini-3-5-flash-migration.md). Model→function registry: [`docs/MODELS.md`](docs/MODELS.md). Committed + pushed (`3fa3cea` on `origin/master`); CLAUDE.md / GEMINI.MD / CHEAT-SHEET synced.

---

**Last session wrapped:** 2026-05-27 (Wednesday) — **diagnostic + decision session, no code shipped.** Answered "why only 3 trades on the app," traced the recurring INVALID_LIQUIDITY no-fills to their root cause, backtested a proposed fix, and **rejected it** on the evidence. Operator decision: accept INVALID_LIQUIDITY as a paper-only artifact and leave liquidity gating untouched. Set the go-forward plan: a **15-closed-trade interim checkpoint** (evals + diagnostic GO/NO-GO) ahead of the unchanged formal real-money DoD. Decision file: [`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`](docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md).

**State at handoff time (2026-05-27):**
- `forward_paper_ledger` — **3 closed/counted trades**: OKTA (scan 05-12, BEARISH, TIMEOUT **−1.96%**), HTZ (scan 05-14, BEARISH, TARGET **+80%**), BBY (scan 05-18, BULLISH, TIMEOUT **+15.28%**). Plus 2 `INVALID_LIQUIDITY` no-fills (KBR 05-13, EQIX 05-20) and 2 `SKIPPED` no-candidate days (05-15, 05-19). App tile: **3 trades / +31.8% ROI / 67% win / $1.5K invested**.
- **In flight (deferred reporting — see below):** BLK (scan 05-21, BULLISH) lands **today 05-27 16:30 ET**; ADI (scan 05-22, BULLISH) lands 05-28; scan 05-26 was a no-pick → writes a SKIPPED row on 05-29. ⚠️ BLK's contract showed "no bars" in the MTM log — it may land as another INVALID_LIQUIDITY.
- **Deferred-reporting mechanic (clarified this session):** the trader is NOT real-time. The 16:30 ET cron processes exactly ONE scan_date = `get_canonical_scan_date()` = **today − 3 trading days** (one cohort per day, **no catch-up loop**). So the ledger always trails real-time by ~3 trading days, and a single missed cron permanently drops that scan_date. The "3 trades" is correct given this lag + heavy gating + the 2 INVALID/2 SKIP days + Memorial Day (05-25).
- Production: `forward-paper-trader` `00035-72h` (unchanged since 2026-05-15). `signal-notifier` `00024-xh7` (active-days gate + fixed-$500 sizing). All services healthy.

**Prior sessions:** 2026-05-27 diagnostic + liquidity decision (this session); 2026-05-19 active-days liquidity gate + fixed-$500 sizing; 2026-05-15 trader resurrection + EOD MTM; 2026-05-12 V5.4 pipeline alignment; 2026-05-09 V5.4 promotion; 2026-05-08 V5.4 spec lock.

**Current policy:** V5.4 Agent Ranker — sole live strategy. Trader mechanics **unchanged** (entry 10:00 ET, −60% stop, +80% target, trail, 3-day hold). Selection changed 2026-06-01 (**daily-cadence fallback**) and 2026-06-02 (**`V/OI>2` removed; `overnight_score`-led ORDER BY; moneyness cap 0.10→0.13 STRICT / 0.10 FALLBACK**) — see top block. Decision lock: [`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`](docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md) + [`docs/DECISIONS/2026-06-01-daily-cadence-fallback.md`](docs/DECISIONS/2026-06-01-daily-cadence-fallback.md).

---

## TL;DR for the next session

**Default mode is monitor + park.** Code work is paused while the ledger accumulates closed trades. Return triggers:

1. **15-closed-trade interim checkpoint** (operator plan, set 2026-05-27). When `forward_paper_ledger` reaches **15 closed/counted trades** (distinct scan_date with a realized exit — excludes SKIPPED and INVALID_LIQUIDITY), run the **evals + a diagnostic** as a GO/NO-GO health check. Currently **4/15** closed (PAAS + CIEN land 06-01/06-02 → ~6/15 mid-week). At ~1-2 counted trades/week this lands roughly **mid-to-late July 2026**. This is a checkpoint, NOT the real-money gate. **Add to the diagnostic: FALLBACK-vs-STRICT EV split (`GROUP BY policy_gate`) once N≥10 fallback closes, and the trailing-stop ratchet calibration (N≥15).**
2. The 30-trade DoD email (`evan@gammarips.com`, subject `[GammaRips] 30-trade gate reached — return trigger active`).
3. The Phase 4 trigger (N ≥ 10 V5.4 closes) — flip `signal-ranker DRY_RUN=false` so per-row Scorer/Picker provenance lands in `signal_ranker_runs`, then build the IC join in `gammarips-eval`. Close at current pace.
4. The "5 consecutive V5.4 losses with no skipped days" rule (`docs/research_reports/V5_4_METHODOLOGY_AUDIT_2026_05_09.md`).
5. The operator surfacing a specific issue.

**Real-money go-live trigger (UNCHANGED — `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`):** all three must fire, PLUS CLAUDE.md's mandatory 30-day OOS + `gammarips-review` audit. The 15-trade checkpoint above does **not** replace this.
- N ≥ 30 closed V5.4 paper trades
- Cohort EV ≥ 0
- ≥ 15 operator-confirmed manual trades match the picker's signal

Until those fire, the system is paper-only. Founder pricing $29/mo continues as the only commercial surface.

**What to put in the 15-trade diagnostic:** cohort EV + win rate; eval/IC health (once Phase 4 lands provenance); fill rate (INVALID_LIQUIDITY %); **and a review of whether the `active_days_20d >= 5` gate should stay** — this session found it may be net-harmful (it would have rejected HTZ, the +80% winner, and did NOT catch EQIX/BLK). See the liquidity decision doc.

---

## What this session did (2026-05-27) — diagnosis only, NO code shipped

1. **"Why only 3 trades?"** — confirmed correct: deferred 3-trading-day reporting lag + heavy upstream gating + 2 INVALID_LIQUIDITY + 2 SKIPPED + Memorial Day. Not a bug.
2. **INVALID_LIQUIDITY root cause** — the contracts V5.4 picks (5–10% OTM, short-DTE, single-name, UOA-spike) are uniformly thin; `recommended_volume` is the scan-day spike that doesn't persist; entry-day fill is near-random. Verified EQIX/BLK printed zero entry-day bars (genuine, not a fetch bug).
3. **Tested a fix (H15: per-day volume floor on the active-days gate) → REJECTED.** Backtest (`backtesting_and_research/2026-05-27_active_day_volume_floor.py`): any floor that rejects EQIX/BLK also rejects OKTA + BBY (real fills), HTZ fails even the current gate, BLK (most trailing activity) never printed, and floor 5 darkens 42% of days. Quote-based fill model blocked (no Polygon NBBO on our tier).
4. **Decision: accept it.** No gate change. INVALID_LIQUIDITY overstates real-world un-fillability (it fires when no one *else* traded; a real buyer crosses the ask). Decision: [`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`](docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md). Research brief updated (H15 resolved). Memory: `project_invalid_liquidity_root_cause`.

**Uncommitted working-tree state (carried from prior sessions, NOT this session's):** `forward-paper-trader/main.py` + `requirements.txt` + `docs/DATA-CONTRACTS.md` + `docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md` (the 05-15 MTM/trader work) and an `enrichment-trigger/main.py` thesis-prompt tweak. These were deployed-from-working-tree but never committed. This session adds: the liquidity decision doc, the INTELLIGENCE_BRIEF H15 entry, and the backtest script/results.

**Locked decisions (don't relitigate):**
- V5.3 is RETIRED. No fallback. signal-ranker uptime is the SLO.
- `LIVE_COHORT_START_DATE = "2026-05-08"`.
- Trader mechanics: entry 10:00 ET, stop −60% initial, trail +30% gain / 25% off peak, target +80%, 3-day hold, exit 15:50 ET day-3. STOP/TRAIL wins on ambiguous bars.
- Composite weights 60/25/15 flow/regime/narrative. `scorer_v5` + `picker_v4`.
- **INVALID_LIQUIDITY accepted as a paper-only artifact (2026-05-27). Do NOT build another trailing-liquidity gate — tested and dead.**
- **Daily-cadence fallback LIVE (2026-06-01).** Relaxes ONLY conviction gates on strict-skip days; all tradeability gates kept; ranker bypassed; tagged FALLBACK. Revisit at N≥10 fallback closes. Do NOT relitigate or "tidy" it before then. NOT a V5.3 fallback.
- **Lock-in / trailing stop: LEAVE IT ALONE until N≥15 (2026-06-01).** Keep clean +80/−60. A ratcheting trail doesn't kill +80% winners (target fills on the way up) but can't be calibrated on the 2 trades that reached +30%. +25% scalp target REJECTED (halves return by clipping the HTZ tail). Revisit the ratchet at N≥15.
- **`V/OI > 2` gate REMOVED 2026-06-02** (realized-PnL: dropped ~60% of winners, lift ≤0). Do NOT reinstate it. V/OI is retained only as data, not a gate or a ranking key.
- **STRICT `ORDER BY` is `overnight_score`-led 2026-06-02** (supersedes the 2026-05-01 V/OI-DESC primary). Don't revert to V/OI-DESC.
- **Moneyness cap is 0.10→0.13 (STRICT), FALLBACK pinned 0.10, 2026-06-02.** Mechanism-corrected (the deep-OTM cliff lit is hold-to-expiry, not our 3-day bracket). Thin evidence — monitor the 10-13% cohort; revert to 0.10 if it underperforms. Do NOT reverse to 5% on the literature argument alone (our realized PnL beats it).
- **−60% premium stop: KEEP (2026-06-02).** Tested removing it on 1,375 fills → ZERO EV change (delta −0.001), just fatter tails. The "wick-out" critique is a hold-to-expiry artifact. Do NOT drop the stop. (Exit mechanics still locked until N≥15 regardless.)
- **Alpaca options order facts (verified 2026-06-01):** market/limit/stop/stop-limit supported; trailing-stop, bracket, OCO, OTO NOT (equity-only). Lock-in must be agent-coded (ratcheting native stop); no OCO → one resting exit order at a time. Margin/float = velocity preserved; ~$1.5–2k overlap capital; 3-day holds don't trip PDT. Agent ("Gemini Spark") deferred per the 3-part trigger.
- No real-money trading until the three-part go-live trigger fires (see above).
- No new trader-side gates. Ever.

---

## Production state (all profitscout-fida8 us-central1)

| Service | Revision | Status |
|---|---|---|
| `signal-notifier` | `00028-pm7` | LIVE V5.4-only fail-closed. `active_days_20d >= 5` gate + fixed-$500 sizing. Daily-cadence fallback (2026-06-01). **2026-06-02: `V/OI>2` gate REMOVED; STRICT `ORDER BY` re-ranked to `overnight_score`-led; moneyness cap `0.10→0.13` (STRICT only, FALLBACK pinned 0.10).** Cron `30 7 * * 1-5` ET. Refreshes `cohort_stats/current` per run. |
| `signal-ranker` | `00010-bmt` | Scorer fanout (`gemini-3.5-flash` since 2026-05-27) + Picker (`gemini-3.1-pro-preview`). IAM-only. `DRY_RUN=false` (live; table previously mis-stated `true`). |
| `forward-paper-trader` | `00036-8jt` | Deferred simulator (today − 3 trading days). Two crons + `/mark_to_market`. **Propagates `policy_gate` (STRICT/FALLBACK) from `todays_pick` into the ledger (2026-06-01).** |
| `win-tracker` | `00011-5l9` | 30-trade DoD gate. Cron `30 16 * * 1-5` ET. |
| `x-poster` | `00036-kj6` | LIVE, DRY_RUN=false. 5 schedulers active. Text on `gemini-3.5-flash` (2026-05-27). |
| `enrichment-trigger` | `00038-6xf` | gates: score≥1, spread≤8%, UOA>$500K. Thesis on `gemini-3.5-flash` (2026-05-27). |
| `overnight-report-generator` | `00017-h6c` | writes `daily_reports/{date}`. On `gemini-3.5-flash`. **Stage 5 (2026-06-01): isolated `generate_per_signal_seo` writes per-ticker `seoMetadata` onto `overnight_signals/{date}_{ticker}` for top-10 candidates — non-blocking, never touches `report_md`.** |
| `gammarips-eval` | `00006-t8p` | monitoring-only. Rubric IC hookup is Phase 4. Judge on `gemini-3.5-flash` (2026-05-27). |
| `reddit-poster` | `00004-2qd` | LIVE DRY_RUN=true. Reddit creds not wired. |
| `blog-generator` | `00022-qf9` | LIVE, DRY_RUN=false. **Slug fix (2026-06-01): Publisher resolves slug/title/description/keywords/cta from front matter + deterministic `fetch_next_schedule_slot` fallback; `/generate` 500s on error/rejected. Publishes `blog_posts/{slug}`.** 12 posts published & live at /blog; `19-per-month-signal-service` held (compliance: "premium signal" alias). |
| `gammarips-mcp` | `00027-mcl` | 18 tools. |
| `agent-arena` | DEPRECATED 2026-05-04 | service exists; propose deletion if touched. |
| `webapp` (`gammarips-webapp` repo) | Firebase App Hosting auto-deploys main | LIVE V5.4 copy. **2026-06-01: per-ticker `seoMetadata` consumed on `/signals/{ticker}`; new `/blog` + `/blog/[slug]` routes reading `blog_posts` (Article+Breadcrumb schema, ISR 300s); `/blog` added to `next.config.ts` ticker-redirect exclusion + sitemap.** |

## Cloud Scheduler (all America/New_York; weekday Mon-Fri unless noted)

| Job | When | Target | Notes |
|---|---|---|---|
| `enrichment-trigger-daily` | 05:30 | enrichment-trigger | |
| `gammarips-eval-daily` | 07:00 | gammarips-eval `/eval` | |
| `signal-notifier-job` | 07:30 | signal-notifier | V5.4 pick → `todays_pick` + email + WhatsApp + `cohort_stats/current` refresh. |
| `x-poster-signal-0800` | 08:00 | x-poster `/post {signal}` | Path B anchor. |
| `overnight-report-generator-trigger` | 08:15 | overnight-report-generator | |
| `x-poster-watchlist-0905` | 09:05 | x-poster `/post {watchlist}` | |
| `forward-paper-trader-mtm` | 16:15 | forward-paper-trader `/mark_to_market` | EOD snapshot of open V5.4 positions → `forward_paper_ledger_intraday`. |
| `polygon-iv-cache-daily` | 16:30 | forward-paper-trader `/cache_iv` | |
| `forward-paper-trader-trigger` | 16:30 | forward-paper-trader | Closes the trade whose `exit_day = today` (1 row/fire; today − 3 trading days). |
| `track-signal-performance` | 16:30 | win-tracker | 30-trade DoD gate. |
| `x-poster-callback-1645` | 16:45 | x-poster `/post {callback}` | |
| `backfill-signal-performance` | 17:30 | win-tracker backfill | |
| `x-poster-scorecard-fri-1700` | Fri 17:00 | x-poster `/post {scorecard}` | N≥5 guard. |
| `x-poster-report-0830` | Mon 06:30 | x-poster `/post {report}` | |
| `overnight-scanner-trigger` | 23:00 | overnight-scanner | |
| `gammarips-eval-weekly` | Mon 08:00 | gammarips-eval weekly | |
| `blog-generator-weekly` | Mon 05:00 | blog-generator `/generate` | |
| `content-drafter-weekly-email` | Sun 17:00 | blog-generator `/draft_email` | operator preview |
| `content-blast-mon-0530` | Mon 05:30 | blog-generator `/blast_latest` | auto-blast (kill via `blast_killswitch/<date>`) |
| `weekly-intel-mon-0700` | Mon 07:00 | blog-generator `/weekly_intel` | |
| `content-drafter-weekly-reddit` | Thu 10:00 | blog-generator `/draft_reddit` | manual-copy drafter |

> **Scheduler hardening (2026-05-20):** 19/22 jobs retry 3× with 30–120s backoff. The 2 trader jobs were skipped pending `gammarips-review`. A single DNS hiccup lost scan_date 2026-05-19 — relevant because the trader has no catch-up loop.

## Firestore schemas relevant to monitoring

| Collection | Schema | Writer | Reader |
|---|---|---|---|
| `todays_pick/{date}` | scan_date, decided_at, has_pick, ticker, direction, contract, score, vix3m_at_enrich, vix_now_at_decision, policy_version, v5_4_run_id, v5_4_justification, v5_4_confidence, v5_4_runner_up | signal-notifier (dual-write under scan_date AND entry_day) | webapp, MCP, x-poster, gamma-bot, `/mark_to_market` |
| `cohort_stats/current` | cohort_start, policy_version, as_of, trades_closed, trades_won, win_rate, total_invested_usd, total_pl_usd, roi_pct | signal-notifier (recomputes from `forward_paper_ledger` once per daily cron) | webapp landing tile |
| `daily_reports/{date}` | scan_date, title, headline, content, bullish_count, bearish_count, total_signals, seoMetadata | overnight-report-generator | x-poster report planner, blog-generator newsletter, webapp `/reports/[date]` |
| `x_posts/{date}_{type}` | scan_date, post_type, text, tweet_id, image_url, iterations, error, dry_run, posted_at | x-poster Publisher | callback / win / loss QRT lookup |
| `blog_posts/{slug}` | slug, title, description, markdown, keywords, cta, reviewer_score, iterations, status, reading_time_min, published_at | blog-generator Publisher | webapp `/blog/[slug]`, newsletter |
| `users` | email, displayName, isAnonymous, isSubscribed, plan, uid, daysActive, usageCount, createdAt, stripeCustomerId | webapp signups | content-drafter `read_email_audience` |
| `park_watchdog/gate_30_alerted` | one-shot flag (created when V5.4 hits 30 closes) | win-tracker | win-tracker (idempotency) |

## BigQuery tables

| Table | Notes |
|---|---|
| `profit_scout.forward_paper_ledger` | One row per scan_date (V5.4-only). ticker/recommended_contract/direction NULLABLE. 16:30 ET cron writes the exit row for scan_date = today − 3 trading days. |
| `profit_scout.forward_paper_ledger_intraday` | Daily EOD MTM snapshots of open V5.4 positions. Partitioned by `snapshot_date`. 16:15 ET cron. Observability only. |
| `profit_scout.overnight_signals_enriched` | Enrichment output (per-ticker). Gate stack applied. |
| `profit_scout.signal_ranker_runs` | Per-row Scorer/Picker provenance. **Empty until Phase 4 trigger flips `DRY_RUN=false`** (N ≥ 10 closes). |
| `profit_scout.signal_performance` | win-tracker output. Drives the 30-trade DoD gate. |
| `profit_scout.polygon_iv_history` | IV cache. Populated daily at 16:30 ET. |

## What's left to do (as of 2026-05-27)

**Priority 1 — passive monitoring (no action unless something breaks):**
1. Watch BLK (lands 05-27 16:30 ET) and ADI (05-28). If a cron fails, check `gcloud run services logs read forward-paper-trader --project=profitscout-fida8 --region=us-central1 --limit=50`. No catch-up loop, so a missed day is lost.

**Priority 2 — Phase 4 (deferred to ~N≥10 closes, close at current pace):**
2. Flip `signal-ranker DRY_RUN=false`. Per-row Scorer/Picker provenance lands in `signal_ranker_runs`.
3. Build the `signal_ranker_runs ⨝ forward_paper_ledger ON (candidate_ticker, scan_date)` IC join in `gammarips-eval`. Spec: `docs/EXEC-PLANS/2026-05-08-v5-4-agent-ranker-plan.md#phase-4`.

**Priority 3 — 15-closed-trade interim checkpoint (~mid-to-late July):**
4. Run evals + diagnostic GO/NO-GO. Include the `active_days_20d >= 5` gate review (see liquidity decision doc), cohort EV, fill rate, IC health.

**Priority 4 — pending operator-side items (none blocking):**
5. Reddit creds; GA4 + GSC for `/weekly_intel`; email-list consolidation + unsubscribe; propose `agent-arena` deletion if touched.

**Priority 5 — real-money go-live (deferred until full 3-part trigger fires):**
6. When N ≥ 30 closes AND cohort EV ≥ 0 AND ≥ 15 operator-confirmed matches: open the Alpaca-agent conversation per `docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`.

## Park trigger

> 📧 `win-tracker` emails `evan@gammarips.com` (subject `[GammaRips] 30-trade gate reached — return trigger active`) when V5.4 closed-trade count (DISTINCT scan_date) ≥ 30. Before that, the **15-closed-trade interim checkpoint** is the first scheduled wake-up for an evals + diagnostic pass.

---

## Read first (in this order)

1. **`docs/DECISIONS/2026-05-27-invalid-liquidity-accepted.md`** — most recent decision; why liquidity gating is parked.
2. **`docs/DECISIONS/2026-05-19-active-days-liquidity-gate.md`** — the gate this session flagged as possibly net-harmful.
3. **`docs/DECISIONS/2026-05-15-trader-resurrection-and-mtm.md`** — trader fixes + EOD MTM.
4. **`docs/DECISIONS/2026-05-08-v5-3-retired-v5-4-promoted.md`** — V5.4 promotion lock.
5. **`docs/DECISIONS/2026-05-09-DEFERRED-alpaca-agent-execution.md`** — real-money go-live trigger (unchanged).
6. `docs/TRADING-STRATEGY.md` — canonical V5.4 execution policy.
7. `docs/DATA-CONTRACTS.md` — BQ + Firestore schemas.
8. `CHEAT-SHEET.md` — operator V5.4 routine.

DO NOT read first: `_archive/`, retired `PROMPT-*` docs, anything pre-2026-04 — historical, not authoritative.

---

## DO NOT do

- Do NOT modify V5.4 trader mechanics. Entry 10:00 ET / stop −60% / trail +30% gain / 25% off peak / target +80% / 3-day hold / exit 15:50 ET day-3.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- **Do NOT build another trailing-liquidity gate (volume floor, OI floor, day-before-scan, etc.) — tested and rejected 2026-05-27. INVALID_LIQUIDITY is accepted as paper-only.**
- **Do NOT reinstate the `V/OI > 2` gate, revert the `overnight_score`-led ORDER BY, reverse moneyness to 5%, or drop the −60% premium stop** — all decided/tested 2026-06-02 on realized option PnL (see locked decisions).
- **Do NOT buy a Polygon Options-Advanced (trades-feed) upgrade for sweep/ISO detection (H20) before the strategy shows positive EV at N≥15–30.** Taxonomy confirmed, endpoint 403 on our tier, parked — premature spend on an unvalidated strategy we can't forward-validate at this N.
- Do NOT add a V5.3 fallback path to signal-notifier. Fail-closed on signal-ranker *error* is the SLO. (The 2026-06-01 **daily-cadence fallback** is unrelated — it relaxes conviction gates on zero-candidate days and is allowed/live; it is NOT a V5.3 strategy fallback and NOT a ranker-error fallback.)
- Do NOT relitigate or refactor the daily-cadence fallback before N≥10 closed FALLBACK trades. Let it run and collect EV.
- Do NOT change the trailing stop / add a tighter lock-in before N≥15. Decision 2026-06-01: keep +80/−60 clean; the ratchet can't be calibrated on 2 data points and a mis-tuned trail risks the convex tail.
- Do NOT use FMP in forward-paper-trader. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1`. Frozen.
- Do NOT add NOT NULL constraints back to `ticker / recommended_contract / direction` on `forward_paper_ledger`.
- Do NOT add execution-side logic to `/mark_to_market`. Observability-only.
- Do NOT treat the 15-trade interim checkpoint as the real-money gate — the full 3-part DoD + 30-day OOS + gammarips-review still applies.
- Do NOT start real-money trading until all three triggers fire.
- Do NOT re-introduce WhatsApp into the paid funnel. Email-only locked 2026-04-27.
- Do NOT add a customer-facing chat agent in V1. Bot is sandboxed to `gammarips-mcp`.
- Do NOT recommend r/gammarips (own subreddit). Discord if brand-owned community is needed.
- Do NOT propose paid acquisition pre-track-record.
- Do NOT add MCP tools without `safe_error` / `clamp` / schema whitelist.
- Do NOT re-add editorial images to x-poster. Text-only.
- Do NOT add the `⚠️ Paper-trade. Not advice.` disclaimer to watchlist/signal/standby/teaser/report posts. Only on realized-P&L recap posts.
- Do NOT name a new ADK service endpoint `/run`. Use `/post`, `/generate`, `/draft_*`, etc.
- Do NOT run any seed/migration script without `PROJECT_ID=profitscout-fida8` prefix.
- Do NOT deploy a new Cloud Run service with a custom service account unless there's a hard isolation requirement.
- Do NOT post the V5.4 paid daily pick on X. Watchlist posts must EXCLUDE the official pick.
- Do NOT broadcast the V5.4 contract on X SIGNAL posts. Path B is anchor-only.
- Do NOT write Reddit posts longer than ~250 chars.
- Do NOT include a multi-row "trades that closed" table in the newsletter — featured-trade-only design (locked 4/30).
- Do NOT flip signal-ranker `DRY_RUN=false` before Phase 4 IC hookup is built.

---

## Subagents available

In `.claude/agents/`:
- `gammarips-engineer` — code cleanup, deploy fixes, BQ integration. Default for implementation.
- `gammarips-researcher` — backtests, cohort analysis. Read-only.
- `gammarips-review` — lookahead bias, leakage, unsafe execution. Read-only. **Required before forward-paper-trader / signal-notifier / signal-ranker deploys.**

---

## Memory entries (auto-loaded)

`/home/user/.claude/projects/-home-user-gammarips-engine/memory/MEMORY.md` indexes all project memories. Latest additions:
- **2026-06-02** `project_option_pnl_relabel_blocked.md` — built realized-option-PnL label (1,375 fills); V/OI>2 removed (no edge); foundation for all 2026-06-02 changes.
- **2026-06-02** `project_moneyness_band_study.md` — moneyness cap widened 0.10→0.13 (10-13% best bucket); mechanism-corrected (H12 lit is hold-to-expiry).
- **2026-06-02** `project_exit_design_backtest.md` — dropping the −60% premium stop = ZERO EV change; keep it; "wick-out" is a hold-to-expiry artifact. H20 (sweep/ISO) parked on data tier.
- **2026-06-01** `project_daily_cadence_fallback.md` — daily-cadence fallback LIVE; relax conviction, keep tradeability, ranker bypassed, tagged FALLBACK; revisit at N≥10 fallback closes.
- **2026-06-01** `project_ledger_written_in_arrears.md` — `forward_paper_ledger` rows appear only at day-3 exit (~16:30 ET); emitted/emailed in-flight signals look "missing" but aren't — don't misread an empty ledger.
- **2026-05-27** `project_invalid_liquidity_root_cause.md` — INVALID_LIQUIDITY is a thin-contract artifact; trailing-liquidity gating tested and rejected; accepted as paper-only.
- **2026-05-20** `project_first_v5_4_win_and_callback_2026_05_20.md` — HTZ +80% win + callback loop verified.
- **2026-05-20** `project_scheduler_retry_hardening_2026_05_20.md` — 19/22 jobs retry; trader jobs pending review; no catch-up loop.
- **2026-05-15** `project_v5_4_trader_observability_2026_05_15.md` — trader resurrection + EOD MTM.
- **2026-05-12** `project_v5_4_funnel_starvation.md` — picker is starved post-gates; revisit at N ≥ 15.

---

*End of handoff (2026-06-01). The engine is rolling: **4 closed trades** (OKTA, HTZ +80%, BBY, ADI) + **PAAS lands 06-01, CIEN lands 06-02** on the natural 3-day-lag cadence → ~6 closed by mid-week. This session shipped the **daily-cadence fallback** (surfaces a trade on strict-skip days, tagged FALLBACK) and **decided to leave the lock-in/trail alone until N≥15**. Alpaca platform constraints are documented for the eventual (deferred) agent. **Default mode is monitor + park — let trades build, evaluate ROI at the N≥10 (fallback EV) / N≥15 (checkpoint + trail calibration) / N≥30 (go-live) milestones.** Next scheduled wake-up: the 15-closed-trade interim checkpoint, or earlier if a cron breaks, Phase 4 (N≥10) lands, or the operator surfaces an issue. Working tree is deployed-but-uncommitted.*
