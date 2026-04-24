# Next Session Prompt

**Last session wrapped:** 2026-04-24 (x-poster + blog-generator ADK services + shared lib — DRY_RUN live, Option B deferred to tomorrow)
**Current policy:** V5.3 "Target 80" (unchanged; no execution-policy edits this session)
**Status:** `x-poster` deployed DRY_RUN=true at `x-poster-00016-js8`. All 4 smoke scenarios clean. Image gen uses theme-driven prompts + PIL-composited logo (og-image reference approach was rejected + deprecated). Engine-repo commit `031110ec` local, not pushed. Webapp changes staged, not committed.

---

## Before you do anything

Read in this order:

1. `CHEAT-SHEET.md` — operator one-pager (unchanged; still current).
2. `docs/TRADING-STRATEGY.md` — canonical execution policy.
3. `docs/EXEC-PLANS/2026-04-24-100-day-gtm-plan.md` — 100-day GTM plan (Framing A locked, 50–150 paid Day 100, organic only).
4. `docs/DECISIONS/2026-04-24-x-poster-launch.md` — **decision record for this session.** What shipped, 8-revision bug trail, architectural decisions (canonicalizer, theme-driven image gen, PIL logo composite).
5. `x-poster/DESIGN_SPEC.md` — the x-poster contract. Read before modifying agent.py or tools.py.
6. `blog-generator/DESIGN_SPEC.md` — blog-generator contract. Read before first deploy.

Do NOT read first: `PROMPT-*` docs, `_archive/`, or any pre-2026-04 research summaries. Historical, not authoritative.

---

## Evan's stated intentions for next session

**Priority ladder (ship-blocking for x-poster going LIVE on @gammarips):**

### 1. Option B — PIL ticker text overlay (2026-04-24 Evan approved)

Adds a large `$TICKER` + direction badge as a deterministic PIL composite on **signal / win / loss** posts only (keep standby / teaser / report / scorecard clean-editorial). Sketch:
```
┌──────────────────────────────────────────┐
│ $NVDA                                    │
│ BULLISH       [AI editorial image]       │
│                                          │
│                                  [logo]  │
└──────────────────────────────────────────┘
```

Implementation:
- Add `_composite_ticker_overlay(image_bytes, ticker, direction, color, font_path) -> bytes` to `x-poster/app/tools.py`
- Wire into `generate_image()` conditionally on post_type ∈ {signal, win, loss}
- Font: bundle Space Grotesk Bold TTF into `x-poster/assets/` (currently only the logo is there). Download from Google Fonts or copy from a font bundle. ~1 MB.
- Text: ticker at ~180pt, direction at ~60pt, lime-green `#a4e600` for BULLISH / red `#cc3333` for BEARISH, dark shadow for legibility on any AI background.
- Size: ticker width ~45% of image width (left-aligned, margin ~60px).

Est. 1–2 hrs including font bundling + smoke test + visual validation. Same deploy loop as today (~7 min per smoke cycle).

### 2. Flip DRY_RUN=false + redeploy + create 5 schedulers

After Option B lands clean:

```bash
# Flip DRY_RUN
sed -i 's/DRY_RUN=true/DRY_RUN=false/' /home/user/gammarips-engine/x-poster/deploy.sh
cd /home/user/gammarips-engine/x-poster && bash deploy.sh

# Create 5 Cloud Scheduler jobs
URL=$(gcloud run services describe x-poster --region=us-central1 --format='value(status.url)' --project=profitscout-fida8)
for SPEC in \
  "x-poster-report-0830|30 8 * * 1-5|report" \
  "x-poster-signal-0905|5 9 * * 1-5|signal" \
  "x-poster-teaser-1230|30 12 * * 1-5|teaser" \
  "x-poster-callback-1600|0 16 * * 1-5|callback" \
  "x-poster-scorecard-1700|0 17 * * 5|scorecard"; do
  IFS='|' read -r NAME SCHEDULE TYPE <<< "$SPEC"
  gcloud scheduler jobs create http "$NAME" \
    --schedule="$SCHEDULE" --time-zone="America/New_York" \
    --uri="$URL/post" --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body="{\"post_type\":\"$TYPE\"}" \
    --project=profitscout-fida8 --location=us-central1
done
```

### 3. Push commits

