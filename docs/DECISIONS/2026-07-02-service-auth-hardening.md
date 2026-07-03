# 2026-07-02 — Service auth hardening (the `--allow-unauthenticated` sweep)

**Status:** FINDING + REMEDIATION PLAN (not yet executed). Surfaced during MCP V3
Phase 1 review, which caught `/label_enriched_pool` as unauthenticated; a
follow-up sweep found the same posture is **systemic**, not a one-off.

## Finding

Nearly every Cloud Run service in `profitscout-fida8/us-central1` is deployed
`--allow-unauthenticated` (IAM `allUsers` → `roles/run.invoker`), the trigger
services do **no app-level auth**, and several answer `GET` as well as `POST`
with attacker-chosen params. Anyone who learns a URL can drive these endpoints.

IAM invoker posture (2026-07-02):

| Service | IAM | Notes |
|---|---|---|
| forward-paper-trader | **PUBLIC** | `/`, `/mark_to_market`, `/cache_iv`, **`/label_enriched_pool`** — writes ledger + the labeled substrate; GET+POST |
| enrichment-trigger | **PUBLIC** | writes the pick pipeline; **LLM $ cost surface** (the $38/day Gemini incident); GET+POST |
| overnight-report-generator | **PUBLIC** | LLM $ ; GET+POST |
| gammarips-eval | **PUBLIC** | LLM $ (`/eval/batch`, `/eval/report`) |
| overnight-scanner | **PUBLIC** | writes scan; POST-only |
| win-tracker | **PUBLIC** | writes `signal_performance`; GET+POST |
| signal-notifier | **PUBLIC** | writes `todays_pick`, **sends operator/subscriber email**; 1 grep hit for auth-ish code — VERIFY whether it's inbound request auth or just outbound email/WhatsApp creds |
| x-poster | **PUBLIC** | **posts to the public @gammarips X account** (reputational); DRY_RUN default true but that's a config, not a lock |
| blog-generator | **PUBLIC** | writes Firestore `blog_posts`; LLM $ ; multiple `/blast_latest` `/draft_*` `/generate` endpoints |
| gammarips-mcp | **PUBLIC** | **intended** — it's the product; app-level rate-limited today, bearer auth in Phase 2 |
| signal-judge | locked | good (invoked by signal-notifier, authenticated) |
| dbt-runner | locked | good (scheduler uses OIDC / compute SA) |
| gammarips-webapp | locked | separate repo / hosting; leave |
| evanparra-ai-site, irw-app | PUBLIC | unrelated projects — out of scope |

**Two-layer risk model:** IAM-public ≠ vulnerable. Real exposure =
`public reachability × what the endpoint does`. The dangerous set is the one
above that (a) spends LLM money, (b) mutates the ledger/substrate, or (c)
publishes externally — all reachable with attacker-chosen params, most with no
app auth, several via GET.

**Worst concrete case** (see `2026-07-02` note in the MCP work / PR #3): a forced
**mid-session** `POST /label_enriched_pool` writes partial intraday labels as
ground truth AND marks the Firestore claim done so the 17:00 ET cron skips →
**permanent poisoning of the paid substrate** the MCP serves. This is a
data-integrity bug on top of the auth gap and must be fixed regardless of IAM.

## Why it's like this

Callers were wired the lazy way. Scheduler OIDC audit (2026-07-02):

- **Already send OIDC** (appspot SA): `enrichment-trigger-daily`,
  `overnight-scanner-trigger`, `agent-arena-trigger`. (compute SA):
  `dbt-*`. → their services can be locked almost for free (token already sent,
  just not required).
- **NO OIDC** (locking the service today would break the cron): all
  `forward-paper-trader-*`, `signal-notifier-job`, `win-tracker` jobs,
  `gammarips-eval-*`, all `x-poster-*`, all `blog-generator`/content jobs.
- **No Pub/Sub push subscriptions exist** → the only caller classes are Cloud
  Scheduler + inter-service HTTP (signal-notifier→signal-judge already does
  this authenticated — that's the pattern to replicate). Manual operator curls
  are the only other caller.

Runtime SAs (for granting `run.invoker`): most services run as the **default
compute SA** `406581297632-compute@`; **forward-paper-trader and signal-notifier
run as `firebase-adminsdk-fbsvc@`**. (Minor drift vs the "everything uses the
default compute SA" note — two services don't.)

## Remediation — OIDC-then-lock, per service

Do NOT flip `--no-allow-unauthenticated` first — that breaks the cron for every
NO-OIDC job. Per service, in order:

1. **Give the caller an identity.** For each scheduler job hitting the service:
   ```bash
   gcloud scheduler jobs update http <job> --location=us-central1 \
     --oidc-service-account-email=<CALLER_SA> \
     --oidc-token-audience=<SERVICE_URL>
   ```
   Use a dedicated invoker SA (cleanest) or the appspot SA already used by the
   3 OIDC jobs. Inter-service callers (e.g. anything invoking these) must send
   an identity token too.
2. **Grant invoke rights:**
   ```bash
   gcloud run services add-iam-policy-binding <svc> --region=us-central1 \
     --member=serviceAccount:<CALLER_SA> --role=roles/run.invoker
   ```
3. **Lock the service:** `gcloud run services update <svc> --region=us-central1 --no-allow-unauthenticated`
4. **Fix `deploy.sh` (CRITICAL, or it self-reverts).** Every service's
   `deploy.sh` passes `--allow-unauthenticated`; the next source deploy
   RE-OPENS the door. Change to `--no-allow-unauthenticated` in each locked
   service's deploy script in the same PR.
5. **Verify the cron still fires** (trigger the job, confirm 200 + expected
   write) and that manual operator access still works with
   `--header "Authorization: Bearer $(gcloud auth print-identity-token)"`
   (update the manual-curl snippets in `CLAUDE.md`).

**Also, independent of IAM (correctness bug, do regardless):** the
`/label_enriched_pool` window guard is date-granularity only
(`exit_day > today_et`; under V7.1 same-day hold `exit_day == today` passes at
any hour). Add a time-of-day guard — refuse when `exit_day == today_et` and now
< ~15:50 ET — and do NOT mark the Firestore claim done on a partial-session
label run. `forward-paper-trader/main.py::run_label_enriched_pool`.

## Priority

1. **HIGH / do first:** forward-paper-trader (substrate poisoning + ledger +
   the clock-guard correctness bug), enrichment-trigger (LLM $ + pick pipeline),
   overnight-report-generator + gammarips-eval + blog-generator (LLM $),
   x-poster (public account).
2. **MEDIUM:** signal-notifier (email/pick writes — verify the app-auth grep hit
   first), win-tracker, overnight-scanner.
3. **Keep public:** gammarips-mcp (the product; Phase 2 bearer auth is its lock).

## Scope note

This is infra/security hardening, not a trading-policy change. No leakage or
execution-policy implications. `gammarips-review` before each locking PR (it
touches production-invocation paths). Owner may sequence/waive per service; the
`/label_enriched_pool` clock guard is the one item recommended as non-optional.
