from fastapi import APIRouter, HTTPException, Depends
from ..auth import require_roles
from ..schemas_careplans import CarePlanCreate, CarePlanUpdate
from ..crud_careplans import (
    create_careplan, get_careplan,
    list_patient_careplans, update_careplan,
    delete_careplan
)

router = APIRouter(prefix="/careplans", tags=["Care Plans"])


@router.post("/", dependencies=[Depends(require_roles("admin", "provider"))])
def create_cp(data: CarePlanCreate):
    return create_careplan(data)


@router.get("/{cp_id}")
def get_cp(cp_id: int):
    rec = get_careplan(cp_id)
    if not rec:
        raise HTTPException(404, "Care plan not found")
    return rec


@router.get("/patient/{patient_id}")
def list_cp(patient_id: int):
    return list_patient_careplans(patient_id)


@router.put("/{cp_id}", dependencies=[Depends(require_roles("admin", "provider"))])
def update_cp(cp_id: int, data: CarePlanUpdate):
    return update_careplan(cp_id, data)


@router.delete("/{cp_id}", dependencies=[Depends(require_roles("admin"))])
def delete_cp(cp_id: int):
    return delete_careplan(cp_id)