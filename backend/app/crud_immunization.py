from .database import get_connection, dict_from_row
from .schemas_immunization import ImmunizationCreate, ImmunizationUpdate, ImmunizationOut
from typing import Optional

def init_immunization_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS immunizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            vaccine_name TEXT NOT NULL,
            cvx_code TEXT,
            manufacturer TEXT,
            lot_number TEXT,
            expiration_date TEXT,
            route TEXT,
            site TEXT,
            dose TEXT,
            administered_date TEXT,
            provider_id INTEGER,
            status TEXT DEFAULT 'completed',
            notes TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_immunization(data: ImmunizationCreate) -> ImmunizationOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO immunizations (
            patient_id, vaccine_name, cvx_code, manufacturer, lot_number,
            expiration_date, route, site, dose, administered_date,
            provider_id, status, notes, active
        )
        VALUES (
            :patient_id, :vaccine_name, :cvx_code, :manufacturer, :lot_number,
            :expiration_date, :route, :site, :dose, :administered_date,
            :provider_id, :status, :notes, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return get_immunization(new_id)


def get_immunization(immunization_id: int) -> Optional[ImmunizationOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM immunizations WHERE id = ?", (immunization_id,))
    row = cur.fetchone()
    conn.close()

    return ImmunizationOut(**dict_from_row(row)) if row else None


def list_immunizations(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM immunizations WHERE patient_id = ? AND active = 1", (patient_id,))
    rows = cur.fetchall()

    conn.close()
    return [ImmunizationOut(**dict_from_row(r)) for r in rows]


def update_immunization(immunization_id: int, data: ImmunizationUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}
    if not payload:
        return get_immunization(immunization_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = immunization_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE immunizations
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    return get_immunization(immunization_id)


def delete_immunization(immunization_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE immunizations SET active = 0 WHERE id = ?", (immunization_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}