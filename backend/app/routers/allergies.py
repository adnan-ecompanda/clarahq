from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..schemas_allergies import AllergyCreate, AllergyUpdate, AllergyOut
from ..crud_allergies import (
    create_allergy, get_allergy,
    get_allergies_for_patient, update_allergy
)

router = APIRouter(prefix="/allergies", tags=["Allergies"])

@router.post("", response_model=AllergyOut)
def create(data: AllergyCreate, user=Depends(get_current_user)):
    data.recorded_by = user["id"]
    return create_allergy(data)

@router.get("/{allergy_id}", response_model=AllergyOut)
def read(allergy_id: int):
    return get_allergy(allergy_id)

@router.get("/patient/{patient_id}", response_model=list[AllergyOut])
def list_by_patient(patient_id: int):
    return get_allergies_for_patient(patient_id)

@router.put("/{allergy_id}", response_model=AllergyOut)
def update(allergy_id: int, data: AllergyUpdate):
    return update_allergy(allergy_id, data)