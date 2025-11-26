import sqlite3

from .database import get_connection, dict_from_row

def init_pa_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prior_authorizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            provider_npi TEXT,
            payer_id TEXT,
            procedure_code TEXT,
            diagnosis_code TEXT,
            clinical_notes TEXT,
            status TEXT DEFAULT 'PENDING',
            request_x12 TEXT,
            response_x12 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def create_prior_auth(data):
    conn = get_connection()
    cur = conn.cursor()

    x12_request = f"278*REQUEST*PATIENT={data.patient_id}*PROC={data.procedure_code}*DX={data.diagnosis_code}"

    cur.execute("""
        INSERT INTO prior_authorizations (
            patient_id, provider_npi, payer_id,
            procedure_code, diagnosis_code, clinical_notes,
            status, request_x12
        )
        VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?)
    """, (
        data.patient_id, data.provider_npi, data.payer_id,
        data.procedure_code, data.diagnosis_code, data.clinical_notes,
        x12_request
    ))

    conn.commit()
    pa_id = cur.lastrowid
    conn.close()

    return pa_id


def get_prior_auth(pa_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM prior_authorizations WHERE id = ?", (pa_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    columns = ["id", "patient_id", "provider_npi", "payer_id", "procedure_code",
               "diagnosis_code", "clinical_notes", "status", "request_x12",
               "response_x12", "created_at", "updated_at"]

    return dict(zip(columns, row))


def update_prior_auth_response(pa_id: int, response_x12: str, status: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE prior_authorizations
        SET response_x12 = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (response_x12, status, pa_id))

    conn.commit()
    conn.close()

    return True