"""
Records module for LeniGuide
Handles loading, searching, and querying cave records.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import Counter


DEFAULT_RECORDS_PATH = Path(__file__).parent.parent / "data" / "sample_records.json"


def load_records(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Load cave records from JSON file.
    
    Args:
        path: Path to JSON file. If None, uses default sample_records.json
    
    Returns:
        List of record dictionaries
    """
    if path is None:
        path = DEFAULT_RECORDS_PATH
    
    with open(path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    return records


def search(q: str, records: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Search records by keyword (case-insensitive).
    Searches across highlights, religion_period, cave_no, and site fields.
    
    Args:
        q: Query string
        records: List of records to search. If None, loads from default path.
    
    Returns:
        List of matching records
    """
    if records is None:
        records = load_records()
    
    q_lower = q.lower()
    results = []
    
    for record in records:
        # Search in relevant fields
        searchable_text = " ".join([
            str(record.get("highlights", "")),
            str(record.get("religion_period", "")),
            str(record.get("cave_no", "")),
            str(record.get("site", ""))
        ]).lower()
        
        if q_lower in searchable_text:
            results.append(record)
    
    return results


def count_by(field: str, records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, int]:
    """
    Count records grouped by a specific field.
    
    Args:
        field: Field name to group by (e.g., 'site', 'religion_period')
        records: List of records. If None, loads from default path.
    
    Returns:
        Dictionary with field values as keys and counts as values
    """
    if records is None:
        records = load_records()
    
    values = [record.get(field, "unknown") for record in records]
    return dict(Counter(values))


def get_by_id(record_id: str, records: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    Get a single record by its ID.
    
    Args:
        record_id: The record ID to find
        records: List of records. If None, loads from default path.
    
    Returns:
        Record dictionary if found, None otherwise
    """
    if records is None:
        records = load_records()
    
    for record in records:
        if record.get("id") == record_id:
            return record
    
    return None


if __name__ == "__main__":
    # Quick test
    all_records = load_records()
    print(f"Loaded {len(all_records)} records")
    
    kailasa_results = search("kailasa", all_records)
    print(f"\nSearch 'kailasa': {len(kailasa_results)} results")
    for r in kailasa_results:
        print(f"  - {r['site'].title()} Cave {r['cave_no']}")
    
    site_counts = count_by("site", all_records)
    print(f"\nCounts by site: {site_counts}")
    
    record = get_by_id("ellora-016", all_records)
    if record:
        print(f"\nRecord ellora-016: Cave {record['cave_no']} - {record['highlights'][:80]}...")
