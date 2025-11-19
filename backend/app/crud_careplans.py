from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_careplans import CarePlanCreate, CarePlanUpdate, CarePlanOut
from .audit import log_event   # <-- AUDIT LOGGER


def init_careplan_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS care_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            patient_id INTEGER NOT NULL,
            encounter_id INTEGER,
            provider_id INTEGER,

            title TEXT NOT NULL,
            diagnosis TEXT,

            goals TEXT,
            interventions TEXT,
            expected_outcomes TEXT,
            actual_outcomes TEXT,

            start_date TEXT,
            review_date TEXT,
            status TEXT DEFAULT 'active',

            active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_careplan(data: CarePlanCreate) -> CarePlanOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO care_plans (
            patient_id, encounter_id, provider_id,
            title, diagnosis, goals, interventions,
            expected_outcomes, actual_outcomes,
            start_date, review_date, status, active
        )
        VALUES (
            :patient_id, :encounter_id, :provider_id,
            :title, :diagnosis, :goals, :interventions,
            :expected_outcomes, :actual_outcomes,
            :start_date, :review_date, :status, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # AUDIT
    log_event("create", "careplan", new_id, payload)

    return get_careplan(new_id)


def get_careplan(cp_id: int) -> Optional[CarePlanOut]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM care_plans WHERE id = ?", (cp_id,))
    row = cur.fetchone()

    conn.close()

    if row:
        log_event("read", "careplan", cp_id)

    return CarePlanOut(**dict_from_row(row)) if row else None


def list_patient_careplans(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM care_plans
        WHERE patient_id = ? AND active = 1
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    # AUDIT
    log_event("list", "careplan", meta={"patient_id": patient_id})

    return [CarePlanOut(**dict_from_row(r)) for r in rows]


def update_careplan(cp_id: int, data: CarePlanUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_careplan(cp_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = cp_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE care_plans
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    # AUDIT
    log_event("update", "careplan", cp_id, payload)

    return get_careplan(cp_id)


def delete_careplan(cp_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE care_plans SET active = 0 WHERE id = ?", (cp_id,))

    conn.commit()
    conn.close()

    # AUDIT
    log_event("delete", "careplan", cp_id)

    return {"status": "deleted"}


def list_careplans_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM care_plans
        WHERE patient_id = ? AND active = 1
        ORDER BY start_date DESC
    """, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    # AUDIT
    log_event("list", "careplan", meta={"patient_id": patient_id})

    return [dict_from_row(r) for r in rows]