from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")

flagged = ["engine-post-mortem-first-30-days","first-30-v53-trades","moneyness-5-15-otm",
           "systems-problem-not-pick-problem","whats-pushed-to-my-phone-at-9am","whatsapp-group-tag-the-agent"]

doc = db.collection("blog_schedule").document("current").get()
rows = doc.to_dict().get("rows", []) if doc.exists else []
slot_by_slug = {r.get("slug"): r for r in rows}
print(f"blog_schedule/current rows: {len(rows)}\n")
print("=== schedule slot for each flagged slug ===")
for s in flagged:
    r = slot_by_slug.get(s)
    if r:
        print(f"\n[{s}]  status={r.get('status')}  cta={r.get('cta')}  type={r.get('type')}")
        print(f"   title_candidate: {r.get('title_candidate')}")
    else:
        print(f"\n[{s}]  *** NOT in blog_schedule/current → /generate by slug would fail ***")

print("\n\n=== published blog_posts status for each flagged slug ===")
for s in flagged:
    d = db.collection("blog_posts").document(s).get()
    if d.exists:
        dd = d.to_dict()
        print(f"  {s}: status={dd.get('status')} title={dd.get('title')[:60]!r}")
    else:
        print(f"  {s}: (no blog_posts doc)")
