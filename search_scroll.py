"""Search the Ricks College newspaper text index (scroll_text.db).

Examples
  python search_scroll.py "glee club"                 exact phrase
  python search_scroll.py "band OR orchestra"         either word
  python search_scroll.py "messiah AND tabernacle"    both words on the same page
  python search_scroll.py "basketbal*"                word starting with...
  python search_scroll.py "glee club" --years 1930-1949 --paper "Viking Scroll"
  python search_scroll.py "glee club" --csv results.csv

Word endings are matched loosely (sing / sings / singing all match), but irregular forms (sang, sung) do not.
Matching ignores capitals and punctuation.
Results are one row per scanned page, sorted by year.
"""
import argparse, csv, os, re, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'scroll_text.db')

def to_fts(q):
    # A query with no operators or quotes is treated as an exact phrase.
    if any(tok in q for tok in ('"', ' OR ', ' AND ', ' NOT ', '*', 'NEAR(')):
        return q
    return '"' + q.replace('"', '') + '"'

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('query')
    ap.add_argument('--years', help='e.g. 1930-1949')
    ap.add_argument('--paper', help='Student Rays, The Purple Flash, Viking Flashes, Viking Scroll, Scroll (bound 1927-1929)')
    ap.add_argument('--csv', help='write all results to this CSV file')
    ap.add_argument('--limit', type=int, default=50, help='rows to print on screen (default 50)')
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    sql = ("SELECT year, paper, issue, page, method, path, snippet(pages, 0, '[', ']', ' ... ', 40) "
           "FROM pages WHERE pages MATCH ?")
    args = [to_fts(a.query)]
    if a.paper:
        sql += ' AND paper = ?'; args.append(a.paper)
    if a.years:
        lo, _, hi = a.years.partition('-')
        sql += ' AND year >= ? AND year <= ?'; args += [lo, hi or lo]
    sql += ' ORDER BY year, path, CAST(page AS INTEGER)'
    rows = con.execute(sql, args).fetchall()

    print(f'{len(rows)} pages match {a.query!r}\n')
    for r in rows[:a.limit]:
        year, paper, issue, page, method, path, snip = r
        print(f'{year}  {paper}  |  {issue}  |  page {page}')
        print(f'    {path}')
        print(f'    {snip}\n')
    if len(rows) > a.limit:
        print(f'... {len(rows) - a.limit} more. Use --csv to save them all.')
    if a.csv:
        with open(a.csv, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['Year', 'Newspaper', 'Issue folder', 'Page', 'Text source', 'Full file path', 'Excerpt'])
            w.writerows(rows)
        print('saved', len(rows), 'rows to', a.csv)

if __name__ == '__main__':
    main()
