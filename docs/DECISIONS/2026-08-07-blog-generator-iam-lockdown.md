# 2026-08-07 — blog-generator IAM lockdown: public newsletter fan-out closed

**Status: DEPLOYED (owner go). `blog-generator` is IAM-locked; 5 Cloud Scheduler jobs moved to OIDC.**

## Problem

`blog-generator` was deployed `--allow-unauthenticated` while exposing mutating
routes that need no guessed arguments:

- **`POST /blast_latest {"audience":"all","dry_run":false}`** — auto-discovers
  the latest draft and fans the **real newsletter** out to every non-anonymous
  user in the Firestore `users` collection, up to `MAX_RECIPIENTS=1000`. The
  only brake was the `blast_history/{date}` idempotency lock, which caps an
  unauthorized send at **one per draft date, not zero**.
- `POST /blast_email` — same fan-out, needs only a guessable
  `gs://gammarips-content-drafts/email/<date>_newsletter.html` path.
- `POST /generate` — anyone could burn Gemini quota and write `blog_posts/{slug}`
  (the published-slug clobber guard limits it to creating new posts).
- `POST /draft_reddit`, `POST /weekly_intel` — likewise open.

Found by `gammarips-review` (finding B7) during the audit of the SEO routes.
Pre-existing, not introduced by that work.

The 2026-07-30 SEO work had added a shared-token gate (`X-Seo-Token`) to its own
two routes, which made those the **only** authenticated surface on the service.
Token-gating the remaining five would have been a strictly LARGER change than
closing the front door.

## Change

1. **`--allow-unauthenticated` -> `--no-allow-unauthenticated`** in `deploy.sh`.
   **Note:** that flag alone does NOT revoke an existing `allUsers` binding — it
   applies at service creation. The binding had to be confirmed gone from the
   live IAM policy after deploy, and there is a short propagation window in
   which the old public access still answers 200. Verify, do not assume.
2. **`roles/run.invoker` granted** to `406581297632-compute@developer.gserviceaccount.com`
   (the SA already used for OIDC by `dbt-source-freshness`, `dbt-daily-build`,
   `freshness-digest`, `fill-closed-windows` — established pattern, not a new
   identity).
3. **All 5 scheduler jobs moved to OIDC** with that SA and
   `--oidc-token-audience=https://blog-generator-406581297632.us-central1.run.app`:
   `blog-generator-weekly` (Mon 05:00 ET, ENABLED),
   `content-drafter-weekly-email` (Sun 17:00 ET, ENABLED),
   `content-blast-mon-0530` (PAUSED), `weekly-intel-mon-0700` (PAUSED),
   `content-drafter-weekly-reddit` (PAUSED).
   **Ordering matters:** the invoker grant and the OIDC updates landed BEFORE
   public access was removed, so no cron was ever left unable to authenticate.

`SEO_ADMIN_TOKEN` is retained as a **second factor** on the two SEO routes, not
as the only control.

## Verification

- All five mutating routes return **403 unauthenticated** (`/blast_latest`,
  `/generate`, `/draft_reddit`, `/weekly_intel`, `/blast_email`).
- Live IAM policy contains exactly one binding: `roles/run.invoker` ->
  the compute SA. No `allUsers`.
- OIDC path proven with a disposable scheduler job (`tmp-oidc-authcheck`) hitting
  `/generate` with `{"dry_run": true}` as the compute SA — the request reached
  the container and executed, which an IAM-rejected request cannot do. Job
  deleted afterward.

Revision: `blog-generator-00033-9nv`.

## Operator impact

Ad-hoc calls now need an identity token:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     -H "Content-Type: application/json" \
     -X POST https://blog-generator-406581297632.us-central1.run.app/generate \
     -d '{"dry_run": true}'
```

`.scratch/regen.sh` calls `/generate` and will need the same header.

## Not done here

`x-poster` and `win-tracker` were not audited for the same exposure in this
change. `x-poster` publishes to @gammarips on enabled crons and should get the
same treatment — route to `gammarips-engineer`.
