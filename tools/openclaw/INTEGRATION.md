# OpenClaw ↔ GammaRips integration (paywall + chat agent)

Two config changes Evan makes in his OpenClaw install, plus one Cloud-Run
service already wired (`signal-notifier → /hooks/agent`).

## 1. Group-membership paywall (OpenClaw config)

Edit `~/.openclaw/config.json`:

```jsonc
{
  "channels": {
    "whatsapp": {
      "accounts": {
        "default": {
          "enabled": true,
          "dmPolicy": "deny",              // no DMs, group-only
          "groupPolicy": "allowlist",      // only listed senders can trigger
          "groupAllowFrom": [
            "+15551234567"                 // ← filled in by sync script
          ],
          "groups": {
            "120363..@g.us": {             // ← replace with GROUP_JID
              "enabled": true,
              "requireMention": true       // agent only responds to @mention
            }
          }
        }
      }
    }
  },
  "hooks": {
    "enabled": true,
    "token": "<OPENCLAW_HOOKS_TOKEN>",
    "path": "/hooks"
  }
}
```

- `groupPolicy: "allowlist"` means non-subscribers in the group (if they
  somehow get added) can see messages but can't trigger the agent.
- `requireMention: true` means the agent only responds to explicit @mentions,
  not every message — quieter group, cheaper LLM spend.
- `dmPolicy: "deny"` prevents DM bypass (Pro is group-only by design).

## 2. Allowlist sync (two options)

**A) Manual (launch-week workflow).** After every new subscriber:

1. Evan manually adds the new sub's phone number to the WhatsApp group.
2. Evan edits the Firestore `whatsapp_allowlist/{uid}` doc, setting
   `senderId` to the subscriber's E.164 number (e.g., `+15551234567`).
3. Run the sync script:

   ```bash
   python tools/openclaw/whatsapp_allowlist_sync.py --project profitscout-fida8
   ```

   Copy the `groupAllowFrom` array from the output into
   `~/.openclaw/config.json`.
4. `openclaw reload` (or restart the daemon).

**B) Automated (post-launch).** Wire this script as a Cloud Run cron service
(every 15 min) that writes the patch directly to a GCS bucket OpenClaw reads
on reload. Defer until ≥50 paid subs — manual is faster below that.

## 3. signal-notifier → OpenClaw (already shipped)

`signal-notifier/main.py` now POSTs to `${OPENCLAW_GATEWAY_URL}/hooks/agent`
after every daily decision (happy path + skip paths). Payload:

```json
{
  "chat_jid": "<OPENCLAW_GROUP_JID>",
  "text": "GammaRips — 2026-04-22\nFIX BULLISH..."
}
```

Three secrets must be mounted on the `signal-notifier` Cloud Run service:
- `OPENCLAW_GATEWAY_URL`
- `OPENCLAW_HOOKS_TOKEN`
- `OPENCLAW_GROUP_JID`

If any are missing the POST is skipped silently — email delivery is
unaffected. Redeploy after secrets are mounted:

```bash
cd signal-notifier && bash deploy.sh
```

## 4. Agent system prompt

Drop `tools/openclaw/agent-system-prompt.md` into OpenClaw's agent config as
the system prompt. Recommended model: Claude Haiku 4.5 with prompt caching
(4-hour cache TTL covers a full trading day; ~$0.10/user/month at ~5
messages/day).

## Launch-day test checklist

- [ ] Group created, OpenClaw number paired, `GROUP_JID` copied into config
- [ ] 3 secrets mounted on `signal-notifier` Cloud Run service
- [ ] `signal-notifier` redeployed (check logs for "OpenClaw push OK")
- [ ] Evan paid $29 via founder coupon → Stripe webhook fires → Firestore
      `whatsapp_allowlist/{evan_uid}` exists with `status: provisioned`
- [ ] Evan manually adds himself to the group + sets `senderId = +1...`
- [ ] `whatsapp_allowlist_sync.py` dry-run includes Evan's number
- [ ] Config patched + OpenClaw reloaded
- [ ] Evan @mentions the agent in the group → agent replies with disclaimer
- [ ] Monday 09:00 ET → WhatsApp ping fires with that day's pick (or skip)
