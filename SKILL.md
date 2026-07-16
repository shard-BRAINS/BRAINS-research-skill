---
name: brains-research
description: Use when Matthew says "process research", "catalogue these papers", "new PDFs", or drops files into the BRAINS research inbox. Maintains the BRAINS research library — extracts, dedupes, categorises, renames, and files PDFs into a locked 10-category taxonomy, appending each entry to _catalog.csv. Read-only status command also available. A BRAINS Incubator project.
version: 1.2.0
license: MIT
---

# BRAINS Research Skill

This skill maintains the BRAINS research library — a curated, categorised corpus of PDFs covering AI, neurodiversity, ethics, mental health, and related domains. The skill runs the inbox-to-library pipeline (extract → dedupe → categorise → rename → file → append catalog) against a locked 10-category taxonomy, producing an append-only `_catalog.csv` that is the canonical record of what has been read and where it lives.

This is a BRAINS Incubator project, v1.0.0.

---

## How this skill operates

This section describes the behavioural contract — how Claude should behave across all turns within a session after the skill is invoked.

**Locked taxonomy.** Never silently add a category. The 10 categories live in `references/taxonomy.md` and are canonical. If a paper genuinely does not fit one of the ten, surface it and ask the user before proceeding.

**Locked dedupe rule.** Byte-exact match against any PDF already filed under the 10 canonical category folders is the only dedupe signal. No fuzzy matching, no near-duplicate inference. False negatives are acceptable; false positives are not.

**Append-only catalog.** `_catalog.csv` is never rewritten. Corrections to past entries are out of scope for this skill and must be done manually.

**No silent renames.** A file already filed under a category folder is not renamed by this skill. If the user wants to rename, that is a separate explicit task.

**Plain, direct tone.** Status reports and error messages are plain and direct. Use identity-first language by default (`autistic researcher`, `neurodivergent participant`). No deficit framing of neurodivergence in any reference, command, or output.

**Air-gap awareness.** The library backs the BRAINS Certified evidence base. This skill never reveals, summarises, or speculates on BRAINS scoring criteria, calibration vignettes, or rubric mechanics from within the papers it catalogues. That concern is handled by the `brains-weekly-intel` skill.

**Confirm before destructive moves.** The pipeline reports its plan before applying it. If the user says "dry run" or "preview", run with `--dry-run` and report what would have moved.

**Reviews are append-history.** A paper can be re-reviewed; the `.review.md` is overwritten with the latest analysis but a new row is appended to `_reviews.csv` so the history is preserved.

**No publishing.** LinkedIn and Bluesky outputs from `/brains-research-review` are drafts handed off to `brains-content`. The skill never posts.

**Brand fallback.** If `brains-brand` is not installed, `/brains-research-review` writes a generic neuro-affirming commentary and notes the fallback in the review file. The skill still works for non-BRAINS users.

---

## Available commands

| Command | Purpose |
|---|---|
| `/brains-research-process` | The full ingest workflow. Extract → dedupe → categorise → rename → file → append catalog. |
| `/brains-research-status` | Read-only summary: counts by category, recent additions, integrity check. |
| `/brains-research-review` | Per-paper review: objective summary, analytical review, BRAINS commentary, optional LinkedIn + Bluesky drafts handed off to `brains-content`. Persists to `Reviews/<Category>/<stem>.review.md` and `_reviews.csv`. |

---

## Configuration

The skill reads `config.json` from the skill root. Paths are per-machine — `config.json` is gitignored. To override the location of `config.json`, set the `BRAINS_RESEARCH_CONFIG` environment variable.

Schema (see `config.json.example`):

```json
{
  "research_root": "C:\\Users\\matth\\Proton Drive\\Matthew Gell\\Shared with me\\05. Supporting Research",
  "inbox_dir": "NEW RESEARCH - TO BE REVIEWED",
  "completed_dir": ".",
  "archive_dir": "NEW RESEARCH - TO BE REVIEWED/COMPLETED",
  "duplicates_dir": "_duplicates",
  "catalog_csv": "_catalog.csv",
  "extract_pages": 2,
  "extract_max_chars": 3000,
  "content_drafts_dir": "C:\\Users\\matth\\Proton Drive\\Matthew Gell\\Shared with me\\06. Operations\\Admin\\03_Content"
}
```

Key notes on the schema:

- `completed_dir` is the folder that contains the 10 category subfolders. Set it to `"."` (or `""`) when the category folders live directly at the research root. Set it to `"Completed Review"` (or another name) for legacy layouts where categories were wrapped in a parent folder.
- `archive_dir` is optional. When present, `apply_renames.py` copies the original file (under its original filename) into that folder before renaming and filing the working copy into the category. Provides an audit-trail receipt of what was ingested and when.
- `content_drafts_dir` is optional. When present, `/brains-research-review` writes LinkedIn / Bluesky drafts as `CT00X.md` files there and appends to `content_calendar.csv`.

---

## References

When deciding category, filename, organisation abbreviation, or edge-case treatment, load the relevant reference file rather than reconstructing the rule from memory:

- `references/taxonomy.md`
- `references/filename-rules.md`
- `references/org-abbreviations.md`
- `references/edge-cases.md`
- `references/review-template.md` (loaded during `/brains-research-review`)
- `references/linkedin-template.md` (loaded during `/brains-research-review` if a LinkedIn draft is requested)
- `references/bluesky-template.md` (loaded during `/brains-research-review` if a Bluesky draft is requested)

The reference files are the canonical source for this skill's rules. Do not paraphrase them.

---

## Scope

In scope: cataloguing the inbox into the locked taxonomy; producing the catalog row; producing a status report.

Out of scope (for now — separate skills will handle these): per-paper review or summarisation, cross-paper synthesis, search across the corpus, mirroring the corpus to the BRAINS website, suggesting LinkedIn or Bluesky posts from new additions, OCR of scanned PDFs, live fetching of papers from journal portals.
