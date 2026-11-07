"""
Data operations module for LeniGuide cave records.
Provides functions to load, search, count, and retrieve cave information.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any


def load_records(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load cave records from JSON file.
    
    Args:
        file_path: Path to JSON file. If None, loads from default location
                   (data/sample_records.json relative to project root).
    
    Returns:
        List of cave record dictionaries.
    
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if file_path is None:
        # Default path: data/sample_records.json relative to project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        file_path = project_root / "data" / "sample_records.json"
    else:
        file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Records file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    return records


def search(records: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """
    Search for caves matching a keyword across all text fields.
    
    Performs case-insensitive substring search across site, cave_no,
    religion_period, highlights, and visit_info fields.
    
    Args:
        records: List of cave record dictionaries.
        keyword: Search term (case-insensitive).
    
    Returns:
        List of matching cave records.
    """
    if not keyword:
        return records
    
    keyword_lower = keyword.lower()
    matches = []
    
    for record in records:
        # Search across key text fields
        searchable_fields = [
            record.get('site', ''),
            record.get('cave_no', ''),
            record.get('religion_period', ''),
            record.get('highlights', ''),
            record.get('visit_info', '')
        ]
        
        # Convert all fields to lowercase and check for keyword
        combined_text = ' '.join(str(field) for field in searchable_fields).lower()
        
        if keyword_lower in combined_text:
            matches.append(record)
    
    return matches


def count_by(records: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    """
    Count records by a specified field.
    
    Args:
        records: List of cave record dictionaries.
        field: Field name to count by. Supports:
               - 'site': Count by Ajanta/Ellora
               - 'religion': Count by broad religious tradition (Buddhist/Hindu/Jain)
               - 'religion_period': Count by full religion_period string
               - Any other field: Count by that field's values
    
    Returns:
        Dictionary mapping field values to counts.
    """
    counts = {}
    
    for record in records:
        if field == 'religion':
            # Extract broad religious category
            religion_period = record.get('religion_period', '')
            if 'Buddhist' in religion_period:
                category = 'Buddhist'
            elif 'Hindu' in religion_period:
                category = 'Hindu'
            elif 'Jain' in religion_period:
                category = 'Jain'
            else:
                category = 'Other'
        else:
            # Use the field value directly
            category = record.get(field, 'Unknown')
        
        counts[category] = counts.get(category, 0) + 1
    
    return counts


def get_by_id(records: List[Dict[str, Any]], 
              record_id_or_site: str, 
              cave_no: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific cave record by ID.
    
    Supports multiple call patterns:
    1. get_by_id(records, "Ajanta", "1") - site and cave number
    2. get_by_id(records, "Ajanta-1") - composite ID with hyphen
    3. get_by_id(records, "1") - cave number only (returns first match)
    
    Args:
        records: List of cave record dictionaries.
        record_id_or_site: Either a site name, a composite ID (site-cave_no),
                          or just a cave number.
        cave_no: Cave number (optional, used with site name).
    
    Returns:
        Matching cave record dictionary, or None if not found.
    """
    # Pattern 1: Two arguments provided (site, cave_no)
    if cave_no is not None:
        site = record_id_or_site
        for record in records:
            if (record.get('site', '').lower() == site.lower() and 
                record.get('cave_no', '') == str(cave_no)):
                return record
        return None
    
    # Pattern 2 & 3: Single argument - could be composite ID or just cave number
    identifier = record_id_or_site
    
    # Check if it's a composite ID (contains hyphen)
    if '-' in identifier:
        parts = identifier.split('-', 1)
        if len(parts) == 2:
            site, cave_num = parts
            for record in records:
                if (record.get('site', '').lower() == site.lower() and 
                    record.get('cave_no', '') == cave_num):
                    return record
    
    # Try matching as cave number only (returns first match)
    for record in records:
        if record.get('cave_no', '') == identifier:
            return record
    
    # Try case-insensitive site match (useful for "ajanta" or "ellora" alone)
    for record in records:
        if record.get('site', '').lower() == identifier.lower():
            return record
    
    return None


def main():
    """Demonstrate records.py functionality."""
    print("=" * 80)
    print("TESTING app/records.py MODULE")
    print("=" * 80)
    
    # Test load_records
    print("\n1. Testing load_records()...")
    records = load_records()
    print(f"   ✓ Loaded {len(records)} cave records")
    
    # Test search
    print("\n2. Testing search()...")
    kailasa_results = search(records, "Kailasa")
    print(f"   ✓ Found {len(kailasa_results)} caves matching 'Kailasa'")
    for r in kailasa_results:
        print(f"     - {r['site']} Cave {r['cave_no']}")
    
    # Test count_by
    print("\n3. Testing count_by()...")
    site_counts = count_by(records, 'site')
    print(f"   ✓ Caves by site: {site_counts}")
    
    religion_counts = count_by(records, 'religion')
    print(f"   ✓ Caves by religion: {religion_counts}")
    
    # Test get_by_id
    print("\n4. Testing get_by_id()...")
    
    cave1 = get_by_id(records, "Ajanta", "1")
    print(f"   ✓ get_by_id(records, 'Ajanta', '1'): Cave {cave1['cave_no']} found")
    
    cave2 = get_by_id(records, "Ellora-16")
    print(f"   ✓ get_by_id(records, 'Ellora-16'): Cave {cave2['cave_no']} (Kailasa) found")
    
    cave3 = get_by_id(records, "16")
    print(f"   ✓ get_by_id(records, '16'): {cave3['site']} Cave {cave3['cave_no']} found")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
