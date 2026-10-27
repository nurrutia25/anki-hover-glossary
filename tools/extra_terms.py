import json, re, sys, collections
matched = json.load(open(sys.argv[1])); corpus = sys.argv[2]; out = sys.argv[3]
covered = set()
for r in matched:
    for s in r['seen_as']:
        covered.update(s.split())
EP = re.compile(r"\b((?:[A-Z][a-z]+(?:['’]s)?[\- ]){1,3}(?:sign|signs|syndrome|disease|triad|lesions?|nodes?|nodules?|rings?|bodies|body|spots?|reflex|test|maneuver|phenomenon|cells?|criteria|law|murmur|fracture|hernia|tumor|ulcers?|granules?|crystals?|line|lines|score|scale|classification|stage|palsy|deformity|contracture|diverticulum|pouch|space|duct|canal|ligament|area|aphasia|anemia))\b")
WORD = re.compile(r"\b[a-z]{7,}\b")
STOP = set('''because however patients patient following including therefore treatment increased decreased associated presents present between disease usually without another commonly results important typically condition symptoms although''' .split())
ep, words = collections.Counter(), collections.Counter()
for line in open(corpus):
    t = json.loads(line)['t']
    ep.update({m.group(1).strip() for m in EP.finditer(t)})
    words.update({w for w in WORD.findall(t.lower()) if w not in covered and w not in STOP})
eps = [(k, v) for k, v in ep.items() if v >= 2 and not k.split()[0] in ('The','This','These','Most','Which','What','Common','Acute','Chronic','Primary','Secondary')]
ws = [(k, v) for k, v in words.items() if v >= 2]
json.dump({'eponyms': sorted(eps, key=lambda x: -x[1]), 'words': sorted(ws, key=lambda x: -x[1])}, open(out, 'w'))
print(len(eps), 'eponym-style phrases;', len(ws), 'uncovered words (>=2 notes)')
print([k for k, _ in sorted(eps, key=lambda x: -x[1])[:40]])
print([k for k, _ in sorted(ws, key=lambda x: -x[1])[:80]])
print([k for k, _ in sorted(ws, key=lambda x: -x[1])[3000:3060]])
