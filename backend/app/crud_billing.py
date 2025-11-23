# crud_billing.py

from typing import Dict, Any, List
from .database import get_connection, dict_from_row
from .schemas_billing import SuperbillCreate
from reportlab.pdfgen import canvas
import io
import base64


# ------------------------
# CREATE SUPERBILL
# ------------------------
def create_superbill(data: SuperbillCreate) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    # Insert superbill
    cur.execute("""
        INSERT INTO superbills (
            encounter_id, patient_id, provider_id,
            notes, status, active, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'))
    """, (
        data.encounter_id,
        data.patient_id,
        data.provider_id,
        data.notes,
        data.status
    ))

    sb_id = cur.lastrowid

    # CPT items
    for item in data.cpt_items:
        cur.execute("""
            INSERT INTO superbill_cpt_items (
                superbill_id, cpt_code, units, amount, modifier,
                pointer, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            sb_id,
            item.cpt_code,
            item.units,
            item.amount,
            item.modifier,
            item.pointer
        ))

    # ICD items
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


# ------------------------
# GET SUPERBILL
# ------------------------
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
        SELECT cpt_code, units, amount, modifier, pointer
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


# ------------------------
# LIST SUPERBILLS
# ------------------------
def list_superbills() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM superbills ORDER BY id DESC")
    ids = [r["id"] for r in cur.fetchall()]

    conn.close()
    return [get_superbill_by_id(sb_id) for sb_id in ids]


# ------------------------
# UPDATE STATUS
# ------------------------
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


# ------------------------
# PDF GENERATOR
# ------------------------
def generate_superbill_pdf(sb_id: int) -> str:
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

    pdf.setFont("Helvetica", 12)
    for c in sb["cpt_items"]:
        pdf.drawString(
            50, y,
            f"{c['cpt_code']}  Units:{c['units']}  Amount:{c['amount']}  Mod:{c['modifier']}  Ptr:{c['pointer']}"
        )
        y -= 20

    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "ICD Items:")
    y -= 20

    pdf.setFont("Helvetica", 12)
    for i in sb["icd_items"]:
        pdf.drawString(50, y, f"{i['icd_code']} - {i['description']}")
        y -= 20

    pdf.save()
    pdf_bytes = buf.getvalue()

    return base64.b64encode(pdf_bytes).decode()


# ------------------------
# CMS-1500 JSON (Minimal Working)
# ------------------------
def cms1500_json(sb_id: int) -> Dict[str, Any]:
    sb = get_superbill_by_id(sb_id)
    return {
        "claim_id": sb_id,
        "patient_id": sb["patient_id"],
        "provider_id": sb["provider_id"],
        "diagnosis_codes": [i["icd_code"] for i in sb["icd_items"]],
        "procedures": [
            {
                "cpt": c["cpt_code"],
                "units": c["units"],
                "charge": c["amount"],
                "modifier": c["modifier"],
                "pointer": c["pointer"],
            }
            for c in sb["cpt_items"]
        ]
    }


# ------------------------
# X12 837P GENERATOR (simple)
# ------------------------
def generate_x12(sb_id: int) -> str:
    sb = get_superbill_by_id(sb_id)
    segments = []

    segments.append("ISA*00*          *00*          *ZZ*SENDERID      *ZZ*RECEIVERID    *000000*0000*^*00501*000000905*1*T*:~")
    segments.append("GS*HC*SENDER*RECEIVER*20250101*0000*1*X*005010X222A1~")
    segments.append("ST*837*0001*005010X222A1~")

    # Loop 2300 Claim Information
    segments.append(f"CLM*{sb_id}*0***11:B:1*Y*A*Y*Y~")

    # ICD pointers
    for i in sb["icd_items"]:
        segments.append(f"HI*ABK:{i['icd_code']}~")

    # CPT lines
    for c in sb["cpt_items"]:
        segments.append(
            f"SV1*HC:{c['cpt_code']}:{c['modifier']}*{c['amount']}*UN*{c['units']}***1~"
        )

    segments.append("SE*23*0001~")
    segments.append("GE*1*1~")
    segments.append("IEA*1*000000905~")

    return "\n".join(segments)

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
            pointer TEXT,
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
