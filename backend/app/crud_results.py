import sqlite3
from typing import Optional, List
from .database import get_connection, dict_from_row
from .schemas_results import (
    LabResultCreate, LabResultUpdate, LabResultOut,
    ImagingResultCreate, ImagingResultUpdate, ImagingResultOut
)
from datetime import datetime

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
    if payload["result_date"] is None:
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
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not payload:
        return get_lab_result(result_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = result_id

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE lab_results SET {set_clause}, updated_at = datetime('now') WHERE id = :id", payload)
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