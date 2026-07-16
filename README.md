<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/shard-BRAINS/.github/main/profile/brand-mark-dark-bg.png">
  <img alt="BRAINS" src="https://raw.githubusercontent.com/shard-BRAINS/.github/main/profile/brand-mark-light-bg.png" width="220">
</picture>

# BRAINS Research Skill

### A Claude Code skill for curating the BRAINS research library — extract, dedupe, categorise, file, review.

<br />

[![Version](https://img.shields.io/badge/version-v1.2.0-D99518?style=for-the-badge&labelColor=0A0A0A)](CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-stable-D99518?style=for-the-badge&labelColor=0A0A0A)](STATUS.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-D99518?style=for-the-badge&logo=python&logoColor=FFFFFF&labelColor=0A0A0A)](#install)
[![Licence](https://img.shields.io/badge/licence-MIT-0A0A0A?style=for-the-badge&labelColor=D99518)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=for-the-badge&logo=discord&logoColor=FFFFFF&labelColor=0A0A0A)](https://discord.gg/BEmTXXscBr)
[![Incubator](https://img.shields.io/badge/BRAINS-Incubator-4DA8FF?style=for-the-badge&labelColor=0A0A0A)](https://github.com/shard-BRAINS)

<br />

[Install ↓](#install) · [Pipeline ↓](#pipeline) · [Commands ↓](#commands) · [Configuration ↓](#configuration) · [Taxonomy ↓](#the-locked-taxonomy)

</div>

---

A Claude Code skill that maintains the BRAINS research library — a curated, categorised corpus of PDFs covering AI, neurodiversity, ethics, mental health, and related domains. Runs the inbox-to-library pipeline (extract → dedupe → categorise → rename → file → append catalog) against a locked 10-category taxonomy, plus a per-paper review workflow that produces objective summaries, analytical reviews, BRAINS commentary, and optional LinkedIn / Bluesky draft posts.

> **Reliable, affirming, inclusive.**

**An Incubator project from [BRAINS](https://github.com/shard-BRAINS) — built by neurodivergent minds, for neurodivergent people.**

---

## Pipeline

```mermaid
flowchart LR
    INBOX["<b>Inbox</b><br/><span style='font-size:11px'>new PDFs<br/>'NEW RESEARCH - TO BE REVIEWED' folder</span>"]:::inbox
    EXTRACT["<b>Extract</b><br/><span style='font-size:11px'>first 2 pages<br/>≤3000 chars</span>"]:::process
    DEDUPE["<b>Dedupe</b><br/><span style='font-size:11px'>against _catalog.csv</span>"]:::process
    CATEGORISE["<b>Categorise</b><br/><span style='font-size:11px'>locked 10-category<br/>taxonomy</span>"]:::process
    RENAME["<b>Rename</b><br/><span style='font-size:11px'>canonical filename</span>"]:::process
    FILE["<b>File</b><br/><span style='font-size:11px'>&lt;Category&gt;/ at root</span>"]:::output
    CATALOG["<b>Catalog</b><br/><span style='font-size:11px'>append row to<br/>_catalog.csv</span>"]:::output
    ARCHIVE["<b>Archive</b><br/><span style='font-size:11px'>original filename<br/>copied to COMPLETED/</span>"]:::output
    DUPES["<b>_duplicates/</b><br/><span style='font-size:11px'>quarantined</span>"]:::dupe
    REVIEW["<b>Review</b><br/><span style='font-size:11px'>summary + analysis<br/>+ BRAINS commentary</span>"]:::process
    REVIEWFILE["<b>Reviews/</b><br/><span style='font-size:11px'>.review.md<br/>+ _reviews.csv</span>"]:::output
    DRAFTS["<b>Drafts</b><br/><span style='font-size:11px'>LinkedIn + Bluesky<br/>handoff to brains-content</span>"]:::output

    INBOX --> EXTRACT --> DEDUPE
    DEDUPE -->|duplicate| DUPES
    DEDUPE -->|new| CATEGORISE --> RENAME --> FILE --> CATALOG
    RENAME -.->|copy original| ARCHIVE
    CATALOG -.->|on demand| REVIEW --> REVIEWFILE
    REVIEW -.->|optional| DRAFTS

    classDef inbox fill:#FFFFFF,stroke:#7A7A7A,stroke-width:2px,color:#0A0A0A
    classDef process fill:#D99518,stroke:#0A0A0A,stroke-width:2px,color:#0A0A0A
    classDef output fill:#2A8B91,stroke:#0A0A0A,stroke-width:2px,color:#FFFFFF
    classDef dupe fill:#F5F5F5,stroke:#7A7A7A,stroke-width:1px,stroke-dasharray:5 5,color:#1A1A1A
```

Idempotent at every step: re-running over the same inbox is safe. The catalog and reviews ledger are both append-only; the taxonomy is locked.

---

## Commands

| Command | What it does | Status |
|---|---|---|
| `/brains-research-process` | Full ingest workflow: extract → dedupe → categorise → rename → file → append catalog | ![live](https://img.shields.io/badge/-live-D99518?style=flat-square&labelColor=0A0A0A) |
| `/brains-research-status` | Read-only summary: total catalogued, count by category, recent additions, inbox + duplicate counts, integrity check | ![live](https://img.shields.io/badge/-live-D99518?style=flat-square&labelColor=0A0A0A) |
| `/brains-research-review` | Per-paper review: objective summary, analytical review, BRAINS commentary, optional LinkedIn + Bluesky drafts handed off to `brains-content`. Persists to `Reviews/<Category>/<stem>.review.md` and `_reviews.csv` | ![live](https://img.shields.io/badge/-live-D99518?style=flat-square&labelColor=0A0A0A) |

The integrity check surfaces both directions of drift: catalog rows pointing at files that no longer exist, and PDFs on disk that the catalog doesn't know about. `/brains-research-review` accepts a paper filename or partial title as an argument, or presents a picker of the 10 most recent catalogued additions.

---

## Install

### One-line installers (recommended)

**Windows** (Command Prompt or PowerShell):

```
.\install\install.cmd
```

The wrapper handles PowerShell's default execution policy automatically — no system setting changed. To invoke PowerShell directly:

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1
```

**macOS / Linux:**

```bash
bash install/install.sh
```

### Manual install

```bash
# 1. Clone
git clone https://github.com/shard-BRAINS/BRAINS-research-skill.git
cd BRAINS-research-skill

# 2. Create + activate a virtual environment
python -m venv .venv
#    Windows:
.venv\Scripts\activate
#    macOS / Linux:
source .venv/bin/activate

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Copy config and set research_root (and optionally content_drafts_dir)
cp config.json.example config.json
```

**Install the skill bundle for Claude Code:**

```bash
# Copy (most users)
cp -r . ~/.claude/skills/brains-research/

# Symlink (edits take effect immediately)
ln -s "$(pwd)" ~/.claude/skills/brains-research

# Copy the slash commands into ~/.claude/commands/
cp commands/brains-research-*.md ~/.claude/commands/
```

---

## Configuration

Edit `config.json` to point `research_root` at your Research folder. The default targets the BRAINS Proton Drive share at `Shared with me\05. Supporting Research`. All other paths are resolved relative to `research_root`.

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

Key fields:

- `completed_dir` — the folder that contains the 10 category subfolders. Use `"."` when categories live at the research root (the current layout). Use a folder name (e.g. `"Completed Review"`) for legacy wrapped layouts.
- `archive_dir` — optional; when set, `apply_renames.py` copies each processed original (under its original filename) here as an audit-trail receipt before renaming and filing the working copy.
- `content_drafts_dir` — optional; when set, `/brains-research-review` writes LinkedIn / Bluesky drafts as `CT00X.md` files there and appends to `content_calendar.csv`.

---

## The locked taxonomy

Eleven categories. See [`references/taxonomy.md`](references/taxonomy.md) for the full definitions. **The taxonomy is doctrine, not configuration** — the skill will refuse to silently invent a new category. If a paper doesn't fit, it asks the user to confirm a re-categorisation or to extend the taxonomy explicitly.

This is deliberate. The library's value is in its consistent shape over time; a drifting taxonomy is a broken library.

---

## Run the tests

```bash
pytest
```

---

## Where this fits in BRAINS

This is a **BRAINS Incubator** project — internal infrastructure that keeps the team's research base curated, consistent, and queryable across many sessions and many contributors. It pairs naturally with the rest of the BRAINS toolkit: research feeds the weekly intelligence brief, the brand methodology, and the certification rubric work.

| | |
|---|---|
| ![Incubator](https://img.shields.io/badge/BRAINS-Incubator-4DA8FF?style=flat-square&labelColor=0A0A0A) | New projects, partnerships, prototypes — see the [BRAINS org page](https://github.com/shard-BRAINS) |
| ![Resume](https://img.shields.io/badge/-BRAINS--resume--skill-D99518?style=flat-square&labelColor=0A0A0A) | Sister skill — [ND-aware résumé toolkit](https://github.com/shard-BRAINS/BRAINS-resume-skill) |
| ![BuildPlatform](https://img.shields.io/badge/-BRAINS--build--platform-D99518?style=flat-square&labelColor=0A0A0A) | Companion delivery tooling — [agentic end-to-end builds](https://github.com/shard-BRAINS/BRAINS-build-platform) |
| ![Discord](https://img.shields.io/badge/-Discord-5865F2?style=flat-square&logo=discord&logoColor=FFFFFF&labelColor=0A0A0A) | Join the BRAINS Community — [discord.gg/BEmTXXscBr](https://discord.gg/BEmTXXscBr) |

If you'd like to use the skill on your own research collection, or contribute, see the Incubator application process at the [org page](https://github.com/shard-BRAINS#apply-to-join-the-incubator), or jump straight into [the Discord](https://discord.gg/BEmTXXscBr).

---

## Contributing

Contributions are welcome. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request — it covers identity-first language requirements, the code of conduct, and how to propose new taxonomy categories or pipeline steps.

---

## Licence

MIT — see [LICENSE](LICENSE).

---

<div align="center">

<br />

**Built by neurodivergent minds, for neurodivergent people.**

<br />

[![Made by](https://img.shields.io/badge/built%20by-neurodivergent%20minds-0A0A0A?style=for-the-badge&labelColor=D99518)](https://brainscertified.com)

</div>
