import os
import sqlite3
from datetime import datetime
from fastapi import UploadFile

from .database import get_connection

UPLOAD_ROOT = os.path.abspath("uploads")
INS_CARD_DIR = os.path.join(UPLOAD_ROOT, "insurance_cards")

os.makedirs(INS_CARD_DIR, exist_ok=True)


def init_insurance_card_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS insurance_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        payer_name TEXT,
        plan_name TEXT,
        member_id TEXT,
        group_id TEXT,
        relationship TEXT,
        effective_date TEXT,
        expiry_date TEXT,
        priority TEXT,
        payer_phone TEXT,
        payer_address TEXT,
        
        card_front TEXT,
        card_back TEXT,

        status TEXT DEFAULT 'active',

        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT
    )
    """)

    conn.commit()

def save_uploaded_file(file: UploadFile, prefix: str):
    ext = file.filename.split(".")[-1]
    filename = f"{prefix}_{datetime.now().timestamp()}.{ext}"
    path = os.path.join(INS_CARD_DIR, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path


def create_insurance_card(data, front_file: UploadFile = None, back_file: UploadFile = None):
    front_path = save_uploaded_file(front_file, "front") if front_file else None
    back_path = save_uploaded_file(back_file, "back") if back_file else None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO insurance_cards
    (patient_id, payer_name, plan_name, member_id, group_id,
     relationship, effective_date, expiry_date, priority,
     payer_phone, payer_address, card_front, card_back, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.patient_id, data.payer_name, data.plan_name, data.member_id, data.group_id,
        data.relationship, data.effective_date, data.expiry_date, data.priority,
        data.payer_phone, data.payer_address, front_path, back_path, "active"
    ))

    conn.commit()
    return {"id": cur.lastrowid, "message": "Insurance card added successfully"}


def list_insurance_cards(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM insurance_cards WHERE patient_id=?", (patient_id,))
    rows = cur.fetchall()

    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def get_insurance_card(card_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM insurance_cards WHERE id=?", (card_id,))
    row = cur.fetchone()

    if not row:
        return None

    cols = [c[0] for c in cur.description]
    return dict(zip(cols, row))