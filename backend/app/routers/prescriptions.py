import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from ..schemas_prescriptions import PrescriptionCreate, PrescriptionSign
from ..crud_prescriptions import (
    create_prescription,
    sign_prescription,
    get_rx_pdf,
    list_prescriptions_for_patient,
    get_prescription
)

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.post("/", summary="Create a draft prescription")
def create_rx(payload: PrescriptionCreate):
    return create_prescription(payload)


@router.put("/{prescription_id}/sign", summary="Sign prescription with provider signature")
def sign_rx(prescription_id: int, payload: PrescriptionSign):
    return sign_prescription(prescription_id, payload)


@router.get("/{prescription_id}/pdf", summary="Download prescription PDF")
def rx_pdf(prescription_id: int):
    path = get_rx_pdf(prescription_id)
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF not found")
    return FileResponse(path, filename=os.path.basename(path))


@router.get("/patient/{patient_id}", summary="List all prescriptions for a patient")
def patient_rx(patient_id: int):
    return list_prescriptions_for_patient(patient_id)


@router.get("/{prescription_id}", summary="Get prescription details")
def rx_detail(prescription_id: int):
    r = get_prescription(prescription_id)
    if not r:
        raise HTTPException(404, "Not found")
    return r
