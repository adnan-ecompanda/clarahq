import sqlite3
from typing import List, Optional
from .schemas_patient_portal import (
    PatientRegister, PatientPortalProfile,
    EncounterSummary, EncounterDetail,
    ClaimSummary, ClaimDetail, PortalDocument
)
from passlib.hash import bcrypt


DB_PATH = "app.db"


# -----------------------
# Helpers
# -----------------------

from .database import get_connection, dict_from_row

def init_patient_portal_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_portal_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------
#  REGISTER PATIENT + CREATE PORTAL USER
# ---------------------------------------------
def register_patient(data):
    conn = get_connection()
    cur = conn.cursor()

    # 1. Create patient record
    cur.execute("""
        INSERT INTO patients (
            first_name, last_name, email, 
            created_at, updated_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        data.first_name,
        data.last_name,
        data.email
    ))

    patient_id = cur.lastrowid

    # 2. Create patient portal user record
    cur.execute("""
        INSERT INTO patient_portal_users (
            patient_id, email, password_hash, created_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        patient_id,
        data.email,
        bcrypt.hash(data.password)
    ))

    conn.commit()
    return {"message": "Patient registered", "patient_id": patient_id}



# ---------------------------------------------
#  LOGIN
# ---------------------------------------------
def login_patient(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT patient_id, password_hash
        FROM patient_portal_users
        WHERE email = ?
    """, (data.email,))

    row = cur.fetchone()
    if not row:
        return None

    patient_id, password_hash = row

    if not bcrypt.verify(data.password, password_hash):
        return None

    return {"patient_id": patient_id}

# -----------------------
# Profile
# -----------------------

def get_patient_profile(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, first_name, last_name, email, 
               phone_primary, dob, gender,
               address_line1, address_line2, city, state, zip_code
        FROM patients
        WHERE id = ?
    """, (patient_id,))

    row = cur.fetchone()
    if not row:
        return None

    columns = [col[0] for col in cur.description]
    return dict(zip(columns, row))


def update_patient_profile(patient_id: int, data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE patients
        SET phone_primary = ?, dob = ?, gender = ?,
            address_line1 = ?, address_line2 = ?, city = ?,
            state = ?, zip_code = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        data.phone_primary,
        data.dob,
        data.gender,
        data.address_line1,
        data.address_line2,
        data.city,
        data.state,
        data.zip_code,
        patient_id
    ))

    conn.commit()
    return {"message": "Profile updated"}


# -----------------------
# Encounters
# -----------------------

def list_encounters(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, visit_date, visit_type, chief_complaint
        FROM encounters WHERE patient_id = ?
        ORDER BY visit_date DESC
    """, (patient_id,))

    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append(
            EncounterSummary(
                id=r[0],
                visit_date=r[1],
                visit_type=r[2],
                chief_complaint=r[3]
            )
        )
    return results


def encounter_detail(encounter_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, visit_date, visit_type, chief_complaint,
               hpi, objective_exam, assessment, plan,
               vitals_bp, vitals_hr, vitals_temp, vitals_rr, vitals_spo2,
               cpt_code, icd10_code
        FROM encounters WHERE id = ?
    """, (encounter_id,))

    row = cur.fetchone()
    if not row:
        return None

    fields = [
        "id", "visit_date", "visit_type", "chief_complaint",
        "hpi", "objective_exam", "assessment", "plan",
        "vitals_bp", "vitals_hr", "vitals_temp", "vitals_rr", "vitals_spo2",
        "cpt_code", "icd10_code"
    ]

    return EncounterDetail(**dict(zip(fields, row)))


# -----------------------
# Claims
# -----------------------

def list_claims(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, superbill_id, status, created_at
        FROM claims
        WHERE patient_id = ?
        ORDER BY created_at DESC
    """, (patient_id,))

    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append(
            ClaimSummary(
                id=r[0],
                superbill_id=r[1],
                status=r[2],
                created_at=r[3]
            )
        )
    return results


def claim_detail(claim_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, superbill_id, provider_id, patient_id,
               status, created_at, updated_at
        FROM claims WHERE id = ?
    """, (claim_id,))

    row = cur.fetchone()
    if not row:
        return None

    fields = [
        "id", "superbill_id", "provider_id", "patient_id",
        "status", "created_at", "updated_at"
    ]

    return ClaimDetail(**dict(zip(fields, row)))


# -----------------------
# Documents
# -----------------------

def documents_for_encounter(encounter_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, file_name, file_type, file_size, file_path, uploaded_at
        FROM document_attachments
        WHERE document_id = ?
    """, (encounter_id,))

    rows = cur.fetchall()
    return [
        PortalDocument(
            id=r[0],
            file_name=r[1],
            file_type=r[2],
            file_size=r[3],
            file_path=r[4],
            uploaded_at=r[5]
        ) for r in rows
    ]


def documents_for_claim(claim_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, file_name, file_type, file_size, file_path, uploaded_at
        FROM document_attachments
        WHERE document_id = ?
    """, (claim_id,))

    rows = cur.fetchall()
    return [
        PortalDocument(
            id=r[0],
            file_name=r[1],
            file_type=r[2],
            file_size=r[3],
            file_path=r[4],
            uploaded_at=r[5]
        ) for r in rows
    ]