import re
from google.cloud import firestore
db = firestore.Client(project="profitscout-fida8")

# 1) picker context
d = db.collection("blog_posts").document("systems-problem-not-pick-problem").get().to_dict()
body = d.get("markdown") or ""
for m in re.finditer(r".{40}picker.{40}", body, re.I):
    print("PICKER CTX:", repr(m.group(0)))

# 2) 9am current status (first reject may have overwritten the doc)
n = db.collection("blog_posts").document("whats-pushed-to-my-phone-at-9am").get().to_dict()
print("\n9am: status=", n.get("status"), "| title=", repr((n.get('title') or '')[:70]))
print("9am body mentions '9:00 AM'?", "9:00 AM" in (n.get("markdown") or ""))
print("9am body mentions '7:30'?", "7:30" in (n.get("markdown") or ""))

# 3) full published list
pub = sorted(x.id for x in db.collection('blog_posts').stream() if x.to_dict().get('status')=='published')
other = sorted((x.id, x.to_dict().get('status')) for x in db.collection('blog_posts').stream() if x.to_dict().get('status') not in ('published','archived'))
print("\nPUBLISHED (%d):" % len(pub)); [print("  ",s) for s in pub]
print("NON-pub/non-arch:", other)
