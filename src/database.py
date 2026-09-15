import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

# Setup SQLite database path in data folder
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "agrismart_history.db"

def init_db():
    """Initializes the SQLite database with required tables."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            image_filename TEXT,
            class_label TEXT,
            confidence REAL,
            precaution TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(image_filename, class_label, confidence, precaution):
    """Saves a prediction result to the history database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO scan_history (timestamp, image_filename, class_label, confidence, precaution)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, image_filename, class_label, confidence, precaution))
    
    conn.commit()
    history_id = cursor.lastrowid
    conn.close()
    
    return history_id

def get_history(limit=50):
    """Retrieves the most recent predictions from the history database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM scan_history
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# Initialize DB on import
init_db()
