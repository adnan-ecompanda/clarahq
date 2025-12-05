import sqlite3
from datetime import datetime
from .database import get_connection
from .schemas_payments import PaymentCreate, PaymentAllocation
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .database import get_connection
from .schemas_payments import PaymentRefundRequest, PaymentLedgerItem, PaymentLedgerResponse
import os

def init_payment_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Master payment table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        encounter_id INTEGER,
        payment_method TEXT,
        amount REAL NOT NULL,
        note TEXT,
        reference TEXT,
        status TEXT DEFAULT 'COMPLETED',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Allocation table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER NOT NULL,
        claim_id INTEGER,
        encounter_id INTEGER,
        allocated_amount REAL NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_refunds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(payment_id) REFERENCES payments(id)
    )
    """)

    conn.commit()

def create_payment(data: PaymentCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payments (patient_id, encounter_id, amount, payment_method, note)
        VALUES (?, ?, ?, ?, ?)
    """, (data.patient_id, data.encounter_id, data.amount, data.payment_method, data.note))

    conn.commit()
    return {"payment_id": cur.lastrowid}

def list_payments_for_patient(patient_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments WHERE patient_id = ?", (patient_id,))
    rows = cur.fetchall()

    return [dict(zip([c[0] for c in cur.description], r)) for r in rows]


def allocate_payment(data: PaymentAllocation):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payment_allocations (payment_id, claim_id, encounter_id, allocated_amount)
        VALUES (?, ?, ?, ?)
    """, (data.payment_id, data.claim_id, data.encounter_id, data.allocated_amount))

    conn.commit()
    return {"allocation_id": cur.lastrowid}

# ===============================
# Refunds
# ===============================

def create_payment_refund(payment_id: int, data: PaymentRefundRequest):
    conn = get_connection()
    cur = conn.cursor()

    # 1) Get original payment
    cur.execute("""
        SELECT id, patient_id, amount
        FROM payments
        WHERE id = ?
    """, (payment_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("Payment not found")

    original_amount = row[2]

    # 2) Decide refund amount
    refund_amount = data.amount if data.amount is not None else original_amount
    if refund_amount <= 0:
        raise ValueError("Refund amount must be positive")

    # 3) Insert refund record
    cur.execute("""
        INSERT INTO payment_refunds (payment_id, amount, reason)
        VALUES (?, ?, ?)
    """, (payment_id, refund_amount, data.reason))

    refund_id = cur.lastrowid

    # 4) Optionally update payment status if full refund
    try:
        if abs(refund_amount - original_amount) < 0.01:  # full refund
            cur.execute("""
                UPDATE payments
                SET status = 'REFUNDED'
                WHERE id = ?
            """, (payment_id,))
    except sqlite3.OperationalError:
        # if 'status' column doesn't exist, silently ignore
        pass

    conn.commit()

    # Return simple dict; router can convert it if needed
    cur.execute("""
        SELECT id, payment_id, amount, reason, created_at
        FROM payment_refunds
        WHERE id = ?
    """, (refund_id,))
    r = cur.fetchone()
    return {
        "id": r[0],
        "payment_id": r[1],
        "amount": r[2],
        "reason": r[3],
        "created_at": r[4],
    }

# ===============================
# Receipt PDF
# ===============================

RECEIPT_ROOT = os.path.abspath("uploads")
RECEIPT_DIR = os.path.join(RECEIPT_ROOT, "payments", "receipts")
os.makedirs(RECEIPT_DIR, exist_ok=True)


def generate_payment_receipt(payment_id: int) -> str:
    """
    Generate a simple payment receipt PDF for the given payment_id.
    Returns the absolute path to the PDF.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, patient_id, encounter_id, amount, payment_method, status, reference, created_at
        FROM payments
        WHERE id = ?
    """, (payment_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("Payment not found")

    (pid, patient_id, encounter_id, amount, payment_method, status, ref, created_at) = row

    # sum of refunds (if any)
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM payment_refunds
        WHERE payment_id = ?
    """, (payment_id,))
    refund_total = cur.fetchone()[0] or 0.0
    net_amount = amount - refund_total

    # Build PDF file
    filename = f"receipt_payment_{payment_id}.pdf"
    pdf_path = os.path.join(RECEIPT_DIR, filename)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 770, "Payment Receipt")

    c.setFont("Helvetica", 11)
    y = 740
    c.drawString(50, y, f"Payment ID: {pid}"); y -= 20
    c.drawString(50, y, f"Patient ID: {patient_id}"); y -= 20
    c.drawString(50, y, f"Encounter ID: {encounter_id or '-'}"); y -= 20
    c.drawString(50, y, f"Original Amount: ${amount:0.2f}"); y -= 20
    c.drawString(50, y, f"Refunds: ${refund_total:0.2f}"); y -= 20
    c.drawString(50, y, f"Net Amount: ${net_amount:0.2f}"); y -= 20
    c.drawString(50, y, f"Method: {payment_method or '-'}"); y -= 20
    c.drawString(50, y, f"Status: {status or '-'}"); y -= 20
    c.drawString(50, y, f"Reference: {ref or '-'}"); y -= 20
    c.drawString(50, y, f"Created At: {created_at}"); y -= 30

    c.drawString(50, y, "Thank you for your payment.")
    c.showPage()
    c.save()

    return pdf_path

# ===============================
# Patient Ledger
# ===============================

def get_patient_ledger(patient_id: int) -> PaymentLedgerResponse:
    conn = get_connection()
    cur = conn.cursor()

    items = []

    # 1) Charges – from claims (if table/columns exist)
    try:
        cur.execute("""
            SELECT id, service_date, total_amount
            FROM claims
            WHERE patient_id = ?
        """, (patient_id,))
        for cid, service_date, total_amount in cur.fetchall():
            items.append(PaymentLedgerItem(
                date=service_date or "",
                type="CHARGE",
                description=f"Claim #{cid}",
                amount=float(total_amount or 0),
                reference=str(cid),
            ))
    except sqlite3.OperationalError:
        # if claims table/columns differ, we just skip charges
        pass

    # 2) Payments
    cur.execute("""
        SELECT id, created_at, amount, payment_method, reference
        FROM payments
        WHERE patient_id = ?
    """, (patient_id,))
    for pid, created_at, amount, payment_method, ref in cur.fetchall():
        items.append(PaymentLedgerItem(
            date=created_at or "",
            type="PAYMENT",
            description=f"Payment ({payment_method or 'unknown'})",
            amount=-float(amount or 0),  # payments reduce balance
            reference=ref,
        ))

        # 3) Refunds for each payment
        cur.execute("""
            SELECT id, created_at, amount, reason
            FROM payment_refunds
            WHERE payment_id = ?
        """, (pid,))
        for rid, r_created, r_amount, reason in cur.fetchall():
            items.append(PaymentLedgerItem(
                date=r_created or "",
                type="REFUND",
                description=f"Refund for payment {pid}: {reason or ''}",
                amount=float(r_amount or 0),  # refund increases balance
                reference=str(rid),
            ))

    # Sort by date if possible
    items_sorted = sorted(items, key=lambda x: x.date or "")

    balance = sum(i.amount for i in items_sorted)

    return PaymentLedgerResponse(
        patient_id=patient_id,
        items=items_sorted,
        balance=balance
    )