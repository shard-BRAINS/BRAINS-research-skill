"""One-time migration for the v1.1 -> v1.2 folder reorg.

Strips the legacy ``Completed Review/`` prefix from the ``new_path`` column of
``_catalog.csv``. Writes a backup to ``_catalog.csv.pre-1.2.0.bak`` before
mutating the source. Safe to re-run: rows already free of the prefix are left
untouched.

Usage:
    python -m scripts.migrate_catalog_1_2_0            # apply
    python -m scripts.migrate_catalog_1_2_0 --dry-run  # report only
"""
from __future__ import annotations

import csv
import io
import shutil
import sys

from scripts.config import load_config

LEGACY_PREFIX = "Completed Review/"


def migrate(dry_run: bool = False) -> dict:
    cfg = load_config()
    src = cfg.catalog_csv
    if not src.exists():
        return {"error": f"catalog not found at {src}", "changed": 0, "total": 0}

    with src.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    before = sum(1 for r in rows if (r.get("new_path") or "").startswith(LEGACY_PREFIX))
    for r in rows:
        p = r.get("new_path") or ""
        if p.startswith(LEGACY_PREFIX):
            r["new_path"] = p[len(LEGACY_PREFIX):]

    if dry_run:
        return {"dry_run": True, "would_change": before, "total": len(rows), "backup": None}

    bak = src.with_name("_catalog.csv.pre-1.2.0.bak")
    shutil.copy2(src, bak)

    with src.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    return {"dry_run": False, "changed": before, "total": len(rows), "backup": str(bak)}


def main(argv: list[str] | None = None) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    argv = argv if argv is not None else sys.argv[1:]
    dry = "--dry-run" in argv
    result = migrate(dry_run=dry)
    if "error" in result:
        print(result["error"])
        return 1
    if dry:
        print(f"Dry-run: would strip prefix from {result['would_change']} of {result['total']} rows.")
    else:
        print(f"Migrated {result['changed']} of {result['total']} rows.")
        print(f"Backup written: {result['backup']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
