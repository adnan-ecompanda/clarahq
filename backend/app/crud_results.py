import os
import shutil
from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile

from .database import get_connection, dict_from_row
from .schemas_results import (
    LabResultCreate, LabResultUpdate, LabResultOut,
    ImagingResultCreate, ImagingResultUpdate, ImagingResultOut
)

from .audit import log_event   # AUDIT LOGGER


# ==========================================
# INIT TABLES
# ==========================================
def init_results_tables():
    conn = get_connection()
    cur = conn.cursor()

    # LAB RESULTS
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
            abnormal_flag TEXT,

            notes TEXT,
            result_date TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # IMAGING RESULTS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imaging_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            encounter_id INTEGER,

            modality TEXT NOT NULL,
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

    # ATTACHMENTS
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


# ==========================================
# LAB RESULTS
# ==========================================
def create_lab_result(data: LabResultCreate) -> LabResultOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    if not payload.get("result_date"):
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

    log_event("create", "lab_result", new_id, payload)

    return get_lab_result(new_id)


def get_lab_result(result_id: int) -> Optional[LabResultOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM lab_results WHERE id = ?", (result_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "lab_result", result_id)

    return LabResultOut(**dict_from_row(row)) if row else None


def update_lab_result(result_id: int, data: LabResultUpdate):
    update_data = data.model_dump(exclude_unset=True)

    if "result_date" in update_data and update_data["result_date"] is None:
        update_data["result_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not update_data:
        return get_lab_result(result_id)

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

    log_event("update", "lab_result", result_id, update_data)

    return get_lab_result(result_id)


def list_lab_results(patient_id: int) -> List[LabResultOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM lab_results
        WHERE patient_id = ?
        ORDER BY result_date DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "lab_result", meta={"patient_id": patient_id})

    return [LabResultOut(**dict_from_row(r)) for r in rows]


# ==========================================
# IMAGING RESULTS
# ==========================================
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

    log_event("create", "imaging_result", new_id, payload)

    return get_imaging_result(new_id)


def get_imaging_result(result_id: int) -> Optional[ImagingResultOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM imaging_results WHERE id = ?", (result_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "imaging_result", result_id)

    return ImagingResultOut(**dict_from_row(row)) if row else None


def update_imaging_result(result_id: int, data: ImagingResultUpdate):
    payload = data.model_dump(exclude_unset=True)

    if not payload:
        return get_imaging_result(result_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = result_id

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE imaging_results SET {set_clause}, updated_at = datetime('now') WHERE id = :id",
        payload
    )

    conn.commit()
    conn.close()

    log_event("update", "imaging_result", result_id, payload)

    return get_imaging_result(result_id)


def list_imaging_results(patient_id: int) -> List[ImagingResultOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM imaging_results
        WHERE patient_id = ?
        ORDER BY result_date DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "imaging_result", meta={"patient_id": patient_id})

    return [ImagingResultOut(**dict_from_row(r)) for r in rows]


# ==========================================
# ATTACHMENTS
# ==========================================
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

    log_event(
        "upload",
        "imaging_attachment",
        entity_id=result_id,
        meta={"file_name": file.filename, "path": file_path}
    )

    return {"message": "File uploaded successfully", "file_path": file_path}


# ==========================================
# CCD ALIASES (FIX FOR YOUR ERROR)
# ==========================================
def list_lab_results_for_patient(patient_id: int):
    return list_lab_results(patient_id)


def list_imaging_results_for_patient(patient_id: int):
    return list_imaging_results(patient_id)