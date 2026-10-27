"""Validate one definitions batch against its candidates batch.

Usage: python3 tools/check_defs.py data/candidates/batch_NNN.jsonl data/defs/batch_NNN.jsonl
Exits non-zero and lists problems if anything is off.
"""

import json
import sys

SKIPS = {"obvious", "not-medical", "wrong-sense", "fragment", "ambiguous"}

cand_p, defs_p = sys.argv[1], sys.argv[2]
cands = [json.loads(l) for l in open(cand_p) if l.strip()]
problems = []
try:
    lines = [l for l in open(defs_p) if l.strip()]
except OSError as e:
    sys.exit(f"cannot read {defs_p}: {e}")
if len(lines) != len(cands):
    problems.append(f"{len(lines)} output lines for {len(cands)} candidates")
kept = 0
for n, (line, c) in enumerate(zip(lines, cands), 1):
    try:
        r = json.loads(line)
    except ValueError:
        problems.append(f"line {n}: not valid JSON")
        continue
    if r.get("id") != c["id"]:
        problems.append(f"line {n}: id {r.get('id')} != candidate id {c['id']}")
    if "skip" in r:
        if r["skip"] not in SKIPS:
            problems.append(f"line {n}: unknown skip reason {r['skip']!r}")
        continue
    kept += 1
    for f in ("term", "def"):
        if not isinstance(r.get(f), str) or not r[f].strip():
            problems.append(f"line {n}: missing {f}")
    for f in ("syn", "abbr"):
        if not isinstance(r.get(f, []), list):
            problems.append(f"line {n}: {f} must be a list")
    words = len(str(r.get("def", "")).split())
    if words > 60:
        problems.append(f"line {n}: definition is {words} words (cap 60)")
    if any(ch in str(r.get("def", "")) for ch in "<>*`"):
        problems.append(f"line {n}: markup in definition")
if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"ok: {len(lines)} lines, {kept} kept, {len(lines) - kept} skipped")
