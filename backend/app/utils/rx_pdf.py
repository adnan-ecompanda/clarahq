from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

PDF_DIR = "assets/prescriptions"
os.makedirs(PDF_DIR, exist_ok=True)


def generate_rx_pdf(rx: dict):
    file_path = f"{PDF_DIR}/rx_{rx['id']}.pdf"

    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)

    y = 750

    c.drawString(50, y, "ClaraHQ Prescription")
    y -= 30

    c.drawString(50, y, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    y -= 20

    c.drawString(50, y, f"Patient: {rx['patient_id']}")
    y -= 20

    c.drawString(50, y, f"Medication: {rx['medication_name']} {rx['dose']}")
    y -= 20

    c.drawString(50, y, f"Route: {rx['route']}  Frequency: {rx['frequency']}")
    y -= 20

    c.drawString(50, y, f"Quantity: {rx['quantity']}  Refills: {rx['refills']}")
    y -= 20

    c.drawString(50, y, f"Instructions: {rx['instructions']}")
    y -= 20

    c.drawString(50, y, f"Diagnosis: {rx['diagnosis']}")
    y -= 40

    c.drawString(50, y, "Provider Signature: _______________________")
    c.save()

    return file_path