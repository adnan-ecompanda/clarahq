from typing import Dict, Any, List
from .database import get_connection, dict_from_row
from .schemas_billing import SuperbillCreate
from reportlab.pdfgen import canvas
import io
import base64


# ------------------------
# INIT TABLES
# ------------------------

def init_superbill_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def init_superbill_cpt_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbill_cpt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            superbill_id INTEGER NOT NULL,
            cpt_code TEXT NOT NULL,
            units INTEGER DEFAULT 1,
            amount REAL DEFAULT 0,
            modifier TEXT,
            icd_pointer TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (superbill_id) REFERENCES superbills(id)
        )
    """)
    conn.commit()
    conn.close()


def init_superbill_icd_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbill_icd_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            superbill_id INTEGER NOT NULL,
            icd_code TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (superbill_id) REFERENCES superbills(id)
        )
    """)
    conn.commit()
    conn.close()


# ------------------------
# CREATE SUPERBILL
# ------------------------

def create_superbill(data: SuperbillCreate) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO superbills (
            encounter_id, patient_id, provider_id,
            notes, status, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        data.encounter_id,
        data.patient_id,
        data.provider_id,
        data.notes,
        data.status
    ))

    sb_id = cur.lastrowid

    # CPT items
    for item in data.cpt_items:
        cur.execute("""
            INSERT INTO superbill_cpt_items (
                superbill_id, cpt_code, units, amount, modifier,
                icd_pointer, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            sb_id,
            item.cpt_code,
            item.units,
            item.amount,
            item.modifier,
            item.icd_pointer
        ))

    # ICD items
    for item in data.icd_items:
        cur.execute("""
            INSERT INTO superbill_icd_items (
                superbill_id, icd_code, description, created_at
            )
            VALUES (?, ?, ?, datetime('now'))
        """, (sb_id, item.icd_code, item.description))

    conn.commit()
    conn.close()

    return get_superbill_by_id(sb_id)


# ------------------------
# GET SUPERBILL
# ------------------------

def get_superbill_by_id(sb_id: int) -> Dict[str, Any] | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM superbills WHERE id = ?", (sb_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    sb = dict_from_row(row)

    cur.execute("""
        SELECT cpt_code, units, amount, modifier, icd_pointer
        FROM superbill_cpt_items WHERE superbill_id = ?
    """, (sb_id,))
    sb["cpt_items"] = [dict_from_row(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT icd_code, description
        FROM superbill_icd_items WHERE superbill_id = ?
    """, (sb_id,))
    sb["icd_items"] = [dict_from_row(r) for r in cur.fetchall()]

    conn.close()
    return sb


# ------------------------
# LIST SUPERBILLS
# ------------------------

def list_superbills() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM superbills ORDER BY id DESC")
    ids = [r["id"] for r in cur.fetchall()]

    conn.close()
    return [get_superbill_by_id(sb_id) for sb_id in ids]


# ------------------------
# STATUS UPDATE
# ------------------------

def update_superbill_status(sb_id: int, status: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE superbills
        SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (status, sb_id))

    conn.commit()
    conn.close()

    return get_superbill_by_id(sb_id)