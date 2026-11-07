"""
Data ingestion and cleaning pipeline for LeniGuide.
Loads, validates, cleans, and normalizes cave records into data/records.json.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Ensure app module can be imported
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.models import Record


def verify_raw_data() -> Dict[str, Any]:
    """
    Verify that raw HTML files exist and log their metadata.
    
    Returns:
        Dictionary with verification results.
    """
    raw_dir = project_root / "data" / "raw"
    results = {
        "raw_dir_exists": raw_dir.exists(),
        "files": {}
    }
    
    if raw_dir.exists():
        for file_path in raw_dir.glob("*.html"):
            size_bytes = file_path.stat().st_size
            results["files"][file_path.name] = {
                "exists": True,
                "size_kb": size_bytes / 1024,
                "size_bytes": size_bytes
            }
    
    return results


def normalize_visit_info(visit_info: str, site: str) -> str:
    """
    Normalize and enhance visit_info field with consistent ASI data.
    
    Args:
        visit_info: Original visit info string
        site: Either "Ajanta" or "Ellora"
    
    Returns:
        Normalized visit info with standardized timing and fee information
    """
    # Ensure ASI timing and fee information is present
    if site == "Ajanta":
        timing = "Open 9:00 AM to 5:00 PM (Closed Mondays)"
    else:  # Ellora
        timing = "Open Sunrise to Sunset (Closed Tuesdays)"
    
    fee_info = "ASI Entry: Rs 40 (cash) / Rs 35 (online), children under 15 years FREE"
    
    # If visit_info already contains timing info, keep it as is
    # Otherwise, ensure it has the critical information
    if "9:00 AM" in visit_info or "Sunrise" in visit_info:
        return visit_info.strip()
    else:
        # Prepend timing if not present
        return f"{timing}. {fee_info}. {visit_info}".strip()


def clean_record(raw_row: Dict[str, Any]) -> Optional[Record]:
    """
    Clean and normalize a single raw record into a validated Record object.
    
    Args:
        raw_row: Raw dictionary from source data
    
    Returns:
        Validated Record object, or None if record is invalid
    
    Raises:
        ValueError: If critical validation fails
        KeyError: If required fields are missing
        TypeError: If field types are incompatible
    """
    # Normalize field names (handle variations)
    normalized = {}
    
    # Map common variations to standard field names
    field_mapping = {
        "site": ["site", "location", "monument_site"],
        "cave_no": ["cave_no", "cave_number", "number", "cave_id"],
        "religion_period": ["religion_period", "period", "religion", "era"],
        "highlights": ["highlights", "description", "features", "details"],
        "visit_info": ["visit_info", "visitor_info", "timing", "visit_details"],
        "source_url": ["source_url", "source", "url", "reference"]
    }
    
    for standard_field, variations in field_mapping.items():
        for variant in variations:
            if variant in raw_row:
                normalized[standard_field] = raw_row[variant]
                break
    
    # Ensure all required fields are present
    required = ["site", "cave_no", "religion_period", "highlights", "visit_info", "source_url"]
    for field in required:
        if field not in normalized:
            raise KeyError(f"Missing required field: {field}")
    
    # Normalize specific fields
    # 1. Site name (capitalize properly)
    site = str(normalized["site"]).strip()
    if site.lower() == "ajanta":
        site = "Ajanta"
    elif site.lower() == "ellora":
        site = "Ellora"
    
    # 2. Cave number (ensure string, remove extra spaces)
    cave_no = str(normalized["cave_no"]).strip()
    
    # 3. Religion period (clean up extra whitespace)
    religion_period = " ".join(str(normalized["religion_period"]).split())
    
    # 4. Highlights (clean up extra whitespace, ensure reasonable length)
    highlights = " ".join(str(normalized["highlights"]).split())
    if len(highlights) < 20:
        raise ValueError(f"Highlights too short ({len(highlights)} chars) for cave {cave_no}")
    
    # 5. Visit info (normalize timing and fee information)
    visit_info = normalize_visit_info(str(normalized["visit_info"]), site)
    
    # 6. Source URL (validate format)
    source_url = str(normalized["source_url"]).strip()
    if not source_url.startswith("http"):
        raise ValueError(f"Invalid source_url: {source_url}")
    
    # Create and validate Record object
    record = Record(
        site=site,
        cave_no=cave_no,
        religion_period=religion_period,
        highlights=highlights,
        visit_info=visit_info,
        source_url=source_url
    )
    
    return record


def load_sample_records() -> List[Dict[str, Any]]:
    """
    Load sample records from data/sample_records.json.
    
    Returns:
        List of raw record dictionaries
    """
    sample_path = project_root / "data" / "sample_records.json"
    
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample records not found: {sample_path}")
    
    with open(sample_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    return records


def inject_test_malformed_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Inject a few malformed test records to verify error handling.
    
    Args:
        records: Original record list
    
    Returns:
        Record list with test malformed records added
    """
    # Create copies to avoid modifying originals
    test_records = records.copy()
    
    # Test case 1: Missing required field
    malformed_1 = {
        "site": "Ajanta",
        "cave_no": "999",
        "religion_period": "Test Period"
        # Missing: highlights, visit_info, source_url
    }
    
    # Test case 2: Invalid site name
    malformed_2 = {
        "site": "InvalidSite",
        "cave_no": "888",
        "religion_period": "Test",
        "highlights": "Test highlights",
        "visit_info": "Test visit info",
        "source_url": "http://test.com"
    }
    
    # Test case 3: Empty highlights (too short)
    malformed_3 = {
        "site": "Ellora",
        "cave_no": "777",
        "religion_period": "Test",
        "highlights": "Short",  # Less than 20 chars
        "visit_info": "Test visit info",
        "source_url": "http://test.com"
    }
    
    # Insert malformed records at different positions
    test_records.insert(5, malformed_1)
    test_records.insert(15, malformed_2)
    test_records.append(malformed_3)
    
    return test_records


