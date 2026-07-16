---
description: Catalogue new PDFs in the BRAINS research inbox — extract, dedupe, categorise, rename, file into <Category>/, archive original, append _catalog.csv
---

# /brains-research-process

Process whatever PDFs are currently sitting in the inbox.

**Paths come from `config.json` at the skill root.** Use `python -m scripts.config` to inspect resolved paths if needed. In the current layout the 10 category folders live directly at the research root; the inbox is `NEW RESEARCH - TO BE REVIEWED/`; processed originals are archived under `NEW RESEARCH - TO BE REVIEWED/COMPLETED/`.

**Locked references — load these before deciding any category, filename, or edge-case treatment:**

- `references/taxonomy.md` — the 10 locked categories
- `references/filename-rules.md` — canonical filename format
- `references/org-abbreviations.md` — institutional author abbreviations
- `references/edge-cases.md` — scanned PDFs, collisions, non-PDFs, duplicates

## Steps

1. **Empty check.** Glob the top level of the inbox for `*.pdf` (do NOT recurse — the `COMPLETED/` subfolder holds already-processed originals and must be ignored). If no PDFs, report `No new files.` and stop.

2. **Extract.** Run `python -m scripts.extract_all` from the skill root (or anywhere — the script resolves paths via config). This writes `_extract_all.json` to the Research root with `{filename: {size, text, pages, error}}` for every PDF at the top level of the inbox.

3. **Dedupe against existing catalog.** For each new file, compare its byte size against every file already filed in any of the 10 category folders under `<research_root>`. If an exact byte match exists, move the new file to `_duplicates/` and skip it (do not include in the rename plan). Use, for each category:
   ```powershell
   Get-ChildItem -Recurse '<research_root>\<Category>' -Filter *.pdf | Where-Object Length -eq <N>
   ```
   or the equivalent `find` on macOS / Linux. The 10 category names are listed in `references/taxonomy.md`.

4. **Read and categorise.** Read `_extract_all.json`. If it is larger than 25 KB, split into chunks of approximately 18 entries and read sequentially. For each non-duplicate file, extract from the text:
   - `year` (four-digit, or `nd` if not findable)
   - `author` (first author surname, or organisation abbreviation from `references/org-abbreviations.md`)
   - `title` (5–15 words, descriptive)
   - `category` (must be one of the 10 in `references/taxonomy.md` — never invent new categories silently)
   - `doc_type` (e.g. `Journal article`, `Preprint`, `Conference paper`, `Institutional report`, `Legislation`, `White paper`, `Master thesis`, `PhD thesis`)

5. **Build filenames.** Apply `references/filename-rules.md`. Canonical form: `YYYY - ShortAuthor - Descriptive title.pdf`.

6. **Write `_rename_plan.json`** at the Research root, overwriting any prior plan. Schema:
   ```json
   {
     "<original_filename>": {
       "category": "<one of the 10>",
       "new_name": "YYYY - ShortAuthor - Descriptive title.pdf",
       "year": "YYYY",
       "author": "ShortAuthor",
       "title": "Descriptive title",
       "doc_type": "Journal article"
     }
   }
   ```

7. **Apply.** Run `python -m scripts.apply_renames` (no flags). For each entry it:
   - copies the original (under its original filename) to `<archive_dir>/` as a receipt,
   - moves + renames the file into `<research_root>/<Category>/<new_name>`,
   - appends a row to `_catalog.csv` with `new_path` = `<Category>/<new_name>` (no `Completed Review/` prefix).

8. **Report back.** Concise summary:
   - N moved by category
   - N originals archived to `<archive_dir>/`
   - N quarantined as duplicates (with names)
   - Any files where extraction failed or year / author was uncertain (flag these for the user to review)
   - Any new organisation abbreviations added to `references/org-abbreviations.md` during this run

## Dry-run

If the user says "dry run" or "preview", run `python -m scripts.apply_renames --dry-run` instead of step 7. Report what would have moved. No archive copies are made in dry-run mode.
