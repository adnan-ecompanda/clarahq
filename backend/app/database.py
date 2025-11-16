import sqlite3
from pathlib import Path
from typing import Any, Dict

DB_PATH = Path(__file__).resolve().parent.parent / "clarahq.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the patients table if it does not exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Identification
            mrn TEXT,
            external_id TEXT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            photo_url TEXT,

            -- Contact
            phone_primary TEXT,
            phone_secondary TEXT,
            email TEXT,

            address_line1 TEXT,
            address_line2 TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            country TEXT,

            -- Emergency contact
            emergency_contact_name TEXT,
            emergency_contact_relationship TEXT,
            emergency_contact_phone TEXT,

            -- Insurance
            insurance_provider TEXT,
            insurance_plan TEXT,
            insurance_member_id TEXT,
            insurance_group_number TEXT,
            insurance_effective_date TEXT,
            insurance_expiration_date TEXT,

            -- Clinical flags
            allergies TEXT,
            medications TEXT,
            notes TEXT,

            preferred_language TEXT,
            requires_interpreter INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
        """
    )

    conn.commit()
    conn.close()


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)