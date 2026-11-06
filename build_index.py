"""Build scroll_text.db (SQLite full-text index) from the page text.

  python build_index.py                  rebuild from data/*.jsonl.gz (the normal case)
  python build_index.py <txt folder> ... also add folders of new page .txt files

A .txt page file starts with a line "SOURCE: <full path>[ | page N]" followed by the page text
(this is what the scripts in ocr_tools produce). After adding new pages, run
`python build_index.py --export` to write them back into data/ so they are kept in the repository.
"""
import glob, gzip, json, os, re, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'scroll_text.db')
DATA = os.path.join(HERE, 'data')
ROOT_MARK = 'Scroll Rescan Project\\'
COLS = ['paper', 'issue', 'year', 'page', 'method', 'path', 'text']

def describe(src):
    page = ''
    m = re.match(r'(.*) \| page (\d+)$', src)
    if m:
        src, page = m.group(1).strip(), m.group(2)
    else:
        m2 = re.search(r'_0*(\d+)\.tiff?$', src, re.I) or re.search(r'Scl\d{8}(\d\d)\w*\.tif$', src) or re.search(r'FN-0*(\d+)\.tif$', src)
        page = m2.group(1) if m2 else ''
    rel = src.split(ROOT_MARK)[-1]
    parts = rel.split('\\')
    paper = parts[0]
    if 'Scroll_1927-1929' in rel:
        paper = 'Scroll (bound 1927-1929)'
    elif paper.startswith('Scroll_StudentRays'):
        paper = 'Student Rays'
    issue = next((p for p in parts[1:-1] if re.search(r'(18|19)\d\d', p) and not p.startswith('Box')), '')
    yr = re.search(r'(19\d\d)', issue) or re.search(r'(19\d\d)', rel)
    return dict(paper=paper, issue=issue, year=yr.group(1) if yr else '', page=page, path=src)

def from_data():
    for fp in sorted(glob.glob(os.path.join(DATA, '*.jsonl.gz'))):
        with gzip.open(fp, 'rt', encoding='utf-8') as f:
            for line in f:
                yield json.loads(line)

def from_txt(folder):
    method = {'ocr': 'OCR of TIFF', 'pdftext': 'PDF text layer', 'pdfocr': 'OCR of PDF page image'}.get(
        os.path.basename(folder.rstrip('/\\')), 'OCR')
    for fp in glob.glob(os.path.join(folder, '*.txt')):
        raw = open(fp, encoding='utf-8', errors='replace').read()
        first, _, body = raw.partition('\n')
        if not first.startswith('SOURCE:') or len(body.strip()) < 20:
            continue
        rec = describe(first[7:].strip())
        rec.update(method=method, text=re.sub(r'\s+', ' ', body))
        yield rec

def group_key(r):
    if r['paper'] == 'Viking Scroll':
        y = int(r['year'] or 0)
        return 'viking-scroll-' + ('1938-1955' if y < 1956 else '1956-1969' if y < 1970 else '1970-1979' if y < 1980 else '1980-1988')
    return re.sub(r'[^a-z0-9]+', '-', r['paper'].lower()).strip('-')

def export(con):
    rows = con.execute('SELECT %s FROM pages ORDER BY paper, year, path, CAST(page AS INTEGER)' % ', '.join(COLS)).fetchall()
    groups = {}
    for r in rows:
        rec = dict(zip(COLS, r))
        groups.setdefault(group_key(rec), []).append(rec)
    os.makedirs(DATA, exist_ok=True)
    for k, recs in groups.items():
        with gzip.open(os.path.join(DATA, k + '.jsonl.gz'), 'wt', encoding='utf-8') as f:
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('exported', len(rows), 'pages to', DATA)

def main(argv):
    do_export = '--export' in argv
    folders = [a for a in argv if a != '--export']
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.execute("""CREATE VIRTUAL TABLE pages USING fts5(
        text, paper UNINDEXED, issue UNINDEXED, year UNINDEXED, page UNINDEXED,
        method UNINDEXED, path UNINDEXED, tokenize='porter unicode61')""")
    seen, n = set(), 0
    sources = [from_data()] + [from_txt(f) for f in folders]
    for src in sources:
        for r in src:
            key = (r['path'], r['page'], r['method'])
            if key in seen:
                continue
            seen.add(key)
            con.execute('INSERT INTO pages(text, paper, issue, year, page, method, path) VALUES (?,?,?,?,?,?,?)',
                        (r['text'], r['paper'], r['issue'], r['year'], r['page'], r['method'], r['path']))
            n += 1
    con.commit()
    con.execute("INSERT INTO pages(pages) VALUES('optimize')")
    con.commit()
    print('indexed', n, 'pages into', DB)
    if do_export:
        export(con)

if __name__ == '__main__':
    main(sys.argv[1:])
