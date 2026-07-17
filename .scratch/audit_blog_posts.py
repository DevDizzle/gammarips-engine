import re
from google.cloud import firestore

db = firestore.Client(project="profitscout-fida8")
docs = list(db.collection("blog_posts").stream())
print(f"TOTAL blog_posts docs: {len(docs)}\n")

# Stale-narrative patterns (case-insensitive)
patterns = {
    "Agent Arena": r"agent arena|adversarial debate|debate transcript|5[- ]model|five[- ]model|grok|deepseek|consensus debate",
    "Scorer/Picker": r"\bscorer\b|\bpicker\b|two[- ]stage|case[- ]memory|judge_v6|60/25/15",
    "Version label": r"V5[._ ]?4|V5[._ ]?3|V5[._ ]?5|agent ranker",
    "Removed gates": r"moneyness|V/OI|vol/oi|volume[- ]?oi|OI floor|volume floor|5.13% OTM|gate stack|spread (gate|.le|<=|≤)|DTE \d",
    "Deterministic claim": r"deterministic|no judgment|no human judgment|no llm|mechanical filter|tiebreak",
}

flagged = {}
for d in docs:
    data = d.to_dict()
    slug = data.get("slug", d.id)
    title = data.get("title", "")
    status = data.get("status", "")
    body = (data.get("markdown") or "") + " " + title + " " + (data.get("description") or "")
    hits = {}
    for label, pat in patterns.items():
        found = sorted(set(m.group(0).lower() for m in re.finditer(pat, body, re.I)))
        if found:
            hits[label] = found
    if hits:
        flagged[slug] = {"title": title, "status": status, "hits": hits}

print(f"FLAGGED: {len(flagged)} of {len(docs)} posts contain stale narrative\n")
print("="*70)
for slug, info in sorted(flagged.items()):
    print(f"\n[{info['status']}] {slug}")
    print(f"  title: {info['title']}")
    for label, terms in info["hits"].items():
        print(f"    - {label}: {terms}")

print("\n" + "="*70)
print("CLEAN posts (no stale narrative):")
clean = [d.to_dict().get("slug", d.id) for d in docs if d.to_dict().get("slug", d.id) not in flagged]
for s in sorted(clean):
    print(f"  - {s}")
