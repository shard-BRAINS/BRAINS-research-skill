# Changelog

All notable changes to BRAINS Research Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] — 2026-07-15

### Changed
- **Research root relocated** from the local SMB share (`\\192.168.1.101\Singularity_Backup\Research`) to the BRAINS Proton Drive share at `Shared with me\05. Supporting Research`. `config.json` and `config.json.example` updated.
- **Category folders now live at the research root**, not under a `Completed Review/` wrapper. `config.json` uses `"completed_dir": "."` to reflect this. The wrapped-layout form (`"completed_dir": "Completed Review"`) still works for legacy installs.
- **Inbox renamed** from `"to be reviwed"` to `"NEW RESEARCH - TO BE REVIEWED"`.
- `scripts/apply_renames.py` now writes the catalog's `new_path` column without any `Completed Review/` prefix — the value is `"<Category>/<new_name>"` in the new layout.
- `scripts/status.py` orphan scan is now category-scoped (iterates the 10 canonical category folders) so it stays correct when `completed_dir` is the research root itself. Inbox count is top-level PDFs only — the archive subfolder is excluded.
- `commands/brains-research-process.md` — dedupe glob is now per-category; archive step documented.
- `references/edge-cases.md` — path language updated; new section on the archive folder.

### Added
- **`archive_dir` config key (optional).** When set, `apply_renames.py` copies each processed original (under its original filename) to that folder before renaming and filing the working copy into `<Category>/`. Provides an audit-trail receipt of what was ingested and when. Default: `NEW RESEARCH - TO BE REVIEWED/COMPLETED`.
- `Config.archive_dir: Path | None` on the dataclass.
- `status.status_report()` returns `archive_count`.
- Test coverage for archive behaviour, top-level-only inbox counting, and legacy `completed_dir` compatibility.

### Migration notes
- Existing `_catalog.csv` had 102 rows carrying the legacy `Completed Review/<Category>/...` prefix in `new_path`. As part of the reorg, these are rewritten in place (one-time migration) to `<Category>/...` so the integrity check does not permanently report 102 missing files. A backup copy of the pre-migration catalog is written to `_catalog.csv.pre-1.2.0.bak` on the share.
- Users on the legacy `\\192.168.1.101\Singularity_Backup\Research` share can keep their existing `config.json` unchanged — no code paths were broken; only the defaults and the doc examples changed. To adopt the categories-at-root layout, set `"completed_dir": "."`.

## [1.1.0] — 2026-05-29

### Added
- `/brains-research-review` slash command — per-paper review workflow producing an objective summary, an analytical review, BRAINS commentary, and optional LinkedIn and Bluesky drafts handed off to `brains-content`.
- `scripts/extract_full.py` — full-text PDF extraction with per-paper JSON cache, mtime-invalidated.
- `scripts/review.py` — paper selection (filename / partial / category / picker), `_reviews.csv` append-only ledger I/O, `.review.md` writer, content-draft handoff.
- `references/review-template.md`, `references/linkedin-template.md`, `references/bluesky-template.md` — section guides loaded on demand during the review flow.
- Optional `content_drafts_dir` config key (defaults to Matthew's BRAINS content folder). The review command writes `CT00X.md` drafts and appends to `content_calendar.csv`. If the directory is unreachable, the review still completes; only the draft handoff is skipped.
- `_reviews.csv` ledger on the share, 13 columns: `new_path, category, paper_year, paper_author, paper_title, review_path, review_date, focus_criteria, linkedin_draft_id, bluesky_draft_id, bias_flags, tags, next_action`. Append-only.
- Stub `.review.md` + `bias_flags=scanned_pdf` row for scanned image-only PDFs — leaves an audit trail.
- Test fixtures and test files (`tests/test_extract_full.py`, `tests/test_review.py`, two new `test_config.py` cases). New `reportlab` dev dependency for generating the multi-page fixture PDF. 43/43 tests passing.

### Changed
- `scripts/config.py` — `Config` dataclass gains optional `content_drafts_dir: Path | None`.

### Migration notes
- v1.0.0 users upgrade by `git pull` and re-running `install.ps1` (or platform equivalent).
- Existing `_catalog.csv` and v1.0.0 commands are untouched.

## [1.0.0] — 2026-05-29

### Added
- `scripts/config.py` — per-machine `config.json` loader with path validation.
- `scripts/extract_text.py` — single-file PDF text extractor.
- `scripts/extract_all.py` — batch extraction to `_extract_all.json`.
- `scripts/apply_renames.py` — applies `_rename_plan.json`, moves files, appends `_catalog.csv` (with `--dry-run`).
- `scripts/status.py` — read-only catalog summary and integrity check.
- `references/taxonomy.md`, `references/filename-rules.md`, `references/org-abbreviations.md`, `references/edge-cases.md` — canonical rule sets.
- `/brains-research-process` and `/brains-research-status` slash commands.
- `SKILL.md` behavioural contract.
- One-line installers for Windows (cmd + PowerShell) and macOS / Linux (bash).
- Test suite (`pytest`) covering config, extraction, rename application, and status reporting (21/21 passing, including UTF-8 BOM tolerance for PowerShell-written config.json).

### Migration notes
- The previous `/process-research` slash command (hardcoded to a OneDrive path) has been deprecated. Use `/brains-research-process` from the installed `brains-research` skill instead.
- The three Python scripts on the share at `\\192.168.1.101\Singularity_Backup\Research` (`_extract_all.py`, `_extract_text.py`, `_apply_renames.py`) had their `ROOT` constants patched in place to point at the UNC path. Pre-migration backups stored under `_backup/`.

### End-to-end verification
- Installer runs cleanly on Windows 11 + PowerShell 5.1.
- `/brains-research-process` against the live inbox of 3 PDFs catalogued them into Neurodiversity-General, AI-Neurodiversity-Autism, and AI-Mental-Health respectively. `_catalog.csv` grew from 102 to 105 rows.
- `/brains-research-status` reports 105 catalogued, 0 inbox, 0 missing files, 0 orphans.
