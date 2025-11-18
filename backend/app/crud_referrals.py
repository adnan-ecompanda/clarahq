import os
import shutil
from datetime import datetime
from fastapi import UploadFile

from .database import get_connection, dict_from_row

UPLOAD_ROOT = "uploads/referrals"


def init_referral_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Main referral table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            encounter_id INTEGER,
            provider_id INTEGER NOT NULL,

            referral_type TEXT,          -- cardiology, imaging, lab, PT, etc.
            referred_to TEXT,            -- doctor/clinic name
            specialty TEXT,
            reason TEXT,
            clinical_summary TEXT,

            status TEXT DEFAULT 'pending',  -- pending, sent, accepted, completed, cancelled

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1
        )
    """)

    # Referral activity log (status timeline)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS referral_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referral_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            note TEXT,
            changed_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Attachments (optional)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS referral_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referral_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            uploaded_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# CRUD HELPERS
# -----------------------------

def create_referral(payload):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO referrals (
            patient_id, encounter_id, provider_id,
            referral_type, referred_to, specialty,
            reason, clinical_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.patient_id,
        payload.encounter_id,
        payload.provider_id,
        payload.referral_type,
        payload.referred_to,
        payload.specialty,
        payload.reason,
        payload.clinical_summary
    ))

    new_id = cur.lastrowid

    # Add first log entry
    cur.execute("""
        INSERT INTO referral_logs (referral_id, status, note)
        VALUES (?, 'pending', 'Referral created')
    """, (new_id,))

    conn.commit()
    conn.close()

    return get_referral(new_id)


def get_referral(referral_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM referrals WHERE id = ?", (referral_id,))
    row = cur.fetchone()
    conn.close()
    return dict_from_row(row) if row else None


def list_referrals_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM referrals 
                   WHERE patient_id = ? AND active = 1""",
                (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def update_referral_status(referral_id: int, status: str, note: str = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE referrals
        SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (status, referral_id))

    cur.execute("""
        INSERT INTO referral_logs (referral_id, status, note)
        VALUES (?, ?, ?)
    """, (referral_id, status, note))

    conn.commit()
    conn.close()

    return get_referral(referral_id)


def get_referral_logs(referral_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM referral_logs
        WHERE referral_id = ?
        ORDER BY changed_at ASC
    """, (referral_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


# -----------------------------
# Attachments
# -----------------------------

def save_attachment_file(referral_id: int, file: UploadFile):
    os.makedirs(f"{UPLOAD_ROOT}/{referral_id}", exist_ok=True)

    ts = int(datetime.now().timestamp())
    filename = f"{ts}_{file.filename}"
    file_path = f"{UPLOAD_ROOT}/{referral_id}/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename, file_path, file.content_type, os.path.getsize(file_path)


def add_referral_attachment(referral_id: int, file: UploadFile):
    fname, fpath, ftype, fsize = save_attachment_file(referral_id, file)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO referral_attachments (
            referral_id, file_name, file_path, file_type, file_size
        )
        VALUES (?, ?, ?, ?, ?)
    """, (referral_id, fname, fpath, ftype, fsize))

    conn.commit()
    conn.close()

    return {"file_name": fname, "file_path": fpath}