"""
test_records.py — Tests for app/records.py
Covers: load returns 20, get_by_id hit and miss, search "kailasa",
count_by site = 8/12, every record has the six fields and a source_url.
"""
import json
from pathlib import Path

import pytest

from app.records import count_by, get_by_id, load_records, search

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def records():
    return load_records()


def test_load_returns_20(records):
    """Load records must return exactly 20 cave records."""
    assert len(records) == 20


def test_count_by_site(records):
    """Ajanta = 8, Ellora = 12."""
    counts = count_by(records, "site")
    assert counts.get("Ajanta") == 8
    assert counts.get("Ellora") == 12


def test_every_record_has_six_fields(records):
    """Every record must have site, cave_no, religion_period, highlights, visit_info, source_url."""
    required = {"site", "cave_no", "religion_period", "highlights", "visit_info", "source_url"}
    for r in records:
        for field in required:
            assert field in r, f"Record missing '{field}': {r.get('site', '?')} cave {r.get('cave_no', '?')}"
            assert r[field], f"Empty '{field}' in {r.get('site', '?')} cave {r.get('cave_no', '?')}"


def test_search_kailasa(records):
    """Search for 'kailasa' must find at least Ellora Cave 16."""
    results = search(records, "kailasa")
    assert len(results) >= 1
    cave_nos = [r["cave_no"] for r in results]
    assert "16" in cave_nos


def test_get_by_id_hit(records):
    """get_by_id must find Ajanta cave 1."""
    result = get_by_id(records, "Ajanta", "1")
    assert result is not None
    assert result["site"] == "Ajanta"
    assert result["cave_no"] == "1"


def test_get_by_id_miss(records):
    """get_by_id must return None for non-existent cave."""
    result = get_by_id(records, "Ajanta", "999")
    assert result is None


def test_get_by_id_composite(records):
    """get_by_id with composite ID 'Ellora-16' must find Kailasa."""
    result = get_by_id(records, "Ellora-16")
    assert result is not None
    assert "Kailasa" in result.get("highlights", "") or "monolithic" in result.get("highlights", "").lower()


def test_search_empty_keyword(records):
    """Empty search returns all records."""
    results = search(records, "")
    assert len(results) == 20
