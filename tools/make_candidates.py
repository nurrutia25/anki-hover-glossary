"""Turn MeSH matches + AnKing-only terms + abbreviations into numbered candidate batches.

Each candidate carries how it appears on cards and 1-2 short AnKing snippets so the
definer can tell the medical sense (and skip junk like "will" -> Volition).

Usage: python3 make_candidates.py matched.json extra.json anking.jsonl out_dir [--batch 250]
"""

import collections
import json
import os
import re
import sys

matched_p, extra_p, corpus_p, out_dir = sys.argv[1:5]
BATCH = int(sys.argv[sys.argv.index("--batch") + 1]) if "--batch" in sys.argv else 250

notes = [json.loads(l)["t"] for l in open(corpus_p)]
WORD = re.compile(r"[a-z0-9]+")
index = collections.defaultdict(list)
for ni, t in enumerate(notes):
    for w in set(WORD.findall(t.lower())):
        if len(index[w]) < 400:
            index[w].append(ni)


def snippets(form, case_sensitive=False, k=2, width=110):
    words = WORD.findall(form.lower())
    if not words:
        return []
    pool = min((index.get(w, []) for w in words), key=len)
    pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(form).replace(r"\ ", r"[\s\-]+") + r"(?![A-Za-z0-9])",
                     0 if case_sensitive else re.I)
    out = []
    for ni in pool:
        m = pat.search(notes[ni])
        if not m:
            continue
        a, b = max(0, m.start() - width), min(len(notes[ni]), m.end() + width)
        out.append(("…" if a else "") + notes[ni][a:b].strip() + ("…" if b < len(notes[ni]) else ""))
        if len(out) >= k:
            break
    return out


cands = []
for r in json.load(open(matched_p)):
    form = r["seen_as"][0]
    cands.append({"kind": "mesh", "name": r["name"], "scope": (r["scope"] or "")[:400],
                  "seen_as": r["seen_as"], "notes": r["notes"], "ctx": snippets(form)})
extra = json.load(open(extra_p))
for term, n in extra["eponyms"]:
    cands.append({"kind": "eponym", "name": term, "notes": n, "ctx": snippets(term)})
for w, n in extra["words"]:
    cands.append({"kind": "word", "name": w, "notes": n, "ctx": snippets(w, k=1)})

ABBR = re.compile(r"\b[A-Z][A-Za-z0-9]{0,2}[A-Z0-9]{1,5}s?\b")
ac = collections.Counter()
for t in notes:
    ac.update(set(a for a in ABBR.findall(t) if sum(ch.isupper() for ch in a) >= 2))
for a, n in ac.most_common():
    if n < 3:
        break
    cands.append({"kind": "abbr", "name": a, "notes": n, "ctx": snippets(a, case_sensitive=True)})

os.makedirs(out_dir, exist_ok=True)
for i, c in enumerate(cands):
    c["id"] = i
for b in range(0, len(cands), BATCH):
    with open(os.path.join(out_dir, f"batch_{b // BATCH:03d}.jsonl"), "w") as f:
        for c in cands[b:b + BATCH]:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
kinds = collections.Counter(c["kind"] for c in cands)
print(len(cands), "candidates", dict(kinds), "->", (len(cands) + BATCH - 1) // BATCH, "batches")
