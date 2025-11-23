from fastapi import APIRouter
from typing import List

from app.schemas_billing_lines import (
    SuperbillCPTCreate,
    SuperbillICDCreate,
    SuperbillCPTOut,
    SuperbillICDOut
)

from app.crud_billing_lines import (
    add_cpt_line,
    list_cpt_lines,
    delete_cpt_line,
    add_icd_line,
    list_icd_lines,
    delete_icd_line
)

router = APIRouter(
    prefix="/billing-lines",
    tags=["Billing Line Items"]
)

# --------------------
# CPT ENDPOINTS
# --------------------

@router.post("/superbill/{sb_id}/cpt", response_model=SuperbillCPTOut)
def add_cpt(sb_id: int, data: SuperbillCPTCreate):
    return add_cpt_line(sb_id, data)


@router.get("/superbill/{sb_id}/cpt", response_model=List[SuperbillCPTOut])
def list_cpt(sb_id: int):
    return list_cpt_lines(sb_id)


@router.delete("/cpt/{line_id}")
def remove_cpt(line_id: int):
    delete_cpt_line(line_id)
    return {"message": "CPT line deleted"}


# --------------------
# ICD ENDPOINTS
# --------------------

@router.post("/superbill/{sb_id}/icd", response_model=SuperbillICDOut)
def add_icd(sb_id: int, data: SuperbillICDCreate):
    return add_icd_line(sb_id, data)


@router.get("/superbill/{sb_id}/icd", response_model=List[SuperbillICDOut])
def list_icd(sb_id: int):
    return list_icd_lines(sb_id)


@router.delete("/icd/{line_id}")
def remove_icd(line_id: int):
    delete_icd_line(line_id)
    return {"message": "ICD line deleted"}