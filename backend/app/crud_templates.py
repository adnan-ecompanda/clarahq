import sqlite3
from jinja2 import Template

from .database import get_connection
from .schemas_templates import (
    TemplateCreate,
    TemplateUpdate,
    TemplateVersion,
)


# ================================================
# INIT TABLES
# ================================================
def init_template_tables():
    conn = get_connection()
    cur = conn.cursor()

    # MAIN TEMPLATES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        content_html TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # VERSIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS template_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER,
        version_number INTEGER,
        content_html TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------
# EXISTING FUNCTIONS (UNCHANGED)
# ------------------------------------------------
def create_template(data: TemplateCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO templates (name, category, content_html, created_by)
        VALUES (?, ?, ?, ?)
    """, (data.name, data.category, data.content_html, data.created_by))

    new_id = cur.lastrowid

    cur.execute("""
        INSERT INTO template_versions (template_id, version_number, content_html)
        VALUES (?, ?, ?)
    """, (new_id, 1, data.content_html))

    conn.commit()
    conn.close()
    return new_id


def get_all_templates():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, category, content_html FROM templates")
    rows = cur.fetchall()

    conn.close()
    return rows


def get_template_by_id(template_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
    tpl = cur.fetchone()

    conn.close()
    return tpl


def update_template(template_id: int, data: TemplateUpdate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
    tpl = cur.fetchone()
    if not tpl:
        return None

    new_name = data.name or tpl[1]
    new_category = data.category or tpl[2]
    new_html = data.content_html or tpl[3]

    cur.execute("""
        UPDATE templates
        SET name = ?, category = ?, content_html = ?
        WHERE id = ?
    """, (new_name, new_category, new_html, template_id))

    cur.execute("SELECT MAX(version_number) FROM template_versions WHERE template_id = ?", (template_id,))
    last_v = cur.fetchone()[0] or 1
    new_v = last_v + 1

    cur.execute("""
        INSERT INTO template_versions (template_id, version_number, content_html)
        VALUES (?, ?, ?)
    """, (template_id, new_v, new_html))

    conn.commit()
    conn.close()

    return new_v


def delete_template(template_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    deleted = cur.rowcount > 0

    conn.commit()
    conn.close()
    return deleted


def get_template_versions(template_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, template_id, version_number, content_html, created_at
        FROM template_versions
        WHERE template_id = ?
        ORDER BY version_number DESC
    """, (template_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "template_id": r[1],
            "version": r[2],
            "content_html": r[3],
            "created_at": r[4]
        }
        for r in rows
    ]


def rollback_template(template_id: int, version: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT content_html FROM template_versions
        WHERE template_id = ? AND version_number = ?
    """, (template_id, version))

    row = cur.fetchone()
    if not row:
        return False

    html = row[0]

    cur.execute("""
        UPDATE templates SET content_html = ?
        WHERE id = ?
    """, (html, template_id))

    conn.commit()
    conn.close()
    return True


# ================================================
# APPLY TEMPLATE TO ENCOUNTER
# ================================================
def apply_template(encounter_id: int, template_id: int):
    conn = get_connection()
    cur = conn.cursor()

    # 1. fetch encounter data
    cur.execute("""
        SELECT id, patient_id, provider_id, note
        FROM encounters
        WHERE id = ?
    """, (encounter_id,))
    enc = cur.fetchone()

    if not enc:
        conn.close()
        return None

    encounter_data = {
        "encounter_id": enc[0],
        "patient_id": enc[1],
        "provider_id": enc[2],
        "note": enc[3] or ""
    }

    # 2. fetch patient
    cur.execute("SELECT id, first_name, last_name, dob FROM patients WHERE id = ?", (enc[1],))
    p = cur.fetchone()
    if not p:
        conn.close()
        return None

    patient_data = {
        "id": p[0],
        "first_name": p[1],
        "last_name": p[2],
        "dob": p[3]
    }

    # 3. fetch template
    cur.execute("SELECT content_html FROM templates WHERE id = ?", (template_id,))
    tpl = cur.fetchone()
    if not tpl:
        conn.close()
        return None

    html_template = tpl[0]

    # 4. render with Jinja2
    rendered = Template(html_template).render(
        patient=patient_data,
        encounter=encounter_data
    )

    # 5. save into notes table (overwrite existing encounter note)
    cur.execute("""
        UPDATE encounters SET note = ?
        WHERE id = ?
    """, (rendered, encounter_id))

    conn.commit()
    conn.close()

    return rendered