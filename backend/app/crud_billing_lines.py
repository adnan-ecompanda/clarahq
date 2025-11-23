from typing import List, Optional
from .database import get_connection, dict_from_row
from .schemas_billing_lines import (
    SuperbillCPTCreate,
    SuperbillICDCreate
)


# -----------------------
# CPT LINES CRUD
# -----------------------

def add_cpt_line(superbill_id: int, data: SuperbillCPTCreate):
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()
    payload["superbill_id"] = superbill_id

    cur.execute("""
        INSERT INTO superbill_cpt_items (
            superbill_id, cpt_code, units, modifier, amount, icd_pointer
        ) VALUES (
            :superbill_id, :cpt_code, :units, :modifier, :amount, :icd_pointer
        )
    """, payload)

    conn.commit()
    cid = cur.lastrowid
    conn.close()

    return get_cpt_line(cid)


def get_cpt_line(line_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM superbill_cpt_items WHERE id = ?", (line_id,))
    row = cur.fetchone()
    conn.close()

    return dict_from_row(row) if row else None


def list_cpt_lines(superbill_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM superbill_cpt_items
        WHERE superbill_id = ?
        ORDER BY id ASC
    """, (superbill_id,))

    rows = cur.fetchall()
    conn.close()

    return [dict_from_row(r) for r in rows]


def delete_cpt_line(line_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM superbill_cpt_items WHERE id = ?", (line_id,))
    conn.commit()
    conn.close()

    return True


# -----------------------
# ICD LINES CRUD
# -----------------------

def add_icd_line(superbill_id: int, data: SuperbillICDCreate):
    conn = get_connection()
    cur = conn.cursor()

    payload = data.model_dump()
    payload["superbill_id"] = superbill_id

    cur.execute("""
        INSERT INTO superbill_icd_items (
            superbill_id, icd_code, description
        ) VALUES (
            :superbill_id, :icd_code, :description
        )
    """, payload)

    conn.commit()
    iid = cur.lastrowid
    conn.close()

    return get_icd_line(iid)


def get_icd_line(line_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM superbill_icd_items WHERE id = ?", (line_id,))
    row = cur.fetchone()
    conn.close()

    return dict_from_row(row) if row else None


def list_icd_lines(superbill_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM superbill_icd_items
        WHERE superbill_id = ?
        ORDER BY id ASC
    """, (superbill_id,))

    rows = cur.fetchall()
    conn.close()

    return [dict_from_row(r) for r in rows]


def delete_icd_line(line_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM superbill_icd_items WHERE id = ?", (line_id,))
    conn.commit()
    conn.close()

    return True