"""Compile glossary entries (JSONL) into addon/web/glossary_data.js.

Each input line: {"term": str, "def": str, "syn": [str], "abbr": [str]}
  syn  - other spellings/names, matched case-insensitively (plural -s/-es handled in JS)
  abbr - abbreviations, matched case-sensitively as whole words

Usage: python3 build_data.py entries.jsonl [more.jsonl ...] -o ../addon/web/glossary_data.js
"""

import argparse
import json
import re

WORD = re.compile(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*")
# Abbreviations too ambiguous to match on their own, whatever an entry says.
NEVER_ABBR = {
    "A", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "OR", "NO", "US", "AND", "NOT",
    "AKA", "CC", "BY", "SA", "ND", "NC", "NZ", "ID", "IT", "AM", "PM", "MD", "DO", "PO", "ST", "PT",
    "CO", "HR", "OK", "VS", "IN", "ON", "AT", "AS", "BE", "TO", "UK", "USA", "IL",
}


# Phrases never marked: everyday words a college reader knows, or names that would map to
# a misleading umbrella entry (any "dehydrogenase" → Oxidoreductase).
NEVER_KEY = {
    "shock", "gout", "mutation", "mutations", "mri", "estrogen", "estrogens", "dopamine",
    "serotonin", "dehydrogenase", "dehydrogenases", "reductase", "reductases", "oxidase",
    "oxidases", "kinase", "kinases", "hormone", "hormones", "antibiotic", "antibiotics",
    "vitamin", "vitamins", "tumor", "tumors", "virus", "viruses", "infection", "infections",
}


def norm(s):
    return " ".join(w.lower().replace("’", "'") for w in WORD.findall(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()

    entries, keys, abbrs, maxn = [], {}, {}, 1
    by_term = {}
    conflicts = 0
    for path in args.inputs:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if not r.get("def"):
                continue
            ab = [a for a in r.get("abbr", []) if a and a not in NEVER_ABBR and len(a) >= 2]
            # The same concept can arrive twice (MeSH heading + abbreviation candidate):
            # keep the first definition, pool the names.
            idx = by_term.get(norm(r["term"]))
            if idx is None:
                idx = by_term[norm(r["term"])] = len(entries)
                entries.append([r["term"], r["def"].strip(), []])
            entries[idx][2] += [a for a in ab if a not in entries[idx][2]]
            for s in [r["term"]] + r.get("syn", []):
                k = norm(s)
                if len(k) < 3 or k.isdigit() or k in NEVER_KEY:
                    continue
                if k in keys and keys[k] != idx:
                    conflicts += 1
                    continue
                keys[k] = idx
                maxn = max(maxn, len(k.split()))
            for a in ab:
                if a in abbrs and abbrs[a] != idx:
                    conflicts += 1
                    continue
                abbrs[a] = idx
    data = {"e": entries, "k": keys, "a": abbrs, "n": min(maxn, 8)}
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("window.HG_DATA=")
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"{len(entries)} entries, {len(keys)} phrases, {len(abbrs)} abbreviations, "
          f"max {data['n']} words, {conflicts} duplicate keys skipped -> {args.out}")


if __name__ == "__main__":
    main()
