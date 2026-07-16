"""Apply a rename plan: file PDFs into <Category>/, optionally archive the original, append _catalog.csv."""
from __future__ import annotations

import csv
import io
import json
import shutil
import sys
from pathlib import Path

from scripts.config import load_config

FIELDNAMES = [
    "original_filename", "new_filename", "category", "year",
    "author", "title", "doc_type", "byte_size", "new_path",
]


def apply_plan(dry_run: bool = False) -> dict:
    cfg = load_config()
    plan_path = cfg.research_root / "_rename_plan.json"
    if not plan_path.exists():
        return {"moved": 0, "would_move": 0, "missing": [], "skipped": [], "no_plan": True}

    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    moves: list[tuple[Path, Path, dict]] = []
    missing: list[str] = []
    skipped: list[str] = []

    for orig, info in plan.items():
        src_path = cfg.inbox_dir / orig
        if not src_path.exists():
            missing.append(orig)
            continue
        dst_dir = cfg.completed_dir / info["category"]
        dst_path = dst_dir / info["new_name"]
        if dst_path.exists():
            skipped.append(f"{orig} -> {dst_path} (target exists)")
            continue
        moves.append((src_path, dst_path, info))

    if dry_run:
        return {
            "moved": 0,
            "would_move": len(moves),
            "missing": missing,
            "skipped": skipped,
        }

    catalog_exists = cfg.catalog_csv.exists()
    rows_to_append = []
    archived: list[str] = []
    for src_path, dst_path, info in moves:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        size = src_path.stat().st_size

        if cfg.archive_dir is not None:
            cfg.archive_dir.mkdir(parents=True, exist_ok=True)
            archive_path = cfg.archive_dir / src_path.name
            shutil.copy2(str(src_path), str(archive_path))
            archived.append(src_path.name)

        shutil.move(str(src_path), str(dst_path))

        rows_to_append.append({
            "original_filename": src_path.name,
            "new_filename": dst_path.name,
            "category": info["category"],
            "year": info["year"],
            "author": info["author"],
            "title": info["title"],
            "doc_type": info["doc_type"],
            "byte_size": size,
            "new_path": str(dst_path.relative_to(cfg.research_root)).replace("\\", "/"),
        })

    if rows_to_append:
        mode = "a" if catalog_exists else "w"
        with cfg.catalog_csv.open(mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not catalog_exists:
                writer.writeheader()
            writer.writerows(rows_to_append)

    return {
        "moved": len(rows_to_append),
        "would_move": 0,
        "missing": missing,
        "skipped": skipped,
        "archived": archived,
    }


def main(argv: list[str] | None = None) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    argv = argv if argv is not None else sys.argv[1:]
    dry = "--dry-run" in argv
    result = apply_plan(dry_run=dry)
    if result.get("no_plan"):
        print("No _rename_plan.json found. Run /brains-research-process first.")
        return 0
    total = result["moved"] + result["would_move"] + len(result["missing"]) + len(result["skipped"])
    print(f"Plan: {total} entries")
    if dry:
        print(f"Would move: {result['would_move']}")
    else:
        print(f"Moved: {result['moved']}")
        print(f"Archived originals: {len(result.get('archived', []))}")
    print(f"Missing source files: {len(result['missing'])}")
    print(f"Skipped (target exists): {len(result['skipped'])}")
    if result["missing"]:
        print("MISSING:", *result["missing"], sep="\n  ")
    if result["skipped"]:
        print("SKIPPED:", *result["skipped"], sep="\n  ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
