from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")
rows = db.collection("blog_schedule").document("current").get().to_dict().get("rows", [])
import json
for r in rows:
    if r.get("slug") == "whats-pushed-to-my-phone-at-9am":
        print(json.dumps(r, indent=2, default=str))
