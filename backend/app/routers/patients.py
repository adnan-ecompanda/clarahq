from fastapi import APIRouter, Depends, HTTPException
from ..schemas_patient import PatientCreate, PatientUpdate, PatientOut
from ..crud_patient import (
    create_patient,
    list_patients,
    get_patient,
    update_patient,
    delete_patient
)
from ..auth import require_roles


router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientOut)
def create(data: PatientCreate, user=Depends(require_roles("admin", "provider"))):
    return create_patient(data)


@router.get("", response_model=list[PatientOut])
def list_all(user=Depends(require_roles("admin", "provider"))):
    return list_patients()


@router.get("/{patient_id}", response_model=PatientOut)
def get(patient_id: int, user=Depends(require_roles("admin", "provider"))):
    p = get_patient(patient_id)
    if not p:
        raise HTTPException(404, "Patient not found")
    return p


@router.put("/{patient_id}", response_model=PatientOut)
def update(patient_id: int, data: PatientUpdate, user=Depends(require_roles("admin", "provider"))):
    updated = update_patient(patient_id, data)
    if not updated:
        raise HTTPException(404, "Patient not found")
    return updated


@router.delete("/{patient_id}")
def delete(patient_id: int, user=Depends(require_roles("admin"))):
    delete_patient(patient_id)
    return {"message": "Patient deleted"}