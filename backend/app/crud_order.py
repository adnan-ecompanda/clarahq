import sqlite3
from typing import Optional, List
from .database import get_connection, dict_from_row
from .schemas_order import OrderCreate, OrderUpdate, OrderOut


def init_order_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            encounter_id INTEGER,
            provider_id INTEGER NOT NULL,

            order_type TEXT NOT NULL,   -- lab, imaging, medication
            name TEXT NOT NULL,         -- CBC, Chest X-ray, Amoxicillin 500mg
            details TEXT,               -- specific instructions

            priority TEXT,              -- routine, urgent, stat
            clinical_notes TEXT,

            status TEXT DEFAULT 'pending',  
            -- pending, in-progress, completed, cancelled

            external_order_id TEXT,     -- lab system order ID
            external_location TEXT,     -- which lab/hospital

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


def create_order(data: OrderCreate) -> OrderOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO orders (
            patient_id, encounter_id, provider_id,
            order_type, name, details, priority,
            clinical_notes, external_order_id, external_location
        )
        VALUES (
            :patient_id, :encounter_id, :provider_id,
            :order_type, :name, :details, :priority,
            :clinical_notes, :external_order_id, :external_location
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_order(new_id)


def get_order(order_id: int) -> Optional[OrderOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return OrderOut(**dict_from_row(row))


def update_order(order_id: int, data: OrderUpdate) -> Optional[OrderOut]:
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_order(order_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = order_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"UPDATE orders SET {set_clause}, updated_at = datetime('now') WHERE id = :id", payload)
    conn.commit()
    conn.close()

    return get_order(order_id)


def list_orders(patient_id: Optional[int] = None) -> List[OrderOut]:
    conn = get_connection()
    cur = conn.cursor()

    if patient_id:
        cur.execute("SELECT * FROM orders WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
    else:
        cur.execute("SELECT * FROM orders ORDER BY created_at DESC")

    rows = cur.fetchall()
    conn.close()

    return [OrderOut(**dict_from_row(r)) for r in rows]
