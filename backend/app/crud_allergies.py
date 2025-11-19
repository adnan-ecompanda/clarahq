from typing import Optional, List
from datetime import datetime
from .database import get_connection, dict_from_row
from .schemas_allergies import AllergyCreate, AllergyUpdate, AllergyOut
from .audit import log_event


def init_allergy_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS allergies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            allergen TEXT NOT NULL,
            reaction TEXT,
            severity TEXT,
            notes TEXT,

            recorded_by INTEGER,
            recorded_at TEXT DEFAULT (datetime('now')),

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_allergy(data: AllergyCreate) -> AllergyOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO allergies (
            patient_id, allergen, reaction, severity,
            notes, recorded_by
        )
        VALUES (
            :patient_id, :allergen, :reaction, :severity,
            :notes, :recorded_by
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    log_event("create", "allergy", new_id, payload)

    return get_allergy(new_id)


def get_allergy(allergy_id: int) -> Optional[AllergyOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM allergies WHERE id = ?", (allergy_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "allergy", allergy_id)

    return AllergyOut(**dict_from_row(row)) if row else None


def get_allergies_for_patient(patient_id: int) -> List[AllergyOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM allergies
        WHERE patient_id = ? AND active = 1
        ORDER BY created_at DESC
    """, (patient_id,))

    rows = cur.fetchall()
    conn.close()

    log_event("list", "allergy", meta={"patient_id": patient_id, "count": len(rows)})

    return [AllergyOut(**dict_from_row(r)) for r in rows]


def update_allergy(allergy_id: int, data: AllergyUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_allergy(allergy_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = allergy_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE allergies
        SET {set_clause},
            updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    log_event("update", "allergy", allergy_id, payload)

    return get_allergy(allergy_id)


def list_allergies(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM allergies WHERE patient_id = ?", (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "allergy", meta={"patient_id": patient_id, "count": len(rows)})

    return [dict_from_row(r) for r in rows]