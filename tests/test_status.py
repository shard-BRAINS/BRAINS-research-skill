"""Tests for scripts.status."""
import csv

from scripts.status import status_report

TAXONOMY = [
    "AI-General", "AI-Ethics-Governance", "AI-Mental-Health",
    "AI-Neurodiversity-Autism", "AI-Education", "Neurodiversity-General",
    "Autism", "Suicide", "Mental-Health-General", "HCI-Cognitive-Theory",
    "Extremism-Radicalisation",
]

INBOX_NAME = "NEW RESEARCH - TO BE REVIEWED"


def _seed_catalog(root, rows):
    catalog = root / "_catalog.csv"
    with catalog.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "original_filename", "new_filename", "category", "year",
            "author", "title", "doc_type", "byte_size", "new_path",
        ])
        writer.writeheader()
        writer.writerows(rows)
    return catalog


def _place_file(root, relpath, content=b"x"):
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def test_status_empty_corpus(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    report = status_report()
    assert report["total"] == 0
    assert report["by_category"] == {cat: 0 for cat in TAXONOMY}
    assert report["inbox_count"] == 0
    assert report["duplicates_count"] == 0
    assert report["archive_count"] == 0
    assert report["missing_files"] == []
    assert report["orphan_files"] == []


def test_status_counts_catalog_and_categories(
    mock_research_root, config_file, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _place_file(mock_research_root, "AI-General/a.pdf")
    _place_file(mock_research_root, "Autism/b.pdf")
    _seed_catalog(mock_research_root, [
        {"original_filename": "x.pdf", "new_filename": "a.pdf", "category": "AI-General",
         "year": "2024", "author": "X", "title": "a", "doc_type": "Test",
         "byte_size": "1", "new_path": "AI-General/a.pdf"},
        {"original_filename": "y.pdf", "new_filename": "b.pdf", "category": "Autism",
         "year": "2025", "author": "Y", "title": "b", "doc_type": "Test",
         "byte_size": "1", "new_path": "Autism/b.pdf"},
    ])
    report = status_report()
    assert report["total"] == 2
    assert report["by_category"]["AI-General"] == 1
    assert report["by_category"]["Autism"] == 1
    assert report["missing_files"] == []
    assert report["orphan_files"] == []


def test_status_detects_missing_files(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [
        {"original_filename": "x.pdf", "new_filename": "ghost.pdf", "category": "AI-General",
         "year": "2024", "author": "X", "title": "ghost", "doc_type": "Test",
         "byte_size": "1", "new_path": "AI-General/ghost.pdf"},
    ])
    report = status_report()
    assert "AI-General/ghost.pdf" in report["missing_files"]


def test_status_detects_orphan_files(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _place_file(mock_research_root, "AI-General/orphan.pdf")
    _seed_catalog(mock_research_root, [])
    report = status_report()
    assert any("orphan.pdf" in p for p in report["orphan_files"])


def test_status_inbox_count_excludes_archive_subfolder(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    """Files in the COMPLETED archive under the inbox must not inflate inbox_count."""
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _place_file(mock_research_root, f"{INBOX_NAME}/COMPLETED/already_processed.pdf")
    _place_file(mock_research_root, "_duplicates/dup1.pdf")
    _place_file(mock_research_root, "_duplicates/dup2.pdf")
    report = status_report()
    assert report["inbox_count"] == 1  # only sample.pdf at the top level
    assert report["duplicates_count"] == 2
    assert report["archive_count"] == 1


def test_status_orphan_scan_ignores_inbox_pdfs(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    """When completed_dir='.', the orphan scan must NOT flag PDFs sitting in the inbox."""
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [])
    report = status_report()
    # sample.pdf is in the inbox — not in a category folder — so it must not be an orphan
    assert report["orphan_files"] == []
