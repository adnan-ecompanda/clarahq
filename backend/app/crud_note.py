import sqlite3
from typing import Optional, List
from .database import get_connection, dict_from_row


def init_note_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clinical_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,

            note_type TEXT NOT NULL,      -- SOAP, Progress, Discharge, Operative
            content TEXT NOT NULL,

            signed_by INTEGER,
            signed_at TEXT,

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),

            FOREIGN KEY (encounter_id) REFERENCES encounters(id),
            FOREIGN KEY (provider_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_note(payload: dict) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO clinical_notes (
            encounter_id, provider_id,
            note_type, content,
            signed_by, signed_at,
            active
        )
        VALUES (
            :encounter_id, :provider_id,
            :note_type, :content,
            :signed_by, :signed_at,
            :active
        )
    """, payload)

    conn.commit()
    note_id = cur.lastrowid
    conn.close()

    return get_note(note_id)


def get_note(note_id: int) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM clinical_notes WHERE id = ?", (note_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None
    return dict_from_row(row)


def get_notes_for_encounter(encounter_id: int) -> List[dict]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM clinical_notes WHERE encounter_id = ?", (encounter_id,))
    rows = cur.fetchall()
    conn.close()

    return [dict_from_row(r) for r in rows]


def update_note(note_id: int, payload: dict) -> Optional[dict]:
    conn = get_connection()
    cur = conn.cursor()

    set_clause = ", ".join([f"{k} = :{k}" for k in payload.keys()])
    payload["id"] = note_id

    cur.execute(f"""
        UPDATE clinical_notes
        SET {set_clause},
            updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()
    return get_note(note_id)


def delete_note(note_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE clinical_notes SET active = 0 WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

    return {"deleted": True}