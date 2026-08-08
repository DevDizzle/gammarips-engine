---
name: seo-auth
description: Authenticate the Google Search Console / GA4 read scripts in scripts/seo/. Use whenever a GSC or GA4 pull returns 403, "insufficient authentication scopes", "Unable to acquire impersonated credentials", or whenever the task needs Search Console / GA4 data and auth state is unknown. Carries the permanent service-account fix, the interactive-login FIFO workaround, and the traps that have burned multiple sessions.
---

# Authenticating the SEO scripts

`scripts/seo/{gsc_query,gsc_inspect,ga4_query}.py` need Google Search Console and
GA4 read access. There are two ways to get it. **One is permanent and one is a
treadmill. Always drive toward the permanent one.**

This flow has been re-derived from scratch in multiple sessions and the owner is
correctly sick of it. Do not improvise here — follow this file.

## Decide in one command

```bash
cd ~/workspace/projects/gammarips-engine
scripts/seo/.venv/bin/python scripts/seo/gsc_query.py --days 28 --dim page --limit 3
```

| What you get | What it means | Go to |
|---|---|---|
| Rows of data | Auth is fine | Nothing to do — run the real query |
| `403 ... insufficient authentication scopes` | `SEO_IMPERSONATE_SA` is unset — running as the user, which can no longer work | **Path A** |
| `403 ... User does not have sufficient permission for site` | Impersonation works; the SA is not a property user yet | **Path A**, step A2/A3 |
| `403 ... iam.serviceAccounts.getAccessToken denied` | Impersonating, but the token-creator binding is missing | **Path A**, step A1 |
| `(no rows)` on stderr, HTTP 200 | Auth worked; the SA/user is not a property user, or `GSC_SITE_URL` is wrong | **Path A**, steps A2/A3 |

Never diagnose past this table by guessing. The three 403s look alike and mean
completely different things.

---

## Path A — the permanent fix (service account impersonation)

**Do this first, every time, unless it is already done.** It does not expire, it
survives Google's client-ID scope purge, and it works headless — which is what
lets an SEO check ride along with a cron job instead of needing a human.

Service account: `ga-admin@profitscout-fida8.iam.gserviceaccount.com`

**A1. Token-creator binding** (owner-run, or ask before running — prod IAM change).
`roles/owner` does **not** include this; Google separates impersonation from basic
roles on purpose.

```bash
gcloud iam service-accounts add-iam-policy-binding \
  ga-admin@profitscout-fida8.iam.gserviceaccount.com \
  --member="user:eraphaelparra@gmail.com" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project=profitscout-fida8
```

**A2. Add the SA as a Search Console user** — UI only, no API exists. Search
Console → gammarips.com property → Settings → Users and permissions → Add user →
the SA email → **Full**. A service account email is a valid GSC user; this is the
documented automation path.

**A3. Add the SA to GA4** — Admin → Property Access Management → Add users → the
SA email → **Viewer**, uncheck "Notify by email".

**A4. Make it the default** so no future session has to think about it:

```bash
export SEO_IMPERSONATE_SA=ga-admin@profitscout-fida8.iam.gserviceaccount.com
```

Persist it in `~/.bashrc`. Steps A2 and A3 are the owner's to click; A1 and A4 are
runnable. If A2/A3 are outstanding, hand the owner a **file** (see "Owner can't
copy from the terminal" below), not terminal output.

---

## Path B — interactive ADC login: **DEAD, DO NOT ATTEMPT**

**Confirmed blocked 2026-08-08.** The consent screen now returns:

> This app is blocked — This app tried to access sensitive info in your Google
> Account. To keep your account safe, Google blocked this access.

Google has blocked the **shared gcloud client ID** from requesting Search Console
and Analytics scopes. The block is on the OAuth app, not the account: the owner is
GCP Owner and a Search Console admin and it still fails. There is no retry, no
flag, and no shell that makes this work.

If a session finds itself about to run `gcloud auth application-default login`
with `webmasters.readonly` or `analytics.readonly`, **stop** — that is the loop
this skill exists to end. Go to Path A. `scripts/seo/reauth.sh` is retained only
for its guard rails and should be considered decommissioned.

The rest of this section is kept as an archaeological record so the failure is
recognized instantly and not re-litigated.

### Why it looked like a TTY problem for so long

Two unrelated failures stacked, and each hid the other:

1. `gcloud auth application-default login` prompts on stdin. Claude Code's `!`
   prefix has no TTY → `gcloud crashed (EOFError)`. Backgrounding with `< fifo`
   and holding the write end via `exec 3>fifo` fails the same way, because the
   Bash tool's shell exits and closes fd 3. A `nohup sleep N > fifo &` holder
   fixes *that* — and only then does the real blocker surface.
2. Once the prompt finally worked, the consent screen was blocked outright.

So every earlier session "fixed" problem 1, hit problem 2, and read it as another
scope lapse. Both are now moot: Path A avoids user OAuth entirely.

### The historical trap detail

`gcloud auth application-default login` prompts on stdin for a verification code.

- The `!` prefix in Claude Code runs **without a TTY** → `gcloud crashed (EOFError)`.
- `scripts/seo/reauth.sh` has the same problem for the same reason.
- Backgrounding it with `< fifo` and holding the write end with `exec 3>fifo`
  **also fails** — the Bash tool's shell exits, fd 3 closes, gcloud reads EOF.

The write end needs a process that outlives the shell.

### The working recipe

```bash
S=<scratchpad>
rm -f $S/authfifo $S/auth.log; mkfifo $S/authfifo
nohup gcloud auth application-default login --no-launch-browser \
  --scopes=https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform \
  < $S/authfifo > $S/auth.log 2>&1 &
nohup sleep 2400 > $S/authfifo &        # <-- holds the FIFO open; this is the whole trick
sleep 6
pgrep -f "auth application-default login" >/dev/null && echo WAITING || echo DEAD
grep -oE 'https://accounts\.google\.com/o/oauth2/auth[^ ]*' $S/auth.log | head -1
```

Give the owner the URL, get the `4/...` code back **in chat**, then deliver it:

```bash
echo "4/0AX4..." > $S/authfifo
sleep 5 && tail -3 $S/auth.log        # confirm credentials were saved
```

This recipe successfully reaches the consent screen. The consent screen then
blocks. Kept only because the FIFO holder trick is reusable for *any* stdin-
interactive CLI run from the Bash tool.

---

## Owner can't copy from the terminal

Claude Code renders in a terminal; the owner cannot copy long URLs or commands out
of it. Anything they must paste elsewhere — consent URLs, gcloud commands, SA
emails — goes in a **plain text file at a short path they can type**, e.g.
`~/AUTH.txt`, and tell them the path. Do not print a 600-character OAuth URL into
chat and expect it to be usable. Do not publish an active OAuth consent URL to a
hosted artifact.

## Facts worth not re-deriving

- Property: `GSC_SITE_URL=sc-domain:gammarips.com` (domain property, not URL-prefix).
- ADC user is `eraphaelparra@gmail.com`, not the business identity.
- ADC's `quota_project_id` may point at an unrelated project (`atlas-voice-agent-2026`
  as of 2026-08-08). Harmless for these APIs — do not chase it.
- Scripts run under `scripts/seo/.venv/bin/python`, never system python.
- Everything in `scripts/seo/` is read-only against GA4/GSC by design. Keep it that
  way; `gsc_inspect.py` uses URL Inspection, which never submits or reindexes.
- URL Inspection quota: 2,000/day, 600/min per property.
