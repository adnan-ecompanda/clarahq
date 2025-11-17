from fastapi import APIRouter, Depends, HTTPException
from ..auth import require_roles
from ..schemas_immunization import ImmunizationCreate, ImmunizationUpdate
from ..crud_immunization import (
    create_immunization, get_immunization, list_immunizations,
    update_immunization, delete_immunization
)

router = APIRouter(prefix="/immunizations", tags=["Immunizations"])


@router.post("/", dependencies=[Depends(require_roles("admin", "provider"))])
def create_immunization_record(data: ImmunizationCreate):
    return create_immunization(data)


@router.get("/{immunization_id}")
def get_immunization_record(immunization_id: int):
    result = get_immunization(immunization_id)
    if not result:
        raise HTTPException(404, "Immunization not found")
    return result


@router.get("/patient/{patient_id}")
def list_patient_immunizations(patient_id: int):
    return list_immunizations(patient_id)


@router.put("/{immunization_id}", dependencies=[Depends(require_roles("admin", "provider"))])
def update_record(immunization_id: int, data: ImmunizationUpdate):
    return update_immunization(immunization_id, data)


@router.delete("/{immunization_id}", dependencies=[Depends(require_roles("admin"))])
def delete_record(immunization_id: int):
    return delete_immunization(immunization_id)