"""Tests for scripts.config."""
import json

import pytest

from scripts.config import Config, ConfigError, load_config

INBOX_NAME = "NEW RESEARCH - TO BE REVIEWED"
ARCHIVE_NAME = f"{INBOX_NAME}/COMPLETED"


def test_load_config_resolves_paths(config_file, mock_research_root):
    cfg = load_config(config_file)
    assert isinstance(cfg, Config)
    assert cfg.research_root == mock_research_root
    assert cfg.inbox_dir == mock_research_root / INBOX_NAME
    # completed_dir = "." → resolves to research_root itself
    assert cfg.completed_dir == mock_research_root
    assert cfg.duplicates_dir == mock_research_root / "_duplicates"
    assert cfg.catalog_csv == mock_research_root / "_catalog.csv"
    assert cfg.extract_pages == 2
    assert cfg.extract_max_chars == 3000
    assert cfg.archive_dir == mock_research_root / INBOX_NAME / "COMPLETED"


def test_load_config_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nonexistent.json")


def test_load_config_missing_required_key_raises(tmp_path):
    bad = tmp_path / "config.json"
    bad.write_text(json.dumps({"inbox_dir": INBOX_NAME}))
    with pytest.raises(ConfigError, match="research_root"):
        load_config(bad)


def test_load_config_unreachable_root_raises(tmp_path):
    bad = tmp_path / "config.json"
    bad.write_text(json.dumps({
        "research_root": str(tmp_path / "does_not_exist"),
        "inbox_dir": INBOX_NAME,
        "completed_dir": ".",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    with pytest.raises(ConfigError, match="research_root"):
        load_config(bad)


def test_load_config_accepts_utf8_bom(tmp_path, mock_research_root):
    """Windows PowerShell 5.1 writes UTF-8 with BOM by default — config loader must accept it."""
    cfg_path = tmp_path / "config.json"
    payload = json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": INBOX_NAME,
        "completed_dir": ".",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    })
    cfg_path.write_bytes(b"\xef\xbb\xbf" + payload.encode("utf-8"))
    cfg = load_config(cfg_path)
    assert cfg.research_root == mock_research_root


def test_load_config_optional_content_drafts_dir(tmp_path, mock_research_root):
    """content_drafts_dir is optional; when present it is loaded as a Path."""
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": INBOX_NAME,
        "completed_dir": ".",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
        "content_drafts_dir": str(tmp_path / "drafts"),
    }))
    loaded = load_config(cfg)
    assert loaded.content_drafts_dir == tmp_path / "drafts"


def test_load_config_missing_content_drafts_dir_is_none(config_file):
    """When content_drafts_dir is absent, the attribute is None."""
    loaded = load_config(config_file)
    assert loaded.content_drafts_dir is None


def test_load_config_missing_archive_dir_is_none(tmp_path, mock_research_root):
    """When archive_dir is absent, the attribute is None (legacy config compatible)."""
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": INBOX_NAME,
        "completed_dir": ".",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    loaded = load_config(cfg)
    assert loaded.archive_dir is None


def test_load_config_legacy_completed_dir_still_works(tmp_path, mock_research_root):
    """A non-'.' completed_dir (legacy layout) still resolves under the research root."""
    (mock_research_root / "Completed Review").mkdir()
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": INBOX_NAME,
        "completed_dir": "Completed Review",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    loaded = load_config(cfg)
    assert loaded.completed_dir == mock_research_root / "Completed Review"


def test_load_config_default_location(monkeypatch, tmp_path, mock_research_root):
    """If no path passed, the env var BRAINS_RESEARCH_CONFIG steers the lookup."""
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": INBOX_NAME,
        "completed_dir": ".",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(cfg_path))
    cfg = load_config()
    assert cfg.research_root == mock_research_root
