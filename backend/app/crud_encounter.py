from typing import Optional, List
from .database import get_connection, dict_from_row
from .schemas_encounter import EncounterCreate, EncounterUpdate, EncounterOut
from .audit import log_event    # <-- AUDIT LOGGER


# -------------------------------------------------
# Initialize Table
# -------------------------------------------------
def init_encounter_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS encounters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,

            visit_type TEXT,
            visit_date TEXT DEFAULT (datetime('now')),

            chief_complaint TEXT,
            hpi TEXT,
            objective_exam TEXT,
            assessment TEXT,
            plan TEXT,

            vitals_bp TEXT,
            vitals_hr TEXT,
            vitals_temp TEXT,
            vitals_rr TEXT,
            vitals_spo2 TEXT,

            cpt_code TEXT,
            icd10_code TEXT,

            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),

            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(provider_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# Create
# -------------------------------------------------
def create_encounter(data: EncounterCreate) -> EncounterOut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()

    cur.execute("""
        INSERT INTO encounters (
            patient_id, provider_id,
            visit_type, visit_date,
            chief_complaint, hpi, objective_exam, assessment, plan,
            vitals_bp, vitals_hr, vitals_temp, vitals_rr, vitals_spo2,
            cpt_code, icd10_code, active
        )
        VALUES (
            :patient_id, :provider_id,
            :visit_type, :visit_date,
            :chief_complaint, :hpi, :objective_exam, :assessment, :plan,
            :vitals_bp, :vitals_hr, :vitals_temp, :vitals_rr, :vitals_spo2,
            :cpt_code, :icd10_code, :active
        )
    """, payload)

    conn.commit()
    encounter_id = cur.lastrowid
    conn.close()

    log_event("create", "encounter", encounter_id, payload)

    return get_encounter(encounter_id)


# -------------------------------------------------
# Read (single)
# -------------------------------------------------
def get_encounter(encounter_id: int) -> Optional[EncounterOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM encounters WHERE id = ? AND active = 1", (encounter_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "encounter", encounter_id)

    return EncounterOut(**dict_from_row(row)) if row else None


# -------------------------------------------------
# List all encounters
# -------------------------------------------------
def list_encounters() -> List[EncounterOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM encounters WHERE active = 1 ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    log_event("list", "encounter", meta={"count": len(rows)})

    return [EncounterOut(**dict_from_row(r)) for r in rows]


# -------------------------------------------------
# List for patient
# -------------------------------------------------
def list_patient_encounters(patient_id: int) -> List[EncounterOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM encounters
        WHERE patient_id = ? AND active = 1
        ORDER BY id DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "encounter", meta={"patient_id": patient_id, "count": len(rows)})

    return [EncounterOut(**dict_from_row(r)) for r in rows]


# -------------------------------------------------
# Update
# -------------------------------------------------
def update_encounter(encounter_id: int, data: EncounterUpdate) -> Optional[EncounterOut]:
    conn = get_connection()
    cur = conn.cursor()

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return get_encounter(encounter_id)

    set_clause = ", ".join([f"{field} = :{field}" for field in updates])
    updates["id"] = encounter_id

    cur.execute(f"""
        UPDATE encounters
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, updates)

    conn.commit()
    conn.close()

    log_event("update", "encounter", encounter_id, updates)

    return get_encounter(encounter_id)


# -------------------------------------------------
# Delete (soft delete)
# -------------------------------------------------
def delete_encounter(encounter_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE encounters
        SET active = 0, updated_at = datetime('now')
        WHERE id = ?
    """, (encounter_id,))

    conn.commit()
    conn.close()

    log_event("delete", "encounter", encounter_id)

    return True


# -------------------------------------------------
# CCD compatibility function
# -------------------------------------------------
def list_encounters_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT *
        FROM encounters
        WHERE patient_id = ? AND active = 1
        ORDER BY visit_date DESC
    """, (patient_id,))
    
    rows = cur.fetchall()
    conn.close()
    
    log_event("list", "encounter", meta={"patient_id": patient_id, "count": len(rows)})

    return [dict_from_row(r) for r in rows]