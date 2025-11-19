import sqlite3
from .database import get_connection
from datetime import datetime

def init_audit_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            entity_type TEXT,
            entity_id INTEGER,
            meta TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def log_event(event_type, entity_type, entity_id=None, meta=None):
    """Unified logger for all CRUD audit entries."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO audit_log (event_type, entity_type, entity_id, meta)
        VALUES (?, ?, ?, ?)
    """, (
        event_type,
        entity_type,
        entity_id,
        str(meta) if meta else None
    ))

    conn.commit()
    conn.close()