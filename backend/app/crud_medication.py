import sqlite3
from typing import Optional
from datetime import datetime
from .database import get_connection, dict_from_row
from .schemas_medication import (
    MedicationCreate, MedicationUpdate, MedicationOut
)

def init_medication_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            encounter_id INTEGER,

            medication_name TEXT NOT NULL,
            strength TEXT,
            route TEXT,
            frequency TEXT,
            duration TEXT,
            quantity TEXT,
            refills INTEGER,
            instructions TEXT,

            allergy_checked INTEGER DEFAULT 0,
            drug_interaction_checked INTEGER DEFAULT 0,

            status TEXT DEFAULT 'active',

            approved_by INTEGER,
            approved_at TEXT,

            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def create_medication_order(data: MedicationCreate) -> MedicationOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO medications (
            patient_id, provider_id, encounter_id,
            medication_name, strength, route, frequency,
            duration, quantity, refills, instructions,
            allergy_checked, drug_interaction_checked,
            status, approved_by, approved_at, active
        )
        VALUES (
            :patient_id, :provider_id, :encounter_id,
            :medication_name, :strength, :route, :frequency,
            :duration, :quantity, :refills, :instructions,
            :allergy_checked, :drug_interaction_checked,
            :status, :approved_by, :approved_at, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_medication_order(new_id)


def get_medication_order(order_id: int) -> Optional[MedicationOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM medications WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return MedicationOut(**dict_from_row(row)) if row else None


def update_medication_order(order_id: int, data: MedicationUpdate) -> MedicationOut:
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not payload:
        return get_medication_order(order_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = order_id

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE medications SET {set_clause}, updated_at = datetime('now') WHERE id = :id",
        payload
    )
    conn.commit()
    conn.close()

    return get_medication_order(order_id)