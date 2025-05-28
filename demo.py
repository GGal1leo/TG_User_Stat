#!/usr/bin/env python3
"""
IOC Monitor Demo Script
Demonstrates the complete IOC monitoring system functionality
"""

import time
import sys
import os
from database import IOCDatabase

def demo_database():
    """Demonstrate database functionality"""
    print("🗄️ IOC Database Demo")
    print("=" * 50)
    
    # Initialize database
    db = IOCDatabase()
    
    # Show current stats
    stats = db.get_stats()
    print(f"📊 Current Database Stats:")
    for key, value in stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n🎯 Adding demo IOCs...")
    
    # Add some demo IOCs
    demo_iocs = [
        ("192.168.1.100", "ip", "Demo adding IP address"),
        ("malicious-domain.com", "domain", "Demo suspicious domain"),
        ("https://phishing-site.example", "url", "Demo phishing URL"),
        ("10.0.0.1", "ip", "Demo internal IP"),
        ("suspicious.ru", "domain", "Demo Russian domain"),
    ]
    
    for ioc_value, ioc_type, description in demo_iocs:
        success = db.save_ioc(
            ioc_value=ioc_value,
            ioc_type=ioc_type,
            chat_id=999999,
            chat_title="Demo Chat",
            message_id=12345,
            message_content=f"Demo message containing {description}",
            sender_id=123,
            sender_username="demo_user"
        )
        if success:
            print(f"   ✅ Added {ioc_type}: {ioc_value}")
        else:
            print(f"   ⚠️  Duplicate {ioc_type}: {ioc_value}")
    
    # Show updated stats
    print(f"\n📊 Updated Database Stats:")
    updated_stats = db.get_stats()
    for key, value in updated_stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    return db

def demo_search(db):
    """Demonstrate search functionality"""
    print(f"\n🔍 Search Demo")
    print("=" * 50)
    
    # Search for different IOC types
    searches = [
        ("192.168", "IP addresses in 192.168 range"),
        (".com", "All .com domains"),
        ("https://", "All HTTPS URLs"),
        ("demo", "Everything containing 'demo'")
    ]
    
    for search_term, description in searches:
        results = db.search_ioc(search_term)
        print(f"\n🔎 Searching for '{search_term}' ({description}):")
        if results:
            for result in results[:3]:  # Show first 3 results
                print(f"   📌 {result['ioc_type'].upper()}: {result['ioc_value']}")
                print(f"      From: {result['source_chat_title']}")
        else:
            print("   No results found")

def demo_export(db):
    """Demonstrate export functionality"""
    print(f"\n📤 Export Demo")
    print("=" * 50)
    
    export_file = "demo_iocs_export.csv"
    success = db.export_to_csv(export_file)
    
    if success:
        print(f"✅ Successfully exported IOCs to {export_file}")
        
        # Show file size
        if os.path.exists(export_file):
            size = os.path.getsize(export_file)
            print(f"   File size: {size} bytes")
            
            # Show first few lines
            print(f"   Preview of {export_file}:")
            try:
                with open(export_file, 'r') as f:
                    lines = f.readlines()[:5]
                    for i, line in enumerate(lines):
                        print(f"   {i+1}: {line.strip()}")
                    if len(lines) == 5:
                        print("   ...")
            except Exception as e:
                print(f"   Error reading file: {e}")
    else:
        print("❌ Export failed")

def demo_analytics(db):
    """Demonstrate analytics functionality"""
    print(f"\n📈 Analytics Demo")
    print("=" * 50)
    
    # Get unique IOCs by type
    for ioc_type in ['ip', 'domain', 'url']:
        unique_iocs = db.get_unique_iocs(ioc_type)
        print(f"📊 Unique {ioc_type.upper()}s: {len(unique_iocs)}")
        if unique_iocs:
            print(f"   Examples: {', '.join(unique_iocs[:3])}")
            if len(unique_iocs) > 3:
                print(f"   ... and {len(unique_iocs) - 3} more")
    
    # Recent activity
    recent_iocs = db.get_iocs(limit=10)
    print(f"\n📅 Recent Activity (last 10 IOCs):")
    for ioc in recent_iocs:
        print(f"   {ioc['detected_at'][:19]} - {ioc['ioc_type'].upper()}: {ioc['ioc_value']}")

def show_web_gui_info():
    """Show information about the web GUI"""
    print(f"\n🌐 Web GUI Information")
    print("=" * 50)
    print("The web interface is running and provides:")
    print("   📊 Dashboard: http://localhost:5000/")
    print("   📋 IOC List: http://localhost:5000/iocs")
    print("   🔍 Search: http://localhost:5000/search")
    print("   📈 Analytics: http://localhost:5000/analytics")
    print("   📤 Export: http://localhost:5000/export")
    print("\n🎯 Features:")
    print("   • Real-time IOC statistics")
    print("   • Interactive search and filtering")
    print("   • Visual analytics with charts")
    print("   • One-click CSV export")
    print("   • Copy-to-clipboard functionality")
    print("   • Responsive design for mobile/desktop")

def show_cli_info():
    """Show information about CLI tools"""
    print(f"\n💻 Command Line Tools")
    print("=" * 50)
    print("IOC Manager CLI commands:")
    print("   python ioc_manager.py stats          # Show database statistics")
    print("   python ioc_manager.py list           # List recent IOCs")
    print("   python ioc_manager.py search <term>  # Search for specific IOCs")
    print("   python ioc_manager.py export         # Export to CSV")
    print("   python ioc_manager.py unique         # Show unique IOCs")
    print("\nMain monitoring script:")
    print("   python main.py                       # Start Telegram monitoring")

def main():
    """Main demo function"""
    print("🔍 IOC Monitor System Demo")
    print("=" * 60)
    print("This demo showcases the complete IOC monitoring system")
    print("=" * 60)
    
    try:
        # Database demo
        db = demo_database()
        
        # Search demo
        demo_search(db)
        
        # Export demo
        demo_export(db)
        
        # Analytics demo
        demo_analytics(db)
        
        # Show web GUI info
        show_web_gui_info()
        
        # Show CLI info
        show_cli_info()
        
        print(f"\n🎉 Demo Complete!")
        print("=" * 60)
        print("Your IOC monitoring system is ready to use!")
        print("Start with: python main.py (for monitoring)")
        print("Or visit: http://localhost:5000 (for web interface)")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
