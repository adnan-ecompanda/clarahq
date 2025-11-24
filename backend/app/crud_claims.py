from typing import Dict, Any
from .database import get_connection, dict_from_row
from .crud_billing import get_superbill, superbill_exists


# --------------------------------------------------
# CREATE CLAIM FROM SUPERBILL
# --------------------------------------------------
def create_claim_from_superbill(sb_id: int) -> Dict[str, Any]:
    if not superbill_exists(sb_id):
        raise ValueError("Superbill does not exist")

    sb = get_superbill(sb_id)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO claims (
            superbill_id, patient_id, provider_id,
            status, created_at
        )
        VALUES (?, ?, ?, 'submitted', datetime('now'))
    """, (
        sb_id,
        sb["patient_id"],
        sb["provider_id"]
    ))

    claim_id = cur.lastrowid

    # Insert claim lines
    for c in sb["cpt_items"]:
        cur.execute("""
            INSERT INTO claim_lines (
                claim_id, cpt_code, units, amount, modifier, icd_pointer
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            claim_id,
            c["cpt_code"],
            c["units"],
            c["amount"],
            c["modifier"],
            c["icd_pointer"]
        ))

    conn.commit()
    conn.close()

    return get_claim(claim_id)


# --------------------------------------------------
# GET CLAIM
# --------------------------------------------------
def get_claim(claim_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    claim = dict_from_row(row)

    cur.execute("""
        SELECT cpt_code, units, amount, modifier, icd_pointer
        FROM claim_lines WHERE claim_id = ?
    """, (claim_id,))
    claim["lines"] = [dict_from_row(i) for i in cur.fetchall()]

    conn.close()
    return claim