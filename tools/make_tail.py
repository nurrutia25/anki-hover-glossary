"""Stage the long tail: words (8+ letters) on exactly one AnKing card that no glossary entry
covers yet. Writes data/candidates/batch_1NN.jsonl in the same format as make_candidates.py,
numbered from 100 so they never collide with the main run.

Usage: python3 tools/make_tail.py anking.jsonl [--batch 250]
"""

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
corpus_p = sys.argv[1]
BATCH = int(sys.argv[sys.argv.index("--batch") + 1]) if "--batch" in sys.argv else 250

d = open(f"{ROOT}/addon/web/glossary_data.js").read()
data = json.loads(d[d.index("=") + 1:d.rindex(";")])
known = set(data["k"]) | {w for k in data["k"] for w in k.split()}

notes = [json.loads(l)["t"] for l in open(corpus_p)]
count, where = collections.Counter(), {}
for ni, t in enumerate(notes):
    for w in set(re.findall(r"\b[a-z]{8,}\b", t.lower())):
        count[w] += 1
        where[w] = ni
words = sorted(w for w, n in count.items() if n == 1 and w not in known and w[:-1] not in known)

start = max(json.loads(l)["id"] for f in os.listdir(f"{ROOT}/data/candidates")
            for l in open(f"{ROOT}/data/candidates/{f}")) + 1
cands = []
for i, w in enumerate(words):
    t = notes[where[w]]
    m = re.search(re.escape(w), t, re.I)
    a, b = max(0, m.start() - 110), min(len(t), m.end() + 110)
    cands.append({"kind": "word", "name": w, "notes": 1, "ctx": [t[a:b].strip()], "id": start + i})
for b in range(0, len(cands), BATCH):
    with open(f"{ROOT}/data/candidates/batch_{100 + b // BATCH:03d}.jsonl", "w") as f:
        for c in cands[b:b + BATCH]:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
print(len(cands), "tail candidates ->", (len(cands) + BATCH - 1) // BATCH, "batches from batch_100")
