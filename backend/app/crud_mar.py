import os
from datetime import datetime
from typing import Optional

from .database import get_connection, dict_from_row
from .schemas_mar import (
    MedicationOrderCreate, MedicationOrderUpdate, MedicationOrderOut,
    MARCreate, MARUpdate, MAROut
)

from .audit import log_event   # <-- ADDED


# -------------------- CREATE TABLES ------------------------

def init_mar_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Medication Orders
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medication_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,

            medication_name TEXT NOT NULL,
            dose TEXT NOT NULL,
            route TEXT NOT NULL,
            frequency TEXT NOT NULL,

            start_date TEXT,
            end_date TEXT,

            instructions TEXT,
            status TEXT DEFAULT 'active',

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # MAR entries
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mar_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,
            administered_by INTEGER NOT NULL,
            administered_at TEXT,

            dose_given TEXT NOT NULL,
            route TEXT NOT NULL,
            notes TEXT,

            prn_reason TEXT,
            prn_effectiveness TEXT,

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
#                    MEDICATION ORDERS
# ============================================================

def create_med_order(data: MedicationOrderCreate) -> MedicationOrderOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO medication_orders (
            patient_id, provider_id,
            medication_name, dose, route, frequency,
            start_date, end_date,
            instructions, status
        )
        VALUES (
            :patient_id, :provider_id,
            :medication_name, :dose, :route, :frequency,
            :start_date, :end_date,
            :instructions, :status
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # AUDIT
    log_event("create", "med_order", new_id, meta=payload)

    return get_med_order(new_id)


def get_med_order(order_id: int) -> Optional[MedicationOrderOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM medication_orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "med_order", order_id)

    return MedicationOrderOut(**dict_from_row(row)) if row else None


def list_med_orders(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM medication_orders WHERE patient_id = ? AND active = 1",
                (patient_id,))
    rows = cur.fetchall()
    conn.close()

    # AUDIT
    log_event("list", "med_order", meta={"patient_id": patient_id})

    return [MedicationOrderOut(**dict_from_row(r)) for r in rows]


def update_med_order(order_id: int, data: MedicationOrderUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not payload:
        return get_med_order(order_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = order_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE medication_orders SET {set_clause}, updated_at = datetime('now') WHERE id = :id",
        payload
    )

    conn.commit()
    conn.close()

    # AUDIT
    log_event("update", "med_order", order_id, meta=payload)

    return get_med_order(order_id)


def delete_med_order(order_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE medication_orders SET active = 0 WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    # AUDIT
    log_event("delete", "med_order", order_id)

    return {"status": "deleted"}


# ============================================================
#                    MAR ENTRIES
# ============================================================

def create_mar_entry(data: MARCreate) -> MAROut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()

    if payload["administered_at"] is None:
        payload["administered_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO mar_entries (
            order_id, administered_by, administered_at,
            dose_given, route, notes,
            prn_reason, prn_effectiveness
        )
        VALUES (
            :order_id, :administered_by, :administered_at,
            :dose_given, :route, :notes,
            :prn_reason, :prn_effectiveness
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # AUDIT
    log_event("create", "mar_entry", new_id, meta=payload)

    return get_mar_entry(new_id)


def get_mar_entry(entry_id: int) -> Optional[MAROut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM mar_entries WHERE id = ?", (entry_id,))
    row = cur.fetchone()

    conn.close()

    if row:
        log_event("read", "mar_entry", entry_id)

    return MAROut(**dict_from_row(row)) if row else None


def list_mar_entries(order_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM mar_entries WHERE order_id = ? AND active = 1",
                (order_id,))
    rows = cur.fetchall()
    conn.close()

    # AUDIT
    log_event("list", "mar_entry", meta={"order_id": order_id})

    return [MAROut(**dict_from_row(r)) for r in rows]


def update_mar_entry(entry_id: int, data: MARUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not payload:
        return get_mar_entry(entry_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = entry_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        f"UPDATE mar_entries SET {set_clause}, updated_at = datetime('now') WHERE id = :id",
        payload
    )

    conn.commit()
    conn.close()

    # AUDIT
    log_event("update", "mar_entry", entry_id, meta=payload)

    return get_mar_entry(entry_id)


def delete_mar_entry(entry_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE mar_entries SET active = 0 WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

    # AUDIT
    log_event("delete", "mar_entry", entry_id)

    return {"status": "deleted"}