def ingest_and_save(dry_run: bool = False) -> Dict[str, int]:
    """
    Main ingestion pipeline: load, clean, validate, and save records.
    
    Args:
        dry_run: If True, inject test malformed records for validation
    
    Returns:
        Dictionary with processing statistics
    """
    print("=" * 80)
    print("LENIGUIDE DATA INGESTION PIPELINE")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)
    
    stats = {
        "total_processed": 0,
        "valid_records": 0,
        "skipped_records": 0,
        "errors": []
    }
    
    # Step 1: Verify raw data exists
    print("\n📂 Step 1: Verifying raw data files...")
    raw_verification = verify_raw_data()
    
    if raw_verification["raw_dir_exists"]:
        print(f"  ✓ Raw data directory exists")
        for filename, metadata in raw_verification["files"].items():
            print(f"  ✓ {filename}: {metadata['size_kb']:.1f} KB")
    else:
        print(f"  ⚠ Raw data directory not found (run 'python -m app.fetch' first)")
    
    # Step 2: Load sample records
    print("\n📥 Step 2: Loading source records...")
    try:
        raw_records = load_sample_records()
        print(f"  ✓ Loaded {len(raw_records)} records from sample_records.json")
        
        if dry_run:
            raw_records = inject_test_malformed_records(raw_records)
            print(f"  ⚠ DRY RUN: Injected 3 malformed test records")
            print(f"  ✓ Total records to process: {len(raw_records)}")
    except FileNotFoundError as e:
        print(f"  ✗ Error: {e}")
        return stats
    
    # Step 3: Clean and validate records
    print("\n🧹 Step 3: Cleaning and validating records...")
    print("-" * 80)
    
    valid_records = []
    
    for idx, raw_row in enumerate(raw_records, 1):
        stats["total_processed"] += 1
        
        try:
            # Attempt to clean and validate the record
            record = clean_record(raw_row)
            
            if record:
                valid_records.append(record.to_dict())
                stats["valid_records"] += 1
                
                # Show progress for valid records
                if idx <= 5 or idx > len(raw_records) - 3:  # Show first 5 and last 3
                    print(f"  ✓ [{idx:2d}] {record.site} Cave {record.cave_no}: {record.religion_period[:40]}")
                elif idx == 6:
                    print(f"  ... processing records 6 to {len(raw_records) - 3} ...")
        
        except (ValueError, KeyError, TypeError) as e:
            stats["skipped_records"] += 1
            stats["errors"].append({
                "row_index": idx,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "cave_no": raw_row.get("cave_no", "unknown")
            })
            print(f"  ✗ [{idx:2d}] SKIPPED: {type(e).__name__} - {e}")
    
    # Step 4: Save to data/records.json
    print("\n💾 Step 4: Saving validated records...")
    
    output_path = project_root / "data" / "records.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(valid_records, f, indent=2, ensure_ascii=False)
        
        output_size_kb = output_path.stat().st_size / 1024
        print(f"  ✓ Saved {len(valid_records)} records to: {output_path.name}")
        print(f"  ✓ File size: {output_size_kb:.1f} KB")
    
    except Exception as e:
        print(f"  ✗ Failed to save records: {e}")
        return stats
    
    # Step 5: Summary
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"  Total records processed:  {stats['total_processed']}")
    print(f"  Valid records saved:      {stats['valid_records']}")
    print(f"  Bad records skipped:      {stats['skipped_records']}")
    print(f"  Success rate:             {stats['valid_records']/stats['total_processed']*100:.1f}%")
    
    if stats["errors"]:
        print(f"\n⚠ Skipped Records Details:")
        for error in stats["errors"]:
            print(f"  • Row {error['row_index']} (Cave {error['cave_no']}): "
                  f"{error['error_type']} - {error['error_message'][:60]}")
    
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"\nNext step: Run 'python -m app.cli' to browse the cleaned data")
    
    return stats


def main():
    """Main entry point for the ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LeniGuide data ingestion pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inject test malformed records to verify error handling"
    )
    
    args = parser.parse_args()
    
    try:
        stats = ingest_and_save(dry_run=args.dry_run)
        
        # Exit with appropriate code
        if stats["valid_records"] >= 20:
            sys.exit(0)  # Success
        else:
            print(f"\n⚠ Warning: Expected at least 20 valid records, got {stats['valid_records']}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
