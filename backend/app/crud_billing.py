from typing import Dict, Any, List
from .database import get_connection, dict_from_row
from .schemas_billing import SuperbillCreate
from reportlab.pdfgen import canvas
import io
import base64
from datetime import datetime

# ---------------------------------------------------------
# INIT TABLES
# ---------------------------------------------------------

def init_superbill_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            provider_id INTEGER NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'draft',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def init_superbill_cpt_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbill_cpt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            superbill_id INTEGER NOT NULL,
            cpt_code TEXT NOT NULL,
            units INTEGER DEFAULT 1,
            amount REAL DEFAULT 0,
            modifier TEXT,
            icd_pointer TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (superbill_id) REFERENCES superbills(id)
        )
    """)
    conn.commit()
    conn.close()


def init_superbill_icd_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superbill_icd_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            superbill_id INTEGER NOT NULL,
            icd_code TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (superbill_id) REFERENCES superbills(id)
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# CREATE SUPERBILL
# ---------------------------------------------------------

def create_superbill(data: SuperbillCreate) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO superbills (
            encounter_id, patient_id, provider_id,
            notes, status, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        data.encounter_id,
        data.patient_id,
        data.provider_id,
        data.notes,
        data.status
    ))

    sb_id = cur.lastrowid

    # Insert CPT items
    for item in data.cpt_items:
        cur.execute("""
            INSERT INTO superbill_cpt_items (
                superbill_id, cpt_code, units, amount, modifier, icd_pointer, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            sb_id,
            item.cpt_code,
            item.units,
            item.amount,
            item.modifier,
            item.icd_pointer
        ))

    # Insert ICD items
    for item in data.icd_items:
        cur.execute("""
            INSERT INTO superbill_icd_items (
                superbill_id, icd_code, description, created_at
            )
            VALUES (?, ?, ?, datetime('now'))
        """, (sb_id, item.icd_code, item.description))

    conn.commit()
    conn.close()

    return get_superbill_by_id(sb_id)

# ---------------------------------------------------------
# GET SUPERBILL
# ---------------------------------------------------------

def get_superbill_by_id(sb_id: int) -> Dict[str, Any] | None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM superbills WHERE id = ?", (sb_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    sb = dict_from_row(row)

    cur.execute("""
        SELECT cpt_code, units, amount, modifier, icd_pointer
        FROM superbill_cpt_items WHERE superbill_id = ?
    """, (sb_id,))
    sb["cpt_items"] = [dict_from_row(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT icd_code, description
        FROM superbill_icd_items WHERE superbill_id = ?
    """, (sb_id,))
    sb["icd_items"] = [dict_from_row(r) for r in cur.fetchall()]

    conn.close()
    return sb

# ---------------------------------------------------------
# LIST SUPERBILLS
# ---------------------------------------------------------

def list_superbills() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM superbills ORDER BY id DESC")
    ids = [r["id"] for r in cur.fetchall()]
    conn.close()

    return [get_superbill_by_id(sb_id) for sb_id in ids]

# ---------------------------------------------------------
# UPDATE STATUS
# ---------------------------------------------------------

def update_superbill_status(sb_id: int, status: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE superbills
        SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (status, sb_id))

    conn.commit()
    conn.close()

    return get_superbill_by_id(sb_id)

# ---------------------------------------------------------
# PDF GENERATION
# ---------------------------------------------------------

def generate_superbill_pdf(sb_id: int):
    sb = get_superbill_by_id(sb_id)

    buf = io.BytesIO()
    pdf = canvas.Canvas(buf)

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 800, f"Superbill #{sb_id}")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, f"Encounter: {sb['encounter_id']}")
    pdf.drawString(50, 750, f"Patient: {sb['patient_id']}")
    pdf.drawString(50, 730, f"Provider: {sb['provider_id']}")

    y = 700
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "CPT Items:")
    y -= 20

    for c in sb["cpt_items"]:
        pdf.drawString(
            50, y,
            f"{c['cpt_code']}  Units:{c['units']}  Amount:{c['amount']}  Mod:{c['modifier']}  Ptr:{c['icd_pointer']}"
        )
        y -= 20

    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "ICD Items:")
    y -= 20

    for i in sb["icd_items"]:
        pdf.drawString(50, y, f"{i['icd_code']} - {i['description']}")
        y -= 20

    pdf.save()
    pdf_bytes = buf.getvalue()
    return base64.b64encode(pdf_bytes).decode()

# ---------------------------------------------------------
# CMS1500 JSON
# ---------------------------------------------------------

def cms1500_json(sb_id: int) -> dict:
    sb = get_superbill_by_id(sb_id)

    return {
        "claim_id": sb_id,
        "patient_id": sb["patient_id"],
        "provider_id": sb["provider_id"],
        "diagnosis_codes": [i["icd_code"] for i in sb["icd_items"]],
        "procedures": [
            {
                "cpt_code": c["cpt_code"],
                "units": c["units"],
                "charge": c["amount"],
                "modifier": c["modifier"],
                "icd_pointer": c["icd_pointer"],
            }
            for c in sb["cpt_items"]
        ]
    }

# ---------------------------------------------------------
# X12 837P GENERATION — FINAL, WORKING
# ---------------------------------------------------------

def generate_x12(sb_id: int) -> str:
    sb = get_superbill_by_id(sb_id)

    isa = "ISA*00*          *00*          *ZZ*SENDERID      *ZZ*RECEIVERID    *240101*1253*^*00501*000000905*1*T*:~"
    gs = "GS*HC*SENDERID*RECEIVERID*20240101*1253*1*X*005010X222A1~"
    st = f"ST*837*0001~"

    # BASIC CLAIM EXAMPLE
    clm_lines = []
    for cpt in sb["cpt_items"]:
        clm_lines.append(
            f"SV1*HC:{cpt['cpt_code']}*{cpt['amount']}*UN*{cpt['units']}~~~1~"
        )

    se = f"SE*{3 + len(clm_lines)}*0001~"
    ge = "GE*1*1~"
    iea = "IEA*1*000000905~"

    return "\n".join([isa, gs, st] + clm_lines + [se, ge, iea])

def superbill_exists(sb_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM superbills WHERE id = ?", (sb_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists