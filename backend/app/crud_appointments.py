import sqlite3
from datetime import datetime
from .database import get_connection, dict_from_row
from .audit import log_event       # <-- ADDED


def init_appointment_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Main appointment table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,

            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            type TEXT,
            location TEXT,

            reason TEXT,
            notes TEXT,

            status TEXT DEFAULT 'scheduled',
            -- allowed: scheduled, confirmed, checked_in, completed, cancelled, no_show

            telehealth_url TEXT,
            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Optional appointment log table (kept)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
            action TEXT,
            action_by INTEGER,
            timestamp TEXT DEFAULT (datetime('now')),
            note TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
#                      CREATE
# ============================================================

def create_appointment(payload):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO appointments (
            patient_id, provider_id,
            start_time, end_time,
            type, location, reason, notes,
            status, telehealth_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload["patient_id"], payload["provider_id"],
        payload["start_time"], payload["end_time"],
        payload.get("type"), payload.get("location"),
        payload.get("reason"), payload.get("notes"),
        payload.get("status", "scheduled"),
        payload.get("telehealth_url")
    ))

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # AUDIT
    log_event("create", "appointment", new_id, meta=payload)

    return get_appointment(new_id)


# ============================================================
#                      READ
# ============================================================

def get_appointment(appt_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM appointments WHERE id = ?", (appt_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "appointment", appt_id)

    return dict_from_row(row) if row else None


def list_appointments(provider_id: int = None, patient_id: int = None):
    conn = get_connection()
    cur = conn.cursor()

    if provider_id:
        cur.execute("SELECT * FROM appointments WHERE provider_id = ? AND active = 1", (provider_id,))
    elif patient_id:
        cur.execute("SELECT * FROM appointments WHERE patient_id = ? AND active = 1", (patient_id,))
    else:
        cur.execute("SELECT * FROM appointments WHERE active = 1")

    rows = cur.fetchall()
    conn.close()

    log_event("list", "appointment")

    return [dict_from_row(r) for r in rows]


# ============================================================
#                      UPDATE
# ============================================================

def update_appointment(appt_id: int, payload: dict):
    if not payload:
        return get_appointment(appt_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = appt_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE appointments
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    # AUDIT
    log_event("update", "appointment", appt_id, meta=payload)

    return get_appointment(appt_id)


# ============================================================
#                      INTERNAL LOGGING TABLE
# ============================================================

def log_appointment_action(appt_id: int, action: str, by: int, note: str = None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO appointment_logs (appointment_id, action, action_by, note)
        VALUES (?, ?, ?, ?)
    """, (appt_id, action, by, note))

    conn.commit()
    conn.close()

    # AUDIT MIRROR
    log_event(action, "appointment_action", appt_id, meta={"by": by, "note": note})


# ============================================================
#                      DELETE
# ============================================================

def delete_appointment(appt_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE appointments SET active = 0 WHERE id = ?", (appt_id,))
    conn.commit()
    conn.close()

    # AUDIT
    log_event("delete", "appointment", appt_id)

    return {"status": "deleted"}