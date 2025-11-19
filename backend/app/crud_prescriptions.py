from .database import get_connection, dict_from_row
from typing import Optional
from datetime import datetime


def init_prescription_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medication_prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            medication_name TEXT NOT NULL,
            dose TEXT NOT NULL,
            route TEXT,
            frequency TEXT,
            quantity TEXT,
            refills INTEGER DEFAULT 0,

            instructions TEXT,
            diagnosis TEXT,

            issued_date TEXT DEFAULT (datetime('now')),
            pdf_path TEXT,

            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()

def create_prescription(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO medication_prescriptions (
            patient_id, provider_id,
            medication_name, dose, route, frequency,
            quantity, refills,
            instructions, diagnosis
        )
        VALUES (
            :patient_id, :provider_id,
            :medication_name, :dose, :route, :frequency,
            :quantity, :refills,
            :instructions, :diagnosis
        )
    """, data)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_prescription(new_id)

def get_prescription(rx_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM medication_prescriptions WHERE id = ?", (rx_id,))
    row = cur.fetchone()
    conn.close()

    return dict_from_row(row) if row else None