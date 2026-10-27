import json, re, sys, collections
mesh = json.load(open(sys.argv[1])); corpus = sys.argv[2]; out = sys.argv[3]
SKIP_BRANCH = ('M', 'N', 'Z', 'K', 'L', 'V', 'I', 'H')  # people, health care, places, humanities, info sci, pub types, social, disciplines
tok = re.compile(r"[a-z0-9]+(?:['\-][a-z0-9]+)*")
def norm(s):
    return ' '.join(tok.findall(s.lower()))
def forms(s):
    out = {s}
    if ', ' in s and s.count(',') == 1:
        a, b = s.split(', '); out.add(f'{b} {a}')
    return {norm(x) for x in out}
lookup = {}
for i, r in enumerate(mesh):
    if r['trees'] and all(t[0] in SKIP_BRANCH for t in r['trees']):
        continue
    for s in [r['name']] + r['syn']:
        for f in forms(s):
            if len(f) < 4 or f.isdigit():
                continue
            lookup.setdefault(f, i)
maxn = max(len(k.split()) for k in lookup); maxn = min(maxn, 7)
counts = collections.Counter(); surface = collections.defaultdict(collections.Counter)
for line in open(corpus):
    words = tok.findall(json.loads(line)['t'].lower())
    seen = set()
    for n in range(maxn, 0, -1):
        for j in range(len(words) - n + 1):
            g = ' '.join(words[j:j+n])
            i = lookup.get(g)
            if i is None and g.endswith('s'):
                i = lookup.get(g[:-1]) if lookup.get(g[:-1]) is not None else lookup.get(g[:-2]) if g.endswith('es') else None
            if i is not None:
                surface[i][g] += 1
                seen.add(i)
    counts.update(seen)
res = []
for i, c in counts.most_common():
    r = mesh[i]
    res.append({'ui': r['ui'], 'name': r['name'], 'notes': c, 'trees': r['trees'][:3],
                'scope': r['scope'], 'seen_as': [s for s, _ in surface[i].most_common(6)]})
json.dump(res, open(out, 'w'))
print(len(res), 'MeSH concepts appear in AnKing')
for k in (1, 2, 3, 5, 10, 25):
    print(f'  in >= {k} notes:', sum(1 for r in res if r['notes'] >= k))
