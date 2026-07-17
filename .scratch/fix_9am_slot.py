from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")
ref = db.collection("blog_schedule").document("current")
data = ref.get().to_dict()
rows = data.get("rows", [])
changed = False
for r in rows:
    if r.get("slug") == "whats-pushed-to-my-phone-at-9am":
        r["title_candidate"] = "What Gets Pushed to My Phone at 7:30 AM ET (Weekly Engine Recap)"
        r["keywords"] = ["options morning alerts", "7:30 AM options trade"]
        changed = True
if changed:
    ref.update({"rows": rows})
    print("UPDATED 9am slot title + keywords")
# verify
for r in ref.get().to_dict().get("rows", []):
    if r.get("slug") == "whats-pushed-to-my-phone-at-9am":
        print("title:", r["title_candidate"]); print("keywords:", r["keywords"])
