import sqlite3
from datetime import datetime
from .database import get_connection, dict_from_row

def init_notification_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT,
            type TEXT,      -- appointment, task, message, lab, imaging, portal_msg, billing
            ref_id INTEGER, -- appointment_id, task_id, etc.
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notification_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email_enabled INTEGER DEFAULT 1,
            sms_enabled INTEGER DEFAULT 0,
            push_enabled INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def create_notification(user_id: int, title: str, message: str, type: str, ref_id: int = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO notifications (user_id, title, message, type, ref_id)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, title, message, type, ref_id))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_notification(new_id)
def get_notification(notification_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notifications WHERE id = ?", (notification_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None

def list_notifications(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]

def mark_notification_read(notification_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notifications SET is_read = 1 WHERE id = ?
    """, (notification_id,))
    conn.commit()
    conn.close()
    return {"status": "read"}

def mark_all_read(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notifications SET is_read = 1 WHERE user_id = ?
    """, (user_id,))
    conn.commit()
    conn.close()
    return {"status": "all_read"}

def count_unread(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) AS count
        FROM notifications
        WHERE user_id = ? AND is_read = 0
    """, (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return {"unread": count}