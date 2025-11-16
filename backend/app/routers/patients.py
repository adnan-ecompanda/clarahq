from fastapi import APIRouter, HTTPException, Depends
from typing import List

from .. import schemas
from .. import crud_patients
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "",
    response_model=schemas.PatientOut,
    dependencies=[Depends(require_roles("admin", "provider"))]
)
def create_patient(payload: schemas.PatientCreate):
    return crud_patients.create_patient(payload)


@router.get(
    "",
    response_model=List[schemas.PatientOut],
    dependencies=[Depends(get_current_user)]
)
def list_all_patients():
    return crud_patients.list_patients()


@router.get(
    "/{patient_id}",
    response_model=schemas.PatientOut,
    dependencies=[Depends(get_current_user)]
)
def get_one_patient(patient_id: int):
    patient = crud_patients.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.delete(
    "/{patient_id}",
    dependencies=[Depends(require_roles("admin"))]
)
def delete_one_patient(patient_id: int):
    ok = crud_patients.delete_patient(patient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"status": "deleted"}