from .database import get_connection, dict_from_row
from datetime import datetime
from typing import Optional
from .audit import log_event   # <-- AUDIT LOGGER


# ----------------------------
# Initialize Tables
# ----------------------------
def init_vitals_tables():
    conn = get_connection()
    cur = conn.cursor()

    # 1) Basic vitals per encounter
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            encounter_id INTEGER,
            taken_by INTEGER,
            taken_at TEXT DEFAULT (datetime('now')),

            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            heart_rate INTEGER,
            respiratory_rate INTEGER,
            temperature REAL,
            spo2 INTEGER,
            weight REAL,
            height REAL,
            bmi REAL,

            notes TEXT,
            active INTEGER DEFAULT 1
        )
    """)

    # 2) Flowsheet rows (time-series)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flowsheet_rows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            encounter_id INTEGER,
            panel TEXT,
            taken_by INTEGER,
            taken_at TEXT DEFAULT (datetime('now')),

            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            heart_rate INTEGER,
            respiratory_rate INTEGER,
            temperature REAL,
            spo2 INTEGER,
            weight REAL,
            height REAL,
            bmi REAL,

            notes TEXT,
            active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


# ----------------------------
# Utility: BMI Calculation
# ----------------------------
def calc_bmi(weight, height):
    try:
        if weight and height:
            return round(weight / ((height / 100) ** 2), 2)
    except:
        return None
    return None


# ----------------------------
# Basic Vitals CRUD
# ----------------------------
def add_vitals(data):
    payload = data.model_dump()
    payload["bmi"] = calc_bmi(payload.get("weight"), payload.get("height"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO vitals (
            patient_id, encounter_id, taken_by,
            bp_systolic, bp_diastolic, heart_rate,
            respiratory_rate, temperature, spo2,
            weight, height, bmi, notes
        )
        VALUES (
            :patient_id, :encounter_id, :taken_by,
            :bp_systolic, :bp_diastolic, :heart_rate,
            :respiratory_rate, :temperature, :spo2,
            :weight, :height, :bmi, :notes
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    log_event("create", "vitals", new_id, payload)

    return get_vitals(new_id)


def get_vitals(vital_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vitals WHERE id = ?", (vital_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "vitals", vital_id)

    return dict_from_row(row) if row else None


def list_vitals_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM vitals
        WHERE patient_id = ?
        ORDER BY taken_at DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "vitals", meta={"patient_id": patient_id, "count": len(rows)})

    return [dict_from_row(r) for r in rows]


# ----------------------------
# Flowsheet CRUD
# ----------------------------
def add_flowsheet_row(data):
    payload = data.model_dump()
    payload["bmi"] = calc_bmi(payload.get("weight"), payload.get("height"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO flowsheet_rows (
            patient_id, encounter_id, panel, taken_by,
            bp_systolic, bp_diastolic, heart_rate,
            respiratory_rate, temperature, spo2,
            weight, height, bmi, notes
        )
        VALUES (
            :patient_id, :encounter_id, :panel, :taken_by,
            :bp_systolic, :bp_diastolic, :heart_rate,
            :respiratory_rate, :temperature, :spo2,
            :weight, :height, :bmi, :notes
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    log_event("create", "flowsheet", new_id, payload)

    return get_flowsheet_row(new_id)


def get_flowsheet_row(row_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM flowsheet_rows WHERE id = ?", (row_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "flowsheet", row_id)

    return dict_from_row(row) if row else None


def list_flowsheet(patient_id: int, panel: str = None):
    conn = get_connection()
    cur = conn.cursor()

    if panel:
        cur.execute("""
            SELECT * FROM flowsheet_rows
            WHERE patient_id = ? AND panel = ?
            ORDER BY taken_at ASC
        """, (patient_id, panel))
    else:
        cur.execute("""
            SELECT * FROM flowsheet_rows
            WHERE patient_id = ?
            ORDER BY taken_at ASC
        """, (patient_id,))

    rows = cur.fetchall()
    conn.close()

    log_event("list", "flowsheet", meta={"patient_id": patient_id, "panel": panel, "count": len(rows)})

    return [dict_from_row(r) for r in rows]


# ----------------------------
# Patient summary helpers
# ----------------------------
def list_patient_vitals(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vitals WHERE patient_id = ?", (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "vitals", meta={"patient_id": patient_id, "count": len(rows)})

    return [dict_from_row(r) for r in rows]


def get_latest_vitals_for_patient(patient_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM vitals
        WHERE patient_id = ?
        AND active = 1
        ORDER BY taken_at DESC
        LIMIT 1
    """, (patient_id,))
    
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "vitals", dict_from_row(row).get("id"))

    return dict_from_row(row) if row else None