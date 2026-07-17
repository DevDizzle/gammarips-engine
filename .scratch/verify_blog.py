import re
from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")

regen = ["systems-problem-not-pick-problem","whatsapp-group-tag-the-agent"]
stale = re.compile(r"V5[._ ]?[345]|agent arena|scorer|picker|gate stack|5.13% OTM|5.15% OTM|9:00 ?AM|deterministic (gate|tiebreak)|two[- ]stage", re.I)

print("=== regenerated posts: status + stale-term scan ===")
for s in regen:
    d = db.collection("blog_posts").document(s).get().to_dict()
    body = (d.get("markdown") or "") + " " + (d.get("title") or "")
    hits = sorted(set(m.group(0) for m in stale.finditer(body)))
    print(f"  {s}: status={d.get('status')} | tournament_mention={'tournament' in body.lower()} | stale_hits={hits or 'NONE'}")

print("\n=== published count (what /blog index will show) ===")
pub = [x.id for x in db.collection('blog_posts').stream() if x.to_dict().get('status')=='published']
print(f"  published: {len(pub)}")
arch = [x.id for x in db.collection('blog_posts').stream() if x.to_dict().get('status')=='archived']
print(f"  archived: {arch}")
