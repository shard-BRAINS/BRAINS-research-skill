"""Read-only catalog status + integrity report."""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

from scripts.config import load_config

TAXONOMY = [
    "AI-General", "AI-Ethics-Governance", "AI-Mental-Health",
    "AI-Neurodiversity-Autism", "AI-Education", "Neurodiversity-General",
    "Autism", "Suicide", "Mental-Health-General", "HCI-Cognitive-Theory",
    "Extremism-Radicalisation",
]


def _load_catalog_rows(catalog: Path) -> list[dict]:
    if not catalog.exists():
        return []
    with catalog.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def status_report(recent_n: int = 10) -> dict:
    cfg = load_config()
    rows = _load_catalog_rows(cfg.catalog_csv)

    by_category = {cat: 0 for cat in TAXONOMY}
    for r in rows:
        cat = r.get("category", "")
        if cat in by_category:
            by_category[cat] += 1

    missing_files: list[str] = []
    catalog_paths: set[str] = set()
    for r in rows:
        rel = r.get("new_path", "")
        catalog_paths.add(rel)
        abs_path = cfg.research_root / rel
        if not abs_path.exists():
            missing_files.append(rel)

    # Category-scoped orphan scan: only look inside the 10 canonical category
    # folders under completed_dir. This is safe whether completed_dir is the
    # research root itself (new layout) or a wrapper folder (legacy layout).
    orphan_files: list[str] = []
    for cat in TAXONOMY:
        cat_dir = cfg.completed_dir / cat
        if not cat_dir.exists():
            continue
        for p in cat_dir.rglob("*.pdf"):
            rel = str(p.relative_to(cfg.research_root)).replace("\\", "/")
            if rel not in catalog_paths:
                orphan_files.append(rel)

    # Inbox count is top-level PDFs only; the archive subfolder (e.g.
    # COMPLETED/) is intentionally excluded.
    inbox_count = sum(1 for _ in cfg.inbox_dir.glob("*.pdf")) if cfg.inbox_dir.exists() else 0
    duplicates_count = (
        sum(1 for _ in cfg.duplicates_dir.glob("*.pdf"))
        if cfg.duplicates_dir.exists() else 0
    )
    archive_count = (
        sum(1 for _ in cfg.archive_dir.glob("*.pdf"))
        if cfg.archive_dir is not None and cfg.archive_dir.exists() else 0
    )

    recent = rows[-recent_n:] if rows else []

    return {
        "total": len(rows),
        "by_category": by_category,
        "inbox_count": inbox_count,
        "duplicates_count": duplicates_count,
        "archive_count": archive_count,
        "missing_files": missing_files,
        "orphan_files": orphan_files,
        "recent": recent,
    }


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    report = status_report()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
