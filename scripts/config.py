"""Per-machine config loader for the BRAINS Research skill."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

REQUIRED_KEYS = (
    "research_root", "inbox_dir", "completed_dir",
    "duplicates_dir", "catalog_csv", "extract_pages", "extract_max_chars",
)


class ConfigError(Exception):
    """Raised when config.json is missing, malformed, or points at unreachable paths."""


@dataclass(frozen=True)
class Config:
    research_root: Path
    inbox_dir: Path
    completed_dir: Path
    duplicates_dir: Path
    catalog_csv: Path
    extract_pages: int
    extract_max_chars: int
    content_drafts_dir: Path | None = None
    archive_dir: Path | None = None


def _default_config_path() -> Path:
    env = os.environ.get("BRAINS_RESEARCH_CONFIG")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "config.json"


def _resolve_subdir(root: Path, value: str) -> Path:
    """Resolve a config subdir. '' or '.' means the root itself."""
    if value in ("", "."):
        return root
    return root / value


def load_config(path: Path | None = None) -> Config:
    cfg_path = Path(path) if path else _default_config_path()
    if not cfg_path.exists():
        raise ConfigError(f"config.json not found at {cfg_path}")
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"config.json malformed: {e}") from e

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ConfigError(f"config.json missing keys: {', '.join(missing)}")

    research_root = Path(data["research_root"])
    if not research_root.exists():
        raise ConfigError(f"research_root does not exist: {research_root}")

    content_drafts_dir = None
    if data.get("content_drafts_dir"):
        content_drafts_dir = Path(data["content_drafts_dir"])

    archive_dir = None
    if data.get("archive_dir"):
        archive_dir = _resolve_subdir(research_root, data["archive_dir"])

    return Config(
        research_root=research_root,
        inbox_dir=research_root / data["inbox_dir"],
        completed_dir=_resolve_subdir(research_root, data["completed_dir"]),
        duplicates_dir=research_root / data["duplicates_dir"],
        catalog_csv=research_root / data["catalog_csv"],
        extract_pages=int(data["extract_pages"]),
        extract_max_chars=int(data["extract_max_chars"]),
        content_drafts_dir=content_drafts_dir,
        archive_dir=archive_dir,
    )
