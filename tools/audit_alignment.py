"""Flag kept entries whose term doesn't plausibly belong to their candidate.

Catches definitions written for the wrong line (e.g. two workers' generator scripts
clobbering each other), which check_defs.py can't see because ids still line up.

Usage: python3 tools/audit_alignment.py [batch numbers...]   (default: every defs file)
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORD = re.compile(r"[a-z0-9]+")


def toks(s):
    return {w for w in WORD.findall(s.lower()) if len(w) > 2}


def stem(w):
    return w[:6]


nums = sys.argv[1:] or sorted(os.path.basename(p)[6:9] for p in glob.glob(f"{ROOT}/data/defs/batch_*.jsonl"))
flagged = total = 0
for n in nums:
    cands = [json.loads(l) for l in open(f"{ROOT}/data/candidates/batch_{n}.jsonl")]
    defs = [json.loads(l) for l in open(f"{ROOT}/data/defs/batch_{n}.jsonl") if l.strip()]
    for c, d in zip(cands, defs):
        if "skip" in d:
            continue
        total += 1
        out_names = [d.get("term", "")] + d.get("syn", []) + d.get("abbr", [])
        if c["kind"] == "abbr":
            a = c["name"]
            ok = any(x == a or x == a.rstrip("s") or x.rstrip("s") == a.rstrip("s") for x in d.get("abbr", []))
            ok = ok or a.lower() in d.get("term", "").lower()
        else:
            src = toks(c["name"]) | set().union(*(toks(s) for s in c.get("seen_as", [])))
            got = set().union(*(toks(s) for s in out_names))
            ok = bool({stem(w) for w in src} & {stem(w) for w in got})
        if not ok:
            flagged += 1
            print(f"{n} id={c['id']} cand={c['name']!r} -> term={d.get('term')!r} abbr={d.get('abbr')}")
print(f"\n{flagged} of {total} kept entries look misaligned")
