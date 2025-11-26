import sqlite3
from .database import get_connection, dict_from_row

# ---------------------------
# Initialize Eligibility Table
# ---------------------------
def init_eligibility_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS eligibility_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT,
        insurance_provider TEXT,
        patient_first_name TEXT,
        patient_last_name TEXT,
        patient_dob TEXT,
        member_id TEXT,
        payer_id TEXT,
        provider_npi TEXT,
        request_x12 TEXT,
        response_x12 TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


# ---------------------------
# CREATE ELIGIBILITY REQUEST
# ---------------------------
def create_eligibility_request(req):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO eligibility_requests (
            patient_id,
            insurance_provider,
            patient_first_name,
            patient_last_name,
            patient_dob,
            member_id,
            payer_id,
            provider_npi,
            request_x12,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    """, (
        req.patient_id,
        req.insurance_provider,
        req.patient_first_name,
        req.patient_last_name,
        req.patient_dob,
        req.member_id,
        req.payer_id,
        req.provider_npi,
        f"ISA*00*TEST*GS*270 REQUEST FOR {req.member_id}"
    ))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return new_id


# ---------------------------
# GET ELIGIBILITY RECORD
# ---------------------------
def get_eligibility_request(req_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM eligibility_requests WHERE id = ?", (req_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    columns = [
        "id", "patient_id", "insurance_provider", "patient_first_name", "patient_last_name",
        "patient_dob", "member_id", "payer_id", "provider_npi",
        "request_x12", "response_x12", "status", "created_at"
    ]

    return dict(zip(columns, row))


# ---------------------------
# UPDATE RESPONSE + STATUS
# ---------------------------
def attach_eligibility_response(req_id: int, response_x12: str, status: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE eligibility_requests
        SET response_x12 = ?, status = ?
        WHERE id = ?
    """, (response_x12, status, req_id))

    conn.commit()
    updated = cur.rowcount > 0
    conn.close()

    return updated