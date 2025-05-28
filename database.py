#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class IOCDatabase:
    def __init__(self, db_path: str = "ioc_database.db"):
        """Initialize the IOC database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the database and tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create IOCs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS iocs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ioc_value TEXT NOT NULL,
                    ioc_type TEXT NOT NULL,
                    source_chat_id INTEGER,
                    source_chat_title TEXT,
                    source_message_id INTEGER,
                    message_content TEXT,
                    sender_id INTEGER,
                    sender_username TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ioc_value, ioc_type, source_message_id)
                )
            ''')
            
            # Create index for faster searches
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ioc_value ON iocs (ioc_value)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ioc_type ON iocs (ioc_type)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_detected_at ON iocs (detected_at)
            ''')
            
            conn.commit()
    
    def save_ioc(self, ioc_value: str, ioc_type: str, chat_id: Optional[int] = None, 
                 chat_title: Optional[str] = None, message_id: Optional[int] = None,
                 message_content: Optional[str] = None, sender_id: Optional[int] = None,
                 sender_username: Optional[str] = None) -> bool:
        """
        Save an IOC to the database.
        
        Args:
            ioc_value: The IOC value (IP, domain, URL)
            ioc_type: Type of IOC ('ip', 'domain', 'url')
            chat_id: Telegram chat ID where the IOC was found
            chat_title: Telegram chat title
            message_id: Telegram message ID
            message_content: Full message content
            sender_id: Sender's user ID
            sender_username: Sender's username
            
        Returns:
            bool: True if saved successfully, False if duplicate
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO iocs 
                    (ioc_value, ioc_type, source_chat_id, source_chat_title, 
                     source_message_id, message_content, sender_id, sender_username)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ioc_value, ioc_type, chat_id, chat_title, message_id, 
                      message_content, sender_id, sender_username))
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_iocs(self, ioc_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve IOCs from the database.
        
        Args:
            ioc_type: Filter by IOC type ('ip', 'domain', 'url')
            limit: Maximum number of results
            
        Returns:
            List of IOC records as dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if ioc_type:
                    cursor.execute('''
                        SELECT * FROM iocs 
                        WHERE ioc_type = ? 
                        ORDER BY detected_at DESC 
                        LIMIT ?
                    ''', (ioc_type, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM iocs 
                        ORDER BY detected_at DESC 
                        LIMIT ?
                    ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_unique_iocs(self, ioc_type: Optional[str] = None) -> List[str]:
        """Get unique IOC values."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if ioc_type:
                    cursor.execute('''
                        SELECT DISTINCT ioc_value FROM iocs 
                        WHERE ioc_type = ? 
                        ORDER BY ioc_value
                    ''', (ioc_type,))
                else:
                    cursor.execute('''
                        SELECT DISTINCT ioc_value FROM iocs 
                        ORDER BY ioc_value
                    ''')
                
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total IOCs
                cursor.execute('SELECT COUNT(*) FROM iocs')
                stats['total_iocs'] = cursor.fetchone()[0]
                
                # IOCs by type
                cursor.execute('''
                    SELECT ioc_type, COUNT(*) 
                    FROM iocs 
                    GROUP BY ioc_type
                ''')
                for ioc_type, count in cursor.fetchall():
                    stats[f'{ioc_type}_count'] = count
                
                # Unique IOCs
                cursor.execute('SELECT COUNT(DISTINCT ioc_value) FROM iocs')
                stats['unique_iocs'] = cursor.fetchone()[0]
                
                return stats
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
    
    def search_ioc(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for IOCs containing the search term."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM iocs 
                    WHERE ioc_value LIKE ? 
                    ORDER BY detected_at DESC
                ''', (f'%{search_term}%',))
                
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def export_to_csv(self, filename: str = "iocs_export.csv") -> bool:
        """Export IOCs to CSV file."""
        try:
            import csv
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM iocs ORDER BY detected_at DESC')
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        'ID', 'IOC Value', 'IOC Type', 'Chat ID', 'Chat Title',
                        'Message ID', 'Message Content', 'Sender ID', 'Sender Username',
                        'Detected At'
                    ])
                    
                    # Write data
                    writer.writerows(cursor.fetchall())
                
                return True
        except Exception as e:
            print(f"Export error: {e}")
            return False


if __name__ == "__main__":
    # Test the database
    db = IOCDatabase()
    print("Database initialized successfully!")
    
    # Test saving some sample data
    db.save_ioc("192.168.1.1", "ip", 123456, "Test Chat", 789, "Test message", 111, "testuser")
    db.save_ioc("example.com", "domain", 123456, "Test Chat", 790, "Another message", 111, "testuser")
    db.save_ioc("https://malicious.com", "url", 123456, "Test Chat", 791, "URL message", 111, "testuser")
    
    print("Sample data saved!")
    print("Stats:", db.get_stats())
