from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")

# ONLY the 3 the owner explicitly designated as dead/unpublish:
to_archive = {
    "moneyness-5-15-otm": "V6 removed the moneyness selection gate — the whole topic no longer exists",
    "first-30-v53-trades": "V5.3 cohort was wiped (ledger truncated); that track record no longer exists",
    "engine-post-mortem-first-30-days": "Post-mortem of the wiped V5.3/V5.4 cohort; V6 has <30 closes so no V6 30-day retro is possible yet",
}

for slug, reason in to_archive.items():
    ref = db.collection("blog_posts").document(slug)
    snap = ref.get()
    if not snap.exists:
        print(f"SKIP {slug}: no doc")
        continue
    cur = snap.to_dict().get("status")
    ref.update({"status": "archived", "archived_reason": reason, "prev_status": cur})
    print(f"ARCHIVED {slug} (was {cur!r})")

print("\n--- verify ---")
for slug in to_archive:
    print(f"  {slug}: status={db.collection('blog_posts').document(slug).get().to_dict().get('status')}")
