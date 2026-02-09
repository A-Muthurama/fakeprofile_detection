import sqlite3
import os
from datetime import datetime

DB_NAME = 'cyberguard.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the reports table"""
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create Reports Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                platform TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                evidence_text TEXT,
                risk_level TEXT DEFAULT 'HIGH',
                reporter_ip TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Index for fast lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON reports (username)')
        
        conn.commit()
        conn.close()
        print(f"Database {DB_NAME} initialized successfully.")

def add_report(username, platform, category, description, evidence, ip_address):
    """Add a new scam report to the DB"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO reports (username, platform, category, description, evidence_text, reporter_ip)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username.lower().strip(), platform, category, description, evidence, ip_address))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        conn.close()

def check_username(username):
    """Check if a username has been reported"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rows = cursor.execute('SELECT * FROM reports WHERE username = ?', (username.lower().strip(),)).fetchall()
    conn.close()
    
    if not rows:
        return None
        
    # Aggregate data
    return {
        'is_flagged': True,
        'report_count': len(rows),
        'last_reported': rows[-1]['timestamp'],
        'categories': list(set([row['category'] for row in rows])),
        'risk_level': 'CRITICAL'
    }

def get_recent_reports(limit=10):
    """Get the latest reports for the live ticker"""
    conn = get_db_connection()
    reports = conn.execute('SELECT username, category, timestamp FROM reports ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in reports]

# Initialize on module load check? No, call explicitly.
