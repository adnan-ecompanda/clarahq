from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_billing import (
    BillingCodeCreate, BillingCodeUpdate, BillingCodeOut,
    SuperbillCreate, SuperbillUpdate, SuperbillOut
)

from .audit import log_event   # <-- AUDIT LOGGER IMPORT


# =====================================================
#                INIT TABLES
# =====================================================

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


# =====================================================
#               BILLING CODES CRUD
# =====================================================

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

    log_event("create", "billing_code", new_id, meta=payload)

    return get_billing_code(new_id)


def get_billing_code(code_id: int) -> Optional[BillingCodeOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM billing_codes WHERE id = ?", (code_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "billing_code", code_id)

    return BillingCodeOut(**dict_from_row(row)) if row else None


def list_billing_codes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM billing_codes WHERE active = 1")
    rows = cur.fetchall()
    conn.close()

    log_event("list", "billing_code")

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

    log_event("update", "billing_code", code_id, payload)

    return get_billing_code(code_id)


def delete_billing_code(code_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE billing_codes SET active = 0 WHERE id = ?", (code_id,))
    conn.commit()
    conn.close()

    log_event("delete", "billing_code", code_id)

    return {"status": "deleted"}


# =====================================================
#                 SUPERBILL CRUD
# =====================================================

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

    log_event("create", "superbill", new_id, meta=payload)

    return get_superbill(new_id)


def get_superbill(sb_id: int) -> Optional[SuperbillOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM superbills WHERE id = ?", (sb_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "superbill", sb_id)

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

    log_event("update", "superbill", sb_id, payload)

    return get_superbill(sb_id)


def delete_superbill(sb_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE superbills SET active = 0 WHERE id = ?", (sb_id,))
    conn.commit()
    conn.close()

    log_event("delete", "superbill", sb_id)

    return {"status": "deleted"}


# =====================================================
#          AUTO GENERATE SUPERBILL
# =====================================================

def auto_generate_superbill(encounter_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
    enc = cur.fetchone()
    if not enc:
        return None

    enc = dict_from_row(enc)
    patient_id = enc["patient_id"]
    provider_id = enc["provider_id"]

    # Problems → ICD10
    cur.execute("""
        SELECT icd10_code FROM problems
        WHERE patient_id = ? AND active = 1
    """, (patient_id,))
    rows = cur.fetchall()
    icd10 = rows[0]["icd10_code"] if rows else None

    # Procedures → CPT
    cur.execute("""
        SELECT cpt_code FROM procedures
        WHERE encounter_id = ?
    """, (encounter_id,))
    proc = cur.fetchone()
    cpt = proc["cpt_code"] if proc else None

    # Default CPT from visit type
    if not cpt:
        visit_map = {
            "office_new": "99203",
            "office_established": "99213",
            "consultation": "99242",
            "telehealth": "99423",
            "urgent_care": "99204"
        }

        visit_type = (enc.get("visit_type") or "").lower()
        for k, v in visit_map.items():
            if k in visit_type:
                cpt = v
                break

        if not cpt:
            cpt = "99213"

    cur.execute("""
        INSERT INTO superbills (
            encounter_id, patient_id, provider_id,
            cpt_code, icd10_code, units, modifier, status
        )
        VALUES (?, ?, ?, ?, ?, 1, NULL, 'draft')
    """, (encounter_id, patient_id, provider_id, cpt, icd10))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    log_event("create", "superbill", new_id, meta={"auto_generated": True})

    return get_superbill(new_id)