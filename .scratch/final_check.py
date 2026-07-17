import re
from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")
stale = re.compile(r"V5[._ ]?[345]|agent arena|gate stack|5.1[35]% OTM|9:00 ?AM|deterministic (gate|tiebreak)", re.I)

d = db.collection("blog_posts").document("whats-pushed-to-my-phone-at-9am").get().to_dict()
body = (d.get("markdown") or "")
print("9am: status=", d.get("status"))
print("  title:", repr((d.get("title") or "")[:75]))
print("  mentions 7:30?", "7:30" in body, "| mentions 9:00 AM?", "9:00 AM" in body)
print("  stale hits:", sorted(set(m.group(0) for m in stale.finditer(body+(d.get('title') or '')))) or "NONE")

pub = sorted(x.id for x in db.collection('blog_posts').stream() if x.to_dict().get('status')=='published')
arch = sorted(x.id for x in db.collection('blog_posts').stream() if x.to_dict().get('status')=='archived')
print(f"\nFINAL: {len(pub)} published, {len(arch)} archived")
print("published:", pub)
print("archived:", arch)
