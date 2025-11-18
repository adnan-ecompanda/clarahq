from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_procedures import ProcedureCreate, ProcedureUpdate, ProcedureOut


def init_procedure_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS procedures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            encounter_id INTEGER,
            provider_id INTEGER,

            name TEXT NOT NULL,
            cpt_code TEXT,
            icd10_pcs TEXT,
            snomed_code TEXT,

            procedure_date TEXT,
            notes TEXT,
            result TEXT,

            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_procedure(data: ProcedureCreate) -> ProcedureOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO procedures (
            patient_id, encounter_id, provider_id,
            name, cpt_code, icd10_pcs, snomed_code,
            procedure_date, notes, result, active
        )
        VALUES (
            :patient_id, :encounter_id, :provider_id,
            :name, :cpt_code, :icd10_pcs, :snomed_code,
            :procedure_date, :notes, :result, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_procedure(new_id)


def get_procedure(proc_id: int) -> Optional[ProcedureOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM procedures WHERE id = ?", (proc_id,))
    row = cur.fetchone()

    conn.close()
    return ProcedureOut(**dict_from_row(row)) if row else None


def list_patient_procedures(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM procedures WHERE patient_id = ? AND active = 1", (patient_id,))
    rows = cur.fetchall()
    conn.close()

    return [ProcedureOut(**dict_from_row(r)) for r in rows]


def update_procedure(proc_id: int, data: ProcedureUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_procedure(proc_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = proc_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE procedures 
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    return get_procedure(proc_id)


def delete_procedure(proc_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE procedures SET active = 0 WHERE id = ?", (proc_id,))

    conn.commit()
    conn.close()

    return {"status": "deleted"}

def list_procedures(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM procedures WHERE patient_id = ?", (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]