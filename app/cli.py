"""
Command-line interface for LeniGuide records
"""

import argparse
import json
import sys
from pathlib import Path

from app.records import load_records, search, count_by, get_by_id


def cmd_list(args):
    """List all records or with a limit"""
    records = load_records(args.file)
    
    limit = args.limit if args.limit else len(records)
    for i, record in enumerate(records[:limit]):
        print(f"{record['id']:20} | {record['site']:8} | Cave {record['cave_no']:3} | {record['religion_period']}")
    
    print(f"\nShowing {min(limit, len(records))} of {len(records)} records")


def cmd_search(args):
    """Search records by keyword"""
    records = load_records(args.file)
    results = search(args.query, records)
    
    if not results:
        print(f"No results found for '{args.query}'")
        return
    
    print(f"Found {len(results)} result(s) for '{args.query}':\n")
    for record in results:
        print(f"ID: {record['id']}")
        print(f"Site: {record['site'].title()}, Cave: {record['cave_no']}")
        print(f"Period: {record['religion_period']}")
        print(f"Highlights: {record['highlights'][:150]}...")
        print()


def cmd_count(args):
    """Count records by field"""
    records = load_records(args.file)
    counts = count_by(args.by, records)
    
    print(f"Counts by '{args.by}':")
    for key, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {key:40} : {count}")
    print(f"\nTotal: {sum(counts.values())} records")


def cmd_get(args):
    """Get a single record by ID"""
    records = load_records(args.file)
    record = get_by_id(args.id, records)
    
    if not record:
        print(f"Record '{args.id}' not found")
        sys.exit(1)
    
    print(json.dumps(record, indent=2))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LeniGuide Records CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-f', '--file',
        type=Path,
        help='Path to records JSON file (default: data/sample_records.json)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # list command
    parser_list = subparsers.add_parser('list', help='List all records')
    parser_list.add_argument('-l', '--limit', type=int, help='Maximum number of records to show')
    parser_list.set_defaults(func=cmd_list)
    
    # search command
    parser_search = subparsers.add_parser('search', help='Search records by keyword')
    parser_search.add_argument('query', help='Search query')
    parser_search.set_defaults(func=cmd_search)
    
    # count command
    parser_count = subparsers.add_parser('count', help='Count records by field')
    parser_count.add_argument('--by', default='site', help='Field to count by (default: site)')
    parser_count.set_defaults(func=cmd_count)
    
    # get command
    parser_get = subparsers.add_parser('get', help='Get record by ID')
    parser_get.add_argument('id', help='Record ID')
    parser_get.set_defaults(func=cmd_get)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
