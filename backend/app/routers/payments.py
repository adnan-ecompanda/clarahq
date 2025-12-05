import os
from fastapi import APIRouter, Depends, HTTPException
from ..schemas_payments import PaymentCreate, PaymentAllocation, RefundCreate
from ..crud_payments import (
    create_payment, 
    list_payments_for_patient,
    allocate_payment
)

from fastapi.responses import FileResponse
from ..auth import get_current_user, require_roles
from ..schemas_payments import PaymentRefundRequest, PaymentLedgerResponse
from ..crud_payments import (
    create_payment_refund,
    generate_payment_receipt,
    get_patient_ledger,
)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/patient")
def create_patient_payment(payload: PaymentCreate, user=Depends(get_current_user)):
    return create_payment(payload)


@router.get("/patient/{patient_id}")
def get_patient_payments(patient_id: int, user=Depends(get_current_user)):
    return list_payments_for_patient(patient_id)


@router.post("/allocate")
def allocate_payment_api(payload: PaymentAllocation, user=Depends(get_current_user)):
    return allocate_payment(payload)

@router.post("/{payment_id}/refund", summary="Refund a payment")
def refund_payment_endpoint(
    payment_id: int,
    payload: PaymentRefundRequest,
    current_user=Depends(get_current_user),
):
    # Optional role check; adjust to your roles
    require_roles(current_user, ["admin", "billing", "front_desk"])

    try:
        refund = create_payment_refund(payment_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return refund

@router.get("/{payment_id}/receipt", summary="Download payment receipt as PDF")
def get_payment_receipt(
    payment_id: int,
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["admin", "billing", "front_desk"])

    try:
        pdf_path = generate_payment_receipt(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Receipt file not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )

@router.get("/patient/{patient_id}/ledger", response_model=PaymentLedgerResponse,
            summary="Get patient financial ledger")
def patient_ledger_endpoint(
    patient_id: int,
    current_user=Depends(get_current_user),
):
    require_roles(current_user, ["admin", "billing", "front_desk", "provider"])

    try:
        return get_patient_ledger(patient_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))