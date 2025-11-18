import os
import shutil
from datetime import datetime
from fastapi import UploadFile

from .database import get_connection, dict_from_row

UPLOAD_ROOT = "uploads/portal_messages"


def init_portal_message_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS portal_message_threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER,
            subject TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS portal_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            sender_type TEXT NOT NULL,
            sender_id INTEGER NOT NULL,
            content TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS portal_message_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            uploaded_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# THREADS ------------------------------------------

def create_thread(patient_id: int, provider_id: int, subject: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO portal_message_threads (patient_id, provider_id, subject)
        VALUES (?, ?, ?)
    """, (patient_id, provider_id, subject))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_thread(new_id)


def get_thread(thread_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM portal_message_threads WHERE id = ?", (thread_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None


def list_threads_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM portal_message_threads
        WHERE patient_id = ?
        ORDER BY updated_at DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


# MESSAGES ------------------------------------------

def send_message(thread_id: int, sender_type: str, sender_id: int, content: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO portal_messages (thread_id, sender_type, sender_id, content)
        VALUES (?, ?, ?, ?)
    """, (thread_id, sender_type, sender_id, content))

    conn.commit()
    new_id = cur.lastrowid

    # Update thread timestamp
    cur.execute("""
        UPDATE portal_message_threads
        SET updated_at = datetime('now')
        WHERE id = ?
    """, (thread_id,))
    conn.commit()

    conn.close()
    return get_message(new_id)


def get_message(message_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM portal_messages WHERE id = ?", (message_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None


def get_messages(thread_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM portal_messages
        WHERE thread_id = ?
        ORDER BY created_at ASC
    """, (thread_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def mark_message_read(message_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE portal_messages
        SET is_read = 1
        WHERE id = ?
    """, (message_id,))
    conn.commit()
    conn.close()
    return {"status": "read"}


# ATTACHMENTS ------------------------------------------

def save_attachment_file(message_id: int, file: UploadFile):
    os.makedirs(UPLOAD_ROOT, exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    fname = f"{timestamp}_{file.filename}"
    path = f"{UPLOAD_ROOT}/{fname}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return fname, path, file.content_type, os.path.getsize(path)


def add_message_attachment(message_id: int, file: UploadFile):
    filename, filepath, filetype, filesize = save_attachment_file(message_id, file)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO portal_message_attachments (
            message_id, file_name, file_path, file_type, file_size
        )
        VALUES (?, ?, ?, ?, ?)
    """, (message_id, filename, filepath, filetype, filesize))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return {
        "id": new_id,
        "message_id": message_id,
        "file_name": filename,
        "file_path": filepath
    }