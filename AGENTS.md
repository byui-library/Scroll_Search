# Instructions for AI assistants

This repository is a full-text index of the Ricks College student newspapers scanned in
`W:\DCAM\Scroll\Scroll Rescan Project`: Student Rays (1905–1933), Scroll (bound 1927–1929),
The Purple Flash (1933–1937), Viking Flashes (1937–1938) and Viking Scroll (1938–1988),
13,787 pages. Users are library and archives staff researching topics in these papers.

## Setup

If `scroll_text.db` does not exist, build it first (Python 3 standard library only, about a minute):

```
python build_index.py
```

If `python` is not found on Windows, use `py`.

## Searching

Use `search_scroll.py`; do not scan the W: drive or re-run OCR to answer a search.

```
python search_scroll.py "exact phrase"
python search_scroll.py "word1 OR word2" --years 1930-1949 --paper "Viking Scroll"
python search_scroll.py "word1 AND word2"
python search_scroll.py "prefix*"
python search_scroll.py "NEAR(glee concert, 15)"
python search_scroll.py "phrase" --csv results.csv --limit 0
```

- Paper names for `--paper`: `Student Rays`, `Scroll (bound 1927-1929)`, `The Purple Flash`, `Viking Flashes`, `Viking Scroll`.
- Matching ignores case and regular word endings (sing/sings/singing), but not irregular forms (sang, sung).
- For anything beyond these options, query the SQLite database directly. Table `pages` is an FTS5 table
  with columns `text` (searchable), `paper`, `issue`, `year`, `page`, `method`, `path`.
  Use `snippet(pages, 0, '[', ']', ' ... ', 40)` for excerpts and `ORDER BY year`.

## Doing a good search

- The text is OCR of old newsprint and has errors. Search several forms of a term
  (for example "male glee", "men's glee", "boys' glee", "glee club") and common OCR damage
  (dropped apostrophes, split words such as "con- cert"), and say which terms you used.
- A keyword hit is not the same as a relevant article. Read the excerpts (or the full page `text`)
  and judge whether each page is really about the topic before reporting it.
- The same article can appear at more than one path because some issues were scanned twice
  (Viking Scroll Box 1 overlaps Boxes 2 and 3; the bound 1927–29 volume overlaps Student Rays Box 11).
  Group results by issue date and note the duplicate paths.
- Report every result with: date or issue, newspaper, page, and the full file path from `path`,
  so the user can open the scan. Quote the newspaper's words only from the text, and remind the user
  to check the original scan before citing, since the OCR may be wrong.
- Do not invent dates, names or details that are not in the text.

## Deliverables

Put finished reports for others in `reports/`. Existing examples: the musical-performance
article list (Excel) and the Men's Glee report and SharePoint wiki version (HTML).

## Changing the data

`data/*.jsonl.gz` is the master copy of the text; `scroll_text.db` is generated and not committed.
To add newly scanned pages, see README.md ("Adding new scans"): produce `.txt` page files with the
scripts in `ocr_tools/`, then run `python build_index.py <folder> --export` and commit `data/`.
Do not edit or delete files on the W: drive.
