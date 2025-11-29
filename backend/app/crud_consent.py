import os
import base64, re
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import io

from .database import get_connection


UPLOAD_ROOT = os.path.abspath("uploads")
SIGNATURE_DIR = os.path.join(UPLOAD_ROOT, "signatures")
CONSENT_DIR = os.path.join(UPLOAD_ROOT, "consents")

os.makedirs(SIGNATURE_DIR, exist_ok=True)
os.makedirs(CONSENT_DIR, exist_ok=True)


def init_consent_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS consent_forms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        consent_type TEXT,
        html_content TEXT,
        signature_path TEXT,
        pdf_path TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        signed_at TEXT
    )
    """)

    conn.commit()


# -------------------------
# Create Consent Form
# -------------------------
def create_consent(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO consent_forms (patient_id, consent_type, html_content)
        VALUES (?, ?, ?)
    """, (
        data.patient_id,
        data.consent_type,
        data.html_content
    ))
    conn.commit()
    return {"consent_id": cur.lastrowid}


# -------------------------
# Sign Consent Form
# -------------------------
def sign_consent(consent_id, data):
    conn = get_connection()
    cur = conn.cursor()

    # Fetch consent record
    cur.execute("SELECT id, patient_id, consent_type FROM consent_forms WHERE id = ?", (consent_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "Consent not found"}

    # === Decode signature safely ===
    sig_bytes = safe_b64decode(data.signature_base64)

    sig_filename = f"signature_{consent_id}_{int(datetime.now().timestamp())}.png"
    sig_path = os.path.join(SIGNATURE_DIR, sig_filename)

    # Save raw bytes
    with open(sig_path, "wb") as f:
        f.write(sig_bytes)

    # === Validate image ===
    from PIL import Image
    import io

    is_valid_signature = True
    try:
        Image.open(io.BytesIO(sig_bytes)).verify()
    except Exception:
        is_valid_signature = False

    # === Generate PDF ===
    pdf_filename = f"consent_{consent_id}.pdf"
    pdf_path = os.path.join(CONSENT_DIR, pdf_filename)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(50, 750, f"Consent Form - {row[2]}")
    c.drawString(50, 730, f"Patient ID: {row[1]}")
    c.drawString(50, 710, f"Signed At: {data.signed_at}")

    if is_valid_signature:
        # Try embedding signature
        try:
            c.drawString(50, 680, "Signature:")
            c.drawImage(sig_path, 50, 600, width=200, height=100)
        except Exception:
            # If ReportLab fails to embed → show placeholder
            c.drawString(50, 680, "Signature (Image Corrupted)")
    else:
        # If base64 is invalid
        c.drawString(50, 680, "Signature (Invalid / Not Renderable)")

    c.showPage()
    c.save()

    # === Update DB ===
    cur.execute("""
        UPDATE consent_forms
        SET signature_path = ?, pdf_path = ?, signed_at = ?
        WHERE id = ?
    """, (sig_filename, pdf_filename, data.signed_at, consent_id))

    conn.commit()

    return {
        "status": "signed",
        "signature_valid": is_valid_signature,
        "pdf_path": pdf_filename,
        "signature_path": sig_filename
    }


# -------------------------
# Get Consent Record
# -------------------------
def get_consent(consent_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, patient_id, consent_type, html_content, signature_path,
               pdf_path, created_at, signed_at
        FROM consent_forms
        WHERE id = ?
    """, (consent_id,))

    row = cur.fetchone()
    if not row:
        return None

    keys = ["id", "patient_id", "consent_type", "html_content", "signature_path",
            "pdf_path", "created_at", "signed_at"]

    return dict(zip(keys, row))

import base64
import re

def safe_b64decode(data: str) -> bytes:
    """
    Safely decode base64 strings:
    - Removes 'data:image/...;base64,' prefix
    - Removes whitespace/newlines
    - Fixes missing '=' padding
    - Validates base64 length
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

    try:
        return base64.b64decode(data, validate=False)
    except Exception as e:
        raise ValueError(f"Invalid base64 format: {e}")