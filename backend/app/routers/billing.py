from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

from ..schemas_billing import SuperbillCreate, SuperbillResponse
from ..crud_billing import (
    create_superbill,
    get_superbill_by_id,
    list_superbills,
    update_superbill_status,
    generate_superbill_pdf,
    cms1500_json,
    generate_x12
)

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.post("/superbills", response_model=SuperbillResponse)
def create_sb(payload: SuperbillCreate):
    sb = create_superbill(payload)
    if not sb:
        raise HTTPException(status_code=400, detail="Unable to create superbill")
    return sb

@router.get("/superbills/{sb_id}", response_model=SuperbillResponse)
def get_sb(sb_id: int):
    sb = get_superbill_by_id(sb_id)
    if not sb:
        raise HTTPException(status_code=404, detail="Superbill not found")
    return sb

@router.get("/superbills", response_model=List[SuperbillResponse])
def list_sb():
    return list_superbills()

@router.put("/superbills/{sb_id}/status", response_model=SuperbillResponse)
def update_sb_status(sb_id: int, payload: Dict[str, str]):
    status = payload.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Missing 'status'")
    sb = update_superbill_status(sb_id, status)
    if not sb:
        raise HTTPException(status_code=404, detail="Superbill not found")
    return sb

@router.get("/superbills/{sb_id}/pdf")
def superbill_pdf(sb_id: int):
    sb = get_superbill_by_id(sb_id)
    if not sb:
        raise HTTPException(status_code=404, detail="Superbill not found")
    pdf_b64 = generate_superbill_pdf(sb_id)
    return {"superbill_id": sb_id, "pdf_base64": pdf_b64}

@router.get("/superbills/{sb_id}/cms1500")
def superbill_cms1500(sb_id: int):
    sb = get_superbill_by_id(sb_id)
    if not sb:
        raise HTTPException(status_code=404, detail="Superbill not found")
    return cms1500_json(sb_id)

@router.get("/superbills/{sb_id}/x12")
def superbill_x12(sb_id: int):
    sb = get_superbill_by_id(sb_id)
    if not sb:
        raise HTTPException(status_code=404, detail="Superbill not found")
    return {"superbill_id": sb_id, "x12": generate_x12(sb_id)}
