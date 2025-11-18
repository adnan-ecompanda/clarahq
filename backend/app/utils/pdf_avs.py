from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    Flowable,
)
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from datetime import datetime
import os

# -------------------------------------------------------------
# BRAND CONSTANTS
# -------------------------------------------------------------
BRAND_BLUE = "#1F4E79"
BRAND_LIGHT = "#E6EEF7"
GRAY_TEXT = "#4A4A4A"
WATERMARK_TEXT = "CLARAHQ — CONFIDENTIAL MEDICAL DOCUMENT"
LOGO_PATH = "assets/logo.png"  # update if needed


# -------------------------------------------------------------
# WATERMARK LAYER
# -------------------------------------------------------------
class WatermarkCanvas:
    @staticmethod
    def apply(canvas, doc):
        canvas.saveState()

        width, height = doc.pagesize

        # Diagonal length of page
        diagonal = (width**2 + height**2) ** 0.5

        canvas.setFont("Helvetica-Bold", 42)

        # Text width (unscaled)
        text_width = canvas.stringWidth(WATERMARK_TEXT, "Helvetica-Bold", 42)

        # Scale required so text fits fully inside diagonal
        scale_factor = min(1.0, (diagonal * 0.75) / text_width)

        canvas.setFont("Helvetica-Bold", 42 * scale_factor)
        canvas.setFillColor(colors.Color(0.75, 0.75, 0.75, alpha=0.18))  # very soft

        # Move center
        canvas.translate(width / 2, height / 2)

        # Rotate
        canvas.rotate(45)

        # Draw centered
        canvas.drawCentredString(0, 0, WATERMARK_TEXT)

        canvas.restoreState()


