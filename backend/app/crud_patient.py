import sqlite3
from typing import Optional, List
from .database import get_connection, dict_from_row
from .schemas_patient import PatientCreate, PatientUpdate, PatientOut


def init_patient_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            gender TEXT,
            phone TEXT,
            email TEXT,

            address_line1 TEXT,
            address_line2 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,

            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            emergency_contact_relationship TEXT,

            insurance_provider TEXT,
            insurance_member_id TEXT,
            insurance_group_number TEXT,

            allergies TEXT,
            medications TEXT,
            chronic_conditions TEXT,

            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_patient(data: PatientCreate) -> PatientOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO patients (
            first_name, last_name, date_of_birth, gender,
            phone, email,
            address_line1, address_line2, city, state, postal_code,
            emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
            insurance_provider, insurance_member_id, insurance_group_number,
            allergies, medications, chronic_conditions,
            active
        )
        VALUES (
            :first_name, :last_name, :date_of_birth, :gender,
            :phone, :email,
            :address_line1, :address_line2, :city, :state, :postal_code,
            :emergency_contact_name, :emergency_contact_phone, :emergency_contact_relationship,
            :insurance_provider, :insurance_member_id, :insurance_group_number,
            :allergies, :medications, :chronic_conditions,
            :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_patient(new_id)


def get_patient(patient_id: int) -> Optional[PatientOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ? AND active = 1", (patient_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None
    return PatientOut(**dict_from_row(row))


def list_patients() -> List[PatientOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE active = 1 ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    return [PatientOut(**dict_from_row(r)) for r in rows]


def update_patient(patient_id: int, data: PatientUpdate) -> Optional[PatientOut]:
    conn = get_connection()
    cur = conn.cursor()

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return get_patient(patient_id)

    set_clause = ", ".join([f"{field} = :{field}" for field in updates])
    updates["id"] = patient_id

    cur.execute(f"""
        UPDATE patients
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, updates)

    conn.commit()
    conn.close()

    return get_patient(patient_id)


def delete_patient(patient_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE patients
        SET active = 0, updated_at = datetime('now')
        WHERE id = ?
    """, (patient_id,))

    conn.commit()
    conn.close()
    return True