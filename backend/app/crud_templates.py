import sqlite3
from .database import get_connection
from datetime import datetime
import re
import html


# -------------------------------
# CREATE TABLES
# -------------------------------
def init_template_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS note_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        content_html TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()


# -------------------------------
# VARIABLE SUBSTITUTION ENGINE
# -------------------------------
VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.]+)\s*}}")


def substitute_variables(template_html: str, data: dict) -> str:
    """Replace {{patient.first_name}} style variables."""

    def lookup(path: str):
        keys = path.split(".")
        ptr = data
        for k in keys:
            if isinstance(ptr, dict) and k in ptr:
                ptr = ptr[k]
            else:
                return ""  # missing → blank
        return ptr

    def replacer(match):
        var_name = match.group(1)
        value = lookup(var_name)
        return html.escape(str(value)) if value else ""

    return VAR_PATTERN.sub(replacer, template_html)


# -------------------------------
# CRUD
# -------------------------------
def create_template(payload):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO note_templates (name, category, content_html)
        VALUES (?, ?, ?)
    """, (payload.name, payload.category, payload.content_html))

    conn.commit()
    return cur.lastrowid


def get_all_templates():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM note_templates ORDER BY id DESC")
    return cur.fetchall()


def get_template_by_id(template_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM note_templates WHERE id = ?", (template_id,))
    return cur.fetchone()


def update_template(template_id: int, payload):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE note_templates
        SET name = ?, category = ?, content_html = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (payload.name, payload.category, payload.content_html, template_id))

    conn.commit()
    return cur.rowcount > 0


def delete_template(template_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM note_templates WHERE id = ?", (template_id,))
    conn.commit()
    return cur.rowcount > 0


# -------------------------------
# APPLY TEMPLATE TO ENCOUNTER
# -------------------------------
def apply_template_to_encounter(template_id: int, encounter_data: dict):
    tpl = get_template_by_id(template_id)
    if not tpl:
        return None

    _, name, category, content_html, _, _ = tpl  # unpack row

    filled_html = substitute_variables(content_html, encounter_data)

    return {
        "template_id": template_id,
        "name": name,
        "category": category,
        "content_html": filled_html
    }