import os
import sqlite3
from datetime import datetime
import base64, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .database import get_connection

UPLOAD_ROOT = os.path.abspath("uploads")
RX_DIR = os.path.join(UPLOAD_ROOT, "prescriptions")
SIGNATURE_DIR = os.path.join(RX_DIR, "signatures")

os.makedirs(RX_DIR, exist_ok=True)
os.makedirs(SIGNATURE_DIR, exist_ok=True)


def safe_b64decode(data: str) -> bytes:
    """
    Safely decode base64 strings:
    - Removes 'data:image/...;base64,' prefix
    - Removes whitespace/newlines
    - Fixes missing '=' padding
    """
    if not data:
        raise ValueError("Empty base64 string")

    # Remove data URL prefix (if exists)
    data = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", data)

    # Remove all whitespace / newlines
    data = re.sub(r"\s+", "", data)

    # Base64 must be divisible by 4 -> fix padding
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += "=" * (4 - missing_padding)

    # Decode (non-strict – same as consent code that works)
    return base64.b64decode(data, validate=False)


# -----------------------------------------------------
# INIT TABLE
# -----------------------------------------------------
def init_prescription_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        encounter_id INTEGER,
        provider_id INTEGER,
        medication_name TEXT,
        dosage TEXT,
        route TEXT,
        frequency TEXT,
        duration TEXT,
        quantity TEXT,
        refills INTEGER,
        instructions TEXT,
        status TEXT DEFAULT 'draft',
        provider_signature_path TEXT,
        rx_pdf_path TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        signed_at TEXT
    )
    """)

    conn.commit()


# -----------------------------------------------------
# Create Prescription (Draft)
# -----------------------------------------------------
def create_prescription(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prescriptions (
            patient_id, encounter_id, medication_name, dosage, route,
            frequency, duration, quantity, refills, instructions
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.patient_id,
        data.encounter_id,
        data.medication_name,
        data.dosage,
        data.route,
        data.frequency,
        data.duration,
        data.quantity,
        data.refills,
        data.instructions
    ))

    conn.commit()
    return {"prescription_id": cur.lastrowid}


# -----------------------------------------------------
# Sign Prescription
# -----------------------------------------------------
def sign_prescription(prescription_id, data):
    import base64, re, os
    from io import BytesIO
    from PIL import Image
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from datetime import datetime

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT patient_id, medication_name FROM prescriptions WHERE id = ?", (prescription_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "Prescription not found"}

    # --- CLEAN BASE64 ---
    raw_b64 = data.signature_base64
    if "," in raw_b64:
        raw_b64 = raw_b64.split(",", 1)[1]

    raw_b64 = re.sub(r"[^A-Za-z0-9+/=]", "", raw_b64)
    pad = len(raw_b64) % 4
    if pad:
        raw_b64 += "=" * (4 - pad)

    try:
        decoded = base64.b64decode(raw_b64)
    except:
        return {"error": "Base64 decode failed"}

    # --- LOAD AS PIL ---
    try:
        img = Image.open(BytesIO(decoded))
    except:
        return {"error": "Invalid or corrupt signature image"}

    # --- FIX: convert to JPG (ReportLab compatible) ---
    rgb_img = img.convert("RGB")

    sig_filename = f"rx_sig_{prescription_id}_{datetime.now().timestamp()}.jpg"
    sig_path = os.path.join(SIGNATURE_DIR, sig_filename)

    os.makedirs(SIGNATURE_DIR, exist_ok=True)
    rgb_img.save(sig_path, "JPEG", quality=95)

    # --- GENERATE PDF ---
    pdf_filename = f"rx_{prescription_id}.pdf"
    pdf_path = os.path.join(RX_DIR, pdf_filename)

    os.makedirs(RX_DIR, exist_ok=True)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(50, 750, "PRESCRIPTION")
    c.drawString(50, 730, f"Patient ID: {row[0]}")
    c.drawString(50, 710, f"Medication: {row[1]}")
    c.drawString(50, 610, "Provider Signature:")

    # Using the JPG image
    c.drawImage(sig_path, 50, 540, width=200, height=80)

    c.showPage()
    c.save()

    cur.execute("""
        UPDATE prescriptions
        SET provider_id = ?, provider_signature_path = ?, rx_pdf_path = ?, 
            status = 'signed', signed_at = ?
        WHERE id = ?
    """, (data.provider_id, sig_filename, pdf_filename, data.signed_at, prescription_id))

    conn.commit()

    return {"status": "signed", "signature": sig_filename, "pdf": pdf_filename}


# -----------------------------------------------------
# Get PDF path
# -----------------------------------------------------
def get_rx_pdf(prescription_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT rx_pdf_path FROM prescriptions WHERE id = ?", (prescription_id,))
    row = cur.fetchone()

    if not row or not row[0]:
        return None

    return os.path.join(RX_DIR, row[0])


# -----------------------------------------------------
# Get full prescription
# -----------------------------------------------------
def get_prescription(prescription_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM prescriptions WHERE id = ?", (prescription_id,))
    row = cur.fetchone()
    return row


# -----------------------------------------------------
# List for patient
# -----------------------------------------------------
def list_prescriptions_for_patient(patient_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM prescriptions WHERE patient_id = ?", (patient_id,))
    return cur.fetchall()
