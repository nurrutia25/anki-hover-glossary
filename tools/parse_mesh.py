import gzip, json, sys
import xml.etree.ElementTree as ET
src, out = sys.argv[1], sys.argv[2]
recs = []
for ev, el in ET.iterparse(gzip.open(src), events=('end',)):
    if el.tag != 'DescriptorRecord':
        continue
    name = el.findtext('DescriptorName/String')
    trees = [t.text for t in el.findall('TreeNumberList/TreeNumber')]
    scope, terms = None, set()
    for c in el.findall('ConceptList/Concept'):
        if c.get('PreferredConceptYN') == 'Y':
            scope = (c.findtext('ScopeNote') or '').strip() or None
        for t in c.findall('TermList/Term'):
            s = t.findtext('String')
            if s: terms.add(s)
    recs.append({'ui': el.findtext('DescriptorUI'), 'name': name, 'trees': trees,
                 'scope': scope, 'syn': sorted(terms - {name})})
    el.clear()
json.dump(recs, open(out, 'w'))
print(len(recs), 'descriptors;', sum(len(r['syn']) for r in recs), 'synonyms')
