from fastapi import APIRouter, HTTPException, Depends
from ..auth import require_roles
from ..schemas_billing import (
    BillingCodeCreate, BillingCodeUpdate,
    SuperbillCreate, SuperbillUpdate
)
from ..crud_billing import (
    create_billing_code, list_billing_codes, get_billing_code,
    update_billing_code, delete_billing_code,
    create_superbill, get_superbill, update_superbill,
    delete_superbill
)

router = APIRouter(prefix="/billing", tags=["Billing"])


# ---------------- BILLING CODES ----------------

@router.post("/codes", dependencies=[Depends(require_roles("admin"))])
def add_code(data: BillingCodeCreate):
    return create_billing_code(data)


@router.get("/codes")
def list_codes():
    return list_billing_codes()


@router.get("/codes/{code_id}")
def get_code(code_id: int):
    rec = get_billing_code(code_id)
    if not rec:
        raise HTTPException(404, "Billing code not found")
    return rec


@router.put("/codes/{code_id}", dependencies=[Depends(require_roles("admin"))])
def update_code(code_id: int, data: BillingCodeUpdate):
    return update_billing_code(code_id, data)


@router.delete("/codes/{code_id}", dependencies=[Depends(require_roles("admin"))])
def delete_code(code_id: int):
    return delete_billing_code(code_id)


# ---------------- SUPERBILLS ----------------

@router.post("/superbill", dependencies=[Depends(require_roles("admin", "provider"))])
def create_sb(data: SuperbillCreate):
    return create_superbill(data)


@router.get("/superbill/{sb_id}")
def get_sb(sb_id: int):
    rec = get_superbill(sb_id)
    if not rec:
        raise HTTPException(404, "Superbill not found")
    return rec


@router.put("/superbill/{sb_id}", dependencies=[Depends(require_roles("admin", "provider"))])
def update_sb(sb_id: int, data: SuperbillUpdate):
    return update_superbill(sb_id, data)


@router.delete("/superbill/{sb_id}", dependencies=[Depends(require_roles("admin"))])
def delete_sb(sb_id: int):
    return delete_superbill(sb_id)