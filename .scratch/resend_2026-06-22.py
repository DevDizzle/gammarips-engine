"""One-shot: resend the ALREADY-DECIDED 2026-06-22 pick (TTWO) email + sub fan-out.

Why: Friday's pre-holiday-guard Juneteenth cron claimed email_sends/2026-06-18
at 07:31 ET 06-19. Monday re-processed the SAME scan_date (no scan over the
holiday) and the dedup guard suppressed the real email. The pick (TTWO) is
already written to todays_pick/{2026-06-18, 2026-06-22} and on the site; this
re-emits it WITHOUT re-running the randomized tournament. No claim is touched.
"""
from datetime import date
import main  # imported with MAILGUN_* env + PROJECT_ID=profitscout-fida8 set

SCAN_DATE = date(2026, 6, 18)
ENTRY_DAY = date(2026, 6, 22)

doc = main.firestore.Client(project="profitscout-fida8") \
    .collection("todays_pick").document(SCAN_DATE.isoformat()).get().to_dict()

assert doc and doc.get("has_pick") and doc.get("ticker") == "TTWO", \
    f"refusing: unexpected pick doc {doc!r}"

# Reconstruct the `top` row the email builder expects. format_email_html uses
# row[...] + row.get(...), so a plain dict works. Map vol_oi_ratio ->
# volume_oi_ratio (the key the builder reads).
top = dict(doc)
top["volume_oi_ratio"] = doc.get("vol_oi_ratio")

v5_4_meta = {
    "justification": doc.get("v5_4_justification"),
    "confidence": doc.get("v5_4_confidence"),
    "runner_up": doc.get("v5_4_runner_up"),
}

subject = f"GammaRips {ENTRY_DAY}: {top['ticker']} {top['direction']}"
html = main.format_email_html(top, SCAN_DATE, ENTRY_DAY, v5_4_meta=v5_4_meta)

subs = main.fetch_paid_subscriber_emails()
print(f"Subject : {subject}")
print(f"Operator: {main.RECIPIENT_EMAIL}")
print(f"Subs    : {len(subs)} -> {subs}")

op_ok = main.send_email(subject, html)
print(f"Operator email sent: {op_ok}")

fan = main.fan_out_to_paid_subscribers(subject, html)
print(f"Subscriber fan-out delivered: {fan}/{len(subs)}")

# WhatsApp mirror (no-ops cleanly if OPENCLAW_* env absent, same as prod).
main.post_to_openclaw(main.format_whatsapp_message(
    top, SCAN_DATE, ENTRY_DAY, has_pick=True, v5_4_meta=v5_4_meta,
))
print("done")
