import sqlite3
from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_user import UserCreate, UserOut
from .security import hash_password


def init_user_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,

            role TEXT NOT NULL,
            department TEXT,
            specialty TEXT,

            npi_number TEXT,
            credentials TEXT,
            license_number TEXT,
            license_state TEXT,

            profile_photo_url TEXT,
            language_preference TEXT,
            notification_preferences TEXT,

            password_hash TEXT NOT NULL,
            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_user(data: UserCreate) -> UserOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()
    payload["password_hash"] = hash_password(payload.pop("password"))

    cur.execute("""
        INSERT INTO users (
            first_name, last_name, email, phone,
            role, department, specialty,
            npi_number, credentials, license_number, license_state,
            profile_photo_url, language_preference, notification_preferences,
            password_hash, active
        )
        VALUES (
            :first_name, :last_name, :email, :phone,
            :role, :department, :specialty,
            :npi_number, :credentials, :license_number, :license_state,
            :profile_photo_url, :language_preference, :notification_preferences,
            :password_hash, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_user(new_id)


def get_user(user_id: int) -> Optional[UserOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return UserOut(**dict_from_row(row))


def get_user_by_email(email: str) -> Optional[UserOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return UserOut(**dict_from_row(row))