from fastapi import APIRouter, HTTPException
from ..crud_billing import (
    create_superbill,
    get_superbill_by_id,
    list_superbills,
    update_superbill_status,
    generate_superbill_pdf,
    cms1500_json,
    generate_x12
)
from ..schemas_billing import SuperbillCreate

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/superbills")
def create_sb(payload: SuperbillCreate):
    sb = create_superbill(payload)
    return sb


@router.get("/superbills")
def all_sb():
    return list_superbills()


@router.get("/superbills/{sb_id}")
def get_sb(sb_id: int):
    sb = get_superbill_by_id(sb_id)
    if not sb:
        raise HTTPException(status_code=404, detail="Superbill not found")
    return sb


@router.put("/superbills/{sb_id}/status/{status}")
def update_status(sb_id: int, status: str):
    sb = update_superbill_status(sb_id, status)
    return sb


@router.get("/superbills/{sb_id}/pdf")
def pdf(sb_id: int):
    encoded_pdf = generate_superbill_pdf(sb_id)
    return {"pdf_base64": encoded_pdf}


@router.get("/superbills/{sb_id}/cms1500")
def cms(sb_id: int):
    return cms1500_json(sb_id)


@router.get("/superbills/{sb_id}/x12")
def x12(sb_id: int):
    return {"x12": generate_x12(sb_id)}