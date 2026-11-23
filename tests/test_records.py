"""
Tests for the records module
"""

import pytest
from app.records import load_records, search, count_by, get_by_id


@pytest.fixture
def records():
    """Load records for tests"""
    return load_records()


def test_load_returns_20_records(records):
    """Test that we have exactly 20 records"""
    assert len(records) == 20


def test_all_records_have_six_core_fields(records):
    """Test that every record has the six required fields"""
    required_fields = {"id", "site", "cave_no", "religion_period", "highlights", "visit_info", "source_url"}
    
    for record in records:
        assert required_fields.issubset(record.keys()), \
            f"Record {record.get('id', 'unknown')} missing required fields"


def test_all_records_have_source_url(records):
    """Test that every record has a source_url"""
    for record in records:
        assert "source_url" in record
        assert record["source_url"].startswith("http"), \
            f"Record {record['id']} has invalid source_url"


def test_search_kailasa_finds_matches(records):
    """Test searching for 'kailasa' returns expected results"""
    results = search("kailasa", records)
    assert len(results) > 0
    assert any("kailasa" in r["highlights"].lower() for r in results)


def test_search_case_insensitive(records):
    """Test that search is case-insensitive"""
    results_lower = search("kailasa", records)
    results_upper = search("KAILASA", records)
    results_mixed = search("Kailasa", records)
    
    assert len(results_lower) == len(results_upper) == len(results_mixed)


def test_search_no_results():
    """Test search with no matches"""
    records = load_records()
    results = search("nonexistent_query_xyz", records)
    assert len(results) == 0


def test_count_by_site(records):
    """Test counting by site returns correct distribution"""
    counts = count_by("site", records)
    
    assert "ajanta" in counts
    assert "ellora" in counts
    assert counts["ajanta"] == 8
    assert counts["ellora"] == 12


def test_count_by_religion_period(records):
    """Test counting by religion_period"""
    counts = count_by("religion_period", records)
    
    # Should have multiple different periods
    assert len(counts) > 3
    assert sum(counts.values()) == 20


def test_get_by_id_hit(records):
    """Test getting a record by valid ID"""
    record = get_by_id("ellora-016", records)
    
    assert record is not None
    assert record["id"] == "ellora-016"
    assert record["cave_no"] == "16"
    assert record["site"] == "ellora"
    assert "Kailasa" in record["highlights"]


def test_get_by_id_miss(records):
    """Test getting a record with invalid ID"""
    record = get_by_id("invalid-id-999", records)
    assert record is None


def test_site_distribution_correct(records):
    """Test that we have 8 Ajanta and 12 Ellora caves as specified"""
    ajanta_records = [r for r in records if r["site"] == "ajanta"]
    ellora_records = [r for r in records if r["site"] == "ellora"]
    
    assert len(ajanta_records) == 8
    assert len(ellora_records) == 12


def test_specific_ajanta_caves_included(records):
    """Test that specified Ajanta caves are included"""
    expected_caves = ["1", "2", "9", "10", "16", "17", "19", "26"]
    ajanta_records = [r for r in records if r["site"] == "ajanta"]
    ajanta_cave_numbers = [r["cave_no"] for r in ajanta_records]
    
    for cave_no in expected_caves:
        assert cave_no in ajanta_cave_numbers, f"Ajanta cave {cave_no} missing"


def test_specific_ellora_caves_included(records):
    """Test that specified Ellora caves are included"""
    expected_caves = ["5", "10", "12", "14", "15", "16", "21", "29", "30", "32", "33", "34"]
    ellora_records = [r for r in records if r["site"] == "ellora"]
    ellora_cave_numbers = [r["cave_no"] for r in ellora_records]
    
    for cave_no in expected_caves:
        assert cave_no in ellora_cave_numbers, f"Ellora cave {cave_no} missing"


def test_highlights_not_empty(records):
    """Test that all records have non-empty highlights"""
    for record in records:
        assert len(record["highlights"]) > 10, \
            f"Record {record['id']} has insufficient highlights"
