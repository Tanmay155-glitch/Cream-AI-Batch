"""
Command-line interface for LeniGuide cave guide application.
Interactive menu to browse, search, and explore Ajanta and Ellora caves.
"""

import sys
from pathlib import Path

# Ensure app module can be imported regardless of how script is run
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.records import load_records, search, count_by, get_by_id


def print_header():
    """Print application header."""
    print("\n" + "=" * 80)
    print(" " * 20 + "🏛️  LENIGUIDE - AJANTA & ELLORA CAVES  🏛️")
    print(" " * 15 + "Student: Tanmay Subhash Gawali (2124UMLM2016)")
    print(" " * 25 + "Project ID: SJ-52")
    print("=" * 80)


def print_menu():
    """Print main menu options."""
    print("\n" + "-" * 80)
    print("MAIN MENU:")
    print("  1. View all cave records")
    print("  2. Search caves by keyword")
    print("  3. Count caves by category")
    print("  4. Get specific cave by ID")
    print("  0. Exit")
    print("-" * 80)


def format_cave_record(record, detailed=False):
    """
    Format a cave record for display.
    
    Args:
        record: Cave record dictionary.
        detailed: If True, show full details; if False, show summary.
    """
    site = record['site']
    cave_no = record['cave_no']
    religion_period = record['religion_period']
    highlights = record['highlights']
    visit_info = record['visit_info']
    
    if detailed:
        print(f"\n{'─' * 80}")
        print(f"🏛️  {site} Cave {cave_no}")
        print(f"{'─' * 80}")
        print(f"Period:      {religion_period}")
        print(f"\nHighlights:\n  {highlights}")
        print(f"\nVisit Info:\n  {visit_info}")
        print(f"\nSource:      {record['source_url']}")
        print(f"{'─' * 80}")
    else:
        # Summary format for lists
        print(f"  • {site} Cave {cave_no:>3} | {religion_period}")
        print(f"    {highlights[:100]}{'...' if len(highlights) > 100 else ''}")


def view_all_caves(records):
    """Display all cave records."""
    print("\n" + "=" * 80)
    print(f"ALL CAVE RECORDS ({len(records)} total)")
    print("=" * 80)
    
    current_site = None
    for idx, record in enumerate(records, 1):
        site = record['site']
        
        # Print site header when it changes
        if site != current_site:
            print(f"\n{'▼' * 40}")
            print(f"  {site} Caves")
            print(f"{'▼' * 40}")
            current_site = site
        
        format_cave_record(record, detailed=False)
    
    print("\n" + "=" * 80)


def search_caves(records):
    """Interactive cave search by keyword."""
    print("\n" + "=" * 80)
    print("SEARCH CAVES BY KEYWORD")
    print("=" * 80)
    print("Examples: 'Kailasa', 'painting', 'Buddhist', 'Jain', 'reclining Buddha'")
    
    keyword = input("\nEnter search keyword (or press Enter to cancel): ").strip()
    
    if not keyword:
        print("Search cancelled.")
        return
    
    results = search(records, keyword)
    
    print("\n" + "-" * 80)
    print(f"SEARCH RESULTS: Found {len(results)} cave(s) matching '{keyword}'")
    print("-" * 80)
    
    if results:
        for record in results:
            format_cave_record(record, detailed=True)
    else:
        print("\nNo caves found matching your search term.")
        print("Try different keywords like: 'Buddha', 'Shiva', 'Jain', 'painting', 'temple'")


def count_caves(records):
    """Display cave counts by various categories."""
    print("\n" + "=" * 80)
    print("CAVE STATISTICS BY CATEGORY")
    print("=" * 80)
    
    # Count by site
    print("\n📍 Caves by Site:")
    print("-" * 40)
    site_counts = count_by(records, 'site')
    for site, count in sorted(site_counts.items()):
        print(f"  {site:.<25} {count:>3} caves")
    
    # Count by religion
    print("\n🕉️  Caves by Religion:")
    print("-" * 40)
    religion_counts = count_by(records, 'religion')
    for religion, count in sorted(religion_counts.items()):
        print(f"  {religion:.<25} {count:>3} caves")
    
    # Count by detailed period
    print("\n📜 Caves by Detailed Period:")
    print("-" * 40)
    period_counts = count_by(records, 'religion_period')
    for period, count in sorted(period_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {period[:40]:.<42} {count:>2}")
    
    print("\n" + "=" * 80)


def get_cave_by_id(records):
    """Interactive cave lookup by ID."""
    print("\n" + "=" * 80)
    print("GET SPECIFIC CAVE BY ID")
    print("=" * 80)
    print("Supported formats:")
    print("  1. Site + Cave Number: 'Ajanta' then '1'")
    print("  2. Composite ID: 'Ajanta-1' or 'Ellora-16'")
    print("  3. Cave Number only: '16' (returns first match)")
    
    id_input = input("\nEnter cave ID: ").strip()
    
    if not id_input:
        print("Lookup cancelled.")
        return
    
    # Check if input contains a hyphen (composite ID)
    if '-' in id_input:
        result = get_by_id(records, id_input)
    else:
        # Ask if this is a site name or cave number
        print(f"\nIs '{id_input}' a site name (s) or cave number (c)?")
        choice = input("Enter 's' for site, 'c' for cave number, or press Enter for cave: ").strip().lower()
        
        if choice == 's':
            # It's a site name, ask for cave number
            cave_num = input("Enter cave number: ").strip()
            result = get_by_id(records, id_input, cave_num)
        else:
            # Treat as cave number
            result = get_by_id(records, id_input)
    
    print("\n" + "-" * 80)
    if result:
        print("CAVE FOUND:")
        format_cave_record(result, detailed=True)
    else:
        print("❌ Cave not found.")
        print("Please check the ID format and try again.")


def main():
    """Main CLI application loop."""
    try:
        # Load cave records at startup
        records = load_records()
        
        print_header()
        print(f"\n✓ Successfully loaded {len(records)} cave records")
        
        while True:
            print_menu()
            choice = input("\nEnter your choice (0-4): ").strip()
            
            if choice == '1':
                view_all_caves(records)
            elif choice == '2':
                search_caves(records)
            elif choice == '3':
                count_caves(records)
            elif choice == '4':
                get_cave_by_id(records)
            elif choice == '0':
                print("\n" + "=" * 80)
                print(" " * 25 + "Thank you for using LeniGuide!")
                print(" " * 20 + "Plan your visit to Ajanta & Ellora today!")
                print("=" * 80 + "\n")
                break
            else:
                print("\n❌ Invalid choice. Please enter a number between 0 and 4.")
            
            # Pause before showing menu again
            input("\nPress Enter to continue...")
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure data/sample_records.json exists in the project directory.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print(" " * 30 + "Application interrupted")
        print("=" * 80 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
