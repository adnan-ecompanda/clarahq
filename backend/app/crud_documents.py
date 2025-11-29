import os
import shutil
from datetime import datetime
from fastapi import UploadFile
from .database import get_connection, dict_from_row
from .schemas_documents import DocumentOut
import base64
import re
import sqlite3

UPLOAD_ROOT = "uploads/patient_docs"


def init_document_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            uploaded_by INTEGER NOT NULL,
            category TEXT,
            title TEXT,
            description TEXT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            uploaded_at TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            uploaded_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def save_document_file(patient_id: int, file: UploadFile):
    os.makedirs(f"{UPLOAD_ROOT}/{patient_id}", exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    filename = f"{timestamp}_{file.filename}"
    file_path = f"{UPLOAD_ROOT}/{patient_id}/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename, file_path, file.content_type, os.path.getsize(file_path)


def create_document(patient_id: int, user_id: int, category: str, title: str,
                    description: str, file: UploadFile):

    filename, filepath, filetype, filesize = save_document_file(patient_id, file)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO patient_documents (
            patient_id, uploaded_by, category, title, description,
            file_name, file_path, file_type, file_size
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, user_id, category, title, description,
          filename, filepath, filetype, filesize))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_document(new_id)


def get_document(doc_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patient_documents WHERE id = ?", (doc_id,))
    row = cur.fetchone()
    conn.close()

    return DocumentOut(**dict_from_row(row)) if row else None


def get_documents_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM patient_documents
        WHERE patient_id = ? AND active = 1
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    return [DocumentOut(**dict_from_row(r)) for r in rows]

UPLOAD_ROOT = os.path.abspath("uploads")
DOC_DIR = os.path.join(UPLOAD_ROOT, "documents")
os.makedirs(DOC_DIR, exist_ok=True)


# Clean base64 before decoding
def clean_b64(data: str) -> str:
    data = re.sub(r"^data:[a-zA-Z0-9\/\-\+\.]+;base64,", "", data)
    data = re.sub(r"\s+", "", data)
    pad = len(data) % 4
    if pad:
        data += "=" * (4 - pad)
    return data


def upload_document_base64(data):
    conn = get_connection()
    cur = conn.cursor()

    # Decode file
    cleaned = clean_b64(data.base64_data)
    file_bytes = base64.b64decode(cleaned)

    ext = data.file_type.lower().replace(".", "")
    safe_name = f"{datetime.now().timestamp()}_{data.file_name}"

    file_path = os.path.join(DOC_DIR, safe_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Insert DB record
    cur.execute("""
        INSERT INTO patient_documents (patient_id, file_name, file_type, file_size, file_path)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.patient_id,
        data.file_name,
        ext,
        len(file_bytes),
        safe_name
    ))

    conn.commit()

    return {"status": "uploaded", "document_id": cur.lastrowid}


def list_documents_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, patient_id, file_name, file_type, file_size, file_path, uploaded_at
        FROM patient_documents
        WHERE patient_id = ?
        ORDER BY uploaded_at DESC
    """, (patient_id,))

    rows = cur.fetchall()
    keys = ["id", "patient_id", "file_name", "file_type", "file_size",
            "file_path", "uploaded_at"]

    return [dict(zip(keys, r)) for r in rows]


def get_document_file(doc_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT file_path FROM patient_documents WHERE id = ?
    """, (doc_id,))

    row = cur.fetchone()
    if not row:
        return None

    file_path = os.path.join(DOC_DIR, row[0])
    if not os.path.exists(file_path):
        return None

    return file_path