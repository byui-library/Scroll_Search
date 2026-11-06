import html, os, sys
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from entries import E
from build import loc, paper  # reuses location helpers (build.py also rewrites the report file harmlessly)

TABLE = 'border-collapse:collapse;width:100%;'
TH = 'border:1px solid #c8c8c8;padding:6px 8px;background-color:#f0f0f0;text-align:left;vertical-align:top;'
TD = 'border:1px solid #c8c8c8;padding:6px 8px;vertical-align:top;'

def table(grp):
    rows = []
    for label, key, ids, g, summ in sorted(E, key=lambda e: e[1]):
        if g != grp:
            continue
        rel, pg = loc(ids[0])
        cell = '%s (%s)' % (html.escape(rel), html.escape(pg))
        for j in ids[1:]:
            r2, p2 = loc(j)
            cell += '<br>Also: %s (%s)' % (html.escape(r2), html.escape(p2))
        rows.append('<tr><td style="%swhite-space:nowrap;">%s</td><td style="%s">%s</td><td style="%s">%s</td><td style="%sfont-size:85%%;">%s</td></tr>'
                    % (TD, html.escape(label), TD, html.escape(paper(rel)), TD, html.escape(summ), TD, cell))
    head = ''.join('<th style="%s">%s</th>' % (TH, h) for h in ('Date', 'Newspaper', 'Article', 'Location'))
    return '<table style="%s"><thead><tr>%s</tr></thead><tbody>\n%s\n</tbody></table>' % (TABLE, head, '\n'.join(rows))

t = open(os.path.join(S, 'wiki_template.html'), encoding='utf-8').read()
t = t.replace('{{TABLE_GLEE}}', table('glee')).replace('{{TABLE_COMB}}', table('combined')).replace('{{TABLE_CHORUS}}', table('chorus'))
open(os.path.join(sys.argv[1]), 'w', encoding='utf-8').write(t)
print('wrote', sys.argv[1], len(t))
