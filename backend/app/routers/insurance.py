from fastapi import APIRouter, UploadFile, File
from ..crud_insurance import (
    create_insurance, get_insurance, get_insurances_for_patient,
    update_insurance, deactivate_insurance, save_card_file
)
from ..schemas_insurance import InsuranceCreate, InsuranceUpdate

router = APIRouter(prefix="/insurance", tags=["Insurance"])


@router.post("/{patient_id}", summary="Add Insurance Plan")
def add_insurance(patient_id: int, payload: InsuranceCreate):
    return create_insurance(patient_id, payload.dict())


@router.get("/patient/{patient_id}", summary="List Insurance")
def list_insurance(patient_id: int):
    return get_insurances_for_patient(patient_id)


@router.get("/{insurance_id}", summary="Get Insurance Detail")
def insurance_detail(insurance_id: int):
    return get_insurance(insurance_id)


@router.put("/{insurance_id}", summary="Update Insurance Plan")
def insurance_update(insurance_id: int, payload: InsuranceUpdate):
    return update_insurance(insurance_id, payload.dict())


@router.delete("/{insurance_id}", summary="Deactivate Insurance")
def insurance_delete(insurance_id: int):
    deactivate_insurance(insurance_id)
    return {"status": "deactivated"}


@router.post("/{insurance_id}/card/front", summary="Upload Front Card")
def upload_front_card(insurance_id: int, patient_id: int, file: UploadFile = File(...)):
    path = save_card_file(patient_id, file)
    return update_insurance(insurance_id, {"card_front": path})


@router.post("/{insurance_id}/card/back", summary="Upload Back Card")
def upload_back_card(insurance_id: int, patient_id: int, file: UploadFile = File(...)):
    path = save_card_file(patient_id, file)
    return update_insurance(insurance_id, {"card_back": path})