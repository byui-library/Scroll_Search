# Scroll newspaper text search

A full-text index of the Ricks College student newspapers in
`W:\DCAM\Scroll\Scroll Rescan Project` (Student Rays, Scroll 1927–1929, The Purple Flash,
Viking Flashes, Viking Scroll 1938–1988). It lets you search every scanned page for a word or
phrase and get back the newspaper, issue, page and full file path of each match.

Built November 2026. 13,787 pages with text.

## What's in this repository

| Path | What it is |
|---|---|
| `data\*.jsonl.gz` | The text of every page, with newspaper, issue, year, page and scan path. This is the master copy (about 29 MB, one file per newspaper or decade). |
| `build_index.py` | Builds the searchable database `scroll_text.db` from `data\`. |
| `search_scroll.py` | Command-line search tool. |
| `scroll_text.db` | The searchable database (about 120 MB). Not stored in git; rebuild it with `python build_index.py`. |
| `ocr_tools\ocr.ps1` | Windows OCR script used to read the TIFF scans (Windows PowerShell 5.1, built-in Windows OCR). |
| `ocr_tools\pdfx3.py` | Pulls the text layer out of the issue PDFs and renders image-only pages for OCR (needs `pip install pymupdf`). |
| `reports\` | Finished deliverables: the musical-performance article list (Excel), the Men's Glee report (HTML) and its SharePoint wiki version. |
| `tools\` | The scripts and review notes used to make those reports, kept for reference. They read intermediate files that are not in the repository, so they won't run as-is. |

## First-time setup

The database isn't stored in git because of its size. After cloning or copying the repository, run once:

```
python build_index.py
```

This takes about a minute and needs only Python 3 (no extra packages).

## Searching

Open a terminal in this folder and run, for example:

```
python search_scroll.py "glee club"
python search_scroll.py "band OR orchestra" --years 1930-1949
python search_scroll.py "messiah AND tabernacle"
python search_scroll.py "basketbal*" --paper "Viking Scroll"
python search_scroll.py "men's chorus" --csv mens_chorus.csv
```

- Plain words are searched as an exact phrase.
- `OR`, `AND`, `NOT` (capitals) combine terms; `*` matches word beginnings; `NEAR(word1 word2, 10)` finds words within 10 words of each other.
- `--csv file.csv` saves every match to a spreadsheet you can open in Excel.

## Searching with an AI assistant

AI coding assistants that run on your computer can run these searches for you and read the results:
Claude Code (desktop app, VS Code extension or command line), OpenAI Codex (app, VS Code extension
or command line), GitHub Copilot in agent mode, and similar tools. Browser chat tools such as the
regular ChatGPT or Claude.ai websites can't, because they can't run programs on your computer.

1. Set up the repository as above.
2. Open the `Scroll_Search` folder in the AI tool (or start the tool from a terminal in that folder).
3. Ask in plain language, for example: "Find articles about the 1950s Homecoming parades and list the
   issue, page and file path for each."

The tool reads `AGENTS.md` (Codex and most others) or `CLAUDE.md` (Claude Code) in this folder,
which tells it how to use the index, which spelling variants to try, and how to report results.
Check the AI's summaries against the original scans before citing them; it can misread OCR text.

Searches send the excerpts it reads to the AI company's servers, so use a tool your
institution has approved for this kind of material.

## How the text was made, and its limits

- Issues with a PDF that has a text layer: that text was used.
- Issues with image-only PDFs: each page was rendered and read with Windows OCR.
- Issues with only TIFF scans (mostly 1938–1957 Viking Scroll, The Purple Flash, 1986 and 1988): the TIFFs were read with Windows OCR.

The text is machine-read from old newsprint. Some words are misread, so a search can miss an
article; try spelling variants or a shorter phrase, and always check the original scan before quoting.
Some issues were scanned more than once, so the same article can appear at two paths.

## Adding new scans

1. Extract text for the new files into a folder of `.txt` files, each starting with a line
   `SOURCE: <full path to the scan>` (add ` | page N` for PDF pages). The scripts in `ocr_tools` do this.
2. Rebuild the index with the existing data plus the new folder, and write the result back into `data\`:
   `python build_index.py <new text folder> --export`
3. Commit the changed files in `data\`.

## Sharing with colleagues

Push the repository to a shared git host, or copy the folder to a shared drive. Anyone with
Python 3 can run `python build_index.py` and then `search_scroll.py`; the database also opens
in any SQLite browser.
