# app/crud_scraper.py
import sqlite3
from .database import get_connection, dict_from_row

def init_scraper_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scraper_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payer TEXT,
        username TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scraper_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        event TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scraper_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        result_type TEXT,
        payload TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_scraper_session(payer: str, username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO scraper_sessions (payer, username, status)
        VALUES (?, ?, 'STARTED')
    """, (payer, username))
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return session_id


def log_scraper_event(session_id: int, event: str, details: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO scraper_logs (session_id, event, details)
        VALUES (?, ?, ?)
    """, (session_id, event, details))
    conn.commit()
    conn.close()


def save_scraper_result(session_id: int, result_type: str, payload: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO scraper_results (session_id, result_type, payload)
        VALUES (?, ?, ?)
    """, (session_id, result_type, payload))
    conn.commit()
    conn.close()