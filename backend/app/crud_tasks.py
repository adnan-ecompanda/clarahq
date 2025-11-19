from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_tasks import TaskCreate, TaskUpdate, TaskOut
from .audit import log_event   # <-- ADDED


# ------------------- INIT TABLE -------------------

def init_task_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,
            description TEXT,

            patient_id INTEGER,
            encounter_id INTEGER,

            assigned_to INTEGER,
            created_by INTEGER,

            due_date TEXT,

            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',

            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ------------------- CREATE -------------------

def create_task(data: TaskCreate) -> TaskOut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()

    cur.execute("""
        INSERT INTO tasks (
            title, description,
            patient_id, encounter_id,
            assigned_to, created_by,
            due_date, priority, status, active
        )
        VALUES (
            :title, :description,
            :patient_id, :encounter_id,
            :assigned_to, :created_by,
            :due_date, :priority, :status, :active
        )
    """, payload)

    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    # AUDIT
    log_event("create", "task", new_id, payload)

    return get_task(new_id)


# ------------------- READ -------------------

def get_task(task_id: int) -> Optional[TaskOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        log_event("read", "task", task_id)

    return TaskOut(**dict_from_row(row)) if row else None


# ------------------- LIST -------------------

def list_tasks(status: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()

    if status:
        cur.execute("SELECT * FROM tasks WHERE status = ? AND active = 1", (status,))
    else:
        cur.execute("SELECT * FROM tasks WHERE active = 1")

    rows = cur.fetchall()
    conn.close()

    # AUDIT
    log_event("list", "task", meta={"status": status})

    return [TaskOut(**dict_from_row(r)) for r in rows]


# ------------------- UPDATE -------------------

def update_task(task_id: int, data: TaskUpdate):
    payload = {k: v for k, v in data.model_dump().items() if v is not None}

    if not payload:
        return get_task(task_id)

    set_clause = ", ".join([f"{k} = :{k}" for k in payload])
    payload["id"] = task_id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        UPDATE tasks
        SET {set_clause}, updated_at = datetime('now')
        WHERE id = :id
    """, payload)

    conn.commit()
    conn.close()

    # AUDIT
    log_event("update", "task", task_id, payload)

    return get_task(task_id)


# ------------------- DELETE -------------------

def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE tasks SET active = 0 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    # AUDIT
    log_event("delete", "task", task_id)

    return {"status": "deleted"}