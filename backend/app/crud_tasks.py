from typing import Optional
from .database import get_connection, dict_from_row
from .schemas_tasks import TaskCreate, TaskUpdate, TaskOut

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

# ------------------- CRUD -------------------

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
    return get_task(new_id)


def get_task(task_id: int) -> Optional[TaskOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return TaskOut(**dict_from_row(row)) if row else None


def list_tasks(status: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()

    if status:
        cur.execute("SELECT * FROM tasks WHERE status = ? AND active = 1", (status,))
    else:
        cur.execute("SELECT * FROM tasks WHERE active = 1")

    rows = cur.fetchall()
    conn.close()

    return [TaskOut(**dict_from_row(r)) for r in rows]


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

    return get_task(task_id)


def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE tasks SET active = 0 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return {"status": "deleted"}