import sqlite3
from datetime import datetime, timedelta
from jose import jwt
from pathlib import Path
from .database import get_connection, dict_from_row

SECRET_KEY = "portal-patient-secret-key-CHANGE-THIS"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def authenticate_portal_patient(email: str, dob: str):
    """
    Patient login using email + DOB.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM patients 
        WHERE email = ? AND dob = ? AND active = 1
    """, (email, dob))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return dict_from_row(row)


def create_portal_jwt(patient):
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(patient["id"]),
        "role": "patient_portal",
        "exp": expire,
        "first_name": patient["first_name"],
        "last_name": patient["last_name"],
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token