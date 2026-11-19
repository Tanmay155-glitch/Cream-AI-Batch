"""
Day 11 – Tests for data layer: load_records, search, count_by, get_by_id, SmartSearch.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide

4 tests covering records operations and TF-IDF smart search ranking.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.records import count_by, get_by_id, load_records, search
from app.smart_search import SmartSearch


# ============================================================================
# Test 1: Load 20 records with correct schema
# ============================================================================
def test_load_records_count_and_schema():
    """Verify 20 cave records load and each has the 6 required keys."""
    records = load_records()
    assert len(records) == 20, f"Expected 20 records, got {len(records)}"

    required_keys = {"site", "cave_no", "religion_period", "highlights", "visit_info", "source_url"}
    for idx, record in enumerate(records):
        missing = required_keys - set(record.keys())
        assert not missing, f"Record {idx} missing keys: {missing}"


# ============================================================================
# Test 2: count_by site returns Ajanta: 8, Ellora: 12
# ============================================================================
def test_count_by_site():
    """Verify count_by('site') returns {'Ajanta': 8, 'Ellora': 12}."""
    records = load_records()
    counts = count_by(records, "site")
    assert counts.get("Ajanta") == 8, f"Ajanta count {counts.get('Ajanta')} != 8"
    assert counts.get("Ellora") == 12, f"Ellora count {counts.get('Ellora')} != 12"


# ============================================================================
# Test 3: get_by_id finds Kailasa (Ellora-16) and keyword search finds Padmapani
# ============================================================================
def test_get_by_id_and_keyword_search():
    """Verify get_by_id('Ellora', '16') returns Kailasa and search('Padmapani') returns Ajanta 1."""
    records = load_records()

    # Ellora Cave 16 = Kailasa Temple
    kailasa = get_by_id(records, "Ellora", "16")
    assert kailasa is not None, "get_by_id('Ellora', '16') returned None"
    assert "Kailasa" in kailasa.get("highlights", ""), "Kailasa not in highlights"

    # Padmapani mural is in Ajanta Cave 1
    padma_results = search(records, "Padmapani")
    assert len(padma_results) >= 1, "search('Padmapani') returned no results"
    first = padma_results[0]
    assert first["site"] == "Ajanta", f"Expected Ajanta, got {first['site']}"
    assert str(first["cave_no"]) == "1", f"Expected cave 1, got {first['cave_no']}"


# ============================================================================
# Test 4: SmartSearch TF-IDF ranks Ellora Cave 16 first for Kailasa query
# ============================================================================
def test_smart_search_tfidf_ranking():
    """Verify SmartSearch.rank('monolithic rock-cut Kailasa temple') puts Ellora-16 at index 0."""
    records = load_records()
    searcher = SmartSearch(records)
    ranked = searcher.rank("monolithic rock-cut Kailasa temple")

    assert len(ranked) >= 1, "SmartSearch returned no results"
    top = ranked[0]
    assert top["site"] == "Ellora", f"Top result site is {top['site']}, expected Ellora"
    assert str(top["cave_no"]) == "16", f"Top result cave_no is {top['cave_no']}, expected 16"
    assert top["score"] > 0, f"Top result score {top['score']} is not positive"
