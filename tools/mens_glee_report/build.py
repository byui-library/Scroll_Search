import json, re, sys, html, os
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from entries import E
B = chr(92)
u = {r['id']: r for r in json.load(open(os.path.join(S, 'glee_u.json'), encoding='utf-8'))}

def loc(i):
    src = u[i]['source'].strip()
    page = ''
    m = re.match(r'(.*) \| page (\d+)$', src)
    if m:
        src, page = m.group(1).strip(), 'p. ' + m.group(2)
    else:
        m2 = re.search(r'_0*(\d+)\.tif$', src) or re.search(r'Scl\d{8}(\d\d)\w*\.tif$', src) or re.search(r'FN-0*(\d+)\.tif$', src)
        page = 'scan ' + m2.group(1) if m2 else ''
    rel = src.split('Scroll Rescan Project' + B)[-1]
    return rel, page

def paper(rel):
    if 'Scroll_1927-1929' in rel: return 'Scroll (bound 1927–29)'
    if rel.startswith('Scroll_StudentRays'): return 'Student Rays'
    return rel.split(B)[0]

rows = {'glee': [], 'combined': [], 'chorus': []}
nloc = 0
for label, key, ids, grp, summ in sorted(E, key=lambda e: e[1]):
    rel, pg = loc(ids[0]); nloc += len(ids)
    dups = ''.join('<span class="dup">also: %s <span class="pg">%s</span></span>' % (html.escape(r2), html.escape(p2))
                   for r2, p2 in (loc(j) for j in ids[1:]))
    rows[grp].append('<tr><td class="date">%s</td><td class="paper">%s</td><td>%s</td><td class="loc">%s <span class="pg">%s</span>%s</td></tr>'
                     % (html.escape(label), html.escape(paper(rel)), html.escape(summ), html.escape(rel), html.escape(pg), dups))
t = open(os.path.join(S, 'template.html'), encoding='utf-8').read()
t = (t.replace('{{ROWS_GLEE}}', '\n'.join(rows['glee'])).replace('{{ROWS_COMB}}', '\n'.join(rows['combined']))
      .replace('{{ROWS_CHORUS}}', '\n'.join(rows['chorus'])).replace('{{N_GLEE}}', str(len(rows['glee'])))
      .replace('{{N_COMB}}', str(len(rows['combined']))).replace('{{N_CHORUS}}', str(len(rows['chorus']))).replace('{{N_LOC}}', str(nloc)))
open(os.path.join(S, 'mens_glee_report.html'), 'w', encoding='utf-8').write(t)
print({k: len(v) for k, v in rows.items()}, nloc)
for k in rows: print(rows[k][0][:400])
