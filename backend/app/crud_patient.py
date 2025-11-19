from typing import Optional, List
from .database import get_connection, dict_from_row
from .schemas_patient import PatientCreate, PatientUpdate, PatientOut
from .audit import log_event
from .security import hash_password

def init_patient_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            phone_primary TEXT,
            email TEXT,

            address_line1 TEXT,
            address_line2 TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,

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
            first_name, last_name, dob, gender,
            phone_primary, email,
            address_line1, address_line2, city, state, zip_code,
            emergency_contact_name, emergency_contact_phone, emergency_contact_relationship,
            insurance_provider, insurance_member_id, insurance_group_number,
            allergies, medications, chronic_conditions, active
        )
        VALUES (
            :first_name, :last_name, :dob, :gender,
            :phone_primary, :email,
            :address_line1, :address_line2, :city, :state, :zip_code,
            :emergency_contact_name, :emergency_contact_phone, :emergency_contact_relationship,
            :insurance_provider, :insurance_member_id, :insurance_group_number,
            :allergies, :medications, :chronic_conditions, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    log_event("create", "patient", new_id, payload)

    return get_patient(new_id)


def get_patient(patient_id: int) -> Optional[PatientOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ? AND active = 1", (patient_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "patient", patient_id)

    return PatientOut(**dict_from_row(row)) if row else None


def list_patients() -> List[PatientOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE active = 1 ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    log_event("list", "patient", meta={"count": len(rows)})

    return [PatientOut(**dict_from_row(r)) for r in rows]


def update_patient(patient_id: int, data: PatientUpdate) -> Optional[PatientOut]:
    conn = get_connection()
    cur = conn.cursor()

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        return get_patient(patient_id)

    set_clause = ", ".join([f"{f} = :{f}" for f in updates])
    updates["id"] = patient_id
    if "password" in updates:
        updates["password_hash"] = hash_password(updates.pop("password"))

    cur.execute(f"""
        UPDATE patients
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, updates)

    conn.commit()
    conn.close()

    log_event("update", "patient", patient_id, updates)

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

    log_event("delete", "patient", patient_id)

    return True


def ensure_active_column():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(patients)")
    cols = [c[1] for c in cur.fetchall()]

    if "active" not in cols:
        cur.execute("ALTER TABLE patients ADD COLUMN active INTEGER DEFAULT 1")
        conn.commit()

    conn.close()