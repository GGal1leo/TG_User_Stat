#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime
from database import IOCDatabase


def print_table(data, headers):
    """Print data in a simple table format."""
    if not data:
        print("No data found.")
        return
    
    # Calculate column widths
    widths = [len(str(header)) for header in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    header_row = " | ".join(f"{header:<{widths[i]}}" for i, header in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print data
    for row in data:
        data_row = " | ".join(f"{str(cell):<{widths[i]}}" for i, cell in enumerate(row))
        print(data_row)


def main():
    parser = argparse.ArgumentParser(description="IOC Database Management Tool")
    parser.add_argument("--db", default="ioc_database.db", help="Database file path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List IOCs")
    list_parser.add_argument("--type", choices=["ip", "domain", "url"], help="Filter by IOC type")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of results")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search IOCs")
    search_parser.add_argument("term", help="Search term")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export IOCs to CSV")
    export_parser.add_argument("--output", default="iocs_export.csv", help="Output CSV file")
    
    # Unique command
    unique_parser = subparsers.add_parser("unique", help="List unique IOCs")
    unique_parser.add_argument("--type", choices=["ip", "domain", "url"], help="Filter by IOC type")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        db = IOCDatabase(args.db)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    if args.command == "stats":
        stats = db.get_stats()
        print("📊 IOC Database Statistics:")
        print("=" * 30)
        for key, value in stats.items():
            formatted_key = key.replace("_", " ").title()
            print(f"{formatted_key}: {value}")
    
    elif args.command == "list":
        iocs = db.get_iocs(ioc_type=args.type, limit=args.limit)
        print(f"📋 Latest IOCs ({args.type or 'all types'}):")
        print("=" * 50)
        
        if iocs:
            headers = ["IOC Value", "Type", "Chat", "Detected At"]
            data = []
            for ioc in iocs:
                detected_at = datetime.fromisoformat(ioc['detected_at']).strftime("%Y-%m-%d %H:%M")
                chat_info = ioc['source_chat_title'] or f"ID:{ioc['source_chat_id']}"
                data.append([ioc['ioc_value'], ioc['ioc_type'], chat_info, detected_at])
            
            print_table(data, headers)
        else:
            print("No IOCs found.")
    
    elif args.command == "search":
        results = db.search_ioc(args.term)
        print(f"🔍 Search results for '{args.term}':")
        print("=" * 50)
        
        if results:
            headers = ["IOC Value", "Type", "Chat", "Message", "Detected At"]
            data = []
            for result in results:
                detected_at = datetime.fromisoformat(result['detected_at']).strftime("%Y-%m-%d %H:%M")
                chat_info = result['source_chat_title'] or f"ID:{result['source_chat_id']}"
                message = (result['message_content'][:50] + "...") if len(result['message_content']) > 50 else result['message_content']
                data.append([result['ioc_value'], result['ioc_type'], chat_info, message, detected_at])
            
            print_table(data, headers)
        else:
            print("No matching IOCs found.")
    
    elif args.command == "export":
        success = db.export_to_csv(args.output)
        if success:
            print(f"✅ IOCs exported successfully to {args.output}")
        else:
            print("❌ Export failed")
    
    elif args.command == "unique":
        unique_iocs = db.get_unique_iocs(ioc_type=args.type)
        print(f"🎯 Unique IOCs ({args.type or 'all types'}):")
        print("=" * 50)
        
        if unique_iocs:
            for ioc in unique_iocs:
                print(ioc)
            print(f"\nTotal: {len(unique_iocs)} unique IOCs")
        else:
            print("No unique IOCs found.")


if __name__ == "__main__":
    main()
