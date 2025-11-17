import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from .database import get_connection, dict_from_row

UPLOAD_ROOT = "uploads/messages"


def init_message_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Conversations container
    cur.execute("""
        CREATE TABLE IF NOT EXISTS message_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_by INTEGER NOT NULL,
            participant_a INTEGER NOT NULL,
            participant_b INTEGER NOT NULL,
            subject TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            last_message_at TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'open'
        )
    """)

    # Individual messages
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message_text TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Attachments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS message_attachments (
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


# ------------------------------------
# FILE SAVE
# ------------------------------------

def save_message_file(conversation_id: int, file: UploadFile):
    os.makedirs(f"{UPLOAD_ROOT}/{conversation_id}", exist_ok=True)

    ts = int(datetime.now().timestamp())
    file_name = f"{ts}_{file.filename}"
    file_path = f"{UPLOAD_ROOT}/{conversation_id}/{file_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_name, file_path, file.content_type, os.path.getsize(file_path)


# ------------------------------------
# CRUD OPERATIONS
# ------------------------------------

def create_conversation(created_by: int, a: int, b: int, subject: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO message_conversations (created_by, participant_a, participant_b, subject)
        VALUES (?, ?, ?, ?)
    """, (created_by, a, b, subject))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_conversation(new_id)


def get_conversation(conv_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM message_conversations WHERE id = ?", (conv_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None


def list_conversations_for_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM message_conversations
        WHERE participant_a = ? OR participant_b = ?
        ORDER BY last_message_at DESC
    """, (user_id, user_id))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def create_message(conversation_id: int, sender_id: int, text: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO messages (conversation_id, sender_id, message_text)
        VALUES (?, ?, ?)
    """, (conversation_id, sender_id, text))

    cur.execute("""
        UPDATE message_conversations
        SET last_message_at = datetime('now')
        WHERE id = ?
    """, (conversation_id,))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_message(new_id)


def get_message(msg_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None


def list_messages(conversation_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
    """, (conversation_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def attach_file(message_id: int, file: UploadFile, conversation_id: int):
    filename, filepath, filetype, filesize = save_message_file(conversation_id, file)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO message_attachments 
        (message_id, file_name, file_path, file_type, file_size)
        VALUES (?, ?, ?, ?, ?)
    """, (message_id, filename, filepath, filetype, filesize))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_attachment(new_id)


def get_attachment(attachment_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM message_attachments WHERE id = ?", (attachment_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None