# routers/billing.py
from fastapi import APIRouter, HTTPException
from app.schemas_billing import SuperbillCreate, SuperbillResponse
from app.crud_billing import (
    create_superbill, list_superbills, get_superbill_by_id,
    update_superbill_status, generate_superbill_pdf,
    cms1500_json, generate_x12
)

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/superbills", response_model=SuperbillResponse)
def create_sb(payload: SuperbillCreate):
    sb = create_superbill(payload)
    return sb


@router.get("/superbills", response_model=list[SuperbillResponse])
def list_sb():
    return list_superbills()


@router.get("/superbills/{sb_id}", response_model=SuperbillResponse)
def get_sb(sb_id: int):
    sb = get_superbill_by_id(sb_id)
    if not sb:
        raise HTTPException(404, "Superbill not found")
    return sb


@router.put("/superbills/{sb_id}/status")
def update_status(sb_id: int, status: str):
    sb = update_superbill_status(sb_id, status)
    return {"message": "updated", "superbill": sb}


@router.get("/superbills/{sb_id}/pdf")
def pdf(sb_id: int):
    encoded = generate_superbill_pdf(sb_id)
    return {"superbill_id": sb_id, "pdf_base64": encoded}


@router.get("/superbills/{sb_id}/cms1500")
def cms1500(sb_id: int):
    return cms1500_json(sb_id)


@router.get("/superbills/{sb_id}/x12")
def x12(sb_id: int):
    return {"x12": generate_x12(sb_id)}