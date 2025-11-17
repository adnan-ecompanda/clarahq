from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_billing import (
    BillingCodeCreate, BillingCodeUpdate, BillingCodeOut,
    SuperbillCreate, SuperbillUpdate, SuperbillOut
)

# ------------------ CREATE TABLES ------------------

def init_billing_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS billing_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            code_type TEXT NOT NULL,
            description TEXT,
            amount REAL DEFAULT 0.0,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,

            cpt_code TEXT,
            icd10_code TEXT,

            units INTEGER DEFAULT 1,
            modifier TEXT,
            notes TEXT,

            status TEXT DEFAULT 'draft',
            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ------------------ BILLING CODES CRUD ------------------

def create_billing_code(data: BillingCodeCreate) -> BillingCodeOut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()

    cur.execute("""
        INSERT INTO billing_codes (code, code_type, description, amount, active)
        VALUES (:code, :code_type, :description, :amount, :active)
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_billing_code(new_id)


def get_billing_code(code_id: int) -> Optional[BillingCodeOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM billing_codes WHERE id = ?", (code_id,))
    row = cur.fetchone()
    conn.close()
    return BillingCodeOut(**dict_from_row(row)) if row else None


def list_billing_codes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM billing_codes WHERE active = 1")
    rows = cur.fetchall()
    conn.close()
    return [BillingCodeOut(**dict_from_row(r)) for r in rows]


def update_billing_code(code_id: int, data: BillingCodeUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_billing_code(code_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = code_id

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE billing_codes SET {set_clause}, updated_at = datetime('now') WHERE id = :id", payload)
    conn.commit()
    conn.close()

    return get_billing_code(code_id)


def delete_billing_code(code_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billing_codes SET active = 0 WHERE id = ?", (code_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}


# ------------------ SUPERBILL CRUD ------------------

def create_superbill(data: SuperbillCreate) -> SuperbillOut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()

    cur.execute("""
        INSERT INTO superbills (
            encounter_id, patient_id, provider_id,
            cpt_code, icd10_code, units, modifier, notes,
            status, active
        )
        VALUES (
            :encounter_id, :patient_id, :provider_id,
            :cpt_code, :icd10_code, :units, :modifier, :notes,
            :status, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_superbill(new_id)


def get_superbill(sb_id: int) -> Optional[SuperbillOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM superbills WHERE id = ?", (sb_id,))
    row = cur.fetchone()
    conn.close()
    return SuperbillOut(**dict_from_row(row)) if row else None


def update_superbill(sb_id: int, data: SuperbillUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_superbill(sb_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = sb_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE superbills
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    return get_superbill(sb_id)


def delete_superbill(sb_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE superbills SET active = 0 WHERE id = ?", (sb_id,))
    conn.commit()
    conn.close()

    return {"status": "deleted"}