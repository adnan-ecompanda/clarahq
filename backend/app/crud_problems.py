from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_problems import ProblemCreate, ProblemUpdate, ProblemOut
from .audit import log_event


def init_problem_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            icd10_code TEXT,
            snomed_code TEXT,
            onset_date TEXT,
            resolved_date TEXT,
            chronic INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            encounter_id INTEGER,
            provider_id INTEGER,
            notes TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def create_problem(data: ProblemCreate) -> ProblemOut:
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()

    cur.execute("""
        INSERT INTO problems (
            patient_id, description, icd10_code, snomed_code,
            onset_date, resolved_date, chronic, status,
            encounter_id, provider_id, notes, active
        )
        VALUES (
            :patient_id, :description, :icd10_code, :snomed_code,
            :onset_date, :resolved_date, :chronic, :status,
            :encounter_id, :provider_id, :notes, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    log_event("create", "problem", new_id, payload)

    return get_problem(new_id)


def get_problem(problem_id: int) -> Optional[ProblemOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "problem", problem_id)

    return ProblemOut(**dict_from_row(row)) if row else None


def list_patient_problems(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM problems WHERE patient_id = ? AND active = 1",
        (patient_id,)
    )
    rows = cur.fetchall()
    conn.close()

    log_event("list", "problem", meta={"patient_id": patient_id, "count": len(rows)})

    return [ProblemOut(**dict_from_row(r)) for r in rows]


def update_problem(problem_id: int, data: ProblemUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_problem(problem_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = problem_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE problems
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    log_event("update", "problem", problem_id, payload)

    return get_problem(problem_id)


def delete_problem(problem_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE problems SET active = 0 WHERE id = ?", (problem_id,))
    conn.commit()
    conn.close()

    log_event("delete", "problem", problem_id)

    return {"status": "deleted"}


def list_problems(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE patient_id = ?", (patient_id,))
    rows = cur.fetchall()
    conn.close()

    log_event("list", "problem", meta={"patient_id": patient_id, "count": len(rows)})

    return [dict_from_row(r) for r in rows]