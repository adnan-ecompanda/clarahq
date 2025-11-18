import sqlite3
from typing import Optional, List
from .database import get_connection, dict_from_row
from .schemas_results import (
    LabResultCreate, LabResultUpdate, LabResultOut,
    ImagingResultCreate, ImagingResultUpdate, ImagingResultOut
)
from datetime import datetime
import shutil, os
from fastapi import UploadFile

def init_results_tables():
    conn = get_connection()
    cur = conn.cursor()

    # -------- LAB RESULTS TABLE --------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lab_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            encounter_id INTEGER,

            test_name TEXT NOT NULL,
            value TEXT,
            unit TEXT,
            reference_range TEXT,
            abnormal_flag TEXT, -- high, low, normal

            notes TEXT,
            result_date TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # -------- IMAGING RESULTS TABLE --------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imaging_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            encounter_id INTEGER,

            modality TEXT NOT NULL, -- X-ray, CT, MRI, US
            body_part TEXT,
            impression TEXT,
            findings TEXT,

            radiologist TEXT,
            result_date TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ============ LAB RESULTS ==============

def create_lab_result(data: LabResultCreate) -> LabResultOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    # Auto-set result_date if null
    if payload.get("result_date") is None:
        payload["result_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO lab_results (
            order_id, patient_id, provider_id, encounter_id,
            test_name, value, unit, reference_range,
            abnormal_flag, notes, result_date
        )
        VALUES (
            :order_id, :patient_id, :provider_id, :encounter_id,
            :test_name, :value, :unit, :reference_range,
            :abnormal_flag, :notes, :result_date
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_lab_result(new_id)


def get_lab_result(result_id: int) -> Optional[LabResultOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM lab_results WHERE id = ?", (result_id,))
    row = cur.fetchone()
    conn.close()
    return LabResultOut(**dict_from_row(row)) if row else None


def update_lab_result(result_id: int, data: LabResultUpdate):
    update_data = data.model_dump(exclude_unset=True)

    # Auto-set date if explicitly passed as null
    if "result_date" in update_data and update_data["result_date"] is None:
        update_data["result_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not update_data:
        return get_lab_result(result_id)

    # Build SQL SET clause
    set_clause = ", ".join([f"{k} = :{k}" for k in update_data])
    update_data["id"] = result_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE lab_results SET {set_clause}, updated_at = datetime('now') WHERE id = :id",
        update_data
    )

    conn.commit()
    conn.close()

    return get_lab_result(result_id)


def list_lab_results(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM lab_results WHERE patient_id = ? ORDER BY result_date DESC", (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [LabResultOut(**dict_from_row(r)) for r in rows]


# ============ IMAGING RESULTS ==============

def create_imaging_result(data: ImagingResultCreate) -> ImagingResultOut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()
    if not payload.get("result_date"):
        payload["result_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO imaging_results (
            order_id, patient_id, provider_id, encounter_id,
            modality, body_part, impression, findings,
            radiologist, result_date
        )
        VALUES (
            :order_id, :patient_id, :provider_id, :encounter_id,
            :modality, :body_part, :impression, :findings,
            :radiologist, :result_date
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_imaging_result(new_id)


def get_imaging_result(result_id: int) -> Optional[ImagingResultOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM imaging_results WHERE id = ?", (result_id,))
    row = cur.fetchone()
    conn.close()
    return ImagingResultOut(**dict_from_row(row)) if row else None


def update_imaging_result(result_id: int, data: ImagingResultUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not payload:
        return get_imaging_result(result_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = result_id

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE imaging_results SET {set_clause}, updated_at = datetime('now') WHERE id = :id", payload)
    conn.commit()
    conn.close()

    return get_imaging_result(result_id)


def list_imaging_results(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM imaging_results WHERE patient_id = ? ORDER BY result_date DESC", (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [ImagingResultOut(**dict_from_row(r)) for r in rows]

def init_imaging_attachments_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imaging_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imaging_result_id INTEGER NOT NULL,
            file_name TEXT,
            file_path TEXT,
            file_type TEXT,
            uploaded_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (imaging_result_id) REFERENCES imaging_results(id)
        )
    """)
    conn.commit()
    conn.close()

UPLOAD_DIR = "uploads/imaging"

def save_imaging_attachment(result_id: int, file: UploadFile):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = f"{UPLOAD_DIR}/{result_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO imaging_attachments (imaging_result_id, file_name, file_path, file_type)
        VALUES (?, ?, ?, ?)
    """, (result_id, file.filename, file_path, file.content_type))

    conn.commit()
    conn.close()

    return {"message": "File uploaded successfully", "file_path": file_path}

def list_labs_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM lab_results
        WHERE patient_id = ?
        ORDER BY result_date DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def list_imaging_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM imaging_results
        WHERE patient_id = ?
        ORDER BY result_date DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]

# Aliases for CCD compatibility ------------------

def list_lab_results_for_patient(patient_id: int):
    return list_labs_for_patient(patient_id)


def list_imaging_results_for_patient(patient_id: int):
    return list_imaging_for_patient(patient_id) 