- Engine repo: `git push origin master` (includes commit `031110ec` + tomorrow's Option B commit)
- Webapp repo (Evan's commits — already staged in working tree):
  - `apphosting.yaml` — GA4 ID swap (line 42) + 18-line scheduledJobs delete (lines 44–61)
  - `src/app/layout.tsx:44` — GA4 ID hardcode swap
  - `src/lib/gtag.ts:8` — GA4 fallback swap
  - Firebase App Hosting auto-deploys on push.

### 4. blog-generator first deploy

Blocked on **task #15** — fix the dangling `{schedule_slot?}` + `{live_context?}` state refs in `blog-generator/app/agent.py` lines 146, 147, 213. Those keys aren't seeded anywhere (planner output_key is only `post_outline`; fast_api_app.py seeds only `slug` + `dry_run`). Because of the `?` suffix they resolve to empty (no crash), but writer loses the planner's data.

**Fix:** have the Planner embed `schedule_slot_data` + `live_context_data` as nested fields inside its `post_outline` output. Writer reads everything from `{post_outline}`, drop the 2 dangling refs. ~10 LOC in the planner + writer instructions.

After fix:
- Run `uv run python scripts/seed_schedule.py` once against prod Firestore to populate `blog_schedule/current` + `blog_config/voice_rules`
- `bash deploy.sh` (DRY_RUN=true first for verification)
- Smoke test against Wk 1 post ("Why UOA is mostly noise")
- Create `blog-generator-weekly` Cloud Scheduler job (Mon 05:00 ET) pointing at `POST /run`

### 5. Follow-on GTM automation (Wk 2–3 per plan)

- **Reddit-drafter subagent** (task #6) — Claude Code `schedule` skill OR Cloud Run service that drafts posts for r/options, r/thetagang, r/Daytrading (SKIP r/wallstreetbets through Month 2), emails drafts to `evan@gammarips.com` Thu 10 ET for manual posting Fri–Sun.
- **7-email Stripe-webhook lifecycle** (from GTM plan §2 Lever 4) — welcome / day-3 / trial-ending / trial-converted / churn-intent / churn-completed / win-back. Requires Mailgun wiring + Firestore state reads on subscription events.

---

## What happened in this session (2026-04-24)

Dense session — full details in `docs/DECISIONS/2026-04-24-x-poster-launch.md`. Headline bullets:

### Shipped
- **`x-poster/`** (new ADK multi-agent service, 7 post types) — DRY_RUN deployed, 4 smoke scenarios APPROVE cleanly on real data
- **`blog-generator/`** (new ADK multi-agent service) — scaffolded, not deployed
- **`libs/gammarips_content/`** (new shared lib) — brand constants, compliance rubric + deterministic canonicalizer, Tweepy + Firestore + MCP helpers
- **`win-tracker`** X posting removed (exclusive ownership moved to x-poster)
- **`docs/EXEC-PLANS/2026-04-24-100-day-gtm-plan.md`** — 100-day GTM plan (Framing A, 50–150 paid Day 100, founder uncapped)
- **GA4 measurement ID** `G-KPGTJDBC6N` → `G-ZF0DQVQEKJ` in webapp (3 files edited, not pushed)
- **4 dead email cron entries** deleted from webapp `apphosting.yaml` (Firebase App Hosting auto-deploy will clean up Cloud Scheduler on push)
- **8 X secrets** provisioned in Secret Manager (4 OAuth 1.0a refreshed, 4 OAuth 2.0 new)
- **Brand logo** uploaded `gs://gammarips-x-media/brand_logo.jpg` (the real wordmark from Evan)
- **Engine-repo commit `031110ec`** local-only (55 files, +17,223 lines)

### Key architectural decisions
- **Theme-driven image gen + PIL logo composite.** Nano Banana (`gemini-3-pro-image-preview`) cooks an editorial image themed around the ticker's industry (`$NVDA`→semis, `$GOOG`→AI) with NO text/logos in the image. PIL composites the real logo deterministically bottom-right at 12% width. og-image reference approach deprecated — it carried /arena debate visuals.
- **Deterministic canonicalizer for drift.** `canonicalize_draft_text()` in `compliance.py` strips writer's disclaimer paraphrases, $SPY/$QQQ filler on empty-standby, `V/OI None` segments. Runs in `score_rubric_before_reviewer` callback so reviewer judges final canonical text.
- **Option B approved, deferred to tomorrow:** PIL ticker text overlay on signal/win/loss only (scroll-readable).

### 8 revisions to production-ready
x-poster took `x-poster-00007` → `x-poster-00016` before all smoke scenarios passed. Full bug trail in the decision doc — ADK gotchas (kwarg names, `App` identifier, `state_delta`, curly-brace state refs), BQ column name bugs, LLM reviewer rule hallucination on standby, moneyness unit drift.

---

## What's still open

### Ship-blocking for x-poster going live

1. **Option B ticker overlay** (signal/win/loss). Est. 1–2 hrs.
2. **Flip DRY_RUN=false** in `x-poster/deploy.sh`, redeploy.
3. **Create 5 Cloud Scheduler jobs** (script in §2 above).

### Blocked on Evan (console / admin, not code)

4. **Push engine-repo commit** `031110ec` + tomorrow's Option B commit to `origin/master`.
5. **Commit + push webapp changes** (GA4 + cron delete). Firebase App Hosting auto-deploys.
6. **GA_API_SECRET rotation** — create new MP API secret in the new GA4 property (`G-ZF0DQVQEKJ`), store in Secret Manager. Phase 2 when conversion tracking turns on; silent no-op until then.
7. **Proofpoint allow-list for `mg.gammarips.com`** — still pending from prior session. Admin action on Evan's `owenec.com` tenant.
8. **Google Programmable Search Engine** CX ID → `gcloud secrets create GOOGLE_CSE_ID` — still pending from prior session. Unblocks `web_search` MCP tool.

### Nice-to-have / post-launch

9. **blog-generator dangling state refs fix** (task #15) — 10 LOC in `blog-generator/app/agent.py` planner + writer.
10. **blog-generator first deploy + seed + scheduler.**
11. **Reddit drafter subagent** (task #6) — Wk 2–3 per GTM plan.
12. **7-email Stripe-webhook lifecycle** — Wk 2 per GTM plan.
13. **Local-dev ergonomics for x-poster** — `gammarips_content` is only vendored at Docker build; `make playground` / direct `uv run` needs `PYTHONPATH=/home/user/gammarips-engine/libs/gammarips_content`. Consider a `make install-dev` target that `uv pip install -e`'s the lib into the venv.
14. **DMARC on `gammarips.com`** — still empty. Add `p=none` first to monitor, then tighten.

---

## Key facts to hold in memory

- **x-poster lives at** `https://x-poster-hrhjaecvhq-uc.a.run.app`. Latest revision `x-poster-00016-js8` (DRY_RUN=true).
- **Signal template matches Evan's WhatsApp premium format** pixel-for-pixel on real data (verified 2026-04-23 $APP test).
- **Image gen produces logo-composited PNGs** — preview at `gs://gammarips-x-media/preview_v2/manual_nvda_test.png` (accepted by Evan as "better"; text-less editorial is intentional, tweet copy carries data).
- **All 4 X post smoke scenarios APPROVE on first iteration** after canonicalizer + reviewer SPECIAL CASES landed. Disclaimer drift eliminated. $SPY filler eliminated. V/OI None suppressed. Moneyness renders as `6.42%`.
- **8 X secrets** live in Secret Manager for `profitscout-fida8`. `x-poster/deploy.sh` mounts 4 OAuth 1.0a creds.
- **Brand logo** is `gs://gammarips-x-media/brand_logo.jpg` (400×400 JPG, dark-teal bg, PIL-composited at 12% width bottom-right).
- **Founder pricing is uncapped** — no seat scarcity play anywhere in copy.
- **Framing A locked** — 50–150 paid Day 100, no paid acquisition pre-track-record.
- **V5.3 ledger still at ~0 closed trades** as of 2026-04-24. Real-money track record narrative gates on ≥30 closed trades (end of May at earliest).

---

## DO NOT do

- Do NOT modify V5.3 execution policy. Entry 10:00 ET / stop −60% / target +80% / 3-day hold / exit 15:50 ET day-3. Pinned in `docs/TRADING-STRATEGY.md`.
- Do NOT add gates to `forward-paper-trader`. Gates live in `enrichment-trigger` + `signal-notifier`.
- Do NOT use FMP. Retired 2026-04-08.
- Do NOT modify `scripts/research/` or `signals_labeled_v1` — frozen.
- Do NOT re-add the og-image.png as a multimodal reference in `generate_image()`. It carried deprecated `/arena` multi-agent debate visuals. Theme-driven prompts + PIL logo composite is the shipped pattern.
- Do NOT add X posting back to `win-tracker`. x-poster owns @gammarips.
- Do NOT flip `DRY_RUN=true` → `false` in x-poster/deploy.sh until Option B ships + smoke passes.
- Do NOT create Cloud Scheduler jobs for x-poster until DRY_RUN is flipped. (They would start firing the service on cron immediately.)
- Do NOT push the engine-repo commit or webapp changes without Evan's explicit go — auto-deploys on push for webapp.
- Do NOT reference retired aliases in any copy: "The Overnight Edge", "Ripper", "Daily Playbook", "@mention" (chat tag is `@gamma`), "GammaRips is Free", "7 AI Models", "score >= 6", "8:30 AM", "premium signal", "$49/$149 pricing", "interactive dashboard".
- Do NOT publish real-money track record until V5.3 has ≥30 closed trades (end of May at earliest).
- Do NOT paste live secrets into chat (X creds pasted 2026-04-24 need rotation in ~2 weeks per standard cadence — already flagged).

---

## Deployed revision sheet (engine)

| Service | Revision | Deployed | Notes |
|---|---|---|---|
| **x-poster** | `x-poster-00016-js8` | 2026-04-24 | DRY_RUN=true. 4 smoke scenarios APPROVE clean. Option B (ticker overlay) pending. |
| **blog-generator** | — | Not deployed | Scaffolded + DESIGN_SPEC + all code. Blocked on dangling-state-ref fix (task #15). |
| signal-notifier | `signal-notifier-00007-pv9` | 2026-04-20 | Unchanged this session. |
| enrichment-trigger | `enrichment-trigger-00032-2z4` | 2026-04-20 | Unchanged. |
| forward-paper-trader | `forward-paper-trader-...` | 2026-04-20 | Unchanged. |
| agent-arena | `agent-arena-...` | 2026-04-10 | Unchanged. |
| overnight-report-generator | `overnight-report-generator-...` | 2026-04-10 | Unchanged. |
| gammarips-mcp | `gammarips-mcp-00023-q8p` | 2026-04-20 | Unchanged. |
| win-tracker | — (redeploy pending) | 2026-04-20 | Code cleanup shipped (X posting removed); redeploy after next touch. |

Scheduler cron (unchanged this session — no new x-poster entries yet):
- `overnight-scanner` — `0 23 * * 1-5` ET
- `enrichment-trigger-daily` — `30 5 * * 1-5` ET
- `agent-arena-trigger` — `0 6 * * 1-5` ET
- `overnight-report-generator-trigger` — `15 8 * * 1-5` ET
- `signal-notifier-job` — `0 9 * * 1-5` ET
- `forward-paper-trader-trigger` — `30 16 * * 1-5` ET
- `track-signal-performance` — `30 16 * * 1-5` ET
- `polygon-iv-cache-daily` — `30 16 * * 1-5` ET

x-poster scheduler jobs to create tomorrow:
- `x-poster-report-0830` — `30 8 * * 1-5` ET
- `x-poster-signal-0905` — `5 9 * * 1-5` ET
- `x-poster-teaser-1230` — `30 12 * * 1-5` ET
- `x-poster-callback-1600` — `0 16 * * 1-5` ET
- `x-poster-scorecard-1700` — `0 17 * * 5` ET

---

## Subagents available in `.claude/agents/`

- **`gammarips-engineer`** — code cleanup, deployment fixes, BQ integration. Used heavily this session (8 deploy/smoke cycles). First-class tool for tomorrow's Option B work.
- **`gammarips-researcher`** — backtests, cohort analysis, BQ diagnostic reads. Read-only.
- **`gammarips-review`** — audits for lookahead bias, data leakage. **ALWAYS invoke before any forward-paper-trader or signal-notifier diff deploys.** Not needed for x-poster / blog-generator (no ledger writes, no execution policy touched).

For social / content work: spawn `general-purpose` or `Explore` as needed. Agent 6 (brand asset extraction) + Agent 3 (webapp cron cleanup) are good exemplars.

---

*End of handoff. First action next session: **ship Option B (PIL ticker overlay) on signal/win/loss** → redeploy → flip DRY_RUN=false → create 5 Cloud Scheduler jobs → x-poster goes LIVE on @gammarips.*