# -------------------------------------------------------------
# MAIN GENERATOR
# -------------------------------------------------------------
def generate_avs_pdf(output_path, patient, encounter, vitals, meds, allergies, problems):
    styles = _styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    # -------------------------------------------------------------
    # HEADER
    # -------------------------------------------------------------
    if os.path.exists(LOGO_PATH):
        story.append(Image(LOGO_PATH, width=130, height=45))
    else:
        story.append(Paragraph("<b>ClaraHQ</b>", styles["TitleBrand"]))

    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("<b>AFTER VISIT SUMMARY (AVS)</b>", styles["MainTitle"]))
    story.append(_divider())
    story.append(Spacer(1, 0.15 * inch))

    # -------------------------------------------------------------
    # PATIENT INFO
    # -------------------------------------------------------------
    story.append(Paragraph("Patient Information", styles["SectionTitle"]))
    patient_info = [
        ["Full Name", f"{patient.first_name} {patient.last_name}"],
        ["DOB", patient.date_of_birth or "N/A"],
        ["Gender", patient.gender or "N/A"],
        ["Phone", patient.phone or "N/A"],
        ["Email", patient.email or "N/A"],
    ]
    story.append(_table(patient_info))
    story.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------------------
    # ENCOUNTER SUMMARY
    # -------------------------------------------------------------
    story.append(Paragraph("Visit Summary", styles["SectionTitle"]))
    encounter_info = [
        ["Visit Type", encounter.visit_type],
        ["Date", encounter.visit_date],
        ["Chief Complaint", encounter.chief_complaint or "N/A"],
    ]
    story.append(_table(encounter_info))
    story.append(Spacer(1, 0.2 * inch))

    # HPI + Exam + Assessment + Plan
    story += _text_block("History of Present Illness (HPI)", encounter.hpi, styles)
    story += _text_block("Objective Exam", encounter.objective_exam, styles)
    story += _text_block("Assessment", encounter.assessment, styles)
    story += _text_block("Plan", encounter.plan, styles)

    # -------------------------------------------------------------
    # VITALS
    # -------------------------------------------------------------
    story.append(Paragraph("Vitals", styles["SectionTitle"]))

    vitals_data = [
        ["Blood Pressure", f"{vitals.get('bp_systolic', '-')} / {vitals.get('bp_diastolic', '-')}"],
        ["Heart Rate", vitals.get("heart_rate", "-")],
        ["Resp. Rate", vitals.get("respiratory_rate", "-")],
        ["Temperature", vitals.get("temperature", "-")],
        ["SpO₂", vitals.get("spo2", "-")],
        ["Weight", vitals.get("weight", "-")],
        ["Height", vitals.get("height", "-")],
        ["BMI", vitals.get("bmi", "-")],
    ]

    story.append(_table(vitals_data))
    story.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------------------
    # MEDICATIONS
    # -------------------------------------------------------------
    story.append(Paragraph("Medications", styles["SectionTitle"]))

    if meds:
        med_rows = [["Name", "Strength", "Frequency", "Status"]]
        for m in meds:
            med_rows.append([
                m["medication_name"],
                m["strength"],
                m["frequency"],
                m["status"],
            ])
        story.append(_table(med_rows))
    else:
        story.append(Paragraph("No medications listed.", styles["Body"]))

    story.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------------------
    # ALLERGIES
    # -------------------------------------------------------------
    story.append(Paragraph("Allergies", styles["SectionTitle"]))

    if allergies:
        allergy_rows = [["Allergen", "Reaction", "Severity"]]
        for a in allergies:
            allergy_rows.append([a["allergen"], a["reaction"], a["severity"]])
        story.append(_table(allergy_rows))
    else:
        story.append(Paragraph("No allergies recorded.", styles["Body"]))

    story.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------------------
    # PROBLEMS
    # -------------------------------------------------------------
    story.append(Paragraph("Active Problems", styles["SectionTitle"]))

    if problems:
        problem_rows = [["Condition", "ICD-10", "Status"]]
        for p in problems:
            problem_rows.append([p["description"], p["icd10_code"], p["status"]])
        story.append(_table(problem_rows))
    else:
        story.append(Paragraph("No active problems.", styles["Body"]))

    story.append(Spacer(1, 0.35 * inch))

    # -------------------------------------------------------------
    # QR CODE BLOCK
    # -------------------------------------------------------------
    story.append(Paragraph("Scan for Full Records", styles["SectionTitle"]))
    story.append(_qr_block(f"https://clarahq.com/patient/{patient.id}/records"))
    story.append(Spacer(1, 0.4 * inch))

    # -------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------
    story.append(_divider())
    story.append(Paragraph(
        f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Body"]
    ))
    story.append(Paragraph("<b>Provider:</b> ClaraHQ Care Team", styles["Body"]))

    # Build with watermark
    doc.build(story, onFirstPage=WatermarkCanvas.apply, onLaterPages=WatermarkCanvas.apply)


# -------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------
def _divider():
    class Divider(Flowable):
        def draw(self):
            self.canv.setStrokeColor(colors.HexColor(BRAND_BLUE))
            self.canv.setLineWidth(2)
            self.canv.line(0, 0, 500, 0)
    return Divider()


def _qr_block(url):
    qr_code = qr.QrCodeWidget(url)
    bounds = qr_code.getBounds()
    size = 100
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    d = Drawing(size, size)
    d.add(qr_code, name="qr")
    return d


def _text_block(title, text, styles):
    return [
        Paragraph(title, styles["SectionTitle"]),
        Paragraph(text or "N/A", styles["Body"]),
        Spacer(1, 0.2 * inch)
    ]


def _table(rows):
    tbl = Table(rows, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRAND_BLUE)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9AA1A9")),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
    ]))
    return tbl


def _styles():
    base = getSampleStyleSheet()

    return {
        "TitleBrand": ParagraphStyle(
            name="TitleBrand",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor(BRAND_BLUE),
            spaceAfter=10,
        ),
        "MainTitle": ParagraphStyle(
            name="MainTitle",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor(BRAND_BLUE),
            alignment=1,
            spaceAfter=12,
        ),
        "SectionTitle": ParagraphStyle(
            name="SectionTitle",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor(BRAND_BLUE),
            spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "Body": ParagraphStyle(
            name="Body",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor(GRAY_TEXT),
        ),
    }