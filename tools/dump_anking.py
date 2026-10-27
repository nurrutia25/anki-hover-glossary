import sqlite3, sys, re, json, html
db, out = sys.argv[1], sys.argv[2]
con = sqlite3.connect(db)
mids = {r[0]: r[1] for r in con.execute("select id, name from notetypes")}
anking = [m for m, n in mids.items() if 'AnKing' in n or 'AnKingMed' in n]
inline = re.compile(r'</?(b|i|u|em|strong|span|font|sup|sub|a|mark|small)(\s[^>]*)?>', re.I)
tagre = re.compile(r'<[^>]+>')
clz = re.compile(r'\{\{c\d+::(.*?)(::[^}]*)?\}\}', re.S)
n = 0
with open(out, 'w') as f:
    for nid, mid, flds, tags in con.execute(f"select id, mid, flds, tags from notes where mid in ({','.join(map(str, anking))})"):
        parts = flds.split('\x1f')
        txt = ' \n '.join(parts[:2] + parts[2:6])  # Text, Extra and the first few others
        txt = clz.sub(r'\1', txt)
        txt = re.sub(r'\[#!occlusions.*?#\]', ' ', txt, flags=re.S)
        txt = html.unescape(tagre.sub(' ', inline.sub('', txt)))
        txt = re.sub(r'\s+', ' ', txt).strip()
        f.write(json.dumps({'id': nid, 't': txt, 'tags': tags.strip()}) + '\n'); n += 1
print(n, 'notes')
