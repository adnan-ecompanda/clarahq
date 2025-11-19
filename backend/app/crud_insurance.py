import os
import shutil
from datetime import datetime
from fastapi import UploadFile

from .database import get_connection, dict_from_row
from .audit import log_event    # <-- ADDED

UPLOAD_ROOT = "uploads/insurance_cards"


def init_insurance_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS insurance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            payer_name TEXT,
            plan_name TEXT,
            member_id TEXT,
            group_id TEXT,
            relationship TEXT,
            effective_date TEXT,
            expiry_date TEXT,
            phone TEXT,
            payer_address TEXT,
            priority INTEGER DEFAULT 1,
            card_front TEXT,
            card_back TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
#                    FILE UPLOAD
# ============================================================

def save_card_file(patient_id: int, file: UploadFile):
    os.makedirs(f"{UPLOAD_ROOT}/{patient_id}", exist_ok=True)

    timestamp = int(datetime.now().timestamp())
    filename = f"{timestamp}_{file.filename}"
    file_path = f"{UPLOAD_ROOT}/{patient_id}/{filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


# ============================================================
#                    CREATE
# ============================================================

def create_insurance(patient_id: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO insurance (
            patient_id, payer_name, plan_name, member_id, group_id,
            relationship, effective_date, expiry_date, phone, payer_address,
            priority, card_front, card_back, active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        data.get("payer_name"),
        data.get("plan_name"),
        data.get("member_id"),
        data.get("group_id"),
        data.get("relationship"),
        data.get("effective_date"),
        data.get("expiry_date"),
        data.get("phone"),
        data.get("payer_address"),
        data.get("priority", 1),
        data.get("card_front"),
        data.get("card_back"),
        1
    ))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # AUDIT
    log_event("create", "insurance", new_id, meta=data)

    return get_insurance(new_id)


# ============================================================
#                    READ
# ============================================================

def get_insurance(insurance_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM insurance WHERE id = ?", (insurance_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "insurance", insurance_id)

    return dict_from_row(row) if row else None


def get_insurances_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM insurance
        WHERE patient_id = ? AND active = 1
        ORDER BY priority ASC
    """, (patient_id,))

    rows = cur.fetchall()
    conn.close()

    # AUDIT
    log_event("list", "insurance", meta={"patient_id": patient_id})

    return [dict_from_row(r) for r in rows]


# ============================================================
#                    UPDATE
# ============================================================

def update_insurance(insurance_id: int, data: dict):
    conn = get_connection()
    cur = conn.cursor()

    fields = ", ".join([f"{k}=?" for k in data.keys()])
    values = list(data.values()) + [insurance_id]

    cur.execute(f"""
        UPDATE insurance
        SET {fields}, updated_at = datetime('now')
        WHERE id = ?
    """, values)

    conn.commit()
    conn.close()

    # AUDIT
    log_event("update", "insurance", insurance_id, meta=data)

    return get_insurance(insurance_id)


# ============================================================
#                    DELETE (SOFT)
# ============================================================

def deactivate_insurance(insurance_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE insurance
        SET active = 0, updated_at = datetime('now')
        WHERE id = ?
    """, (insurance_id,))

    conn.commit()
    conn.close()

    # AUDIT
    log_event("delete", "insurance", insurance_id)

    return True